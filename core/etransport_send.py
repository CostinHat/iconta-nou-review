# -*- coding: utf-8 -*-
"""
core/etransport_send.py — TRIMITERE e-Transport UIT prin API OAuth (F121).

Reutilizeaza spv_principal + apel_anaf (drept UNIFICAT cu e-Factura: acelasi token SPV acopera si
e-Transport - roluri EFACTURA+ETRANSPORT in JWT, OMFP 660/2017 = toate serviciile). Fara client paralel.

ENDPOINT-URI (VERIFICAT LA SURSA, ARHITECTURA_SPV.md) - host OAuth api.anaf.ro, path ETRANSPORT/ws/v1,
PARAMETRII IN PATH (nu query):
  - upload:     POST /upload/ETRANSP/{cif}/{versiune}   (body XML)
  - stareMesaj: GET  /stareMesaj/{id_incarcare}
  - lista:      GET  /lista/{zile}/{cif}

GARDA DE TIMP UIT (specifica, NU copiata de la factura): declarare max 3 zile INAINTE de miscare;
UIT valabil 5 zile (national) / 15 zile (intracomunitar); folosire dupa expirare = BLOCATA.

POARTA PRE-TRIMITERE = validare pe TEST (mediu=test) - NU exista validator fara auth ca e-Factura
validare/FACT1 (confirmat la sursa). Nu se trimite pe prod nevalidat.

LIMITA (onest, ca la e-Factura): formatul EXACT al raspunsului upload/stareMesaj (ExecutionStatus/UIT/
erori) e din pattern-ul ANAF, NU dovedit live - parsare DEFENSIVA, se logheaza brut la primul raspuns real.
Trimiterea live ramane pending drept e-Transport pe CIF real.
"""
import re
import hashlib
from datetime import date, datetime, timedelta

from core import db
from core import observare as _obs
from core import spv_conector
from core import chei_unice as _chei   # [lotul 10, C73 / U2] a doua trimitere vie a notificării -> numită, nu 500
from core.common import cfg, azi_ro, cate as _cate
from core.pdf_util import data_ro as _data_ro   # DS cap.4: data pentru om, sursa unică

#: [598 / 600, lotul 12] ce nu s-a întâmplat când drumul spre ANAF a căzut (`spv_conector.mesaj_pentru_contabil`)
MESAJ_NETRIMISA = "Notificarea e-Transport nu a plecat la ANAF, deci nu are încă cod UIT."

# Config din env — citită LA APEL prin cfg() (nu înghețată la import, item 5).
# ETRANSPORT_BASE (host OAuth, webserviceapl = cert), ETRANSPORT_VERSIUNE (int,
# implicit 2 = v2 curent; v1 inca acceptat) — vezi etransport_base() / versiune la trimite().


def etransport_base(mediu="test"):
    """Baza REST e-Transport pentru mediu 'prod'/'test'. SINGURA sursa a host-ului.
    Host din ETRANSPORT_BASE (implicit api.anaf.ro/%s/ETRANSPORT/ws/v1), citit la apel."""
    mediu = (mediu or "test").strip().lower()
    if mediu not in ("prod", "test"):
        mediu = "test"
    return cfg("ETRANSPORT_BASE", "https://api.anaf.ro/%s/ETRANSPORT/ws/v1") % mediu


# ============================================================
#  GARDA DE TIMP UIT — PURA (fara DB/retea)
# ============================================================
# [OUG 41/2022 art.11(2)] UIT valabil 15 zile (nu 5): achizitii intracom (cod 10, art.2 pct.9 lit.a),
# tranzactie intracom in tranzit-intrare (cod 60, lit.g), nontransfer / stocuri la dispozitia clientului
# (cod 80, lit.j). Restul = 5 zile.
COD_UIT_15_ZILE = ("10", "60", "80")


def uit_15_zile(cod_tip_operatiune):
    """True daca operatiunea are UIT valabil 15 zile (art.11(2) OUG 41/2022): achizitii
    intracomunitare + operatiunile de la art.2 pct.9 lit.g) si lit.j)."""
    return str(cod_tip_operatiune) in COD_UIT_15_ZILE


