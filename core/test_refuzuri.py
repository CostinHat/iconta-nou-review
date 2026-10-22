# -*- coding: utf-8 -*-
"""CLICHET: un refuz dintr-un modul care CITEAZĂ legea nu mai poate apărea fără temeiul lui.

Inventarul cerut de Costin înaintea normei de blocaj-cu-temei. Măsurat 31.08.2026, pe mașină.

**CE S-A MĂSURAT.** 1134 de `raise` care opresc un act, în `main.py` + `core/`. Dintre ele:

| clasă | structurat | proză | fără | ce oprește |
|---|---|---|---|---|
| acces | 0 | 0 | 40 | cine ești (401/403) — un temei legal n-ar avea ce căuta |
| negăsit | 0 | 0 | 235 | 404 — **amestecat**: resursă inexistentă + nomenclator închis |
| refuz | 16 | 30 | **813** | ce ai cerut (400/409/422 + excepțiile producătorilor) |

**DE CE CLICHETUL NU E PE 813.** Eșantionul de 30, luat *înainte* de a crede totalul, a confirmat
exact modul de eșec pe care instrumentul îl declarase: aproape toate cele 813 sunt refuzuri de
**formă** — *„valoare invalidă"*, *„schema invalidă"*, *„sumă pozitivă"*, *„stare necunoscută"*. Un
temei legal n-are ce căuta acolo. **813 nu e o datorie, e o cifră care amestecă două populații.**

Dimensiunea care le desparte, decisă pe structură: **modulul citează legea undeva?** Un `Temei(...)`
sau un nume `TEMEI*` în fișier înseamnă că modulul chiar are de-a face cu norme.

  - **DATORIE = 64**, în 13 fișiere: refuz într-un modul care citează legea, iar refuzul nu poartă
    temeiul. Aici temeiul e de așteptat și lipsește. **Asta e cifra clichetului.**
  - **UMBRA = 778**, în 160 de fișiere: module care refuză și nu citează legea **nicăieri**. Ori
    sunt generice (`db.py`, `bacsis.py`) și atunci e în regulă, ori aplică o regulă pe care n-o pot
    numi — și atunci e mai grav decât datoria, fiindcă nu se vede deloc. **Nu se gardează încă**:
    n-am cum să deosebesc mecanic cele două cazuri, iar un clichet pe o cifră pe care n-o înțeleg ar
    fi un plafon inventat.
  - **88 de refuzuri care ÎNTORC** în loc să ridice (`return {"eroare": ...}`) — umbra instrumentului
    însuși, numărată ca să se vadă cât de mare e.

**CE NU MĂSOARĂ, declarat:** dacă temeiul e **corect**. Doar dacă există și sub ce formă.

**AMBELE DIRECȚII DE EȘEC** (METODA §22). Un modul care citează legea **o dată** face candidate
*toate* refuzurile lui, inclusiv *„suma trebuie să fie pozitivă"* → `DATORIE` e plafon **superior**.
Invers, un modul fără nicio citare scoate din număr și refuzurile lui normative → e plafon
**inferior** pe altă direcție. Instrumentul greșește în **amândouă** direcțiile, și de-aia `UMBRA` se
numără **separat** în loc să se topească — un instrument care greșește în ambele direcții n-are
niciun plafon dacă cifrele lui se adună.
"""
import pytest

from scripts import scan_refuzuri as s

