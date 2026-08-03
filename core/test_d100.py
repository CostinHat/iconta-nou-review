# -*- coding: utf-8 -*-
"""Teste gardian pentru D100 - modulul a fost REFACUT complet 16.07.2026.

D100 e diferita structural de celelalte declaratii: nu are un set fix de campuri,
ci raporteaza o LISTA de obligatii fiscale (element repetabil <obligatie>), fiecare
din Nomenclatorul ANAF (https://static.anaf.ro/.../NomBugetStat.htm), cu propriul
cod_oblig, cod_bugetar, suma si nr_evid (numar de evidenta a platii, 23 caractere
cu structura fixa si cifra de control).

Atributele reale au fost extrase din D100Validator.jar (constant pool), apoi
verificate/corectate iterativ pe validatorul oficial: cui/luna/tip_oblig NU
apartin sectiunii <obligatie> (desi apar in constant pool, sunt uz intern);
nr_evid are 23 pozitii cu formula exacta de control; totalPlata_A = suma pe
toate campurile (suma_dat+suma_ded+suma_plata+suma_rest), nu doar suma_dat.
"""
import pytest
from core.d100 import calcul_d100, build_xml, _nr_evid, COD_BUGETAR


def _prof():
    return {"cui": "14399840", "nume": "DANTE INTERNATIONAL SA", "adresa": "X"}


def test_nr_evid_are_23_caractere():
    n = _nr_evid("103", 6, 2026, 25, 7, 2026)
    assert len(n) == 23
    assert n.isdigit()


def test_nr_evid_incepe_cu_10_si_cod_oblig():
    """Poz.1-2 = '10' fix, poz.3-5 = cod_oblig (3 cifre)."""
    n = _nr_evid("103", 6, 2026, 25, 7, 2026)
    assert n[:2] == "10"
    assert n[2:5] == "103"
    assert n[5:7] == "01"


def test_nr_evid_cifra_de_control():
    """Poz.22-23 = ultimele 2 cifre din suma primelor 21 pozitii."""
    n = _nr_evid("103", 6, 2026, 25, 7, 2026)
    suma = sum(int(c) for c in n[:21])
    assert n[21:23] == "%02d" % (suma % 100)


def test_calcul_micro():
    # cod_oblig micro = 121 (codul din nomenclator), NU pozitia "5" (respinsa de
    # validator: "valoarea '5' nu se afla in lista"). cont unic 5503 (X-padat C(10)).
    res = calcul_d100(_prof(), 2026, 6, [{"cod_oblig": "121", "suma_dat": 1000, "cota": "1"}])
    assert res.obligatii[0].cod_oblig == "121"
    assert res.obligatii[0].cod_bugetar == COD_BUGETAR["121"] == "5503XXXXXX"


def test_micro_are_cota_1_pe_obligatie():
    """Cerinta validatorului (D100): cod_oblig 121 CERE cota="1" pe <obligatie>; profitul (103)
    NU are cota. Fara ea, validatorul respinge micro-ul."""
    xm = build_xml(calcul_d100(_prof(), 2026, 6, [{"cod_oblig": "121", "suma_dat": 1000, "cota": "1"}]))
    lin_m = [l for l in xm.split("\n") if "<obligatie" in l][0]
    assert 'cota="1"' in lin_m
    xp = build_xml(calcul_d100(_prof(), 2026, 6, [{"cod_oblig": "103", "suma_dat": 2400}]))
    lin_p = [l for l in xp.split("\n") if "<obligatie" in l][0]
    assert 'cota=' not in lin_p


def test_calcul_profit():
    res = calcul_d100(_prof(), 2026, 6, [{"cod_oblig": "103", "suma_dat": 2400}])
    assert res.obligatii[0].cod_oblig == "103"
    assert res.obligatii[0].cod_bugetar == "5503XXXXXX"


def test_obligatie_cu_suma_zero_nu_intra():
    res = calcul_d100(_prof(), 2026, 6, [{"cod_oblig": "103", "suma_dat": 0}])
    assert res.obligatii == []


def test_luna_invalida_e_respinsa():
    """D100 trimestrial: luna trebuie sa fie 3, 6, 9 sau 12."""
    with pytest.raises(ValueError):
        calcul_d100(_prof(), 2026, 5, [{"cod_oblig": "103", "suma_dat": 100}])


def test_xml_nu_are_cui_luna_tip_oblig_pe_obligatie():
    """Regresie: aceste atribute apar in constant pool-ul clasei Obligatie, dar
    validatorul le respinge ca 'atribut necunoscut' - nu se scriu in XML."""
    res = calcul_d100(_prof(), 2026, 6, [{"cod_oblig": "103", "suma_dat": 100}])
    xml = build_xml(res)
    linie_obligatie = [l for l in xml.split("\n") if "<obligatie" in l][0]
    assert 'cui=' not in linie_obligatie
    assert 'luna=' not in linie_obligatie
    assert 'tip_oblig=' not in linie_obligatie


