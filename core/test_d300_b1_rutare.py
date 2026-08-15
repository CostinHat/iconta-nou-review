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
#  F125: RECLASIFICARE bun->serviciu pe SURSA UNICA partajata cu D390 (MUTA, nu adauga).
#  Cheia (directie, tara, cod) = din PREFIXUL CUI via d390._clasifica_partener, identic cu D390.
#  Reclasificari cheiate 3-tuple (o luna) - forma acceptata de calcul_d300.
# ============================================================
_CUI_DE = "DE123456789"   # partener IC (prefix UE) -> _clasifica_partener -> ("ic","DE","123456789")
_KEY_DE = ("DE", "123456789")   # (tara, cod) fara prefix, ca in D390


def test_reclas_emisa_serviciu_P_muta_R1_la_R3():
    """[F125 mut, nu adauga] Livrare IC catre UE reclasificata SERVICIU (P) in D390 -> rd.3
    (R3_1 baza col.1, 0% fara TVA) + sub-rand rd.3.1 (R3_1_1 'din care servicii IC'). R1_1 ABSENT
    (mutat, nu adaugat). RED fara F125: emisa UE 0% cadea mereu in R1 (bunuri), fara citirea sursei D390."""
    f = {"directie": "emisa", "tert_tara": "DE", "cui": _CUI_DE, "linii": [(1, 8000, 0)]}
    recl = {("emisa",) + _KEY_DE: "P"}
    res = calcul_d300(_prof(), Perioada(2026, luna=8), [f], reclasificari=recl)
    assert res.R.get("R3_1") == 8000, "prestare serviciu IC -> rd.3 (R3_1)"
    assert res.R.get("R3_1_1") == 8000, "sub-rand rd.3.1 (din care servicii IC)"
    assert "R1_1" not in res.R, "MUTAT nu adaugat: livrarea de bunuri (rd.1) NU mai apare"
    # rd.3 e 0% -> nu adauga TVA colectata (R17_2 nu creste din serviciu emis)
    assert "R3_2" not in res.R, "rd.3 e 0% (col.2 nu exista)"


def test_reclas_primita_serviciu_S_muta_R5R18_la_R7R20_oglinda():
    """[F125 mut, nu adauga] Achizitie IC din UE reclasificata SERVICIU (S) in D390 -> rd.7 colectat
    (R7_1/R7_2 + R7_1_1/R7_1_2) + OGLINDA rd.20 deductibil (R20_1/R20_2 + R20_1_1/R20_1_2), net zero
    (DUK V_13-V_16: R20_x==R7_x). R5_1/R18_1 ABSENTE (mutat, nu adaugat). Autolichidare cota interna 21%."""
    f = {"directie": "primita", "tert_tara": "DE", "cui": _CUI_DE, "linii": [(1, 15000, 0)]}
    recl = {("primita",) + _KEY_DE: "S"}
    res = calcul_d300(_prof(), Perioada(2026, luna=6), [f], reclasificari=recl)
    assert (res.R.get("R7_1"), res.R.get("R7_2")) == (15000, 3150), "rd.7 colectat (15000 x 21%)"
    assert (res.R.get("R7_1_1"), res.R.get("R7_1_2")) == (15000, 3150), "sub-rand rd.7.1 servicii IC"
    assert (res.R.get("R20_1"), res.R.get("R20_2")) == (15000, 3150), "oglinda rd.20 deductibil"
    assert (res.R.get("R20_1_1"), res.R.get("R20_1_2")) == (15000, 3150), "sub-rand rd.20.1 (oglinda rd.7.1)"
    assert res.R["R20_1"] == res.R["R7_1"] and res.R["R20_2"] == res.R["R7_2"], "DUK V_13/V_14 R20==R7"
    assert res.R["R20_1_1"] == res.R["R7_1_1"] and res.R["R20_1_2"] == res.R["R7_1_2"], "DUK V_15/V_16 R20.1==R7.1"
    assert "R5_1" not in res.R and "R18_1" not in res.R, "MUTAT nu adaugat: rd.5/rd.18 (bunuri) absente"
    assert res.tva_de_plata == 0 and res.tva_de_recuperat == 0, "net zero (colectat==deductibil)"


