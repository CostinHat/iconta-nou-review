# -*- coding: utf-8 -*-
"""Gard B1-B4 (15.08.2026): comportamentele NOI ale remedierii D300 nu aveau test de
regresie dedicat. Fiecare asertie de aici ar fi PICAT inainte de B1 (comportament vechi
descris in comentariul fiecarui test). Regula permanenta: regula noua intra SIMULTAN in
verificator.

Confruntat cu sursa: core/d300.py (calcul_d300 rutare IC/export via tert_tara; pull() fereastra
pe exigibilitate cu exceptie avans; _pull_furnizor_incasare deducere amanata art.297 alin.2) +
core/d300_manual_api.py (persistenta d300_manual, paritate preview<->depunere).

Stil de fixtura identic cu core/test_d300.py / test_d300_zero_rate.py: pentru calculul PUR se
construiesc `prof` + lista de `facturi` si se cheama calcul_d300 FARA DB; pentru caile care depind
de SQL (fereastra avans, deducerea amanata, persistenta manual) se cladeste o schema de test din
tenant_template.sql (ca fixtura conn_tvai) si se cheama pull()/genereaza() CU DB.

Toate aserttile/marker ASCII (regula diacritice: log/assert ASCII); numerele sunt verificabile
(21% cota standard 2026: baza x 21 / 100).
"""
import pytest
from core.common import Perioada
from core.d300 import calcul_d300


def _prof():
    return {"cui": "14399840", "nume": "X", "banca": "BCR", "iban": "RO1", "caen": "4711",
            "tip_decont": "L", "pro_rata": 100}


# ============================================================
#  1-4, 8: RUTAREA PURA (calcul_d300, fara DB). tert_tara decide IC/export, NU cota.
# ============================================================
def test_livrare_ic_bunuri_ruteaza_R1():
    """[sit.1] Livrare IC bunuri: EMISA catre partener UE (DE), cota 0% -> rd.1 (R1_1).
    RED pre-B1: strainele 0% cadeau in R26/avertisment (nu exista rutare pe tert_tara)."""
    f = {"directie": "emisa", "tert_tara": "DE", "linii": [(1, 8000, 0)]}
    res = calcul_d300(_prof(), Perioada(2026, luna=8), [f])
    assert res.R.get("R1_1") == 8000, "livrare IC bunuri catre UE -> rd.1 (R1_1)"
    assert "R26_1" not in res.R, "livrarea IC NU merge la R26 (achizitii scutite)"
    assert "R9_1" not in res.R, "livrarea IC 0% NU cade in colectat intern (rd.9)"


def test_achizitie_ic_bunuri_R5_oglinda_R18():
    """[sit.2] Achizitie IC bunuri: PRIMITA din UE (DE), 0% -> taxare inversa net zero:
    rd.5 colectat + oglinda rd.18 deductibil, R18 == R5 (autolichidare la cota interna 21%).
    RED pre-B1: cadeau in R26 (achizitie scutita), nu se autolichidau."""
    f = {"directie": "primita", "tert_tara": "DE", "linii": [(1, 15000, 0)]}
    res = calcul_d300(_prof(), Perioada(2026, luna=6), [f])
    assert (res.R.get("R5_1"), res.R.get("R5_2")) == (15000, 3150), "rd.5 colectat (15000 x 21%)"
    assert (res.R.get("R18_1"), res.R.get("R18_2")) == (15000, 3150), "rd.18 deductibil"
    assert res.R["R18_1"] == res.R["R5_1"] and res.R["R18_2"] == res.R["R5_2"], "oglinda net zero R18==R5"
    assert res.tva_de_plata == 0 and res.tva_de_recuperat == 0, "autolichidare -> impact zero"


def test_export_non_ue_ruteaza_R14():
    """[sit.3] Export non-UE: EMISA catre partener non-UE (US), 0% -> rd.14 (scutit cu drept).
    RED pre-B1: strainele 0% cadeau in R26/avertisment, nu la rd.14."""
    f = {"directie": "emisa", "tert_tara": "US", "linii": [(1, 6000, 0)]}
    res = calcul_d300(_prof(), Perioada(2026, luna=9), [f])
    assert res.R.get("R14_1") == 6000, "export non-UE -> rd.14"
    assert "R26_1" not in res.R, "exportul NU merge la R26"
    assert "R9_1" not in res.R, "exportul NU cade in colectat intern (rd.9)"


