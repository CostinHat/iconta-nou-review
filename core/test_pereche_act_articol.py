# -*- coding: utf-8 -*-
"""GARD [31.08.2026, faza 2]: un temei nu numește un act care nu conține articolul lui.

**Instanța care a deschis clasa**, găsită măsurând interdicția 55: `OG 16/2022 art. 97`. Articolul
97 nu e al ordonanței — OG 16/2022 spune *„articolul 97 alineatul (7) … se modifică"*. Temeiul
numește actul **MODIFICATOR** cu articolul actului **MODIFICAT**. Confirmat la sursă și pe
`OUG 8/2026` (*„articolul 282, alineatul (3) se modifică"*).

Consecința: orice verificare de vigoare pe perechea aia întreabă **documentul greșit**. Iar
`COTE.impozit_dividend` are **patru** temeiuri și **niciunul** nu se confruntă cu documentul lui.

CE FACE IMPOSIBIL:
  1. o pereche (act, articol) NOUĂ care nu se poate confrunta — clichetul nu poate crește;
  2. dispariția tăcută a unei perechi confirmate — se cere și pragul de jos, pe confirmate;
  3. întoarcerea **celei de-a cincea reparații** din `articol_in_act`: o citare dintr-un marcaj de
     consolidare nu are voie să taie articolul (măsurat: tăia `CF art. 78` de la 16.719 la 532 de
     caractere și îi ascundea cinci din șase ani de modificare — în direcția liniștitoare);
  4. o a doua implementare a localizării articolului: scriptul trebuie să IMPORTE modulul.

CE NU FACE, declarat:
  - **nu spune că articolul potrivit e cel potrivit.** Dacă actul citat conține din întâmplare un
    articol cu același număr, perechea trece. Ar cere o citire, nu o potrivire — deci cifra
    „confirmate" e **plafon superior**;
  - **nu deosebește vina.** Un `CIOT` nu spune că temeiul e greșit, ci că documentul adus e un ciot:
    e o problemă de **corpus**, nu de temei. De-aia se numără separat;
  - **nu repară.** Cele șase perechi cer, fiecare, o verificare la sursă a actului care poartă
    **azi** valoarea — muncă fiscală, nu mecanică.
"""
import ast
import io
import os
import sys

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _RAD not in sys.path:
    sys.path.insert(0, _RAD)

from core import articol_in_act as A  # noqa: E402
from core import scan_pereche_act_articol as S  # noqa: E402

#: CLICHET. Nu poate CREȘTE.
#:
#: **ZERO, și nu prin reparație de date.** Prima formă a instrumentului a raportat **6** perechi
#: negăsite și le-am deschis ca restanță (R106). Erau **convenția de modelare declarată la
#: interdicția 50**, cu opt zile înainte: *`Legea 141/2025 art. 97` înseamnă «CF art. 97, așa cum
#: l-a modificat Legea 141/2025»*. Registrul scrisese și eșecul: *„un instrument care le-ar lua
#: literal ar căuta art. 97 în Legea 141/2025 și n-ar găsi nimic"*. Exact asta am făcut.
#: **R106 s-a RETRAS**, temeiurile s-au pus la loc, iar instrumentul a învățat convenția
#: (`scan_pereche_act_articol.document_tinta`). Zero, deci orice apariție e o regresie.

