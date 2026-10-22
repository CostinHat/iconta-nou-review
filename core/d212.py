"""core/d212.py - D212: Declaratia unica privind impozitul pe venit si contributiile sociale
datorate de persoanele fizice (ns v11, pachet validator v9 = J13.0.1).

CE FACE (03.10.2026, dupa D212 Etapele 2-5): contabilul da DATELE persoanei fizice (identitate, venitul din registrul
RIP al firmei PFA/II/IF, normele de venit, celelalte venituri din Romania, veniturile din strainatate, cele cateva alegeri
pe care evidenta nu le poate sti — exceptia de la baza minima CASS, asiguratul in alt stat); generatorul CALCULEAZA
randurile dupa instructiunile OPANAF 2736/2025 si Codul fiscal, cu temeiul pe constantele ancorate:
  - cap11 (Subsectiunea I.1.1), cate o sectiune pe sursa: activitati independente din RIP (`cap11_din_rip`) si categoriile
    fara date in aplicatie (`cap11_categorie`: DPI, cedarea folosintei, turistic, agricole, investitii, alte surse);
  - cap12 (Subsectiunea I.1.2), cate o sectiune pe activitate/loc: venitul pe norma (`cap12_norma`);
  - cap14 (Sectiunea 2), cate o sectiune pe tara si sursa: veniturile din strainatate (`cap14_sectiune`), creditul fiscal
    plafonat (CF art.131 alin.(4)), metoda scutirii;
  - oblig_realizat (Sectiunile 3, 4, 5, 7 si Sectiunea 2 Subsectiunea a 2-a): CAS si CASS (2.1 si 2.2 pe trepte, din
    `d212_engine`), impozitul in sistem real si pe DPI cu contributiile deductibile pe pondere, sumarul de plata.
  - totalPlata_A = suma cifrelor CNP (DUK regula R4, ValidatorCode.validateD212 citita integral 01.10.2026).
Apelantul poate trimite si sectiuni gata calculate (chei `cap11`/`cap12`/`cap14`/`oblig_realizat` in `manual`) — se emit
asa cum sunt, verificate doar pe numele atributelor (`_CAMPURI`, confruntat cu jar-ul de test_d212_campuri_validator).

CE REFUZA NUMIT (nu emite pe jumatate): agricolul pe norma (Subsectiunea a 4-a — validatorul instalat n-are campurile),
optiunea CAS sub 12 sm (lit.B — fara casuta), CASS pe pensiile din strainatate (Subsectiunea a 3-a a Sectiunii 2 — lipsa),
CASS 2.2 retinuta peste cea datorata (fara rand „in minus”), categoriile pentru veniturile 2026 (Legea 239/2025 si
141/2025 schimba regulile; formularul ANAF nepublicat). Detaliul si temeiurile: D212_PERIMETRU.md §5-§9, DECIZII.

SURSA STRUCTURII = VALIDATORUL OFICIAL ANAF (arbitrul), D212Validator.jar:
  - Radacina = element <d212> (NU <declaratie>; acela era ns:v1, invechit). Namespace v11; selectia versiunii
    (d212validator/Validator._dateVersionTable): '2025-01 J13.0.1 9 7 2025-01-15' => pachet v9 + Parameters_v7.
  - Copii (elemente lowercase): cap11, cap12, cap14, oblig_realizat, oblig_estimat, coasigurat — cap11/cap12/cap14 se
    repeta (probat pe DUK). Atribute OBLIGATORII pe radacina: d_rec, rectif1, rectif2, totalPlata_A, luna_r (=12),
    an_r ([2025,2100]), bifele (bifa_succesor ... bifa15), nerezident + identificare (cif, nume_c, adresa_c).
  - Cazul minim (doar identificare, bifele pe 0) ramane valid — e ce iese cand nu se da niciun venit.

Contract dXXX: NS, _cif/_cnp_valid/_esc, calcul_d212, pull(conn,schema,perioada)->{},
erori_generare, build_xml, genereaza(conn, schema, perioada, manual=None). conn=None este acceptat
(pull nu atinge baza; venitul din RIP cere conexiunea).
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
    # [440, w5] cele două refuzuri (sumele, zilele scutite) sunt independente: pleacă împreună (`RefuzuriSectiune`)
    motive = []
    vb, cd = _lei(venit_brut), _lei(chelt_deduc)
    pp = _suma_camp({"p": pierdere_precedenta}, "p", "pierderea reportată", motive, "D212 registrul RIP")
    if vb < 0 or cd < 0 or (pp is not None and pp < 0):
        motive.append("Venitul brut, cheltuielile și pierderea reportată nu pot fi negative.")
    c = {"categ_venit": CATEG_ACTIVITATI_INDEPENDENTE, "det_ven_net": DET_VEN_NET_SISTEM_REAL,
         "forma_org": FORMA_ORG_INDIVIDUAL, "venit_brut": vb, "chelt_deduc": cd}
    if caen:
        c["caen"] = str(caen).strip()
    scut = _intreg_camp({"z": nr_zile_scutite}, "z", "zilele scutite", motive, "D212 registrul RIP")
    if scut is not None and not 0 <= scut <= 366:   # refuz de FORMĂ: număr de zile în afara anului
        motive.append("Zilele scutite trebuie să fie între 0 și numărul de zile ale anului.")
    if motive:
        raise RefuzuriSectiune(motive)
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


def _cota_venit(an):
    """Cota de impozit pe venitul fiecărei surse din fiecare categorie (procent întreg), pentru anul venitului: registrul unic
    (`common.COTE["impozit_venit_categorii"]`, CF art.64 alin.(1)), la 1 ianuarie — ca `impozit_dividend` / `impozit_venit` mai jos.
    Se aplică la lit.a^1) DPI, c) cedarea folosinței, d) investiții, f) agricole, h) alte surse (la alte surse și art.116 alin.(2)); aplicat
    de instrucțiunile D212 (OPANAF 2736/2025) pct.4-9, rd.9. [R3c, 11.10.2026] Până atunci, `COTA_IMPOZIT_VENIT = 10` ancorat aici dubla
    aceeași prevedere cu `bacsis.COTA_IMPOZIT`."""
    from core import common as _c
    return _c.cota("impozit_venit_categorii", _dt.date(an, 1, 1))[0] * 100
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
#: Categoriile introduse de contabil pe ecran. Activitățile independente vin de regulă din registrul RIP al firmei; cele din
#: afara registrului (a doua activitate, ținută în altă firmă, sau perioada unei forme de exercitare anterioare din același an)
#: se adaugă aici, ca să se cumuleze pentru CAS/CASS (CF art.148 alin.(3), art.170 alin.(1)).
CATEG_MANUALE = (CATEG_ACTIVITATI_INDEPENDENTE, CATEG_DPI, CATEG_CEDARE, CATEG_TURISTIC) + CATEG_AGRICOLE + (CATEG_INVESTITII,) \
    + CATEG_ALTE_SURSE


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


def _suma_camp(a, k, camp, motive, prefix):
    """[440] Suma din formular în lei întregi (`_lei`); dacă rubrica nu e un număr, motivul intră în `motive` și se întoarce None —
    refuz de FORMĂ, alături de celelalte ale secțiunii (până la 22.10.2026 textul nenumeric ieșea ca excepție brută, nu ca refuz)."""
    try:
        return _lei(a.get(k))
    except (ArithmeticError, ValueError):   # decimal.InvalidOperation e ArithmeticError
        motive.append("%s: %s %r nu e o sumă în lei." % (prefix, camp, a.get(k)))
        return None


def _intreg_camp(a, k, camp, motive, prefix, implicit=0):
    """[440] Numărul întreg din formular (rubrica goală / 0 -> `implicit`, ca `int(a.get(k) or implicit)` de până acum); dacă nu e un
    număr întreg, motivul intră în `motive` și se întoarce None (refuz de FORMĂ, nu mai „invalid literal for int()”)."""
    v = a.get(k)
    if not v:
        return implicit
    try:
        return int(v.strip()) if isinstance(v, str) else int(v)
    except (TypeError, ValueError):
        motive.append("%s: %s %r nu e un număr întreg." % (prefix, camp, v))
        return None


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
          caen?, sediu?, nr_doc?, data_doc?, data_incep?, data_sf?, nr_zile_scutite?}. Sume în lei întregi (half-up).

    [440, comanda Costin 11.1 pct.16: „toate erorile apar deodată, fiecare cu textul ei”] Refuzurile secțiunii se ADUNĂ și pleacă
    împreună (`RefuzuriSectiune`, câte un motiv; unul singur rămâne fraza lui). Regulile sunt aceleași — se schimbă numai momentul.
    Rămân singure, înaintea celorlalte, fiindcă de ele DEPINDE ce se verifică mai departe:
      - categoria în afara listei de pe ecran — rubricile pe care le are secțiunea și regulile lor sunt ale categoriei;
      - anul fără reguli verificate — niciun rând nu se poate judeca.
    Se judecă apoi, toate, independent una de alta: sumele (număr, nenegative), zilele scutite (număr, categoria care le admite,
    intervalul), determinarea venitului net (DPI), forma de organizare, cele trei date (formă și an), și refuzurile ramurii
    (pierderi la cote forfetare, cheltuieli date la cote forfetare, pierderea la turistic, brut/cheltuieli la investiții și la alte
    surse, venitul impozabil lipsă). DEPENDENTE, deci sărite cât timp lipsește premisa (nu dublează motivul ei):
      - refuzurile ramurii la DPI cer determinarea venitului net validă — ramura (forfetar / real) e aleasă de ea;
      - „sumele cuvenite organismelor de gestiune depășesc venitul brut” cere ambele sume valide și nenegative."""
    an = int(an)
    try:
        cat = int(a.get("categ_venit"))
    except (TypeError, ValueError):
        cat = None
    if cat not in CATEG_MANUALE:   # refuz de FORMĂ: codul în afara listei de pe ecran (singur: restul depinde de categorie)
        raise ValueError("D212: categoria de venit %r nu e în lista de pe ecran (%s)."
                         % (a.get("categ_venit"), ", ".join(str(c) for c in CATEG_MANUALE)))
    # activitățile independente urmează regulile căii din registrul RIP (anii verificați în oblig_realizat), nu ANI_CATEGORII
    if an not in ANI_CATEGORII and cat != CATEG_ACTIVITATI_INDEPENDENTE:
        raise ValueError("D212: %s — regulile pe categorii sunt verificate pentru veniturile %s (instrucțiunile OPANAF 2736/2025); "
                         "pentru %d, Legea 239/2025 art.XII schimbă cedarea folosinței (CF art.83-87) și alte surse (art.114-116), "
                         "iar ANAF n-a publicat formularul. Se declară pe formularul ANAF."
                         % (CATEG_VENIT_CAP11[cat], "/".join(map(str, ANI_CATEGORII)), an))
    eticheta = CATEG_VENIT_CAP11[cat]
    prefix = "D212 %s" % eticheta
    motive = []
    vb = _suma_camp(a, "venit_brut", "venitul brut", motive, prefix)
    cd = _suma_camp(a, "chelt_deduc", "cheltuielile", motive, prefix)
    pp = _suma_camp(a, "pierdere_precedenta", "pierderea reportată", motive, prefix)
    if any(x is not None and x < 0 for x in (vb, cd, pp)):   # refuz de FORMĂ: sume negative
        motive.append("D212 %s: venitul brut, cheltuielile și pierderea reportată nu pot fi negative." % eticheta)
    sume_ok = all(x is not None and x >= 0 for x in (vb, cd, pp))
    scut = _intreg_camp(a, "nr_zile_scutite", "zilele scutite", motive, prefix)
    if scut and cat not in CATEG_SCUTIRE_HANDICAP:
        motive.append("D212 %s: zilele scutite nu se aplică — scutirea pentru handicap grav sau accentuat (CF art.60 pct.1) "
                      "privește activitățile independente, drepturile de proprietate intelectuală și activitățile agricole."
                      % eticheta)
    if scut is not None and not 0 <= scut <= 366:   # refuz de FORMĂ: număr de zile în afara anului
        motive.append("D212 %s: zilele scutite trebuie să fie între 0 și numărul de zile ale anului." % eticheta)
    det_ok = True
    if cat == CATEG_DPI:
        try:
            det = int(a.get("det_ven_net") or DET_VEN_NET_FORFETAR)
        except (TypeError, ValueError):
            det = a.get("det_ven_net")
        if det not in (DET_VEN_NET_SISTEM_REAL, DET_VEN_NET_FORFETAR):   # refuz de FORMĂ: validatorul are două căsuțe
            motive.append("D212 %s: determinarea venitului net %r — 1 sistem real, 2 cote forfetare." % (eticheta, det))
            det_ok = False
    elif cat == CATEG_CEDARE:
        det = DET_VEN_NET_FORFETAR                      # pct.5.6.2 „se bifează căsuța cote forfetare de cheltuieli”
    elif cat in (CATEG_TURISTIC, CATEG_ACTIVITATI_INDEPENDENTE) or cat in CATEG_AGRICOLE:
        det = DET_VEN_NET_SISTEM_REAL                   # pct.3.5.2 / 5.7.2 / 6.6.2 „se bifează căsuța sistem real”
    else:
        det = None                                      # investiții, alte surse: rd.2 nu se completează (pct.7.3, 9.2)
    c = {"categ_venit": cat}
    if det and det_ok:
        c["det_ven_net"] = det
    if cat in (CATEG_DPI, CATEG_ACTIVITATI_INDEPENDENTE) or cat in CATEG_AGRICOLE:
        try:
            forma = int(a.get("forma_org") or FORMA_ORG_INDIVIDUAL)
        except (TypeError, ValueError):
            forma = None
        if forma not in FORME_ORG_NORMA:   # refuz de FORMĂ: pct.4.5.3 / 6.6.3 au două căsuțe
            motive.append("D212 %s: forma de organizare %r — 1 individual, 2 asociere." % (eticheta, a.get("forma_org")))
        c["forma_org"] = forma
    for k, kx in (("caen", "caen"), ("sediu", "descriere_sediu_bun"), ("nr_doc", "nr_doc_autoriz")):
        if str(a.get(k) or "").strip():
            c[kx] = str(a[k]).strip()
    ian1, dec31 = _dt.date(an, 1, 1), _dt.date(an, 12, 31)
    for k, kx, camp in (("data_doc", "data_doc_autoriz", "data documentului"), ("data_incep", "data_incep", "data începerii"),
                        ("data_sf", "data_sf", "data încetării")):
        try:
            d = _data(a.get(k), camp, prefix)
        except ValueError as e:
            motive.append(str(e))
            continue
        if d is None:
            continue
        if kx != "data_doc_autoriz" and not ian1 <= d <= dec31:
            motive.append("D212 %s: %s (%s) nu e în anul %d — rubrica se completează numai dacă evenimentul se produce în "
                          "cursul anului (OPANAF 2736/2025, instrucțiuni rd.8/rd.9)." % (eticheta, camp, d, an))
            continue
        c[kx] = _dmy(d)
    if scut:
        c["nr_zile_scutite"] = scut

    # refuzurile ramurii (fiecare citește numai rubricile ei, deja judecate mai sus)
    cn = vi = None
    if det_ok and det == DET_VEN_NET_FORFETAR:
        if pp:   # refuz de FORMĂ: la cote forfetare nu există rd.5 (pct.4.5.9 / 5.6.6 enumeră rd.1, 2, 3, 7, 9)
            motive.append("D212 %s: la cote forfetare nu se reportează pierderi." % eticheta)
        if cat == CATEG_DPI and a.get("fara_cota_forfetara"):
            if sume_ok and cd > vb:   # refuz de FORMĂ: sumele cuvenite organismelor de gestiune nu pot depăși venitul brut
                motive.append("D212 %s: sumele cuvenite organismelor de gestiune colectivă depășesc venitul brut." % eticheta)
        elif cd:   # refuz de FORMĂ: cheltuielile la cote forfetare le stabilește cota, nu contabilul
            motive.append("D212 %s: la cote forfetare cheltuielile se calculează din venitul brut; câmpul se lasă gol." % eticheta)
    elif det_ok and det == DET_VEN_NET_SISTEM_REAL:
        if cat == CATEG_TURISTIC and pp:
            motive.append("D212 %s: pierderea din închirierea în scop turistic „reprezintă pierdere definitivă” (OPANAF "
                          "2736/2025, instrucțiuni pct.5.7.3) — nu se reportează." % eticheta)
    elif cat == CATEG_INVESTITII:
        if vb or cd:   # refuz de FORMĂ: pct.7.3.2 începe de la rd.3 (câștigul net), rd.1/rd.2 nu există
            motive.append("D212 %s: se introduce câștigul net anual (pierderea, cu minus), nu venitul brut și cheltuielile."
                          % eticheta)
        cn = _suma_camp(a, "castig_net", "câștigul net anual", motive, prefix)
    elif det_ok:
        if vb or cd or pp:   # refuz de FORMĂ: pct.9.2.2 cere doar rd.7 (venitul impozabil) și rd.9
            motive.append("D212 %s: se introduce venitul impozabil (rd.7), nu venitul brut, cheltuielile sau pierderi." % eticheta)
        vi = _suma_camp(a, "venit_impozabil", "venitul impozabil", motive, prefix)
        if vi is not None and vi <= 0:   # refuz de FORMĂ: secțiune fără venit
            motive.append("D212 %s: venitul impozabil lipsește." % eticheta)
    if motive:
        raise RefuzuriSectiune(motive)

    if det == DET_VEN_NET_FORFETAR:
        if cat == CATEG_DPI and a.get("fara_cota_forfetara"):
            ded = cd          # pct.4.5.10 / CF art.72^1 alin.(2): „fără aplicarea cotei forfetare de cheltuieli”
        else:
            ded = _procent(vb, COTA_FORFETARA_DPI if cat == CATEG_DPI else COTA_FORFETARA_CEDARE)
        net = vb - ded
        c.update(venit_brut=vb, chelt_deduc=ded, venit_net_anual=net, venit_recalculat=net)
        baza = net
        if scut:
            c["venit_redus"] = baza = redus_handicap(net, scut, an)
        c["impozit11"] = _procent(baza, _cota_venit(an))
    elif det == DET_VEN_NET_SISTEM_REAL:
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
            if cat not in (CATEG_DPI, CATEG_ACTIVITATI_INDEPENDENTE):
                # DPI / activități independente în sistem real: rd.8/rd.9 nu se completează — impozitul e în Secțiunea 5 / 4
                # (pct.4.5.7 / 3.5.11)
                baza = net - comp
                if scut:
                    c["venit_redus"] = baza = redus_handicap(baza, scut, an)
                c["impozit11"] = _procent(baza, _cota_venit(an))
        else:
            if cd > vb:
                c["pierdere"] = cd - vb
            c["impozit11"] = 0
    elif cat == CATEG_INVESTITII:
        if pp:
            c["pierdere_precedenta"] = pp
        if cn > 0:
            comp = min(pp, _procent(cn, PROCENT_COMPENSARE_INVESTITII))
            c["venit_net_anual"] = cn
            if pp:
                c["pierdere_compensata"] = comp
            c["venit_recalculat"] = cn - comp
            c["impozit11"] = _procent(cn - comp, _cota_venit(an))
        else:
            if cn < 0:
                c["pierdere"] = -cn
            c["impozit11"] = 0
    else:
        c.update(venit_recalculat=vi, impozit11=_procent(vi, _cota_venit(an)))
    return c



