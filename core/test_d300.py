# -*- coding: utf-8 -*-
"""Teste gardian pentru D300 — lantul de calcul R27->R42 lipsea complet.

Descoperit prin audit pe date reale (16.07.2026): modulul calcula R17 (colectata)
si R22/R30/R31 (deductibila), apoi sarea direct la R40/R42 (rezultat), ignorand
lantul obligatoriu R27->R28->R32->R34->R37->R40->R42 pe care validatorul il
verifica formula cu formula (structura_D300_v12.0.0_10022026.pdf).
"""
from decimal import Decimal
from core.common import Perioada
from core.d300 import calcul_d300


def _prof(pro_rata=100):
    return {"cui": "14399840", "nume": "X", "adresa": "Y", "banca": "BCR",
            "iban": "RO1", "caen": "4711", "tip_decont": "L", "pro_rata": pro_rata}


def test_lantul_R27_R42_se_calculeaza_complet():
    """Livrare 10000@21% (TVA 2100), achizitie 1000@21% (TVA 210) -> de plata 1890."""
    facturi = [
        {"directie": "emisa", "total": 12100, "tva": 2100},
        {"directie": "primita", "total": 1210, "tva": 210},
    ]
    res = calcul_d300(_prof(), Perioada(2026, luna=6), facturi)
    assert res.R["R17_2"] == 2100          # total colectata
    assert res.R["R27_2"] == 210           # total deductibila (lipsea complet)
    assert res.R["R28_2"] == 210           # subtotal dedusa
    assert res.R["R32_2"] == 210           # total dedusa
    assert res.R["R34_2"] == 1890          # taxa de plata (17-32)
    assert res.R["R37_2"] == 1890          # TVA de plata cumulat
    assert res.R["R41_2"] == 1890          # sold de plata la sfarsit
    assert "R42_2" not in res.R            # nu exista sold negativ simultan
    assert res.tva_de_plata == 1890


def test_formula_R27_respecta_structura_oficiala():
    """R27_2 = R18_2+R19_2+R20_2+R21_2+R22_2+R23_2+R24_2+R25_2+R43_2+R44_2+R74_2+R75_2"""
    facturi = [{"directie": "primita", "total": 1210, "tva": 210}]  # -> R22_2=210
    res = calcul_d300(_prof(), Perioada(2026, luna=6), facturi)
    assert res.R["R27_2"] == res.R["R22_2"]


def test_achizitie_mai_mare_decat_livrarea_da_sold_negativ():
    facturi = [
        {"directie": "emisa", "total": 1210, "tva": 210},
        {"directie": "primita", "total": 12100, "tva": 2100},
    ]
    res = calcul_d300(_prof(), Perioada(2026, luna=6), facturi)
    assert res.R["R33_2"] == 1890          # suma negativa in perioada
    assert res.R["R40_2"] == 1890          # suma negativa cumulata
    assert res.R["R42_2"] == 1890          # sold negativ la sfarsit
    assert "R34_2" not in res.R
    assert res.tva_de_recuperat == 1890


def test_fara_operatiuni_nu_scrie_randuri_goale():
    res = calcul_d300(_prof(), Perioada(2026, luna=6), [])
    assert "R27_2" not in res.R
    assert "R32_2" not in res.R


def test_d300_manual_cheie_necunoscuta_ridica():
    """Contract A1: manual d300 accepta doar chei Rxx_y; o cheie straina (typo) RIDICA, nu se
    ignora tacut (clasa 'or 21')."""
    import pytest
    with pytest.raises(ValueError) as e:
        calcul_d300(_prof(), Perioada(2026, luna=6), [], {"R9_1": 100, "totalGresit": 5})
    assert "necunoscut" in str(e.value).lower() and "totalGresit" in str(e.value)

import pytest
from core import duk as _duk300
from core.d300 import build_xml
_D300_DUK = _duk300.poate_valida("d300")


