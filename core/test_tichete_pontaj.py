# -*- coding: utf-8 -*-
"""D2 (02.08.2026): tichetele de masa pe zile EFECTIV lucrate (HG 1045/2018 art.10 alin.3). Zilele de
CO/delegatie/absente/invoire din pontaj NU dau drept la tichet. Calculul cere pontaj CONFIRMAT (cap.23):
o modificare de-confirma, deci se confirma DUPA ce pontajul lunii e complet."""
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
                              data_angajare="2025-01-01", salariu_brut=5000, tip_norma="intreaga",
                              cor="522101")["salariat_id"]
    with conn.cursor() as cur:
        cur.execute("UPDATE salariati SET tichet_masa_valoare = 40 WHERE id = %s", (sid,))
    return sid


CO5 = ["2026-08-03", "2026-08-04", "2026-08-05", "2026-08-06", "2026-08-07"]


def test_zile_fara_tichet_numara_exceptiile(conn):
    sid = _sid(conn)
    for zi in CO5:
        pj.seteaza(conn, SCHEMA, sid, zi, "concediu_odihna")
    assert pj.zile_fara_tichet(conn, SCHEMA, sid, 2026, 8) == 5


def test_tichete_blocheaza_daca_pontaj_neconfirmat(conn):
    """[#1/#3] cap.23: fara confirmarea pontajului, tichetele raman BLOCATE - dar statul NU mai arunca
    (deadlock: 423 omora ecranul -> butonul Pontaj inaccesibil). Randul se intoarce cu tichete=0 + flag
    pontaj_neconfirmat; dupa confirmare, tichetele apar."""
    sid = _sid(conn)
    st0 = {f["id"]: f for f in sp.stat_plata(conn, SCHEMA, 2026, 8)}[sid]  # NU arunca
    assert st0["pontaj_neconfirmat"] is True
    assert st0["tichete_zile"] == 0 and st0["tichete_nominal"] == 0
    per.confirma(conn, SCHEMA, 2026, 8, "pontaj", user_id=1)
    st = {f["id"]: f for f in sp.stat_plata(conn, SCHEMA, 2026, 8)}[sid]
    assert st.get("pontaj_neconfirmat") is False
    assert st["tichete_zile"] > 0


def test_tichete_scad_cu_zilele_de_co(conn):
    """5 zile de CO -> 5 tichete mai putine. Re-confirmare dupa editare (seteaza de-confirma)."""
    sid = _sid(conn)
    per.confirma(conn, SCHEMA, 2026, 8, "pontaj", user_id=1)          # pontaj gol (tot prezent), confirmat
    fara = {f["id"]: f for f in sp.stat_plata(conn, SCHEMA, 2026, 8)}[sid]
    for zi in CO5:
        pj.seteaza(conn, SCHEMA, sid, zi, "concediu_odihna")          # editare -> de-confirma
    assert per.e_confirmat(conn, SCHEMA, 2026, 8, "pontaj")["confirmat"] is False   # de-confirmat automat
    per.confirma(conn, SCHEMA, 2026, 8, "pontaj", user_id=1)          # re-confirmare
    cu = {f["id"]: f for f in sp.stat_plata(conn, SCHEMA, 2026, 8)}[sid]
    assert fara["tichete_zile"] - cu["tichete_zile"] == 5


def test_pontaj_blocat_dupa_depunere_d112(conn):
    """cap.23 reversibilitate: dupa D112 depusa pe luna, editarea pontajului se blocheaza (-> rectificativa)."""
    sid = _sid(conn)
    with conn.cursor() as cur:
        cur.execute("INSERT INTO public.declaratii_depuse (tenant_id,an,luna,tip,data_depunere,sursa,nr_depunere) "
                    "VALUES (99999,2026,8,'d112',now(),'test',1)")
    r = pj.seteaza(conn, SCHEMA, sid, "2026-08-10", "concediu_odihna", tenant_id=99999)
    assert r["ok"] is False and "rectificativa" in r["mesaj"].lower()
    r2 = pj.seteaza(conn, SCHEMA, sid, "2026-08-10", "concediu_odihna")  # fara tenant_id -> nu se verifica depunerea
    assert r2["ok"] is True
