# -*- coding: utf-8 -*-
"""scripts/curata_coduri_ghid.py — scoate denumirile din CODUL APLICAȚIEI din textele publice ale ghidurilor (comanda Costin 13.10.2026,
pct.2b, verbatim în DECIZII): „Scoate din textele publice denumirile din cod (de ex. nir_gv, coeficient_k) și înlocuiește-le cu numele
funcției din aplicație, cum îl vede contabilul.”

CE SCHIMBĂ, în `ghid/*.md` (titlu, descriere, corp):
  · numele de funcții, câmpuri, tabele, constante, fișiere `.py`, rute, teste ale aplicației -> numele din ecran (`NOMENCLATOR_CODURI_GHID`,
    `NOMENCLATOR_CODURI_SCURTE`); un apel `nume(argumente)` -> numele funcției, fără argumente;
  · codurile funcționalităților (F027) -> numele lor din `FUNCTIONALITATI.csv`; „dosarul de cercetare Fnnn” (document intern) dispare;
  · fișierele locale cu documente oficiale (`cod_fiscal_227_2015_consolidat.txt`, L…) -> numele actului (`NOMENCLATOR_DOCUMENTE_OFICIALE`);
  · expresiile de cod (`regim == "micro"`, `deductibil: False`, `pull()`) -> ce înseamnă pentru contabil (`NOMENCLATOR_EXPRESII`);
    trimiterile la registrul intern al proiectului („neconformitate deschisă (R95)”) -> „limitare cunoscută a aplicației” (`FRAZE_INTERNE`);
  · în blocurile de temei: un citat a cărui sursă e APLICAȚIA (codul ei, registrul intern) nu e temei — se scoate; citatele din acte rămân.
CE NU SCHIMBĂ: denumirile din STRUCTURILE OFICIALE ANAF (`NOMENCLATOR_OFICIALE`: `d_rec`, `cod_oblig`, `tip_venit1` …, elementele SAF-T) —
nu sunt cod al aplicației, așa le scrie ANAF. Un ghid schimbat primește `modified:` = data rulării (data ultimei actualizări, pct.2c).
Gard: `core/test_ghid_fara_coduri.py`.

Uz: python scripts/curata_coduri_ghid.py            -> câte ghiduri s-ar schimba (nu scrie)
    python scripts/curata_coduri_ghid.py --scrie    -> rescrie ghidurile
"""
import datetime
import glob
import os
import re
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: identificator din codul aplicației -> numele pe care îl vede contabilul (funcția, ecranul, câmpul)
NOMENCLATOR_CODURI_GHID = {
    # ── stocuri ──
    "nir_gv": "NIR global-valoric (Stocuri)", "coeficient_k": "coeficientul K (Stocuri, descărcarea global-valorică)",
    "descarcare_gv": "descărcarea global-valorică (Stocuri)", "descarca_luna": "descărcarea lunii (Stocuri)",
    "nota_ajustare_stoc": "nota de ajustare a stocurilor (Operațiuni speciale)", "nota_perisabilitati": "nota de perisabilități (Stocuri)",
    "fisa_magazie": "fișa de magazie (Stocuri)", "valoare_iesire": "valoarea ieșirii (fișa de magazie)", "cmp_curent": "costul mediu ponderat",
    "adauga_nir": "adăugarea NIR-ului (Stocuri)", "intrare_din_factura": "intrarea în stoc din factură (Stocuri)", "miscari_stoc": "mișcările de stoc",
    "rc_707": "rulajul creditor 707", "tva_vanzari": "TVA-ul vânzărilor", "si_378": "soldul inițial 378", "rc_378": "rulajul creditor 378",
    "si_371": "soldul inițial 371", "rd_371": "rulajul debitor 371", "si_4428": "soldul inițial 4428", "rc_4428": "rulajul creditor 4428",
    "tva_stoc": "TVA-ul din stoc", "baza_stoc": "baza stocului", "cont_stoc": "contul de stoc", "cont_transport": "contul de transport",
    "cont_taxe": "contul de taxe", "cota_tva_implicita": "cota de TVA", "coef_348": "coeficientul diferențelor de preț (348)",
    "facturi_marfa": "facturile de marfă", "nota_productie_in_curs": "nota producției în curs (Producție)",
    "nota_obtinere": "nota de obținere a produselor finite (Producție)", "nota_plus": "nota plusurilor de inventar (Inventariere)",
    "nota_minus": "nota minusurilor de inventar (Inventariere)", "registru_inventar": "registrul-inventar (Registre)",
    "valoare_intrari": "valoarea intrărilor", "procent_limita": "procentul de limită",
    # ── casă, bancă, avansuri ──
    "verifica_plafon": "verificarea plafonului de numerar (Casă)", "registru_casa": "registrul de casă (Casă)",
    "casa_operatiuni": "operațiunile de casă (Casă)", "sold_final": "soldul final al registrului de casă", "chitanta_emite": "emiterea chitanței (Casă)",
    "chitanta_stinge": "stingerea chitanței primite (Portal)", "pdf_chitanta": "chitanța tipărită (Casă)", "suma_in_litere": "suma în litere",
    "urmatorul_numar_chitanta": "numărul următor al chitanței", "regula_cont_casa": "regula de contare a casei (Casă)",
    "ridicare_banca": "ridicare de numerar din bancă (Casă)", "depunere_banca": "depunere de numerar la bancă (Casă)",
    "incasare_client": "încasare de la client (Casă)", "plata_furnizor": "plată către furnizor (Casă)",
    "avans_decontare": "avans spre decontare (Casă)", "avans_acordare": "acordarea avansului de trezorerie",
    "avans_restituire": "restituirea avansului de trezorerie", "avans_deconteaza": "decontarea avansului de trezorerie",
    "avans_sold": "soldul avansului de trezorerie", "nota_decont": "nota decontului de avans", "rest_de_restituit": "suma de restituit",
    "plafon_avans_decontare": "plafonul avansului spre decontare", "plafon_sold_casa": "plafonul soldului de casă",
    "casierie_id": "casieria", "punct_lucru": "punctul de lucru", "partener_tip": "tipul partenerului",
    "import_banca": "importul extrasului bancar (Bancă)", "contabilizeaza_extras": "contarea extrasului (Bancă)",
    "potriveste_extras": "potrivirea extrasului cu facturile (Bancă)", "extras_linii": "liniile extrasului bancar",
    "inregistreaza_import": "evidența importurilor de extrase (Bancă)", "cont_banca": "contul bancar",
    "alte_incasari": "alte încasări", "rambursare_credit": "rambursare de credit", "aport_retragere": "aport sau retragere",
    "cheltuiala_deductibila": "cheltuială deductibilă", "cheltuiala_limitata": "cheltuială cu deductibilitate limitată",
    "cheltuiala_nedeductibila": "cheltuială nedeductibilă", "total_incasari": "totalul încasărilor", "total_plati": "totalul plăților",
    # ── facturi, e-Factura ──
    "creeaza_factura": "emiterea facturii (Facturi)", "sterge_factura": "ștergerea facturii (Facturi)", "lista_facturi": "lista facturilor (Facturi)",
    "facturi_partener": "facturile partenerului", "facturi_storno": "stornarea facturii (Facturi)", "factura_linii": "liniile facturii",
    "factura_id": "factura legată", "factura_ref": "referința facturii", "factura_emisa": "factura emisă", "facturi_ciorna": "nota ciornă a facturii",
    "facturi_deschise_detalii": "facturile deschise", "storno_din_id": "factura stornată (referința)", "data_emitere": "data emiterii",
    "genereaza_note": "contarea facturii", "genereaza_xml": "generarea XML-ului e-Factura", "upload_ubl": "transmiterea în RO e-Factura",
    "stare_mesaj": "starea transmiterii în RO e-Factura", "lista_mesaje": "lista mesajelor din SPV", "efactura_primite": "facturile primite din SPV",
    "efactura_send": "transmiterea în RO e-Factura", "efactura_trimitere": "evidența transmiterilor în RO e-Factura",
    "ultima_trimitere_per_factura": "ultima transmitere a facturii", "eroare_upload": "eroare la transmitere", "index_incarcare": "indexul de încărcare",
    "furnizor_tva_incasare": "furnizor cu TVA la încasare", "furnizor_incasare_freeze": "verificarea TVA la încasare a furnizorului",
    "tva_la_incasare": "TVA la încasare", "tva_din_incasare": "TVA-ul exigibil la încasare", "tva_exigibil_alocari": "TVA-ul exigibil pe cote",
    "suma_incasata": "suma încasată", "suma_fara_tva": "suma fără TVA", "cli_vat": "codul de TVA al clientului", "sup_vat": "codul de TVA al furnizorului",
    "deja_contata": "factură deja contată", "de_preluat": "de preluat",
    # ── TVA, operațiuni intracomunitare ──
    "achizitie_ic": "achiziție intracomunitară (Operațiuni)", "vanzare_ic": "vânzare intracomunitară (Operațiuni)", "operatiuni_ic": "operațiuni intracomunitare (Date firmă)",
    "valideaza_prestare_ic": "validarea prestării intracomunitare", "valideaza_lic": "validarea livrării intracomunitare",
    "cod_tva_client": "codul de TVA al clientului", "cod_valid_vies": "cod valid în VIES", "are_dovada_transport": "dovada transportului",
    "verifica_vies": "verificarea în VIES", "checksum_vies": "verificarea cifrei de control a codului de TVA", "desparte_cod_tva": "separarea prefixului de țară",
    "cod_tva": "codul de TVA", "tert_tara": "țara partenerului", "axa_ic": "marcajul de operațiune intracomunitară",
    "tva_taxare_inversa": "TVA prin taxare inversă", "note_taxare_inversa": "nota de taxare inversă", "se_aplica": "verificarea taxării inverse",
    "achizitii_d301": "achizițiile pentru D301", "d390_reclasificare": "reclasificările D390 (Declarații)", "pull_reclasificari": "reclasificările",
    "calcul_d300": "calculul D300 (Declarații)", "calcul_d394": "calculul D394 (Declarații)", "d300_manual": "rândurile D300 completate manual (Declarații)",
    "tip_decont": "periodicitatea TVA (Date firmă)", "platitor_tva": "plătitor de TVA (Date firmă)", "inreg_art317": "înregistrare art.317 (Date firmă)",
    "pro_rata": "pro-rata (Date firmă)", "potriveste_cota": "potrivirea cotei de TVA", "cota_ceruta": "validarea cotei de TVA",
    "restaurant_catering": "restaurant și catering (cota redusă)", "bauturi_alcoolice": "băuturi alcoolice", "bauturi_nc2202": "băuturi NC 2202",
    "locuinte_sociale": "locuințe sociale", "emite_tva": "TVA-ul facturilor emise", "per_trim": "trimestrial", "per_luni": "lunar",
    "clasifica_partener": "clasificarea partenerului", "taxare_inversa": "taxare inversă", "plafon_tva_incasare": "plafonul TVA la încasare",
    "tip_operatiune": "tipul operațiunii", "regularizare_avans": "regularizarea avansului",
    # ── declarații, conformare ──
    "erori_generare": "verificarea datelor înainte de generare (Declarații)", "build_xml": "generarea XML-ului declarației (Declarații)",
    "obligatii_datorate": "obligațiile datorate (Control fiscal)", "declaratii_datorate": "declarațiile datorate (Control fiscal)",
    "deriva_obligatii": "calculul obligațiilor (Declarații)", "declaratii_fapt": "verificarea faptelor (Control fiscal)",
    "d112_fapt": "verificarea D112 (Control fiscal)", "declaratii_depuse": "evidența declarațiilor depuse", "compara_d112": "comparația D112 (Control fiscal)",
    "verifica_d112": "verificarea D112 (Control fiscal)", "verifica_reconciliere": "reconcilierea D112 (Control fiscal)", "compara_d390": "comparația D390 (Control fiscal)",
    "control_fiscal_api": "Control fiscal", "termene_firma": "termenele firmei (Termene)", "periodicitate_firma": "periodicitatea declarațiilor (Date firmă)",
    "fereastra_d406": "perioada D406 (Declarații)", "xml_asset": "XML-ul activelor D406", "xml_assets": "XML-ul activelor D406",
    "xml_d406_anual_active": "D406 active (Declarații)", "xml_entry": "XML-ul D406 stocuri", "xml_physical_stock": "XML-ul D406 stocuri",
    "calcul_d101": "calculul D101 (Declarații)", "calcul_d205": "calculul D205 (Declarații)", "datoreaza_imca": "verificarea IMCA (Declarații)",
    "impozit_minim_cifra_afaceri": "impozitul minim pe cifra de afaceri", "fisa_d212": "fișa de calcul D212 (Declarații)",
    "calculeaza_d212": "calculul D212 (Declarații)", "calculeaza_cas": "calculul CAS (Declarații)", "calculeaza_cass": "calculul CASS (Declarații)",
    "venit_net": "venitul net", "venit_brut": "venitul brut", "cheltuieli_deductibile": "cheltuielile deductibile", "baza_impozit": "baza impozabilă",
    "optiune_cas": "opțiunea CAS", "optiune_cass": "opțiunea CASS", "mod_venit_net": "modul de determinare a venitului net",
    "dividende_curs": "dividendele în curs", "impozit_ponderat": "impozitul pe tranșe de plată", "select_asociati": "lista asociaților (Date firmă)",
    "select_clienti": "lista clienților", "venituri_trimestru": "veniturile trimestrului", "suma_ded": "deducerea",
    "regim_fiscal": "regimul fiscal (Date firmă)", "vector_fiscal_api": "vectorul fiscal (Date firmă)", "baza_contabila": "norma contabilă (Date firmă)",
    "are_operatiuni_afiliate": "operațiuni cu afiliați (Date firmă)", "are_salariati": "are salariați", "firma_profil": "Date firmă",
    "precompleteaza_din_anaf": "precompletarea din ANAF (Date firmă)", "cui_valid": "verificarea CUI-ului", "impozit_micro": "cota impozitului micro",
    "impozit_dividend": "cota impozitului pe dividende", "impozit_profit": "impozitul pe profit", "cifra_afaceri": "cifra de afaceri",
    "ca_an_precedent_eur": "cifra de afaceri a anului precedent (euro)", "tip_impozit": "tipul de impozit", "calc_baza": "calculul bazei",
    "plafoane_an": "plafoanele anului", "plafon_la": "plafonul la dată", "la_data": "data", "inceput_an": "începutul anului",
    "registru_evidenta_fiscala": "registrul de evidență fiscală (Registre)", "registru_pf": "registrul persoanelor fizice (Registre)",
    "registru_profit": "registrul de evidență fiscală — profit (Registre)", "venituri_pf": "venituri — persoane fizice",
    "perioade_blocate": "perioadele închise", "inchidere_luna": "închiderea lunii (Control fiscal)",
    # ── sponsorizări, creanțe, provizioane ──
    "credit_sponsorizare": "creditul fiscal pentru sponsorizări (Operațiuni speciale)", "plafon_credit": "plafonul creditului fiscal",
    "sponsorizari_efectuate": "sponsorizările efectuate", "redirectionabil_d177": "suma redirecționabilă prin D177", "nota_sponsorizare": "nota de sponsorizare",
    "beneficiar_in_registru": "beneficiar în registrul entităților", "plafon_m": "plafonul", "deductibilitate_creanta": "deductibilitatea creanței (Operațiuni speciale)",
    "zile_depasire_scadenta": "zilele de la scadență", "faliment_declarat": "faliment declarat", "nota_ajustare_creanta": "nota de ajustare a creanței",
    "nota_provizion": "nota de provizion (Operațiuni speciale)", "nota_garantie": "nota de garanție (Operațiuni speciale)",
    # ── mijloace fixe, leasing, valută, împrumuturi ──
    "amortizat_la_data": "amortizarea cumulată (Mijloace fixe)", "amortizare_luna": "amortizarea lunii (Mijloace fixe)",
    "amortizare_lunara": "amortizarea lunară", "amortizare_fiscala": "amortizarea fiscală", "dnf_luni": "durata normală de funcționare (Mijloace fixe)",
    "data_pif": "data punerii în funcțiune (Mijloace fixe)", "mijloace_fixe": "registrul mijloacelor fixe", "mijloc_fix_id": "mijlocul fix",
    "valoare_activ": "valoarea activului", "nota_vanzare_activ": "nota de vânzare a activului", "nota_casare_mf": "nota de casare (Mijloace fixe)",
    "nota_vanzare": "nota de vânzare (Operațiuni speciale)", "de_amortizat": "activele de amortizat", "prag_mf": "pragul mijloacelor fixe",
    "plafon_mijloc_fix": "plafonul mijloacelor fixe", "e_obiect_inventar": "încadrarea ca obiect de inventar", "durata_sub_1_an": "durata sub un an",
    "adauga_cu_reevaluare": "adăugarea mijlocului fix cu reevaluare", "urca_valoarea": "majorarea valorii (Mijloace fixe)",
    "reluare_lunara_investitii": "reluarea lunară a subvenției pentru investiții", "imobilizari_necorporale": "imobilizări necorporale",
    "nota_rata_operational": "nota ratei de leasing operațional (Operațiuni speciale)", "nota_primire_financiar": "nota de primire în leasing financiar",
    "nota_reziduala": "nota valorii reziduale (leasing)", "reevaluare_sold": "reevaluarea soldului în valută (Operațiuni speciale)",
    "reevaluare_valuta": "reevaluarea în valută (Operațiuni speciale)", "sold_valuta": "soldul în valută", "curs_evidenta": "cursul din evidență",
    "curs_bnr_sfarsit_luna": "cursul BNR de la sfârșitul lunii", "cont_sold": "contul", "valoare_valuta": "valoarea în valută", "val_valuta": "valoarea în valută",
    "curs_initial": "cursul inițial", "curs_final": "cursul final", "curs_factura": "cursul facturii", "curs_decontare": "cursul decontării",
    "nota_decontare": "nota de decontare în valută", "decontare_valuta": "decontare în valută (Operațiuni speciale)", "cont_tert": "contul terțului",
    "cont_credit": "contul creditor", "cont_ajustare": "contul de ajustare", "nota_imprumut_asociat": "nota împrumutului de la asociat (Operațiuni speciale)",
    "nota_primire": "nota de primire a creditului", "nota_plata": "nota de plată a ratei", "nota_restanta": "nota de reclasificare la restanță",
    "nota_dobanda_angajata": "nota dobânzii angajate", "comodat_chirii": "chirii și comodat (Operațiuni speciale)", "nota_chirie_incasata": "nota chiriei încasate",
    "nota_chirie_platita": "nota chiriei plătite", "nota_refacturare": "nota de refacturare a utilităților", "nota_avans": "nota de avans",
    "nota_avans_incasat": "nota avansului încasat", "nota_avans_platit": "nota avansului plătit", "nota_regularizare_avans_incasat": "regularizarea avansului încasat",
    "nota_regularizare_avans_platit": "regularizarea avansului plătit", "capital_social": "capitalul social", "pierdere_constatata": "pierderea constatată",
    "reclasificare_bilant": "reclasificarea în bilanț", "f10_din_balanta": "bilanțul din balanță (Bilanț)",
    # ── salarii ──
    "calcul_salariu": "calculul salariului (Salarii)", "monografie_salariu": "monografia salariului (Salarii)", "stat_plata": "statul de plată (Salarii)",
    "calcul_cm": "calculul concediului medical (Salarii)", "taxe_cm": "contribuțiile la concediul medical", "procent_cm": "procentul indemnizației",
    "calcul_mandat": "calculul contractului de mandat (Salarii)", "deducere_personala": "deducerea personală", "baza_podea": "baza minimă a contribuțiilor",
    "plafon_diurna": "plafonul diurnei", "tichet_masa_valoare": "valoarea tichetului de masă (Salariați)", "zile_fara_tichet": "zilele fără tichet",
    "tichet_cultural": "tichetul cultural", "concediu_odihna": "concediu de odihnă", "absent_motivat": "absent motivat", "absent_nemotivat": "absent nemotivat",
    "data_angajare": "data angajării", "tip_norma": "tipul normei", "norma_intreaga": "normă întreagă", "salariu_baza": "salariul de bază",
    "salariu_minim": "salariul minim", "salariu_minim_luna": "salariul minim al lunii", "scutit_contrib_minim": "scutit de contribuția minimă (Salariați)",
    "exceptat_suprataxare": "exceptat de la suprataxare", "podea_part_time_minus_facilitate": "baza minimă la timp parțial",
    "mesaj_adaugare_contract": "transmiterea contractului în REGES (Salarii)", "mesaj_incetare_contract": "încetarea contractului în REGES (Salarii)",
    "mesaj_inregistrare_salariat": "înregistrarea salariatului în REGES (Salarii)",
    # ── HoReCa, AMEF, producție, diverse ──
    "horeca_z": "raportul Z (HoReCa)", "horeca_import_amef": "importul AMEF (HoReCa)", "horeca_raport_z": "raportul Z introdus manual (HoReCa)",
    "parseaza_raport_z": "citirea raportului Z", "amef_import": "importul AMEF", "nota_incasare": "nota de încasare (HoReCa, bacșiș)",
    "nota_distribuire": "nota de distribuire a bacșișului (HoReCa)", "bacsis_brut": "bacșișul brut", "sume_serv_in": "sumele de serviciu de la începutul zilei",
    "sume_serv_out": "sumele de serviciu de la sfârșitul zilei", "payment_method": "metoda de plată", "payment_method_anaf": "codul ANAF al metodei de plată",
    "cash_and_carry": "cash and carry", "data_livrare": "data livrării", "data_nota": "data notei", "marfa_pleaca_cu_factura": "marfa pleacă cu factura",
    "pleaca_marfa": "marfa pleacă", "tert_nume": "numele terțului", "tert_cui": "CUI-ul terțului", "tert_pf": "persoană fizică",
    "detecteaza_tip": "detectarea tipului de operațiune", "regula_cont": "regula de contare", "degradare_dovedita_distrusa": "bunuri distruse dovedit",
    "valoare_imputare": "valoarea imputată", "ramura_291_5": "ramura art.291 alin.(5)", "cu_plata": "cu plată",
    "solduri_initiale": "soldurile inițiale (Migrare)", "inregistrari_linii": "notele contabile", "admin_firma": "administrator",
    "tenant_id": "firma", "venit_lunar": "venitul lunar", "neaplic_statut": "nu se aplică", "data_start": "data de început", "data_end": "data de sfârșit",
}
#: denumirile din STRUCTURILE OFICIALE ANAF (câmpuri XML / XSD / API) — nu sunt cod al aplicației; rămân, fiindcă așa le scrie ANAF
NOMENCLATOR_OFICIALE = {
    "d_rec", "d_reg", "d_reglem", "d_anulare", "d_succ", "d_prof", "d_alte", "tip_venit1", "tip_venit", "tip_partener", "cod_oblig", "cod_bugetar",
    "nr_evid", "pers_inreg", "mij_transp", "an_r", "luna_r", "nume_declar", "solicit_ramb", "bifa_interne", "oblig_realizat",
    "str_credit_fiscal", "str_impozit_platit", "real_ajustare", "real_impozit", "real_norma_venit", "real_venit_net_anual", "norma_forma_org",
    "vat_rate", "taxable_amount", "vat_amount", "r28_2", "r31_2", "id_descarcare", "cod_caen", "tip_plata", "stare_inactiv",
}
N = NOMENCLATOR_CODURI_GHID
O = NOMENCLATOR_OFICIALE
#: metode / module / constante ale aplicației (nume scurte) -> ce vede contabilul
NOMENCLATOR_CODURI_SCURTE = {
    "pull": "preluarea datelor", "genereaza": "generarea", "valideaza": "validarea", "storneaza": "stornarea", "conteaza": "contarea",
    "partaj": "partajul", "editeaza": "editarea", "lista": "lista", "adauga": "adăugarea", "diferenta": "calculul diferenței de curs",
    "registru_casa": N["registru_casa"], "valideaza_cui": "verificarea CUI-ului", "erori_declarant": "verificarea datelor declarantului (Date firmă)",
    "sugestie": "sugestia de cont", "cere_cont": "verificarea contului", "zile_lucratoare_luna": "zilele lucrătoare ale lunii",
    "balanta": "balanța de verificare", "fereastra_tva": "perioada TVA", "nota_amef_ciorna": "nota raportului Z",
    "ROUND_HALF_UP": "rotunjirea aritmetică (jumătatea în sus)", "ROUND_HALF_EVEN": "rotunjirea bancară", "Decimal": "calcul zecimal exact",
    "PLAFON_PF": "plafonul pentru persoane fizice", "PLAFON_INCASARE_PJ": "plafonul de încasare de la persoane juridice",
    "PLAFON_INCASARE_PJ_CC": "plafonul de încasare cash and carry", "PLAFON_PLATA_PJ": "plafonul de plată către persoane juridice",
    "PLAFON_PLATA_PJ_TOTAL": "plafonul total de plăți", "PLAFON_AVANS": "plafonul avansului de trezorerie",
    "EXCEPTII_21": "excepțiile cu cota de 21%", "CATEGORII_11": "categoriile cu cota de 11%", "CATEGORII_PLATA": "categoriile de plăți",
    "CATEGORII_INCASARE": "categoriile de încasări", "COD_BUGETAR": "codul bugetar", "COD_CONT_D112": "contul bugetar D112",
    "COTE": "registrul de cote al aplicației", "COTA_STANDARD": "cota standard", "COTA_REDUSA": "cota redusă", "COTA_IMPOZIT": "cota de impozit",
    "TARI_UE": "statele membre UE", "TEMEI_CMP": "temeiul costului mediu ponderat", "PLAN_NOMENCLATOR": "planul de conturi",
    "REGIM_INVALID": "refuzul regimului invalid", "REGIM_LA_PARTIDA_SIMPLA": "refuzul regimului la partidă simplă",
    "PESTE_PERIOADA_INCHISA": "refuzul pe perioadă închisă", "ValueError": "refuz", "NotImplementedError": "refuz", "MAX_COMBO": "numărul maxim de combinații",
    "_REGIMURI": "regimurile fiscale", "ANI_VERIFICATI": "anii verificați", "_VARIANTE_PLAFON_CREDIT": "variantele plafonului de credit",
    "ActiuneIncetare": "acțiunea de încetare", "line_items": "liniile comenzii", "_calcul_salariu_2018": N["calcul_salariu"],
    "_valideaza": "validarea", "_cere_luna_deschisa": "verificarea lunii deschise", "_vatid": "codul de TVA", "_adauga_d100_micro": "D100 micro",
    "_scadenta_2026": "scadența", "_scadenta_cod": "scadența", "_partener_registration_number": "codul partenerului",
    "_partener_id_saft": "codul partenerului în SAF-T", "_erori_valori_p": "verificarea valorilor", "_conteaza_la_creare": "contarea la emitere",
    "_data_cota": "data cotei", "querySelector": "câmpul din ecran", "intrare": "intrarea în stoc", "storno": "stornarea",
    "reconciliaza": "reconcilierea", "sterge": "ștergerea", "contabilizeaza": "contarea", "construieste": "construirea declarației",
    "iesire": "ieșirea din stoc", "citeste": "citirea", "salveaza": "salvarea", "descarca": "descărcarea", "d101": "D101", "d100": "D100", "d112": "D112", "d205": "D205", "d390": "D390",
}
N2 = NOMENCLATOR_CODURI_SCURTE
#: fișierele locale cu documente OFICIALE -> numele documentului
NOMENCLATOR_DOCUMENTE_OFICIALE = {
    "cod_fiscal_227_2015_consolidat.txt": "Codul fiscal (Legea 227/2015), forma consolidată",
    "opanaf_206_2025_d101.txt": "OPANAF 206/2025 (structura D101)", "d101_struct_anaf.txt": "structura D101 publicată de ANAF",
    "d406_schema_anaf.xlsx": "schema SAF-T (D406) publicată de ANAF", "d406_nomenclatoare_anaf.properties": "nomenclatoarele SAF-T publicate de ANAF",
    "structura_D207_2025.txt": "structura D207 publicată de ANAF", "DUKIntegrator_AnLunaUI.jar": "validatorul ANAF (DUKIntegrator)",
    "SAFT.xml.err.txt": "raportul de erori al validatorului ANAF",
    "opanaf_1783_2021_saft_d406.txt": "OPANAF 1783/2021 (SAF-T, D406)", "opanaf_407_2025_saft_d406.txt": "OPANAF 407/2025 (SAF-T, D406)",
    "ordin_394_19012017.pdf": "OPANAF 394/2017",
}
DOC_OFICIAL = NOMENCLATOR_DOCUMENTE_OFICIALE
_DOC_RX = re.compile(r"(?<![\w/])`?(%s)(?::\d+)?`?(,\s*L\d+(?:-\d+)?(?:,\s*L\d+(?:-\d+)?)*)?" % "|".join(re.escape(k) for k in sorted(DOC_OFICIAL, key=len, reverse=True)))