# ============================================================
#  Cluster cote TVA -> randuri | d300. Maparea cotelor pe randurile D300 (structura
#  v12.0.0, confirmata prin marja validatorului DUK). Bug reparat: achizitii deductibile
#  11% erau puse la R74 (=Rd.24.1, cota 19% legacy, marja 18-20%) si 9% la R76 (=taxare
#  inversa Rd.27.4). Corect: 11%->R23 (Rd.25), 21%->R22 (Rd.24).
# ============================================================
def test_cote_tva_maparea_pe_randuri_d300():
    facturi = [
        {"directie": "emisa", "total": 1210, "tva": 210},    # 21%
        {"directie": "emisa", "total": 1110, "tva": 110},    # 11%
        {"directie": "emisa", "total": 1090, "tva": 90},     # 9%
        {"directie": "primita", "total": 1210, "tva": 210},  # 21% deductibil
        {"directie": "primita", "total": 1110, "tva": 110},  # 11% deductibil
    ]
    res = calcul_d300(_prof(), Perioada(2026, luna=6), facturi)
    # LIVRARI (colectata): 21->Rd.9, 11->Rd.10, 9->Rd.11
    assert (res.R["R9_1"], res.R["R9_2"]) == (1000, 210)
    assert (res.R["R10_1"], res.R["R10_2"]) == (1000, 110)
    assert (res.R["R11_1"], res.R["R11_2"]) == (1000, 90)
    # ACHIZITII DEDUCTIBILE: 21->Rd.24(R22), 11->Rd.25(R23)
    assert (res.R["R22_1"], res.R["R22_2"]) == (1000, 210)
    assert (res.R["R23_1"], res.R["R23_2"]) == (1000, 110)   # 11% -> R23, NU R74
    # GARD anti-regresie: 11% NU merge la R74 (=19% legacy) si nici la R76 (=taxare inversa)
    assert res.R.get("R74_1", 0) == 0 and res.R.get("R74_2", 0) == 0
    assert res.R.get("R76_1", 0) == 0


def test_9pct_deductibil_nu_emite_rand_invalid_si_avertizeaza():
    # 9% deductibil: R75 (v12) / R76 respinse de validatorul DUK instalat -> NU se emit
    # (un atribut invalid ar respinge intreaga declaratie); se semnaleaza pentru declarare manuala.
    facturi = [{"directie": "primita", "total": 1090, "tva": 90}]  # 9% deductibil
    res = calcul_d300(_prof(), Perioada(2026, luna=6), facturi)
    assert res.R.get("R75_1", 0) == 0 and res.R.get("R76_1", 0) == 0
    assert any("9%" in a and "MANUAL" in a for a in res.avertismente)


@pytest.mark.skipif(not _D300_DUK, reason="DUK d300 indisponibil")
def test_cote_tva_d300_proba_duk_valid():
    # Proba pana la declaratie: D300 cu livrari 21/11/9 + achizitii 21/11 trece DUKIntegrator.
    # Marja validatorului (R9_2 in 20-22%R9_1, R10_2 in 10-12%, R11_2 in 8-10%, R22=21%, R23=11%)
    # respinge orice swap cota<->rand - validarea confirma maparea. Un 9% deductibil in R76 (vechiul
    # cod) ERA respins de DUK - de aceea reparatia trece proba aici.
    facturi = [
        {"directie": "emisa", "total": 1210, "tva": 210},
        {"directie": "emisa", "total": 1110, "tva": 110},
        {"directie": "emisa", "total": 1090, "tva": 90},
        {"directie": "primita", "total": 1210, "tva": 210},
        {"directie": "primita", "total": 1110, "tva": 110},
        {"directie": "primita", "total": 1090, "tva": 90},   # 9% deductibil -> manual (avertisment), nu emis
    ]
    res = calcul_d300(_prof(), Perioada(2026, luna=6), facturi)
    rez = _duk300.valideaza(build_xml(res), "d300", an=2026, luna=6)
    assert rez["stare"] == "valid", "DUK a respins D300: %s" % rez.get("erori")


