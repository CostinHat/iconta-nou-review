"""core/d212.py - D212: Declaratia unica privind impozitul pe venit si contributiile sociale
datorate de persoanele fizice (cea mai complexa declaratie ANAF; ns v11, pachet validator v9).

Declaratie MANUALA (persoana fizica): aplicatia nu are registru de persoane fizice, nici
veniturile/contributiile lor. Toate datele vin din dict-ul `manual`. Firma (conn/schema) NU
contine sursa - `pull` intoarce {} (contractul dXXX cere metoda).

SURSA STRUCTURII = VALIDATORUL OFICIAL ANAF (arbitrul), D212Validator.jar. Structura in vigoare
pentru anul de raportare 2025 a fost CITITA din bytecode si PROBATA camp cu camp pe DUKIntegrator:
  - Radacina reala = element <d212> (NU <declaratie>; acela era ns:v1, invechit). Namespace v11.
  - Selectia versiunii (d212validator/Validator._dateVersionTable): randul
    '2025-01 J13.0.1 9 7 2025-01-15' => pachet validator v9 + Parameters_v7 => namespace v11.
  - Copii (elemente lowercase): cap11, cap12, cap14, oblig_realizat, oblig_estimat, coasigurat.
  - Atribute OBLIGATORII pe radacina (flag mandatory=1 in checkTag), probate ca lipsa/necesare:
    d_rec, rectif1, rectif2, totalPlata_A, luna_r(=12 fix, interval [12,12]), an_r(interval
    [2025,2100]), bifa_succesor, anulare_litA, anulare_litB, bifa_conformare, bifa111, bifa112,
    bifa113, bifa121, bifa122, bifa131, bifa132, bifa14, bifa15, nerezident + identificare
    (cif, nume_c, adresa_c). bifa16/bifa18 optionale.
  - DUK regula R4 (ValidatorCode.validateD212, citita INTEGRAL 01.10.2026): daca `cif` are 13 cifre
    (CNP), totalPlata_A == suma celor 13 cifre — MEREU, indiferent de sumele de plata (forma veche a acestui
    docstring, „suma sumelor de plata", era gresita: o declaratie cu obligatii ar fi picat la R4).
    Probat: CNP ...1144 => 25; 21580 (suma obligatiilor) => R4.

CAZUL PRINCIPAL ACOPERIT + PROBAT DUK VALID: declaratie de identificare (fara obligatii de plata
- nula / rectificativa / doar identificare), cu toate bifele pe 0. Este cazul MINIM care trece
validatorul si nucleul garantat-VALID al generatorului.

EXTENSIBIL (structura mapata integral din bytecode, se emite din `manual` cand e furnizata):
capitolele de venit realizat (cap11 sistem real, cap12 norma de venit, cap14 strainatate) si
contributiile (oblig_realizat CAS/CASS, oblig_estimat, coasigurat). Pentru un capitol POPULAT,
apelantul furnizeaza valorile deja calculate (venituri, baze, impozit, CAS, CASS) intr-un sub-dict
per element; generatorul le emite ca atribute si NU recalculeaza cotele/plafoanele (interzis sa
hardcodam cote de impozit/CAS/CASS). Regulile de consistenta interne (impozit=venit*cota, baze la
plafon, R-uri CAS/CASS) raman in sarcina datelor de intrare - vezi field-reference in `_CAMPURI`.

Contract dXXX: NS, _cif/_cnp_valid/_esc, calcul_d212, pull(conn,schema,perioada)->{},
erori_generare, build_xml, genereaza(conn, schema, perioada, manual=None). conn=None este acceptat
(pull nu atinge baza).
"""

#: [07.09.2026] denumirea OFICIALA (cu diacritice) - se afiseaza pe ecranul public,
#: derivata de scripts/genereaza_declaratii_lista.py. Corectura ORTOGRAFICA peste
#: denumirea deja consemnata in modul; NU o re-verificare la ANAF.
DENUMIRE_OFICIALA = 'Declarația unică privind impozitul pe venit și contribuțiile sociale datorate de persoanele fizice'
from dataclasses import dataclass, field
import calendar
import datetime as _dt
from decimal import Decimal, ROUND_HALF_UP
import re

from core.common import Temei as _Tm, ancoreaza as _anc, temei_ancorat as _temei_anc

NS = "mfp:anaf:dgti:d212:declaratie:v11"

_NEDIGIT = re.compile(r"\D")
_CNP_W = [2, 7, 9, 1, 4, 6, 3, 5, 8, 2, 7, 9]

# Luna de raportare - constanta structurala a schemei (interval [12,12] in validator), nu o cota.
_LUNA_R = "12"

# Elementele-copil in ordinea din initializareDocument (validatorul accepta atributele dupa nume,
# ordinea nu e critica; o pastram pentru lizibilitate).
_COPII = ["oblig_realizat", "oblig_estimat", "cap11", "cap12", "cap14", "coasigurat"]

# Referinta campurilor pe element (numele de atribut XML = numele campului fara '_' din bytecode).
# Emitem DOAR chei din aceste seturi (o cheie necunoscuta e respinsa de validator ca atribut strain).
_CAMPURI = {
    "cap11": {"scutire", "categ_venit", "det_ven_net", "forma_org", "mod_forma_org",
              "caen", "descriere_sediu_bun", "nr_doc_autoriz", "data_doc_autoriz",
              "data_incep", "data_sf", "nr_zile_scutite", "venit_brut", "chelt_deduc",
              "venit_net_anual", "pierdere", "pierdere_precedenta", "pierdere_compensata",
              "venit_recalculat", "venit_redus", "impozit11"},
    "cap12": {"norma_forma_org", "norma_caen", "norma_descriere_sediu_bun", "norma_nr_doc_autoriz",
              "norma_data_doc_autoriz", "norma_data_incep", "norma_data_sf", "norma_data_susp",
              "norma_nr_zile_scutite", "real_norma_venit", "real_ajustare",
              "real_venit_net_anual", "real_venit_impozit", "real_impozit"},
    "cap14": {"str_stat_realiz_v", "str_categ_venit", "dubla_impunere", "str_data_incep",
              "str_data_sf", "str_venit_brut", "str_chelt_deduc", "str_venit_net_anual",
              "str_pierdere_anuala", "str_pierdere_precedenta", "str_pierdere_compensata",
              "str_venit_recalculat", "str_impozit_datorat_Ro", "str_impozit_platit",
              "str_credit_fiscal", "str_dif_impozit_datorat"},
    "oblig_estimat": {"bifa_optiune", "situatie_optiune", "baza_optiune", "cass_optiune",
                      "bifa_optiune_coasigurat", "totalCassDatorat", "totalCassDatoratCoasigurat"},
    "coasigurat": {"tipCoasigurat", "numeCoasigurat", "cnpCoasigurat", "bazaCassCoasigurat",
                   "cassDatoratCoasigurat"},
    # oblig_realizat: numele ATRIBUTELOR XML din D212Validator.jar v9, clasa Oblig_realizat — nu numele câmpurilor interne
    # (`_cass_ret_plat_alin6_ai` se citește din `cass_retinut_platitor_alin6_ai`; I.4 rd.2/rd.3 n-au atribut propriu, ele
    # sunt `real_cas_deductibila_ai` / `real_cass_deductibila_ai` din I.4.1/I.4.2). Confruntat cu jar-ul de
    # core/test_d212_campuri_validator.py (corectat 02.10.2026: 7 nume interne aici + `reg` la cap11).
    "oblig_realizat": {
        "real_camere_inchiriere", "real_venit_inchiriere", "real_impozit_inchiriere",
        "str_cas_baza", "str_cas_datorat", "str_cass_baza", "str_cass_datorat",
        "bifa_cas_real", "cas_total_ven", "cas_baza", "cas_datorat", "cas_retinut_platitor",
        "cas_dif_plus", "bifa_cass_datorat_ai", "bifa_cass_datorat_dpi", "cass_total_ven_ai",
        "baza_cass_datorat_ai", "cass_datorat_ai", "cass_retinut_platitor_alin6_ai", "cass_dif_plus_ai",
        "cass_dif_minus6_ai", "cass_retinut_platitor_alin7_ai", "cass_dif_minus8_ai", "bifa_cass_real",
        "cass_ven_dpi", "cass_ven_asc", "cass_ven_cfb", "cass_ven_inv", "cass_ven_asp",
        "cass_ven_alt", "cass_total_ven", "cass_baza", "cass_datorat", "cass_retinut",
        "cass_dif_plus", "real_venit_net_recalculat_ai",
        "real_venit_net_impozabil_ai", "real_venit_net_impozabil_redus_ai",
        "real_impozit_datorat_ai", "real_cas_venit_net_ai", "real_cas_total_ven_ai",
        "real_cas_pondere_ai", "real_cas_datorata_ai", "real_cas_deductibila_ai",
        "real_cass_venit_net_ai", "real_cass_total_ven_ai", "real_cass_pondere_ai",
        "real_cass_datorata_ai", "real_cass_calculata_ai", "real_cass_deductibila_ai",
        "real_venit_net_recalculat_dpi", "real_cas_dpi", "real_venit_net_impozabil_dpi",
        "real_venit_net_impozabil_redus_dpi", "real_impozit_datorat_dpi", "real_cas_venit_net_dpi",
        "real_cas_total_ven_dpi", "real_cas_pondere_dpi", "real_cas_datorata_dpi",
        "real_cas_deductibila_dpi", "real_diferenta_CASS", "real_impozit_diferenta_CASS",
        "oblimpoz_real_total", "oblimpoz_real_anticipat", "oblimpoz_real_dif_deplata",
        "oblimpoz_real_dif_restituit", "oblcas_real_difPlus", "oblcas_real_str",
        "oblcass_real_difPlus_ai", "oblcass_real_difMinus_ai", "oblcass_real_difMinus_174",
        "oblcass_real_difPlus_dpi", "oblcass_real_str", "impozit_venit_plus",
        "impozit_venit_minus", "cas_plus", "cass_plus", "cass_minus", "dif_de_plata",
        "dif_de_restituit", "oblimpozit_real_bonif", "oblcas_real_bonif", "oblcass_real_bonif"},
}

