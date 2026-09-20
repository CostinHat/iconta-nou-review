# -*- coding: utf-8 -*-
"""C5 — importul de extras bancar e IDEMPOTENT la nivel de fisier (audit independent 2026-09-17).

Neconformitate (confirmata la sursa + functional 20.09): `reconciliere_api.importa_extras` insera
liniile fara cheie de dedup; reimportul aceluiasi extras (dublu-click / raspuns pierdut dupa commit)
dubla `extras_linii` -> contarile pe 5121 dublate.

Fix (decizia Costin 20.09, varianta A): idempotenta la nivel de FISIER, pe hash de continut, prin
tabelul `extras_import` cu UNIQUE pe `fisier_hash`. Reimportul aceluiasi fisier NU insereaza nimic si
raporteaza „extras deja importat: N linii". Doua tranzactii REALE identice in ACELASI fisier raman
AMBELE (fara over-dedup) — de aia cheia e pe FISIER, nu pe continut de linie.

Temei: N/A — integritate tehnica (nu regula fiscala). Principiu conex CLAUDE.md §8 (date nealterate).

Probe end-to-end pe schema efemera din template (gated DB), ROLLBACK la iesire.
"""
import io
import pytest

from core import db as _db
from core import tenant_provisioning as _tprov
from core import reconciliere_api as _rec

_SCH = "efemer_c5_idem"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


_DB = _db_ok()
pytestmark = pytest.mark.skipif(not _DB, reason="DB indisponibil")


@pytest.fixture()
def conn():
    _db.init_pool()
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCH)
            cur.execute(_tprov.parametrizeaza_template(
                io.open("tenant_template.sql", encoding="utf-8").read(), _SCH))
            cur.execute("SET search_path TO %s, public" % _SCH)
            cur.execute("""INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,email,telefon,caen,
                           declarant_nume,declarant_prenume,declarant_functie,platitor_tva)
                           VALUES (1,'C5 SRL','RO14399840','s','B','B','e@x.ro','07','4690','P','I','A',true)""")
        c.commit()
    with _db.get_conn(_SCH) as c:
        yield c
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCH)
        c.commit()


_TZ = [{"data": "2026-03-10", "detalii": "PLATA FURNIZOR X", "suma": -119.00},
       {"data": "2026-03-11", "detalii": "INCASARE CLIENT Y", "suma": 238.00}]
_CONTINUT = b"data;detalii;suma\n2026-03-10;PLATA FURNIZOR X;-119.00\n2026-03-11;INCASARE CLIENT Y;238.00\n"


def _nr_linii(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM extras_linii")
        return cur.fetchone()[0]


# ── PROBA: reimportul aceluiasi fisier NU dubleaza + raporteaza deja_importat ──
def test_C5_reimport_acelasi_fisier_nu_dubleaza(conn):
    r1 = _rec.importa_extras(conn, _SCH, _TZ, "extras_martie.csv", _CONTINUT)
    conn.commit()
    assert len(r1["linii"]) == 2 and not r1.get("deja_importat")
    assert _nr_linii(conn) == 2

    r2 = _rec.importa_extras(conn, _SCH, _TZ, "extras_martie.csv", _CONTINUT)  # REIMPORT identic
    conn.commit()
    assert r2.get("deja_importat") is True, "reimportul aceluiasi fisier trebuie recunoscut"
    assert r2["nr_linii"] == 2, "mesajul poarta cate linii avea importul initial"
    assert _nr_linii(conn) == 2, "reimportul NU adauga linii noi (idempotent)"


# ── CALIBRARE: un fisier DIFERIT se importa normal (gardul nu blocheaza tot) ──
def test_C5_fisier_diferit_se_importa(conn):
    _rec.importa_extras(conn, _SCH, _TZ, "martie.csv", _CONTINUT)
    conn.commit()
    tz2 = [{"data": "2026-04-01", "detalii": "PLATA FURNIZOR Z", "suma": -50.00}]
    cont2 = b"data;detalii;suma\n2026-04-01;PLATA FURNIZOR Z;-50.00\n"
    r = _rec.importa_extras(conn, _SCH, tz2, "aprilie.csv", cont2)
    conn.commit()
    assert not r.get("deja_importat") and len(r["linii"]) == 1
    assert _nr_linii(conn) == 3


# ── CALIBRARE (fara over-dedup): doua tranzactii REALE identice in ACELASI fisier -> AMBELE pastrate ──
def test_C5_doua_tranzactii_identice_in_acelasi_fisier_ambele_pastrate(conn):
    tz = [{"data": "2026-05-02", "detalii": "COMISION CARD", "suma": -5.00},
          {"data": "2026-05-02", "detalii": "COMISION CARD", "suma": -5.00}]
    cont = b"data;detalii;suma\n2026-05-02;COMISION CARD;-5.00\n2026-05-02;COMISION CARD;-5.00\n"
    r = _rec.importa_extras(conn, _SCH, tz, "mai.csv", cont)
    conn.commit()
    assert not r.get("deja_importat")
    assert _nr_linii(conn) == 2, ("cheia e pe FISIER, nu pe continut de linie: doua tranzactii real "
                                  "identice in acelasi extras raman ambele, nu se over-dedup")


# ── CALIBRARE: fara `continut` (apel programatic) comportamentul vechi ramane ──
def test_C5_fara_continut_nu_gateaza(conn):
    _rec.importa_extras(conn, _SCH, _TZ, "x.csv")  # fara continut
    _rec.importa_extras(conn, _SCH, _TZ, "x.csv")  # fara continut -> NU se gateaza
    conn.commit()
    assert _nr_linii(conn) == 4, "fara hash de fisier, gardul C5 nu se aplica (apel programatic)"
