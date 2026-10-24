# -*- coding: utf-8 -*-
"""
core/spv_receive.py — cron RECEIVE e-Factura (F179): facturi de la furnizori din SPV.

Jumatatea de PRIMIRE a F126. Ruleaza pe timer (spv-receive.timer), listeaza mesajele filtru=P
(FACTURA PRIMITA) per tenant, descarca facturile NOI, le insereaza CIORNA in efactura_primite.
FOUR-EYES: NU creeaza cheltuiala automat - contabilul valideaza (pasul 5), abia atunci factura_id.

GARDURI (nenegociabile):
- Reutilizeaza efactura_send.lista_mesaje/descarca (apel_anaf pe PRINCIPAL, fara client paralel).
- [P7 · D2] principalul unei scheme vine de la `spv_conector`, nu din motorul fiscal.
- DEDUP pe id_mesaj_anaf: pre-check + INSERT ... ON CONFLICT DO NOTHING (fereastra 2-3z suprapusa la
  30 min -> aceeasi factura la mai multe rulari). Nu re-descarca ce e deja importat.
- cif_beneficiar VALIDAT la insert (== CIF tenant), nu doar stocat. Pe token de cabinet care acopera
  N CIF-uri, factura se leaga de tenantul al carui CIF = cif_beneficiar. Mismatch -> SKIP + log
  anti-scurgere intre chiriasi (la nivel de insert, nu de afisare).
- Token expirat/mort -> apel_anaf face refresh; EroareSpv -> SKIP tenant/mesaj (auth-fail != eroare).
- MASINA DE STARI: descarcata (fallback neparsabil) / ciorna (parsata, prezentata) -> validata/respinsa
  DOAR prin four-eyes (om). factura_id NULL pana la validare.
"""
import os
import sys
import hashlib
import requests

from core import db
from core import spv_conector
from core import efactura_send as efs
from core import efactura_import as efi
from core.common import cate

#: [598 / 600, lotul 12] ce nu s-a întâmplat când citirea din SPV a căzut (`spv_conector.mesaj_pentru_contabil`)
MESAJ_NECITITE = "Facturile de la furnizori nu s-au citit acum din SPV."
#: [C42 + 598] ANAF n-a răspuns la citire: se spune ce face aplicația (reia singură), fără numele excepției
MESAJ_ANAF_FARA_RASPUNS = spv_conector.MESAJ_CITIRE_ANAF_TACE
#: [598] arhiva încărcată la „Import manual XML” nu se deschide (era textul bibliotecii, în engleză: „File is not a zip file”)
MESAJ_ARHIVA_STRICATA = "%s: arhiva nu se poate deschide. Încarcă XML-ul facturii sau arhiva ZIP descărcată din SPV, așa cum a venit."

MEDIU = os.environ.get("EFACTURA_MEDIU", "prod")
ZILE = int(os.environ.get("SPV_RECEIVE_ZILE", "3"))            # fereastra suprapusa, < 60 oficial
INTERVAL_SEC = float(os.environ.get("SPV_RECEIVE_INTERVAL_SEC", "1.0"))


def _digits(x):
    return "".join(c for c in str(x or "") if c.isdigit())


def _deja_importat(schema, id_mesaj):
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT 1 FROM {schema}.efactura_primite WHERE id_mesaj_anaf=%s", (id_mesaj,))
            return cur.fetchone() is not None


