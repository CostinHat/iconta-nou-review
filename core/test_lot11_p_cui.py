# -*- coding: utf-8 -*-
"""[lotul 11, decizia Costin 10.3 pct.4, verbatim în DECIZII „Comanda 10.3”] „CUI-ul se păstrează fără «RO» și fără spații; «RO» apare doar
la afișare, după starea de plătitor de TVA.”

Temei (forma afișată): CF art.318 alin.(1) — „Codul de înregistrare în scopuri de TVA, atribuit conform art. 316 și 317 , are prefixul RO,
conform Standardului internațional ISO 3166 - alpha 2.” (anaf_surse/cod_fiscal_227_2015_consolidat.txt) — prefixul e al codului de TVA.
GARDA: un trigger pe fiecare coloană de cod fiscal (`core/migrare_cui_fara_ro.py`), deci niciun drum de scriere nu poate păstra „RO” /
spații; garda structurală de mai jos pică dacă șablonul capătă o coloană de cod fiscal fără trigger.
Fixturile: schemă efemeră din `tenant_template.sql`, ROLLBACK; CUI-urile 14399840 / 2864518 (cifra de control verificată mai jos).
MUTAȚII: `EXPR` fără scoaterea lui „RO” -> `test_paritatea_python_sql` și `test_triggerul_normalizeaza_pe_orice_drum` pică; o tabelă scoasă
din `COLOANE_FIRMA` -> `test_fiecare_coloana_de_cod_fiscal_are_trigger` pică.
"""
import io
import re

import pytest

from core import cui_forma as cf, migrare_cui_fara_ro as m

MOSTRE = ["RO14399840", "ro 14399840", " RO 143 998 40 ", "14399840", "DE123456789", "EL 094014201", "", None, "RO", "ROMANIA",
          "RO12A", "2864518", "\tRO2864518\n"]


def test_fixtura_e_valida():
    from core.identitate import valideaza_cui
    assert valideaza_cui("14399840")[0] and valideaza_cui("2864518")[0]


def test_forma_pastrata_si_cea_afisata():
    assert cf.stocare("RO 14399840") == cf.stocare("ro14399840") == "14399840"   # fără „RO” și fără spații (decizia 10.3)
    assert cf.stocare("DE 123456789") == "DE123456789"                          # codul altui stat: prefixul e chiar codul (CF art.318 alin.(1))
    assert cf.stocare("") is None and cf.stocare("  ") is None and cf.stocare(None) is None
    assert cf.afisare("14399840", True) == "RO14399840"                         # plătitorul de TVA: „RO” + cifre (CF art.318 alin.(1))
    assert cf.afisare("RO14399840", False) == "14399840"                        # neplătitorul: fără prefix
    assert cf.afisare("14399840", None) == "14399840"                           # starea necunoscută: nu se ghicește prefixul
    assert cf.afisare("DE123456789", True) == "DE123456789"


def test_oglinda_din_sablon_e_cea_generata_de_migrare():
    t = io.open("tenant_template.sql", encoding="utf-8").read()
    i, j = t.index(m.MARCAJ_INCEPUT), t.index(m.MARCAJ_SFARSIT) + len(m.MARCAJ_SFARSIT)
    assert t[i:j] == m.sql("TENANT_PLACEHOLDER")


def test_fiecare_coloana_de_cod_fiscal_are_trigger():
    """Toate coloanele `cui` / `cif` / `*_cui` / `cif_*` / `cui_*` din șablon sunt în `COLOANE_FIRMA` (deci au triggerul)."""
    t = io.open("tenant_template.sql", encoding="utf-8").read()
    gasite = set()
    for tab, corp in re.findall(r"CREATE TABLE (?:IF NOT EXISTS )?TENANT_PLACEHOLDER\.(\w+)\s*\((.*?)\n\);", t, re.S):
        for col in re.findall(r"^\s+(\w+)\s+(?:text|character varying|varchar)", corp, re.M | re.I):
            if re.fullmatch(r"(\w+_)?(cui|cif)(_\w+)?", col):
                gasite.add((tab, col))
    for tab, col in re.findall(r"ALTER TABLE TENANT_PLACEHOLDER\.(\w+) ADD COLUMN IF NOT EXISTS (\w+) (?:text|character varying|varchar)", t, re.I):
        if re.fullmatch(r"(\w+_)?(cui|cif)(_\w+)?", col):
            gasite.add((tab, col))
    declarate = {(tab, c) for tab, cols in m.COLOANE_FIRMA for c in cols}
    assert len(gasite) >= 12, gasite                                           # anti-vacuu: cititorul vede coloanele
    assert gasite <= declarate, sorted(gasite - declarate)


# ── pe bază ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _db_ok():
    try:
        from core import db
        db.init_pool()
        with db.get_conn():
            return True
    except Exception:
        return False


_SCHEMA = "ztest_l11p_cui"