def test_discriminare_pe_tara_RO_zero_nu_autoclasifica():
    """[discriminare] Aceeasi factura 0% cu tert_tara='RO' NU se auto-clasifica in R1/R14 (ramane
    pentru clasificare manuala) -> dovada ca rutarea e pe TARA, nu pe cota. Coerent cu
    test_d300_zero_rate. RED daca rutarea ar fi pe cota: DE si RO ar produce acelasi R1/R14."""
    f = {"directie": "emisa", "tert_tara": "RO", "linii": [(1, 8000, 0)]}
    res = calcul_d300(_prof(), Perioada(2026, luna=8), [f])
    assert "R1_1" not in res.R, "livrarea 0% interna NU e livrare IC (rd.1)"
    assert "R14_1" not in res.R, "livrarea 0% interna NU e export (rd.14)"
    assert "R9_1" not in res.R, "0% NU cade in colectat cu cota"
    assert any("R14/R15" in a for a in res.avertismente), \
        "livrarea 0% interna se semnaleaza per-linie pentru clasificare manuala R14/R15"


def test_antidubla_numarare_ic_livrare_manual_ridica():
    """[anti-dubla-numarare] rand DERIVAT automat din facturi in perioada (rd.1 din livrare IC)
    + acelasi rand trimis prin `manual` -> ValueError vizibil, nu insumare tacita.
    RED pre-B1: rutarea IC nu exista, deci nici gardul anti-dubla-numarare pe R1."""
    f = {"directie": "emisa", "tert_tara": "DE", "linii": [(1, 8000, 0)]}
    with pytest.raises(ValueError) as ei:
        calcul_d300(_prof(), Perioada(2026, luna=8), [f], {"R1_1": 8000})
    assert "dubla numarare" in str(ei.value), "mesaj vizibil de dubla numarare pe rd.1"


