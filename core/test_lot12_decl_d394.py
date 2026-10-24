# -*- coding: utf-8 -*-
"""[lotul 12] D394: secțiunile E / F (C19) și numărul de facturi la factura cu mai multe cote (131 / 185), pe validatorul DUK.

C19 — ce genera aplicația până azi (core/d394.py `calcul_d394`): factura EMISĂ către un partener din UE / din afara UE intra ca „L”, iar
cu cota 0 ca „LS” (livrarea intracomunitară și exportul declarate în E / F), iar orice factură PRIMITĂ de la ei era exclusă (și serviciul
din afara UE, la care beneficiarul plătește TVA). Temei: OPANAF 2194/2025, anexa 2, lit.E / F pct.10 (anaf_surse/opanaf_2194_2025_d394.txt
r.929–932 și 963–968): „se vor declara numai operaţiunile taxabile pentru care locul livrării/prestării este în România conform art. 275,
respectiv art. 278 din Codul fiscal şi, în cazul achiziţiilor de bunuri/servicii, beneficiarul este obligat la plata TVA conform art. 307
alin. (2), (3), (5) şi (6) din Codul fiscal”; la F: „Nu vor fi declarate operaţiunile de export şi import de bunuri […], precum şi
operaţiunile care se înscriu în declaraţia recapitulativă […] (formular 390)”; pct.8–9 cer achizițiile cu beneficiarul obligat la plată.

131 / 185 — OPANAF 2194/2025, anexa 2, secțiunea a 2-a pct.5 (r.1221–1225): „valoarea 1 în dreptul operaţiunii cu valoarea cea mai mare
a TVA şi valoarea 0 pentru restul operaţiunilor; dacă valoarea TVA este aceeaşi pentru operaţiunile respective, factura se va numerota o
singură dată în dreptul cotei de TVA cea mai mare.” — VALOAREA TVA decide, nu cota: aici linia de 11% are TVA-ul mai mare.

Fixtura: schemă efemeră din tenant_template, ROLLBACK; firma 14399840 (cifra de control verificată în `test_fixtura_e_valida`); partenerii
străini au coduri de TVA sintetice (DE / US), clasificate după prefix (`clasifica_partener`).
"""
import io
import xml.etree.ElementTree as ET
from decimal import Decimal

import pytest

from core import d394
from core.common import Perioada

_SCHEMA = "ztest_lot12_decl_d394"


def _op1(xml):
    rad = ET.fromstring(xml.encode("utf-8"))
    return sorted((e.get("tip"), e.get("tip_partener"), e.get("cota"), e.get("denP"), e.get("nrFact"), e.get("baza"), e.get("tva"))
                  for e in rad.iter() if e.tag.rsplit("}", 1)[-1] == "op1")


def test_fixtura_e_valida():
    from core.identitate import valideaza_cui
    assert valideaza_cui("14399840")[0]
    assert d394.clasifica_partener("DE123456789")[0] == d394.P_UE and d394.clasifica_partener("US123456789")[0] == d394.P_NONUE


def _db_ok():
    try:
        from core import db
        db.init_pool()
        with db.get_conn():
            return True
    except Exception:
        return False


def _factura(cur, numar, directie, cui, nume, linii, axa=None, serie="E"):
    total = sum(Decimal(b) * (1 + Decimal(c) / 100) for b, c in linii)
    tva = sum(Decimal(b) * Decimal(c) / 100 for b, c in linii)
    cur.execute("INSERT INTO facturi (serie, numar, data_emitere, directie, total, tva, tert_cui, tert_nume, status, axa_ic, taxare_inversa) "
                "VALUES (%s, %s, '2026-06-10', %s, %s, %s, %s, %s, %s, %s, false) RETURNING id",
                (serie if directie == "emisa" else None, numar, directie, total, tva, cui, nume, directie, axa))
    fid = cur.fetchone()[0]
    for b, c in linii:
        cur.execute("INSERT INTO factura_linii (factura_id, descriere, um, cantitate, pret_unitar, cota_tva) VALUES (%s, 'x', 'buc', 1, %s, %s)",
                    (fid, b, c))


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
                cur.execute("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,caen,banca,iban,telefon,platitor_tva,tip_decont,"
                            "declarant_nume,declarant_prenume,declarant_functie) VALUES (1,'PROBA D394 SRL','14399840','Str 1','Buc','B',"
                            "'4711','BCR','RO49RNCB0000000000000001','0700000000',true,'L','Popescu','Ion','ADMINISTRATOR')")
            yield c
        finally:
            c.rollback()


