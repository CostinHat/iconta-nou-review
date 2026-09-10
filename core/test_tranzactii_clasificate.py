# -*- coding: utf-8 -*-
"""GARD P4 — FIECARE candidat brut are un verdict, iar niciun verdict nu îmbătrânește.

**CE PĂZEȘTE.** `scripts/scan_tranzactii.py` derivă din cod inventarul brut: orice cale care
aprinde **cel puțin unul** din cele șase semne cerute de comandă e candidat. `core/p4_clasificare.py`
dă fiecăruia un verdict — fie printr-un rând **individual**, fie printr-o **regulă pe clasă
structurală**, care se aplică pe faptele derivate ale căii, nu pe numele ei. Gardul ăsta leagă cele
două și transformă legătura în poartă:

  1. `RAW_CANDIDATES == CLASSIFIED_CANDIDATES` și `UNCLASSIFIED_RAW_CANDIDATES = 0` — **fiecare**
     dintre cei 332, nu doar cei de peste un prag ales de mine;
  2. fiecare verdict poartă **regula** care l-a produs și un **motiv concret**;
  3. fiecare excludere din critic are justificare scrisă (`UNEXPLAINED_EXCLUSIONS = 0`);
  4. fiecare cale critică numește o probă de injecție care **există** — verificat cu `ast`;
  5. fiecare loc cu efect ireversibil în tranzacție are verdict scris;
  6. **CALIBRARE NEGATIVĂ**: pentru fiecare din C1…C6 se injectează o cale sintetică ce îl aprinde,
     se arată că intră în inventarul brut, și se arată că mecanismul de completitudine **REFUZĂ**
     inventarul dacă acea cale rămâne neclasificată. *Nu e destul ca detectorul s-o vadă.*

**DE CE PRAGUL A DISPĂRUT.** Prima formă a livrării clasifica 32 de căi dintr-un inventar de 332,
cu un prag pe care îl alesesem eu — adică exact „am declarat un candidat neimportant ÎNAINTE de
clasificare". Regula lui P4 nu are prag: are șase semne și trei verdicte.

**PREMISA ANTI-VACUU.** Dacă inventarul e gol, sau instrumentul nu se mai calibrează, gardul PICĂ.

**ASERȚIUNILE SUNT PE STRUCTURĂ** (METODA §23): mulțimi de chei și numere derivate, nu căutări de
șiruri în text.
"""
import ast
import io
import os
import sys

import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _RAD not in sys.path:
    sys.path.insert(0, _RAD)

from core import p4_clasificare as CL  # noqa: E402
from scripts import scan_tranzactii as ST  # noqa: E402

#: Fișierul în care trăiesc probele de injecție.
FISIER_PROBE = os.path.join(_RAD, "core", "test_p4_fault_injection.py")


@pytest.fixture(scope="module")
def inventar():
    inv, stat = ST.inventar()
    return inv, stat


# ============================================================================
#  PREMISELE
# ============================================================================

def test_instrumentul_se_calibreaza():
    """Fără calibrare trecută, orice cifră de mai jos e despre altceva."""
    assert ST.calibreaza(verbose=False) is True


def test_inventarul_nu_e_gol(inventar):
    """ANTI-VACUU. Un inventar gol ar face toate celelalte probe să treacă degeaba."""
    inv, stat = inventar
    assert stat["intrari"] > 100, "prea puține puncte de intrare: instrumentul nu vede aplicația"
    assert len(inv) > 100, "inventar brut suspect de mic: gardul s-ar uita într-un loc gol"


def test_fiecare_candidat_aprinde_cel_putin_un_semn(inventar):
    """Definiția candidatului, verificată pe inventar: cel puțin unul din C1…C6, niciun prag."""
    inv, _stat = inventar
    fara_semne = [x["intrare"] for x in inv if not x["semne"]]
    assert fara_semne == [], "candidați fără niciun semn: %s" % fara_semne[:5]
    coduri = {c for x in inv for c in x["semne"]}
    assert coduri <= {"C1", "C2", "C3", "C4", "C5", "C6"}, sorted(coduri)