# ── CAP14 (Secțiunea a 2-a, Subsecțiunea 1 — veniturile realizate din străinătate) ───────────────────────────────────
# [D212 Etapa 5c, 03.10.2026] O secțiune pe țară și pe sursă de venit (instrucțiuni pct.32), rândurile după pct.39.6;
# CF art.130 alin.(2): baza „după regulile proprii fiecărei categorii de venit”; art.131: creditul fiscal pe fiecare țară
# și natură de venit, „dar nu poate fi mai mare decât partea de impozit pe venit datorat în România”.
#: Codurile de țară acceptate de validator (D212Validator.jar, Parameters_v7._nomenclatorTari; ISO 3166-1 alfa-2, Grecia
#: = EL, Kosovo = XK; România lipsește — venitul e din străinătate). Confruntat cu jar-ul de core/test_d212_cap14.py.
TARI_STRAINATATE = tuple("AF AX AL DZ AS AD AO AI AQ AG AR AM AW AU AT AZ BS BH BD BB BY BE BZ BJ BM BT BO BQ BA BW BV BR IO BN BG BF BI KH CM CA CV KY CF TD CL CN CX CC CO KM CG CD CK CR CI HR CU CW CY CZ DK DJ DM DO EC EG SV GQ ER EE ET FK FO FJ FI FR GF PF TF GA GM GE DE GH GI EL GL GD GP GU GT GG GN GW GY HT HM VA HN HK HU IS IN ID IR IQ IE IM IL IT JM JP JE JO KZ KE KI KP KR KW KG LA LV LB LS LR LY LI LT LU MO MK MG MW MY MV ML MT MH MQ MR MU YT MX FM MD MC MN ME MS MA MZ MM NA NR NP NL NC NZ NI NE NG NU NF MP NO OM PK PW PS PA PG PY PE PH PN PL PT PR QA RE RU RW BL SH KN LC MF PM VC WS SM ST SA SN RS SC SL SG SX SK SI SB SO ZA GS SS ES LK SD SR SJ SZ SE CH SY TW TJ TZ TH TL TG TK TO TT TN TR TM TC TV UG UA AE GB US UM UY UZ VU VE VN VG VI WF EH YE ZM ZW XK".split())
#: Categoriile din străinătate (D212Pdf Pdf_v8: str_categ_venit_N; 2027/2003 refolosesc etichetele 1./2. din I.1.1 —
#: constant pool deduplicat). Cheia: (eticheta, regula bazei).
CATEG_STRAINATATE = {
    2027: ("Activități independente", "real"),
    2003: ("Drepturi de proprietate intelectuală", "dpi"),
    2004: ("Cedarea folosinței bunurilor", "cedare"),
    2009: ("Activități agricole", "real"), 2010: ("Silvicultură", "real"), 2011: ("Piscicultură", "real"),
    2012: ("Transferul titlurilor de valoare și alte operațiuni cu instrumente financiare", "castig"),
    2017: ("Dobânzi", "brut"), 2018: ("Dividende", "brut"), 2014: ("Alte venituri", "brut"),
    2028: ("Lichidarea unei persoane juridice", "lichidare"),
    2016: ("Salarii plătite din România pentru activitatea desfășurată în străinătate", "salariu"),
    # [5c-2a] categoriile cu bază și cotă proprii (CF art.108-111)
    2025: ("Premii", "premiu"), 2013: ("Jocuri de noroc", "joc"),
    2029: ("Transferul proprietăților imobiliare deținute cel mult 3 ani", "transfer"),
    2030: ("Transferul proprietăților imobiliare deținute mai mult de 3 ani", "transfer"),
    2024: ("Transferul proprietăților imobiliare cu titlu de moștenire", "mostenire"),
    # [5c-2b] pensiile (CF art.130 alin.(2^1)) și remunerațiile administratorilor (art.76 alin.(2), art.78 alin.(2) lit.b)
    2020: ("Pensii", "pensie"),
    2015: ("Remunerații ale membrilor consiliului de administrație, administratorilor, cenzorilor și venituri similare", "remuneratie"),
}
#: Suma neimpozabilă lunară din pensie (lei): 3.000 de la veniturile lunii octombrie 2024 (Legea 244/2024 art.II), păstrată de
#: Legea 141/2025 (art.100 rescris de la 01.08.2025, cu deducerea CASS în plus) — deci aceeași pe tot anul 2025.
PENSIE_NEIMPOZABIL_LUNAR = _anc("d212.PENSIE_NEIMPOZABIL_LUNAR", 3000, _Tm(
    "CF", art="100", alin="1", data_in="2024-10-01", verificat_la="2026-10-03", de_cine="Code/D212-E5",
    nivel_sursa="MO", url="anaf_surse/cod_fiscal_227_2015_consolidat.html",
    text_citat="sumei neimpozabile lunare de 3.000 lei",
    lant_acte="Legea 244/2024 art.I (alin.(1) cu 3.000 lei) și art.II („se aplică începând cu veniturile aferente lunii octombrie "
              "2024”) — anaf_surse/legea_244_2024.html (MO nr. 899/05.09.2024); Legea 141/2025 art.II pct.7 rescrie art.100 de la "
              "01.08.2025 cu aceeași sumă; "
              "art.130 alin.(2^1): pentru pensiile din străinătate suma se calculează „la nivelul anului”"))
