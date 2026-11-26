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
    # GARD anti-scurgere: importa DOAR daca beneficiarul e chiar tenantul. [17.5-Q10, F179] Lista SPV poate veni FĂRĂ beneficiar (mesajul
    # 8962564865 pentru 55229657, 24.11.2026): atunci beneficiarul se citește din documentul autentic (XML-ul descărcat, cumpărătorul) și se
    # confruntă cu CUI-ul firmei înainte de orice scriere; absent, ambiguu sau altul = refuz, nimic scris (`refuz_beneficiar`)
    if cif_ben and cif_ben != _digits(cif_tenant):
        stat["scurgere_evitata"] += 1
        print("  ANTI-SCURGERE %s: mesaj %s cif_beneficiar=%s != cif tenant %s - NU import"
              % (schema, id_mesaj, cif_ben, _digits(cif_tenant)), file=sys.stderr)
        return
    if _deja_importat(schema, id_mesaj):     # dedup: nu re-descarca (aceeași citire repetată / reîncercarea aceluiași index)
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
    if not cif_ben:
        motiv = refuz_beneficiar(xml, cif_tenant)
        if motiv:
            stat["scurgere_evitata"] += 1
            print("  ANTI-SCURGERE %s: mesaj %s fără beneficiar în listă — %s - NU import" % (schema, id_mesaj, motiv), file=sys.stderr)
            return
        cif_ben = _digits(cif_tenant)   # confirmat din documentul autentic
    xml_txt = xml.decode("utf-8", "replace") if isinstance(xml, (bytes, bytearray)) else xml
    sha = hashlib.sha256(xml_txt.encode("utf-8")).hexdigest()
    status = "descarcata"
    try:
        efi.parseaza_xml(xml, cif_tenant)    # doar valideaza parsabilitatea -> ciorna
        status = "ciorna"
    except Exception:
        status = "descarcata"                # fallback: descarcata, neparsabila (om o vede oricum)
    # [17.5-C9, AC201] emitentul: din metadate când e valabil, altfel din partea furnizorului a XML-ului autentic (`emitent_din_surse`)
    emitent, sursa_emitent, motiv_emitent = emitent_din_surse(msg, xml, cif_tenant)
    if motiv_emitent:
        stat["emitent_nedovedit"] = stat.get("emitent_nedovedit", 0) + 1
    # [17.5-C9, AC200] t_SPV = data_creare a listei ANAF (AAAALLZZHHmm, ora României, la minut); necunoscută = NULL, nu se inventează
    t_spv = data_creare_spv(msg.get("data_creare"))
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(f"""INSERT INTO {schema}.efactura_primite
                (id_mesaj_anaf, id_solicitare, cif_emitent, cif_beneficiar, data_creare, tip,
                 xml_brut, xml_sha256, status)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (id_mesaj_anaf) DO NOTHING RETURNING id, importat_la""",
                (id_mesaj, msg.get("id_solicitare"), emitent or "", cif_ben, t_spv,
                 msg.get("tip"), xml_txt, sha, status))
            nou = cur.fetchone()
    # [17.5-C9, AC200] două procesări concurente ale aceluiași index: numai inserarea reală se numără ca importată; cealaltă e duplicat
    if not nou:
        stat["deja"] += 1
        _jurnal_receptie(schema, id_mesaj, msg, "duplicat", None, None, sursa_emitent, motiv_emitent)
        return
    stat[status] += 1
    _jurnal_receptie(schema, id_mesaj, msg, status, nou[0], nou[1], sursa_emitent, motiv_emitent)


#: [17.5-C9, AC200] precizia lui data_creare din lista ANAF: AAAALLZZHHmm = la minut (forma răspunsului folosit de conector și a probei
#: arhitectului, «202611261630»); fusul: ora României (Europe/Bucharest), ca orele ANAF. Altă formă = necunoscută (NULL), nu se ghicește.
PRECIZIE_DATA_CREARE_SEC = 60
FUS_ANAF = "Europe/Bucharest"
#: [17.5-C9, AC200] intervalul cerut între disponibilitatea în SPV și apariția ciornei: 0 ≤ Δ ≤ 30:00 (inclusiv)
INTERVAL_MAX_SEC = 30 * 60


def data_creare_spv(v):
    """[17.5-C9, AC200] `data_creare` din lista ANAF -> datetime cu fus (Europe/Bucharest), sau None când lipsește, nu are exact
    12 cifre (AAAALLZZHHmm) ori e o dată imposibilă. PURĂ."""
    import re
    from datetime import datetime
    from zoneinfo import ZoneInfo
    t = str(v or "").strip()
    if not re.fullmatch(r"[0-9]{12}", t):
        return None
    try:
        return datetime.strptime(t, "%Y%m%d%H%M").replace(tzinfo=ZoneInfo(FUS_ANAF))
    except ValueError:
        return None