def test_reclas_tip_nelegal_pt_directie_ridica():
    """[F125 gard tranzitie] Reclasificare cu tip NELEGAL pentru directie (S = achizitie, pus pe EMISA)
    -> ValueError vizibil (refoloseste d390._reclasificare_tip). NU revine tacit la default (misclasificare)."""
    f = {"directie": "emisa", "tert_tara": "DE", "cui": _CUI_DE, "linii": [(1, 8000, 0)]}
    recl = {("emisa",) + _KEY_DE: "S"}   # S nu e permis pe emisa (permise L/T/P/R)
    with pytest.raises(ValueError) as ei:
        calcul_d300(_prof(), Perioada(2026, luna=8), [f], reclasificari=recl)
    assert "nepermis" in str(ei.value).lower() or "S" in str(ei.value), "tip nelegal pt directie -> eroare"


def test_reclas_antidubla_serviciu_S_plus_manual_R7_ridica():
    """[F125 anti-dubla] rd.7 DERIVAT automat (serviciu S reclasificat) + acelasi rand prin `manual`
    (R7_1) -> ValueError, nu insumare tacita. Ca la rd.1/rd.5."""
    f = {"directie": "primita", "tert_tara": "DE", "cui": _CUI_DE, "linii": [(1, 15000, 0)]}
    recl = {("primita",) + _KEY_DE: "S"}
    with pytest.raises(ValueError) as ei:
        calcul_d300(_prof(), Perioada(2026, luna=6), [f], {"R7_1": 15000}, reclasificari=recl)
    assert "dubla numarare" in str(ei.value), "mesaj vizibil de dubla numarare pe rd.7"


def test_reclas_absenta_pastreaza_L_A_actual():
    """[F125 fara regresie] Cu CUI IC prezent DAR fara reclasificare -> comportamentul L/A actual:
    emisa UE -> rd.1 (bunuri); primita UE -> rd.5+rd.18. Adaugarea CUI-ului NU schimba defaultul."""
    fe = {"directie": "emisa", "tert_tara": "DE", "cui": _CUI_DE, "linii": [(1, 8000, 0)]}
    res_e = calcul_d300(_prof(), Perioada(2026, luna=8), [fe])
    assert res_e.R.get("R1_1") == 8000 and "R3_1" not in res_e.R, "fara reclasificare -> rd.1 (bunuri)"
    fp = {"directie": "primita", "tert_tara": "DE", "cui": _CUI_DE, "linii": [(1, 15000, 0)]}
    res_p = calcul_d300(_prof(), Perioada(2026, luna=6), [fp])
    assert (res_p.R.get("R5_1"), res_p.R.get("R5_2")) == (15000, 3150), "fara reclasificare -> rd.5 (bunuri)"
    assert "R7_1" not in res_p.R, "fara reclasificare -> NU rd.7 (servicii)"


def test_reclas_T_emisa_ramane_bunuri_dar_semnaleaza():
    """[F125 T/R limita declarata] Reclasificare T (triangulatie, emisa) NU e axa bun-serviciu: ramane
    rutata numeric ca bunuri (rd.1) DAR se semnaleaza explicit (limita declarata, nu tacere)."""
    f = {"directie": "emisa", "tert_tara": "DE", "cui": _CUI_DE, "linii": [(1, 8000, 0)]}
    recl = {("emisa",) + _KEY_DE: "T"}
    res = calcul_d300(_prof(), Perioada(2026, luna=8), [f], reclasificari=recl)
    assert res.R.get("R1_1") == 8000, "T ramane rutat ca bunuri (rd.1)"
    assert "R3_1" not in res.R, "T NU merge la rd.3 (nu e serviciu)"
    assert any("triangula" in a.lower() or "T/R" in a for a in res.avertismente), \
        "T/R se semnaleaza explicit (limita declarata)"


