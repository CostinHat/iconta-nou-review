# -*- coding: utf-8 -*-
"""[lotul 11, C91] Deducerea personală se acordă în limita venitului impozabil lunar realizat — aceeași cifră în calcul, pe fluturaș și
în D112 (E3_12 / E3_121 / E3_1221 / E3_1222, E1_4 / E1_41 / E1_42 …).

SURSA. CF art.77 alin.(2) (`anaf_surse/cod_fiscal_227_2015_consolidat.txt`): „Deducerea personală cuprinde deducerea personală de bază
și deducerea personală suplimentară și se acordă în limita venitului impozabil lunar realizat.” HG 1/2016 Titlul IV pct.13 alin.(1): „…
deducerea personală se acordă … numai pentru veniturile din salarii la locul unde se află funcția de bază, în limita venitului realizat.”
OPANAF 605/2026 anexa 1.2, secțiunea E.1, rândul 4: „se completează cu suma reprezentând deduceri personale acordate persoanei fizice,
potrivit legii. Deducerea personală … se acordă în limita venitului impozabil lunar realizat.”

Până la 22.10.2026 baza impozitului se oprea la 0, dar deducerea declarată (E3_12) și cea de pe fluturaș erau cele calculate întregi
(ex. 1.946 lei la un venit net de 650 lei).

CNP-urile de test sunt verificate cu algoritmul cifrei de control (CLAUDE.md): 1800101410013, 5000101410011.
"""
import datetime
from decimal import Decimal

import pytest

from core import d112, db as _db, salarizare, stat_plata_api, tenant_provisioning as _tp
from core.common import Perioada

_SCHEMA = "test_lot11_s9_ded"
_LA = datetime.date(2026, 10, 1)


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