# ============================================================================
#  COMPLETITUDINEA — cerința 1 din runda de acceptare
# ============================================================================

def test_fiecare_candidat_brut_are_verdict(inventar):
    """`RAW_CANDIDATES == CLASSIFIED_CANDIDATES` și `UNCLASSIFIED_RAW_CANDIDATES = 0`."""
    inv, _stat = inventar
    n = CL.numaratori(inv)
    assert n["UNCLASSIFIED_RAW_CANDIDATES"] == 0, (
        "candidați bruți fără verdict: %s" % n["neclasificate"][:10])
    assert n["RAW_CANDIDATES"] == n["CLASSIFIED_CANDIDATES"] == len(inv)


# ============================================================================
#  CONTABILITATEA — DOUĂ UNIVERSURI, care nu se adună între ele
#
#  Defectul care a produs probele astea: blocul de acceptare punea sub același
#  nume (`CRITICAL_COMPOSITES`) șase căi din inventarul brut ȘI a șaptea, care
#  e o cale internă și nu e în inventar. Suma ieșea 333 pe o populație de 332.
#  Un câmp nu poate purta două universuri; de-aici încolo, nici numele nu poate.
# ============================================================================

def test_contabilitatea_inventarului_brut_se_inchide(inventar):
    """`RAW_CRITICAL + RAW_NON_CRITICAL + RAW_FALSE_POSITIVES = CLASSIFIED = RAW = len(inventar)`."""
    inv, _stat = inventar
    n = CL.numaratori(inv)
    suma = (n["RAW_CRITICAL_COMPOSITES"] + n["RAW_NON_CRITICAL_COMPOSITES"]
            + n["RAW_FALSE_POSITIVES"])
    assert suma == n["RAW_CLASS_SUM"], "RAW_CLASS_SUM nu e suma claselor: %s" % n
    assert suma == n["CLASSIFIED_CANDIDATES"] == n["RAW_CANDIDATES"] == len(inv), (
        "contabilitatea inventarului brut NU se închide: %d + %d + %d = %d, dar "
        "CLASSIFIED=%d și RAW=%d"
        % (n["RAW_CRITICAL_COMPOSITES"], n["RAW_NON_CRITICAL_COMPOSITES"],
           n["RAW_FALSE_POSITIVES"], suma, n["CLASSIFIED_CANDIDATES"], n["RAW_CANDIDATES"]))
    assert n["RAW_CLASS_ACCOUNTING"] == "PASS", n


def test_contabilitatea_operatiilor_critice_se_inchide_separat(inventar):
    """`TOTAL_CRITICAL_OPERATIONS = RAW_CRITICAL_COMPOSITES + INTERNAL_CRITICAL_COMPOSITES`.

    Al doilea univers. Nu se adună cu primul, și nicio probă nu-l amestecă în el."""
    inv, _stat = inventar
    n = CL.numaratori(inv)
    assert (n["TOTAL_CRITICAL_OPERATIONS"]
            == n["RAW_CRITICAL_COMPOSITES"] + n["INTERNAL_CRITICAL_COMPOSITES"]), n
    assert n["TOTAL_CRITICAL_OPERATIONS"] == len(CL.cai_critice()), (
        "universul operațiilor critice nu se potrivește cu registrul: %d vs %d"
        % (n["TOTAL_CRITICAL_OPERATIONS"], len(CL.cai_critice())))
    interne = set(CL.cai_interne())
    intrari = {x["intrare"] for x in inv}
    assert interne and not (interne & intrari), (
        "o cale declarată INTERNĂ apare totuși ca punct de intrare: %s"
        % sorted(interne & intrari))