def test_reclas_cheie_per_luna_5tuple():
    """[F125 trimestru] Cheie 5-tuple {(an,luna,directie,tara,cod):tip} potriveste factura pe LUNA ei
    de exigibilitate (an_exig/luna_exig). Acelasi partener, luni diferite, tipuri diferite."""
    f_iun = {"directie": "emisa", "tert_tara": "DE", "cui": _CUI_DE, "an_exig": 2026, "luna_exig": 6,
             "linii": [(1, 8000, 0)]}
    recl = {(2026, 6, "emisa") + _KEY_DE: "P"}
    res = calcul_d300(_prof(), Perioada(2026, luna=6), [f_iun], reclasificari=recl)
    assert res.R.get("R3_1") == 8000, "5-tuple potrivit pe luna 6 -> serviciu rd.3"
    # aceeasi factura in alta luna (fara override pe acea luna) -> ramane bunuri rd.1
    f_iul = dict(f_iun, luna_exig=7)
    res2 = calcul_d300(_prof(), Perioada(2026, luna=7), [f_iul], reclasificari=recl)
    assert res2.R.get("R1_1") == 8000 and "R3_1" not in res2.R, "luna fara override -> bunuri rd.1"


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


# ============================================================
#  RECONCILIERE CROSS-DECLARATIE D300<->D390 (15.08.2026): SURSA UNICA d390_reclasificare.
#  Costin: "o singura sursa cu gard care face imposibila reaparitia randurilor auto peste cele
#  reclasificate" + "cele doua declaratii trebuie oricum sa se reconcilieze intre ele". Pe ACEEASI
#  perioada + aceeasi reclasificare (DB reala, schema efemera): baza D300 (R3_1/R7_1) == baza D390
#  (bazaP/bazaS), operatiunea NU reapare pe calea auto (R1/R5+R18 in D300; L/A in D390). O singura
#  scriere in d390_reclasificare muta AMBELE declaratii -> nu exista a doua sursa care ar putea diverge.
#  D300 citeste via _incarca_reclasificari -> d390.pull_reclasificari; D390 via calculeaza ->
#  pull_reclasificari (ACELASI tabel). Aserttile ASCII (regula diacritice).
# ============================================================
from core import d390 as _d390
_SCHEMA_REC = "test_d300_recon_d390"
_AN_REC, _LUNA_REC = 2026, 8
_FR_COD = "40303265045"   # emisa servicii -> P (FR40303265045, checksum verificat DUK)
_DE_COD = "136695976"     # primita servicii -> S (DE136695976, checksum verificat DUK)


@pytest.fixture(scope="module")
def conn_recon():
    """Firma regim normal, decont lunar. Doua operatiuni IC de SERVICII (0%), aceeasi luna (august):
      SRVP  emisa   FR40303265045, net 4000  -> reclasificabila P (prestare servicii IC)   -> rd.3
      SRVS  primita DE136695976, net 9000    -> reclasificabila S (achizitie servicii IC)  -> rd.7+rd.20
    Reclasificarea se scrie/sterge PER TEST in d390_reclasificare (sursa unica). ROLLBACK + DROP la teardown."""
    _db.init_pool()
    with _db.get_conn() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA_REC)
                cur.execute(_tp.parametrizeaza_template(
                    open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA_REC))
                cur.execute("SET search_path TO %s, public" % _SCHEMA_REC)
                cur.execute(
                    "INSERT INTO firma_profil (id, nume, cui, adresa, oras, judet, caen, banca, iban, "
                    "regim_fiscal, platitor_tva, tip_decont, declarant_nume, declarant_prenume, declarant_functie) "
                    "VALUES (1,'RECON SRL','14399840','Str Test 1','Bucuresti','B','4711','BCR','RO49AAAA1B31007593840000',"
                    "'real',true,'L','Pop','Ion','administrator')")
                cur.execute("INSERT INTO facturi (numar, data_emitere, directie, total, tva, tert_tara, tert_cui, status) "
                            "VALUES ('SRVP','2026-08-05','emisa',4000,0,'FR','FR%s','emisa') RETURNING id" % _FR_COD)
                sp = cur.fetchone()[0]
                cur.execute("INSERT INTO factura_linii (factura_id, descriere, cantitate, pret_unitar, cota_tva) "
                            "VALUES (%s,'prestare servicii IC',1,4000,0)", (sp,))
                cur.execute("INSERT INTO facturi (numar, data_emitere, directie, total, tva, tert_tara, tert_cui, status) "
                            "VALUES ('SRVS','2026-08-07','primita',9000,0,'DE','DE%s','emisa') RETURNING id" % _DE_COD)
                ss = cur.fetchone()[0]
                cur.execute("INSERT INTO factura_linii (factura_id, descriere, cantitate, pret_unitar, cota_tva) "
                            "VALUES (%s,'achizitie servicii IC',1,9000,0)", (ss,))
            yield conn
        finally:
            conn.rollback()
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA_REC)
            conn.commit()