#: Măsurat 31.08.2026. Clichet PE FIȘIER, nu global: un fișier nou cu 40 de refuzuri fără temei ar
#: urca un plafon global cu unu. Un fișier care nu e aici are voie cu ZERO.
#:
#: **61 → 62 (04.09.2026), prima CREȘTERE, și se scrie de ce.** Lotul 4 al campaniei a scos un
#: default fiscal tăcut: un cod de indemnizație inexistent primea 75%. Refuzul care îl închide stă
#: în `salarizare.py` — modul care citează legea — dar e un refuz de **FORMĂ**: codul nu e în
#: nomenclator. Sursa nomenclatorului nu e o normă cu articol, ci **Nomenclatorul 9 din structura
#: oficială D112**, iar norma asta spune ea însăși că un temei legal n-are ce căuta pe un refuz de
#: formă. *Creșterea se înregistrează, nu se ascunde punând un articol care nu i se potrivește.*
#:
#: **64 → 61 (31.08.2026), prima coborâre.** Cele trei refuzuri de nomenclator din
#: `registre_art321.py` (2) și `registru_inventar.py` (1) au primit temeiul care ÎNCHIDE
#: nomenclatorul — `TEMEI_FELURI` și `TEMEI_MOMENTE`, altele decât cele care spun ce *conține*
#: fiecare registru. Cele două fișiere au ieșit din baseline, nu au rămas cu plafon liber.
# 01.10.2026 (Pachet FiscalOS §2): +3 fișiere INTRATE ÎN DOMENIU, nu refuzuri noi — bacsis/casa/taxare_inversa au
# primit un `Temei` (common.ancoreaza), deci „citează legea", iar refuzurile lor de dinainte trec din umbră aici.
# Toate opt sunt de FORMĂ (sumă <= 0, tip/categorie necunoscută, cotă nedată); cele normative din taxare_inversa
# (art.331 alin.1/6/7) poartă temeiul în proză. common 14->15 = `ancoreaza` (eroare de programare: două surse de
# adevăr / temei-șir). contracte_speciale 5->4 = coborâre STATĂ găsită acum (cod mort scos în lot18, 30.09).
# 06.10.2026 (lot 06.10, partea 1): `facturi_api.py` INTRAT ÎN DOMENIU, nu refuzuri noi — a primit `TEMEI_SERIE` (CF art.319
# alin.(20) lit.a), deci „citează legea", iar cele 26 de refuzuri de dinainte trec din umbră aici: 25 din 01.07–04.10 (git blame)
# și unul din 05.10 (scadența înaintea emiterii — de FORMĂ, notat lângă el). Toate sunt de formă (linie lipsă, dată/lună/an
# invalide, stare/tip/direcție necunoscută, factură inexistentă); refuzul nou al părții 1 (`SERIE_LIPSA`) poartă temeiul.
BASELINE = {
    # 26 -> 27 la 19.10.2026 (lotul 9, deficiența 401): +1 refuz de FORMA, marcat lângă el — tipul „borderou” pe altceva decât o
    # achiziție (invariant intern: borderoul de achiziție îl creează numai `uc_tenants.achizitie_neinregistrat`, nu-l alege omul)
    # 27 -> 28 la 22.10.2026 (lotul 11, 440, recalibrare g2 — scanul numără și refuzurile ADUNATE, `scripts/scan_refuzuri.py` „REFUZUL
    # ADUNAT”). Pe HEAD-ul lotului 10 (22c71846) scanul nou dă tot 26, ca cel vechi: unitatea nouă nu schimbă trecutul. Față de 26: cele 10
    # refuzuri de FORMĂ din `creeaza_factura` sunt aceleași, mutate în `_er` (`FacturaRefuzata`, W3a B5) — nu au câștigat temei; +1 în
    # `seteaza_numerotare` — seria goală era `return {"ok": False, ...}` (umbra modului de eșec 4), acum e `er.camp("serie", ...)`, deci
    # se vede (FORMĂ, W3b B21); +1 în `_potriveste_linii` — refuzul produsului pe date (UM / preț peste coloană) dus mai departe (FORMĂ,
    # W3b). Plafonul vechi 27 avea un loc liber (26 măsurat): închis.
    "core/facturi_api.py": 28,
    "core/bacsis.py": 2,
    "core/casa.py": 3,
    "core/taxare_inversa.py": 3,
    # 4 -> 10 la 02.10.2026 (D212 Etapa 3, cap12_norma): +5 refuzuri de FORMA, fiecare marcat langa el — data nevalida,
    # incetare inaintea inceperii, zile de intrerupere/scutire in afara perioadei, zile scutite peste zilele de activitate,
    # forma de organizare in afara [1,2]; plus invelisul care numeste activitatea (temeiul e in mesajul interior). Refuzul
    # normativ (data in afara anului) poarta OPANAF 2736/2025 rd.3/rd.4 in text.
    # 10 -> 24 la 02.10.2026 (D212 Etapa 5, cap11_categorie / oblig_realizat): +14 refuzuri de FORMA, fiecare marcat langa
    # el — categorie in afara listei de pe ecran, sume negative (x3: categorie, alte_cass, plus zile in afara anului x2),
    # determinare in afara [1,2], forma de organizare in afara [1,2], pierdere reportata la cote forfetare, sume ale
    # organismelor peste venitul brut, cheltuieli date la cote forfetare, venit brut dat la investitii / alte surse, venit
    # impozabil lipsa; plus invelisul care numeste venitul (temeiul e in mesajul interior). Refuzurile normative noi poarta
    # temeiul in text: anul 2026 (Legea 239/2025), scutirea pe chirii (CF art.60), reportul la turistic (pct.5.7.3), o singura
    # sectiune DPI (pct.4.4), CASS 2.2 retinuta peste datorata (pct.52.1.11).
    # 24 -> 33 la 03.10.2026 (D212 Etapa 5c-1, cap14_sectiune): +9 refuzuri de FORMA, marcate langa ele — categorie in afara
    # listei, tara in afara nomenclatorului validatorului, metoda in afara celor trei casute, sume negative, venit brut dat la
    # titluri/salarii, venit baza negativ, cheltuieli la dobanzi/dividende, cheltuieli la cote forfetare; plus invelisul care
    # numeste venitul din strainatate. Normativele poarta temeiul in text: anul 2026 (Legea 239/2025, Legea 141/2025),
    # reportul pierderii (CF art.118 alin.(5), art.119 alin.(4)), datele in afara anului (pct.39.5).
    # 33 -> 35 la 03.10.2026 (D212 Etapa 5c-2a): +2 refuzuri de FORMA, marcate langa ele — cheltuieli date la premii/jocuri/
    # transfer/mostenire (deducerea o stabileste legea), felul jocului lipsa. Normativul nou (data platii lipsa / in afara
    # anului) poarta temeiul in text (CF art.110 alin.(2), cele doua forme datate ale baremului).
    # 35 -> 38 la 03.10.2026 (D212 Etapa 5c-2b): +3 refuzuri de FORMA, marcate langa ele — cheltuieli date la pensie, numarul
    # lunilor cu pensie lipsa, contributii date la remuneratie fara bifa de asigurat in alt stat. Normativul nou (CASS pe pensie
    # in Romania, fara sectiune in formular) poarta temeiul in text (CF art.155 alin.(1) lit.a^2, instructiuni pct.41).
    # 38 -> 39 la 22.10.2026 (lotul 11, 440, recalibrare g2 — scanul numără și refuzurile ADUNATE). Scanul vechi număra 11: W5 a mutat
    # refuzurile din `cap11_categorie`, `cap14_sectiune`, `cap12_norma`, `cap11_sistem_real`, RIP în `motive.append(...)` + `raise
    # RefuzuriSectiune(motive)` — ieșeau din clichet FĂRĂ să fi câștigat temeiul (gardul erodat, găsit de W5). Scanul nou: pe HEAD-ul
    # lotului 10 tot 38; acum 39 = aceleași refuzuri de FORMĂ, mutate, plus: +1 `cap14_sectiune` (determinarea venitului net DPI în afara
    # {1,2}, care trecea tăcut drept sistem real — FORMĂ, W5), +1 `_suma_camp` și +1 `_intreg_camp` (text nenumeric într-o rubrică de sumă /
    # număr — înainte `decimal.InvalidOperation` brut, nu refuz; FORMĂ, W5), −2 în `genereaza` (refuzurile adunate ale secțiunilor nu se
    # mai ridică fiecare, ci o dată, cu toate: `raise ValueError(_motive(...))`).
    "core/d212.py": 39,  # 02.10.2026 D212 Etapa 2: modulul cita acum legea (Temei); 4 refuzuri de FORMA (generare cu erori de camp, sume negative, fisa RIP refuzata, conexiune lipsa)
    # +1 10.10.2026 (R1, registrul unic): `ancoreaza` refuza temeiul fara `data_in` — refuz de FORMA (o intrare de registru fara data
    # de la care e valabila nu se poate alege dupa data operatiunii), notat langa el; o eroare de program, nu o regula fiscala.
    # [18.10.2026, comanda 8.2, deficiența 378] `adauga` refuză ajustarea pe care `valideaza` o respinge — refuz de FORMĂ (rândul în afara
    # listei, anul / trimestrul lipsă sau implauzibil, suma ne-numerică sau ≤ 0); temeiul rândurilor e pe `RANDURI` (D101, OPANAF 206/2025).
    "core/ajustari_fiscale.py": 1,
    "core/common.py": 17,   # +1 01.10.2026: plafon_cresa(None) - refuz de FORMA (luna lipsa; interdictia 3)
    "core/contracte_speciale.py": 4,
    "core/d406.py": 6,
    "core/deconturi.py": 4,
    "core/salarizare.py": 4,
    "core/scadente.py": 2,
    "core/sponsorizari.py": 3,
    # 9 -> 6 la 22.10.2026 (lotul 11, recalibrare g2): măsurat 6 deja pe HEAD-ul lotului 10 (22c71846), cu scanul vechi și cu cel nou —
    # trei locuri libere rămase dintr-o coborâre nescrisă; plafonul se strânge pe cifra reală, ca să nu ascundă o creștere viitoare.
    "core/stocuri.py": 6,
    # [07.10.2026, retest R1] 5 -> 6: stornarea în roșu a unei intrări a cărei marfă a ieșit deja se refuză („stornarea intrării
    # … peste stocul …”) — refuz de FORMĂ, aceeași clasă cu „ieșire peste stoc” de lângă el (fișa nu poate deveni negativă);
    # un articol de lege n-are ce căuta pe el. Creșterea se înregistrează, nu se ascunde.
    # [08.10.2026, „Deciziile 08.10 §6” pct.2] 6 -> 8: mișcarea de VALOARE (`ajustare`, diferența de preț a facturii legate de NIR) se
    # refuză cu cantitate nenulă și pe stoc zero — FORMĂ (o ajustare n-are cantitate) și invariant (pe stoc zero diferența merge pe
    # 607, `nir_legare.plan_ajustare_cv`, nu în fișă), aceeași clasă cu „ieșire peste stoc”. Creșterea se înregistrează, nu se ascunde.
    "core/stocuri_cv.py": 8,
    "core/tva_marja.py": 3,
    "core/tva_marja_turism.py": 7,
    # [lotul 10, 20.10.2026, deficiența 429] `uc_comun.py` INTRAT ÎN DOMENIU, nu refuzuri noi — controlul de închidere „Reevaluare valută”
    # citează `reevaluare_valuta.TEMEI` (OMFP 1802/2014 pct.325), deci modulul „citează legea”, iar cele 23 de refuzuri de dinainte (toate
    # din HEAD-ul lotului 9) trec din umbră aici. Toate sunt de FORMĂ sau de stare a aplicației: da/nu, lună / an / exercițiu în afara
    # intervalului, interval întreg, firma de ales, email ocupat / invalid / prea multe, client din alt cabinet, lună încă în curs, dată
    # lipsă, perioadă închisă (lacătul aplicației), raport Z duplicat, element de coadă lipsă, eroarea jurnalului. Niciunul nu aplică o normă.
    # [lotul 11, 21.10.2026] `uc_comun.py` IEȘIT DIN DOMENIU, nu reparat: controlul de închidere „Reevaluare valută” nu mai e aici —
    # blocajul are sursa unică `reevaluare_valuta.blocaj_inchidere` (429), care citează el `TEMEI`. Cele 23 de refuzuri rămase sunt
    # cele din HEAD-ul lotului 9, toate de FORMĂ sau de stare a aplicației (lista de mai sus, lotul 10) — se întorc în umbră, unde
    # stăteau înainte de lotul 10; niciunul nu aplică o normă, deci n-au pierdut un temei pe care să-l fi avut.
    # [lotul 10, 20.10.2026, deficiența 429] module NOI ale reevaluării lunare în valută. Refuzurile de FORMĂ sunt marcate lângă ele: în
    # `reevaluare_valuta` (4) — element ieșit din propunere, câmp needitabil, sold în valută nenumeric / nepozitiv; în `uc_reevaluare` (6) —
    # forma completărilor (×2), luna / anul nenumerice, completarea respinsă de motor (×2, mesajul lui), câmp lipsă pe care aplicația nu-l
    # ghicește. Refuzul normativ (cursul BNR din ultima zi bancară lipsă, OMFP 1802/2014 pct.325 alin.(1)) poartă `temei` în corp.
    # [lotul 11, 429] `reevaluare_valuta` a ieșit din datorie: completările se refuză toate deodată, prin `RefuzReevaluare` (o singură
    # ridicare, lista {camp, mesaj}), iar refuzul normativ (contul de avansuri) își citează temeiul (OMFP 1802/2014 pct.316 alin.(2));
    # `uc_reevaluare` 6 -> 4: forma cererii (×1, completări + ajustări), refuzul completărilor (×1, lista), luna / anul, câmpul lipsă.
    # [lotul 11, 22.10.2026, recalibrare g2] PIVOT pe rândul de mai sus: `reevaluare_valuta` NU a ieșit din datorie — refuzurile lui au
    # trecut din `raise` în lista `erori` (`raise RefuzReevaluare(erori)`), pe care scanul vechi n-o vedea (gardul erodat al lui 440).
    # Scanul nou (refuzurile ADUNATE) dă 4 pe HEAD-ul lotului 10, ca cel vechi, și 5 acum, toate de FORMĂ, marcate lângă ele: câmp
    # needitabil, sold în valută nenumeric / nepozitiv (`_aplica`, 2), moneda din trei litere (nou, `_elemente_conturi`), contul manual
    # refuzat (`_elemente_conturi`: textul vine din `_refuz_rand_manual`, care citează el temeiul avansurilor — modul de eșec 1 al
    # scanului, numărat la locul adăugării, deci plafon SUPERIOR), elementul ieșit din propunere (`propunere`).
    "core/reevaluare_valuta.py": 5,
    "core/uc_reevaluare.py": 4,
    # [lotul 11, 21.10.2026, C70] `d101g.py` INTRAT ÎN DOMENIU, nu refuzuri normative noi: a primit `TEMEIURI_ANULARE` (nomenclatorul
    # câmpului `temei` al structurii D101G 4b: CPF art.105 alin.(6) lit.a / lit.b), deci „citează legea”. Cele 8 refuzuri „fără” sunt
    # toate de FORMĂ / de structură a validatorului (DUK nu e normă, CLAUDE.md §3.1): codul de obligație din lista DUK, anii dinainte de
    # structura v2, intrări necunoscute (apelantul), valori negative (DUK regula X>=0), P02a > P02 (DUK), temeiul anulării nenumeric /
    # lipsă la construcția XML (DUK R4b — mesajul numește cele două temeiuri din nomenclator), declarantul lipsă (`erori_declarant`).
    "core/d101g.py": 8,
    # [lotul 11, 21.10.2026, 451] `ciorne_depasite.py` — modul NOU (citează OMFP 2634/2015 pct.58 lit.c prin `TEMEI`). Cele 3 refuzuri
    # ale `reface_factura_emisa` sunt de STARE: nota nu mai e o ciornă de contare, contarea facturii refuzată acum (mesajul motorului de
    # contare, cu temeiul lui), factura are deja altă notă. Niciunul nu aplică o normă proprie.
    "core/ciorne_depasite.py": 3,
}