# ── CAP11 (subsectiunea I.1.1 — venituri din Romania, sistem real / cote forfetare) ──────────────────
# Nomenclatoarele NU sunt in anaf_surse; sunt in artefactele OFICIALE ANAF (URL-uri din anaf_surse/versiuni.xml,
# D212_40): lista ACCEPTATA = D212Validator.jar, parameters/Parameters_v7._listaCateg_venit (pachetul v9, in
# vigoare pt 2025); SEMNIFICATIA = D212Pdf.jar, d212/Pdf_v8 (casuta `categ_venit_N` se bifeaza cand codul
# == valoarea; eticheta tiparita langa ea). Verificat 01.10.2026.
CATEG_VENIT_CAP11 = {
    1016: "1. Activități independente", 1003: "2. Drepturi de proprietate intelectuală",
    1015: "3. Cedarea folosinței bunurilor (altele decât cele de la pct.4)",
    1006: "4. Cedarea folosinței bunurilor, în scop turistic", 1009: "5. Activități agricole",
    1010: "6. Silvicultură", 1011: "7. Piscicultură",
    1012: "8. Transferul titlurilor de valoare și orice alte operațiuni cu instrumente financiare",
    1021: "9. Alte surse (art.114 CF)", 1022: "9. Alte surse (art.114 CF)",
    1023: "9. Alte surse (art.114 CF)", 1024: "9. Alte surse (art.114 CF)",
}
CATEG_ACTIVITATI_INDEPENDENTE = 1016
DET_VEN_NET_SISTEM_REAL = 1          # Pdf_v8: det_ven_net_1 = „1. Sistem real", _2 = „2. Cote forfetare"
FORMA_ORG_INDIVIDUAL = 1             # Pdf_v8: forma_org_1/2/3 = Individual / Asociere / Transparenta fiscala

#: Pierderea reportata se compenseaza in limita a 70% din venitul net anual (rd.6 din §3.5.11). Procent intreg.
PROCENT_COMPENSARE_PIERDERE = _anc("d212.PROCENT_COMPENSARE_PIERDERE", Decimal("70"), _Tm(
    "CF", art="118", alin="4", data_in="2024-01-01", verificat_la="2026-10-01", de_cine="Code/D212-E2",
    nivel_sursa="MO", url="anaf_surse/cod_fiscal_227_2015_consolidat.html",
    text_citat=("se reportează și se compensează de către contribuabil în limita a 70% din veniturile nete "
                "anuale, obținute din aceeași sursă de venit în următorii 5 ani fiscali consecutivi"),
    lant_acte="alin.(4) modificat de OUG 115/2023 art.LIII pct.70 (de la 01.01.2024); aplicat de instrucțiunile "
              "D212 (OPANAF 2736/2025) pct.3.5.11 rd.6"))
TEMEI_COMPENSARE_PIERDERE = _temei_anc("d212.PROCENT_COMPENSARE_PIERDERE")
#: Randurile cap11 pt activitate individuala in sistem real.
TEMEI_RANDURI_CAP11 = _Tm(
    "OPANAF", 2736, 2025, data_in="2026-01-01", verificat_la="2026-10-01", de_cine="Code/D212-E2",
    nivel_sursa="MO", url="anaf_surse/instructiuni_d212_2736_2025.txt",
    text_citat=("Rd.3 \"Venit net anual\" - se înscrie suma reprezentând diferența dintre venitul brut (rd. 1) și "
                "cheltuielile aferente deductibile (rd.2)"),
    lant_acte="instrucțiuni de completare formular 212, pct.3.5.11 (rd.1-rd.9); rd.8 și rd.9 (pentru venit net) nu se "
              "completează — impozitul se stabilește în secțiunea 4 a capitolului I")


def cap11_sistem_real(venit_brut, chelt_deduc, pierdere_precedenta=0, caen=None, nr_zile_scutite=0):
    """Subsectiunea I.1.1 pt activitate INDIVIDUALA in sistem real, rand cu rand dupa instructiunile
    D212 (OPANAF 2736/2025 pct.3.5.11). Sume in lei intregi (half-up).

      rd.1 venit_brut · rd.2 chelt_deduc
      rd.3 venit_net_anual = rd.1 - rd.2 — NUMAI daca venitul brut > cheltuielile
      rd.4 pierdere        = rd.2 - rd.1 — NUMAI daca cheltuielile > venitul brut
      rd.5 pierdere_precedenta (reportata din anii precedenti, data de contabil)
      rd.6 pierdere_compensata = min(rd.5, 70% x rd.3) — NUMAI cand exista venit net (CF art.118 alin.(4))
      rd.7 venit_recalculat = rd.3 - rd.6
      rd.8 venit_redus     — „rubrica nu se completeaza"
      rd.9 impozit11       = 0 la pierdere sau venit net zero; altfel „nu se completeaza"
    """
    vb, cd, pp = _lei(venit_brut), _lei(chelt_deduc), _lei(pierdere_precedenta)
    if vb < 0 or cd < 0 or pp < 0:
        raise ValueError("Venitul brut, cheltuielile și pierderea reportată nu pot fi negative.")
    c = {"categ_venit": CATEG_ACTIVITATI_INDEPENDENTE, "det_ven_net": DET_VEN_NET_SISTEM_REAL,
         "forma_org": FORMA_ORG_INDIVIDUAL, "venit_brut": vb, "chelt_deduc": cd}
    if caen:
        c["caen"] = str(caen).strip()
    scut = int(nr_zile_scutite or 0)
    if not 0 <= scut <= 366:   # refuz de FORMĂ: număr de zile în afara anului
        raise ValueError("Zilele scutite trebuie să fie între 0 și numărul de zile ale anului.")
    if scut:
        # rd.A.9 (instrucțiuni pct.3.5.6); venitul redus se calculează în Secțiunea 4 rd.5 (oblig_realizat)
        c["nr_zile_scutite"] = scut
    if pp:
        c["pierdere_precedenta"] = pp
    if vb > cd:
        net = vb - cd
        comp = min(pp, _lei(Decimal(net) * PROCENT_COMPENSARE_PIERDERE / 100))
        c["venit_net_anual"] = net
        if pp:
            c["pierdere_compensata"] = comp
        c["venit_recalculat"] = net - comp
    else:
        if cd > vb:
            c["pierdere"] = cd - vb
        c["impozit11"] = 0
    return c


# ── CAP12 (Subsectiunea a 2-a lit.A — activitati independente impuse pe baza de NORME DE VENIT) ────────────────
# [D212 Etapa 3, 02.10.2026] Atributele = clasa Cap12 din D212Validator.jar v9 (15, toate optionale, element REPETABIL —
# „Se completează câte o secțiune pentru fiecare activitate și loc de desfășurare a activității”, instructiuni pct.19.1
# A2). validateCap12 e goala; R8: bifa112=1 => cap12 exista. Corespondenta cu randurile (D212Pdf Pdf_v8): real_norma_venit
# = rd.7, real_ajustare = rd.8, real_venit_net_anual = rd.9, real_venit_impozit = rd.9.1, real_impozit = impozitul anual.
#: Cota impozitului pe norma de venit (procent intreg).
COTA_IMPOZIT_NORMA = _anc("d212.COTA_IMPOZIT_NORMA", Decimal("10"), _Tm(
    "CF", art="69^2", alin="1", data_in="2025-01-01", verificat_la="2026-10-02", de_cine="Code/D212-E3",
    nivel_sursa="MO", url="anaf_surse/cod_fiscal_227_2015_consolidat.html",
    text_citat="prin aplicarea cotei de 10% asupra normei anuale de venit ajustate",
    lant_acte="art.69^2 introdus de OUG 128/2024 (veniturile din 2025): impozitul anual se stabilește pe baza Declarației "
              "unice; aplicat de instrucțiunile D212 (OPANAF 2736/2025) pct.19.1 lit.C rd.2 (10% asupra totalului)"))
