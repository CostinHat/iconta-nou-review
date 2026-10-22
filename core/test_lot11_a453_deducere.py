# -*- coding: utf-8 -*-
"""[lotul 11, deficiența 453] Deducerea personală rotunjită la leu — aceeași cifră în calcul, pe fluturaș și în D112.

Comanda Costin 11.3 pct.8, verbatim: „453: verifică la sursă rotunjirea deducerii personale (fluturașul arată 562,25) și aplic-o în
calcul, fluturaș și D112.”

SURSA. CF art.77 (forma consolidată, `anaf_surse/cod_fiscal_227_2015_consolidat.txt`) și normele lui (HG 1/2016 Titlul IV pct.13) dau
procentul din salariul minim, fără să spună cum se rotunjește suma (alin.(8) rotunjește PERIOADA). Procedura ANAF a D112 o spune:
structura D112 (`anaf_surse/d112_struct_anaf.txt`, antet) — „Toate valorile sunt numere intregi pozitive. Parametrii pot avea zecimale.
Campurile calculate cu ajutorul parametrilor vor avea valori intregi, pozitive obtinute prin rotunjire matematica”. Deducerea =
procent × salariul minim (parametru) -> întreg, rotunjit aritmetic. Se rotunjește O DATĂ, în `salarizare.deducere_personala`.

D112. Până la 22.10.2026 secțiunea E declara deducerea 0 (E1_4="0", fără E3_12), iar E3_9 / E1_2 (contribuțiile) purtau baza CAS și
E3_14 / E1_6 (venitul bază de calcul) purtau impozitul. Testele de aici cer rândurile cu cifrele lor (OPANAF 605/2026 anexa 1.2).

CNP-urile de test sunt verificate cu algoritmul cifrei de control (CLAUDE.md): 1800101410013, 5000101410011, 1800202410011.
"""
import datetime
import re
from decimal import Decimal

import pytest

from core import d112, db as _db, salarizare, stat_plata_api, tenant_provisioning as _tp
from core.common import Perioada

_SCHEMA = "test_lot11_a453"
_LA = datetime.date(2026, 10, 1)


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


def _setup(cur, salariati):
    cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
    cur.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA))
    cur.execute("SET LOCAL search_path TO %s, public" % _SCHEMA)
    cur.execute("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,caen,platitor_tva,tip_decont,"
                "declarant_nume,declarant_prenume,declarant_functie) VALUES (1,'PROBA SRL','14399840','Str 1',"
                "'Buc','B','6202',true,'L','Pop','Ion','administrator')")
    for s in salariati:
        cur.execute("WITH s AS (INSERT INTO salariati (cnp,nume,prenume,data_angajare,ore_zi,judet_casa,cor,data_nastere,"
                    "copii_scolarizati,declaratie_copii,tip_asigurat,functie_baza) VALUES (%(cnp)s,%(nume)s,'X','2024-01-01',8,'B',"
                    "'251401',%(dn)s,%(copii)s,%(decl)s,'1',true) RETURNING id, data_angajare), "
                    "i AS (INSERT INTO salariu_istoric (salariat_id, valabil_din, salariu_brut) SELECT id, data_angajare, %(brut)s FROM s) "
                    "SELECT id FROM s", s)


@pytest.fixture
def conn():
    _db.init_pool()
    with _db.get_conn() as c:
        try:
            yield c
        finally:
            c.rollback()
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
            c.commit()


def _atr(xml, sectiune, nume):
    el = re.search(r"<%s [^>]*/>" % sectiune, xml).group(0)
    return int(re.search(r' %s="(\d+)"' % nume, el).group(1))


# ---------------------------------------------------------------- calculul (pur)

def test_453_calcul_deducere_rotunjita_si_impozit():
    """Brut 5.000 lei, 10/2026 (salariul minim 4.325): treapta „+651 … +700 lei” = 13% -> 562,25 -> 562; impozitul rămâne 269."""
    r = salarizare.calcul_salariu(5000, la_data=_LA)
    # structura D112 (antet): „Campurile calculate cu ajutorul parametrilor vor avea valori intregi … obtinute prin rotunjire matematica”
    assert r["deducere"]["total"] == Decimal("562.00"), r["deducere"]
    # HG 1/2016 Titlul IV pct.4: baza = 5.000 − 1.250 (CAS) − 500 (CASS) − 562 = 2.688 (întreagă); impozit 10% = 268,80 -> 269
    assert (r["baza_impozabila"], r["impozit"]) == (Decimal("2688.00"), Decimal("269.00")), r


# ---------------------------------------------------------------- fluturașul și D112 (pe bază)

