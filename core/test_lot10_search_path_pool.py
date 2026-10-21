# -*- coding: utf-8 -*-
"""[lotul 10, prins de e2e 430] GARDA: un test nu lasă `search_path` pe o conexiune din pool.

Defectul: `uc_tenants.dividende_impartire` / `nota_asociati` citeau asociații pe o conexiune `public` cu SQL necalificat -> 500 pe ecran
(„relation asociati does not exist”). Testele lui treceau: fixtura făcea `SET search_path TO <schema>` (de SESIUNE) pe o conexiune din
pool, care rămânea așa și era refolosită „din întâmplare” de use-case. `db.get_conn` resetează `search_path` numai când primește `schema`
(codul aplicației îl folosește așa — verificat: niciun `SET search_path` de sesiune pe o conexiune fără schemă); deci scurgerea e a
TESTELOR, și ascunde exact defectele de schemă. Regula: în test, `SET LOCAL search_path` (pe tranzacție), sau `db.get_conn(schema)`.
CLICHET: fișierele de dinaintea lotului 10 care o fac de sesiune (BAZA) rămân, ca limită declarată (GARZI); niciun fișier NOU.
MUTAȚIE: `SET LOCAL` -> `SET` într-un test al lotului 10 -> pică.
"""
import glob
import io
import re

_TIPAR = re.compile(r'execute\(\s*f?["\']SET search_path TO')