#: Numitorul proratarii normei pe perioada de activitate (zile), indiferent de anul bisect.
ZILE_AN_NORMA = _anc("d212.ZILE_AN_NORMA", 365, _Tm(
    "OPANAF", 2736, 2025, data_in="2026-01-01", verificat_la="2026-10-02", de_cine="Code/D212-E3",
    nivel_sursa="MO", url="anaf_surse/ordin_2736_2025__anexa_306268.html",
    text_citat="la 365 de zile, iar rezultatul se înmulțește cu numărul zilelor de activitate",
    lant_acte="instrucțiuni formular 212, Subsecțiunea a 2-a lit.A rd.9; CF art.69 alin.(5): „norma de venit aferentă "
              "acelei activități se reduce proporțional” pentru perioadele mai mici decât anul calendaristic"))
FORME_ORG_NORMA = {1: "Individual", 2: "Asociere fără personalitate juridică"}   # validator: interval [1,2]


# ── CAP11 PE CATEGORII (Subsecțiunea I.1.1 pentru veniturile fără date în aplicație) ─────────────────────────────────
# [D212 Etapa 5, 02.10.2026] Contabilul dă datele sursei (venitul brut, cheltuielile reale, câștigul net, venitul
# impozabil); rândurile le calculează aplicația, după instrucțiunile D212 (OPANAF 2736/2025) Subsecțiunea 1 pct.4-9.
# Secțiunea cap11 se REPETĂ în validatorul instalat (J13.0.1, fără reguli încrucișate pe cap11; probat pe DUK 02.10.2026:
# două secțiuni = valid), câte una pe sursă de venit. Corespondența cod -> literă la alte surse (1021 lit.k^1, 1022 lit.l,
# 1023 lit.m, 1024 celelalte) e tipărită în D212Pdf.jar Pdf_v5/Pdf_v6 („Alte surse, venituri prevazute la art.114 alin.(2)
# lit.k1) din Codul fiscal" ...); Pdf_v8 le bifează pe toate în căsuța 9.
#: Anii de venit cu regulile pe categorii verificate la sursă: instrucțiunile 2736/2025 sunt pentru veniturile 2025; de la
#: veniturile 2026, Legea 239/2025 art.XII pct.7-14 schimbă cedarea folosinței (CF art.83-87) și alte surse (art.114-116),
#: iar formularul pentru veniturile 2026 nu e publicat. Un an se adaugă DUPĂ verificarea lui, nu înainte.
ANI_CATEGORII = (2025,)
#: Cota forfetară de cheltuieli la drepturile de proprietate intelectuală (procent întreg).
COTA_FORFETARA_DPI = _anc("d212.COTA_FORFETARA_DPI", Decimal("40"), _Tm(
    "CF", art="72^1", alin="1", data_in="2018-03-23", verificat_la="2026-10-02", de_cine="Code/D212-E5",
    nivel_sursa="MO", url="anaf_surse/cod_fiscal_227_2015_consolidat.html",
    text_citat="prin scăderea din venitul brut a cheltuielilor determinate prin aplicarea cotei de 40% asupra venitului brut",
    lant_acte="art.72^1 introdus de OUG 18/2018; aplicat de instrucțiunile D212 (OPANAF 2736/2025) pct.4.5.9 rd.2"))
#: Cota forfetară de cheltuieli la cedarea folosinței bunurilor (procent întreg).
COTA_FORFETARA_CEDARE = _anc("d212.COTA_FORFETARA_CEDARE", Decimal("20"), _Tm(
    "CF", art="84", alin="3", data_in="2024-01-01", verificat_la="2026-10-02", de_cine="Code/D212-E5",
    nivel_sursa="MO", url="anaf_surse/cod_fiscal_227_2015_consolidat.html",
    text_citat="se stabilește prin deducerea din venitul brut a cheltuielilor determinate prin aplicarea cotei de 20% asupra venitului brut",
    lant_acte="cota de 20% din OUG 115/2023 art.LIII (veniturile 2024+); alin.(3) reformulat de Legea 239/2025 art.XII pct.8 "
              "(veniturile 2026), cota neschimbată; aplicat de instrucțiunile D212 (OPANAF 2736/2025) pct.5.6.6 rd.2"))
#: Cota de impozit pe venitul fiecărei surse din fiecare categorie (procent întreg).
COTA_IMPOZIT_VENIT = _anc("d212.COTA_IMPOZIT_VENIT", Decimal("10"), _Tm(
    "CF", art="64", alin="1", data_in="2018-01-01", verificat_la="2026-10-02", de_cine="Code/D212-E5",
    nivel_sursa="MO", url="anaf_surse/cod_fiscal_227_2015_consolidat.html",
    text_citat="Cota de impozit este de 10% și se aplică asupra venitului impozabil corespunzător fiecărei surse din fiecare categorie",
    lant_acte="lit.a^1) DPI, c) cedarea folosinței, d) investiții, f) agricole, h) alte surse; la alte surse și art.116 alin.(2) "
              "(„prin aplicarea cotei de 10%”); aplicat de instrucțiunile D212 (OPANAF 2736/2025) pct.4-9, rd.9"))
#: Pierderea netă din investiții se recuperează din câștigul net, în limita a 70% (procent întreg) — normă proprie, alta
#: decât art.118 alin.(4) (activitățile), aceeași cifră.
PROCENT_COMPENSARE_INVESTITII = _anc("d212.PROCENT_COMPENSARE_INVESTITII", Decimal("70"), _Tm(
    "CF", art="119", alin="2", data_in="2024-01-01", verificat_la="2026-10-02", de_cine="Code/D212-E5",
    nivel_sursa="MO", url="anaf_surse/cod_fiscal_227_2015_consolidat.html",
    text_citat="se recuperează în limita a 70% din câștigurile nete anuale obținute în următorii 5 ani fiscali consecutivi",
    lant_acte="alin.(2) modificat de OUG 115/2023 art.LIII pct.71; aplicat de instrucțiunile D212 (OPANAF 2736/2025) pct.7.3.2 rd.6"))

CATEG_DPI, CATEG_CEDARE, CATEG_TURISTIC, CATEG_INVESTITII = 1003, 1015, 1006, 1012
CATEG_AGRICOLE = (1009, 1010, 1011)
CATEG_ALTE_SURSE = (1021, 1022, 1023, 1024)
DET_VEN_NET_FORFETAR = 2
#: Categoriile pentru care persoana cu handicap grav sau accentuat e scutită de impozit (CF art.60 pct.1 lit.a), a^1), d)).
CATEG_SCUTIRE_HANDICAP = (CATEG_ACTIVITATI_INDEPENDENTE, CATEG_DPI) + CATEG_AGRICOLE
#: Categoriile introduse de contabil pe ecran (activitățile independente vin din registrul RIP).
CATEG_MANUALE = (CATEG_DPI, CATEG_CEDARE, CATEG_TURISTIC) + CATEG_AGRICOLE + (CATEG_INVESTITII,) + CATEG_ALTE_SURSE


def _procent(suma, cota):
    return _lei(Decimal(suma) * cota / 100)


def redus_handicap(valoare, zile_scutite, an):
    """Venitul impozabil redus pentru persoana cu handicap grav sau accentuat (cap11 rd.8, I.4 rd.5, I.5 rd.4).

    Temei: CF art.60 pct.1 (scutirea) + normele HG 1/2016 la art.69, alin.(11): venitul net „se reduce, de către
    contribuabil, proporțional cu numărul de zile calendaristice pentru care venitul este scutit”. INTERPRETARE CU TEMEI:
    proporția se raportează la zilele calendaristice ale ANULUI (365/366) — textul spune „zile calendaristice” și nu fixează
    numitorul; alternativă respinsă: 365 fix (aceea e regula proprie normei, rd.9 „la 365 de zile”). De reconfirmat dacă
    apare o normă care transează."""
    zile = 366 if calendar.isleap(int(an)) else 365
    return _lei(Decimal(valoare) * (zile - int(zile_scutite)) / zile)