#: Suma neimpozabilă pe fiecare premiu (lei) și cota pe venitul net din premiu (procent întreg).
PREMIU_NEIMPOZABIL = _anc("d212.PREMIU_NEIMPOZABIL", 600, _Tm(
    "CF", art="110", alin="4", lit="a", data_in="2018-01-01", verificat_la="2026-10-03", de_cine="Code/D212-E5",
    nivel_sursa="MO", url="anaf_surse/cod_fiscal_227_2015_consolidat.html",
    text_citat="premii sub valoarea sumei neimpozabile stabilite în sumă de 600 lei",
    lant_acte="art.109: venitul net din premii = venitul minus suma neimpozabilă; aplicat de instrucțiunile D212 pct.39.6.2"))
COTA_PREMII = _anc("d212.COTA_PREMII", Decimal("10"), _Tm(
    "CF", art="110", alin="1", data_in="2018-01-01", verificat_la="2026-10-03", de_cine="Code/D212-E5",
    nivel_sursa="MO", url="anaf_surse/cod_fiscal_227_2015_consolidat.html",
    text_citat="cu o cotă de 10% aplicată asupra venitului net realizat din fiecare premiu",
    lant_acte="alin.(1) modificat de OUG 79/2017 pct.33 (de la 01.01.2018)"))