def test_caile_interne_nu_intra_in_contabilitatea_bruta(inventar):
    """Oglinda: nicio cale internă nu e numărată printre cei 332, și niciun candidat brut nu e
    marcat `cale_interna`. Fără proba asta, cele două universuri s-ar putea reamesteca tăcut."""
    inv, _stat = inventar
    intrari = {x["intrare"] for x in inv}
    gresite = {k for k, v in CL.CLASIFICARE.items()
               if v.get("cale_interna") and k in intrari}
    assert gresite == set(), "căi interne care sunt totuși în inventarul brut: %s" % sorted(gresite)


def test_acoperirea_injectiei_e_pe_universul_operatiilor_critice(inventar):
    """`CRITICAL_OPERATIONS_REQUIRING_FAULT_TESTS = WITH = TOTAL_CRITICAL_OPERATIONS`, cu calea
    internă ÎNĂUNTRU. *Nu se pierde din acoperire ca să iasă contabilitatea inventarului.*"""
    inv, _stat = inventar
    n = CL.numaratori(inv)
    assert n["CRITICAL_OPERATIONS_REQUIRING_FAULT_TESTS"] == n["TOTAL_CRITICAL_OPERATIONS"], n
    assert (n["CRITICAL_OPERATIONS_WITH_FAULT_TESTS"]
            == n["CRITICAL_OPERATIONS_REQUIRING_FAULT_TESTS"]), n
    assert n["UNTESTED_CRITICAL_OPERATIONS"] == 0, (
        "operații critice fără probă de injecție: %s" % n["netestate"])
    # calea internă e chiar înăuntru, nu doar numărată
    cerute = CL.probe_cerute()
    for k in CL.cai_interne():
        assert k in cerute, "calea internă %s a ieșit din acoperire" % k


def test_excluderile_se_numara_peste_TOTI_candidatii_exclusi(inventar):
    """`UNEXPLAINED_EXCLUSIONS` se derivă peste **toți** candidații clasificați NON_CRITICAL sau
    FALSE_POSITIVE — nu doar peste rândurile scrise de mână.

    Prima formă măsura 35 de excluderi individuale și raporta zero; zero pe o populație mai mică
    decât cea despre care pare că vorbește e adevărat și înșelător."""
    inv, _stat = inventar
    n = CL.numaratori(inv)
    assert n["EXCLUSIONS_TOTAL"] == (n["RAW_NON_CRITICAL_COMPOSITES"]
                                     + n["RAW_FALSE_POSITIVES"]), n
    assert n["EXCLUSIONS_TOTAL"] > len(CL.CLASIFICARE), (
        "populația excluderilor e mai mică decât registrul individual — semn că se numără "
        "iar doar rândurile scrise: %d" % n["EXCLUSIONS_TOTAL"])
    assert n["UNEXPLAINED_EXCLUSIONS"] == 0, (
        "excluderi fără justificare scrisă: %s" % n["nemotivate"][:10])


def test_fiecare_verdict_poarta_regula_si_motiv(inventar):
    """Un verdict fără regulă și fără motiv concret nu se poate confrunta cu nimic."""
    inv, _stat = inventar
    rele = []
    for x in inv:
        v = CL.verdict(x)
        if v is None:
            rele.append((x["intrare"], "fără verdict"))
            continue
        if not str(v.get("regula", "")).strip():
            rele.append((x["intrare"], "fără regulă"))
        if len(str(v.get("de_ce", "")).strip()) < 80:
            rele.append((x["intrare"], "justificare prea scurta"))
        if v["clasa"] not in (CL.CRITIC, CL.NECRITIC, CL.FALS):
            rele.append((x["intrare"], "clasă în afara vocabularului: %r" % v["clasa"]))
    assert rele == [], "verdicte incomplete: %s" % rele[:8]


def test_regulile_folosite_sunt_cele_declarate(inventar):
    """Nicio cale nu primește verdict printr-o regulă care nu e în listă (sau individual)."""
    inv, _stat = inventar
    declarate = {r["cod"] for r in CL.REGULI} | {CL.INDIVIDUAL}
    folosite = {CL.verdict(x)["regula"] for x in inv if CL.verdict(x)}
    assert folosite <= declarate, "reguli nedeclarate: %s" % sorted(folosite - declarate)