# ============================================================
#  Cluster randuri / checksum | d300: totalPlata_A = suma(camp 27..124) EXCEPT 62(14.1)/63(14.2).
#  Struct D300 (structura_D300 OPANAF): checksum = suma tuturor randurilor R emise (fiecare rand R*_*
#  = un camp 27..124); campurile 62/63 (rd 14.1=R67, 14.2=R68) au fost ELIMINATE din suma de control.
# ============================================================
@pytest.mark.skipif(not _D300_DUK, reason="DUK d300 indisponibil")
def test_checksum_totalplata_a_egal_suma_randuri_emise_duk_valid():
    """totalPlata_A emis == sum(res.R) (sursa unica, ca celelalte declaratii) SI e checksum-ul pe care
    DUK il impune (ERR suma de control eronata daca difera). Decont fix: emisa 1210/210(21%) + 1110/110(11%)
    + primita 1210/210(21%) -> golden 7810."""
    facturi = [
        {"directie": "emisa", "total": 1210, "tva": 210},
        {"directie": "emisa", "total": 1110, "tva": 110},
        {"directie": "primita", "total": 1210, "tva": 210},
    ]
    res = calcul_d300(_prof(), Perioada(2026, luna=6), facturi)
    assert res.total_plata_a == sum(res.R.values()), "totalPlata_A trebuie sa fie suma randurilor emise"
    assert res.total_plata_a == 7810, "golden checksum; got %d" % res.total_plata_a
    rez = _duk300.valideaza(build_xml(res), "d300", an=2026, luna=6)
    assert rez["stare"] == "valid", "DUK a respins checksum-ul D300: %s" % rez.get("erori")


def test_randuri_14_1_14_2_eliminate_nu_intra_in_checksum():
    """Campurile 62(14.1=R67) si 63(14.2=R68) au fost ELIMINATE din suma de control (struct D300).
    Nu-s in nicio allow-list manuala -> gardul-clasa le RESPINGE, deci nu pot intra niciodata in
    sum(res.R) = totalPlata_A. Fara acest pin, adaugarea lor tacita in allow-list ar strica checksum-ul."""
    facturi = [{"directie": "emisa", "total": 1210, "tva": 210}]
    for rd in ("R67_1", "R68_1"):
        with pytest.raises(ValueError, match="neacceptate"):
            calcul_d300(_prof(), Perioada(2026, luna=6), facturi, manual={rd: 500})


# ============================================================
#  Cluster exigibilitate / TVA la incasare | d300 (art.282 alin.3+8 CF, OUG 8/2026).
#  Firma pe sistem: exigibilitate la INCASARE/PLATA, proportional, suta marita.
#  Calcul PUR (fara DB): facturile poarta `decontari=[{suma, cota}]` (sumele decontate in perioada).
# ============================================================
def test_tva_la_incasare_exigibilitate_pe_decontari_suta_marita():
    prof = dict(_prof(), tva_la_incasare=True)
    facturi = [
        {"directie": "emisa", "decontari": [{"suma": 1210, "cota": 21}]},   # incasat integral 21%
        {"directie": "emisa", "decontari": [{"suma": 605, "cota": 21}]},    # incasat partial 21%
        {"directie": "primita", "decontari": [{"suma": 555, "cota": 11}]},  # platit 11%
    ]
    res = calcul_d300(prof, Perioada(2026, luna=6), facturi)
    # colectata 21% (Rd.9): suta marita 1210->210 (baza 1000) + 605->105 (baza 500) = baza 1500, TVA 315
    assert (res.R["R9_1"], res.R["R9_2"]) == (1500, 315)
    # deductibila 11% (Rd.25/R23): 555 -> TVA 55, baza 500
    assert (res.R["R23_1"], res.R["R23_2"]) == (500, 55)


def test_tva_la_incasare_partial_proportional():
    # art.282 alin.3: exigibilitate la incasarea PARTIALA. Factura 1210@21% incasata doar 605
    # -> exigibil DOAR jumatate (TVA 105, baza 500), nu 210 pe toata factura.
    prof = dict(_prof(), tva_la_incasare=True)
    res = calcul_d300(prof, Perioada(2026, luna=6),
                      [{"directie": "emisa", "decontari": [{"suma": 605, "cota": 21}]}])
    assert (res.R["R9_1"], res.R["R9_2"]) == (500, 105)