#: Cotele impozitului la transferul proprietăților imobiliare (procent întreg, pe valoarea tranzacției / masei succesorale).
COTA_TRANSFER_PANA_3_ANI = _anc("d212.COTA_TRANSFER_PANA_3_ANI", Decimal("3"), _Tm(
    "CF", art="111", alin="1", lit="a", data_in="2023-01-01", verificat_la="2026-10-03", de_cine="Code/D212-E5",
    nivel_sursa="MO", url="anaf_surse/cod_fiscal_227_2015_consolidat.html",
    text_citat="3% pentru construcțiile de orice fel și terenurile aferente acestora",
    lant_acte="alin.(1) modificat de OG 16/2022 pct.46 (de la 01.01.2023): deținute o perioadă de până la 3 ani inclusiv"))
COTA_TRANSFER_PESTE_3_ANI = _anc("d212.COTA_TRANSFER_PESTE_3_ANI", Decimal("1"), _Tm(
    "CF", art="111", alin="1", lit="b", data_in="2023-01-01", verificat_la="2026-10-03", de_cine="Code/D212-E5",
    nivel_sursa="MO", url="anaf_surse/cod_fiscal_227_2015_consolidat.html",
    text_citat="1% pentru imobilele descrise la lit. a) , deținute o perioadă mai mare de 3 ani",
    lant_acte="alin.(1) modificat de OG 16/2022 pct.46 (de la 01.01.2023)"))
COTA_MOSTENIRE = _anc("d212.COTA_MOSTENIRE", Decimal("1"), _Tm(
    "CF", art="111", alin="3", data_in="2016-01-01", verificat_la="2026-10-03", de_cine="Code/D212-E5",
    nivel_sursa="MO", url="anaf_surse/cod_fiscal_227_2015_consolidat.html",
    text_citat="moștenitorii datorează un impozit de 1% calculat la valoarea masei succesorale",
    lant_acte="doar dacă succesiunea nu e dezbătută și finalizată în 2 ani de la deces (alin.(3)); instrucțiunile D212 pct.39.2 lit.a)"))
#: Plafonul neimpozabil pe fiecare venit brut din jocurile caracteristice cazinourilor, poker, slot-machine și lozuri (lei).
PLAFON_JOCURI_NEIMPOZABIL = _anc("d212.PLAFON_JOCURI_NEIMPOZABIL", 66750, _Tm(
    "CF", art="110", alin="4", lit="b", data_in="2022-08-01", verificat_la="2026-10-03", de_cine="Code/D212-E5",
    nivel_sursa="MO", url="anaf_surse/cod_fiscal_227_2015_consolidat.html",
    text_citat="sub valoarea sumei neimpozabile de 66.750 lei",
    lant_acte="pe fiecare venit brut primit; peste plafon se aplică baremul și se scade baza fixă a tranșei a treia (alin.(2^2))"))
#: Baremul jocurilor de noroc, pe DATA PLĂȚII (o formulă datată, nu un „if data”): ((prag, procent, bază fixă) pe tranșe).
_VARIANTE_BAREM_JOCURI = [
    ("2022-08-01", ((10000, Decimal("3"), 0), (66750, Decimal("20"), 300), (None, Decimal("40"), 11650)), _Tm(
        "OG", 16, 2022, art="I", data_in="2022-08-01", verificat_la="2026-10-03", de_cine="Code/D212-E5", nivel_sursa="MO",
        url="anaf_surse/og_16_2022_consolidat.html",
        text_citat=("până la 10.000 inclusiv 3% peste 10.000-66.750 inclusiv 300 + 20% pentru ceea ce depășește suma de 10.000 "
                    "peste 66.750 11.650 + 40% pentru ceea ce depășește suma de 66.750"),
        lant_acte="art.I pct.45 modifică CF art.110 alin.(2) și (2^2); art.IX lit.c): „se aplică veniturilor plătite începând cu "
                  "1 august 2022”; în vigoare până la Legea 141/2025")),
    ("2025-08-01", ((10000, Decimal("4"), 0), (66750, Decimal("20"), 400), (None, Decimal("40"), 11750)), _Tm(
        "CF", art="110", alin="2", data_in="2025-08-01", verificat_la="2026-10-03", de_cine="Code/D212-E5", nivel_sursa="MO",
        url="anaf_surse/cod_fiscal_227_2015_consolidat.html",
        text_citat=("până la 10.000 inclusiv 4% peste 10.000-66.750 inclusiv 400 + 20% pentru ceea ce depășește suma de 10.000 "
                    "peste 66.750 11.750 + 40% pentru ceea ce depășește suma de 66.750"),
        lant_acte="forma din Legea 141/2025 art.II pct.8; art.VII alin.(1) lit.b): „pentru veniturile plătite începând cu data de "
                  "1 august 2025”")),
]
TIPURI_JOC = {"cazinou": "cazinouri, poker, slot-machine, lozuri (art.110 alin.(2^2))", "altele": "alte jocuri de noroc"}


def impozit_joc(brut, data_plata, tip):
    """Impozitul pe un venit brut din jocuri de noroc (CF art.110 alin.(2), (2^2), (4) lit.b), cu baremul în vigoare la data
    plății (`common.alege_varianta`). La cazinouri/poker/slot/lozuri: neimpozabil până la plafon, peste el baremul minus
    baza fixă a tranșei a treia. Întoarce (suma neimpozabilă, impozit)."""
    from core import common as _c
    transe, _t = _c.alege_varianta(_VARIANTE_BAREM_JOCURI, data_plata)
    (p1, c1, _b1), (p2, c2, b2), (_p3, c3, b3) = transe
    if tip == "cazinou" and brut <= PLAFON_JOCURI_NEIMPOZABIL:
        return brut, 0
    if brut <= p1:
        imp = Decimal(brut) * c1 / 100
    elif brut <= p2:
        imp = b2 + Decimal(brut - p1) * c2 / 100
    else:
        imp = b3 + Decimal(brut - p2) * c3 / 100
    if tip == "cazinou":
        return PLAFON_JOCURI_NEIMPOZABIL, _lei(imp - b3)
    return 0, _lei(imp)
#: Grupările de coduri cap14 pe care le citesc contribuțiile (nomenclatorul de mai sus, nu valori fiscale).
CATEG_STR_INDEPENDENTE, CATEG_STR_DPI, CATEG_STR_CEDARE, CATEG_STR_ALTE = 2027, 2003, 2004, 2014
CATEG_STR_AGRICOLE, CATEG_STR_INVESTITII, CATEG_STR_DOBANZI_DIVIDENDE = (2009, 2010, 2011), (2012, 2028), (2017, 2018)
CATEG_STR_REMUNERATIE = 2015
#: Metoda de evitare a dublei impuneri (Pdf_v8 dubla_impunere_1/_2/_4; rd.3 și rd.4 din lit.A).
DUBLA_CREDIT, DUBLA_SCUTIRE, DUBLA_ACORD = 1, 2, 4


def _cota_strainatate(cat, an):
    """Cota impozitului român pe categoria din străinătate (CF art.130 alin.(2): cotele categoriei)."""
    from core import common as _c, lichidare as _lq
    if cat == 2018:
        return _c.cota("impozit_dividend", _dt.date(an, 1, 1))[0] * 100          # CF art.97 alin.(7) pe anul venitului
    if cat in (2016, 2015):
        return _c.cota("impozit_venit", _dt.date(an, 1, 1))[0] * 100             # CF art.78 alin.(2) (lit.a / lit.b)
    if cat == 2028:
        return _lq._cota_lichidare(_dt.date(an, 12, 31))                          # CF art.97 alin.(5)
    if cat == 2025:
        return COTA_PREMII                                                       # CF art.110 alin.(1)
    if cat in (2029, 2030):
        return COTA_TRANSFER_PANA_3_ANI if cat == 2029 else COTA_TRANSFER_PESTE_3_ANI   # CF art.111 alin.(1)
    if cat == 2024:
        return COTA_MOSTENIRE                                                    # CF art.111 alin.(3)
    return _cota_venit(an)                                                       # CF art.64 alin.(1)