def cap11_categorie(a, an):
    """O secțiune I.1.1 pentru o categorie fără date în aplicație, rând cu rând (instrucțiunile D212, Subsecțiunea 1):

      DPI 1003, cote forfetare (pct.4.5.9): rd.2 = 40% x rd.1 (moștenitori / drept de suită, pct.4.5.10: sumele cuvenite
          organismelor de gestiune, fără cotă); rd.7 = rd.3; rd.8 redus (handicap); rd.9 = 10% x rd.7 (sau rd.8)
      DPI 1003, sistem real (pct.4.5.7): rd.1-rd.7 ca la activitățile independente; rd.9 = 0 la pierdere, altfel
          „nu se completează” — impozitul se stabilește în Secțiunea 5
      cedarea folosinței 1015 (pct.5.6.6): rd.2 = 20% x rd.1; rd.7 = rd.3; rd.9 = 10% x rd.7
      închiriere în scop turistic 1006 (pct.5.7.3): sistem real, pierderea e definitivă (fără rd.5/rd.6); rd.9 = 10% x rd.7
      agricole 1009-1011 (pct.6.6.10): sistem real, compensare 70%; rd.8 redus; rd.9 = 10% x rd.7 (sau rd.8), 0 la pierdere
      investiții 1012 (pct.7.3.2): rd.3 câștig / rd.4 pierdere netă, rd.6 = min(rd.5, 70% x rd.3); rd.9 = 10% x rd.7
      alte surse 1021-1024 (pct.9.2.2): rd.7 venitul impozabil, rd.9 = 10% x rd.7
    `a`: {categ_venit, det_ven_net? (DPI: 1 real / 2 forfetar), venit_brut?, chelt_deduc?, pierdere_precedenta?,
          castig_net? (1012, negativ = pierdere), venit_impozabil? (alte surse), fara_cota_forfetara? (DPI), forma_org?,
          caen?, sediu?, nr_doc?, data_doc?, data_incep?, data_sf?, nr_zile_scutite?}. Sume în lei întregi (half-up)."""
    an = int(an)
    try:
        cat = int(a.get("categ_venit"))
    except (TypeError, ValueError):
        cat = None
    if cat not in CATEG_MANUALE:   # refuz de FORMĂ: codul în afara listei de pe ecran
        raise ValueError("D212: categoria de venit %r nu se introduce aici (activitățile independente vin din registrul RIP); "
                         "categoriile: %s." % (a.get("categ_venit"), ", ".join(str(c) for c in CATEG_MANUALE)))
    if an not in ANI_CATEGORII:
        raise ValueError("D212: %s — regulile pe categorii sunt verificate pentru veniturile %s (instrucțiunile OPANAF 2736/2025); "
                         "pentru %d, Legea 239/2025 art.XII schimbă cedarea folosinței (CF art.83-87) și alte surse (art.114-116), "
                         "iar ANAF n-a publicat formularul. Se declară pe formularul ANAF."
                         % (CATEG_VENIT_CAP11[cat], "/".join(map(str, ANI_CATEGORII)), an))
    eticheta = CATEG_VENIT_CAP11[cat]
    vb, cd, pp = _lei(a.get("venit_brut")), _lei(a.get("chelt_deduc")), _lei(a.get("pierdere_precedenta"))
    if vb < 0 or cd < 0 or pp < 0:   # refuz de FORMĂ: sume negative
        raise ValueError("D212 %s: venitul brut, cheltuielile și pierderea reportată nu pot fi negative." % eticheta)
    scut = int(a.get("nr_zile_scutite") or 0)
    if scut and cat not in CATEG_SCUTIRE_HANDICAP:
        raise ValueError("D212 %s: zilele scutite nu se aplică — scutirea pentru handicap grav sau accentuat (CF art.60 pct.1) "
                         "privește activitățile independente, drepturile de proprietate intelectuală și activitățile agricole."
                         % eticheta)
    if not 0 <= scut <= 366:   # refuz de FORMĂ: număr de zile în afara anului
        raise ValueError("D212 %s: zilele scutite trebuie să fie între 0 și numărul de zile ale anului." % eticheta)
    if cat == CATEG_DPI:
        det = int(a.get("det_ven_net") or DET_VEN_NET_FORFETAR)
        if det not in (DET_VEN_NET_SISTEM_REAL, DET_VEN_NET_FORFETAR):   # refuz de FORMĂ: validatorul are două căsuțe
            raise ValueError("D212 %s: determinarea venitului net %r — 1 sistem real, 2 cote forfetare." % (eticheta, det))
    elif cat == CATEG_CEDARE:
        det = DET_VEN_NET_FORFETAR                      # pct.5.6.2 „se bifează căsuța cote forfetare de cheltuieli”
    elif cat == CATEG_TURISTIC or cat in CATEG_AGRICOLE:
        det = DET_VEN_NET_SISTEM_REAL                   # pct.5.7.2 / 6.6.2 „se bifează căsuța sistem real”
    else:
        det = None                                      # investiții, alte surse: rd.2 nu se completează (pct.7.3, 9.2)
    c = {"categ_venit": cat}
    if det:
        c["det_ven_net"] = det
    if cat == CATEG_DPI or cat in CATEG_AGRICOLE:
        forma = int(a.get("forma_org") or FORMA_ORG_INDIVIDUAL)
        if forma not in FORME_ORG_NORMA:   # refuz de FORMĂ: pct.4.5.3 / 6.6.3 au două căsuțe
            raise ValueError("D212 %s: forma de organizare %r — 1 individual, 2 asociere." % (eticheta, a.get("forma_org")))
        c["forma_org"] = forma
    for k, kx in (("caen", "caen"), ("sediu", "descriere_sediu_bun"), ("nr_doc", "nr_doc_autoriz")):
        if str(a.get(k) or "").strip():
            c[kx] = str(a[k]).strip()
    ian1, dec31 = _dt.date(an, 1, 1), _dt.date(an, 12, 31)
    for k, kx, camp in (("data_doc", "data_doc_autoriz", "data documentului"), ("data_incep", "data_incep", "data începerii"),
                        ("data_sf", "data_sf", "data încetării")):
        d = _data(a.get(k), camp)
        if d is None:
            continue
        if kx != "data_doc_autoriz" and not ian1 <= d <= dec31:
            raise ValueError("D212 %s: %s (%s) nu e în anul %d — rubrica se completează numai dacă evenimentul se produce în "
                             "cursul anului (OPANAF 2736/2025, instrucțiuni rd.8/rd.9)." % (eticheta, camp, d, an))
        c[kx] = _dmy(d)
    if scut:
        c["nr_zile_scutite"] = scut

    if det == DET_VEN_NET_FORFETAR:
        if pp:   # refuz de FORMĂ: la cote forfetare nu există rd.5 (pct.4.5.9 / 5.6.6 enumeră rd.1, 2, 3, 7, 9)
            raise ValueError("D212 %s: la cote forfetare nu se reportează pierderi." % eticheta)
        if cat == CATEG_DPI and a.get("fara_cota_forfetara"):
            if cd > vb:   # refuz de FORMĂ: sumele cuvenite organismelor de gestiune nu pot depăși venitul brut
                raise ValueError("D212 %s: sumele cuvenite organismelor de gestiune colectivă depășesc venitul brut." % eticheta)
            ded = cd          # pct.4.5.10 / CF art.72^1 alin.(2): „fără aplicarea cotei forfetare de cheltuieli”
        else:
            if cd:   # refuz de FORMĂ: cheltuielile la cote forfetare le stabilește cota, nu contabilul
                raise ValueError("D212 %s: la cote forfetare cheltuielile se calculează din venitul brut; câmpul se lasă gol."
                                 % eticheta)
            ded = _procent(vb, COTA_FORFETARA_DPI if cat == CATEG_DPI else COTA_FORFETARA_CEDARE)
        net = vb - ded
        c.update(venit_brut=vb, chelt_deduc=ded, venit_net_anual=net, venit_recalculat=net)
        baza = net
        if scut:
            c["venit_redus"] = baza = redus_handicap(net, scut, an)
        c["impozit11"] = _procent(baza, COTA_IMPOZIT_VENIT)
    elif det == DET_VEN_NET_SISTEM_REAL:
        if cat == CATEG_TURISTIC and pp:
            raise ValueError("D212 %s: pierderea din închirierea în scop turistic „reprezintă pierdere definitivă” (OPANAF "
                             "2736/2025, instrucțiuni pct.5.7.3) — nu se reportează." % eticheta)
        c.update(venit_brut=vb, chelt_deduc=cd)
        if pp:
            c["pierdere_precedenta"] = pp
        if vb > cd:
            net = vb - cd
            comp = min(pp, _procent(net, PROCENT_COMPENSARE_PIERDERE))
            c["venit_net_anual"] = net
            if pp:
                c["pierdere_compensata"] = comp
            c["venit_recalculat"] = net - comp
            if cat != CATEG_DPI:      # DPI în sistem real: rd.8/rd.9 nu se completează, impozitul e în Secțiunea 5 (pct.4.5.7)
                baza = net - comp
                if scut:
                    c["venit_redus"] = baza = redus_handicap(baza, scut, an)
                c["impozit11"] = _procent(baza, COTA_IMPOZIT_VENIT)
        else:
            if cd > vb:
                c["pierdere"] = cd - vb
            c["impozit11"] = 0
    elif cat == CATEG_INVESTITII:
        if vb or cd:   # refuz de FORMĂ: pct.7.3.2 începe de la rd.3 (câștigul net), rd.1/rd.2 nu există
            raise ValueError("D212 %s: se introduce câștigul net anual (pierderea, cu minus), nu venitul brut și cheltuielile."
                             % eticheta)
        cn = _lei(a.get("castig_net"))
        if pp:
            c["pierdere_precedenta"] = pp
        if cn > 0:
            comp = min(pp, _procent(cn, PROCENT_COMPENSARE_INVESTITII))
            c["venit_net_anual"] = cn
            if pp:
                c["pierdere_compensata"] = comp
            c["venit_recalculat"] = cn - comp
            c["impozit11"] = _procent(cn - comp, COTA_IMPOZIT_VENIT)
        else:
            if cn < 0:
                c["pierdere"] = -cn
            c["impozit11"] = 0
    else:
        if vb or cd or pp:   # refuz de FORMĂ: pct.9.2.2 cere doar rd.7 (venitul impozabil) și rd.9
            raise ValueError("D212 %s: se introduce venitul impozabil (rd.7), nu venitul brut, cheltuielile sau pierderi." % eticheta)
        vi = _lei(a.get("venit_impozabil"))
        if vi <= 0:   # refuz de FORMĂ: secțiune fără venit
            raise ValueError("D212 %s: venitul impozabil lipsește." % eticheta)
        c.update(venit_recalculat=vi, impozit11=_procent(vi, COTA_IMPOZIT_VENIT))
    return c