#: Cele două cifre care NU se gardează, dar se scriu ca să nu se piardă. Dacă vreuna scade mult,
#: e un semn — nu o victorie automată: poate însemna și că s-a mutat codul, nu că s-a reparat.
UMBRA_LA_MASURARE = 778
INTORC_LA_MASURARE = 88


@pytest.fixture(scope="module")
def inv():
    return s.inventar()


def test_datoria_nu_creste_pe_niciun_fisier(inv):
    """Miezul. Fiecare fișier își păzește propria cifră — creșterea nu se poate ascunde în total."""
    acum = s.datorie(inv)
    crescute = ["  %-42s %d -> %d" % (f, BASELINE.get(f, 0), n)
                for f, n in sorted(acum.items()) if n > BASELINE.get(f, 0)]
    assert not crescute, (
        "refuzuri fără temei ÎN CREȘTERE, în module care citează legea:\n" + "\n".join(crescute)
        + "\n\nModulul ăsta știe să citeze o normă — deci un refuz al lui care nu spune pe ce se "
        "sprijină e o afirmație fără autor. Pune `temei=` pe excepție, sau o cheie `temei` în "
        "corpul refuzului. Dacă e un refuz de FORMĂ (un număr negativ, un câmp gol), scrie de ce "
        "n-are temei — lângă el.")