#: **0 → 11 la 06.09.2026, și niciunul nu e un temei nou.** `scan_citate` culegea temeiuri numai din
#: `core/common`; decizia 73 le mută în modulul REGULII, deci domeniul se micșora cu fiecare temei
#: pus corect (**R169**). Lărgit, inventarul trece de la 36 la 60 de citări — iar cele 24 nou-văzute
#: aduc **11 perechi care n-au fost confruntate niciodată**. *Cifra veche nu era o reușită, era o
#: necunoaștere.*
#:
#: **Cauza lor e una singură, și e cea deja numită la R111**: forma LOCALIZATORULUI, nu actul greșit.
#: `pct.9` (OMFP 1802/2014 numerotează puncte, nu articole) · `norme art.321` / `norme art.19`
#: (HG 1/2016 sunt normele, care trimit la articolul din CF) · `1-6` (un interval, nu un articol).
#: `articol_in_act._TITLURI_NUMARATE` caută titluri de articol, deci nu găsește nimic. **Verdictul e
#: în direcția sigură** — refuză, nu inventează un STABIL —, dar motivul e fals: actul le conține.
#: Rezolvarea cere citire la sursă pe fiecare, adică muncă fiscală: **restanța R171**.
#: **11 → 1 la 06.09.2026 (R171).** `articol_in_act` a învățat PUNCTE și NORME, iar zece din cele
#: unsprezece s-au reparat: `OMFP 1802/2014 pct.9` (×6), `HG 1/2016 norme art.321` (×3) și
#: `norme art.19` (×1). A rămas **una singură**, și e de alt fel: `OMFP 3254/2017 1-6` nu e nici
#: punct, nici normă — e un **interval** de articole. Actul are „Articolul 1"…„Articolul 10";
#: citarea numește șase deodată. Se repară în temei, nu în instrument — v. R171.
#: **1 → 0 la 06.09.2026.** Ultima pereche negăsită, `OMFP 3254/2017 art. 1-6`, s-a despicat în
#: ȘASE citări, una per articol (decizia lui Costin: *„nu se alege un singur articol «care poartă
#: regula» — ar fi o interpretare"*). **Zero, deci orice apariție e o regresie.**
CLICHET_NEGASIT = 0
#: Ce a rămas după convenție: **2**, amândouă `OUG 156/2024 art. LXVI` — articol care CHIAR e al
#: ordonanței, într-un document adus ca ciot. Problemă de **corpus**, nu de temei: **R107**.
#:
#: **2 → 3 la 01.09.2026, și a treia e de ALT FEL — de-aia se scrie, în loc să crească un număr.**
#: `Ordin 1604/2025 art. 1` citează un document care **NU e un ciot**: e actul întreg, șase articole,
#: adus de la emitent ca scan al paginii din Monitorul Oficial. Îl declară ciot **instrumentul**:
#: `articol_in_act._TITLURI_NUMARATE` cere cuvântul „Articolul", iar Monitorul Oficial scrie
#: „Art. 1. —". Deci **orice formă de MO e ciot prin construcție**, pentru toate articolele ei.
#: Cauza e **R111**, nu R107 — una e corpus adus parțial, cealaltă e o formă pe care instrumentul
#: n-o citește. Verdictul e în direcția sigură (refuză, nu inventează un STABIL), motivul e fals.
#:
#: **N-am reparat tiparul în commitul ăsta, cu motivul:** `titluri()` decide starea CIOT pentru
#: **tot** corpusul, iar starea aia hrănește `reverificare`, care hrănește raportul lunar. E o
#: schimbare de contract, nu o linie — se face în tura lui R111, cu volumul de alerte măsurat
#: înainte și după, ca la R109. Iar tiparul are o direcție periculoasă proprie: numărând „Art." prea
#: larg, o trimitere în proză ar deveni titlu, iar un document ar trece din CIOT în GĂSIT — adică
#: din refuz în răspuns fals.
#: **3 → 4 la 03.09.2026, si a patra e din ACEEASI cauza ca a treia, nu una noua.**
#: `OMFP 2634/2015 anexa 1 pct. 24` — temeiul numerotarii secventiale a documentelor, adaugat in
#: lotul 2 al campaniei. Documentul e adus INTREG si pasajul a fost citit verbatim din el
#: (`anaf_surse/omfp_2634_2015_anexa1_norme_generale.txt`), dar actul **nu are „Articolul"**: anexa
#: lui numeroteaza PUNCTE. `articol_in_act._TITLURI_NUMARATE` cauta titluri de articol, deci nu
#: gaseste nimic si declara CIOT. *Aceeasi clasa ca `Ordin 1604/2025` — o forma pe care
#: instrumentul n-o citeste (R111) —, nu corpus adus partial (R107).* Verdictul ramane in directia
#: sigura: refuza, nu inventeaza un STABIL.
#: **4 → 7 la 06.09.2026, din aceeași lărgire de domeniu (R169), și toate trei din cauza deja
#: numită mai sus**: `OMFP 2634/2015` numerotează PUNCTE în anexe, nu articole — `Anexa 1 pct. 52`
#: (jurnalele D406) și `anexa 2` de două ori (registrul-inventar). Nicio formă nouă de eșec; aceleași
#: trei temeiuri erau acolo și înainte, doar că nu le vedea nimeni.
#: **7 → 5 la 06.09.2026 (R171).** `OMFP 2634/2015 anexa 2` (×2) a ieșit din ciot: actul își spune
#: singur, în antet, «(Anexa nr. 2)», iar acum i se numără punctele. `anexa 1` (×2) **rămâne**, și
#: motivul e o regulă, nu o scăpare: antetul ei nu se auto-identifică — spune doar «NORME GENERALE
#: din 5 noiembrie 2015…» —, iar *un act se identifică după conținut, nu după numele fișierului*.
CLICHET_CIOT = 5
#: Pragul de JOS pe confirmate: dacă scade, ceva a dispărut din registru sau instrumentul s-a rupt.
#: 15 → **24** după ce instrumentul a învățat convenția — fără ca vreun temei să se schimbe.
#: 24 → **34** la 06.09.2026: lărgirea domeniului a adus și confirmări, nu doar necunoscute.
#: Pragul de jos se ridică la ce s-a câștigat, altfel câștigul se poate pierde tăcut.
#: 34 → **46** la 06.09.2026 (R171): douăsprezece perechi au trecut din „nu pot spune" în GĂSIT.
#: 46 → **52** la 06.09.2026: cele șase citări ale lui OMFP 3254/2017, fiecare confruntabilă.
PRAG_CONFIRMATE = 52