def _set_recl(conn, directie, tara, cod, tip):
    """Scrie override-ul de tip in SURSA UNICA d390_reclasificare (fara commit - rollback-safe)."""
    with conn.cursor() as cur:
        cur.execute("INSERT INTO %s.d390_reclasificare (an,luna,directie,tara,cod,tip) "
                    "VALUES (%%s,%%s,%%s,%%s,%%s,%%s) "
                    "ON CONFLICT (an,luna,directie,tara,cod) DO UPDATE SET tip=EXCLUDED.tip"
                    % _SCHEMA_REC, (_AN_REC, _LUNA_REC, directie, tara, cod, tip))


def _clear_recl(conn):
    with conn.cursor() as cur:
        cur.execute("DELETE FROM %s.d390_reclasificare WHERE an=%%s AND luna=%%s"
                    % _SCHEMA_REC, (_AN_REC, _LUNA_REC))


def _d300_res(conn):
    """D300 pe calea REALA: pull + _incarca_reclasificari (SURSA UNICA) + calcul_d300."""
    per = Perioada(_AN_REC, luna=_LUNA_REC)
    prof, facturi = _d300mod.pull(conn, _SCHEMA_REC, per)
    recl = _d300mod._incarca_reclasificari(conn, _SCHEMA_REC, prof, per)
    return calcul_d300(prof, per, facturi, reclasificari=recl)