def cap14_sectiune(a, an):
    """O secțiune cap14 (o țară, o sursă), rând cu rând după instrucțiunile D212 pct.39.6:

      rd.1 brut · rd.2 cheltuieli/alte sume deductibile — după regula categoriei: sistem real (dat), DPI 40% sau real,
          cedarea folosinței 20%, lichidare (aportul, dat); dobânzi/dividende/alte venituri: fără deduceri
      rd.3 net / câștig net (titluri: câștigul anual dat; salarii: venitul bază de calcul din documentul angajatorului)
      rd.4 pierdere · rd.5 pierderi reportate · rd.6 = min(rd.5, 70% x rd.3) (CF art.118 alin.(5), art.119 alin.(4):
          aceeași natură și sursă, pe fiecare țară) · rd.7 = rd.3 - rd.6
      rd.8 impozit în România = cota categoriei x rd.7; zero la metoda scutirii, la venit scutit prin acord, la pierdere
      rd.9 impozit plătit în străinătate · rd.10 credit = min(rd.9, rd.8) — doar la metoda creditului (CF art.131 alin.(4))
      rd.11 = rd.8 - rd.10 (zero dacă creditul acoperă impozitul)
    `a`: {tara, categ_venit, dubla_impunere?, venit_brut?, chelt_deduc?, det_ven_net? (DPI), castig_net? (titluri),
          venit_baza? (salarii), pierdere_precedenta?, impozit_platit?, data_incep?, data_sf?}.

    [440, comanda Costin 11.1 pct.16: „toate erorile apar deodată, fiecare cu textul ei”] Refuzurile secțiunii se ADUNĂ și pleacă
    împreună (`RefuzuriSectiune`, câte un motiv; unul singur rămâne fraza lui). Regulile sunt aceleași — se schimbă numai momentul.
    Rămân singure, înaintea celorlalte, fiindcă de ele DEPINDE ce se verifică mai departe:
      - categoria în afara listei de pe ecran — regula bazei (real / forfetar / brut / pensie / joc …) e a categoriei;
      - anul fără reguli verificate — niciun rând nu se poate judeca.
    Se judecă apoi, toate, independent una de alta: țara, metoda de evitare a dublei impuneri, sumele (număr, nenegative), datele
    (formă și an), determinarea venitului net (DPI), și refuzurile regulii categoriei (cheltuieli date unde le stabilește legea,
    lunile de pensie, CASS pe pensie, felul jocului, data plății, brut/cheltuieli la titluri și salarii, venitul bază negativ,
    pierderi reportate unde nu se admit). DEPENDENTE, deci sărite cât timp lipsește premisa:
      - la DPI, „cheltuielile la cote forfetare” și „pierderile nu se reportează” cer determinarea venitului net validă — ea alege
        forfetarul sau sistemul real;
      - data plății la jocuri: dacă nu e o dată, motivul e cel de formă, nu și „lipsește / nu e în an”."""
    an = int(an)
    try:
        cat = int(a.get("categ_venit"))
    except (TypeError, ValueError):
        cat = None
    if cat not in CATEG_STRAINATATE:   # refuz de FORMĂ: codul în afara listei de pe ecran (singur: restul depinde de categorie)
        raise ValueError("D212 străinătate: categoria %r nu e în lista de pe ecran (%s)."
                         % (a.get("categ_venit"), ", ".join(str(c) for c in CATEG_STRAINATATE)))
    eticheta, regula = CATEG_STRAINATATE[cat]
    if an not in ANI_CATEGORII:
        raise ValueError("D212 străinătate: %s — regulile sunt verificate pentru veniturile %s (instrucțiunile OPANAF 2736/2025); "
                         "pentru %d, Legea 239/2025 și Legea 141/2025 schimbă cote și baze, iar ANAF n-a publicat formularul. Se "
                         "declară pe formularul ANAF." % (eticheta, "/".join(map(str, ANI_CATEGORII)), an))
    prefix = "D212 străinătate %s" % eticheta
    motive = []
    tara = str(a.get("tara") or "").strip().upper()
    if tara not in TARI_STRAINATATE:   # refuz de FORMĂ: nomenclatorul de țări al validatorului
        motive.append("D212 străinătate: țara %r nu e în nomenclatorul ANAF (cod din două litere, ex. DE, AT; Grecia = EL)."
                      % a.get("tara"))
    try:
        metoda = int(a.get("dubla_impunere") or 0)
    except (TypeError, ValueError):
        metoda = None
    if metoda not in (0, DUBLA_CREDIT, DUBLA_SCUTIRE, DUBLA_ACORD):   # refuz de FORMĂ: trei căsuțe în formular
        motive.append("D212 străinătate: metoda %r — 1 creditul fiscal, 2 scutirea, 4 venit scutit prin acord internațional."
                      % a.get("dubla_impunere"))
    vb, cd, pp, platit = (_suma_camp(a, k, camp, motive, prefix) for k, camp in (
        ("venit_brut", "venitul brut"), ("chelt_deduc", "cheltuielile"), ("pierdere_precedenta", "pierderea reportată"),
        ("impozit_platit", "impozitul plătit în străinătate")))
    if any(x is not None and x < 0 for x in (vb, cd, pp, platit)):   # refuz de FORMĂ: sume negative
        motive.append("D212 străinătate %s: sumele nu pot fi negative (pierderea la titluri se scrie la câștigul net)." % eticheta)
    forfetar = regula == "cedare"
    if regula == "dpi":
        try:
            det = int(a.get("det_ven_net") or DET_VEN_NET_FORFETAR)
        except (TypeError, ValueError):
            det = a.get("det_ven_net")
        if det in (DET_VEN_NET_SISTEM_REAL, DET_VEN_NET_FORFETAR):
            forfetar = det == DET_VEN_NET_FORFETAR
        else:   # refuz de FORMĂ: două căsuțe, ca la I.1.1 (până la 22.10.2026 orice altă valoare trecea tăcut drept sistem real)
            motive.append("D212 străinătate %s: determinarea venitului net %r — 1 sistem real, 2 cote forfetare." % (eticheta, det))
            forfetar = None   # necunoscut: refuzurile care depind de el se sar
    c = {"str_stat_realiz_v": tara, "str_categ_venit": cat}
    if metoda:
        c["dubla_impunere"] = metoda
    ian1, dec31 = _dt.date(an, 1, 1), _dt.date(an, 12, 31)
    for k, kx, camp in (("data_incep", "str_data_incep", "data începerii"), ("data_sf", "str_data_sf", "data încetării")):
        try:
            d = _data(a.get(k), camp, prefix)
        except ValueError as e:
            motive.append(str(e))
            continue
        if d is None:
            continue
        if not ian1 <= d <= dec31:
            motive.append("D212 străinătate %s: %s (%s) nu e în anul %d — rubrica se completează numai dacă evenimentul se "
                          "produce în cursul anului (OPANAF 2736/2025, instrucțiuni pct.39.5)." % (eticheta, camp, d, an))
            continue
        c[kx] = _dmy(d)

    # refuzurile regulii categoriei (fiecare citește numai rubricile ei)
    luni = tip = dp = net = None
    if regula == "pensie":
        if cd:   # refuz de FORMĂ: suma neimpozabilă o stabilește legea
            motive.append("D212 străinătate %s: suma neimpozabilă se calculează; câmpul de cheltuieli se lasă gol." % eticheta)
        try:
            luni = int(a.get("nr_luni") or 0)
        except (TypeError, ValueError):
            luni = 0
        if not 1 <= luni <= 12:   # refuz de FORMĂ: lunile de pensie în an
            motive.append("D212 străinătate %s: numărul lunilor cu pensie în an (1-12) e obligatoriu." % eticheta)
        if _intreg_camp(a, "luni_cass_ro", "lunile august–decembrie cu CASS în România", motive, prefix) \
                and not a.get("fara_contributii"):
            motive.append("D212 străinătate %s: CASS datorată în România pe pensia din străinătate (de la veniturile lunii august "
                          "2025, CF art.155 alin.(1) lit.a^2) se declară în Subsecțiunea a 3-a a Secțiunii 2 (instrucțiuni pct.41), "
                          "pe care formularul validatorului ANAF instalat (J13.0.1) n-o are. Se declară pe formularul ANAF." % eticheta)
    elif regula == "remuneratie":
        if cd and not a.get("fara_contributii"):   # refuz de FORMĂ: CAS/CASS datorate în România se calculează (Secțiunea 2 Subsecțiunea a 2-a)
            motive.append("D212 străinătate %s: CAS și CASS datorate în România se calculează; câmpul de contribuții se "
                          "completează doar pentru un asigurat în alt stat (contribuțiile plătite acolo)." % eticheta)
    elif regula in ("premiu", "joc", "transfer", "mostenire"):
        if cd:   # refuz de FORMĂ: deducerea o stabilește legea (suma neimpozabilă / plafonul), nu contabilul
            motive.append("D212 străinătate %s: suma neimpozabilă se calculează; câmpul de cheltuieli se lasă gol." % eticheta)
        if regula == "joc":
            tip = str(a.get("tip_joc") or "")
            if tip not in TIPURI_JOC:   # refuz de FORMĂ: două feluri, cu regimuri diferite
                motive.append("D212 străinătate %s: alege felul jocului — %s." % (eticheta, " / ".join(TIPURI_JOC.values())))
            try:
                dp = _data(a.get("data_plata"), "data plății", prefix)
            except ValueError as e:   # nu e o dată: motivul de formă, nu și „obligatorie” (aceeași rubrică)
                motive.append(str(e))
            else:
                if dp is None or not ian1 <= dp <= dec31:
                    motive.append("D212 străinătate %s: data plății (în anul %d) e obligatorie — baremul depinde de ea (CF art.110 "
                                  "alin.(2): forma OG 16/2022 până la 31.07.2025, forma Legea 141/2025 de la 01.08.2025)."
                                  % (eticheta, an))
    elif regula in ("castig", "salariu"):
        if vb or cd:   # refuz de FORMĂ: pct.39.6.3 — la titluri câștigul anual, la salarii venitul bază de calcul
            motive.append("D212 străinătate %s: se scrie %s, nu venitul brut și cheltuielile." % (
                eticheta, "câștigul net anual (pierderea cu minus)" if regula == "castig" else "venitul bază de calcul din documentul angajatorului"))
        net = _suma_camp(a, "castig_net" if regula == "castig" else "venit_baza",
                         "câștigul net anual" if regula == "castig" else "venitul bază de calcul", motive, prefix)
        if regula == "salariu" and net is not None and net < 0:   # refuz de FORMĂ: venitul bază de calcul nu e negativ
            motive.append("D212 străinătate %s: venitul bază de calcul nu poate fi negativ." % eticheta)
    else:
        if regula in ("brut",) and cd:   # refuz de FORMĂ: dobânzile, dividendele, alte venituri — impozit pe sumă
            motive.append("D212 străinătate %s: impozitul se aplică asupra sumei încasate; cheltuielile nu se scriu." % eticheta)
        if forfetar and cd:   # refuz de FORMĂ: la cote forfetare cheltuiala o stabilește cota
            motive.append("D212 străinătate %s: la cote forfetare cheltuielile se calculează din venitul brut; câmpul se "
                          "lasă gol." % eticheta)
    if pp and (forfetar is True or regula in ("brut", "salariu", "lichidare", "premiu", "joc", "transfer", "mostenire", "pensie",
                                              "remuneratie")):
        motive.append("D212 străinătate %s: pierderile se reportează doar la activități în sistem real și la titluri "
                      "(CF art.118 alin.(5), art.119 alin.(4))." % eticheta)
    if motive:
        raise RefuzuriSectiune(motive)

    joc_imp = None
    if regula == "pensie":
        cd = min(vb, PENSIE_NEIMPOZABIL_LUNAR * luni)          # CF art.130 alin.(2^1) + art.100 alin.(1), la nivelul anului
    elif regula == "remuneratie":
        if not a.get("fara_contributii"):
            # asigurat în alt stat: contribuțiile plătite acolo (date de contabil) se scad — CF art.78 alin.(2) lit.b); altfel
            # CAS și CASS datorate în România se calculează
            from core import common as _c
            cd = (_procent(vb, _c.cota("cas", ian1)[0] * 100) + _procent(vb, _c.cota("cass", ian1)[0] * 100))
    elif regula == "premiu":
        cd = min(vb, PREMIU_NEIMPOZABIL)                     # CF art.109 + art.110 alin.(4) lit.a), pe fiecare premiu
    elif regula == "joc":
        cd, joc_imp = impozit_joc(vb, dp, tip)
    elif forfetar:
        cd = _procent(vb, COTA_FORFETARA_CEDARE if regula == "cedare" else COTA_FORFETARA_DPI)   # CF art.84 alin.(3) / 72^1
    if regula not in ("castig", "salariu"):
        c.update(str_venit_brut=vb, str_chelt_deduc=cd)
        net = vb - cd
    if pp:
        c["str_pierdere_precedenta"] = pp
    cota = _cota_strainatate(cat, an)
    if net > 0:
        procent = PROCENT_COMPENSARE_INVESTITII if regula == "castig" else PROCENT_COMPENSARE_PIERDERE
        comp = min(pp, _procent(net, procent))
        c["str_venit_net_anual"] = net
        if pp:
            c["str_pierdere_compensata"] = comp
        c["str_venit_recalculat"] = net - comp
        datorat = 0 if metoda in (DUBLA_SCUTIRE, DUBLA_ACORD) else (joc_imp if joc_imp is not None else _procent(net - comp, cota))
    else:
        if net < 0:
            c["str_pierdere_anuala"] = -net
        datorat = 0
    c["str_impozit_datorat_Ro"] = datorat
    if platit:
        c["str_impozit_platit"] = platit
    credit = min(platit, datorat) if metoda == DUBLA_CREDIT else 0
    if credit:
        c["str_credit_fiscal"] = credit
    c["str_dif_impozit_datorat"] = datorat - credit
    return c