def _doc_oficial(text, n):
    def r(m):
        n[0] += 1
        return DOC_OFICIAL[m.group(1)]
    return _DOC_RX.sub(r, text)
_SN = re.compile(r"(?<![\w/.-])([a-z][a-z0-9]*(?:_[a-z0-9]+)+)(?![\w/-])")
_TOK = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def _eticheta(t):
    t = t.split(".")[-1].rstrip("()")
    return N.get(t) or N2.get(t)


def _e_cod_aplicatie(s):
    """Span-ul conține cod al aplicației (nu o formulă contabilă, nu un nume oficial ANAF)?"""
    if re.search(r"\.(py|js|md|csv)\b|/home/|/tenants/|\btest_\w+|\btenant_\d+|^grep |^-abs\(|^nota\(|^(status|sursa)\s*=", s) or s.strip() in NOMENCLATOR_OPERATIUNI \
            or s.strip() in NOMENCLATOR_EXPRESII:
        return True
    return any((t in N or t in N2) and t not in O for t in _TOK.findall(s)) or any(_eticheta(x) for x in re.findall(r"[\w.]+\(\)", s))


#: cheile operațiunilor din ecranul Operațiuni speciale / enumerări interne
NOMENCLATOR_OPERATIUNI = {"nota-tva-incasare": "nota TVA la încasare (Operațiuni speciale)", "nota-inventariere": "nota de inventariere (Operațiuni speciale)",
         "nota-obiect-inventar": "nota obiectului de inventar (Operațiuni speciale)"}