def _d390_res(conn):
    """D390 pe calea REALA: calculeaza (incarca singur reclasificarile din ACELASI tabel)."""
    return _d390.calculeaza(conn, _SCHEMA_REC, _AN_REC, _LUNA_REC)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_recon_P_emisa_serviciu_d300_R3_egal_d390_bazaP(conn_recon):
    """[RECONCILIERE P] Dupa reclasificarea operatiunii IC emise ca P in d390_reclasificare: baza D300
    rd.3 (R3_1) == baza P din d390.calcul_d390 (ACEEASI operatiune, ambele declaratii), SI operatiunea
    NU mai apare in D300 rd.1 (R1_1) si NU e L in D390. Reaparitia auto peste reclasificat = imposibila."""
    _set_recl(conn_recon, "emisa", "FR", _FR_COD, "P")
    try:
        r3 = _d300_res(conn_recon)
        r9 = _d390_res(conn_recon)
        assert r3.R.get("R3_1") == 4000, "D300 rd.3 (R3_1) baza prestare servicii IC"
        assert r3.R.get("R3_1_1") == 4000, "D300 sub-rand rd.3.1 (din care servicii IC)"
        assert r9.rezumat["P"] == 4000, "D390 bazaP prestare servicii IC (aceeasi operatiune)"
        assert r3.R["R3_1"] == r9.rezumat["P"], "RECONCILIERE: D300 R3_1 == D390 bazaP"
        assert "R1_1" not in r3.R, "reaparitie auto IMPOSIBILA: R1_1 (bunuri) absent in D300 (mutat, nu adaugat)"
        assert r9.rezumat["L"] == 0, "operatiunea NU e L (bunuri) in D390 (mutata la P)"
    finally:
        _clear_recl(conn_recon)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_recon_S_primita_serviciu_d300_R7_egal_d390_bazaS(conn_recon):
    """[RECONCILIERE S] Dupa reclasificarea operatiunii IC primite ca S in d390_reclasificare: baza D300
    rd.7 (R7_1) == baza S din d390.calcul_d390, SI absenta din rd.5/rd.18 (R5_1/R18_1) si din A in D390.
    Autolichidare la cota interna 21% (R7_2), oglinda rd.20 net zero."""
    _set_recl(conn_recon, "primita", "DE", _DE_COD, "S")
    try:
        r3 = _d300_res(conn_recon)
        r9 = _d390_res(conn_recon)
        assert (r3.R.get("R7_1"), r3.R.get("R7_2")) == (9000, 1890), "D300 rd.7 colectat (9000 x 21%)"
        assert (r3.R.get("R20_1"), r3.R.get("R20_2")) == (9000, 1890), "D300 oglinda rd.20 deductibil (net zero)"
        assert r9.rezumat["S"] == 9000, "D390 bazaS achizitie servicii IC (aceeasi operatiune)"
        assert r3.R["R7_1"] == r9.rezumat["S"], "RECONCILIERE: D300 R7_1 == D390 bazaS"
        assert "R5_1" not in r3.R and "R18_1" not in r3.R, "reaparitie auto IMPOSIBILA: rd.5/rd.18 absente (mutat)"
        assert r9.rezumat["A"] == 0, "operatiunea NU e A (bunuri) in D390 (mutata la S)"
    finally:
        _clear_recl(conn_recon)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_recon_sursa_unica_o_scriere_muta_ambele(conn_recon):
    """[SURSA UNICA dovedita] O singura scriere in d390_reclasificare schimba AMBELE declaratii - nu
    exista o a doua sursa care ar putea diverge. FARA rand -> L/A (bunuri) in AMBELE (D300 R1/R5+R18,
    D390 L/A). CU rand -> P/S in AMBELE (D300 R3/R7+R20, D390 P/S). D300 si D390 citesc din acelasi tabel."""
    _clear_recl(conn_recon)
    r3 = _d300_res(conn_recon)
    r9 = _d390_res(conn_recon)
    assert r3.R.get("R1_1") == 4000, "fara reclasificare -> D300 emisa = rd.1 (bunuri)"
    assert (r3.R.get("R5_1"), r3.R.get("R5_2")) == (9000, 1890), "fara reclasificare -> D300 primita = rd.5 (bunuri)"
    assert "R3_1" not in r3.R and "R7_1" not in r3.R, "fara reclasificare -> NU servicii (rd.3/rd.7) in D300"
    assert r9.rezumat["L"] == 4000 and r9.rezumat["A"] == 9000, "fara reclasificare -> L/A (bunuri) in D390"
    assert r9.rezumat["P"] == 0 and r9.rezumat["S"] == 0, "fara reclasificare -> NU P/S in D390"
    # o singura scriere per directie in ACELASI tabel -> P/S in AMBELE declaratii
    _set_recl(conn_recon, "emisa", "FR", _FR_COD, "P")
    _set_recl(conn_recon, "primita", "DE", _DE_COD, "S")
    try:
        r3 = _d300_res(conn_recon)
        r9 = _d390_res(conn_recon)
        assert r3.R.get("R3_1") == 4000 and r3.R.get("R7_1") == 9000, "cu reclasificare -> D300 citeste sursa unica (rd.3/rd.7)"
        assert r9.rezumat["P"] == 4000 and r9.rezumat["S"] == 9000, "cu reclasificare -> D390 citeste ACEEASI sursa (P/S)"
        assert "R1_1" not in r3.R and "R5_1" not in r3.R, "MUTAT nu adaugat in D300 (rd.1/rd.5 dispar)"
        assert r9.rezumat["L"] == 0 and r9.rezumat["A"] == 0, "MUTAT nu adaugat in D390 (L/A dispar)"
    finally:
        _clear_recl(conn_recon)
