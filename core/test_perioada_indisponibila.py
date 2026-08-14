# -*- coding: utf-8 -*-
"""Blocaj MOTIVAT pentru cote de regula cu data_in tarzie (01.08.2026). O cota ceruta de un calcul pentru
o perioada anterioara primei valori cunoscute NU crapa cu exceptie bruta (500 in UI), ci ridica
PerioadaIndisponibila - mesaj cu cele 4 elemente + tag PERIOADA_BLOCATA (handler-ul global -> 423).
Decizie: LIMITA DECLARATA, nu backfill (nu se inventeaza o valoare, nu se cerceteaza istoricul acum)."""
from datetime import date

import pytest

from core import common as c
from core import db as _db, tenant_provisioning as _tp
from core import salariati_api as sa, adeverinta, salarizare as sz


def test_cota_pre_data_ridica_blocaj_motivat():
    """O valoare ceruta INAINTE de prima ei aparitie -> PerioadaIndisponibila (subclasa de ValueError),
    cu tag PERIOADA_BLOCATA + prima_data corecta. salariu_minim incepe la 2025-01-01 (DATA_START_SISTEM);
    cerut pentru 2024 -> blocaj. (plafon_facilitate si tichet completate pe 2025 - B1 - exemplul e sub podea.)"""
    with pytest.raises(c.PerioadaIndisponibila) as ei:
        c.cota("salariu_minim", date(2024, 6, 1))
    assert ei.value.prima_data == date(2025, 1, 1)
    assert isinstance(ei.value, ValueError)              # `except ValueError` existent ramane valabil
    assert "PERIOADA_BLOCATA:" in str(ei.value)


def test_calcul_salariu_pre_2026_blocaj_2026_ok():
    """calcul_salariu propaga blocajul motivat pentru OCTOMBRIE 2025 (tichet_masa_plafon neverificat la
    sursa - gol intre 40,18 sep si 45 nov, B1); pentru restul 2025 (ex. mai) si pentru 2026 merge."""
    with pytest.raises(ValueError):
        sz.calcul_salariu(4050, la_data=date(2025, 10, 1), norma_intreaga=True, venit_brut_total=4050)
    r = sz.calcul_salariu(4050, la_data=date(2026, 8, 1), norma_intreaga=True, venit_brut_total=4050)
    assert r["net"] > 0
    r2 = sz.calcul_salariu(4050, la_data=date(2025, 5, 1), norma_intreaga=True, venit_brut_total=4050)
    assert r2["net"] > 0


def test_mesaj_blocaj_ajunge_la_user():
    """Contractul pe care se bazeaza handler-ul global (main.py _handler_perioada_blocata): tag
    PERIOADA_BLOCATA -> ramura 423 (nu re-ridica = 500); textul de dupa (prima linie) = detaliul aratat
    utilizatorului. Replicam extractia handler-ului ca sa aratam mesajul cu cele 4 elemente."""
    exc = c.PerioadaIndisponibila("plafon_facilitate_salariu_minim", date(2025, 6, 1), date(2026, 1, 1))
    msg = str(exc)
    assert "PERIOADA_BLOCATA:" in msg
    detaliu = msg.split("PERIOADA_BLOCATA:")[1].split("\n")[0].strip()
    user = "Perioada %s." % detaliu
    assert "2025-06-01 nu poate fi calculata" in user      # ce s-a oprit
    assert "nu e definita inainte de 2026-01-01" in user    # de ce (valoare neverificata la sursa)
    assert "disponibil de la 2026-01-01" in user            # ce se poate face
    assert "completeaza in COTE la sursa" in user           # cine decide (dezvoltator)


# ---- proba pe calea reala a adeverintei (schema efemera, ROLLBACK) ----
SCHEMA_T = "ztest_perioada_indisp"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_adeverinta_2025_blocaj_2026_ok():
    """adeverinta pentru o luna 2025 -> blocaj motivat (nu traceback); pentru 2026 -> merge (net)."""
    _db.init_pool()
    with _db.get_conn() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCHEMA_T)
                cur.execute(_tp.parametrizeaza_template(
                    open("tenant_template.sql", encoding="utf-8").read(), SCHEMA_T))
                cur.execute("SET search_path TO %s, public" % SCHEMA_T)
            sid = sa.creeaza_salariat(conn, nume="POP", prenume="I", cnp="1900101410011",
                                      data_angajare="2025-01-01", salariu_brut=4050,
                                      tip_norma="intreaga", cor="522101")["salariat_id"]
            with pytest.raises(ValueError):
                adeverinta.date_auto(conn, SCHEMA_T, sid, 2025, 10)  # gol tichet octombrie 2025 (B1)
            d2026 = adeverinta.date_auto(conn, SCHEMA_T, sid, 2026, 8)
            assert d2026 is not None and d2026["net"] > 0
        finally:
            conn.rollback()