def fereastra_uit(data_transport, intracom=False, acum=None):
    """
    Verdictul ferestrei legale UIT (ARHITECTURA_SPV.md), pur. data_transport = date sau 'YYYY-MM-DD'.
    Reguli: declarare max 3 zile INAINTE de data transportului; UIT valabil 5 zile (national) /
    15 zile (intracomunitar). Folosire dupa expirare = blocata. Intoarce dict cu verdictul.
    """
    acum = acum if acum is not None else azi_ro()   # [fus] verdict UIT expirat/valabil = zi RO, robust la OS TZ
    dt = data_transport if isinstance(data_transport, date) else \
        datetime.strptime(str(data_transport)[:10], "%Y-%m-%d").date()
    zile_val = 15 if intracom else 5
    # [OUG 41/2022 art.11(2)] "N zile calendaristice ... INCEPAND CU data declarata": ziua transportului
    # e ziua 1, deci ultima zi valabila = X+(N-1) (5 zile = X..X+4; 15 = X..X+14).
    valabil_pana = dt + timedelta(days=zile_val - 1)
    prea_devreme = (dt - acum).days > 3
    expirat = acum > valabil_pana
    poate_trimite = not prea_devreme and not expirat
    if prea_devreme:
        mesaj = "Prea devreme: transportul se declară cu cel mult 3 zile înainte (transport %s)." % _data_ro(dt)
    elif expirat:
        mesaj = "UIT expirat: valabilitatea (%s) a trecut." % _data_ro(valabil_pana)
    else:
        mesaj = "Codul UIT e valabil până la %s (%s)." % (_data_ro(valabil_pana), _cate(zile_val, "zi", "zile"))
    return {"poate_trimite": poate_trimite, "prea_devreme": prea_devreme, "expirat": expirat,
            "zile_valabilitate": zile_val, "uit_valabil_pana": valabil_pana,
            "data_transport": dt, "mesaj": mesaj}


# ============================================================
#  APELURI ANAF — prin apel_anaf pe principal (fara client paralel)
# ============================================================
def upload_uit(principal, cif, xml, versiune=None, mediu="test"):
    """POST /upload/ETRANSP/{cif}/{versiune}. Intoarce Response."""
    versiune = versiune if versiune is not None else cfg("ETRANSPORT_VERSIUNE", "2", int)
    cifn = "".join(c for c in str(cif) if c.isdigit())
    url = "%s/upload/ETRANSP/%s/%s" % (etransport_base(mediu), cifn, versiune)
    return spv_conector.apel_anaf(principal, "POST", url, data=xml.encode("utf-8"),
                                  headers={"Content-Type": "application/xml"}, timeout=60)


def stare_uit(principal, index_incarcare, mediu="test"):
    """GET /stareMesaj/{id_incarcare}. Intoarce Response."""
    url = "%s/stareMesaj/%s" % (etransport_base(mediu), index_incarcare)
    return spv_conector.apel_anaf(principal, "GET", url, timeout=30)


def lista_uit(principal, zile, cif, mediu="test"):
    """GET /lista/{zile}/{cif}. zile 1..60. Intoarce Response."""
    zile = max(1, min(int(zile), 60))
    cifn = "".join(c for c in str(cif) if c.isdigit())
    url = "%s/lista/%s/%s" % (etransport_base(mediu), zile, cifn)
    return spv_conector.apel_anaf(principal, "GET", url, timeout=60)


def _parse_upload(text):
    """(execution_status, index_incarcare, uit, [erori]) din raspunsul upload. DEFENSIV - formatul exact
    se confirma la primul raspuns real (loghezi brut). Cauta atributele ANAF uzuale + campul UIT."""
    t = text or ""
    ex = re.search(r'ExecutionStatus="(\d+)"', t)
    idx = re.search(r'index_incarcare="(\d+)"', t)
    uit = re.search(r'UIT="([^"]+)"', t) or re.search(r'<UIT>([^<]+)</UIT>', t)
    errs = re.findall(r'errorMessage="([^"]*)"', t)
    return (int(ex.group(1)) if ex else None,
            idx.group(1) if idx else None,
            uit.group(1) if uit else None, errs)