# ── OBLIG_REALIZAT (Secțiunile 3, 4 și 7 ale cap.I — CAS, CASS, impozitul în sistem real, sumarul) ──────────────
# [D212 Etapa 4, 02.10.2026] Atributele = clasa Oblig_realizat din D212Validator.jar v9 (fără reguli încrucișate, doar
# intervale); corespondența atribut -> rând = D212Pdf.jar Pdf_v8 (formularul validatorului): I.3.1 CAS rd.1-5, I.3.2.1
# CASS rd.1-5, I.4 rd.1-6 + I.4.1/I.4.2 (contribuțiile deductibile pe pondere, CF art.118 alin.(2^2)/(2^3)), I.7.1-I.7.4.
# Rândurile urmează instrucțiunile D212 (OPANAF 2736/2025) Secțiunile 3, 4 și 7; CAS și CASS vin din `d212_engine`
# (aceeași sursă ca fișa RIP), nu dintr-o a doua formulă.
def _pondere(parte, total):
    """Ponderea (rd.1/rd.2) cu 4 zecimale, ca text (validatorul o citește ca valoare reală)."""
    return "%.4f" % (Decimal(parte) / Decimal(total)) if total else "0.0000"


def oblig_realizat(cap11, cap12, an, optiune_cas=False, exceptie_minim_cass=None, alte_cass=None):
    """Secțiunile 3, 4, 5 și 7 din venitul declarat în cap11 (o secțiune pe sursă) și cap12 (normă). Întoarce (secțiune, bife).

    Venitul pentru încadrarea CAS (I.3.1 rd.1, I.4.1/I.5.1 rd.2) = venitul net din activități independente (cap11 rd.3;
    pierderea nu se ia — instrucțiuni pct.49.1.2.4) + normele (cap12 rd.9) + venitul net din drepturi de proprietate
    intelectuală — CF art.148 alin.(3). Venitul pentru CASS 2.1 (I.3.2.1 rd.1) = fără DPI — art.170 alin.(1). DPI, cedarea
    folosinței, investițiile, agricolele și alte surse merg la CASS 2.2, pe trepte — art.170 alin.(2)-(4).
    `alte_cass`: {asociere_pj, dividende_dobanzi, cass_retinuta} — venituri art.155 alin.(1) lit.c)-h) fără secțiune I.1.1
    (impuse la sursă: venitul distribuit din asocieri cu PJ, dividendele/dobânzile nete) și CASS reținută de plătitori
    (art.174^1), date de contabil."""
    from core import d212_engine as _e
    if int(an) not in _e.ANI_VERIFICATI:
        raise ValueError("D212: contribuțiile se calculează doar pentru anii cu plafoane verificate la sursă (%s); pragurile "
                         "din Codul fiscal art.148 și art.170 se raportează la salariul minim al anului — pentru %s verifică-l întâi."
                         % ("/".join(map(str, _e.ANI_VERIFICATI)), an))
    p = _e.plafoane_an(int(an))
    secs = _sectiuni(cap11)

    def _cat(s):
        return int(s.get("categ_venit") or 0)

    def _suma(categorii, camp, filtru=lambda s: True):
        return sum(_lei(s.get(camp) or 0) for s in secs if _cat(s) in categorii and filtru(s))

    def _scutite(categorii):
        return max((int(s.get("nr_zile_scutite") or 0) for s in secs if _cat(s) in categorii), default=0)

    ai = (CATEG_ACTIVITATI_INDEPENDENTE,)
    net_real, recalc = _suma(ai, "venit_net_anual"), _suma(ai, "venit_recalculat")
    real_dpi = lambda s: int(s.get("det_ven_net") or 0) == DET_VEN_NET_SISTEM_REAL   # noqa: E731
    dpi_net = _suma((CATEG_DPI,), "venit_net_anual")
    dpi_real_net = _suma((CATEG_DPI,), "venit_net_anual", real_dpi)
    dpi_recalc = _suma((CATEG_DPI,), "venit_recalculat", real_dpi)
    norme = sum(_lei(c.get("real_venit_net_anual") or 0) for c in _sectiuni(cap12))
    total = net_real + norme                 # art.170 alin.(1): CASS 2.1
    total_cas = total + dpi_net              # art.148 alin.(3): CAS
    o, bife = {}, {}
    if optiune_cas and total_cas < p.cas_prag_min_sm * p.salariu_minim:
        # instrucțiuni pct.46.2 lit.B „sub plafonul minim și optez” — formularul validatorului instalat (J13.0.1, Pdf_v8)
        # are doar căsuțele A1 (12-24 sm) și A2 (>= 24 sm); emiterea opțiunii pe A1 ar declara un venit pe care nu-l are
        raise ValueError("D212: opțiunea pentru CAS sub 12 salarii minime (OPANAF 2736/2025, instrucțiuni pct.46.2, lit.B) nu are "
                         "căsuță în formularul validatorului ANAF instalat (J13.0.1, formularul pentru veniturile 2024); se declară "
                         "pe formularul ANAF.")
    cas = _e.calculeaza_cas(float(total_cas), p, optiune_cas)
    cas_d = _lei(cas["cas"])
    if cas_d:
        # rd.1-rd.5 (instrucțiuni pct.46.3-46.7); căsuța: A1 între 12 și 24 sm, A2 de la 24 sm (pct.46.1)
        o.update(bifa_cas_real=2 if total_cas >= p.cas_prag_max_sm * p.salariu_minim else 1, cas_total_ven=total_cas,
                 cas_baza=_lei(cas["baza"]), cas_datorat=cas_d, cas_dif_plus=cas_d)
        bife["bifa131"] = "1"
    # CASS 2.2 (pct.52.1): venitul cumulat pe categoriile lit.c)-h) -> treapta 6/12/24 sm (CF art.170 alin.(3)-(4))
    x = alte_cass or {}
    asc, divd, ret22 = _lei(x.get("asociere_pj")), _lei(x.get("dividende_dobanzi")), _lei(x.get("cass_retinuta"))
    if asc < 0 or divd < 0 or ret22 < 0:   # refuz de FORMĂ: sume negative
        raise ValueError("D212: veniturile pentru CASS și CASS reținută nu pot fi negative.")
    ven22 = {"cass_ven_dpi": dpi_net, "cass_ven_asc": asc,
             "cass_ven_cfb": _suma((CATEG_CEDARE, CATEG_TURISTIC), "venit_net_anual"),
             "cass_ven_inv": _suma((CATEG_INVESTITII,), "venit_net_anual") + divd,
             "cass_ven_asp": _suma(CATEG_AGRICOLE, "venit_net_anual"),
             "cass_ven_alt": _suma(CATEG_ALTE_SURSE, "venit_recalculat")}
    total22 = sum(ven22.values())
    c22 = _e.calculeaza_cass_alte_venituri(float(total22), p)
    cass22 = _lei(c22["cass"])
    if ret22 > cass22:
        from core import pdf_util
        raise ValueError("D212: CASS reținută de plătitori (%s lei) depășește CASS datorată pe veniturile din DPI, cedarea folosinței, "
                         "investiții, agricole și alte surse (%s lei); formularul validatorului ANAF instalat (J13.0.1) n-are la "
                         "subsecțiunea 2.2 rândul „diferența stabilită în minus” (OPANAF 2736/2025, instrucțiuni pct.52.1.11). Se "
                         "declară pe formularul ANAF." % (pdf_util.bani(ret22), pdf_util.bani(cass22)))
    dif22 = cass22 - ret22
    if cass22:
        # căsuța = treapta (pct.52.1.1-52.1.3); rd.1 tabelul pe categorii; rd.2 baza; rd.3 CASS; rd.4 reținută; rd.5 în plus
        o.update({k: v for k, v in ven22.items() if v})
        o.update(bifa_cass_datorat_dpi=1, bifa_cass_real=c22["treapta"], cass_total_ven=total22, cass_baza=_lei(c22["baza"]),
                 cass_datorat=cass22, cass_dif_plus=dif22)
        if ret22:
            o["cass_retinut"] = ret22
        bife["bifa132"] = "1"
        if exceptie_minim_cass is None:
            # CF art.174 alin.(7) lit.b): diferența până la 6 sm din 2.1 nu se datorează când veniturile lit.c)-h) poartă CASS
            # „la un nivel cel puțin egal cu 6 salarii minime brute pe țară” — rezultă din datele de mai sus, nu din alegere
            exceptie_minim_cass = "venituri_c_h"
    cass = _e.calculeaza_cass(float(total), p, False, exceptie_minim_cass)
    cass_d = _lei(cass["cass"])
    if cass_d:
        # rd.1-rd.3 + diferența în plus (pct.49.1.1-49.1.7; nu există CASS reținută la sursă pe activități independente)
        o.update(bifa_cass_datorat_ai=1, cass_total_ven_ai=total, baza_cass_datorat_ai=_lei(cass["baza"]),
                 cass_datorat_ai=cass_d, cass_dif_plus_ai=cass_d)
        bife["bifa132"] = "1"
    # impozitul stabilit direct în I.1.1 (rd.9 al fiecărei secțiuni) și pe norme (pct.56.1 rd.1, prima și a doua liniuță)
    impozit = sum(_lei(s.get("impozit11") or 0) for s in secs) + sum(_lei(c.get("real_impozit") or 0) for c in _sectiuni(cap12))
    if net_real:
        # I.4.1: CAS deductibilă = pondere sistem real (în venitul art.148) x CAS datorată (CF art.118 alin.(2^2))
        cas_ded = _lei(Decimal(cas_d) * net_real / total_cas) if total_cas else 0
        # I.4.2: CASS deductibilă = pondere x CASS datorată, sau x CASS calculată pe venit sub 6 sm (rd.5, art.174 alin.(1))
        sub_minim = cass["diferenta_minim"] > 0
        baza_ded = _lei(cass["cass_pe_venit"]) if sub_minim else cass_d
        cass_ded = _lei(Decimal(baza_ded) * net_real / total) if total else 0
        o.update(real_cas_venit_net_ai=net_real, real_cas_total_ven_ai=total_cas,
                 real_cas_pondere_ai=_pondere(net_real, total_cas), real_cas_datorata_ai=cas_d, real_cas_deductibila_ai=cas_ded,
                 real_cass_venit_net_ai=net_real, real_cass_total_ven_ai=total,
                 real_cass_pondere_ai=_pondere(net_real, total), real_cass_datorata_ai=cass_d,
                 real_cass_deductibila_ai=cass_ded)
        if sub_minim:
            o["real_cass_calculata_ai"] = baza_ded
        # I.4 rd.1-rd.6: deducerile nu pot depăși venitul net recalculat (pct.53 rd.4)
        ded_cas, ded_cass = min(cas_ded, recalc), min(cass_ded, max(0, recalc - min(cas_ded, recalc)))
        impozabil = recalc - ded_cas - ded_cass
        o.update(real_venit_net_recalculat_ai=recalc, real_venit_net_impozabil_ai=impozabil)
        scut = _scutite(ai)
        if scut:
            # rd.5 „redus proporțional cu numărul de zile calendaristice pentru care venitul este scutit” (pct.53)
            o["real_venit_net_impozabil_redus_ai"] = impozabil = redus_handicap(impozabil, scut, an)
        # cota din motor (aceeași sursă ca fișa RIP): CF art.64 alin.(1) lit.a) „Cota de impozit este de 10%”
        imp_real = _lei(Decimal(impozabil) * Decimal(str(p.impozit_cota)))
        # rd.2/rd.3 (contribuțiile deductibile) n-au atribut propriu în XML: sunt rd.5 din I.4.1 / rd.6 din I.4.2
        o["real_impozit_datorat_ai"] = imp_real
        bife["bifa14"] = "1"
        impozit += imp_real
    if dpi_real_net:
        # Secțiunea 5 (pct.54): DPI în sistem real; 5.1 CAS deductibilă = pondere DPI (în venitul art.148) x CAS datorată
        # (CF art.118 alin.(2^1)); rd.2 nu poate depăși venitul net recalculat
        cas_ded_dpi = _lei(Decimal(cas_d) * dpi_real_net / total_cas) if total_cas else 0
        ded = min(cas_ded_dpi, dpi_recalc)
        impozabil_dpi = dpi_recalc - ded
        o.update(real_cas_venit_net_dpi=dpi_real_net, real_cas_total_ven_dpi=total_cas,
                 real_cas_pondere_dpi=_pondere(dpi_real_net, total_cas), real_cas_datorata_dpi=cas_d,
                 real_cas_deductibila_dpi=cas_ded_dpi, real_venit_net_recalculat_dpi=dpi_recalc, real_cas_dpi=ded,
                 real_venit_net_impozabil_dpi=impozabil_dpi)
        scut = _scutite((CATEG_DPI,))
        if scut:
            o["real_venit_net_impozabil_redus_dpi"] = impozabil_dpi = redus_handicap(impozabil_dpi, scut, an)
        imp_dpi = _procent(impozabil_dpi, COTA_IMPOZIT_VENIT)
        o["real_impozit_datorat_dpi"] = imp_dpi
        bife["bifa15"] = "1"
        impozit += imp_dpi
    # I.7 sumarul (pct.56): impozitul, CAS, CASS 2.1 și 2.2 stabilite în plus, diferența de plată
    o.update(oblimpoz_real_total=impozit, oblimpoz_real_dif_deplata=impozit, oblcas_real_difPlus=cas_d,
             oblcass_real_difPlus_ai=cass_d, impozit_venit_plus=impozit, cas_plus=cas_d, cass_plus=cass_d + dif22,
             dif_de_plata=impozit + cas_d + cass_d + dif22)
    if dif22:
        o["oblcass_real_difPlus_dpi"] = dif22
    return o, bife