def test_totalPlata_A_e_suma_dat_plus_suma_plata():
    """DUK regula R11b: totalPlata_A = suma_dat + suma_ded + suma_plata + suma_rest.
    Cu suma_plata = suma_dat si ded/rest = 0, e 2x suma_dat."""
    res = calcul_d100(_prof(), 2026, 6, [{"cod_oblig": "103", "suma_dat": 2400}])
    xml = build_xml(res)
    assert 'totalPlata_A="4800"' in xml


# ── CONTRACT UNIFORM A1 (modul 5/10, C1, 31.07.2026) — proba pana la declaratie ──
# genereaza(conn, schema, perioada, manual) prin pull() -> calcul_d100 -> build_xml -> DUK valid.
# N/A temei fiscal (schimbare de tooling: uniformizare contract, comportament identic).
from core.common import Perioada
from core import db as _db, tenant_provisioning as _tp, duk as _duk, d100 as _d100

_SCHEMA_D100 = "ztest_d100_contract"
_D100_DUK = _duk.poate_valida("d100")


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture
def conn_schema_micro():
    """Schema temporara, firma_profil MICRO completa + o nota validata cu venit (cont 704,
    10000 lei, 2026-05-15 = T2). ROLLBACK garantat."""
    _db.init_pool()
    with _db.get_conn() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA_D100)
                cur.execute(_tp.parametrizeaza_template(
                    open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA_D100))
                cur.execute("SET search_path TO %s, public" % _SCHEMA_D100)
                cur.execute(
                    "INSERT INTO firma_profil (id, nume, cui, adresa, oras, judet, caen, "
                    "regim_fiscal, platitor_tva, tip_decont, declarant_nume, declarant_prenume, declarant_functie) "
                    "VALUES (1,'PROBA SRL','14399840','Str. Test 1','Bucuresti','B','6202','micro',true,'L','Pop','Ion','administrator') "
                    "ON CONFLICT (id) DO UPDATE SET regim_fiscal=EXCLUDED.regim_fiscal")
                cur.execute("INSERT INTO inregistrari (data, status, sursa) "
                            "VALUES ('2026-05-15','validata','test') RETURNING id")
                iid = cur.fetchone()[0]
                cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) "
                            "VALUES (%s,'4111','704',10000)", (iid,))
            yield conn
        finally:
            conn.rollback()


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_d100_contract_pull_genereaza_perioada(conn_schema_micro):
    """C1 contract uniform: genereaza(conn, schema, Perioada(an, trim=), manual={'cota':..}).
    Micro, venit 10000 in T2 -> impozit 1%% = 100 (cod_oblig 121, cota 1 - cerinta DUK)."""
    xml, res = _d100.genereaza(conn_schema_micro, _SCHEMA_D100, Perioada(2026, trim=2), {"cota": "1"})
    assert res.an == 2026 and res.luna == 6, "trim=2 -> luna raportare 6"
    assert len(res.obligatii) == 1
    o = res.obligatii[0]
    assert o.cod_oblig == "121" and o.suma_dat == 100 and o.cota == "1", (
        "micro 10000*1%%=100 asteptat; got cod=%s suma=%s cota=%s" % (o.cod_oblig, o.suma_dat, o.cota))
    assert 'cota="1"' in xml


@pytest.mark.skipif(not _db_ok() or not _D100_DUK, reason="DB sau DUK d100 indisponibil")
def test_d100_contract_proba_duk_valid(conn_schema_micro):
    """Proba pana la declaratie: D100 generat prin contractul uniform trece validatorul OFICIAL DUK."""
    xml, res = _d100.genereaza(conn_schema_micro, _SCHEMA_D100, Perioada(2026, trim=2), {"cota": "1"})
    rez = _duk.valideaza(xml, "d100", an=2026, luna=6)
    assert rez["stare"] == "valid", "DUK a respins D100: %s" % rez



def test_cota_micro_121_gard_bidirectional():
    """Struct D100 poz.17a: cod_oblig 121 (micro) CERE cota="1"; orice alt cod_oblig NU are cota
    (altfel validator ERR). Gard bidirectional in build_xml - face imposibil un XML respins."""
    from core.d100 import calcul_d100, build_xml
    import pytest as _pt
    # 121 fara cota -> respins la generare (nu XML tacit invalid)
    res = calcul_d100(_prof(), 2026, 6, [{"cod_oblig": "121", "suma_dat": 1000}])
    with _pt.raises(ValueError):
        build_xml(res)
    # cota pe cod non-micro (103) -> respins
    res2 = calcul_d100(_prof(), 2026, 6, [{"cod_oblig": "103", "suma_dat": 1000, "cota": "1"}])
    with _pt.raises(ValueError):
        build_xml(res2)
    # 121 + cota "1" -> corect, cota=1 in XML
    res3 = calcul_d100(_prof(), 2026, 6, [{"cod_oblig": "121", "suma_dat": 1000, "cota": "1"}])
    assert 'cota="1"' in build_xml(res3)
