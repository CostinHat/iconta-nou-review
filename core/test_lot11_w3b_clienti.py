# -*- coding: utf-8 -*-
"""[lotul 11, subagentul w3b, deficiența 440 pe server — comanda Costin 11.1 pct.16, verbatim] „toate erorile apar deodată, fiecare cu
textul ei, în casetă și lângă câmp.” Fișa clientului / furnizorului (B35 din lista U0): numele lipsă se refuza înaintea județului (un
singur refuz, fără câmp), iar o localitate peste coloană (`oras character varying(100)`) cădea în INSERT / UPDATE (DataError -> 500).
Acum: numele, județul și lungimile, toate deodată, cu `camp` = numele din cerere (ecranul: `${P}-${camp}-${cheie}`).

Temei: N/A — contractul refuzului (G10) și lungimile coloanelor din `tenant_template.sql` (`clienti`, `furnizori`), confruntate mai jos
cu schema bazei.
"""
import io
import os
import re

import pytest

from core import clienti_api as ca, db as _db, erori, tenant_provisioning as _tp

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SCH = "efemer_lot11_w3b_cl"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture
def conn():
    if not _db_ok():
        pytest.skip("DB indisponibil")
    with _db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCH)
                cur.execute(_tp.parametrizeaza_template(io.open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read(), _SCH))
                cur.execute("SET LOCAL search_path TO %s, public" % _SCH)
            yield c
        finally:
            c.rollback()


def _campuri(e):
    return [c["camp"] for c in e.value.detaliu["erori_campuri"]]


def test_b35_clientul_nou_refuza_numele_judetul_si_localitatea_deodata(conn):
    """Fără nume + județ necunoscut + localitate de 101 caractere: trei erori, nimic scris. MUTAȚIE: refuzul numelui ridicat înainte
    de `_curata` (forma veche) -> pică."""
    with pytest.raises(erori.DateInvalide) as e:
        ca.creeaza_client(conn, " ", cui="14399840", oras="L" * 101, judet="Atlantida")
    assert _campuri(e) == ["oras", "judet", "nume"], e.value.detaliu   # 440: „toate erorile apar deodată”
    m = e.value.detaliu["mesaj"]
    # mesajul pe rânduri, fiecare eroare cu textul ei (core/test_garzi_pe_text.py: valoarea întreagă, nu „fragmentul apare”)
    assert m.split("\n— ") == ["Fișa clientului nu s-a salvat:", "Localitatea are cel mult 100 de caractere; are 101.",
                               "Județul 'Atlantida' nu e în listă: alege-l din listă (ex. Cluj, București).",
                               "Scrie numele clientului: fără el, fișa nu se poate salva."], m
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM clienti")
        assert cur.fetchone()[0] == 0


def test_b35_editarea_fisei_refuza_numele_golit_si_localitatea_lunga(conn):
    """Pe drumul ecranului Clienți (PUT cu numele golit și localitatea lungă): două erori; furnizorul la fel. MUTAȚIE: verificarea
    lungimii oprită (`if False:`) -> localitatea lipsește din refuz (și ar cădea în bază, DataError) -> pică."""
    cid = ca.creeaza_client(conn, "CLIENT W3B SRL", oras="Cluj-Napoca", judet="CJ")["client_id"]
    with pytest.raises(erori.DateInvalide) as e:
        ca.actualizeaza_client(conn, cid, nume="", oras="O" * 150)
    assert _campuri(e) == ["oras", "nume"], e.value.detaliu
    fid = ca.creeaza_furnizor(conn, "FURNIZOR W3B SRL")["furnizor_id"]
    with pytest.raises(erori.DateInvalide) as e:
        ca.actualizeaza_furnizor(conn, fid, nume=" ", cod_postal="1" * 21)
    assert _campuri(e) == ["cod_postal", "nume"], e.value.detaliu


def test_limitele_fisei_sunt_ale_coloanelor(conn):
    """Garda: `clienti_api.LUNGIMI` = lungimile din `tenant_template.sql` și din schema creată, la amândouă tabelele. MUTAȚIE:
    `"oras": 120` -> pică."""
    sablon = io.open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read()
    for tabel in ("clienti", "furnizori"):
        bloc = re.search(r"CREATE TABLE TENANT_PLACEHOLDER\.%s \((.*?)\);" % tabel, sablon, re.S).group(1)
        din_sablon = {k: int(n) for k, n in re.findall(r"^\s*(\w+) character varying\((\d+)\)", bloc, re.M) if k in ca.LUNGIMI}
        assert din_sablon == ca.LUNGIMI, (tabel, din_sablon)
        with conn.cursor() as cur:
            cur.execute("SELECT column_name, character_maximum_length FROM information_schema.columns WHERE table_schema = %s "
                        "AND table_name = %s AND column_name = ANY(%s)", (_SCH, tabel, list(ca.LUNGIMI)))
            assert dict(cur.fetchall()) == ca.LUNGIMI, tabel