# ── OBLIG_REALIZAT (Secțiunile 3, 4 și 7 ale cap.I — CAS, CASS, impozitul în sistem real, sumarul) ──────────────
# [D212 Etapa 4, 02.10.2026] Atributele = clasa Oblig_realizat din D212Validator.jar v9 (fără reguli încrucișate, doar
# intervale); corespondența atribut -> rând = D212Pdf.jar Pdf_v8 (formularul validatorului): I.3.1 CAS rd.1-5, I.3.2.1
# CASS rd.1-5, I.4 rd.1-6 + I.4.1/I.4.2 (contribuțiile deductibile pe pondere, CF art.118 alin.(2^2)/(2^3)), I.7.1-I.7.4.
# Rândurile urmează instrucțiunile D212 (OPANAF 2736/2025) Secțiunile 3, 4 și 7; CAS și CASS vin din `d212_engine`
# (aceeași sursă ca fișa RIP), nu dintr-o a doua formulă.
def _alte_cass_refuz(x):
    """[440, w5] Refuzul de FORMĂ al veniturilor pentru CASS 2.2 (sume negative) — un singur loc: `oblig_realizat` îl ridică, `genereaza`
    îl adună cu refuzurile secțiunilor (rubrici ale omului, independente de venituri). None dacă sumele sunt bune."""
    try:
        if min(_lei(x.get(k)) for k in ("asociere_pj", "dividende_dobanzi", "cass_retinuta")) >= 0:
            return None
    except ArithmeticError:   # decimal.InvalidOperation: rubrica nu e număr
        return "D212: veniturile pentru CASS și CASS reținută se scriu în lei, ca numere."
    return "D212: veniturile pentru CASS și CASS reținută nu pot fi negative."


def _pondere(parte, total):
    """Ponderea (rd.1/rd.2) cu 4 zecimale, ca text (validatorul o citește ca valoare reală)."""
    return "%.4f" % (Decimal(parte) / Decimal(total)) if total else "0.0000"