#: Perechile negăsite **cunoscute** — IDENTITĂȚILE, nu numărul. Clichetul pe număr n-ar vedea o
#: pereche reparată și alta stricată în aceeași tură. Cele patru de aici sunt cele scoase la iveală
#: de lărgirea domeniului (R169), toate din forma localizatorului; se închid prin **R171**.
#: Goală — iar goliciunea ei e chiar aserțiunea.
NEGASITE_CUNOSCUTE = set()


def _inv():
    return S.inventar()


# ── ANTI-VACUU ─────────────────────────────────────────────────────────────────────────────────

def test_ANTI_VACUU_registrul_chiar_are_temeiuri_si_se_pot_intreba():
    inv = _inv()
    assert len(inv) >= 30, (
        "[anti-vacuu] doar %d temeiuri în inventar — domeniul s-a rupt, iar toate clichetele de mai "
        "jos ar fi verzi despre o mulțime goală" % len(inv))
    stari = S.pe_stare(inv)
    assert stari.get("GASIT", 0) > 0, (
        "[anti-vacuu] niciun temei confirmat: %s — instrumentul nu mai citește documentele" % stari)


# ── FORMELE NOI DE LOCALIZARE (R171) ───────────────────────────────────────────────────────────
#
# `articol_in_act` a învățat trei feluri de a numi altceva decât un articol: **punctul**, **anexa**
# și **norma** unui articol din Codul fiscal. Aici se cere ca fiecare să aterizeze pe documentul
# real — și, în cealaltă direcție, ca extinderea să NU fi lărgit ce nu trebuia.

_ANAF = os.path.join(_RAD, "anaf_surse")


def _cauta(fisier, art):
    return A.cauta(os.path.join(_ANAF, fisier), art)


