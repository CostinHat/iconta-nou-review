# -*- coding: utf-8 -*-
"""
core/spv_poll.py — cron de POLL e-Factura (F178): jumatatea de PRIMIRE a propriului send.

Fara el, o factura urcata ramane blocata in 'incarcat' la infinit - nimic n-o avanseaza.
Masina de stari e INCOMPLETA fara poll. Ruleaza pe timer (spv-poll.timer), interogheaza
stareMesaj pentru trimiterile in asteptare si, la verdict terminal, descarca recipisa.

GARDURI (nenegociabile):
- Reutilizeaza infra: apel_anaf (prin efactura_send.stare_mesaj/descarca) pe tokenul PRINCIPALULUI
  (cabinet XOR gratuit, derivat din tenant, acelasi model ca spv_principal). NU duplica token/refresh.
- Scope strict: DOAR randurile incarcat/in_prelucrare/investigatie cu index_incarcare. Terminale
  (ok/nok/eroare_upload) NU se re-interogheaza (nu intra in de_polat).
- Token expirat intre upload si poll: apel_anaf face refresh; daca tokenul e mort (EroareSpv) ->
  SKIP randul, reia data viitoare. NU marca randul (auth-fail != factura respinsa).
- Rata: sleep intre randuri + timer rar. Verificat la sursa: 1000 apeluri/min (apel_anaf face 429
  backoff). Cuota ZILNICA stareMesaj/descarcare NU e documentata in sursele locale -> conservator:
  un poll per rand per rulare, timer la 30 min. De confirmat la sursa la primul patron real.
- Timeout: blocat in in_prelucrare peste PRAG_INVESTIGATIE_ZILE -> stare='investigatie' (GRI, verifica
  manual in SPV), nu abandon tacit. Pragul e conservator (ANAF nu documenteaza public timpul de
  prelucrare) - de confirmat la sursa; filozofia control_incrucisat: gri, nu fals verde.
- Parsare DEFENSIVA: logheaza raspunsul brut integral; forma neasteptata -> NU avanseaza spre verde
  (decizie 'neasteptat' -> gri + log, nu swallow tacit).
"""
import os
import sys
import io
import hashlib
import zipfile
from datetime import datetime, timezone, timedelta

from core import db
from core import spv_conector
from core import efactura_send as efs

INTERVAL_SEC = float(os.environ.get("SPV_POLL_INTERVAL_SEC", "1.0"))       # intre randuri (rata-friendly)
PRAG_INVESTIGATIE_ZILE = int(os.environ.get("SPV_POLL_PRAG_ZILE", "2"))    # conservator; de confirmat la sursa
ZIP_DIR = os.environ.get("EFACTURA_ZIP_DIR", os.path.expanduser("~/iconta_nou/efactura_zip"))


# ---- DECIZIE PURA (unit-testabila, fara DB/retea) ----
def clasifica_stare(text, vechime_zile, prag_zile=None):
    """
    Din raspunsul stareMesaj + vechimea trimiterii -> (decizie, stare_anaf, id_descarcare).
    decizie in {in_prelucrare, investigatie, ok, nok, neasteptat}. PURA.
    """
    prag = prag_zile if prag_zile is not None else PRAG_INVESTIGATIE_ZILE
    stare_anaf, id_desc = efs._parse_stare(text)
    sl = (stare_anaf or "").lower()
    if "prelucr" in sl:                       # inca in prelucrare la ANAF
        return ("investigatie" if vechime_zile > prag else "in_prelucrare"), stare_anaf, id_desc
    if sl == "ok":
        return "ok", stare_anaf, id_desc
    if "nok" in sl or "eroare" in sl or "erori" in sl:
        return "nok", stare_anaf, id_desc
    return "neasteptat", stare_anaf, id_desc  # forma neasteptata -> gri, NU verde


def _principal_pentru_schema(conn, schema):
    """Deleg la helper-ul partajat (efactura_send) - un singur loc pt derivarea principalului."""
    return efs.principal_pentru_schema(conn, schema)


def de_polat(conn, schema):
    """Randurile de interogat: doar non-terminale cu index. Terminale NU se re-interogheaza."""
    with conn.cursor() as cur:
        cur.execute(f"""SELECT id, factura_id, mediu, index_incarcare, stare, trimis_la
            FROM {schema}.efactura_trimiteri
            WHERE stare IN ('incarcat','in_prelucrare','investigatie') AND index_incarcare IS NOT NULL
            ORDER BY trimis_la""")
        return cur.fetchall()