# ============================================================
#  ORCHESTRARE — porti in ordine (timp -> idempotency -> validare TEST -> upload)
# ============================================================
def valideaza_pe_test(principal, cif, xml):
    """POARTA pre-trimitere: upload pe TEST (nu exista validator fara auth). Intoarce (ok, index, erori)."""
    try:
        r = upload_uit(principal, cif, xml, mediu="test")
    except spv_conector.EroareSpv as e:
        # [598 / 600, lotul 12] motivul pe înțelesul contabilului; excepția, în jurnal
        _obs.esec_secundar("SPV: validarea e-Transport pe mediul de test", e)
        return False, None, [spv_conector.mesaj_pentru_contabil(e, MESAJ_NETRIMISA)]
    ex, idx, _uit, errs = _parse_upload(r.text or "")
    ok = (getattr(r, "status_code", None) == 200 and ex == 0 and not errs)
    return ok, idx, (errs or ([] if ok else [(r.text or "")[:400]]))


def trimite(schema, principal, cif, xml, data_transport, intracom=False, mediu="prod", ref=None, acum=None):
    """
    Trimite o notificare e-Transport UIT. PORTI in ordine (niciuna sarita):
      1) GARDA DE TIMP (fereastra_uit) -> blocat daca prea devreme / expirat.
      2) IDEMPOTENCY (send viu pe xml_sha256, prod) -> deja_trimisa (upload ANAF nu e idempotent).
      3) VALIDARE pe TEST (nu exista validator fara auth) -> nevalidat, NU trimite pe prod.
      4) UPLOAD (prod) -> scrie randul indiferent de rezultat (ok/eroare_upload + UIT + valabilitate).
    Intoarce {stare, ...}. NU face stareMesaj sincron.
    """
    sha = hashlib.sha256(xml.encode("utf-8")).hexdigest()
    fer = fereastra_uit(data_transport, intracom, acum)
    if not fer["poate_trimite"]:                                  # POARTA 1
        return {"stare": "blocat_timp", "mesaj": fer["mesaj"], "fereastra": fer}

    if mediu == "prod":                                          # POARTA 2
        with db.get_conn() as conn:
            with conn.cursor() as cur:
                refuz = _poarta_vie(cur, schema, sha)
                if refuz:
                    return refuz

    val_ok, _vidx, val_err = valideaza_pe_test(principal, cif, xml)   # POARTA 3
    if not val_ok:
        return {"stare": "nevalidat", "erori": val_err}
    if mediu == "test":
        return {"stare": "validat_test", "fereastra": fer}

    # POARTA 4: upload prod + scrie randul
    # [lotul 10, C73 / U2] poarta 2 se reia AICI, sub lacăt, în tranzacția rândului «pregătit»: între ea și scriere a trecut validarea
    # pe test, iar o a doua cerere simultană ar fi încărcat aceeași notificare (UIT dublu) și ar fi căzut cu 500 la scrierea rezultatului
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            refuz = _poarta_vie(cur, schema, sha)
            if refuz:
                return refuz
            cur.execute(f"""INSERT INTO {schema}.etransport_trimiteri
                (mediu, stare, data_transport, intracom, uit_valabil_pana, ref_declarant, xml_trimis, xml_sha256, trimis_la)
                VALUES ('prod','pregatit',%s,%s,%s,%s,%s,%s, now()) RETURNING id""",
                (fer["data_transport"], intracom, fer["uit_valabil_pana"], ref, xml, sha))
            tid = cur.fetchone()[0]
    rez = {"trimitere_id": tid, "xml_sha256": sha, "fereastra": fer}
    try:
        r = upload_uit(principal, cif, xml, mediu="prod")
        ex, index, uit, errs = _parse_upload(r.text or "")
        rez.update({"http": r.status_code, "execution_status": ex, "index_incarcare": index,
                    "uit": uit, "errors": errs, "raspuns": r.text})
        if r.status_code == 200 and ex == 0 and index:
            stare, errmsg = "incarcat", None
        else:
            stare, errmsg = "nok", ("\n".join(errs) if errs else (r.text or "")[:4000])
    except Exception as e:  # noqa: BLE001 — 403 fără drept, conectorul, rețeaua: rândul se scrie oricum, cu motivul spus pe înțelesul omului
        _obs.esec_secundar("SPV: încărcarea e-Transport", e)
        mesaj = spv_conector.mesaj_pentru_contabil(e, MESAJ_NETRIMISA)
        rez.update({"fara_drept": isinstance(e, spv_conector.EroareSpvFaraDrept), "raspuns": mesaj})
        stare, errmsg, index, ex, uit = "eroare_upload", mesaj, None, None, None
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            # [lotul 10, C73 / U2] rândul ar deveni al doilea viu al notificării (numai peste o încărcare mai lungă decât fereastra porții):
            # UIT-ul primit nu se pierde într-un 500 — se scrie, cu dublura numită, iar rândul rămâne «pregătit» (nu e al doilea viu)
            try:
                with _chei.refuza_dublura(cur, ("uq_etransport_trimiteri_viu",), lambda cur, e: _chei.CheieDublata(
                        "ANAF a primit și această încărcare (UIT %s), dar notificarea avea deja o trimitere vie: verifică în SPV și "
                        "anulează UIT-ul dublat." % (uit or "?"))):
                    cur.execute(f"""UPDATE {schema}.etransport_trimiteri
                        SET stare=%s, index_incarcare=%s, execution_status=%s, uit=%s, error_message=%s, actualizat_la=now()
                        WHERE id=%s""", (stare, index, ex, uit, errmsg, tid))
            except _chei.CheieDublata as e:
                cur.execute(f"""UPDATE {schema}.etransport_trimiteri
                    SET index_incarcare=%s, execution_status=%s, uit=%s, error_message=%s, actualizat_la=now() WHERE id=%s""",
                            (index, ex, uit, str(e), tid))
                stare, rez["mesaj"] = "dublura", str(e)
    rez["stare"] = stare
    return rez