def importa_mesaj(schema, principal, cif_tenant, msg, stat):
    """Un mesaj listaMesajeFactura -> rand efactura_primite (ciorna/descarcata). Idempotent + anti-scurgere."""
    id_mesaj = str(msg.get("id") or "")
    cif_ben = _digits(msg.get("cif_beneficiar"))
    # GARD anti-scurgere: importa DOAR daca beneficiarul e chiar tenantul
    if not cif_ben or cif_ben != _digits(cif_tenant):
        stat["scurgere_evitata"] += 1
        print("  ANTI-SCURGERE %s: mesaj %s cif_beneficiar=%s != cif tenant %s - NU import"
              % (schema, id_mesaj, cif_ben, _digits(cif_tenant)), file=sys.stderr)
        return
    if _deja_importat(schema, id_mesaj):     # dedup: nu re-descarca
        stat["deja"] += 1
        return
    try:
        r = efs.descarca(principal, id_mesaj, MEDIU)
    except spv_conector.EroareSpv as e:
        stat["skip_auth"] += 1
        print("  SKIP auth descarca %s/%s: %s" % (schema, id_mesaj, e), file=sys.stderr)
        return
    if getattr(r, "status_code", None) != 200 or not getattr(r, "content", None):
        stat["descarca_esec"] += 1
        return
    xml = None
    try:
        for _nume, xmlb in efi.extrage_fisiere("f.zip", r.content):
            xml = xmlb
            break
    except Exception:
        xml = None
    if not xml:
        stat["fara_xml"] += 1
        return
    xml_txt = xml.decode("utf-8", "replace") if isinstance(xml, (bytes, bytearray)) else xml
    sha = hashlib.sha256(xml_txt.encode("utf-8")).hexdigest()
    status = "descarcata"
    try:
        efi.parseaza_xml(xml, cif_tenant)    # doar valideaza parsabilitatea -> ciorna
        status = "ciorna"
    except Exception:
        status = "descarcata"                # fallback: descarcata, neparsabila (om o vede oricum)
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(f"""INSERT INTO {schema}.efactura_primite
                (id_mesaj_anaf, id_solicitare, cif_emitent, cif_beneficiar, tip,
                 xml_brut, xml_sha256, status)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (id_mesaj_anaf) DO NOTHING""",
                (id_mesaj, msg.get("id_solicitare"), _digits(msg.get("cif_emitent")), cif_ben,
                 msg.get("tip"), xml_txt, sha, status))
    stat[status] += 1


#: [lotul 6, 273 / comanda Costin pct.2b] prima citire a unui CUI pe tokenul activ cuprinde toată fereastra oficială: o firmă nou adăugată
#: (sau un cabinet nou conectat) primește facturile din ultimele 60 de zile, nu numai din ultimele `ZILE`.
ZILE_PRIMA_CITIRE = 60
#: ANAF: „Nu aveti drept in SPV pentru CIF=…” — certificatul nu are drept pentru firmă (împuternicire)
_FARA_DREPT = "nu aveti drept"


def _citire_anterioara(conn, token_id, cif):
    with conn.cursor() as cur:
        cur.execute("SELECT ultima_reusita FROM public.spv_cui_acoperit WHERE token_id = %s AND cui = %s", (token_id, cif))
        r = cur.fetchone()
    return r[0] if r else None


def _inregistreaza_citire(conn, token_id, cif, eroare, mesaje):
    """Rândul (token, CUI) din `public.spv_cui_acoperit`: când s-a verificat, dacă certificatul are drept, câte mesaje, ce eroare."""
    are_drept = None if eroare and _FARA_DREPT not in eroare.lower() else (not eroare)
    with conn.cursor() as cur:
        # upsert-ok: starea ULTIMEI citiri pe (token, CUI) — rescrisă la fiecare citire, intenționat; `ultima_reusita` se păstrează la eșec
        cur.execute("""INSERT INTO public.spv_cui_acoperit (token_id, cui, verificat_la, are_drept, eroare, mesaje, ultima_reusita)
                       VALUES (%s, %s, now(), %s, %s, %s, CASE WHEN %s IS NULL THEN now() END)
                       ON CONFLICT (token_id, cui) DO UPDATE SET verificat_la = now(), are_drept = EXCLUDED.are_drept,
                         eroare = EXCLUDED.eroare, mesaje = EXCLUDED.mesaje,
                         ultima_reusita = COALESCE(EXCLUDED.ultima_reusita, public.spv_cui_acoperit.ultima_reusita)""",
                    (token_id, cif, are_drept, eroare, mesaje, eroare))


