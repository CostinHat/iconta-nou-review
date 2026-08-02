# -*- coding: utf-8 -*-
"""D2 (02.08.2026): tichetele de masa se acorda pe zile EFECTIV lucrate (HG 1045/2018 art.10 alin.3).
Zilele de CO/delegatie/absente/invoire din pontaj NU dau drept la tichet. Reversarea decuplarii 20.07."""
import pytest
from core import db as _db, tenant_provisioning as _tp
from core import salariati_api as sa, stat_plata_api as sp, pontaj as pj, perioada as per

SCHEMA = "ztest_tichete_pontaj"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


@pytest.fixture
def conn():
    _db.init_pool()
    with _db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCHEMA)
                cur.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), SCHEMA))
                cur.execute("SET search_path TO %s, public" % SCHEMA)
            yield c
        finally:
            c.rollback()


def _sid(conn):
    sid = sa.creeaza_salariat(conn, nume="POP", prenume="I", cnp="1900101410011",
                              data_angajare="2025-01-01", salariu_brut=5000, tip_norma="intreaga")["salariat_id"]
    with conn.cursor() as cur:
        cur.execute("UPDATE salariati SET tichet_masa_valoare = 40 WHERE id = %s", (sid,))
    per.confirma(conn, SCHEMA, 2026, 8, "pontaj", user_id=1)  # cap.23: fara confirmare, tichetele blocheaza
    return sid


CO5 = ["2026-08-03", "2026-08-04", "2026-08-05", "2026-08-06", "2026-08-07"]


def test_zile_fara_tichet_numara_exceptiile(conn):
    sid = _sid(conn)
    for zi in CO5:
        pj.seteaza(conn, SCHEMA, sid, zi, "concediu_odihna")
    assert pj.zile_fara_tichet(conn, SCHEMA, sid, 2026, 8) == 5


def test_tichete_scad_cu_zilele_de_co(conn):
    """5 zile de CO -> 5 tichete mai putine (HG 1045/2018 art.10 alin.3)."""
    sid = _sid(conn)
    fara = {f["id"]: f for f in sp.stat_plata(conn, SCHEMA, 2026, 8)}[sid]
    for zi in CO5:
        pj.seteaza(conn, SCHEMA, sid, zi, "concediu_odihna")
    cu = {f["id"]: f for f in sp.stat_plata(conn, SCHEMA, 2026, 8)}[sid]
    assert fara["tichete_zile"] - cu["tichete_zile"] == 5, \
        "CO nu reduce tichetele: fara=%s cu=%s" % (fara["tichete_zile"], cu["tichete_zile"])


def test_tichete_blocheaza_daca_pontaj_neconfirmat(conn):
    """cap.23: fara confirmarea pontajului, calculul tichetelor blocheaza cu blocaj motivat."""
    sid = sa.creeaza_salariat(conn, nume="POP", prenume="I", cnp="1900101410011",
                              data_angajare="2025-01-01", salariu_brut=5000, tip_norma="intreaga")["salariat_id"]
    with conn.cursor() as cur:
        cur.execute("UPDATE salariati SET tichet_masa_valoare = 40 WHERE id = %s", (sid,))
    with pytest.raises(per.PerioadaNeconfirmata):
        sp.stat_plata(conn, SCHEMA, 2026, 8)
    per.confirma(conn, SCHEMA, 2026, 8, "pontaj", user_id=1)
    st = {f["id"]: f for f in sp.stat_plata(conn, SCHEMA, 2026, 8)}[sid]   # dupa confirmare, merge
    assert st["tichete_zile"] > 0