def test_tva_la_incasare_neincasat_nu_e_exigibil():
    # factura emisa dar NEINCASATA in perioada (fara decontari) -> nimic exigibil (rand gol).
    prof = dict(_prof(), tva_la_incasare=True)
    res = calcul_d300(prof, Perioada(2026, luna=6),
                      [{"directie": "emisa", "decontari": []}])
    assert res.R.get("R9_1", 0) == 0 and res.R.get("R9_2", 0) == 0


def test_firma_fara_tva_incasare_ramane_pe_emitere():
    # GARD anti-regresie: firma normala (fara flag) -> exigibilitate la faptul generator (emitere),
    # `decontari` sunt IGNORATE, comportamentul vechi neschimbat.
    res = calcul_d300(_prof(), Perioada(2026, luna=6),
                      [{"directie": "emisa", "total": 1210, "tva": 210,
                        "decontari": [{"suma": 99999, "cota": 21}]}])
    assert (res.R["R9_1"], res.R["R9_2"]) == (1000, 210)   # din emitere, decontari ignorate


# ============================================================
#  TVA la incasare - proba pe DB reala (pull + exigibilitate din decontari) + proba DUK.
# ============================================================
from core import db as _db300, tenant_provisioning as _tp300, d300 as _d300mod
_SCHEMA_TVAI = "test_d300_tvai"


def _db300_ok():
    try:
        _db300.init_pool()
        with _db300.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture
def conn_tvai():
    """Firma pe TVA la incasare. F1 emisa 1210@21% in luna 5, INCASATA (5121=4111) in luna 6.
    F2 primita 555@11% in luna 5, PLATITA (401=5121) in luna 6. ROLLBACK garantat."""
    _db300.init_pool()
    with _db300.get_conn() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA_TVAI)
                cur.execute(_tp300.parametrizeaza_template(
                    open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA_TVAI))
                cur.execute("SET search_path TO %s, public" % _SCHEMA_TVAI)
                cur.execute(
                    "INSERT INTO firma_profil (id, nume, cui, adresa, oras, judet, caen, banca, iban, "
                    "regim_fiscal, platitor_tva, tip_decont, tva_la_incasare, declarant_nume, declarant_prenume, declarant_functie) "
                    "VALUES (1,'TVAI SRL','14399840','Str Test 1','Bucuresti','B','4711','BCR','RO49AAAA1B31007593840000',"
                    "'real',true,'L',true,'Pop','Ion','administrator') "
                    "ON CONFLICT (id) DO UPDATE SET tva_la_incasare=true")
                # F1 emisa (luna 5), incasata luna 6
                cur.execute("INSERT INTO facturi (numar, data_emitere, total, tva, directie) "
                            "VALUES ('F1','2026-05-20',1210,210,'emisa') RETURNING id")
                f1 = cur.fetchone()[0]
                cur.execute("INSERT INTO factura_linii (factura_id, descriere, cantitate, pret_unitar, cota_tva) "
                            "VALUES (%s,'marfa',1,1000,21)", (f1,))
                cur.execute("INSERT INTO inregistrari (data, factura_id, status, sursa) "
                            "VALUES ('2026-06-10',%s,'validata','test') RETURNING id", (f1,))
                n1 = cur.fetchone()[0]
                cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) "
                            "VALUES (%s,'5121','4111',1210)", (n1,))
                # F2 primita (luna 5), platita luna 6
                cur.execute("INSERT INTO facturi (numar, data_emitere, total, tva, directie) "
                            "VALUES ('F2','2026-05-22',555,55,'primita') RETURNING id")
                f2 = cur.fetchone()[0]
                cur.execute("INSERT INTO factura_linii (factura_id, descriere, cantitate, pret_unitar, cota_tva) "
                            "VALUES (%s,'servicii',1,500,11)", (f2,))
                cur.execute("INSERT INTO inregistrari (data, factura_id, status, sursa) "
                            "VALUES ('2026-06-12',%s,'validata','test') RETURNING id", (f2,))
                n2 = cur.fetchone()[0]
                cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) "
                            "VALUES (%s,'401','5121',555)", (n2,))
                # F3 taxare inversa emisa (regim general art.282(6)) incasata 5000 in luna 6 -> EXCLUSA din
                # cash-basis. Daca ar intra, R9_1 ar deveni ~5132 si asertiile de mai jos ar pica (gard).
                cur.execute("INSERT INTO facturi (numar, data_emitere, total, tva, directie, taxare_inversa) "
                            "VALUES ('F3','2026-05-25',5000,0,'emisa',true) RETURNING id")
                f3 = cur.fetchone()[0]
                cur.execute("INSERT INTO factura_linii (factura_id, descriere, cantitate, pret_unitar, cota_tva) "
                            "VALUES (%s,'fier vechi',1,5000,21)", (f3,))
                cur.execute("INSERT INTO inregistrari (data, factura_id, status, sursa) "
                            "VALUES ('2026-06-15',%s,'validata','test') RETURNING id", (f3,))
                n3 = cur.fetchone()[0]
                cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) "
                            "VALUES (%s,'5121','4111',5000)", (n3,))
            yield conn
        finally:
            conn.rollback()