def test_regulile_care_cer_judecata_nu_au_regula_de_clasa(inventar):
    """O cale cu scrieri în mai multe tranzacții, commit parțial sau efect ireversibil în
    tranzacție **nu poate** primi verdict pe clasă: doar individual. Altfel mecanismul ar
    absorbi tăcut exact căile pentru care există."""
    inv, _stat = inventar
    rele = []
    for x in inv:
        if not CL._cere_individual(x):
            continue
        v = CL.verdict(x)
        if v is None:
            rele.append((x["intrare"], "cere judecată și n-o are"))
        elif v["regula"] != CL.INDIVIDUAL:
            rele.append((x["intrare"], "absorbită de regula %s" % v["regula"]))
    assert rele == [], "%s" % rele[:8]


# ============================================================================
#  CALIBRAREA NEGATIVĂ — cerința 1, partea a doua
#
#  Pentru fiecare criteriu: o cale sintetică, faptul că intră în inventarul brut,
#  și faptul că mecanismul REFUZĂ inventarul cât timp ea rămâne neclasificată.
# ============================================================================

CORPUS_SEMNE = '''
from core import db
import requests


@app.post("/numai_c1")
def numai_c1():
    with db.get_conn() as a:                      # domeniul 1: doar citeste
        with a.cursor() as cur:
            cur.execute("SELECT 1 FROM facturi")
    with db.get_conn() as b:                      # domeniul 2: o singura scriere
        with b.cursor() as cur:
            cur.execute("INSERT INTO facturi (nr) VALUES (1)")


@app.post("/numai_c2")
def numai_c2():
    with db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("INSERT INTO facturi (nr) VALUES (1)")
            cur.execute("INSERT INTO note (a) VALUES (1)")


@app.post("/numai_c3")
def numai_c3():
    with db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("INSERT INTO facturi (nr) VALUES (1)")
        requests.post("https://exemplu", json={})


@app.post("/minim_c4")
def minim_c4():
    with db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("INSERT INTO facturi (nr) VALUES (1)")
            cur.execute("INSERT INTO public.firma_rezumat (x) VALUES (1)")


@app.post("/minim_c5")
def minim_c5():
    with db.get_conn() as a:
        with a.cursor() as cur:
            cur.execute("INSERT INTO facturi (nr) VALUES (1)")
    with db.get_conn() as b:
        with b.cursor() as cur:
            cur.execute("INSERT INTO facturi (nr) VALUES (2)")


@app.post("/minim_c6")
def minim_c6():
    with db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("INSERT INTO facturi (nr) VALUES (1)")
        requests.post("https://exemplu", json={})
        with c.cursor() as cur:
            cur.execute("INSERT INTO facturi (nr) VALUES (2)")
'''

#: `cod -> (ruta, semnele ASTEPTATE, verdictul cu regulile REALE)`
#:
#: Mulțimea așteptată e **pinată**, fiindcă ea poartă implicațiile dintre criterii — iar ele nu
#: sunt o preferință, ci o consecință a definițiilor din comandă, măsurată aici:
#:   * **C1, C2, C3 se pot izola**;
#:   * **C4 ⟹ C2** — C4 cere o scriere în sursă *și* una în modelul de citire, adică ≥2 tabele,
#:     care e chiar C2. „Numai C4" nu există prin construcție;
#:   * **C5 ⟹ C1 ∧ C6** — două domenii care scriu sunt două frontiere (C1), iar între cele două
#:     scrieri stă închiderea unui domeniu (C6);
#:   * **C6 ⟹ C1 ∨ C3** — ce poate sta între două scrieri e o frontieră (C1) sau un efect (C3).
#: Dacă o definiție se schimbă, mulțimea se mișcă și proba pică — ceea ce e chiar rostul ei.
SEMNE_SINTETICE = {
    "C1": ("POST /numai_c1", {"C1"}, "NON_CRITICAL_COMPOSITE"),
    "C2": ("POST /numai_c2", {"C2"}, "NON_CRITICAL_COMPOSITE"),
    "C3": ("POST /numai_c3", {"C3"}, None),
    "C4": ("POST /minim_c4", {"C2", "C4"}, "NON_CRITICAL_COMPOSITE"),
    "C5": ("POST /minim_c5", {"C1", "C5", "C6"}, None),
    "C6": ("POST /minim_c6", {"C3", "C6"}, None),
}


