# -*- coding: utf-8 -*-
"""[lotul 13, zona firme2] Deficiența 589 — Plan de conturi.

Comanda Costin 13.1, verbatim: „589: Plan de conturi | Contul sintetic 731 (în afara planului legal) a fost adăugat manual; avertismentul
apare după salvare; contul nu se poate șterge. Adăugarea manuală doar pentru analitice sub sintetic legal. De curățat de Code: 731 «Test
cont nelegal» pe F6.”

CE FACE IMPOSIBIL: (a) un cont SINTETIC adăugat manual (planul general e deja semănat la crearea firmei); (b) un analitic sub un sintetic
din afara planului legal al normei firmei sau sub un sintetic care nu e în planul firmei; (c) drumul manual de adăugare din `uc_tenants`
fără regula asta (garda textuală — aceeași funcție ca ecranul); (d) ecranul cu alți separatori ai analiticului decât serverul (oglinda
din firme.js, cu care spune refuzul ÎNAINTE de salvare); (e) scriptul de curățenie care scoate alt cont decât 731 „Test cont nelegal”
sau un cont cu rulaj. Schemă efemeră din șablon, tranzacție anulată, perioade sintetice (2099).
TEMEI: planul legal = nomenclatorul validatorului ANAF pe norma firmei (`d406.plan_oficial`, `anaf_surse/d406_nomenclatoare_anaf.properties`);
OMFP 1802/2014 (planul general de conturi al societăților) — decizia Costin 08.10.2026 V3 („un cont care nu e în planul legal nu se poate
crea sau folosi fără avertisment”), întărită de comanda 13.1 (589: „adăugarea manuală doar pentru analitice sub sintetic legal”).
"""
import os
import re
import sys

import pytest

from core import db as _db, plan_legal, uc_tenants

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA = "ztest_lot13_firme2_pc"


def test_separatorii_analiticului_sunt_aceiasi_pe_ecran_si_pe_server():
    js = open(os.path.join(RAD, "static", "js", "ecrane", "firme.js"), encoding="utf-8").read()
    m = re.search(r'const SEPARATORI_ANALITIC = "([^"]+)";', js)
    assert m and m.group(1) == uc_tenants.SEPARATORI_ANALITIC, (m and m.group(1), uc_tenants.SEPARATORI_ANALITIC)


def test_drumul_manual_de_adaugare_aplica_regula():
    """Garda textuală pe `uc_tenants.tenant_plan_conturi_adauga` (peticul l13_petice/firme2_2.json): regula se cere înaintea scrierii."""
    src = open(os.path.join(RAD, "core", "uc_tenants.py"), encoding="utf-8").read()
    corp = src.split("def tenant_plan_conturi_adauga(", 1)[1].split("\ndef ", 1)[0]
    assert "refuz_adaugare_manuala(" in corp, "adăugarea manuală nu mai cere regula 589"
    assert corp.index("refuz_adaugare_manuala(") < corp.index("adauga_cont_in_plan("), "regula vine după scriere"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture
def cur():
    if not _db_ok():
        pytest.skip("DB indisponibil")
    from core import tenant_provisioning as _tp
    sablon = open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read()
    with _db.get_conn() as c:
        try:
            with c.cursor() as k:
                k.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCHEMA)
                k.execute(_tp.parametrizeaza_template(sablon, SCHEMA))
                k.execute("SET LOCAL search_path TO %s, public" % SCHEMA)
                k.execute("INSERT INTO plan_conturi (simbol, denumire, tip) VALUES ('731', 'Test cont nelegal', 'Nedeterminat')")
                yield k
        finally:
            c.rollback()


def _plan(cur):
    from core import repo_contabilitate as rc
    return [r[0] for r in rc.toate_conturile(cur)]


@pytest.mark.parametrize("simbol, incepe", [
    ("731", "Contul 731 e sintetic"),                         # sinteticul nelegal, ca pe F6
    ("4111", "Contul 4111 e sintetic"),                       # orice sintetic: planul general e deja în plan
    ("731.01", "Contul sintetic 731 nu e în planul de conturi al normei firmei (OMFP 1802/2014)"),
    ("9999.01", "Contul sintetic 9999 nu e în planul firmei"),
    ("4111.01", None),                                       # analitic sub sintetic legal: se adaugă
    ("401_7", None),
])
def test_regula_adaugarii_manuale(cur, simbol, incepe):
    m = plan_legal.refuz_adaugare_manuala(cur, SCHEMA, simbol, uc_tenants.sintetic_al(simbol), _plan(cur))
    assert (m is None) if incepe is None else (m or "").startswith(incepe), m


def test_scriptul_scoate_numai_731_de_test_si_numai_fara_rulaj(cur):
    sys.path.insert(0, os.path.join(RAD, "scripts"))
    import lot13_firme2_curata_731 as sc
    conn = cur.connection
    # cu rulaj: nu se scoate, motivul aplicației
    cur.execute("INSERT INTO inregistrari (data, descriere, sursa, status) VALUES ('2099-10-20', 'probă 589', 'manual', 'ciorna') RETURNING id")
    nid = cur.fetchone()[0]
    cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s, '5311', '731', 10)", (nid,))
    assert sc.curata(conn, SCHEMA) == (False, "contul 731 nu se scoate: apare în note contabile (are rulaj), deci evidența îl folosește")
    cur.execute("DELETE FROM inregistrari WHERE id = %s", (nid,))
    # altă denumire: nu e contul de test
    cur.execute("UPDATE plan_conturi SET denumire = 'Venituri din cotizații' WHERE simbol = '731'")
    assert sc.curata(conn, SCHEMA)[0] is False
    cur.execute("UPDATE plan_conturi SET denumire = 'Test cont nelegal' WHERE simbol = '731'")
    assert sc.curata(conn, SCHEMA) == (True, "contul 731 „Test cont nelegal” scos din planul firmei (1 rând)")
    assert "731" not in _plan(cur)
    assert sc.curata(conn, SCHEMA) == (False, "contul 731 nu e în planul firmei: nimic de scos")     # idempotent
