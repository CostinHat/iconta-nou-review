# -*- coding: utf-8 -*-
"""Teste gardian pentru D101 - REFACUT A DOUA OARA 16.07.2026.

Prima refacere fusese GRESITA IN EXECUTIE: structura veche (P1-P53) era de fapt
cea CORECTA (confirmata ulterior direct din D101Validator.jar, clasa
Identificare), dar fusese inlocuita cu P1-P16 inventat din cap, crezand gresit
ca modulul vechi genera dupa formularul de grup fiscal (D101G). A doua refacere
foloseste doar atributele confirmate in constant pool-ul validatorului instalat.
"""
import pytest
from core.d101 import calcul_d101, build_xml, erori_generare, _nr_evid, NS


def _prof():
    return {"cui": "14399840", "nume": "DANTE INTERNATIONAL SA",
            "adresa": "Bd. Timisoara 26Z", "caen": "4711"}


def test_namespace_e_v10():
    assert NS == "mfp:anaf:dgti:d101:declaratie:v10"


def test_calcul_simplu_profit():
    res = calcul_d101(_prof(), 2025, venituri_totale=20000, cheltuieli_totale=12000)
    assert res.P["P1"] == 20000
    assert res.P["P3"] == 8000
    assert res.P["P9"] == 8000
    assert res.P["P11"] == 1280
    assert res.total_plata_a == 1280


def test_pierdere_nu_genereaza_impozit():
    res = calcul_d101(_prof(), 2025, venituri_totale=5000, cheltuieli_totale=9000)
    assert res.P.get("P9", 0) == 0
    assert "P11" not in res.P


def test_flagurile_valide_apar_pe_radacina():
    """d_recN si d_grup NU accepta "0" (validator: "valoarea 0 nu se
    incadreaza in intervalul cerut" - valorile lor valide sunt doar 1 sau
    lipsa). Restul flagurilor accepta "0" explicit."""
    res = calcul_d101(_prof(), 2025, venituri_totale=1000, cheltuieli_totale=500)
    xml = build_xml(res)
    for flag in ("d_rec", "d_reg", "d_reglem", "d_anulare",
                 "d_succ", "d_prof", "d_alte"):
        assert '%s="0"' % flag in xml, "lipseste %s" % flag
    assert "d_recN=" not in xml
    assert "d_grup=" not in xml


def test_cod_obligatie_e_prezent():
    """Regresie: lipsea complet - 'atributul trebuie sa existe'.
    103 = impozit pe profit PJ romane (nomenclator D100/D101)."""
    res = calcul_d101(_prof(), 2025, venituri_totale=1000, cheltuieli_totale=500)
    xml = build_xml(res)
    assert 'cod_obligatie="103"' in xml


def test_denumire_nu_den():
    """Regresie: 'den' e atribut necunoscut la D101 (spre deosebire de alte
    declaratii) - numele corect e 'denumire'."""
    res = calcul_d101(_prof(), 2025, venituri_totale=1000, cheltuieli_totale=500)
    xml = build_xml(res)
    assert 'denumire=' in xml
    assert ' den=' not in xml


def test_scadenta_format_zzllaa_compact():
    """Regresie: 'scadenta="25.03.2026"' respins ('sir mai lung de 6
    caractere'). Formatul e ZZLLAA compact, 6 cifre. Formula reala
    (DUK regula R17): pentru Data_S in [2022,2025], LL=luna+6 (nu +3)."""
    res = calcul_d101(_prof(), 2025, venituri_totale=1000, cheltuieli_totale=500)
    xml = build_xml(res)
    assert 'scadenta="250626"' in xml
    assert '.' not in [c for c in xml.split('scadenta="')[1].split('"')[0]]


def test_cod_bug_e_prezent():
    res = calcul_d101(_prof(), 2025, venituri_totale=1000, cheltuieli_totale=500)
    xml = build_xml(res)
    assert 'cod_bug="5503XXXXXX"' in xml


def test_data_i_si_data_s():
    res = calcul_d101(_prof(), 2025, venituri_totale=1000, cheltuieli_totale=500)
    xml = build_xml(res)
    assert 'Data_I="01.01.2025"' in xml
    assert 'Data_S="31.12.2025"' in xml


def test_nr_evid_are_23_caractere_si_cifra_control():
    n = _nr_evid("14399840", 2025, 12)
    assert len(n) == 23 and n.isdigit()
    suma = sum(int(c) for c in n[:21])
    assert n[21:23] == "%02d" % (suma % 100)


def test_lipsa_caen_e_prinsa_la_generare():
    prof = dict(_prof())
    del prof["caen"]
    assert any("CAEN" in e for e in erori_generare(prof))


# ── CONTRACT UNIFORM A1 (modul 6/10, C2, 31.07.2026) ──
# genereaza(conn, schema, perioada, manual) prin pull() -> calcul_d101 -> build_xml.
# N/A temei fiscal (schimbare de tooling: uniformizare contract, comportament identic).
# NOTA: proba DUK-valid NU e aici - D101 build_xml e RESPINS de DUK (P1 sectiune necunoscuta +
# cod_bug placeholder), pre-existent refactorului. Consemnat: test_datorie_d101_build_xml_respins_de_duk.
from core.common import Perioada
from core import db as _db, tenant_provisioning as _tp, d101 as _d101

_SCHEMA_D101 = "ztest_d101_contract"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture
def conn_schema_profit():
    """Schema temporara, firma_profil completa (caen obligatoriu D101) + note validate:
    venit 100000 (cont 707) si cheltuiala 60000 (cont 607) in 2026. ROLLBACK garantat."""
    _db.init_pool()
    with _db.get_conn() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA_D101)
                cur.execute(_tp.parametrizeaza_template(
                    open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA_D101))
                cur.execute("SET search_path TO %s, public" % _SCHEMA_D101)
                cur.execute(
                    "INSERT INTO firma_profil (id, nume, cui, adresa, oras, judet, caen, "
                    "regim_fiscal, platitor_tva, tip_decont, declarant_nume, declarant_prenume, declarant_functie) "
                    "VALUES (1,'PROBA SRL','14399840','Str. Test 1','Bucuresti','B','6202','real',true,'L','Pop','Ion','administrator') "
                    "ON CONFLICT (id) DO UPDATE SET caen=EXCLUDED.caen")
                cur.execute("INSERT INTO inregistrari (data, status, sursa) "
                            "VALUES ('2026-06-15','validata','test') RETURNING id")
                iid = cur.fetchone()[0]
                cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) "
                            "VALUES (%s,'4111','707',100000)", (iid,))
                cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) "
                            "VALUES (%s,'607','401',60000)", (iid,))
            yield conn
        finally:
            conn.rollback()


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_d101_contract_pull_genereaza_perioada(conn_schema_profit):
    """C2 contract uniform: genereaza(conn, schema, Perioada(an), manual) prin pull().
    Venit 100000 - cheltuieli 60000 = profit 40000; impozit 16%% = 6400 (P11=P15)."""
    xml, res = _d101.genereaza(conn_schema_profit, _SCHEMA_D101, Perioada(2026))
    assert res.an == 2026
    assert res.P.get("P1") == 100000 and res.P.get("P2") == 60000, "venituri/cheltuieli din pull"
    assert res.P.get("P3") == 40000, "profit contabil"
    assert res.P.get("P11") == 6400 and res.total_plata_a == 6400, (
        "impozit 16%% pe 40000 = 6400; got P11=%s total=%s" % (res.P.get("P11"), res.total_plata_a))