NOMENCLATOR_STARI = {"ciorna": "ciornă", "validata": "validată", "contat": "contată", "banca": "bancă", "numerar": "numerar", "manual": "manual"}


#: expresii de cod (comparații, apeluri, valori Python) scrise între backtick-uri -> ce înseamnă ele pentru contabil
NOMENCLATOR_EXPRESII = {
    "deductibil: False": "„nedeductibil”", "deductibil = (tip == \"garantii\")": "deductibil numai pentru garanții",
    "datetime.date.today()": "data zilei", "_lei()": "„rotunjirea la leu întreg”", "regim == \"micro\"": "„regim micro”",
    "regim == \"profit\"": "„regim profit”", "None": "un rezultat gol", "g(\"P23\")": "P23", "g(\"P33\")": "P33",
"emisa=True": "factură emisă", "inventar()": "„inventarierea gestiunii”",
    "completat=False": "vector fiscal necompletat", "portofoliu()": "„termenele portofoliului”", "activ=false": "marcat inactiv",
    "filtru=P": "tipul „P” — facturi primite",
}
#: trimiteri la registrele interne ale proiectului (coduri de neconformitate) -> ce înseamnă pentru contabil
FRAZE_INTERNE = [
    (r"o neconformitate deschisă \(R\d+, urmărită în registrul intern al proiectului\)", "o limitare cunoscută a aplicației"),
    (r"o neconformitate deschisă \(R\d+\) în registrul intern al proiectului", "o limitare cunoscută a aplicației"),
]
#: PROZĂ DESPRE COD — comanda Costin 13.10.2026 (răspunsul la §6 COMANDA_13_10 pct.2): „rescrie acele pasaje din perspectiva
#: contabilului, adică ce face aplicația pentru el, fără referiri la cod sau la registrele proiectului.” Tiparele numite de Costin și
#: trimiterile tehnice: ZERO în orice ghid (gard absolut).
PROZA_COD_ZERO = re.compile(r"comentariul din cod|registrul intern al (proiectului|aplicației|funcționalităților)|evidența internă a funcționalităților"
                            r"|\bdosar(ul|ului)? (tehnic|de cercetare)\b|\bmirror\w*|\bGH-\d{5}\b|\bliniile \d+[–-]\d+\b|\.timer\b|\bcron(-ul|ul)?\b",
                            re.I)