def test_R171_punctul_anexa_si_norma_se_localizeaza():
    """Cele trei forme, pe documentele lor reale. `ani` nevid = fragmentul poartă marcaje de
    consolidare, adică s-a nimerit CORPUL actului, nu cuprinsul (care n-are marcaje)."""
    p = _cauta("omfp_1802_2014_reglementari_consolidat.txt", "pct.9")
    assert p["stare"] == "GASIT" and p["ani"] == ["2015", "2024"], p

    a = _cauta("omfp_2634_2015_anexa2_norme_specifice.txt", "anexa 2")
    assert a["stare"] == "GASIT" and a["ani"] == ["2024"], a

    n1 = _cauta("hg_1_2016_norme_cod_fiscal.txt", "norme art.321")
    assert n1["stare"] == "GASIT" and n1["ani"] == ["2016", "2021"], n1
    n2 = _cauta("hg_1_2016_norme_cod_fiscal.txt", "norme art.19")
    assert n2["stare"] == "GASIT" and n2["ani"] == ["2018"], n2


def test_R171_CALIBRARE_articolul_simplu_merge_pe_calea_veche():
    """Dispecerul e pe FORMA citării. O citare de articol simplu nu are voie să se schimbe."""
    assert _cauta("cod_fiscal_227_2015_consolidat.txt", "322")["stare"] == "GASIT"
    assert _cauta("cod_fiscal_227_2015_consolidat.txt", "99999")["stare"] == "NEGASIT"


def test_R171_CALIBRARE_anexa_nu_se_ghiceste_din_numele_fisierului():
    """`omfp_2634_2015_anexa1_norme_generale.txt` SE NUMEȘTE anexa 1 și **rămâne CIOT**: antetul
    lui nu se auto-identifică. *Un act se identifică după conținut, nu după numele fișierului* —
    dacă proba asta cade, localizatorul a început să creadă calea."""
    assert _cauta("omfp_2634_2015_anexa1_norme_generale.txt", "anexa 1")["stare"] == "CIOT"
    # și direcția inversă: anexa 2 NU se dă drept anexa 3
    assert _cauta("omfp_2634_2015_anexa2_norme_specifice.txt", "anexa 3")["stare"] == "NEGASIT"


def test_R171_tiparul_LARG_de_puncte_nu_a_fost_adoptat():
    """**Decizia de a NU extinde, făcută verificabilă.**

    S-au măsurat două forme de punct pe tot corpusul: `9. - ` (1.834 potriviri, 11 documente ies
    din ciot) și `52. Text` (9.983 potriviri, **80** de documente ies din ciot). A doua scoate din
    refuz descrieri de structură XML și enumerări din proză — *o numărare prea largă transformă o
    trimitere în proză într-un titlu, iar un document trece din refuz în răspuns fals*. Față de 24
    de citări cunoscute, 84 e disproporționat, deci nu s-a implementat.

    Proba ține decizia: `d101_struct_anaf.txt` are 64 de „puncte" în forma largă și **zero** în cea
    îngustă, deci trebuie să rămână CIOT. Dacă cineva lărgește tiparul, cade aici, nu peste șase
    luni într-o cifră fiscală."""
    assert A.e_ciot(A.din_fisier(os.path.join(_ANAF, "d101_struct_anaf.txt"))[0]) is True
    assert A.e_ciot(A.din_fisier(os.path.join(_ANAF, "d112_struct_anaf.txt"))[0]) is True


def test_R171_ANTI_VACUU_numararea_punctelor_chiar_face_ceva():
    """Cele de mai sus ar trece și cu numărarea punctelor scoasă cu totul. Aici se cere efectul ei:
    un act care numerotează PUNCTE, nu articole, nu mai e ciot."""
    t = A.din_fisier(os.path.join(_ANAF, "omfp_2634_2015_anexa2_norme_specifice.txt"))[0]
    assert A.e_ciot(t) is False
    assert A.titluri(t) >= A.PRAG_TITLURI


# ── CLICHETUL ──────────────────────────────────────────────────────────────────────────────────