@pytest.mark.skipif(not _db300_ok(), reason="DB indisponibil")
def test_tva_incasare_exigibil_la_decontare_nu_la_emitere(conn_tvai):
    # luna 6 (decontare): exigibil. F1 incasat -> R9 21%; F2 platit -> R23 11%.
    prof, facturi = _d300mod.pull(conn_tvai, _SCHEMA_TVAI, Perioada(2026, luna=6))
    assert prof["tva_la_incasare"] is True
    res = calcul_d300(prof, Perioada(2026, luna=6), facturi)
    assert (res.R["R9_1"], res.R["R9_2"]) == (1000, 210)    # colectata 21% la incasare
    assert (res.R["R23_1"], res.R["R23_2"]) == (500, 55)    # deductibila 11% la plata
    # luna 5 (emitere, dar NEDECONTAT inca): nimic exigibil
    prof5, fac5 = _d300mod.pull(conn_tvai, _SCHEMA_TVAI, Perioada(2026, luna=5))
    res5 = calcul_d300(prof5, Perioada(2026, luna=5), fac5)
    assert res5.R.get("R9_1", 0) == 0 and res5.R.get("R23_1", 0) == 0


@pytest.mark.skipif(not _db300_ok() or not _D300_DUK, reason="DB/DUK d300")
def test_tva_incasare_d300_proba_duk_valid(conn_tvai):
    prof, facturi = _d300mod.pull(conn_tvai, _SCHEMA_TVAI, Perioada(2026, luna=6))
    res = calcul_d300(prof, Perioada(2026, luna=6), facturi)
    rez = _duk300.valideaza(build_xml(res), "d300", an=2026, luna=6)
    assert rez["stare"] == "valid", "DUK a respins D300 TVA la incasare: %s" % rez.get("erori")


# ============================================================
#  Taxare inversa | d300 (CF art.331: beneficiarul e obligat la plata TVA - auto-taxare).
#  Beneficiarul declara MANUAL rd.12 (colectata, self-charge) + rd.27/R25 (deductibila) = net zero.
#  BUG reparat: R12_ lipsea din allow-list-ul manual -> reverse charge era SILENTIOS ignorat
#  (contabilul introducea rd.12 dar D300 il arunca -> auto-taxare nedeclarata).
# ============================================================
def _rc_manual():
    return {"R12_1": 1000, "R12_2": 210, "R12_1_1": 1000, "R12_1_2": 210,   # rd.12 colectata 21%
            "R25_1": 1000, "R25_2": 210, "R25_1_1": 1000, "R25_1_2": 210}   # rd.27 deductibila 21% (= rd.12)