#: Clasa LARGĂ, măsurată la 13.10.2026 (1.413 ghiduri): „verificat în cod”, „motorul de calcul”, „cercetarea”, termeni tehnici. Nu
#: crește (clichet pe fișier, core/clichet_proza_cod_ghid.json); rescrierea ei e decizia lui Costin (raportul lotului, §6).
PROZA_COD_CLICHET = re.compile(
    r"\b(în|din|la nivel de) cod(ul)?(?!\s*(fiscal|de procedur|muncii|civil|penal|caen|tva|nc\b|de bare|de identificare|cpv|iban|bic|swift|"
    r"siruta|poștal|postal|de înregistrare|unic|de țară|țării|tarifar|vamal|partener|special|al tipului|de cont|obligației|de obligație|"
    r"bugetar|ue\b|eori|\d))\b|\bcodul (refuză|aplicației|sursă|motorului|verificat|iconta)|\bcod(ul)? sursă\b"
    r"|\bhardcod\w*|\bflag(-ul|-uri\w*|ul|uri)?\b|\bfallback\b|\bparser\w*|\bpicker\w*|\bendpoint\w*|\bdocstring\w*|\bbackend\b|\bfrontend\b"
    r"|\bcercetarea (de temei|de bază|de până|tehnică)|\bacest dosar\b"
    r"|\bmotor(ul|ului)?\b(?! (diesel|electric|termic|vehicul|auto))", re.I)