def _setup(cur, salariati, schema=_SCHEMA):
    cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % schema)
    cur.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), schema))
    cur.execute("SET LOCAL search_path TO %s, public" % schema)
    cur.execute("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,caen,platitor_tva,tip_decont,"
                "declarant_nume,declarant_prenume,declarant_functie) VALUES (1,'PROBA SRL','14399840','Str 1',"
                "'Buc','B','6202',true,'L','Pop','Ion','administrator')")
    for s in salariati:
        s = {"pt": False, "ore": 8, "pers": 0, "fb": True, **s}
        cur.execute("WITH s AS (INSERT INTO salariati (cnp,nume,prenume,data_angajare,ore_zi,judet_casa,cor,data_nastere,"
                    "copii_scolarizati,declaratie_copii,tip_asigurat,functie_baza,part_time,persoane_intretinere,scutit_contrib_minim) "
                    "VALUES (%(cnp)s,%(nume)s,'X','2024-01-01',%(ore)s,'B','251401',%(dn)s,0,false,'1',%(fb)s,%(pt)s,%(pers)s,false) "
                    "RETURNING id, data_angajare), "
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


_NS = "{mfp:anaf:dgti:declaratie_unica:declaratie:v7}"


def structura(xml):
    """XML-ul D112 PARSAT (ElementTree): {"_angajator": {secțiune: [atribute]}, cnpAsig: {secțiune: [atribute]}}. Gărzile citesc
    atributul secțiunii, nu un sub-șir din text."""
    import xml.etree.ElementTree as ET
    rad = ET.fromstring(xml.encode("utf-8"))

    def _sectiuni(el):
        out = {}
        for c in el:
            out.setdefault(c.tag.replace(_NS, ""), []).append(dict(c.attrib))
        return out
    d = {"_angajator": _sectiuni(rad.find(_NS + "angajator"))}
    for a in rad.findall(_NS + "asigurat"):
        d[a.get("cnpAsig")] = _sectiuni(a)
    return d


def unic(sectiuni, nume):
    """Secțiunea `nume`, care trebuie să apară EXACT o dată (premisa verificată: lipsa ei pică, nu trece)."""
    lista = sectiuni.get(nume, [])
    assert len(lista) == 1, (nume, sorted(sectiuni), lista)
    return lista[0]


def _int(sectiuni, nume, *atribute):
    el = unic(sectiuni, nume)
    return tuple(int(el[a]) for a in atribute)


# ---------------------------------------------------------------- calculul (pur)

def test_c91_deducerea_plafonata_la_venitul_net():
    """Normă parțială, brut 1.000 lei, 4 persoane în întreținere, 10/2026 (salariul minim 4.325): deducerea calculată 45% × 4.325 =
    1.946,25 -> 1.946, dar venitul net e 1.000 − 250 (CAS) − 100 (CASS) = 650 -> deducerea ACORDATĂ 650, baza 0, impozit 0.
    ROȘU pe codul vechi: deducerea 1.946 (baza tot 0)."""
    r = salarizare.calcul_salariu(1000, persoane=4, la_data=_LA, norma_intreaga=False, exceptat_suprataxare=True)
    # CF art.77 alin.(2): „se acordă în limita venitului impozabil lunar realizat”
    assert r["deducere"] == {"baza": Decimal("650.00"), "tineri": Decimal("0.00"), "copii": Decimal("0.00"),
                             "total": Decimal("650.00")}, r["deducere"]
    # CF art.78 alin.(2) lit.a: baza = venitul net − deducerea personală acordată = 650 − 650
    assert (r["baza_impozabila"], r["impozit"]) == (Decimal("0.00"), Decimal("0.00")), r


def test_c91_plafonul_consuma_intai_deducerea_de_baza_apoi_suplimentara():
    """Tânăr sub 26 de ani, brut 1.000: de bază 20% × 4.325 = 865, suplimentară 15% × 4.325 = 648,75 -> 649 (total 1.514), venit net
    650 -> acordat 650, toată pe deducerea de bază (ordinea din CF art.77 alin.(2): „deducerea personală de bază și deducerea personală
    suplimentară”), suplimentara 0."""
    r = salarizare.calcul_salariu(1000, sub_26=True, la_data=_LA, norma_intreaga=False, exceptat_suprataxare=True)
    assert (r["deducere"]["baza"], r["deducere"]["tineri"], r["deducere"]["total"]) == (
        Decimal("650.00"), Decimal("0.00"), Decimal("650.00")), r["deducere"]
    # brut 2.000: venit net 1.300 -> de bază 865 întreagă, suplimentara 1.300 − 865 = 435 din 649
    r = salarizare.calcul_salariu(2000, sub_26=True, la_data=_LA, norma_intreaga=False, exceptat_suprataxare=True)
    assert (r["deducere"]["baza"], r["deducere"]["tineri"], r["deducere"]["total"]) == (
        Decimal("865.00"), Decimal("435.00"), Decimal("1300.00")), r["deducere"]
    assert r["impozit"] == Decimal("0.00"), r


def test_c91_venit_net_cu_bani_deducerea_ramane_intreaga():
    """Brut 1.001,55: venit net 1.001,55 × 65% = 651,0075 -> deducerea acordată 651 (întreagă: structura D112, antet — „Campurile
    calculate cu ajutorul parametrilor vor avea valori intregi … obtinute prin rotunjire matematica”), baza 0 (HG 1/2016 Titlul IV
    pct.4: fracțiunile de până la 50 de bani se neglijează)."""
    r = salarizare.calcul_salariu(Decimal("1001.55"), persoane=4, la_data=_LA, norma_intreaga=False, exceptat_suprataxare=True)
    assert r["deducere"]["total"] == Decimal("651.00"), r["deducere"]
    assert (r["baza_impozabila"], r["impozit"]) == (Decimal("0.00"), Decimal("0.00")), r


def test_c91_sub_plafon_deducerea_neschimbata():
    """Venitul net acoperă deducerea (brut 5.000): neschimbat față de 453 — 562 (13% × 4.325 = 562,25 -> 562)."""
    r = salarizare.calcul_salariu(5000, la_data=_LA)
    assert r["deducere"]["total"] == Decimal("562.00"), r["deducere"]
    assert r["impozit"] == Decimal("269.00"), r


def test_c91_garda_deducerea_niciodata_peste_venitul_net():
    """Garda (orice brut, orice persoane, tânăr sau nu): deducerea acordată nu depășește venitul net rotunjit la leu, iar componentele
    însumează totalul. Pică dacă o cale nouă de calcul ocolește plafonul."""
    from core.numere import leu_aritmetic
    for brut in (0, 1, 300, 999.99, 1000, 1500, 2216.5, 3000, 4325, 6325):
        for pers in (0, 2, 4):
            for tanar in (False, True):
                r = salarizare.calcul_salariu(brut, persoane=pers, sub_26=tanar, la_data=_LA, norma_intreaga=False,
                                              exceptat_suprataxare=True)
                d = r["deducere"]
                vn = max(Decimal(str(brut)) - r["facilitate"] - Decimal(str(brut)) * Decimal("0.35"), Decimal(0))
                assert d["total"] <= leu_aritmetic(vn), (brut, pers, tanar, d, vn)   # CF art.77 alin.(2)
                assert d["baza"] + d["tineri"] + d["copii"] == d["total"], (brut, pers, tanar, d)


# ---------------------------------------------------------------- fluturașul și D112 (pe bază)

@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_c91_fluturas_si_d112_aceeasi_deducere_plafonata(conn):
    """Salariat cu normă parțială (4 ore), brut 1.000, 4 persoane: statul / fluturașul arată 650, iar D112 declară E3_12 = E3_121 = 650,
    E1_4 = E1_41 = 650, E3_14 = 0, E3_15 = 0 — și e valid la DUKIntegrator. ROȘU pe codul vechi: 1.946 pe ambele."""
    with conn.cursor() as cur:
        _setup(cur, [{"cnp": "1800101410013", "nume": "PARTIAL", "dn": "1980-06-01", "brut": 1000, "pt": True, "ore": 4,
                      "pers": 4}])
    conn.commit()
    with conn.cursor() as cur:
        cur.execute("SET LOCAL search_path TO %s, public" % _SCHEMA)
    stat = stat_plata_api.stat_plata(conn, _SCHEMA, 2026, 10)
    assert stat[0]["deducere"] == 650.0, stat[0]                        # CF art.77 alin.(2)
    assert stat_plata_api.randuri_deducere(stat[0]) == [("Deducere personală", 650.0)]
    xml = d112.genereaza(conn, _SCHEMA, Perioada(an=2026, luna=10))[0]
    # OPANAF 605/2026 anexa 1.2, E.1 rândul 4: „deduceri personale acordate … în limita venitului impozabil lunar realizat”
    a = structura(xml)["1800101410013"]
    assert _int(a, "asiguratE3", "E3_12", "E3_121", "E3_122") == (650, 650, 0)
    assert _int(a, "asiguratE1", "E1_4", "E1_41") == (650, 650)
    assert _int(a, "asiguratE3", "E3_14", "E3_15") == (0, 0)
    from core import duk
    if not duk.poate_valida("d112"):
        pytest.skip("DUK d112 indisponibil")
    rez = duk.valideaza(xml, "d112", an=2026, luna=10)
    assert rez["stare"] == "valid", rez
