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
from core import spv_conector
from core.common import cfg

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
def fereastra_uit(data_transport, intracom=False, acum=None):
    """
    Verdictul ferestrei legale UIT (ARHITECTURA_SPV.md), pur. data_transport = date sau 'YYYY-MM-DD'.
    Reguli: declarare max 3 zile INAINTE de data transportului; UIT valabil 5 zile (national) /
    15 zile (intracomunitar). Folosire dupa expirare = blocata. Intoarce dict cu verdictul.
    """
    acum = acum if acum is not None else date.today()
    dt = data_transport if isinstance(data_transport, date) else \
        datetime.strptime(str(data_transport)[:10], "%Y-%m-%d").date()
    zile_val = 15 if intracom else 5
    valabil_pana = dt + timedelta(days=zile_val)
    prea_devreme = (dt - acum).days > 3
    expirat = acum > valabil_pana
    poate_trimite = not prea_devreme and not expirat
    if prea_devreme:
        mesaj = "Prea devreme: se declara cu MAX 3 zile inainte (transport %s)." % dt.isoformat()
    elif expirat:
        mesaj = "UIT expirat: valabilitatea (%s) a trecut." % valabil_pana.isoformat()
    else:
        mesaj = "OK - UIT valabil pana la %s (%d zile)." % (valabil_pana.isoformat(), zile_val)
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
        return False, None, ["auth/drept TEST: %s" % e]
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
                cur.execute(f"""SELECT id, stare, uit FROM {schema}.etransport_trimiteri
                    WHERE xml_sha256=%s AND mediu='prod' AND stare IN ('incarcat','ok') LIMIT 1""", (sha,))
                viu = cur.fetchone()
                if viu:
                    return {"stare": "deja_trimisa", "trimitere_id": viu[0], "uit": viu[2]}

    val_ok, _vidx, val_err = valideaza_pe_test(principal, cif, xml)   # POARTA 3
    if not val_ok:
        return {"stare": "nevalidat", "erori": val_err}
    if mediu == "test":
        return {"stare": "validat_test", "fereastra": fer}

    # POARTA 4: upload prod + scrie randul
    with db.get_conn() as conn:
        with conn.cursor() as cur:
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
    except spv_conector.EroareSpvFaraDrept as e:
        rez.update({"fara_drept": True, "raspuns": str(e)})
        stare, errmsg, index, ex, uit = "eroare_upload", "403 fara drept e-Transport: %s" % e, None, None, None
    except Exception as e:
        rez.update({"raspuns": str(e)})
        stare, errmsg, index, ex, uit = "eroare_upload", "exceptie upload: %s" % str(e)[:2000], None, None, None
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(f"""UPDATE {schema}.etransport_trimiteri
                SET stare=%s, index_incarcare=%s, execution_status=%s, uit=%s, error_message=%s, actualizat_la=now()
                WHERE id=%s""", (stare, index, ex, uit, errmsg, tid))
    rez["stare"] = stare
    return rez