def test_perechile_neconfirmate_nu_cresc():
    st = S.pe_stare(_inv())
    ng, ci = st.get("NEGASIT", 0), st.get("CIOT", 0)
    assert ng <= CLICHET_NEGASIT, (
        "perechi (act, articol) negăsite: %d > clichet %d. Un temei nou numește un act care nu "
        "conține articolul lui — verificarea vigorii pe el ar întreba documentul greșit."
        % (ng, CLICHET_NEGASIT))
    assert ci <= CLICHET_CIOT, (
        "temeiuri care citează un document-ciot: %d > clichet %d. Nu e vina temeiului, e a "
        "corpusului — dar tot nu se poate confrunta nimic." % (ci, CLICHET_CIOT))
    assert (ng, ci) == (CLICHET_NEGASIT, CLICHET_CIOT) or ng < CLICHET_NEGASIT or ci < CLICHET_CIOT


def test_confirmatele_nu_scad():
    st = S.pe_stare(_inv())
    c = st.get("GASIT", 0) + st.get("ABROGAT", 0)
    assert c >= PRAG_CONFIRMATE, (
        "confirmate: %d < pragul de jos %d. O pereche care se confirma nu se mai confirmă — ori a "
        "dispărut din registru, ori documentul ei s-a schimbat, ori instrumentul s-a rupt. "
        "Niciuna dintre cele trei nu e o veste bună." % (c, PRAG_CONFIRMATE))


def test_negasitele_sunt_CELE_CUNOSCUTE_nu_doar_atatea():
    """Clichetul pe număr nu vede o pereche care se repară și alta care se strică în aceeași tură.
    Se cere identitatea, nu cardinalitatea."""
    gasite = {(x["act"], str(x["art"])) for x in _inv() if x["stare"] == "NEGASIT"}
    noi = sorted(gasite - NEGASITE_CUNOSCUTE)
    assert not noi, (
        "perechi negăsite NOI: %s — clichetul pe număr nu le-ar fi văzut dacă altele s-au reparat "
        "în aceeași tură" % noi)
    disparute = sorted(NEGASITE_CUNOSCUTE - gasite)
    assert not disparute, (
        "perechi reparate: %s. Bravo — coboară `CLICHET_NEGASIT` și scoate-le din "
        "`NEGASITE_CUNOSCUTE`, altfel marja rămasă ascunde următoarea regresie" % disparute)


# ── REGRESIE pe CONVENȚIA de modelare (interdicția 50) ─────────────────────────────────────────

def test_conventia_articolelor_de_COD_FISCAL_e_aplicata():
    """LECȚIA CARE A COSTAT O RESTANȚĂ RETRASĂ.

    `Temei` reține **actul care a schimbat regula** și **numărul articolului din actul schimbat** —
    `Legea 141/2025 art. 97` înseamnă *CF art. 97, așa cum l-a modificat Legea 141/2025*. Convenția
    e declarată la interdicția **50** din 23.08.2026, împreună cu eșecul pe care îl provoacă: *„un
    instrument care le-ar lua literal ar căuta art. 97 în Legea 141/2025 și n-ar găsi nimic."*

    Prima formă a instrumentului ăstuia a făcut exact asta și a raportat șase perechi ca defect de
    date. **Nu erau.** Testul de aici cere ca rezolvarea să se facă: perechile de Cod fiscal trebuie
    să fie căutate în Codul fiscal, nu în actul care l-a modificat.
    """
    perechi = [(t["act"], str(t["art"]), t.get("dupa_conventie"), t["stare"])
               for t in _inv() if str(t["art"]) in S.ART_DE_COD_FISCAL]
    assert perechi, "[anti-vacuu] niciun temei cu articol de Cod fiscal — domeniul s-a rupt"
    literale = [(a, r, s) for a, r, dc, s in perechi if not dc]
    assert not literale, (
        "perechi de Cod fiscal căutate LITERAL, în actul care doar le-a modificat: %s. Convenția e "
        "declarată la interdicția 50; un instrument care n-o cunoaște raportează defecte de date "
        "care nu există." % literale)
    rele = [(a, r, s) for a, r, _dc, s in perechi if s != "GASIT"]
    assert not rele, "perechi de Cod fiscal care nu se găsesc nici în Codul fiscal: %s" % rele