def oblig_realizat(cap11, cap12, an, optiune_cas=False, exceptie_minim_cass=None, alte_cass=None, cap14=None,
                   cap14_contributii=None):
    """Secțiunile 3, 4, 5 și 7 din venitul declarat în cap11 (o secțiune pe sursă) și cap12 (normă). Întoarce (secțiune, bife).

    Venitul pentru încadrarea CAS (I.3.1 rd.1, I.4.1/I.5.1 rd.2) = venitul net din activități independente (cap11 rd.3;
    pierderea nu se ia — instrucțiuni pct.49.1.2.4) + normele (cap12 rd.9) + venitul net din drepturi de proprietate
    intelectuală — CF art.148 alin.(3). Venitul pentru CASS 2.1 (I.3.2.1 rd.1) = fără DPI — art.170 alin.(1). DPI, cedarea
    folosinței, investițiile, agricolele și alte surse merg la CASS 2.2, pe trepte — art.170 alin.(2)-(4).
    `alte_cass`: {asociere_pj, dividende_dobanzi, cass_retinuta} — venituri art.155 alin.(1) lit.c)-h) fără secțiune I.1.1
    (impuse la sursă: venitul distribuit din asocieri cu PJ, dividendele/dobânzile nete) și CASS reținută de plătitori
    (art.174^1), date de contabil.
    `cap14` (veniturile din străinătate): intră în CAS (instrucțiuni pct.46.3, „din România și din afara României”), în CASS
    2.2 (pct.52.1.4) și — INTERPRETARE CU TEMEI — activitățile independente din străinătate în CASS 2.1: art.170 alin.(1)
    cumulează „venitul net anual realizat” fără limită teritorială, iar pct.46.3/52.1.4 o spun explicit pentru celelalte
    două baze; alternativă respinsă: 2.1 doar pe venitul din România (ar crea o bază mai mică decât cea a CAS pe același
    venit). Impozitul din cap14 rd.11 intră în I.7 rd.1 (pct.56.1, a cincea liniuță).
    `cap14_contributii`: secțiunile cap14 care intră în CAS/CASS (implicit toate). Instrucțiunile pct.46.3/52.1.4 le cer
    „cu respectarea legislației europene aplicabile în domeniul securității sociale, precum și a acordurilor” — dacă
    persoana e asigurată în alt stat, venitul nu poartă contribuții în România; asta o știe contabilul, nu evidența."""
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

    str_secs = _sectiuni(cap14)
    str_contrib = str_secs if cap14_contributii is None else _sectiuni(cap14_contributii)

    def _str(categorii, camp):
        return sum(_lei(s.get(camp) or 0) for s in str_contrib if int(s.get("str_categ_venit") or 0) in categorii)

    ai = (CATEG_ACTIVITATI_INDEPENDENTE,)
    net_real, recalc = _suma(ai, "venit_net_anual"), _suma(ai, "venit_recalculat")
    real_dpi = lambda s: int(s.get("det_ven_net") or 0) == DET_VEN_NET_SISTEM_REAL   # noqa: E731
    dpi_net = _suma((CATEG_DPI,), "venit_net_anual")
    dpi_real_net = _suma((CATEG_DPI,), "venit_net_anual", real_dpi)
    dpi_recalc = _suma((CATEG_DPI,), "venit_recalculat", real_dpi)
    norme = sum(_lei(c.get("real_venit_net_anual") or 0) for c in _sectiuni(cap12))
    str_ai, str_dpi = _str((CATEG_STR_INDEPENDENTE,), "str_venit_net_anual"), _str((CATEG_STR_DPI,), "str_venit_net_anual")
    total = net_real + norme + str_ai                  # art.170 alin.(1): CASS 2.1 (cu străinătatea, v. docstring)
    total_cas = total + dpi_net + str_dpi              # art.148 alin.(3) + pct.46.3: CAS
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
    m = _alte_cass_refuz(x)
    if m:
        raise ValueError(m)
    asc, divd, ret22 = _lei(x.get("asociere_pj")), _lei(x.get("dividende_dobanzi")), _lei(x.get("cass_retinuta"))
    # din străinătate (pct.52.1.4): dobânzile și dividendele „diminuate cu impozitul reținut” (art.170 alin.(4) lit.d) —
    # INTERPRETARE CU TEMEI: impozitul aferent = cel plătit în străinătate + diferența datorată în România (rd.9 + rd.11);
    # alternativă respinsă: doar impozitul străin (ar lăsa în bază un impozit pe care persoana îl plătește)
    str_div = sum(_lei(s.get("str_venit_brut") or 0) - _lei(s.get("str_impozit_platit") or 0) - _lei(s.get("str_dif_impozit_datorat") or 0)
                  for s in str_contrib if int(s.get("str_categ_venit") or 0) in CATEG_STR_DOBANZI_DIVIDENDE)
    ven22 = {"cass_ven_dpi": dpi_net + str_dpi, "cass_ven_asc": asc,
             "cass_ven_cfb": _suma((CATEG_CEDARE, CATEG_TURISTIC), "venit_net_anual") + _str((CATEG_STR_CEDARE,), "str_venit_net_anual"),
             "cass_ven_inv": _suma((CATEG_INVESTITII,), "venit_net_anual") + divd + _str(CATEG_STR_INVESTITII, "str_venit_net_anual")
             + max(0, str_div),
             "cass_ven_asp": _suma(CATEG_AGRICOLE, "venit_net_anual") + _str(CATEG_STR_AGRICOLE, "str_venit_net_anual"),
             "cass_ven_alt": _suma(CATEG_ALTE_SURSE, "venit_recalculat") + _str((CATEG_STR_ALTE,), "str_venit_net_anual")}
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
    impozit = sum(_lei(s.get("impozit11") or 0) for s in secs) + sum(_lei(c.get("real_impozit") or 0) for c in _sectiuni(cap12)) \
        + sum(_lei(s.get("str_dif_impozit_datorat") or 0) for s in str_secs)
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
        imp_dpi = _procent(impozabil_dpi, _cota_venit(an))
        o["real_impozit_datorat_dpi"] = imp_dpi
        bife["bifa15"] = "1"
        impozit += imp_dpi
    # Secțiunea 2 Subsecțiunea a 2-a (pct.40): remunerațiile din străinătate — CAS 25% și CASS 10% pe câștigul brut (CF art.139^1,
    # art.157^2), afară de asigurații în alt stat (cap14_contributii); I.7.2 rd.2 și I.7.3 rd.5
    from core import common as _c
    ian = _dt.date(int(an), 1, 1)
    baza_str = _str((CATEG_STR_REMUNERATIE,), "str_venit_brut")
    cas_str = _procent(baza_str, _c.cota("cas", ian)[0] * 100) if baza_str else 0
    cass_str = _procent(baza_str, _c.cota("cass", ian)[0] * 100) if baza_str else 0
    if baza_str:
        o.update(str_cas_baza=baza_str, str_cas_datorat=cas_str, str_cass_baza=baza_str, str_cass_datorat=cass_str,
                 oblcas_real_str=cas_str, oblcass_real_str=cass_str)
        bife["bifa122"] = "1"
    # I.7 sumarul (pct.56): impozitul, CAS, CASS 2.1 și 2.2 stabilite în plus, diferența de plată
    o.update(oblimpoz_real_total=impozit, oblimpoz_real_dif_deplata=impozit, oblcas_real_difPlus=cas_d,
             oblcass_real_difPlus_ai=cass_d, impozit_venit_plus=impozit, cas_plus=cas_d + cas_str,
             cass_plus=cass_d + dif22 + cass_str, dif_de_plata=impozit + cas_d + cass_d + dif22 + cas_str + cass_str)
    if dif22:
        o["oblcass_real_difPlus_dpi"] = dif22
    return o, bife


def _dmy(d):
    """Data în formatul XML ANAF (dd.MM.yyyy), aritmetic — ca la d108/d177 (nu e afișare, e câmp de structură)."""
    return "%02d.%02d.%04d" % (d.day, d.month, d.year)


def _data(v, camp, prefix="D212 normă"):
    """Data din formular (AAAA-LL-ZZ sau ZZ.LL.AAAA) -> date; None daca lipseste. `prefix` = secțiunea care o cere (pana la
    22.10.2026 refuzul spunea „D212 normă” si pe o data a unui venit din I.1.1 sau din strainatate)."""
    if v in (None, ""):
        return None
    t = str(v).strip()
    for fmt in ("%Y-%m-%d", "%d.%m.%Y"):
        try:
            return _dt.datetime.strptime(t[:10], fmt).date()
        except ValueError:
            continue
    raise ValueError("%s: %s %r nu e o dată (AAAA-LL-ZZ)." % (prefix, camp, v))   # refuz de FORMĂ — fără temei legal