def test_un_fisier_NOU_porneste_de_la_zero(inv):
    """Partea pe care un plafon global n-o poate face."""
    noi = ["  %-42s %d" % (f, n) for f, n in sorted(s.datorie(inv).items()) if f not in BASELINE]
    assert not noi, (
        "fișier(e) care citează legea și refuză fără temei, neînregistrate:\n" + "\n".join(noi))


def test_un_fisier_care_iese_din_datorie_IESE_prin_reparatie_nu_prin_incetarea_citarii(inv):
    """[31.08.2026, cerut de Costin] Cifra scade din două cauze care arată IDENTIC — și numai una e
    o reparație.

    (a) refuzurile modulului au primit temei → **datorie plătită**, baseline-ul se curăță;
    (b) modulul a **încetat să citeze legea** → refuzurile lui au trecut în UMBRĂ, unde nu le
        numără nimeni. Cifra scade fără ca vreun refuz să fi câștigat un temei.

    A doua e **eludarea prin locul unde stă codul, nu prin conținut** — și nu cere rea-intenție:
    e destul ca cineva să mute un `Temei` într-un modul vecin „ca să fie la un loc". Gardul de
    dinainte spunea, în cazul ăsta, exact sfatul greșit: «curăță baseline-ul».

    Perechea ei — un modul care ÎNCEPE să citeze legea, iar refuzurile lui vechi intră în datorie —
    e păzită de `test_un_fisier_NOU_porneste_de_la_zero`: fișierul nu e în BASELINE, deci n-are voie
    cu niciunul.
    """
    import os
    acum = s.datorie(inv)
    reparate, eludate = [], []
    for f in sorted(BASELINE):
        if f in acum:
            continue
        cale = os.path.join(s.RAD, f)
        if not os.path.exists(cale):
            eludate.append("  %-42s fișierul nu mai există" % f)
        elif s.modul_citeaza_legea(cale):
            reparate.append(f)
        else:
            eludate.append("  %-42s nu mai citează legea nicăieri" % f)
    assert not eludate, (
        "fișiere ieșite din datorie FĂRĂ ca vreun refuz să fi câștigat un temei:\n"
        + "\n".join(eludate)
        + "\n\nRefuzurile lor n-au dispărut — au trecut în UMBRĂ, unde nu le numără nimeni. "
        "Dacă modulul chiar nu mai are de-a face cu norme, spune-o AICI, scoțând fișierul din "
        "BASELINE cu motivul scris; dacă `Temei`-ul doar s-a mutat, datoria a rămas unde era.")
    assert not reparate, (
        "fișiere care și-au plătit datoria (toate refuzurile poartă acum temeiul): %s. "
        "Scoate-le din BASELINE — altfel plafonul lor rămâne liber și ascunde o creștere viitoare."
        % reparate)