@pytest.fixture(scope="module")
def inventar_sintetic(tmp_path_factory):
    """Inventarul brut al corpusului sintetic — șase căi, câte una per criteriu."""
    d = tmp_path_factory.mktemp("p4_semne")
    os.makedirs(os.path.join(str(d), "core"), exist_ok=True)
    cale = os.path.join(str(d), "main.py")
    with io.open(cale, "w", encoding="utf-8", newline="") as f:
        f.write(CORPUS_SEMNE)
    inv, _stat = ST.inventar_din([cale], str(d))
    return {x["intrare"]: x for x in inv}


@pytest.mark.parametrize("cod", sorted(SEMNE_SINTETICE))
def test_calea_sintetica_aprinde_criteriul_si_intra_in_inventar(cod, inventar_sintetic):
    """(a) criteriul se aprinde · (b) calea E candidat brut · (c) implicațiile sunt cele pinate."""
    ruta, asteptat, _verdict = SEMNE_SINTETICE[cod]
    assert ruta in inventar_sintetic, (
        "calea sintetică pentru %s NU e în inventarul brut — deci nu intră în domeniul care cere "
        "clasificare, iar criteriul n-ar fi acoperit de nimic" % cod)
    x = inventar_sintetic[ruta]
    semne = set(x["semne"])
    assert cod in semne, "%s nu s-a aprins pe calea lui: %s" % (cod, sorted(semne))
    assert semne == asteptat, (
        "implicațiile dintre criterii s-au schimbat pentru %s: %s, așteptat %s"
        % (cod, sorted(semne), sorted(asteptat)))


@pytest.mark.parametrize("cod", sorted(SEMNE_SINTETICE))
def test_mecanismul_REFUZA_daca_o_cale_ramane_neclasificata(cod, inventar_sintetic):
    """MIEZUL CALIBRĂRII NEGATIVE.

    Nu e destul ca detectorul să vadă calea. Se arată că mecanismul de completitudine o
    **raportează ca neclasificată** — adică poarta ar cădea — cât timp niciun rând individual și
    nicio regulă n-o acoperă. Fără proba asta, „fiecare candidat are verdict" ar putea fi adevărat
    din întâmplare, nu prin construcție.
    """
    ruta, _asteptat, _v = SEMNE_SINTETICE[cod]
    x = inventar_sintetic[ruta]
    verdicte, neclasificate = CL.clasifica([x], clasificare={}, reguli=[])
    assert verdicte == [] and neclasificate == [ruta], (
        "mecanismul NU a refuzat o cale neacoperită de nimic (%s): verdicte=%s, neclasificate=%s"
        % (cod, verdicte, neclasificate))
    n = CL.numaratori([x], clasificare={}, reguli=[])
    assert n["UNCLASSIFIED_RAW_CANDIDATES"] == 1 and n["CLASSIFIED_CANDIDATES"] == 0, n


@pytest.mark.parametrize("cod", sorted(SEMNE_SINTETICE))
def test_ce_face_mecanismul_REAL_cu_fiecare_cale_sintetica(cod, inventar_sintetic):
    """Cealaltă direcție, pinată: cu regulile REALE, fiecare cale sintetică fie primește o clasă,
    fie e **trimisă la judecată scrisă** (`None`). A doua nu e o scăpare — e refuzul de a absorbi
    pe clasă exact căile pentru care clasificarea individuală există."""
    ruta, _asteptat, astept_verdict = SEMNE_SINTETICE[cod]
    v = CL.verdict(inventar_sintetic[ruta], clasificare={})
    if astept_verdict is None:
        assert v is None, (
            "%s ar trebui trimisă la judecată scrisă, dar a fost absorbită de regula %s"
            % (cod, v and v["regula"]))
    else:
        assert v is not None and v["clasa"] == astept_verdict, (
            "%s: verdict %s, așteptat %s" % (cod, v, astept_verdict))
        assert v["regula"] != CL.INDIVIDUAL