@pytest.fixture
def conn():
    from core import db, tenant_provisioning as tp
    db.init_pool()
    with db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
                cur.execute(tp.parametrizeaza_template(io.open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA))
                cur.execute("SET LOCAL search_path TO %s, public" % _SCHEMA)
                cur.execute("INSERT INTO firma_profil (id, nume, cui) VALUES (1, 'FIRMA L11 SRL', 'RO 14399840')")
            yield c
        finally:
            c.rollback()


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_paritatea_python_sql(conn):
    with conn.cursor() as cur:
        for v in MOSTRE:
            cur.execute("SELECT %s.cui_stocare(%%s)" % _SCHEMA, (v,))
            sql = cur.fetchone()[0]
            py = cf.stocare(v)
            # golul rămâne gol în bază (coloanele NOT NULL au '' implicit); Python îl dă None — același „fără cod”
            assert (sql if (sql or "").strip() else None) == py, (v, sql, py)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_triggerul_normalizeaza_pe_orice_drum(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT cui FROM firma_profil")
        assert cur.fetchone()[0] == "14399840"                                 # profilul firmei
        cur.execute("INSERT INTO clienti (nume, cui) VALUES ('A', 'ro 2864518') RETURNING cui")
        assert cur.fetchone()[0] == "2864518"                                  # o scriere SQL directă (orice drum) — normalizată
        cur.execute("INSERT INTO furnizori (nume, cui) VALUES ('B', 'DE 123456789') RETURNING cui")
        assert cur.fetchone()[0] == "DE123456789"
        cur.execute("INSERT INTO solduri_parteneri (cont, cui, denumire) VALUES ('4111', ' RO14399840', 'C') RETURNING cui")
        assert cur.fetchone()[0] == "14399840"
        # factura: „RO” scris fără starea înghețată -> starea înghețată (CF art.318 alin.(1)); starea dată de ANAF nu se atinge
        cur.execute("INSERT INTO facturi (numar, data_emitere, directie, total, tva, tert_cui, tert_nume) VALUES "
                    "('F1', '2026-06-10', 'emisa', 0, 0, 'RO 2864518', 'X'), ('F2', '2026-06-10', 'emisa', 0, 0, 'RO2864518', 'X') "
                    "RETURNING tert_cui, tert_platitor_tva")
        assert cur.fetchall() == [("2864518", True), ("2864518", True)]
        cur.execute("UPDATE facturi SET tert_platitor_tva = false WHERE numar = 'F2'")
        cur.execute("UPDATE facturi SET tert_cui = 'RO2864518' WHERE numar = 'F2' RETURNING tert_cui, tert_platitor_tva")
        assert cur.fetchone() == ("2864518", False)
        cur.execute("INSERT INTO facturi (numar, data_emitere, directie, total, tva, tert_cui, tert_nume) VALUES "
                    "('F3', '2026-06-10', 'primita', 0, 0, '', 'PF') RETURNING tert_cui, tert_platitor_tva")
        assert cur.fetchone() == ("", None)                                    # golul rămâne gol, fără stare ghicită


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_migrarea_opreste_pe_fise_dublate_si_le_numeste(conn):
    from core import migrare_cui_fara_ro as mig
    with conn.cursor() as cur:
        cur.execute("ALTER TABLE clienti DISABLE TRIGGER trg_cui_fara_ro")    # datele de dinaintea gardului
        cur.execute("INSERT INTO clienti (nume, cui) VALUES ('ALTEX', 'RO2864518'), ('ALTEX ROMANIA', '2864518')")
        cur.execute("ALTER TABLE clienti ENABLE TRIGGER trg_cui_fara_ro")
    with pytest.raises(ValueError) as ei:
        mig.aplica(conn, _SCHEMA)
    assert ei.value.args == ("fișe care ar avea același CUI după normalizare (se unesc de contabil, apoi se rulează din nou): clienti "
                             "2864518: 2864518, RO2864518",), ei.value.args
    with conn.cursor() as cur:
        cur.execute("DELETE FROM clienti WHERE nume = 'ALTEX'")
        cur.execute("ALTER TABLE furnizori DISABLE TRIGGER trg_cui_fara_ro")
        cur.execute("INSERT INTO furnizori (nume, cui) VALUES ('Z', 'RO 14399840')")
        cur.execute("ALTER TABLE furnizori ENABLE TRIGGER trg_cui_fara_ro")
    assert mig.aplica(conn, _SCHEMA) is True and mig.verifica(conn, _SCHEMA)
    with conn.cursor() as cur:
        cur.execute("SELECT cui FROM furnizori")
        assert cur.fetchone()[0] == "14399840"                                 # datele de bază existente, normalizate


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_date_firma_nu_refuza_acelasi_cui_scris_cu_ro_si_il_arata_dupa_stare(conn):
    from core import firma_profil_api as fp
    r = fp.salveaza_date(conn, {"cui": "RO 14399840", "telefon": "0264111222"}, user_id=1)
    assert r["ok"] is True, r                                                  # același CUI: nu e o schimbare refuzată
    assert r["profil"]["cui"] == "14399840" and r["profil"]["cui_afisat"] == "14399840"   # plătitorul nedeclarat: fără „RO”
    with conn.cursor() as cur:
        cur.execute("UPDATE firma_profil SET platitor_tva = true")
    assert fp.citeste_date(conn)["profil"]["cui_afisat"] == "RO14399840"      # CF art.318 alin.(1): plătitorul — „RO” la afișare