def proza_cod(text, tipar):
    """Potrivirile unui tipar de proză despre cod în textul PUBLIC al ghidului. Clasa largă se caută în afara casetelor de temei (un
    citat de lege poate spune „motor”); tiparele cu zero absolut se caută peste tot — nota „verificat pe mirrorul local” stătea chiar în
    casete, iar niciun text de lege nu spune „mirror” sau „comentariul din cod”."""
    corp = text if tipar is PROZA_COD_ZERO else re.sub(r"^:::\s*ghid-temei.*?^:::\s*$", " ", text, flags=re.S | re.M)
    return [m.group(0) for m in tipar.finditer(corp)]


#: o expresie de cod între backtick-uri (gardul o caută; o formulă contabilă `6814=491` nu e cod)
EXPRESIE_COD = re.compile(r"==|!=|\bNone\b|\bTrue\b|\bFalse\b|\w\(\)|\"\w+\"\)|\b[a-z_]+\.[a-z_]+\(|\b[a-z_]+=[A-Za-z]")


def inlocuieste_span(s):
    s0 = s.strip()
    if s0 in NOMENCLATOR_EXPRESII:
        return NOMENCLATOR_EXPRESII[s0]
    if s0 in NOMENCLATOR_OPERATIUNI:
        return "„%s”" % NOMENCLATOR_OPERATIUNI[s0]
    m = re.fullmatch(r"(status|sursa)\s*=\s*['\"](\w+)['\"]", s0)
    if m:
        return "%s „%s”" % ({"status": "starea", "sursa": "sursa"}[m.group(1)], NOMENCLATOR_STARI.get(m.group(2), m.group(2)))
    if s0.startswith("grep "):
        return "verificarea în aplicație"
    if re.fullmatch(r"-abs\((\w+)\)", s0):
        return "cantitatea, cu semn minus"
    m = re.fullmatch(r"nota\(fel=(.+)\)", s0)
    if m:
        return "nota contabilă (%s)" % m.group(1).replace('"', "")
    if s0 in DOC_OFICIAL:
        return DOC_OFICIAL[s0]
    if re.search(r"\.(py|js)\b", s0) and not re.search(r"\w\(", s0):
        return "aplicația"
    if re.search(r"\.(md|csv)\b|/home/", s0):
        return "documentația internă"
    if re.match(r"test_\w+", s0) or re.search(r"::test_", s0):
        return "testele aplicației"
    m = re.match(r"^(GET|POST|PUT|PATCH|DELETE)\s+/tenants/\S+", s0)
    if m or s0.startswith("/tenants/"):
        return "aplicația"
    if "querySelector" in s0 or "=>" in s0:             # fragment de cod din ecran: câmpul, cum îl vede contabilul
        e = next((_eticheta(t) for t in _TOK.findall(s0) if _eticheta(t)), None)
        return "câmpul „%s” din ecran" % e if e else "câmpul din ecran"
    if re.match(r"^(GET|POST|PUT|PATCH|DELETE)\s+/", s0):
        return "aplicația"
    m = re.match(r"^([\w.]+)\s*\(", s0)                  # apel: numele funcției, fără argumente
    if m and _eticheta(m.group(1)):
        return "„%s”" % _eticheta(m.group(1))
    m = re.match(r"^([A-Z_][A-Z0-9_]*)\s*=\s*(.+)$", s0)   # constantă = valoare
    if m and _eticheta(m.group(1)):
        return "%s = %s" % (_eticheta(m.group(1)), re.sub(r'Decimal\("?([\d.]+)"?\)', r"\1", m.group(2)))
    if _TOK.fullmatch(s0.replace(".", "_")) and _eticheta(s0):
        return "„%s”" % _eticheta(s0)
    # altfel: fiecare nume de cod din span -> eticheta lui; span-ul devine text simplu
    out = re.sub(r"[\w.]+\(\)", lambda m: _eticheta(m.group(0)) or m.group(0), s0)
    out = _TOK.sub(lambda m: (N.get(m.group(0)) or N2.get(m.group(0)) or m.group(0)) if m.group(0) not in O else m.group(0), out)
    return out