#: [lotul 10, C73 / U2] cât timp o trimitere «pregătit» e „în curs” (aceeași fereastră ca la e-Factura, `efactura_trimitere`)
FEREASTRA_IN_CURS_MIN = 10
MESAJ_IN_CURS = ("Notificarea aceasta e deja în curs de trimitere către ANAF (pornită la %s). Așteaptă câteva secunde rezultatul ei; o a "
                 "doua încărcare ar da un al doilea cod UIT pentru același transport.")


def _poarta_vie(cur, schema, sha):
    """[lotul 10, C73 / U2] Poarta de idempotență, SERIALIZATĂ pe notificare (lacăt de tranzacție pe amprenta XML-ului, ca în
    `migrare_nr_curent_note`): trimiterea vie (incarcat/ok) -> „deja_trimisa”; o trimitere «pregătit» pornită în ultimele
    `FEREASTRA_IN_CURS_MIN` minute -> „in_curs”. Altfel None. Rândul «pregătit» nu e în indexul `uq_etransport_trimiteri_viu`, deci
    fără poarta asta două cereri simultane încărcau amândouă."""
    cur.execute("SELECT pg_advisory_xact_lock(hashtext(%s))", ("etransport:%s:%s" % (schema, sha),))
    cur.execute(f"""SELECT id, stare, uit FROM {schema}.etransport_trimiteri
        WHERE xml_sha256=%s AND mediu='prod' AND stare IN ('incarcat','ok') LIMIT 1""", (sha,))
    viu = cur.fetchone()
    if viu:
        return {"stare": "deja_trimisa", "trimitere_id": viu[0], "uit": viu[2]}
    cur.execute(f"""SELECT id, trimis_la FROM {schema}.etransport_trimiteri
        WHERE xml_sha256=%s AND mediu='prod' AND stare='pregatit' AND trimis_la > now() - %s * interval '1 minute'
        ORDER BY id DESC LIMIT 1""", (sha, FEREASTRA_IN_CURS_MIN))
    r = cur.fetchone()
    if r:
        from zoneinfo import ZoneInfo
        from core import pdf_util as _pu
        return {"ok": False, "stare": "in_curs", "trimitere_id": r[0],
                "mesaj": MESAJ_IN_CURS % _pu.data_ro(r[1].astimezone(ZoneInfo("Europe/Bucharest")), "cu_ora")}
    return None