def test_taxare_inversa_rd12_se_declara_manual():
    res = calcul_d300(_prof(), Perioada(2026, luna=6), [], _rc_manual())
    # rd.12 (auto-taxare colectata) NU mai e aruncat:
    assert (res.R["R12_1"], res.R["R12_2"]) == (1000, 210)
    # intra in totalul colectat R17:
    assert res.R["R17_1"] >= 1000 and res.R["R17_2"] >= 210
    # latura deductibila (rd.27/R25) = rd.12 -> net zero pe deducere integrala:
    assert (res.R["R25_1"], res.R["R25_2"]) == (1000, 210)


def test_taxare_inversa_r12_fara_fix_ar_fi_dropped():
    # GARD anti-regresie: daca R12_ dispare din allow-list, rd.12 devine None si testul de mai sus pica.
    # Aici verificam direct ca un R12 manual ajunge in rezultat (nu tacut ignorat ca inainte de fix).
    res = calcul_d300(_prof(), Perioada(2026, luna=6), [], {"R12_1": 500, "R12_2": 105})
    assert res.R.get("R12_1") == 500, "rd.12 (taxare inversa) e ignorat - R12_ lipseste din allow-list"


@pytest.mark.skipif(not _D300_DUK, reason="DUK d300 indisponibil")
def test_taxare_inversa_d300_proba_duk_valid():
    # Proba pana la declaratie: decont echilibrat (rd.12 = rd.27) trece DUKIntegrator. Validatorul cere
    # R25_x == R12_x (rd.27<->rd.12, regulile V_19/V_21) - deci validarea confirma perechea colectata/deductibila.
    res = calcul_d300(_prof(), Perioada(2026, luna=6), [], _rc_manual())
    rez = _duk300.valideaza(build_xml(res), "d300", an=2026, luna=6)
    assert rez["stare"] == "valid", "DUK a respins reverse charge D300: %s" % rez.get("erori")


# ============================================================
#  Pro-rata deducere | d300 (CF art.300: persoana cu regim mixt - deducere pro-rata cand nu poate
#  tine evidente separate). D300: R31_2 = "Ajustari conform pro-rata" (Rd.33 structura v12) =
#  -(taxa dedusa x fractia nedeductibila); total dedus R32 = R28 x pro_rata/100. NU scalare directa.
# ============================================================
def test_pro_rata_ajustare_deductibila_art300():
    facturi = [{"directie": "primita", "total": 1210, "tva": 210}]   # achizitie 21%
    res = calcul_d300(_prof(pro_rata=80), Perioada(2026, luna=6), facturi)
    assert res.R["R22_2"] == 210      # deductibila bruta (rd.24)
    assert res.R["R28_2"] == 210      # subtotal dedusa inainte de ajustare (rd.30)
    assert res.R["R31_2"] == -42      # ajustare pro-rata (rd.33): -210 x (100-80)/100
    assert res.R["R32_2"] == 168      # total dedusa: 210 x 80%


def test_pro_rata_100_fara_ajustare():
    # GARD: pro_rata=100 (uzual) -> nicio ajustare (R31 absent), deducere integrala.
    facturi = [{"directie": "primita", "total": 1210, "tva": 210}]
    res = calcul_d300(_prof(100), Perioada(2026, luna=6), facturi)
    assert "R31_2" not in res.R
    assert res.R["R32_2"] == 210


@pytest.mark.skipif(not _D300_DUK, reason="DUK d300 indisponibil")
def test_pro_rata_d300_proba_duk_valid():
    # Proba pana la declaratie: decont cu pro-rata 80% (achizitie + livrare) trece DUKIntegrator.
    facturi = [{"directie": "primita", "total": 1210, "tva": 210},
               {"directie": "emisa", "total": 2420, "tva": 420}]
    res = calcul_d300(_prof(pro_rata=80), Perioada(2026, luna=6), facturi)
    rez = _duk300.valideaza(build_xml(res), "d300", an=2026, luna=6)
    assert rez["stare"] == "valid", "DUK a respins pro-rata D300: %s" % rez.get("erori")