def test_CALIBRARE_conventia_NU_se_aplica_unde_articolul_e_chiar_al_actului():
    """Direcția inversă: convenția nu are voie să înghită tot. `OUG 89/2025 art. III` și
    `OUG 156/2024 art. LXVI` sunt articole **proprii** ale actelor lor — se caută acolo, nu în CF.
    Fără proba asta, `document_tinta` ar putea trimite totul la Codul fiscal și ar părea că merge."""
    straine = [(t["act"], str(t["art"])) for t in _inv()
               if t.get("dupa_conventie") and str(t["art"]) not in S.ART_DE_COD_FISCAL
               and str(t["art"]) != "291"]
    assert not straine, (
        "articole trimise la Codul fiscal deși nu sunt ale lui: %s — convenția s-a lărgit" % straine)
    assert S.cheie_articol("OUG", 89, 2025, "III") == ("OUG 89/2025", "III")
    assert S.cheie_articol("Legea", 141, 2025, "97") == ("CF", "97")
    assert S.cheie_articol("CF", None, None, "51") == ("CF", "51")


# ── CALIBRARE POZITIVĂ: cazul cunoscut e GĂSIT ─────────────────────────────────────────────────

def test_CALIBRARE_articolul_care_EXISTA_e_gasit():
    r = A.cauta(os.path.join(_RAD, "anaf_surse/cod_fiscal_227_2015_consolidat.txt"), "78")
    assert r["stare"] == "GASIT", "CF art. 78 nu mai e găsit: %s" % r["stare"]
    assert len(r["frag"]) > 5000, (
        "CF art. 78 are doar %d caractere — trunchierea de la a cincea reparație s-a întors"
        % len(r["frag"]))
    assert set(r["ani"]) >= {"2024", "2026"}, (
        "CF art. 78 a pierdut ani de modificare: %s. Cu ei pierduți, articolul pare mai STABIL "
        "decât e, deci ar primi cel mai lung prag de reverificare exact unde trebuie cel mai scurt"
        % r["ani"])


# ── CALIBRARE NEGATIVĂ: cele trei feluri de „nu pot spune", pe cod sintetic ────────────────────

def _act(tmp_path, nume, corp):
    f = tmp_path / nume
    f.write_text(corp, encoding="utf-8")
    return str(f)


ACT_CU_DOUA = ("Forma printabilă\n\nArticolul 1\nCeva.\n\nArticolul 2\nAltceva.\n")


def test_CALIBRARE_articol_care_NU_e_in_act(tmp_path):
    r = A.cauta(_act(tmp_path, "a.txt", ACT_CU_DOUA), "97")
    assert r["stare"] == "NEGASIT", r["stare"]


def test_CALIBRARE_act_CIOT(tmp_path):
    r = A.cauta(_act(tmp_path, "b.txt", "Forma printabilă\n\nArticolul 1\nDoar unul.\n"), "1")
    assert r["stare"] == "CIOT", (
        "un act cu un singur titlu de articol a dat %s — un «negăsit» despre un act neadus nu e un "
        "răspuns, e o tăcere care arată ca un răspuns" % r["stare"])


def test_CALIBRARE_fisier_lipsa(tmp_path):
    assert A.cauta(str(tmp_path / "nu_exista.txt"), "1")["stare"] == "FISIER_LIPSA"


def test_CALIBRARE_articolul_care_EXISTA_in_actul_sintetic(tmp_path):
    r = A.cauta(_act(tmp_path, "c.txt", ACT_CU_DOUA), "2")
    assert r["stare"] == "GASIT" and r["frag"].startswith("Altceva"), r


# ── REGRESIE pe a CINCEA reparație: citarea nu taie articolul ─────────────────────────────────