def _cu(conn, facturi):
    with conn.cursor() as cur:
        for f in facturi:
            _factura(cur, *f)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_def_c19_sectiunile_e_f_declara_numai_ce_cere_ordinul(conn):
    _cu(conn, [("1", "emisa", "DE123456789", "KUNDE GMBH", [(1000, 0)]),             # livrare intracomunitară: D390
               ("2", "emisa", "US123456789", "CLIENT INC", [(2000, 0)]),             # export: nu se declară
               ("3", "emisa", "US123456789", "CLIENT INC", [(500, 21)]),             # prestare cu locul în România, taxată: L
               ("FS1", "primita", "US987654321", "SUPPLIER INC", [(1000, 0)], "servicii"),   # serviciu din afara UE: C (art.307 alin.(2))
               ("FB1", "primita", "US987654321", "SUPPLIER INC", [(800, 0)], "bunuri"),      # import de bunuri: nu se declară
               ("FU1", "primita", "DE987654321", "LIEFERANT GMBH", [(300, 0)], "servicii")])  # achiziție intracomunitară: D390
    xml, res = d394.genereaza(conn, _SCHEMA, Perioada(2026, luna=6))
    # OPANAF 2194/2025 anexa 2 lit.E / F pct.10: numai operațiunile taxabile cu locul în România și achizițiile art.307 alin.(2)
    assert _op1(xml) == [("C", "4", "21", "SUPPLIER INC", "1", "1000", "210"),
                         ("L", "4", "21", "CLIENT INC", "1", "500", "105")], _op1(xml)
    # fiecare avertisment întreg (textul pe care îl citește contabilul, cu documentele numite), și niciunul în plus
    assert set(res.avertismente) == {
        # lit.E pct.10 — D390
        "1 factură emisă fără TVA către parteneri din UE nu intră în D394 — livrările și prestările intracomunitare se declară în D390 "
        "(OPANAF 2194/2025, anexa 2, lit.E pct.10): E nr. 1.",
        # lit.F pct.10 — export
        "1 factură emisă fără TVA către parteneri din afara UE nu intră în D394 — exportul și prestările cu locul în afara României nu se "
        "declară aici (OPANAF 2194/2025, anexa 2, lit.F pct.10): E nr. 2.",
        # lit.F pct.10 — import
        "1 factură primită de la parteneri din afara UE nu intră în D394: FB1. Importul de bunuri nu se declară aici (OPANAF 2194/2025, "
        "anexa 2, lit.F pct.10); dacă e un serviciu, alege „servicii” pe factură și generează din nou — serviciul intră în D394 la "
        "achiziții cu taxare inversă (CF art.307 alin.(2)).",
        "1 achiziție de la parteneri din UE — nu intră în D394 (se declară în D390 - VIES).",
    } and len(res.avertismente) == 4, res.avertismente


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_def_c19_sectiunile_e_f_valide_pe_duk(conn):
    from core import duk
    if not duk.poate_valida("d394"):
        pytest.skip("DUK d394 indisponibil")
    _cu(conn, [("1", "emisa", "DE123456789", "KUNDE GMBH", [(1000, 0)]),
               ("3", "emisa", "US123456789", "CLIENT INC", [(500, 21)]),
               ("FS1", "primita", "US987654321", "SUPPLIER INC", [(1000, 0)], "servicii")])
    xml, _res = d394.genereaza(conn, _SCHEMA, Perioada(2026, luna=6))
    rez = duk.valideaza(xml, "d394", an=2026, luna=6)
    assert rez["stare"] == "valid", rez   # DUK D394 — judecătorul final