# ============================================================
#  5-7: CAILE CU DB (fereastra pe exigibilitate, deducere amanata, persistenta manual).
#  Schema de test cladita din tenant_template.sql (ca fixtura conn_tvai din test_d300.py).
# ============================================================
from core import db as _db, tenant_provisioning as _tp, d300 as _d300mod
_SCHEMA = "test_d300_b1_rutare"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture(scope="module")
def conn_b1():
    """Firma regim normal. Facturi cu campurile noi B1:
      AV1  emisa 2026-07-05, faptul generator 2026-10-15, tip_operatiune='avans', 1000/210 @21%
      ON1  emisa 2026-10-20, normala (fara avans), 2000/420 @21%   -> contrast in octombrie
      FTI1 primita 2026-11-08, furnizor_tva_incasare=true, 2000/420 @21%, PLATITA (401=5121) 2026-12-15
    ROLLBACK garantat + DROP la teardown (fara commit)."""
    _db.init_pool()
    with _db.get_conn() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
                cur.execute(_tp.parametrizeaza_template(
                    open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA))
                cur.execute("SET search_path TO %s, public" % _SCHEMA)
                cur.execute(
                    "INSERT INTO firma_profil (id, nume, cui, adresa, oras, judet, caen, banca, iban, "
                    "regim_fiscal, platitor_tva, tip_decont, declarant_nume, declarant_prenume, declarant_functie) "
                    "VALUES (1,'B1 SRL','14399840','Str Test 1','Bucuresti','B','4711','BCR','RO49AAAA1B31007593840000',"
                    "'real',true,'L','Pop','Ion','administrator')")
                # AVANS: exigibil la EMITERE (iulie), desi faptul generator e in octombrie.
                cur.execute("INSERT INTO facturi (numar, data_emitere, data_faptului_generator, directie, "
                            "total, tva, tert_tara, tip_operatiune, status) "
                            "VALUES ('AV1','2026-07-05','2026-10-15','emisa',1210,210,'RO','avans','emisa') RETURNING id")
                av = cur.fetchone()[0]
                cur.execute("INSERT INTO factura_linii (factura_id, descriere, cantitate, pret_unitar, cota_tva) "
                            "VALUES (%s,'avans',1,1000,21)", (av,))
                # Normala in octombrie (contrast: octombrie are 2000/420, NU 3000/630).
                cur.execute("INSERT INTO facturi (numar, data_emitere, directie, total, tva, tert_tara, "
                            "tip_operatiune, status) "
                            "VALUES ('ON1','2026-10-20','emisa',2420,420,'RO','normal','emisa') RETURNING id")
                on = cur.fetchone()[0]
                cur.execute("INSERT INTO factura_linii (factura_id, descriere, cantitate, pret_unitar, cota_tva) "
                            "VALUES (%s,'marfa',1,2000,21)", (on,))
                # FURNIZOR la incasare: primita noiembrie, deducere amanata pana la PLATA (decembrie).
                cur.execute("INSERT INTO facturi (numar, data_emitere, directie, total, tva, tert_tara, "
                            "furnizor_tva_incasare, status) "
                            "VALUES ('FTI1','2026-11-08','primita',2420,420,'RO',true,'emisa') RETURNING id")
                fti = cur.fetchone()[0]
                cur.execute("INSERT INTO factura_linii (factura_id, descriere, cantitate, pret_unitar, cota_tva) "
                            "VALUES (%s,'servicii',1,2000,21)", (fti,))
                cur.execute("INSERT INTO inregistrari (data, factura_id, status, sursa) "
                            "VALUES ('2026-12-15',%s,'validata','test') RETURNING id", (fti,))
                nid = cur.fetchone()[0]
                cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) "
                            "VALUES (%s,'401','5121',2420)", (nid,))
            yield conn
        finally:
            conn.rollback()
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
            conn.commit()


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_avans_fereastra_pe_emitere_nu_reapare(conn_b1):
    """[sit.4] Avans: exigibil la EMITERE (art.282 alin.2 lit.b). Factura de avans (data_emitere in
    IULIE, faptul generator in OCTOMBRIE) apare in decontul lunii facturii (iulie) si NU reapare in
    octombrie la faptul generator. RED pre-B1: fereastra pull era pe data_emitere fara COALESCE si
    fara exceptia avans -> nu exista notiunea; data_faptului_generator era cod mort."""
    prof, fac_iul = _d300mod.pull(conn_b1, _SCHEMA, Perioada(2026, luna=7))
    res_iul = calcul_d300(prof, Perioada(2026, luna=7), fac_iul)
    assert (res_iul.R.get("R9_1"), res_iul.R.get("R9_2")) == (1000, 210), \
        "avansul e exigibil in iulie (la emitere)"
    prof, fac_oct = _d300mod.pull(conn_b1, _SCHEMA, Perioada(2026, luna=10))
    res_oct = calcul_d300(prof, Perioada(2026, luna=10), fac_oct)
    # octombrie contine DOAR livrarea normala (2000/420), NU si avansul (altfel 3000/630).
    assert (res_oct.R.get("R9_1"), res_oct.R.get("R9_2")) == (2000, 420), \
        "avansul NU reapare in octombrie la faptul generator (dubla numarare)"


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_deducere_amanata_furnizor_la_incasare(conn_b1):
    """[sit.6] Deducere amanata furnizor la incasare (art.297 alin.2): primita de la furnizor cu
    furnizor_tva_incasare=true, firma proprie regim normal -> TVA NU se deduce la data facturii pe
    calea de emitere (NU intra in R22 in luna facturii, noiembrie); se deduce cand se PLATESTE
    (decembrie). RED pre-B1: nu exista _pull_furnizor_incasare -> factura era dedusa la data facturii."""
    prof, fac_nov = _d300mod.pull(conn_b1, _SCHEMA, Perioada(2026, luna=11))
    res_nov = calcul_d300(prof, Perioada(2026, luna=11), fac_nov)
    assert "R22_1" not in res_nov.R and "R22_2" not in res_nov.R, \
        "deducerea NU se face la data facturii (noiembrie)"
    prof, fac_dec = _d300mod.pull(conn_b1, _SCHEMA, Perioada(2026, luna=12))
    res_dec = calcul_d300(prof, Perioada(2026, luna=12), fac_dec)
    assert (res_dec.R.get("R22_1"), res_dec.R.get("R22_2")) == (2000, 420), \
        "deducerea devine exigibila la plata (decembrie)"


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_persistenta_manual_paritate_preview_depunere(conn_b1):
    """[sit.7 / B2-B3] Persistenta + paritate d300_manual: un rand persistat in d300_manual e incarcat
    din DB de genereaza(manual=None) (apare in res.R), SI XML-ul cu manual=None (din DB) == XML-ul cu
    manual=param (acelasi rand) -> paritate preview<->depunere. RED pre-B2/B3: nu exista tabelul
    d300_manual/incarcarea din DB -> calea de depunere (manual=None) producea alt XML decat preview-ul.
    Randul se curata la final (idempotent)."""
    an, luna = 2026, 4   # aprilie: nicio factura in fixtura -> decontul e pur randul manual
    try:
        with conn_b1.cursor() as cur:
            cur.execute("INSERT INTO %s.d300_manual (an, luna, rand, baza, tva, descriere) "
                        "VALUES (%%s,%%s,'R16',1000,210,'proba paritate') "
                        "ON CONFLICT (an, luna, rand) DO UPDATE SET baza=EXCLUDED.baza, tva=EXCLUDED.tva"
                        % _SCHEMA, (an, luna))
        per = Perioada(an, luna=luna)
        xml_db, res_db = _d300mod.genereaza(conn_b1, _SCHEMA, per, manual=None)
        assert (res_db.R.get("R16_1"), res_db.R.get("R16_2")) == (1000, 210), \
            "randul manual persistat e incarcat din DB pe calea de depunere (manual=None)"
        xml_par, _res_par = _d300mod.genereaza(conn_b1, _SCHEMA, per, manual={"R16_1": 1000, "R16_2": 210})
        assert xml_db == xml_par, "paritate preview<->depunere: XML din DB == XML din param"
    finally:
        with conn_b1.cursor() as cur:
            cur.execute("DELETE FROM %s.d300_manual WHERE an=%%s AND luna=%%s AND rand='R16'"
                        % _SCHEMA, (an, luna))