# ============================================================================
#  RÂNDURILE INDIVIDUALE — nu îmbătrânesc, și spun ce s-a făcut
# ============================================================================

def test_nicio_clasificare_individuala_nu_ramane_fara_cale(inventar):
    """O intrare rămasă din trecut ar descrie o lume care nu mai există.

    Excepția, declarată: `cale_interna` — funcții din interiorul căilor, care nu sunt puncte de
    intrare, dar sunt cauza mai multora."""
    inv, _stat = inventar
    intrari = {x["intrare"] for x in inv}
    orfane = {k for k, v in CL.CLASIFICARE.items()
              if k not in intrari and not v.get("cale_interna")}
    assert orfane == set(), "clasificări fără cale în inventar (stătute): %s" % sorted(orfane)


def test_fiecare_excludere_INDIVIDUALA_are_motiv_scris():
    """Rândurile scrise de mână, verificate pe conținut. Populația mare — toți candidații
    excluși — e verificată de `test_excluderile_se_numara_peste_TOTI_candidatii_exclusi`."""
    fara_motiv = {k for k, motiv in CL.excluderi().items()
                  if not isinstance(motiv, str) or len(motiv.strip()) < 80}
    assert fara_motiv == set(), (
        "excluderi din CRITICAL_COMPOSITE fără justificare scrisă: %s" % sorted(fara_motiv))


def test_fiecare_clasificare_numeste_efectele_compuse():
    """O clasificare fără efectele numite nu se poate confrunta cu inventarul."""
    fara_efecte = {k for k, v in CL.CLASIFICARE.items()
                   if not str(v.get("efecte", "")).strip()}
    assert fara_efecte == set(), "clasificări fără câmpul `efecte`: %s" % sorted(fara_efecte)


def _functii_din_probe():
    """Numele funcțiilor de test din fișierul de injecție, derivate cu `ast` — o probă comentată
    sau redenumită trebuie să cadă, nu să treacă pe potrivire de șir."""
    if not os.path.exists(FISIER_PROBE):
        return set()
    arbore = ast.parse(io.open(FISIER_PROBE, encoding="utf-8").read())
    return {n.name for n in ast.walk(arbore)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}


def test_fiecare_cale_critica_are_proba_de_injectie():
    """`CRITICAL_COMPOSITES_WITH_FAULT_TESTS = CRITICAL_COMPOSITES`, mecanic.
    `UNTESTED_CRITICAL_COMPOSITES = 0` e chiar mulțimea goală de mai jos."""
    cerute = CL.probe_cerute()
    assert cerute, "nicio cale critică: clasificarea ar fi vacuă"
    existente = _functii_din_probe()
    lipsa = {cale: nume for cale, nume in cerute.items() if nume not in existente}
    assert lipsa == {}, "căi critice fără probă de injecție: %s" % sorted(lipsa)


def test_fiecare_cale_critica_spune_ce_s_a_facut_cu_ea():
    """O cale critică fără `reparatie` scrisă ar lăsa nespus dacă s-a reparat sau doar s-a probat."""
    fara = {k for k in CL.cai_critice()
            if len(str(CL.CLASIFICARE[k].get("reparatie", "")).strip()) < 40}
    assert fara == set(), "căi critice fără câmpul `reparatie`: %s" % sorted(fara)