# ============================================================
#  Rotunjire aritmetica | d300 (DUK regula A91b: sumele fiscale se rotunjesc half-up, nu bancar).
#  _int = numar_fiscal(...).quantize(ROUND_HALF_UP). Deja in gardul de identitate cross-generator.
# ============================================================
def test_d300_rotunjeste_aritmetic_nu_bancar():
    from core.d300 import _int
    assert _int(112.5) == 113   # aritmetic; bancar (half-to-even) ar da 112
    assert _int(2.5) == 3       # bancar ar da 2 (par)
    assert _int(0.5) == 1       # bancar ar da 0
    assert _int(112.4) == 112
    assert _int(112.6) == 113


# ============================================================
#  Ajustari | d300 (CF art.304 regularizari + art.305 ajustari bunuri de capital). Randurile de
#  ajustare/regularizare se declara MANUAL si intra in totaluri. BUG reparat: R29/R30/R35/R36
#  lipseau din allow-list-ul manual -> ajustarile erau SILENTIOS aruncate (nedeclarate).
#    R29 = TVA restituita cumparatori straini (Rd.31) ; R30 = Regularizari taxa dedusa (Rd.32) -> R32
#    R35 = sold reportat neachitat ; R36 = Diferente TVA de plata (inspectie, Rd.38) -> R37 cumulat
# ============================================================
def test_ajustari_regularizari_deductibila_se_declara():
    facturi = [{"directie": "primita", "total": 1210, "tva": 210}]   # R28 dedusa = 210
    res = calcul_d300(_prof(), Perioada(2026, luna=6), facturi,
                      {"R29_1": 100, "R29_2": 21, "R30_1": 500, "R30_2": 50})
    assert res.R["R29_2"] == 21    # restituiri cumparatori straini declarate
    assert res.R["R30_2"] == 50    # regularizari taxa dedusa declarate
    assert res.R["R32_2"] == 281   # total dedusa = 210 (R28) + 21 (R29) + 50 (R30)


def test_regularizari_rezultat_r36_intra_in_cumulat():
    # R36 (diferente de TVA de plata din inspectie) intra in R37 (TVA de plata cumulat).
    facturi = [{"directie": "emisa", "total": 6050, "tva": 1050},
               {"directie": "primita", "total": 1210, "tva": 210}]
    res = calcul_d300(_prof(), Perioada(2026, luna=6), facturi, {"R36_2": 100})
    assert res.R["R36_2"] == 100
    assert res.R["R37_2"] == res.R["R34_2"] + 100   # cumulat = plata perioada + diferenta inspectie


def test_ajustari_r30_fara_fix_ar_fi_dropped():
    # GARD anti-regresie: daca R30_ dispare din allow-list, regularizarea devine None (silentios ignorata).
    res = calcul_d300(_prof(), Perioada(2026, luna=6), [], {"R30_2": 99, "R35_2": 30})
    assert res.R.get("R30_2") == 99, "regularizari (R30) ignorate - R30_ lipseste din allow-list"
    assert res.R.get("R35_2") == 30, "sold reportat (R35) ignorat - R35_ lipseste din allow-list"


@pytest.mark.skipif(not _D300_DUK, reason="DUK d300 indisponibil")
def test_ajustari_d300_proba_duk_valid():
    facturi = [{"directie": "emisa", "total": 6050, "tva": 1050},
               {"directie": "primita", "total": 1210, "tva": 210}]
    res = calcul_d300(_prof(), Perioada(2026, luna=6), facturi, {"R30_1": 500, "R30_2": 50, "R36_2": 100})
    rez = _duk300.valideaza(build_xml(res), "d300", an=2026, luna=6)
    assert rez["stare"] == "valid", "DUK a respins ajustari D300: %s" % rez.get("erori")


def test_d300_manual_rand_necunoscut_ridica_nu_dispare():
    # [GARD CLASA] un rand manual care nu e in allow-list produce EROARE VIZIBILA, nu drop tacit.
    # Radacina bug-urilor R12 / R29-R30-R35-R36 / R38-R39-R43-R44: allow-list incompleta inghitea randuri.
    import pytest as _pt
    with _pt.raises(ValueError) as e:
        calcul_d300(_prof(), Perioada(2026, luna=6), [], {"R99_1": 100})
    assert "neacceptate" in str(e.value) and "R99_1" in str(e.value)