def _dmy(d):
    """Data în formatul XML ANAF (dd.MM.yyyy), aritmetic — ca la d108/d177 (nu e afișare, e câmp de structură)."""
    return "%02d.%02d.%04d" % (d.day, d.month, d.year)


def _data(v, camp):
    """Data din formular (AAAA-LL-ZZ sau ZZ.LL.AAAA) -> date; None daca lipseste."""
    if v in (None, ""):
        return None
    t = str(v).strip()
    for fmt in ("%Y-%m-%d", "%d.%m.%Y"):
        try:
            return _dt.datetime.strptime(t[:10], fmt).date()
        except ValueError:
            continue
    raise ValueError("D212 normă: %s %r nu e o dată (AAAA-LL-ZZ)." % (camp, v))   # refuz de FORMĂ — fără temei legal


def cap12_norma(a, an):
    """O secțiune cap12 (o activitate, un loc) din datele contabilului, rând cu rând după instrucțiunile D212 (OPANAF
    2736/2025, Subsecțiunea a 2-a lit.A). Sume în lei întregi (half-up).

      rd.7 real_norma_venit   = norma anuală publicată de DGRFP pentru locul activității (dată de contabil)
      rd.8 real_ajustare      = norma ajustată cu coeficienții de corecție (dată de contabil, opțional)
      rd.9 real_venit_net_anual = rd.8 (dacă e completat) altfel rd.7; la început/încetare/întrerupere în an:
                                 „raportarea … la 365 de zile, iar rezultatul se înmulțește cu numărul zilelor de activitate”
      rd.9.1 real_venit_impozit = rd.9 redus proporțional cu zilele scutite (handicap grav/accentuat). INTERPRETARE CU
                                 TEMEI: aceeași zi-normă (normă / 365) ca la rd.9 — zilele scutite ies din zilele de activitate;
                                 alternativă respinsă: o a doua proporție peste rd.9 (numitor diferit pe aceeași secțiune).
      real_impozit            = 10% × rd.9.1 (CF art.69^2 alin.(1))
    `a`: {norma, norma_ajustata?, data_incep?, data_sf?, zile_intrerupere?, nr_zile_scutite?, forma_org?, caen?,
          sediu?, nr_doc_autoriz?, data_doc_autoriz?, data_susp?}."""
    an = int(an)
    norma = _lei(a.get("norma"))
    if norma <= 0:
        raise ValueError("D212 normă: norma anuală de venit (rd.7) lipsește — se ia din lista DGRFP pentru locul activității.")
    ajust = _lei(a.get("norma_ajustata")) if a.get("norma_ajustata") not in (None, "") else None
    if ajust is not None and ajust < 0:
        raise ValueError("D212 normă: norma ajustată (rd.8) nu poate fi negativă.")
    baza = ajust if ajust is not None else norma
    inc, sf = _data(a.get("data_incep"), "data începerii"), _data(a.get("data_sf"), "data încetării")
    ian1, dec31 = _dt.date(an, 1, 1), _dt.date(an, 12, 31)
    for d, camp in ((inc, "data începerii"), (sf, "data încetării")):
        if d is not None and not (ian1 <= d <= dec31):
            raise ValueError("D212 normă: %s (%s) nu e în anul %d — se completează numai dacă evenimentul e în anul de "
                             "impunere (OPANAF 2736/2025, instrucțiuni rd.3/rd.4: „numai dacă evenimentele respective se produc în "
                             "cursul anului”)." % (camp, d, an))
    start, end = inc or ian1, sf or dec31
    if end < start:
        raise ValueError("D212 normă: data încetării e înaintea datei începerii.")   # refuz de FORMĂ (coerența datelor)
    intrerupere = int(a.get("zile_intrerupere") or 0)
    scutite = int(a.get("nr_zile_scutite") or 0)
    zile_contract = (end - start).days + 1
    if intrerupere < 0 or scutite < 0 or intrerupere > zile_contract:   # refuz de FORMĂ: numere de zile în afara perioadei
        raise ValueError("D212 normă: zilele de întrerupere/scutire trebuie să fie între 0 și zilele de activitate (%d)."
                         % zile_contract)
    zile_act = zile_contract - intrerupere
    if scutite > zile_act:   # refuz de FORMĂ: rd.6 nu poate depăși zilele de activitate pe care le reduce
        raise ValueError("D212 normă: zilele scutite (%d) depășesc zilele de activitate (%d)." % (scutite, zile_act))
    an_intreg = inc is None and sf is None and intrerupere == 0
    zi = Decimal(baza) / Decimal(ZILE_AN_NORMA)
    # an întreg -> rd.9 = norma (lit.a); altfel norma/365 × zilele de activitate (lit.b/c), cel mult norma (an bisect)
    net = baza if an_intreg else min(baza, _lei(zi * zile_act))
    if not scutite:
        impozabil = net
    elif an_intreg:
        impozabil = _lei(Decimal(baza) - zi * scutite)
    else:
        impozabil = _lei(zi * (zile_act - scutite))
    forma = int(a.get("forma_org") or 1)
    if forma not in FORME_ORG_NORMA:   # refuz de FORMĂ: valoarea în afara intervalului validatorului [1,2]
        raise ValueError("D212 normă: forma de organizare %r — 1 individual, 2 asociere." % a.get("forma_org"))
    c = {"norma_forma_org": forma, "real_norma_venit": norma, "real_venit_net_anual": net,
         "real_venit_impozit": impozabil,
         "real_impozit": _lei(Decimal(impozabil) * COTA_IMPOZIT_NORMA / 100)}
    if ajust is not None:
        c["real_ajustare"] = ajust
    if scutite:
        c["norma_nr_zile_scutite"] = scutite
    for k, kx in (("caen", "norma_caen"), ("sediu", "norma_descriere_sediu_bun"), ("nr_doc_autoriz", "norma_nr_doc_autoriz")):
        if str(a.get(k) or "").strip():
            c[kx] = str(a[k]).strip()
    for k, kx in (("data_doc_autoriz", "norma_data_doc_autoriz"), ("data_susp", "norma_data_susp")):
        d = _data(a.get(k), k)
        if d:
            c[kx] = _dmy(d)
    if inc:
        c["norma_data_incep"] = _dmy(inc)
    if sf:
        c["norma_data_sf"] = _dmy(sf)
    return c