def interval_spv_ciorna(t_spv, t_ciorna, precizie_sec=PRECIZIE_DATA_CREARE_SEC):
    """[17.5-C9, AC200] Judecata intervalului SPV -> ciornă (PURĂ). `t_spv` = data_creare (trunchiată la precizia ei), `t_ciorna` =
    prima apariție persistentă ca ciornă; ambele cu fus. Δ real ∈ [t_ciorna − (t_spv + precizie − 1 s), t_ciorna − t_spv].
    Întoarce {"verdict": "in_interval" | "depasire" | "nedovedit", "delta_sec": Δ observat sau None, "motiv": text}."""
    from datetime import timedelta
    if t_spv is None:
        return {"verdict": "nedovedit", "delta_sec": None, "motiv": "interval nedovedit: data_creare din SPV lipsește"}
    if t_ciorna is None:
        return {"verdict": "nedovedit", "delta_sec": None, "motiv": "interval nedovedit: momentul ciornei lipsește"}
    if t_spv.tzinfo is None or t_ciorna.tzinfo is None:
        return {"verdict": "nedovedit", "delta_sec": None, "motiv": "interval nedovedit: fus orar necunoscut"}
    maxim = (t_ciorna - t_spv).total_seconds()                       # disponibil la începutul minutului
    minim = (t_ciorna - (t_spv + timedelta(seconds=max(precizie_sec - 1, 0)))).total_seconds()
    if maxim < 0:
        return {"verdict": "nedovedit", "delta_sec": maxim,
                "motiv": "interval nedovedit: ciorna e înaintea disponibilității în SPV (inversat)"}
    if minim >= 0 and maxim <= INTERVAL_MAX_SEC:
        return {"verdict": "in_interval", "delta_sec": maxim, "motiv": "în interval (≤ 30:00)"}
    if minim > INTERVAL_MAX_SEC:
        return {"verdict": "depasire", "delta_sec": maxim, "motiv": "depășire: peste 30:00"}
    return {"verdict": "nedovedit", "delta_sec": maxim,
            "motiv": "interval nedovedit: precizia datei din SPV (%d s) nu permite judecarea pragului" % precizie_sec}


def interval_rand(data_creare, importat_la, status_la_import):
    """[17.5-C9, AC200] Intervalul unui rând persistent: t_ciornă = `importat_la` numai când rândul a intrat direct ca ciornă (nicio cale
    nu trece un rând «descarcata» în «ciorna»; `importat_la` nu se rescrie la validare, respingere sau reluare). Starea la import
    necunoscută (rândul e acum validat / respins) = interval nedovedit. PURĂ."""
    if status_la_import != "ciorna":
        return {"verdict": "nedovedit", "delta_sec": None,
                "motiv": "interval nedovedit: rândul n-a apărut ca ciornă" if status_la_import == "descarcata"
                else "interval nedovedit: starea la import nu e păstrată"}
    return interval_spv_ciorna(data_creare, importat_la)


def emitent_din_surse(msg, xml, cif_tenant):
    """[17.5-C9, AC201] Emitentul unui mesaj SPV (PURĂ): (cod în forma păstrată sau None, sursa, motivul când nu e cert).
    Ordinea: metadatele mesajului (`cif_emitent`) când sunt valabile; altfel partea furnizorului din XML-ul autentic (aceleași căi ca
    parserul UBL al aplicației, `efactura_import._parte`: PartyTaxScheme/CompanyID și PartyLegalEntity/CompanyID). Valabil = cod românesc
    cu cifra de control bună (`identitate.valideaza_cui`), cu sau fără «RO»; se păstrează fără «RO» (`cui_forma.stocare`, decizia 10.3).
    Gol, «-/-/-», două coduri valabile diferite în XML, codul cumpărătorului sau contradicția metadate–XML = niciun emitent (politica:
    nu se atribuie automat un furnizor nedovedit; diferența se spune în motiv și în jurnalul recepției)."""
    from core import cui_forma
    from core.identitate import valideaza_cui
    import re
    import xml.etree.ElementTree as _ET

    def _cod(v):
        s = cui_forma.stocare(v) or ""
        return s if re.fullmatch(r"[0-9]{2,10}", s) and valideaza_cui(s)[0] else None

    tenant = _digits(cif_tenant)
    meta = _cod(msg.get("cif_emitent"))
    din_xml, motiv_xml = None, None
    try:
        root = _ET.fromstring(xml if isinstance(xml, (bytes, bytearray)) else str(xml or "").encode("utf-8"))
        p = root.find("cac:AccountingSupplierParty/cac:Party", efi.NS)
        brute = [] if p is None else [e.text for e in p.findall("cac:PartyTaxScheme/cbc:CompanyID", efi.NS)
                                       + p.findall("cac:PartyLegalEntity/cbc:CompanyID", efi.NS)]
        coduri = {c for c in (_cod(b) for b in brute) if c}
        if len(coduri) > 1:
            motiv_xml = "furnizorul din XML are coduri diferite (%s): ambiguu" % ", ".join(sorted(coduri))
        elif coduri:
            din_xml = next(iter(coduri))
        else:
            motiv_xml = "furnizorul din XML nu are un cod fiscal valabil"
    except _ET.ParseError:
        motiv_xml = "XML-ul nu se poate citi"
    if din_xml and din_xml == tenant:
        din_xml, motiv_xml = None, "codul furnizorului din XML e al firmei (cumpărătorul)"
    if meta and meta == tenant:
        meta = None
    if meta and din_xml and meta != din_xml:
        return None, "contradictie", "metadatele SPV spun %s, XML-ul spune %s: emitent nedovedit" % (meta, din_xml)
    if meta:
        return meta, "metadate", None
    if din_xml:
        return din_xml, "xml", None
    return None, "niciuna", motiv_xml or "emitentul lipsește"