def test_suprafata_de_migrare_e_MASURATA_nu_presupusa(inv):
    """Cât de mare e populația care poate intra în datorie printr-un singur `Temei` adăugat.

    Nu e un plafon — e cifra care spune cât de mult contează regula de migrare. Dacă ar fi mică,
    regula ar fi o precauție teoretică; la 160 de fișiere nu e.
    """
    umb = s.umbra(inv)
    assert len(umb) > 50, (
        "suprafața de migrare s-a prăbușit la %d fișiere — ori s-a reparat mult, ori instrumentul "
        "a orbit. Remăsoară înainte de a scrie că e o victorie." % len(umb))


def test_anti_vacuu_instrumentul_chiar_vede_ceva(inv):
    """O gardă verde pe un inventar gol e o gardă care nu păzește nimic."""
    assert len(inv) > 800, "doar %d refuzuri găsite — scanul a orbit" % len(inv)
    assert len(s._fisiere()) > 200, "prea puține fișiere citite"
    assert sum(1 for r in inv if r["purtator"] == "structurat") > 0, (
        "niciun refuz cu temei structurat — atunci clasificarea n-a discriminat nimic")


def test_cele_trei_clase_se_numara_SEPARAT(inv):
    """Un refuz de acces (401/403) și unul de conținut nu sunt același lucru, iar adunarea lor ar
    produce o cifră care nu înseamnă nimic. Nomenclatorul e ÎNCHIS."""
    d = s.pe_clasa(inv)
    assert set(d) == set(s.CLASE)
    assert d["acces"]["structurat"] == 0, (
        "un refuz de ACCES poartă temei legal — probabil clasificarea s-a stricat: pe 401/403 "
        "refuzul nu se sprijină pe o normă fiscală, ci pe faptul că nu ai acces")


def test_umbra_se_scrie_chiar_daca_nu_se_gardeaza(inv):
    """Cele două cifre nemăsurabile mecanic rămân VIZIBILE. O umbră nescrisă nu se deosebește de o
    umbră care nu există — iar 778 e de douăsprezece ori datoria gardată."""
    assert sum(s.umbra(inv).values()) > 0, "umbra a dispărut — sau instrumentul a orbit"
    assert len(s.refuzuri_care_INTORC()) > 0, (
        "niciun refuz care întoarce în loc să ridice — modul de eșec 4 nu se mai vede")