def citeste_firma(schema, stat=None, _dormi=None):
    """O firmă: lista mesajelor primite (filtru P) + importul celor noi + rândul ei din `spv_cui_acoperit`. Folosită de timer și de
    „Verifică acum în SPV”. Întoarce {cif, zile, mesaje, eroare}; `eroare` = textul ANAF sau motivul (fără CUI, fără conexiune)."""
    stat = stat if stat is not None else _stat_nou()
    _dormi = _dormi or (lambda _s: None)
    with db.get_conn() as conn:
        principal = spv_conector.principal_pentru_schema(conn, schema)
        token = spv_conector.ia_token_activ(conn, principal) if principal else None
        with conn.cursor() as cur:
            cur.execute(f"SELECT cui FROM {schema}.firma_profil WHERE id=1")
            row = cur.fetchone()
        cif = _digits(row[0]) if row and row[0] else ""
        if not cif:
            stat["tenanti_fara_cif"] += 1
            return {"cif": "", "zile": 0, "mesaje": 0, "eroare": "Firma n-are CUI în Date firmă.", "de_la_anaf": False}
        if not token:
            stat["skip_auth"] += 1
            return {"cif": cif, "zile": 0, "mesaje": 0, "eroare": spv_conector.MESAJ_CITIRE_NECONECTAT, "de_la_anaf": False}
        zile = ZILE if _citire_anterioara(conn, token["id"], cif) else ZILE_PRIMA_CITIRE
    # [598, lotul 12] `de_la_anaf`: textul e răspunsul ANAF (ecranul îl citează „ANAF a răspuns: …”) sau motivul spus de aplicație
    de_la_anaf = True
    try:
        mesaje, eroare = efs.lista_mesaje(principal, cif, MEDIU, zile=zile, filtru="P")
    except spv_conector.EroareSpvFaraDrept:
        # 403: refuzul de drept pe CIF (ARHITECTURA_SPV.md, „fara drept” vine de obicei ca 200 + eroare; 403 e aceeași concluzie)
        stat["skip_auth"] += 1
        mesaje, eroare = [], "Nu aveti drept in SPV pentru CIF=%s" % cif
    except spv_conector.EroareSpv as e:
        stat["skip_auth"] += 1
        print("  SKIP auth lista %s: %s" % (schema, e), file=sys.stderr)
        # [598 / 600, lotul 12] `eroare` ajunge pe ecran („ANAF a răspuns: …”, Conectare SPV): motivul pe înțelesul omului, nu excepția
        mesaje, eroare, de_la_anaf = [], spv_conector.mesaj_pentru_contabil(e, MESAJ_NECITITE), False
    except requests.exceptions.RequestException as e:
        # [C42, 16.10.2026] ANAF n-a răspuns (16.10 19:47: ReadTimeout după 60 s): se spune pe firma ei și se trece la următoarea —
        # înainte, excepția oprea citirea TUTUROR firmelor și trimitea alerta „job eșuat” pentru un lucru care trece singur (296)
        stat["anaf_fara_raspuns"] += 1
        print("  %s: ANAF n-a răspuns: %s" % (schema, e), file=sys.stderr)
        mesaje, eroare, de_la_anaf = [], MESAJ_ANAF_FARA_RASPUNS, False   # [598] fără numele excepției („ReadTimeout”) pe ecran
    with db.get_conn() as conn:
        # „Nu exista mesaje in ultimele N zile” e un răspuns reușit (zero facturi), nu o eroare
        fara_mesaje = bool(eroare) and eroare.lower().startswith("nu exista mesaje")
        _inregistreaza_citire(conn, token["id"], cif, None if fara_mesaje else eroare, len(mesaje))
    if eroare and not fara_mesaje:
        print("  %s: lista fara mesaje/eroare: %s" % (schema, eroare))
        return {"cif": cif, "zile": zile, "mesaje": 0, "eroare": eroare, "de_la_anaf": de_la_anaf}
    for msg in mesaje:
        try:
            importa_mesaj(schema, principal, cif, msg, stat)
        except Exception as e:
            print("  EROARE import %s/%s: %s" % (schema, msg.get("id"), e), file=sys.stderr)
        _dormi(INTERVAL_SEC)
    return {"cif": cif, "zile": zile, "mesaje": len(mesaje), "eroare": None}


def _stat_nou():
    return {"ciorna": 0, "descarcata": 0, "deja": 0, "scurgere_evitata": 0,
            "skip_auth": 0, "descarca_esec": 0, "fara_xml": 0, "tenanti_fara_cif": 0, "anaf_fara_raspuns": 0}