@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_453_fluturas_si_d112_aceeasi_deducere(conn):
    """Același salariat, aceeași lună: statul / fluturașul arată 562, iar D112 declară 562 (E3_12 = E3_121, E1_4 = E1_41) și venitul
    bază de calcul 2.688 = 5.000 − 1.750 − 562 (E3_14 = E3_8 − E3_9 − E3_12). RED pe codul vechi: fluturașul 562,25, D112 E1_4 = 0."""
    with conn.cursor() as cur:
        _setup(cur, [{"cnp": "1800101410013", "nume": "MATUR", "dn": "1980-06-01", "copii": 0, "decl": False, "brut": 5000}])
    conn.commit()
    with conn.cursor() as cur:
        cur.execute("SET LOCAL search_path TO %s, public" % _SCHEMA)
    stat = stat_plata_api.stat_plata(conn, _SCHEMA, 2026, 10)
    assert stat[0]["deducere"] == 562.0, stat[0]
    assert stat_plata_api.randuri_deducere(stat[0]) == [("Deducere personală", 562.0)]
    xml = d112.genereaza(conn, _SCHEMA, Perioada(an=2026, luna=10))[0]
    # OPANAF 605/2026 anexa 1.2, secțiunea E: rândul 4 „Deducere personală” = deducerea acordată; rândul 2 = contribuțiile; rândul 6 =
    # venitul net minus deducerea personală; structura D112: E3_12=E3_121+E3_122, E1_41=ΣE3_121, E1_6=ΣE3_14
    assert (_atr(xml, "asiguratE3", "E3_12"), _atr(xml, "asiguratE3", "E3_121"), _atr(xml, "asiguratE3", "E3_122")) == (562, 562, 0)
    assert (_atr(xml, "asiguratE1", "E1_4"), _atr(xml, "asiguratE1", "E1_41"), _atr(xml, "asiguratE1", "E1_42")) == (562, 562, 0)
    assert _atr(xml, "asiguratE3", "E3_9") == _atr(xml, "asiguratE1", "E1_2") == 1750      # CAS 1.250 + CASS 500
    assert _atr(xml, "asiguratE3", "E3_14") == _atr(xml, "asiguratE1", "E1_6") == 2688     # 5.000 − 1.750 − 562
    assert _atr(xml, "asiguratE3", "E3_14") == (_atr(xml, "asiguratE3", "E3_8") - _atr(xml, "asiguratE3", "E3_9")
                                                 - _atr(xml, "asiguratE3", "E3_12"))
    assert _atr(xml, "asiguratE3", "E3_15") == _atr(xml, "asiguratE1", "E1_7") == 269     # 10% × 2.688 = 268,80 -> 269


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_453_d112_deducerile_suplimentare_pe_randurile_lor(conn):
    """Tânăr sub 26 de ani la salariul minim (4.325) + părinte cu 2 copii școlarizați și declarație: suplimentarele pe rândurile lor."""
    with conn.cursor() as cur:
        _setup(cur, [{"cnp": "5000101410011", "nume": "TANAR", "dn": "2002-06-01", "copii": 0, "decl": False, "brut": 4325},
                     {"cnp": "1800202410011", "nume": "PARINTE", "dn": "1980-06-01", "copii": 2, "decl": True, "brut": 5000}])
    conn.commit()
    xml = d112.genereaza(conn, _SCHEMA, Perioada(an=2026, luna=10))[0]
    asig = {re.search(r'cnpAsig="(\d+)"', b).group(1): b for b in re.findall(r"<asigurat .*?</asigurat>", xml, re.S)}
    t, p = asig["5000101410011"], asig["1800202410011"]
    # CF art.77 alin.(10) lit.a: 15% × 4.325 = 648,75 -> 649 (E3_1221); alin.(4): 20% × 4.325 = 865 (E3_121)
    assert (_atr(t, "asiguratE3", "E3_121"), _atr(t, "asiguratE3", "E3_1221"), _atr(t, "asiguratE3", "E3_122"),
            _atr(t, "asiguratE3", "E3_12")) == (865, 649, 649, 1514)
    assert (_atr(t, "asiguratE1", "E1_421"), _atr(t, "asiguratE1", "E1_42"), _atr(t, "asiguratE1", "E1_4")) == (649, 649, 1514)
    # CF art.77 alin.(10) lit.b: 100 lei lunar pentru fiecare copil -> 200 (E3_1222); baza 562 (13% × 4.325)
    assert (_atr(p, "asiguratE3", "E3_121"), _atr(p, "asiguratE3", "E3_1222"), _atr(p, "asiguratE3", "E3_12")) == (562, 200, 762)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_453_d112_cu_deducerea_duk_valid(conn):
    """Proba la arbitru: D112 cu secțiunea E completă (deducere de bază + suplimentare) e valid la DUKIntegrator."""
    from core import duk
    if not duk.poate_valida("d112"):
        pytest.skip("DUK d112 indisponibil")
    with conn.cursor() as cur:
        _setup(cur, [{"cnp": "5000101410011", "nume": "TANAR", "dn": "2002-06-01", "copii": 0, "decl": False, "brut": 4325},
                     {"cnp": "1800202410011", "nume": "PARINTE", "dn": "1980-06-01", "copii": 2, "decl": True, "brut": 5000},
                     {"cnp": "1800101410013", "nume": "MATUR", "dn": "1980-06-01", "copii": 0, "decl": False, "brut": 5000}])
    conn.commit()
    xml = d112.genereaza(conn, _SCHEMA, Perioada(an=2026, luna=10))[0]
    rez = duk.valideaza(xml, "d112", an=2026, luna=10)
    assert rez["stare"] == "valid", rez