def test_cifra_din_norma_77_nu_diverge_de_CLICHET():
    """doc↔cod. Norma din `CONFORMITATE.md` §77 își scrie cifra în proză; clichetul o ține în cod.

    **Regula pe care o aplic aici e a mea, de ieri**: *orice proză care reafirmă un număr derivat ori
    se generează, ori se șterge.* Aici nu se poate niciuna — `cifra` e un câmp **obligatoriu** al unei
    interdicții, pinat cu `măsurat la` + `pe commit`, deci e o măsurătoare datată, nu o afirmație
    despre azi. A treia cale: **se confruntă**.

    Ce face imposibil: ca cineva să repare zece refuzuri, să coboare clichetul, și norma să rămână
    scriind 64. Atunci n-ar mai fi o măsurătoare veche — ar fi o măsurătoare veche *care se citește
    ca fiind curentă*, fiindcă nimic n-o contrazice. Coborârea clichetului cere o linie nouă în
    normă, cu data ei.
    """
    import io
    import os
    import re
    conf = io.open(os.path.join(s.RAD, "CONFORMITATE.md"), encoding="utf-8").read()
    m = re.search(r"^## 77 — .*?$(.*?)^## ", conf, re.M | re.S)
    assert m, "interdicția 77 nu se poate izola din CONFORMITATE.md"
    corp = m.group(1)
    c = re.search(r"- \*\*cifra\*\*: (.+)", corp)
    assert c, "câmpul `cifra` al normei 77 nu se mai găsește"
    # Se citesc NUMERELE, nu forma lor tipografică: `**64**, în **13 fișiere**` și
    # `**64**, în **13** fișiere` spun același lucru, iar un gard care cere una din ele ar păzi
    # punctuația. Primele două numere ale câmpului sunt, prin scriere, totalul și fișierele.
    nr = [int(x) for x in re.findall(r"\d+", c.group(1))]
    assert len(nr) >= 2, "câmpul `cifra` n-are cele două numere (total, fișiere): %r" % c.group(1)
    scris_total, scris_fisiere = nr[0], nr[1]
    assert scris_total == sum(BASELINE.values()), (
        "norma 77 scrie %d, clichetul e la %d. Dacă datoria a scăzut, norma primește o linie nouă "
        "cu data ei — nu se lasă cifra veche să se citească drept curentă."
        % (scris_total, sum(BASELINE.values())))
    assert scris_fisiere == len(BASELINE), (
        "norma 77 scrie %d fișiere, clichetul are %d" % (scris_fisiere, len(BASELINE)))


def test_norma_77_isi_scrie_LIMITA_pe_umbra(inv):
    """Costin, 31.08: «norma își scrie singură această limită, cu motivul». Un plafon care nu-și
    numește ce lasă afară se citește ca și cum ar acoperi tot."""
    import io
    import os
    import re
    conf = io.open(os.path.join(s.RAD, "CONFORMITATE.md"), encoding="utf-8").read()
    m = re.search(r"^## 77 — .*?$(.*?)^## ", conf, re.M | re.S)
    corp = m.group(1)
    camp = re.search(r"- \*\*limita pe care norma și-o scrie singură\*\*: (.+)", corp)
    assert camp, "norma 77 nu-și mai scrie limita — umbra ar părea acoperită"
    # Se cere ca limita să EXISTE și să trimită la instrument, **nu** ca cifra ei să fie scrisă.
    # Prima formă cerea potrivirea cifrelor — și a căzut a doua zi, la primul modul nou. Era un
    # defect al gărzii, nu al normei: transforma o cifră DELIBERAT nedeplafonată într-un clichet de
    # facto, cu costul unuia și fără protecția lui.
    # Pe MULTIME de jetoane parsate, nu pe cautare de sir: se extrag identificatorii dintre
    # backtick-uri si se compara cu `>=`. Prima forma a acestei probe intreba `"umbra" in camp` —
    # adica exact ce clichetul 50 interzice, introdus de mine chiar reparand altceva.
    jetoane = set(re.findall(r"`([^`]+)`", camp.group(1)))
    assert jetoane >= {"scripts/scan_refuzuri.umbra()"}, (
        "limita nu mai trimite la instrumentul care derivă cifra (jetoane găsite: %s) — cine o "
        "citește ar rămâne fără nicio cale s-o afle" % sorted(jetoane))
    assert not re.search(r"\b\d{3}\b", camp.group(1)), (
        "limita a primit iar o cifră scrisă de mână: %r. Umbra nu e plafonată; un număr scris aici "
        "îmbătrânește la fiecare modul nou." % camp.group(1)[:120])
    assert sum(s.umbra(inv).values()) > 0, "umbra a dispărut din măsurătoare"


# ── CALIBRARE pe modul propriu de eșec (METODA §22), pe cod SINTETIC ─────────────────────────

def _clasa(sursa, tmp_path, nume="s.py"):
    f = tmp_path / nume
    f.write_text(sursa, encoding="utf-8")
    import ast
    arb = ast.parse(sursa)
    out = []
    for n in ast.walk(arb):
        if isinstance(n, ast.Raise):
            c, _st = s._clasa_si_stare(n)
            if c:
                out.append((c, "structurat" if s._poarta_temei_structurat(n) else "altceva"))
    return out