# Flag-uri (bife) de pe radacina, implicit 0, suprascriabile din `manual`.
_BIFE = ["bifa_succesor", "anulare_litA", "anulare_litB", "bifa_conformare", "bifa111",
         "bifa112", "bifa113", "bifa121", "bifa122", "bifa131", "bifa132", "bifa14", "bifa15"]
_BIFE_OPT = ["bifa16", "bifa18"]  # optionale


def _cif(x):
    return _NEDIGIT.sub("", str(x or ""))


def _cnp_valid(cnp):
    cnp = _cif(cnp)
    if len(cnp) != len(_CNP_W) + 1:
        return False
    s = sum(int(cnp[i]) * _CNP_W[i] for i in range(len(_CNP_W)))
    c = s % 11
    c = 1 if c == 10 else c
    return c == int(cnp[len(_CNP_W)])


def _esc(s, lim=None):
    t = ("" if s is None else str(s)).replace("&", "&amp;").replace("<", "&lt;") \
        .replace(">", "&gt;").replace('"', "&quot;").strip()
    return t[:lim] if lim else t


def _lei(x):
    """Rotunjire half-up la leu intreg (D212 lucreaza in lei intregi; campurile _f sunt long)."""
    if x in (None, ""):
        return 0
    q = Decimal(str(x).replace(",", ".")).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return int(q)


def _suma_cifre_cnp(cnp):
    cnp = _cif(cnp)
    return sum(int(d) for d in cnp)


def calcul_d212(manual):
    """totalPlata_A = suma de control (DUK regula R4, ValidatorCode.validateD212).

    Pt `cif` de 13 cifre (CNP): suma celor 13 cifre, MEREU — R4 nu priveste sumele de plata, iar un
    `totalPlata_A` impus din afara care difera e respins de validator, deci nu se accepta.
    Pt `cif` care nu e CNP (nerezident cu cod strain), R4 nu se aplica; ramane suma sumelor de plata
    (`manual['sume_de_plata']`) sau valoarea impusa — NEVERIFICAT pe validator (nerezidentul nu e in perimetru)."""
    cnp = _cif(manual.get("cif"))
    if len(cnp) == 13:
        return {"totalPlata_A": _suma_cifre_cnp(cnp)}
    if manual.get("totalPlata_A") not in (None, ""):
        return {"totalPlata_A": _lei(manual.get("totalPlata_A"))}
    return {"totalPlata_A": sum(_lei(v) for v in (manual.get("sume_de_plata") or []))}


def pull(conn, schema, perioada):
    """D212 e MANUALA pe persoana fizica; firma nu are registru PF. conn poate fi None."""
    return {}


def erori_generare(prof, manual):
    er = []
    if not str(manual.get("nume_c") or "").strip():
        er.append("Lipsă nume/denumire contribuabil (nume_c).")
    if not str(manual.get("adresa_c") or "").strip():
        er.append("Lipsă adresa contribuabil (adresa_c).")
    nerez = str(manual.get("nerezident") or "0").strip()
    if nerez == "1":
        if not _cif(manual.get("cif_str")):
            er.append("Nerezident: lipsă cod fiscal străin (cif_str).")
    else:
        if not _cnp_valid(manual.get("cif")):
            er.append("CNP contribuabil (cif) invalid (13 cifre + cifra de control).")
    an = int(manual.get("an_r") or getattr(prof, "an", 0) or 0)
    if an and an < 2025:
        er.append("an_r %d sub anul minim acceptat de validator (2025)." % an)
    dpi = 0
    for cap11 in _sectiuni(manual.get("cap11")):
        try:
            cv = int(cap11.get("categ_venit"))
        except (TypeError, ValueError):
            cv = None
        if cv not in CATEG_VENIT_CAP11:
            er.append("Capitol cap11: categoria de venit %r nu e în nomenclatorul D212 (%s)."
                      % (cap11.get("categ_venit"), ", ".join(str(k) for k in sorted(CATEG_VENIT_CAP11))))
        dpi += cv == CATEG_DPI
    if dpi > 1:
        er.append("Drepturile de proprietate intelectuală se declară într-o singură secțiune, oricâți plătitori ar fi (OPANAF "
                  "2736/2025, instrucțiuni pct.4.4: „completează o singură subsecțiune în declarație”).")
    for nume in _COPII:
        for cap in _sectiuni(manual.get(nume)):
            straine = set(cap) - _CAMPURI[nume]
            if straine:
                er.append("Capitol %s: câmpuri necunoscute (respinse de validator): %s"
                          % (nume, ", ".join(sorted(straine))))
    return er


