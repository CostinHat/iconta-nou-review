# -*- coding: utf-8 -*-
"""GARD P4 — nicio operație compusă nu rămâne neclasificată, și nicio clasificare nu îmbătrânește.

**CE PĂZEȘTE.** `scripts/scan_tranzactii.py` derivă din cod căile în care o singură operație logică
se sprijină pe mai multe tranzacții, sau amestecă o scriere cu un efect pe care `rollback` nu-l
desface. `core/p4_clasificare.py` spune, pentru fiecare, dacă e critică și **de ce**. Gardul ăsta
leagă cele două:

  1. **fiecare** cale peste prag e clasificată — una nouă, neclasificată, cade poarta;
  2. **fiecare** clasificare corespunde unei căi reale — o intrare rămasă din trecut cade poarta,
     afară de cele marcate `reparat`, care rămân ca urmă a reparației;
  3. **fiecare** excludere din critic poartă un motiv scris, nu o etichetă;
  4. **fiecare** cale critică numește o probă de injecție de defect **care există** — asta e chiar
     criteriul `CRITICAL_COMPOSITES_WITH_FAULT_TESTS = CRITICAL_COMPOSITES`, verificat mecanic, nu
     afirmat în raport.

**DE CE E NEVOIE DE EL.** O clasificare făcută o dată, într-o zi, e adevărată în ziua aia. Ruta a
o suta unu, adăugată peste trei săptămâni, cu o a doua tranzacție în ea, n-ar întâlni nimic —
exact clasa „regulă scrisă care nu e regulă păzită”.

**PREMISA ANTI-VACUU.** Un gard care se uită într-un loc gol raportează verde despre o lume pe care
n-o vede. Aici: dacă inventarul e gol, sau dacă instrumentul nu se mai calibrează, gardul PICĂ —
nu trece.

**ASERȚIUNILE SUNT PE STRUCTURĂ** (METODA §23): mulțimi de chei, nu căutări de șiruri în text.
"""
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


def _peste_prag(inv):
    """Căile care cer clasificare: scrieri în mai multe tranzacții, commit parțial, sau efect
    ireversibil înăuntrul unei tranzacții care scrie."""
    out = {}
    for x in inv:
        a = x["analiza"]
        if (a["domenii_care_scriu"] > 1 or a["partial_commit"]
                or a["extern_in_tranzactie"]):
            out[x["intrare"]] = a
    return out


@pytest.fixture(scope="module")
def inventar():
    inv, stat = ST.inventar()
    return inv, stat


def test_instrumentul_se_calibreaza():
    """PREMISA. Fără calibrare trecută, orice cifră de mai jos e despre altceva."""
    assert ST.calibreaza(verbose=False) is True


def test_inventarul_nu_e_gol(inventar):
    """ANTI-VACUU. Un inventar gol ar face toate celelalte probe să treacă degeaba."""
    inv, stat = inventar
    assert stat["intrari"] > 100, "prea puține puncte de intrare: instrumentul nu vede aplicația"
    assert len(_peste_prag(inv)) > 0, "nicio cale peste prag: gardul s-ar uita într-un loc gol"


def test_nicio_cale_ramane_neclasificata(inventar):
    """(1) O cale compusă nouă nu poate intra tăcut: cere o clasificare, cu motiv."""
    inv, _stat = inventar
    peste_prag = set(_peste_prag(inv))
    clasificate = set(CL.CLASIFICARE)
    neclasificate = peste_prag - clasificate
    assert neclasificate == set(), (
        "căi compuse fără clasificare în core/p4_clasificare.py: %s"
        % sorted(neclasificate))


def test_nicio_clasificare_nu_ramane_fara_cale(inventar):
    """(2) O intrare rămasă din trecut ar descrie o lume care nu mai există.

    Excepția, declarată: intrările marcate `reparat` — reparația le-a scos din inventar, iar
    urma reparației trebuie să rămână. Și cele marcate `cale_interna`, care nu sunt puncte de
    intrare, ci funcții din interiorul lor."""
    inv, _stat = inventar
    peste_prag = set(_peste_prag(inv))
    orfane = {k for k, v in CL.CLASIFICARE.items()
              if k not in peste_prag and not v.get("reparat")
              and not v.get("cale_interna")}
    assert orfane == set(), (
        "clasificări fără cale în inventar (stătute): %s" % sorted(orfane))


def test_fiecare_excludere_are_motiv_scris():
    """(3) Comanda P4: `UNEXPLAINED_EXCLUSIONS = 0`. Verificat pe conținut, nu pe prezență."""
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
    """Numele funcțiilor de test definite în fișierul de injecție. Derivat cu `ast`, nu căutat
    ca text: o probă comentată sau redenumită trebuie să cadă, nu să treacă pe potrivire de șir."""
    import ast
    import io
    if not os.path.exists(FISIER_PROBE):
        return set()
    arbore = ast.parse(io.open(FISIER_PROBE, encoding="utf-8").read())
    return {n.name for n in ast.walk(arbore)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}


def test_fiecare_cale_critica_are_proba_de_injectie():
    """(4) `CRITICAL_COMPOSITES_WITH_FAULT_TESTS = CRITICAL_COMPOSITES`, mecanic.

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
    gasite = {v["clasa"] for v in CL.CLASIFICARE.values()}
    assert gasite <= permise, "clase în afara vocabularului: %s" % sorted(gasite - permise)


def test_falsii_pozitivi_numesc_oarbirea_care_i_a_produs():
    """Un „fals pozitiv" care nu spune PRIN CE s-a înșelat instrumentul e o scutire, nu o
    clasificare. Fiecare trebuie să trimită la o oarbire declarată în antetul scanerului."""
    falsi = [k for k, v in CL.CLASIFICARE.items() if v["clasa"] == CL.FALS]
    assert falsi, "niciun fals pozitiv: probabil clasificarea nu s-a confruntat cu instrumentul"
    scurte = {k for k in falsi if len(CL.CLASIFICARE[k]["de_ce"].strip()) < 120}
    assert scurte == set(), "falși pozitivi fără oarbirea numită: %s" % sorted(scurte)


# ============================================================================
#  EFECTELE PE CARE `ROLLBACK` NU LE DESFACE — analiza separată, păzită la fel
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
    """Comanda P4 cere analiza SEPARATĂ a efectelor pe care `rollback` nu le desface.

    Lista lor e derivată mecanic; judecata — interogare sau efect, și ce s-a hotărât — e scrisă
    în `EFECTE_EXTERNE`. Un loc nou, nejudecat, cade poarta."""
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
    """Un verdict trebuie să spună CE E locul și CE S-A HOTĂRÂT, cu felul din vocabularul declarat."""
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
