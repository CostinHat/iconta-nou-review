# -*- coding: utf-8 -*-
"""
Teste core/spv_poll.py (F178) — pe MOCK, niciodata pe ANAF real.

Formele stareMesaj/ZIP sunt din documentatia ANAF (dovedite din docs, NU live - la prima
interogare reala se logheaza raspunsul brut). Testeaza masina de stari cap-coada:
  incarcat -> in_prelucrare -> ok (+ZIP recipisa); incarcat -> nok (+ZIP erori);
  blocat in in_prelucrare peste prag -> investigatie; token expirat -> skip (nu marca);
  terminal (ok/nok) NU se re-interogheaza.
"""
import os
import io
import time
import zipfile

# env inainte de import (constante la import in modulele SPV)
from cryptography.fernet import Fernet
os.environ.setdefault("SPV_FERNET_KEY", Fernet.generate_key().decode())
os.environ.setdefault("JWT_SECRET", "test-secret-spv")
os.environ.setdefault("ANAF_CLIENT_ID", "TEST")
os.environ.setdefault("ANAF_REDIRECT_URI", "https://iconta.eu/anaf/oauth/callback")

import pytest

from core import db as _db
from core import spv_conector as s
from core import efactura_send as efs
from core import spv_poll as poll

# --- forme stareMesaj documentate ANAF ---
NS = 'xmlns="mfp:anaf:dgti:efactura:stareMesajFactura:v1"'
ST_PRELUCRARE = f'<header {NS} stare="in prelucrare"/>'
ST_OK = f'<header {NS} stare="ok" id_descarcare="4001"/>'
ST_NOK = f'<header {NS} stare="nok" id_descarcare="4002"/>'
ST_ERORI = f'<header {NS} stare="XML cu erori nepreluat de sistem"/>'
ST_GUNOI = '<html><body>500</body></html>'


class _Resp:
    def __init__(self, text="", content=b"", status=200):
        self.text = text; self.content = content; self.status_code = status


def _zip_cu_xml(nume="recipisa.xml", continut=b"<Invoice/>"):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr(nume, continut)
    return buf.getvalue()


# ============================================================
#  PUR — clasifica_stare pe formele documentate (fara DB)
# ============================================================
def test_clasifica_in_prelucrare_tanar():
    dec, st, idd = poll.clasifica_stare(ST_PRELUCRARE, vechime_zile=0, prag_zile=2)
    assert dec == "in_prelucrare"


def test_clasifica_in_prelucrare_vechi_investigatie():
    dec, st, idd = poll.clasifica_stare(ST_PRELUCRARE, vechime_zile=5, prag_zile=2)
    assert dec == "investigatie"   # timeout -> gri, nu abandon


def test_clasifica_ok_cu_id_descarcare():
    dec, st, idd = poll.clasifica_stare(ST_OK, vechime_zile=0)
    assert dec == "ok" and idd == "4001"


def test_clasifica_nok():
    dec, st, idd = poll.clasifica_stare(ST_NOK, vechime_zile=0)
    assert dec == "nok" and idd == "4002"


def test_clasifica_erori_e_nok():
    dec, st, idd = poll.clasifica_stare(ST_ERORI, vechime_zile=0)
    assert dec == "nok"           # "XML cu erori..." = terminal nok


def test_clasifica_gunoi_neasteptat_nu_verde():
    dec, st, idd = poll.clasifica_stare(ST_GUNOI, vechime_zile=0)
    assert dec == "neasteptat"    # forma neasteptata -> NU ok/verde


# ============================================================
#  INTEGRARE (DB + mock retea) — cu curatenie explicita
# ============================================================
def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


@pytest.fixture
def rand_incarcat():
    """Insereaza un rand 'incarcat' in tenant_002 (commit), il curata la final."""
    _db.init_pool()
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("""INSERT INTO tenant_002.efactura_trimiteri
                (factura_id, mediu, stare, xml_sha256, index_incarcare, trimis_la)
                VALUES (1,'test','incarcat','x','9001', now()) RETURNING id""")
            tid = cur.fetchone()[0]
    yield tid
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DELETE FROM tenant_002.efactura_trimiteri WHERE id=%s", (tid,))


def _stare_row(tid):
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("SELECT stare, finalizat_la, zip_raspuns_path, xml_semnat_sha256 "
                        "FROM tenant_002.efactura_trimiteri WHERE id=%s", (tid,))
            return cur.fetchone()


def test_poll_ok_descarca_recipisa(rand_incarcat, monkeypatch):
    monkeypatch.setattr(efs, "stare_mesaj", lambda p, i, m: _Resp(text=ST_OK))
    monkeypatch.setattr(efs, "descarca", lambda p, i, m: _Resp(content=_zip_cu_xml()))
    stat = {"ok": 0, "nok": 0, "in_prelucrare": 0, "investigatie": 0, "skip_auth": 0, "neasteptat": 0}
    row = (rand_incarcat, 1, "test", "9001", "incarcat", poll.datetime.now(poll.timezone.utc))
    poll.poll_rand("tenant_002", row, poll.datetime.now(poll.timezone.utc), stat)
    stare, finalizat, zippath, xsha = _stare_row(rand_incarcat)
    assert stare == "ok" and finalizat is not None
    assert zippath and xsha   # recipisa salvata + amprenta


def test_poll_skip_auth_nu_marcheaza(rand_incarcat, monkeypatch):
    def _cade(p, i, m):
        raise s.EroareSpvNeconectat("token mort")
    monkeypatch.setattr(efs, "stare_mesaj", _cade)
    stat = {"ok": 0, "nok": 0, "in_prelucrare": 0, "investigatie": 0, "skip_auth": 0, "neasteptat": 0}
    row = (rand_incarcat, 1, "test", "9001", "incarcat", poll.datetime.now(poll.timezone.utc))
    poll.poll_rand("tenant_002", row, poll.datetime.now(poll.timezone.utc), stat)
    assert stat["skip_auth"] == 1
    assert _stare_row(rand_incarcat)[0] == "incarcat"   # NEATINSA (auth-fail != respinsa)


def test_de_polat_exclude_terminale(rand_incarcat, monkeypatch):
    # marcheaza randul ok -> nu mai apare in de_polat (terminal, ne-repollat)
    poll._seteaza("tenant_002", rand_incarcat, "ok", finalizat=True)
    with _db.get_conn() as c:
        ids = [r[0] for r in poll.de_polat(c, "tenant_002")]
    assert rand_incarcat not in ids