CITARE = ("Forma printabilă\n\nArticolul 78\n"
          "(1) Prima parte. (la 01-01-2018, Alineatul (1) a fost modificat de "
          "Articolul I ORDONANȚA DE URGENȚĂ nr. 79 din 8 noiembrie 2017 )\n"
          "(2) A doua parte, care trebuie să RĂMÂNĂ. "
          "(la 01-01-2024, Alineatul (2) a fost modificat de Legea nr. 1 din 2024 )\n"
          "\nArticolul 79\nAlt articol. "
          "(la 01-01-2030, Alineatul (1) a fost modificat de Legea nr. 9 din 2030 )\n")


def test_o_CITARE_dintr_un_marcaj_nu_taie_articolul(tmp_path):
    """Bugul găsit DE extragere. Tiparul lax de terminare potrivea „Articolul I ORDONANȚA … **din**
    8 noiembrie 2017" — o citare dinăuntrul unui marcaj —, tăia articolul acolo, și arunca
    alineatele de după, cu tot cu modificările lor. Pe registru: `CF art. 78` de la 16.719 la 532 de
    caractere și de la șase ani de modificare la unul."""
    r = A.cauta(_act(tmp_path, "d.txt", CITARE), "78")
    assert r["stare"] == "GASIT", r["stare"]
    assert set(r["ani"]) == {"2018", "2024"}, (
        "articolul a fost tăiat la citare: ani găsiți %s, așteptați 2018 și 2024. Direcția greșelii "
        "e cea liniștitoare — articolul pare mai stabil decât e." % r["ani"])


def test_CALIBRARE_INVERSA_un_titlu_REAL_chiar_taie(tmp_path):
    """Direcția opusă, obligatorie: dacă nimic nu mai taie, fragmentul înghite actul întreg și
    împrumută marcaje de la articolele următoare — cealaltă față a aceleiași greșeli."""
    r = A.cauta(_act(tmp_path, "e.txt", CITARE), "78")
    # Se probează EFECTUL, nu forma: art. 79 din fixtură poartă un marcaj din **2030**, an care nu
    # apare nicăieri altundeva. Dacă apare în anii lui art. 78, fragmentul a înghițit articolul
    # următor și i-a împrumutat modificările — exact alarma falsă de pe OUG 89/2025.
    #
    # *Prima formă a testului căuta titluri de articol în fragment și a rămas VERDE pe cod mutat:
    # fragmentul e normalizat pe spații, iar tiparul de titlu e ancorat pe linie, deci nu mai avea
    # ce vedea. Un gard care se uită la forma greșită nu e un gard.*
    ani = set(r["ani"])
    assert not (ani & {"2030"}), (
        "fragmentul art. 78 a împrumutat marcajul lui art. 79 (ani: %s) — modificările articolului "
        "următor s-ar atribui acestuia" % sorted(ani))
    assert ani == {"2018", "2024"}, "anii lui art. 78: %s" % sorted(ani)


# ── O SINGURĂ IMPLEMENTARE ─────────────────────────────────────────────────────────────────────

def test_scriptul_IMPORTA_modulul_nu_isi_scrie_propria_copie():
    """Motivul mutării: logica neimportabilă se multiplică prost. Am re-scris-o de două ori într-o
    oră și amândouă copiile au dat cifre greșite. Se cere pe **AST**, nu pe text: un import se vede
    ca nod, iar un comentariu care pomenește modulul nu trece drept import."""
    cale = os.path.join(_RAD, "scripts", "vigoare_articol.py")
    arb = ast.parse(io.open(cale, encoding="utf-8").read())
    importate = set()
    for n in ast.walk(arb):
        if isinstance(n, ast.ImportFrom) and n.module:
            for a in n.names:
                importate.add("%s.%s" % (n.module, a.name))
        elif isinstance(n, ast.Import):
            for a in n.names:
                importate.add(a.name)
    assert {"core.articol_in_act"} & importate, (
        "`scripts/vigoare_articol.py` nu mai importă `core.articol_in_act` (importuri văzute: %s). "
        "Dacă și-a rescris localizarea articolului, există iar două implementări — și una dintre "
        "ele va rămâne în urmă." % sorted(importate))