def _seteaza(schema, tid, stare, err=None, id_desc=None, zip_path=None, xml_sha=None, finalizat=False):
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(f"""UPDATE {schema}.efactura_trimiteri
                SET stare=%s, error_message=COALESCE(%s, error_message),
                    id_descarcare=COALESCE(%s, id_descarcare),
                    zip_raspuns_path=COALESCE(%s, zip_raspuns_path),
                    xml_semnat_sha256=COALESCE(%s, xml_semnat_sha256),
                    actualizat_la=now(),
                    finalizat_la=CASE WHEN %s THEN now() ELSE finalizat_la END
                WHERE id=%s""", (stare, err, id_desc, zip_path, xml_sha, finalizat, tid))


def _descarca_recipisa(schema, tid, principal, id_desc, mediu):
    """Descarca ZIP-ul recipisei, salveaza fisier + sha256 al XML-ului semnat. Best-effort."""
    if not id_desc:
        return None, None
    try:
        r = efs.descarca(principal, id_desc, mediu)
    except spv_conector.EroareSpv:
        return None, None
    if r.status_code != 200 or not r.content:
        return None, None
    os.makedirs(ZIP_DIR, exist_ok=True)
    path = os.path.join(ZIP_DIR, "%s_%s_%s.zip" % (schema, tid, id_desc))
    with open(path, "wb") as f:
        f.write(r.content)
    xml_sha = None
    try:
        zf = zipfile.ZipFile(io.BytesIO(r.content))
        for n in zf.namelist():
            if n.lower().endswith(".xml") and "semnatura" not in n.lower():
                xml_sha = hashlib.sha256(zf.read(n)).hexdigest()
                break
    except Exception:
        pass
    return path, xml_sha


def poll_rand(schema, row, acum, stat):
    """Interogheaza un rand + aplica decizia. Un rand = o tranzactie (via _seteaza)."""
    tid, factura_id, mediu, index, stare, trimis_la = row
    with db.get_conn() as conn:
        principal = _principal_pentru_schema(conn, schema)
    try:
        r = efs.stare_mesaj(principal, index, mediu)   # apel_anaf face refresh la token expirat
    except spv_conector.EroareSpv as e:
        stat["skip_auth"] += 1
        print("  SKIP auth %s/%s (index %s): %s" % (schema, tid, index, e), file=sys.stderr)
        return   # NU marca randul - auth-fail != factura respinsa
    text = r.text or ""
    print("  RAW stareMesaj %s/%s (index %s): %s" % (schema, tid, index, text[:600]))
    vechime = (acum - trimis_la).days if trimis_la else 0
    decizie, stare_anaf, id_desc = clasifica_stare(text, vechime)
    if decizie == "in_prelucrare":
        if stare != "in_prelucrare":
            _seteaza(schema, tid, "in_prelucrare")
        stat["in_prelucrare"] += 1
    elif decizie == "investigatie":
        _seteaza(schema, tid, "investigatie",
                 err="blocat in prelucrare de %d zile - verifica in SPV" % vechime)
        stat["investigatie"] += 1
    elif decizie == "ok":
        path, xsha = _descarca_recipisa(schema, tid, principal, id_desc, mediu)
        _seteaza(schema, tid, "ok", id_desc=id_desc, zip_path=path, xml_sha=xsha, finalizat=True)
        stat["ok"] += 1
    elif decizie == "nok":
        path, xsha = _descarca_recipisa(schema, tid, principal, id_desc, mediu)
        _seteaza(schema, tid, "nok", id_desc=id_desc, zip_path=path, xml_sha=xsha,
                 err="stareMesaj=nok: %s" % text[:500], finalizat=True)
        stat["nok"] += 1
    else:  # neasteptat - NU avanseaza spre verde
        stat["neasteptat"] += 1
        print("  NEASTEPTAT %s/%s: stare_anaf=%r raw=%s" % (schema, tid, stare_anaf, text[:300]), file=sys.stderr)


def ruleaza(acum=None, _dormi=None):
    import time
    _dormi = _dormi or time.sleep
    acum = acum or datetime.now(timezone.utc)
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT schema_name FROM information_schema.schemata "
                        "WHERE schema_name ~ '^tenant_[0-9]+$' ORDER BY schema_name")
            scheme = [r[0] for r in cur.fetchall()]
    stat = {"ok": 0, "nok": 0, "in_prelucrare": 0, "investigatie": 0, "skip_auth": 0, "neasteptat": 0}
    for schema in scheme:
        with db.get_conn() as conn:
            randuri = de_polat(conn, schema)
        for row in randuri:
            try:
                poll_rand(schema, row, acum, stat)
            except Exception as e:
                print("  EROARE poll %s/%s: %s" % (schema, row[0], e), file=sys.stderr)
            _dormi(INTERVAL_SEC)
    print("%s spv_poll terminat: %s" % (datetime.now(timezone.utc).isoformat(), stat))
    return stat


if __name__ == "__main__":
    from core import cron  # [R74] alerta la esec + bataie la reusita
    cron.ruleaza("spv_poll", ruleaza)