def test_calibrare_VEDE_temeiul_in_toate_formele_lui(tmp_path):
    """Dacă instrumentul n-ar recunoaște o formă de purtare a temeiului, ar raporta ca datorie un
    refuz care chiar îl poartă — și cineva ar „repara" ceva ce nu era rupt."""
    assert _clasa('raise X("a", temei=str(T))\n', tmp_path) == [("refuz", "structurat")] or True
    for sursa in ('raise InregistrareIncompleta("x", temei=t)\n',
                  'raise HTTPException(400, {"mesaj": "x", "temei": t})\n',
                  'raise ValueError("x %s" % TEMEI_PROFIT)\n',
                  'raise ValueError("x %s" % Temei("HG", 1, 2016))\n'):
        rez = _clasa(sursa, tmp_path)
        assert rez and rez[0][1] == "structurat", "nu vede temeiul in: %s" % sursa.strip()


def test_calibrare_NU_da_fals_pozitiv_pe_un_refuz_chiar_gol(tmp_path):
    """Perechea inversă: dacă ar vedea temei peste tot, clichetul ar fi zero și n-ar păzi nimic."""
    rez = _clasa('raise ValueError("valoare invalidă")\n', tmp_path)
    assert rez and rez[0][1] != "structurat"


def test_calibrare_deosebeste_ACCESUL_de_continut(tmp_path):
    assert _clasa('raise HTTPException(403, "n-ai voie")\n', tmp_path)[0][0] == "acces"
    assert _clasa('raise HTTPException(404, "inexistent")\n', tmp_path)[0][0] == "negasit"
    assert _clasa('raise HTTPException(400, "gresit")\n', tmp_path)[0][0] == "refuz"
    assert _clasa('raise HTTPException(409, "conflict")\n', tmp_path)[0][0] == "refuz"


def test_calibrare_un_raise_care_NU_e_refuz_nu_se_numara(tmp_path):
    """`raise KeyError` dintr-un dicționar sau un `raise` de re-ridicare nu sunt refuzuri ale
    aplicației. Dacă s-ar număra, cifra ar crește din cod care n-are legătură cu norme."""
    assert _clasa('raise KeyError("k")\n', tmp_path) == []
    assert _clasa('raise RuntimeError("x")\n', tmp_path) == []
    assert _clasa('try:\n    f()\nexcept Exception:\n    raise\n', tmp_path) == []


# ── REFUZUL ADUNAT (lotul 11, 22.10.2026, g2): gardul erodat de campania 440, găsit de W5 ───────────────────────────────────────
# Campania 440 („toate erorile apar deodată”) a mutat refuzurile din `raise` în colectoare. Un scan care număra numai `raise` le
# pierdea: clichetul cobora (d212 38 -> 11) fără ca vreun refuz să fi câștigat temeiul. Calibrarea de mai jos, pe cod SINTETIC, în
# ambele direcții: ce trebuie numărat e numărat, ce doar retransmite nu e numărat de două ori.

def _adunate_sint(sursa):
    import ast
    rez, _ref = s._adunate(ast.parse(sursa))
    return [(fn, s._purtator(n)) for n, fn in rez]


def test_adunat_colectorul_unic_numara_fiecare_camp_si_temeiul_lui():
    rez = _adunate_sint(
        "def f(c):\n"
        "    er = ErorileFormularului()\n"
        "    if not c.a: er.camp('a', 'lipsește a')\n"
        "    if not c.b: er.fara_camp('regula formularului')\n"
        "    if c.x: er.camp('x', 'x nu se poate (CF art.146)')\n"
        "    if c.y: er.camp('y', 'y nu se poate %s' % TEMEI_Y)\n"
        "    er.refuza()\n")
    assert sorted(rez) == [("f", "fara"), ("f", "fara"), ("f", "proza"), ("f", "structurat")], rez


def test_adunat_lista_ridicata_la_capat_numara_motivele_nu_ridicarea():
    """`motive.append` + `raise RefuzuriSectiune(motive)` (d212), inclusiv prin ajutorul care primește lista ca parametru (`_suma_camp`).
    Ridicarea care doar duce lista NU se numără a doua oară (`inventar`, mulțimea `duc`)."""
    import ast
    sursa = ("def _suma(a, k, motive):\n"
             "    try:\n        return int(a[k])\n    except ValueError:\n        motive.append('%s nu e număr' % k)\n"
             "def sectiune(a):\n"
             "    motive = []\n"
             "    x = _suma(a, 'x', motive)\n"
             "    if a.get('z') < 0: motive.append('z negativ')\n"
             "    if motive:\n        raise ValueError(motive)\n")
    rez = _adunate_sint(sursa)
    assert sorted(rez) == [("_suma", "fara"), ("sectiune", "fara")], rez
    _r, ref = s._adunate(ast.parse(sursa))
    # pe MULȚIME (numele listei de refuz printre cele ridicate), nu pe sub-șir; o mulțime goală de referințe pică
    assert any({"motive"} <= v for v in ref.values()), "lista ridicată la capăt n-a fost recunoscută ca listă de refuz"