#: fișierele de test care, la 20.10.2026, fac `SET search_path` de sesiune (moștenite; se scot de aici pe măsură ce se repară)
BAZA = {
    "core/test_274b_categorii_tva.py",
    "core/test_281_amortizare_restanta.py",
    "core/test_288_povestea_lunii.py",
    "core/test_295_rezumat_d100.py",
    "core/test_380_381_d406_surse.py",
    "core/test_398_400_nir.py",
    "core/test_401_403_borderou.py",
    "core/test_404_407_lipsa_avans.py",
    "core/test_405_plata_nir_avans.py",
    "core/test_406_casa_negativa.py",
    "core/test_411_net_cu_cm.py",
    "core/test_412_cim_salariat.py",
    "core/test_417_storno_trimitere.py",
    "core/test_418_import_efactura.py",
    "core/test_419_storno_retur.py",
    "core/test_a12b_destinatie_linie.py",
    "core/test_a1_valuta_pana_in_declaratie.py",
    "core/test_a2_tvai_ic.py",
    "core/test_a3_a4_lant.py",
    "core/test_a6_d205_cota_distribuire.py",
    "core/test_a8_micro_baza.py",
    "core/test_a8_profit_cumulat.py",
    "core/test_achizitii_factura.py",
    "core/test_amortizare_ecran_metoda.py",
    "core/test_aplicabilitate_o_singura_sursa.py",
    "core/test_audit_campuri_oficiale.py",
    "core/test_b1_apartenenta_coada.py",
    "core/test_bilant_an_precedent.py",
    "core/test_bilant_f30.py",
    "core/test_bilant_regcom_poarta.py",
    "core/test_c1_numerotare.py",
    "core/test_c48_d406.py",
    "core/test_c5_extras_idempotent.py",
    "core/test_c61_adresa_client_ro.py",
    "core/test_c63_proforma_transformata.py",
    "core/test_c7_periodicitate_trimestriala.py",
    "core/test_capital_social.py",
    "core/test_casa_facturi_avans.py",
    "core/test_ciorne_proprii.py",
    "core/test_comportament_chei_suspendare.py",
    "core/test_cont_venit_linie.py",
    "core/test_contare_automata.py",
    "core/test_control_incrucisat_wiring.py",
    "core/test_control_reconciliere_vizibila.py",
    "core/test_d100.py",
    "core/test_d100_profit_baza.py",
    "core/test_d100_profit_cumulat.py",
    "core/test_d100_reconciliere.py",
    "core/test_d101.py",
    "core/test_d101_imca_ca_precedent.py",
    "core/test_d101_impozit_nededus.py",
    "core/test_d101_reconciliere.py",
    "core/test_d112_asiguratd_zerobase.py",
    "core/test_d112_cadou.py",
    "core/test_d112_deducere_suplimentara.py",
    "core/test_d112_reconciliere.py",
    "core/test_d112_ziua_diminuare.py",
    "core/test_d205.py",
    "core/test_d205_cesiune.py",
    "core/test_d205_cota_2025.py",
    "core/test_d205_divid_platit.py",
    "core/test_d205_imp_manual.py",
    "core/test_d205_reconciliere.py",
    "core/test_d300.py",
    "core/test_d300_b1_rutare.py",
    "core/test_d300_d394_paritate.py",
    "core/test_d300_d394_trimestrial.py",
    "core/test_d300_forfait_agricol.py",
    "core/test_d300_rapoarte_z.py",
    "core/test_d300_reconciliere.py",
    "core/test_d301_reconciliere.py",
    "core/test_d301_zero_ruptura.py",
    "core/test_d390_d301_acoperire.py",
    "core/test_d390_nota1.py",
    "core/test_d390_reconciliere.py",
    "core/test_d390_ziua15.py",
    "core/test_d394.py",
    "core/test_d394_i2.py",
    "core/test_d394_nrfact_multicota.py",
    "core/test_d394_op2_rapoarte_z.py",
    "core/test_d394_pull_ti_fara_linii.py",
    "core/test_d394_reconciliere.py",
    "core/test_d406.py",
    "core/test_d406_accounttype_wired.py",
    "core/test_d406_active_duk.py",
    "core/test_d406_cnp_tert.py",
    "core/test_d406_coercitie_t3.py",
    "core/test_d406_cui_checksum.py",
    "core/test_d406_master_pf.py",
    "core/test_d406_reconciliere.py",
    "core/test_d406_reg_number_header.py",
    "core/test_d406_supplierid.py",
    "core/test_d406_taxcode_nota.py",
    "core/test_decizii_0710.py",
    "core/test_deducere_generalizare.py",
    "core/test_document_fara_administrator.py",
    "core/test_drepturi_rol.py",
    "core/test_e1_contare_primita_mixt.py",
    "core/test_eticheta_nota.py",
    "core/test_eu_parola.py",
    "core/test_exces_vacanta_d112.py",
    "core/test_export_din_bon.py",
    "core/test_factura_bon_fiscal.py",
    "core/test_flux_factura_f1_c.py",
    "core/test_flux_factura_f1_d.py",
    "core/test_granite_cota.py",
    "core/test_inchidere_an.py",
    "core/test_inchidere_luna.py",
    "core/test_izolare_api_key.py",
    "core/test_izolare_incrucisata.py",
    "core/test_izolare_structurala.py",
    "core/test_limita_text_anaf.py",
    "core/test_lot0610_p1.py",
    "core/test_lot0610_p3.py",
    "core/test_lot0710_p2.py",
    "core/test_neplatitor_tva_emitere.py",
    "core/test_nir_legare_inversa.py",
    "core/test_p4_fault_injection.py",
    "core/test_perechi_citesc_generatorul.py",
    "core/test_perioada.py",
    "core/test_perioada_indisponibila.py",
    "core/test_pfa_note_interne.py",
    "core/test_plan_conturi_omfp.py",
    "core/test_poarta_inchidere.py",
    "core/test_portal_bon.py",
    "core/test_pull_declaratii.py",
    "core/test_r193_model_fara_conexiune.py",
    "core/test_reconciliere_d100_wiring.py",
    "core/test_reconciliere_factura_stoc.py",
    "core/test_reguli_fond.py",
    "core/test_retest_0810_s6.py",
    "core/test_ruptura_seed_control.py",
    "core/test_rute_fiscale_lot3b.py",
    "core/test_rute_stoc_pana_in_declaratie.py",
    "core/test_s1_elemente_salariale.py",
    "core/test_salariu_in_timp.py",
    "core/test_salariu_proratare.py",
    "core/test_salariu_scrieri.py",
    "core/test_scrieri_pana_in_declaratie.py",
    "core/test_sesiune_fara_pierdere.py",
    "core/test_smoke_duk.py",
    "core/test_testare_asistent.py",
    "core/test_tichet_cresa.py",
    "core/test_tichet_cultural.py",
    "core/test_tichete_pontaj.py",
    "core/test_validare_note.py",
    "core/test_verde_peste_necunoscut.py",
    "core/test_zero_base_declaratii.py",
}


def _cu_scurgere():
    # garda însăși conține tiparul (calibrarea de mai jos), deci nu se scanează
    return {f for f in glob.glob("core/test_*.py") if f != "core/test_lot10_search_path_pool.py"
            and _TIPAR.search(io.open(f, encoding="utf-8").read())}


def test_niciun_test_nou_nu_lasa_search_path_in_pool():
    noi = sorted(_cu_scurgere() - BAZA)
    assert not noi, "SET search_path de sesiune într-un test nou (folosește SET LOCAL sau db.get_conn(schema)): %s" % noi


def test_baza_nu_tine_fisiere_reparate():
    """Clichetul coboară: un fișier reparat iese din BAZA (altfel ar putea reveni tăcut)."""
    reparate = sorted(BAZA - _cu_scurgere())
    assert not reparate, "scoate din BAZA fișierele care nu mai au scurgerea: %s" % reparate


def test_tiparul_vede_forma_veche():
    assert _TIPAR.search('cur.execute("SET search_path TO %s, public" % SCH)')
    assert not _TIPAR.search('cur.execute("SET LOCAL search_path TO %s, public" % SCH)')