def _protejate(corp):
    """Intervalele (start, stop) ale citatelor OFICIALE din blocurile `::: ghid-temei` — nu se ating."""
    out = []
    # blocul se termină la „:::” sau, dacă autorul a uitat să-l închidă, la titlul următor („## …”) — nu înghite corpul ghidului
    for b in re.finditer(r"^:::\s*ghid-temei.*?(?:^:::\s*$|(?=^## ))", corp, re.S | re.M):
        out.append((b.start(), b.end()))
    return out


def curata(text):
    """(text nou, schimbări) — citatele oficiale din temei rămân; restul își pierde numele de cod."""
    if text.startswith("---\n"):
        i = text.index("\n---\n", 4) + 5
        fm, corp = text[:i], text[i:]
    else:
        fm, corp = "", text
    prot = _protejate(corp)
    bucati, poz = [], 0
    for a, b in prot:
        bucati.append((corp[poz:a], False))
        bucati.append((corp[a:b], True))
        poz = b
    bucati.append((corp[poz:], False))
    n = [0]

    def span(m):
        s = m.group(1)
        if not _e_cod_aplicatie(s):
            return m.group(0)
        n[0] += 1
        return inlocuieste_span(s)

    rez = []
    for bucata, e_temei in bucati:
        bucata = _doc_oficial(bucata, n)
        if e_temei:
            bucata = _curata_temei(bucata, n, span)
            bucata = _feature(bucata, n)
        else:
            bucata = _feature(bucata, n)
            for rx, inloc in FRAZE_INTERNE:
                bucata, k = re.subn(rx, inloc, bucata)
                n[0] += k
            bucata = bucata.replace("`Decimal` și `ROUND_HALF_UP`", "aritmetică (jumătatea în sus)")
            bucata = re.sub(r"\s*\(\s*`([^`\n]+\.(?:py|js))`\s*\)", lambda m: (n.__setitem__(0, n[0] + 1) or ""), bucata)
            bucata = re.sub(r"`([^`\n]+)`", span, bucata)
            bucata = re.sub(r"\btenant_\d+\b", lambda m: (n.__setitem__(0, n[0] + 1) or "o firmă de test"), bucata)
            bucata = _SN.sub(lambda m: (n.__setitem__(0, n[0] + 1) or N[m.group(1)]) if m.group(1) in N and m.group(1) not in O else m.group(0),
                             bucata)
        rez.append(bucata)
    # liste de module devenite „(aplicația, aplicația)” -> o singură mențiune; parantezele goale dispar
    for i, bucata in enumerate(rez):
        bucata = re.sub(r"\((?:aplicația,\s*)+aplicația\)", "(aplicația)", bucata)
        bucata = re.sub(r"(?:aplicația,\s*)+aplicația\b", "aplicația", bucata)
        bucata = re.sub(r"\b(aplicație|aplicația|aplicației)( și modulele conexe)? \(aplicația\)", r"\1\2", bucata)
        rez[i] = bucata
    # un bloc de temei rămas GOL (singurul lui citat era codul aplicației) dispare, cu titlul secțiunii dacă nu mai are nimic sub el
    corp_nou = "".join(rez)
    # titlul „Temeiul legal” de imediat deasupra unui bloc rămas gol pleacă odată cu el (altfel ar sta deasupra unui text care nu e temei)
    corp_nou, k = re.subn(r"^## Temeiul legal\s*\n(?:\s*\n)*:::\s*ghid-temei\s*\n(?:\s*\n)*:::\s*\n(?:\s*\n)*(?!:::)(?=\S)", "", corp_nou, flags=re.M)
    n[0] += k
    corp_nou, k = re.subn(r"^:::\s*ghid-temei\s*\n(?:\s*\n)*:::\s*\n?", "", corp_nou, flags=re.M)
    n[0] += k
    corp_nou = re.sub(r"^## Temeiul legal\s*\n(?:\s*\n)*(?=^## |\Z)", "", corp_nou, flags=re.M)
    rez = [corp_nou]
    # titlul și descrierea din front-matter sunt și ele text public (meta description, cuprins)
    def fm_linie(m):
        v = _feature(m.group(2), n)
        v = re.sub(r"`([^`\n]+)`", span, v)
        v = _SN.sub(lambda x: (n.__setitem__(0, n[0] + 1) or N[x.group(1)]) if x.group(1) in N and x.group(1) not in O else x.group(0), v)
        return m.group(1) + v
    fm = re.sub(r"(?m)^((?:title|description):\s*)(.*)$", fm_linie, fm)
    return fm + "".join(rez), n[0]