def _sectiuni(cap):
    """Un capitol poate fi o secțiune (dict) sau o listă de secțiuni (cap11: o sursă de venit fiecare; cap12: o activitate /
    un loc fiecare)."""
    if not cap:
        return []
    return list(cap) if isinstance(cap, (list, tuple)) else [cap]


def _attr(nume, val, lim=None):
    return '%s="%s"' % (nume, _esc(val, lim))


def build_xml(prof, an, luna, manual, calc=None):
    calc = calc or calcul_d212(manual)
    nerez = str(manual.get("nerezident") or "0").strip()
    h = []
    h.append(_attr("d_rec", manual.get("d_rec", "0")))
    h.append(_attr("rectif1", manual.get("rectif1", "0")))
    h.append(_attr("rectif2", manual.get("rectif2", "0")))
    h.append('totalPlata_A="%d"' % calc["totalPlata_A"])
    h.append(_attr("luna_r", _LUNA_R))
    h.append('an_r="%d"' % int(an))
    for b in _BIFE:
        h.append('%s="%s"' % (b, _esc(manual.get(b, "0"))))
    for b in _BIFE_OPT:
        if manual.get(b) is not None:
            h.append('%s="%s"' % (b, _esc(manual.get(b))))
    if manual.get("bifa_succesor") == "1" and manual.get("cif_succesor"):
        h.append(_attr("cif_succesor", _cif(manual.get("cif_succesor"))))
    # identificare
    h.append(_attr("nume_c", manual.get("nume_c"), 250))
    h.append(_attr("adresa_c", manual.get("adresa_c"), 200))
    for opt, lim in (("telefon_c", 15), ("fax_c", 15), ("email_c", 250)):
        if manual.get(opt):
            h.append(_attr(opt, manual.get(opt), lim))
    h.append(_attr("nerezident", nerez))
    if nerez == "1":
        if manual.get("cif"):
            h.append(_attr("cif", _cif(manual.get("cif"))))
        h.append(_attr("stat_rezidenta", manual.get("stat_rezidenta")))
        h.append(_attr("cif_str", manual.get("cif_str")))
    else:
        h.append(_attr("cif", _cif(manual.get("cif"))))
    if manual.get("cont_bancar"):
        h.append(_attr("cont_bancar", str(manual.get("cont_bancar")).replace(" ", "").upper(), 24))
    # imputernicit / reprezentant (optional)
    if manual.get("den_i"):
        h.append(_attr("den_i", manual.get("den_i"), 250))
        h.append(_attr("cif_i", _cif(manual.get("cif_i"))))
        for opt, lim in (("adresa_i", 200), ("telefon_i", 15), ("fax_i", 15), ("email_i", 250)):
            if manual.get(opt):
                h.append(_attr(opt, manual.get(opt), lim))
    # elemente-copil (capitole), emise cand sunt furnizate in manual
    copii = []
    for nume in _COPII:
        for cap in _sectiuni(manual.get(nume)):
            a = [_attr(k, cap[k]) for k in sorted(_CAMPURI[nume]) if k in cap and cap[k] is not None]
            copii.append("  <%s %s/>" % (nume, " ".join(a)))
    corp = ("\n" + "\n".join(copii) + "\n") if copii else ""
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<d212 xmlns="%s" %s>%s</d212>\n' % (NS, " ".join(h), corp))


@dataclass
class Rezultat212:
    an: int
    total_plata_a: int = 0
    capitole: list = field(default_factory=list)
    avertismente: list = field(default_factory=list)


def cap11_din_rip(conn, schema, an, pierdere_precedenta=0, caen=None, nr_zile_scutite=0):
    """Lantul RIP -> cap11: venitul brut si cheltuielile deductibile din operatiunile VALIDATE ale
    registrului (rip_api.fisa_d212, aceeasi sursa ca fisa afisata pe ecran). Refuza anii cu plafoane
    neverificate (refuzul fisei) si avertizeaza despre ce nu intra in calcul."""
    from core import rip_api
    f = rip_api.fisa_d212(conn, schema, an)
    if f.get("eroare"):
        raise ValueError("D212: fișa RIP nu se poate trage — " + f["eroare"])
    return cap11_sistem_real(f["venit_brut"], f["cheltuieli_deductibile"], pierdere_precedenta, caen, nr_zile_scutite), \
        f.get("avertisment")


def genereaza(conn, schema, perioada, manual=None):
    manual = dict(manual or {})
    an = int(getattr(perioada, "an", None) or manual.get("an_r"))
    avert = []
    if manual.get("din_rip") and not manual.get("cap11"):
        if conn is None:
            raise ValueError("D212: venitul din registrul RIP cere firma (conexiunea lipsește).")
        manual["cap11"], a = cap11_din_rip(conn, schema, an, manual.get("pierdere_precedenta") or 0,
                                           manual.get("caen"), manual.get("nr_zile_scutite_rip") or 0)
        if a:
            avert.append(a)
    if manual.get("venituri"):
        # [D212 Etapa 5] categoriile fără date în aplicație: câte o secțiune I.1.1 pe sursă, lângă cea din registrul RIP
        sectiuni = _sectiuni(manual.get("cap11"))
        for i, x in enumerate(_sectiuni(manual["venituri"]), 1):
            try:
                sectiuni.append(cap11_categorie(x, an))
            except ValueError as e:      # numește venitul vinovat (temeiul, unde există, e în mesajul interior)
                raise ValueError("Venitul %d — %s" % (i, e)) from None
        manual["cap11"] = sectiuni
    if manual.get("cap11"):
        manual["bifa111"] = "1"      # subsectiunea I.1.1 completata (R7 cere si reciproca)
    if manual.get("agricol"):
        # [D212 Etapa 3] Subsecțiunea a 4-a (activități agricole pe normă, CF art.107 alin.(2)) NU are loc în structura
        # validatorului instalat (J13.0.1 = formularul pentru veniturile 2024: niciun atribut agricol, fără bifa114).
        # Nu se emite pe altă subsecțiune și nu se sare tăcut.
        raise ValueError("D212: venitul agricol pe normă (Subsecțiunea a 4-a, CF art.107 alin.(2)) nu se poate încă emite — "
                         "validatorul ANAF instalat (J13.0.1) e al formularului pentru veniturile 2024 și nu are câmpurile "
                         "agricole; ANAF n-a publicat validatorul pentru OPANAF 2736/2025. Se declară pe formularul ANAF.")
    if manual.get("norma"):
        # [D212 Etapa 3] activitățile pe normă (Subsecțiunea a 2-a lit.A): o secțiune cap12 pe activitate / loc
        cap12 = []
        for i, x in enumerate(_sectiuni(manual["norma"]), 1):
            try:
                cap12.append(cap12_norma(x, an))
            except ValueError as e:      # numește activitatea vinovată (temeiul, unde există, e în mesajul interior)
                raise ValueError("Activitatea %d — %s" % (i, e)) from None
        manual["cap12"] = cap12
    if manual.get("cap12"):
        manual["bifa112"] = "1"      # R8: bifa112=1 => cap12 exista (și subsecțiunea se declară completată)
    alte_cass = {k: v for k, v in (manual.get("alte_cass") or {}).items() if v not in (None, "", 0, "0")}
    if (manual.get("cap11") or manual.get("cap12") or alte_cass) and not manual.get("oblig_realizat"):
        # [D212 Etapa 4-5] CAS, CASS (2.1 și 2.2), impozitul în sistem real și sumarul, din veniturile declarate mai sus
        manual["oblig_realizat"], bife = oblig_realizat(manual.get("cap11"), manual.get("cap12"), an,
                                                        bool(manual.get("optiune_cas")), manual.get("exceptie_minim_cass") or None,
                                                        alte_cass)
        manual.update(bife)
    prof = pull(conn, schema, perioada)
    er = erori_generare(prof, manual)
    if er:
        raise ValueError("D212 nu se poate genera: " + " ".join(er))
    calc = calcul_d212(manual)
    xml = build_xml(prof, an, None, manual, calc)
    capitole = [n for n in _COPII if manual.get(n)]
    return xml, Rezultat212(an=an, total_plata_a=calc["totalPlata_A"], capitole=capitole, avertismente=avert)