def test_def_c19_profil_minim_c_din_afara_ue_valid_pe_duk():
    """Profil minim construit manual (calea pură): numai serviciul din afara UE, tip C, tip_partener 4 — valid pe DUK."""
    from core import duk
    if not duk.poate_valida("d394"):
        pytest.skip("DUK d394 indisponibil")
    prof = {"declarant_nume": "Popescu", "declarant_prenume": "Ion", "cui": "14399840", "nume": "PROBA SRL", "caen": "4711",
            "tip_decont": "L", "adresa": "Str 1", "judet": "B", "reprezentant_nume": "POPESCU ION", "reprezentant_functie": "ADMINISTRATOR",
            "declarant_functie": "CONTABIL", "platitor_tva": True, "telefon": "0700000000"}
    f = dict(cui="US987654321", nume="SUPPLIER INC", directie="primita", taxare_inversa=False, cota=0, baza=Decimal(1000), tva=Decimal(0),
             nrFact=1, factura_id=1, axa="servicii", document="FS1")
    res = d394.calcul_d394(prof, Perioada(2026, luna=6), {"facturi": [f], "nr_facturi": 0})
    xml = d394.build_xml(res)
    assert _op1(xml) == [("C", "4", "21", "SUPPLIER INC", "1", "1000", "210")]   # CF art.307 alin.(2): TVA-ul la beneficiar, cota standard
    assert duk.valideaza(xml, "d394", an=2026, luna=6)["stare"] == "valid"


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_def_185_numarul_facturii_merge_la_tva_ul_cel_mai_mare_nu_la_cota_cea_mai_mare(conn):
    # 100 lei la 21% (TVA 21) + 1.000 lei la 11% (TVA 110): TVA-ul cel mai mare e pe 11%
    _cu(conn, [("5", "emisa", "RO14399840", "CLIENT RO SRL", [(100, 21), (1000, 11)])])
    xml, res = d394.genereaza(conn, _SCHEMA, Perioada(2026, luna=6))
    # OPANAF 2194/2025 anexa 2 secțiunea a 2-a pct.5: „valoarea 1 în dreptul operaţiunii cu valoarea cea mai mare a TVA”
    assert _op1(xml) == [("L", "1", "11", "CLIENT RO SRL", "1", "1000", "110"), ("L", "1", "21", "CLIENT RO SRL", "0", "100", "21")]
    assert res.rezumat2[11]["nrFacturiL"] == 1 and res.rezumat2[21]["nrFacturiL"] == 0
    assert {"Factura E nr. 5 are operațiuni pe cotele 11%, 21%: se numără o singură dată, la cota cu TVA-ul cel mai mare (11%); la 21% "
            "apare cu 0 facturi — OPANAF 2194/2025, instrucțiuni, secțiunea a 2-a pct.5."} <= set(res.sinteza), res.sinteza
    from core import duk
    if duk.poate_valida("d394"):
        assert duk.valideaza(xml, "d394", an=2026, luna=6)["stare"] == "valid"


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_def_131_rindul_11_la_tva_mai_mic_are_0_facturi_si_e_valid_pe_duk(conn):
    _cu(conn, [("6", "emisa", "RO14399840", "CLIENT RO SRL", [(1000, 21), (200, 11)])])
    xml, res = d394.genereaza(conn, _SCHEMA, Perioada(2026, luna=6))
    assert res.rezumat2[21]["nrFacturiL"] == 1 and res.rezumat2[11]["nrFacturiL"] == 0   # secțiunea a 2-a pct.5: 1 la TVA-ul 210, 0 la 22
    from core import duk
    if duk.poate_valida("d394"):
        assert duk.valideaza(xml, "d394", an=2026, luna=6)["stare"] == "valid"   # validatorul primește 0 pe rândul de 11%