def _functionalitati():
    import csv
    import io
    rows = csv.DictReader(io.StringIO(open(os.path.join(RAD, "FUNCTIONALITATI.csv"), encoding="utf-8").read()))
    return {r["ID"]: r["Functionalitate"].strip() for r in rows}


_F = _functionalitati()
#: referințele la dosarele interne de cercetare nu sunt ale cititorului
_DOSAR = [
    (re.compile(r",?\s*verificat (?:direct )?în dosarul(?: de cercetare)? F\d{3}"), ""),
    (re.compile(r"\s*\((?:conform |vezi )?dosarul(?: de cercetare)?(?: pentru)? F\d{3}[^)]*\)"), ""),
    (re.compile(r"\s*[—-]\s*dosarul(?: de cercetare)? F\d{3}[^.\n]*"), ""),
    (re.compile(r"dosar(?:ul)?(?: de cercetare)?(?: pentru)?(?: funcționalitatea)? F\d{3}"), "documentația aplicației"),
]


def _feature(text, n):
    for rx, r in _DOSAR:
        text, k = rx.subn(r, text)
        n[0] += k

    def f(m):
        nume = _F.get(m.group(1))
        if not nume:
            return m.group(0)
        n[0] += 1
        par = m.group(2)
        if par and par.strip(" ()").lower().startswith(nume.lower()[:12]):
            return "„%s”" % nume
        return "„%s”%s" % (nume, par or "")
    return re.sub(r"\b(F\d{3})\b(\s*\([^)]*\))?", f, text)