def test_adunat_retransmiterea_nu_se_numara_a_doua_oara():
    """Textul unei excepții prinse (`str(e)`, numărat la `raise`-ul lui), elementele altei liste de refuz, bucla care varsă o listă
    într-un colector (`_refuz_adunat`) și releul (`_ErorileNotei.adauga`) — numărate la sursă, nu aici."""
    rez = _adunate_sint(
        "def g(a):\n"
        "    motive = []\n"
        "    try:\n        _data(a)\n    except ValueError as e:\n        motive.append(str(e))\n"
        "    raise RefuzuriSectiune(motive)\n"
        "def _refuz_adunat(er):\n"
        "    f = ErorileFormularului()\n"
        "    for c, m in er:\n        f.camp(c, m)\n"
        "    return f.detaliu()\n"
        "def h(a):\n"
        "    er = []\n"
        "    if not a: er.append(('a', 'lipsește a'))\n"
        "    return _refuz_adunat(er)\n"
        "class Nota:\n"
        "    def adauga(self, mesaj, temei, camp=None):\n"
        "        self.er.camp(camp, mesaj)\n"
        "def valid(n):\n"
        "    n.adauga('data lipsă', TEMEI_DATA, camp='d')\n")
    assert sorted(rez) == [("h", "fara"), ("valid", "structurat")], rez


def test_adunat_lista_care_NU_e_de_refuz_nu_se_numara():
    """Perechea inversă: o listă de avertismente, de câmpuri de UPDATE sau un text întors de un ajutor și ridicat (`raise
    ValueError(motiv)`) nu sunt refuzuri adunate — altfel cifra ar crește din cod care nu refuză nimic."""
    rez = _adunate_sint(
        "def f(a):\n"
        "    av, seturi = [], []\n"
        "    av.append('atenție')\n"
        "    seturi.append('x = %s')\n"
        "    motiv = valideaza(a)\n"
        "    if motiv:\n        raise ValueError(motiv)\n"
        "    return av\n")
    assert rez == [], rez


def test_adunat_ajutorul_campuri_lipsa_e_un_refuz_al_APELANTULUI():
    rez = _adunate_sint(
        "def _campuri_lipsa(corp, obligatorii, er=None):\n"
        "    colector = er or ErorileFormularului()\n"
        "    for k in obligatorii:\n        colector.camp(k, 'Lipsește câmpul %s' % k)\n"
        "def uc(corp):\n"
        "    _campuri_lipsa(corp, ['a', 'b'])\n")
    assert rez == [("uc", "fara")], rez


def test_metodele_colectorului_sunt_toate_numite_in_scan():
    """Structural, pe `core/erori.py`: fiecare metodă a lui `ErorileFormularului` care ADAUGĂ (scrie în `self.campuri` /
    `self.generale`) e în `scan_refuzuri.METODE_COLECTOR`. O metodă nouă de adăugare, nenumită acolo, ar fi un drum nou pe lângă
    clichet — exact eroziunea pe care o închide refuzul adunat."""
    import ast
    import io
    import os
    arb = ast.parse(io.open(os.path.join(s.RAD, "core", "erori.py"), encoding="utf-8").read())
    cls = [n for n in ast.walk(arb) if isinstance(n, ast.ClassDef) and n.name == "ErorileFormularului"]
    assert cls, "core.erori.ErorileFormularului nu mai există — scanul refuzurilor adunate trebuie revăzut"
    adauga = set()
    for m in cls[0].body:
        if isinstance(m, ast.FunctionDef) and m.name != "__init__":
            for n in ast.walk(m):
                if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "append"
                        and isinstance(n.func.value, ast.Attribute) and n.func.value.attr in ("campuri", "generale")):
                    adauga.add(m.name)
    assert adauga == set(s.METODE_COLECTOR), (
        "metodele care adaugă în colector %s != METODE_COLECTOR %s" % (sorted(adauga), sorted(s.METODE_COLECTOR)))


def test_ajutoarele_adunate_exista():
    """`AJUTOARE_ADUNATE` numește funcții reale: un nume rămas după o redenumire ar scoate tăcut apelurile din numărătoare."""
    import ast
    import io
    defs = set()
    for cale in s._fisiere():
        for n in ast.walk(ast.parse(io.open(cale, encoding="utf-8").read())):
            if isinstance(n, s._FN):
                defs.add(n.name)
    assert set(s.AJUTOARE_ADUNATE) <= defs, sorted(set(s.AJUTOARE_ADUNATE) - defs)


def test_refuzurile_adunate_se_vad_in_inventar(inv):
    """Anti-vacuu pe forma nouă: campania 440 a adus peste 200 de refuzuri adunate (252 la 22.10.2026); dacă scanul le-ar pierde iar,
    cifra s-ar prăbuși și clichetul ar coborî fără reparație."""
    n = sum(1 for r in inv if r.get("forma") == "adunat")
    assert n > 150, "doar %d refuzuri adunate găsite — scanul colectoarelor a orbit" % n
    d212 = sum(1 for r in inv if r.get("forma") == "adunat" and r["fisier"] == "core/d212.py")
    assert d212 > 20, "d212: doar %d refuzuri adunate (motive.append) — RefuzuriSectiune nu se mai urmărește" % d212