class RefuzuriSectiune(ValueError):
    """[440] Refuzul unei secțiuni cu TOATE motivele ei independente (`motive`); ca text, le spune pe toate. E `ValueError`, deci orice
    cale care prindea refuzul ca text îl prinde la fel; `genereaza` le numerotează una câte una."""

    def __init__(self, motive):
        self.motive = list(motive)
        super().__init__(" ".join(self.motive))


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
    # [440] rubricile care nu depind una de alta (norma, norma ajustată, datele, forma de organizare) se judecă toate și se refuză
    # împreună (`RefuzuriSectiune`); cele care se sprijină pe ele (ordinea datelor, zilele) vin după, ca până acum
    motive = []
    norma = _suma_camp(a, "norma", "norma anuală de venit (rd.7)", motive, "D212 normă")
    if norma is not None and norma <= 0:
        motive.append("D212 normă: norma anuală de venit (rd.7) lipsește — se ia din lista DGRFP pentru locul activității.")
    ajust = (_suma_camp(a, "norma_ajustata", "norma ajustată (rd.8)", motive, "D212 normă")
             if a.get("norma_ajustata") not in (None, "") else None)
    if ajust is not None and ajust < 0:
        motive.append("D212 normă: norma ajustată (rd.8) nu poate fi negativă.")
    baza = ajust if ajust is not None else norma
    ian1, dec31 = _dt.date(an, 1, 1), _dt.date(an, 12, 31)
    date = {}
    for k, camp in (("data_incep", "data începerii"), ("data_sf", "data încetării")):
        try:
            d = date[k] = _data(a.get(k), camp)
        except ValueError as e:
            date[k] = None
            motive.append(str(e))
            continue
        if d is not None and not (ian1 <= d <= dec31):
            motive.append("D212 normă: %s (%s) nu e în anul %d — se completează numai dacă evenimentul e în anul de "
                          "impunere (OPANAF 2736/2025, instrucțiuni rd.3/rd.4: „numai dacă evenimentele respective se produc în "
                          "cursul anului”)." % (camp, d, an))
    inc, sf = date["data_incep"], date["data_sf"]
    # [440, w5] data documentului și data suspendării: tot rubrici independente — până la 22.10.2026 se citeau abia la sfârșit, după
    # celelalte refuzuri, iar refuzul lor numea cheia internă („data_doc_autoriz”), nu rubrica
    for k, camp in (("data_doc_autoriz", "data documentului"), ("data_susp", "data suspendării")):
        try:
            date[k] = _data(a.get(k), camp)
        except ValueError as e:
            motive.append(str(e))
    try:
        forma = int(a.get("forma_org") or 1)
    except (TypeError, ValueError):
        forma = None
    if forma not in FORME_ORG_NORMA:   # refuz de FORMĂ: valoarea în afara intervalului validatorului [1,2]
        motive.append("D212 normă: forma de organizare %r — 1 individual, 2 asociere." % a.get("forma_org"))
    # [440, w5] numerele de zile se citesc aici (rubrici independente); intervalul lor depinde de perioadă, deci se judecă după
    intrerupere = _intreg_camp(a, "zile_intrerupere", "zilele de întrerupere", motive, "D212 normă")
    scutite = _intreg_camp(a, "nr_zile_scutite", "zilele scutite", motive, "D212 normă")
    if motive:
        raise RefuzuriSectiune(motive)
    start, end = inc or ian1, sf or dec31
    if end < start:
        raise ValueError("D212 normă: data încetării e înaintea datei începerii.")   # refuz de FORMĂ (coerența datelor)
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
        d = date[k]
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


def _motive(texte):
    """[440] Refuzul generării cu TOATE motivele, fiecare pe rândul lui (DS cap.6: rând cu rând), în forma refuzului bilanțului
    (`bilant.refuz`); un singur motiv rămâne fraza lui, ca până acum."""
    from core.common import cate as _cate
    if len(texte) == 1:
        return texte[0]
    return ("D212 nu se poate genera — %s; rezolvă-le pe toate, apoi generează din nou.\n" % _cate(len(texte), "motiv", "motive")
            + "\n".join("%d. %s" % (i, t) for i, t in enumerate(texte, start=1)))


def genereaza(conn, schema, perioada, manual=None):
    manual = dict(manual or {})
    an = int(getattr(perioada, "an", None) or manual.get("an_r"))
    avert = []
    # [440, comanda Costin 11.1 pct.16: „toate erorile apar deodată, fiecare cu textul ei”] refuzul fiecărei secțiuni (venitul din registru,
    # venit, venit din străinătate, activitate pe normă, veniturile pentru CASS 2.2) se ADAUGĂ aici, nu oprește generarea la prima:
    # contabilul le vede pe toate, numite, dintr-o trecere
    refuzuri = []
    if manual.get("din_rip") and not manual.get("cap11"):
        if conn is None:
            raise ValueError("D212: venitul din registrul RIP cere firma (conexiunea lipsește).")
        try:
            manual["cap11"], a = cap11_din_rip(conn, schema, an, manual.get("pierdere_precedenta") or 0,
                                               manual.get("caen"), manual.get("nr_zile_scutite_rip") or 0)
        except ValueError as e:          # [440, w5] până la 22.10.2026 oprea generarea înaintea celorlalte secțiuni
            manual.pop("cap11", None)
            refuzuri.extend("Venitul din registrul RIP — %s" % t for t in getattr(e, "motive", None) or [e])
        else:
            if a:
                avert.append(a)
    m_cass = _alte_cass_refuz(manual.get("alte_cass") or {})
    if m_cass:
        refuzuri.append(m_cass)
    if manual.get("venituri"):
        # [D212 Etapa 5] categoriile fără date în aplicație: câte o secțiune I.1.1 pe sursă, lângă cea din registrul RIP
        sectiuni = _sectiuni(manual.get("cap11"))
        for i, x in enumerate(_sectiuni(manual["venituri"]), 1):
            try:
                sectiuni.append(cap11_categorie(x, an))
            except ValueError as e:      # numește venitul vinovat (temeiul, unde există, e în mesajul interior)
                refuzuri.extend("Venitul %d — %s" % (i, t) for t in getattr(e, "motive", None) or [e])
        manual["cap11"] = sectiuni
    if manual.get("strainatate"):
        # [D212 Etapa 5c] veniturile din străinătate: câte o secțiune cap14 pe țară și sursă (instrucțiuni pct.32)
        cap14, contrib = [], []
        for i, x in enumerate(_sectiuni(manual["strainatate"]), 1):
            try:
                sec = cap14_sectiune(x, an)
            except ValueError as e:      # numește venitul vinovat (temeiul, unde există, e în mesajul interior)
                refuzuri.extend("Venitul din străinătate %d — %s" % (i, t) for t in getattr(e, "motive", None) or [e])
                continue
            cap14.append(sec)
            if not x.get("fara_contributii"):   # asigurat în alt stat (legislația europeană / acord) -> fără CAS/CASS aici
                contrib.append(sec)
        manual["cap14"], manual["_cap14_contributii"] = cap14, contrib
    if manual.get("cap14"):
        manual["bifa121"] = "1"      # R10: bifa121=1 => cap14 există
    if manual.get("cap11"):
        manual["bifa111"] = "1"      # subsectiunea I.1.1 completata (R7 cere si reciproca)
    if manual.get("agricol"):
        # [D212 Etapa 3] Subsecțiunea a 4-a (activități agricole pe normă, CF art.107 alin.(2)) NU are loc în structura
        # validatorului instalat (J13.0.1 = formularul pentru veniturile 2024: niciun atribut agricol, fără bifa114).
        # Nu se emite pe altă subsecțiune și nu se sare tăcut.
        refuzuri.append("D212: venitul agricol pe normă (Subsecțiunea a 4-a, CF art.107 alin.(2)) nu se poate încă emite — "
                        "validatorul ANAF instalat (J13.0.1) e al formularului pentru veniturile 2024 și nu are câmpurile "
                        "agricole; ANAF n-a publicat validatorul pentru OPANAF 2736/2025. Se declară pe formularul ANAF.")
    if manual.get("norma"):
        # [D212 Etapa 3] activitățile pe normă (Subsecțiunea a 2-a lit.A): o secțiune cap12 pe activitate / loc
        cap12 = []
        for i, x in enumerate(_sectiuni(manual["norma"]), 1):
            try:
                cap12.append(cap12_norma(x, an))
            except ValueError as e:      # numește activitatea vinovată (temeiul, unde există, e în mesajul interior)
                refuzuri.extend("Activitatea %d — %s" % (i, t) for t in getattr(e, "motive", None) or [e])
        manual["cap12"] = cap12
    if refuzuri:
        # [440] cu ele, și ce lipsește din datele contribuabilului (`erori_generare`: numele, adresa, CNP-ul) — tot dintr-o trecere
        raise ValueError(_motive(refuzuri + erori_generare(pull(conn, schema, perioada), manual)))
    if manual.get("cap12"):
        manual["bifa112"] = "1"      # R8: bifa112=1 => cap12 exista (și subsecțiunea se declară completată)
    alte_cass = {k: v for k, v in (manual.get("alte_cass") or {}).items() if v not in (None, "", 0, "0")}
    if (manual.get("cap11") or manual.get("cap12") or manual.get("cap14") or alte_cass) and not manual.get("oblig_realizat"):
        # [D212 Etapa 4-5] CAS, CASS (2.1 și 2.2), impozitul în sistem real și sumarul, din veniturile declarate mai sus
        manual["oblig_realizat"], bife = oblig_realizat(manual.get("cap11"), manual.get("cap12"), an,
                                                        bool(manual.get("optiune_cas")), manual.get("exceptie_minim_cass") or None,
                                                        alte_cass, manual.get("cap14"), manual.get("_cap14_contributii"))
        manual.update(bife)
    prof = pull(conn, schema, perioada)
    er = erori_generare(prof, manual)
    if er:
        raise ValueError(_motive(er) if len(er) > 1 else "D212 nu se poate genera: " + er[0])
    calc = calcul_d212(manual)
    xml = build_xml(prof, an, None, manual, calc)
    capitole = [n for n in _COPII if manual.get(n)]
    return xml, Rezultat212(an=an, total_plata_a=calc["totalPlata_A"], capitole=capitole, avertismente=avert)