def _citat_din_aplicatie(u):
    """Un CITAT (începe cu ghilimele / „>”) a cărui sursă e aplicația: codul ei, registrul intern, „dosarul de cercetare Fnnn”."""
    s = u.strip()
    if re.search(r"Descrierea funcționalității|înregistrarea canonică a funcționalității|FUNCTIONALITATI\.csv|/home/", s):
        return True                                  # registrul intern al funcționalităților, citat ca „temei”
    if not re.match(r"^(:::[^\n]*\n)?\s*[„\"“>]", s):
        return False
    atrib = s.rsplit("—", 1)[-1] if "—" in s else ""
    app_in = any(x in N and x not in O for x in re.findall(r"[a-z][a-z0-9]*(?:_[a-z0-9]+)+", s))
    return bool(app_in or re.search(r"(în|din) cod(ul)?( sursă)?\b|marcaj intern|docstring|/home/|FUNCTIONALITATI|funcționalității „|GARZI|"
                                    r"DECIZII|\.md:\d+|stare documentată intern", s)
                or re.search(r"[Ss]ursă:\s*(\[)?\s*(Aplicația|aplicația|codul aplicației|iConta)", s) or re.search(r"dosar(ul)?( de cercetare)? F\d{3}", s)
                or re.search(r"\b(aplicația|aplicație|codul|docstring|\.py)\b", atrib)
                or (re.match(r"^[„\"]\s*`", s) and _e_cod_aplicatie(s))
                or any(EXPRESIE_COD.search(x) for x in re.findall(r"^(?::::[^\n]*\n)?\s*[„\"]\s*`([^`\n]+)`", s)))


def _curata_temei(bloc, n, span):
    """În blocul de temei: un CITAT a cărui sursă e APLICAȚIA nu e temei — se scoate (deschiderea / închiderea blocului rămân); citatele
    din acte rămân neatinse; un paragraf explicativ (nu citat) își pierde numai denumirile din cod, ca restul ghidului."""
    for rx, r in _DOSAR[:3]:                         # întâi: fragmentele „verificat în dosarul Fnnn” din sursa unui citat oficial
        bloc, k = rx.subn(r, bloc)
        n[0] += k
    out = []
    for u in re.split(r"(\n\s*\n)", bloc):
        if _citat_din_aplicatie(u):
            n[0] += 1
            cap = re.match(r"^(\s*:::[^\n]*\n)", u)
            coada = re.search(r"(\n\s*:::\s*)$", u)
            out.append((cap.group(1) if cap else "") + (coada.group(1).lstrip("\n") if coada else ""))
            continue
        if not re.match(r"^\s*(:::[^\n]*\n)?\s*[„\"“>]", u):   # paragraf explicativ: numai numele din cod
            u = re.sub(r"`([^`\n]+)`", span, u)
            u = _SN.sub(lambda m: (n.__setitem__(0, n[0] + 1) or N[m.group(1)]) if m.group(1) in N and m.group(1) not in O else m.group(0), u)
        out.append(u)
    return "".join(out)


def cu_data(text, zi):
    """Front-matter-ul cu `modified: <zi>` (data ultimei actualizări a ghidului)."""
    if re.search(r"(?m)^modified:", text[:text.find("\n---\n", 4) + 1]):
        return re.sub(r"(?m)^modified:.*$", "modified: %s" % zi, text, count=1)
    return text.replace("\n---\n", "\nmodified: %s\n---\n" % zi, 1)


if __name__ == "__main__":
    sys.path.insert(0, RAD)
    import argumente_script  # noqa: F401
    argv = argumente_script.citeste(sys.argv[1:], __doc__, flaguri=("--scrie",), prefix="[curata_coduri]")
    zi = datetime.date.today().isoformat()
    tot = fis = 0
    for p in sorted(glob.glob(os.path.join(RAD, "ghid", "*.md"))):
        t = open(p, encoding="utf-8").read()
        nou, k = curata(t)
        if k and nou != t:
            fis += 1
            tot += k
            if "--scrie" in argv:
                open(p, "w", encoding="utf-8").write(cu_data(nou, zi))
    print("ghiduri schimbate: %d · înlocuiri: %d%s" % (fis, tot, "" if "--scrie" in argv else " (fără --scrie: nimic scris)"))