def importa_xml_manual(schema, continut, nume_fisier=""):
    """[lotul 6 pct.7b, 273] „Import manual XML UBL”: factura primită încărcată de contabil intră în ACELAȘI flux ca cele din SPV
    (`efactura_primite`, ciornă, validată apoi de contabil), nu direct în facturi. Cheia de unicitate: `manual-<sha256 XML>` (același
    fișier a doua oară nu se dublează). Beneficiarul din XML trebuie să fie firma. Întoarce {"importate", "deja", "erori": [...]}."""
    rez = {"importate": 0, "deja": 0, "erori": []}
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT cui FROM {schema}.firma_profil WHERE id=1")
            row = cur.fetchone()
    cif = _digits(row[0]) if row and row[0] else ""
    if not cif:
        return dict(rez, erori=["Firma n-are CUI în Date firmă: factura nu se poate verifica."])
    try:
        perechi = efi.extrage_fisiere(nume_fisier or "f.xml", continut)
    except Exception as e:  # noqa: BLE001 — arhiva stricată: refuzul pe înțelesul omului, excepția în jurnal
        print("  import manual XML %s: arhiva nu se deschide: %s" % (schema, e), file=sys.stderr)
        return dict(rez, erori=[MESAJ_ARHIVA_STRICATA % (nume_fisier or "fișierul")])
    for nume, xml in perechi:
        try:
            f = efi.parseaza_xml(xml, cif)
        except ValueError as e:
            rez["erori"].append("%s: %s" % (nume, e))
            continue
        if f["directie"] != "primita":
            rez["erori"].append("%s: factura e emisă de firmă, nu primită — se încarcă la facturile emise." % nume)
            continue
        _alta = efi.alta_firma(f, cif)   # [lotul 12, C120, clasa 599] factura între alte două firme nu intră
        if _alta:
            rez["erori"].append("%s: %s" % (nume, _alta))
            continue
        xml_txt = xml.decode("utf-8", "replace") if isinstance(xml, (bytes, bytearray)) else xml
        sha = hashlib.sha256(xml_txt.encode("utf-8")).hexdigest()
        with db.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(f"""INSERT INTO {schema}.efactura_primite (id_mesaj_anaf, cif_emitent, cif_beneficiar, tip, xml_brut, xml_sha256, status)
                                VALUES (%s,%s,%s,'MANUAL',%s,%s,'ciorna') ON CONFLICT (id_mesaj_anaf) DO NOTHING RETURNING id""",
                            ("manual-" + sha[:40], _digits(f["tert_cui"]), cif, xml_txt, sha))
                rez["importate" if cur.fetchone() else "deja"] += 1
    return rez


def ruleaza(_dormi=None):
    import time
    _dormi = _dormi or time.sleep
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT schema_name FROM information_schema.schemata "
                        "WHERE schema_name ~ '^tenant_[0-9]+$' ORDER BY schema_name")
            scheme = [r[0] for r in cur.fetchall()]
    stat = _stat_nou()
    cazute = []
    for schema in scheme:
        # [C42] o firmă care cade (alt motiv decât ANAF) nu oprește citirea celorlalte; la capăt jobul eșuează cu toate numite —
        # ăla e un defect, deci alertă (296: cere acțiune)
        try:
            inainte = stat["ciorna"] + stat["descarcata"]
            citeste_firma(schema, stat, _dormi)
            noi = stat["ciorna"] + stat["descarcata"] - inainte
            if noi > 0:
                # [deficiența 320] „Facturi și SPV”: cei care pregătesc pe firmă află că au venit facturi noi (clopoțelul + canalul ales);
                # o notificare căzută nu e o citire căzută
                try:
                    from core import notificari_termene as _nt
                    _nt.notifica_firma(schema, "factura_primita", lambda nume, n=noi: "%s: %s din SPV, de verificat în Facturi primite." % (
                        nume, cate(n, "factură nouă primită", "facturi noi primite")))
                except Exception as _e:  # noqa: BLE001
                    from core import observare as _obs
                    _obs.esec_secundar("notificarea facturilor primite %s" % schema, _e)
        except Exception as e:
            print("  EROARE citire %s: %s: %s" % (schema, type(e).__name__, e), file=sys.stderr)
            cazute.append((schema, type(e).__name__, str(e)))
    from datetime import datetime, timezone
    print("%s spv_receive terminat: %s" % (datetime.now(timezone.utc).isoformat(), stat))
    if cazute:
        e = RuntimeError("citirea SPV a căzut la %s: %s" % (
            cate(len(cazute), "firmă", "firme"), "; ".join("%s (%s: %s)" % c for c in cazute)))
        e.cazute = cazute
        raise e
    return stat


if __name__ == "__main__":
    from core import cron  # [R74] alerta la esec + bataie la reusita
    cron.ruleaza("spv_receive", ruleaza)