def test_clasele_sunt_din_vocabularul_declarat():
    """Trei clase, nu patru. O etichetă nouă ar trece pe lângă toate probele de mai sus."""
    permise = {CL.CRITIC, CL.NECRITIC, CL.FALS}
    gasite = {v["clasa"] for v in CL.CLASIFICARE.values()} | {r["clasa"] for r in CL.REGULI}
    assert gasite <= permise, "clase în afara vocabularului: %s" % sorted(gasite - permise)


def test_falsii_pozitivi_numesc_oarbirea_care_i_a_produs():
    """Un „fals pozitiv" care nu spune PRIN CE s-a înșelat instrumentul e o scutire, nu o
    clasificare."""
    falsi = [k for k, v in CL.CLASIFICARE.items() if v["clasa"] == CL.FALS]
    assert falsi, "niciun fals pozitiv individual: clasificarea nu s-a confruntat cu instrumentul"
    scurte = {k for k in falsi if len(CL.CLASIFICARE[k]["de_ce"].strip()) < 120}
    assert scurte == set(), "falși pozitivi fără oarbirea numită: %s" % sorted(scurte)


# ============================================================================
#  EFECTELE PE CARE `ROLLBACK` NU LE DESFACE
# ============================================================================

def _situri_externe(inv):
    """`{fisier:funcție}` — locurile unde un efect extern se face cât timp există scrieri necomise.

    Cheia e funcția care găzduiește apelul, nu linia: prima formă era pe `fisier:linie`, iar prima
    editare a fișierului a făcut toate verdictele lui să pară stătute, deși codul era același."""
    out = set()
    for x in inv:
        for e in x["analiza"]["extern_in_tranzactie"]:
            out.add(e["unde"])
    return out


def test_fiecare_efect_din_tranzactie_e_judecat(inventar):
    """Analiza SEPARATĂ a efectelor pe care `rollback` nu le desface: lista e derivată mecanic,
    judecata e scrisă. Un loc nou, nejudecat, cade poarta."""
    inv, _stat = inventar
    situri = _situri_externe(inv)
    assert situri, "niciun efect extern în tranzacție: proba s-ar uita într-un loc gol"
    nejudecate = situri - set(CL.EFECTE_EXTERNE)
    assert nejudecate == set(), (
        "locuri cu efect extern înăuntrul unei tranzacții care scrie, fără verdict scris în "
        "core/p4_clasificare.EFECTE_EXTERNE: %s" % sorted(nejudecate))


def test_niciun_verdict_de_efect_nu_ramane_fara_loc(inventar):
    """Oglinda: un verdict rămas despre un loc care nu mai există descrie o lume dispărută."""
    inv, _stat = inventar
    orfane = set(CL.EFECTE_EXTERNE) - _situri_externe(inv)
    assert orfane == set(), "verdicte fără loc în cod (stătute): %s" % sorted(orfane)


def test_fiecare_verdict_de_efect_e_scris_si_din_vocabular():
    """Un verdict trebuie să spună CE E locul și CE S-A HOTĂRÂT, cu felul din vocabular."""
    permise = {CL.INTEROGARE, CL.EFECT}
    feluri = {v["fel"] for v in CL.EFECTE_EXTERNE.values()}
    assert feluri <= permise, "feluri în afara vocabularului: %s" % sorted(feluri - permise)
    scurte = {k for k, v in CL.EFECTE_EXTERNE.items()
              if len(str(v.get("verdict", "")).strip()) < 80
              or not str(v.get("ce_e", "")).strip()}
    assert scurte == set(), "verdicte fără conținut: %s" % sorted(scurte)


def test_exista_si_interogari_si_efecte():
    """CALIBRARE ÎN AMBELE DIRECȚII pe chiar tabelul de judecăți: dacă tot ce e acolo ar fi
    „interogare", tabelul ar fi o scutire în bloc; dacă tot ar fi „efect", n-ar deosebi nimic."""
    feluri = [v["fel"] for v in CL.EFECTE_EXTERNE.values()]
    assert CL.INTEROGARE in feluri and CL.EFECT in feluri, (
        "tabelul de efecte nu deosebește nimic: %s" % sorted(set(feluri)))