def _jurnal_receptie(schema, id_mesaj, msg, rezultat, rand_id, importat_la, sursa_emitent, motiv_emitent):
    """[17.5-C9, AC200] Rândul jurnalului recepției (stderr -> jurnalul serviciului spv-receive): identificatorii de corelare (schema,
    indexul, cererea, rândul), cele două momente și Δ, sursa emitentului. Fără token, fără XML."""
    from datetime import datetime, timezone
    t_spv = data_creare_spv(msg.get("data_creare"))
    j = interval_spv_ciorna(t_spv, importat_la) if rezultat == "ciorna" else None
    print("  RECEPTIE %s mesaj=%s solicitare=%s rezultat=%s rand=%s data_creare=%s t_spv=%s t_ciorna=%s delta_sec=%s interval=%s "
          "emitent_sursa=%s%s la=%s" % (
              schema, id_mesaj, msg.get("id_solicitare") or "-", rezultat, rand_id or "-", msg.get("data_creare") or "-",
              t_spv.isoformat() if t_spv else "-", importat_la.isoformat() if importat_la else "-",
              ("%d" % j["delta_sec"]) if j and j["delta_sec"] is not None else "-", j["verdict"] if j else "-",
              sursa_emitent, (" emitent_motiv=" + motiv_emitent) if motiv_emitent else "",
              datetime.now(timezone.utc).isoformat()), file=sys.stderr)


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
    inainte = dict(stat)
    erori_import = 0
    for msg in mesaje:
        try:
            importa_mesaj(schema, principal, cif, msg, stat)
        except Exception as e:
            erori_import += 1
            print("  EROARE import %s/%s: %s" % (schema, msg.get("id"), e), file=sys.stderr)
        _dormi(INTERVAL_SEC)
    return {"cif": cif, "zile": zile, "mesaje": len(mesaje), "eroare": None, "pe_rezultat": pe_rezultat(inainte, stat, len(mesaje), erori_import)}


def pe_rezultat(inainte, dupa, gasite, erori_import=0):
    """[17.5-Q12, F179 Simplitate] Ce s-a întâmplat cu mesajele găsite la o citire, pe rezultat (PURĂ): `importate` (intrate în lista de validat,
    ciornă sau descărcate neparsabile), `duplicate` (deja în listă: aceeași citire repetată / reîncercarea aceluiași index), `refuzate` (garda
    beneficiarului: alt CUI, absent sau ambiguu în documentul autentic) și `neimportate` (descărcarea n-a mers / fără XML / fără drept / eroare).
    Suma lor = `gasite`."""
    d = lambda k: dupa.get(k, 0) - inainte.get(k, 0)
    return {"gasite": gasite, "importate": d("ciorna") + d("descarcata"), "duplicate": d("deja"), "refuzate": d("scurgere_evitata"),
            "neimportate": d("skip_auth") + d("descarca_esec") + d("fara_xml") + erori_import}


def refuz_beneficiar(xml, cif_tenant):
    """[17.5-Q10, F179] Motivul refuzului unui mesaj SPV fără beneficiar în listă, citit din documentul autentic, sau None când beneficiarul
    facturii (AccountingCustomerParty: PartyLegalEntity/CompanyID sau PartyTaxScheme/CompanyID) e chiar firma. Absent (niciun cod),
    ambiguu (coduri diferite între ele) sau străin (alt cod) = refuz. PURĂ."""
    import xml.etree.ElementTree as _ET
    try:
        root = _ET.fromstring(xml if isinstance(xml, (bytes, bytearray)) else str(xml).encode("utf-8"))
    except _ET.ParseError:
        return "documentul nu se poate citi"
    ns = {"cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
          "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"}
    coduri = {_digits(e.text) for e in root.findall("cac:AccountingCustomerParty/cac:Party/cac:PartyLegalEntity/cbc:CompanyID", ns)
              + root.findall("cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID", ns) if _digits(e.text)}
    if not coduri:
        return "beneficiarul lipsește din document (absent)"
    if len(coduri) > 1:
        return "documentul are mai multe coduri de beneficiar (%s): ambiguu" % ", ".join(sorted(coduri))
    if coduri != {_digits(cif_tenant)}:
        return "beneficiarul din document e %s, nu firma (%s): străin" % (next(iter(coduri)), _digits(cif_tenant))
    return None


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
