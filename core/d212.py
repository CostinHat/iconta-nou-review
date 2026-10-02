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
    "cap11": {"scutire", "reg", "categ_venit", "det_ven_net", "forma_org", "mod_forma_org",
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
    # oblig_realizat: ~90 campuri CAS/CASS/impozit. Set larg; valorile vin gata calculate din manual.
    "oblig_realizat": {
        "real_camere_inchiriere", "real_venit_inchiriere", "real_impozit_inchiriere",
        "str_cas_baza", "str_cas_datorat", "str_cass_baza", "str_cass_datorat",
        "bifa_cas_real", "cas_total_ven", "cas_baza", "cas_datorat", "cas_retinut_platitor",
        "cas_dif_plus", "bifa_cass_datorat_ai", "bifa_cass_datorat_dpi", "cass_total_ven_ai",
        "baza_cass_datorat_ai", "cass_datorat_ai", "cass_ret_plat_alin6_ai", "cass_dif_plus_ai",
        "cass_dif_minus6_ai", "cass_ret_plat_alin7_ai", "cass_dif_minus8_ai", "bifa_cass_real",
        "cass_ven_dpi", "cass_ven_asc", "cass_ven_cfb", "cass_ven_inv", "cass_ven_asp",
        "cass_ven_alt", "cass_total_ven", "cass_baza", "cass_datorat", "cass_retinut",
        "cass_dif_plus", "real_venit_net_recalculat_ai", "real_cas_deduc_ai",
        "real_cass_deductibil_ai", "real_venit_net_impozabil_ai", "real_venit_net_imp_redus_ai",
        "real_impozit_datorat_ai", "real_cas_venit_net_ai", "real_cas_total_ven_ai",
        "real_cas_pondere_ai", "real_cas_datorata_ai", "real_cas_deductibila_ai",
        "real_cass_venit_net_ai", "real_cass_total_ven_ai", "real_cass_pondere_ai",
        "real_cass_datorata_ai", "real_cass_calculata_ai", "real_cass_deductibila_ai",
        "real_venit_net_recalc_dpi", "real_cas_dpi", "real_venit_net_impozabil_dpi",
        "real_venit_net_imp_redus_dpi", "real_impozit_datorat_dpi", "real_cas_venit_net_dpi",
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


def cap11_sistem_real(venit_brut, chelt_deduc, pierdere_precedenta=0, caen=None):
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
    cap11 = manual.get("cap11")
    if cap11:
        try:
            cv = int(cap11.get("categ_venit"))
        except (TypeError, ValueError):
            cv = None
        if cv not in CATEG_VENIT_CAP11:
            er.append("Capitol cap11: categoria de venit %r nu e în nomenclatorul D212 (%s)."
                      % (cap11.get("categ_venit"), ", ".join(str(k) for k in sorted(CATEG_VENIT_CAP11))))
    for nume in _COPII:
        for cap in _sectiuni(manual.get(nume)):
            straine = set(cap) - _CAMPURI[nume]
            if straine:
                er.append("Capitol %s: câmpuri necunoscute (respinse de validator): %s"
                          % (nume, ", ".join(sorted(straine))))
    if isinstance(manual.get("cap11"), list):
        er.append("Capitol cap11: o singură secțiune (validatorul o primește o dată).")
    return er


def _sectiuni(cap):
    """Un capitol poate fi o secțiune (dict) sau, la cap12, o listă de secțiuni (o activitate / un loc fiecare)."""
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


def cap11_din_rip(conn, schema, an, pierdere_precedenta=0, caen=None):
    """Lantul RIP -> cap11: venitul brut si cheltuielile deductibile din operatiunile VALIDATE ale
    registrului (rip_api.fisa_d212, aceeasi sursa ca fisa afisata pe ecran). Refuza anii cu plafoane
    neverificate (refuzul fisei) si avertizeaza despre ce nu intra in calcul."""
    from core import rip_api
    f = rip_api.fisa_d212(conn, schema, an)
    if f.get("eroare"):
        raise ValueError("D212: fișa RIP nu se poate trage — " + f["eroare"])
    return cap11_sistem_real(f["venit_brut"], f["cheltuieli_deductibile"], pierdere_precedenta, caen), \
        f.get("avertisment")


def genereaza(conn, schema, perioada, manual=None):
    manual = dict(manual or {})
    an = int(getattr(perioada, "an", None) or manual.get("an_r"))
    avert = []
    if manual.get("din_rip") and not manual.get("cap11"):
        if conn is None:
            raise ValueError("D212: venitul din registrul RIP cere firma (conexiunea lipsește).")
        manual["cap11"], a = cap11_din_rip(conn, schema, an, manual.get("pierdere_precedenta") or 0,
                                           manual.get("caen"))
        if a:
            avert.append(a)
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
    prof = pull(conn, schema, perioada)
    er = erori_generare(prof, manual)
    if er:
        raise ValueError("D212 nu se poate genera: " + " ".join(er))
    calc = calcul_d212(manual)
    xml = build_xml(prof, an, None, manual, calc)
    capitole = [n for n in _COPII if manual.get(n)]
    return xml, Rezultat212(an=an, total_plata_a=calc["totalPlata_A"], capitole=capitole, avertismente=avert)
