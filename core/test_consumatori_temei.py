# -*- coding: utf-8 -*-
"""GARD [06.09.2026, R171]: graful „cine consumă valoarea" pentru temeiurile din afara registrului.

**Ce păzește.** Pragul de reverificare se compune din frecvență și **consecință**. Consecința se
calcula numai prin lanțul `articol → cheie din COTE → funcții`, care se rupe la primul pas pentru
orice temei care nu e în registrul de cote — adică pentru toate cele scrise după **decizia 73**, care
cere ca temeiul să stea în modulul REGULII. Măsurat: **19 din 42** de temeiuri fără prag ieșeau
NECUNOSCUT *prin construcție*.

**Proprietatea apărată, și e una singură:** *orice temei a cărui frecvență se poate citi are și un
consumator numit.* Dacă apare unul care n-are, ori codul nu-l folosește (și atunci e o urmă de
intenție, clasa R23), ori graful nu-l vede — și amândouă trebuie să cadă aici, nu peste șase luni
într-o cifră fiscală.

**CE NU PĂZEȘTE, declarat**: că valoarea e folosită CORECT. Graful spune că e citită, nu că e citită
cum trebuie. Ca peste tot: e o potrivire, nu o citire.
"""
import os
import sys

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _RAD not in sys.path:
    sys.path.insert(0, _RAD)

from core import consumatori_temei as C  # noqa: E402
from core import reverificare as R  # noqa: E402
from core import scan_citate  # noqa: E402


def _inv():
    return {c: t for c, t, _v in scan_citate.inventar()}


# ── ANTI-VACUU ─────────────────────────────────────────────────────────────────────────────────

def test_ANTI_VACUU_harta_cititorilor_chiar_vede_codul():
    """Dacă harta s-ar goli, toate verdictele de mai jos ar fi NECUNOSCUT, iar gardul ar trece pe
    o mulțime goală raportând «nimic nu consumă nimic»."""
    h = C.harta_cititori()
    assert len(h) > 2000, "harta cititorilor are doar %d perechi (fișier, nume) — s-a rupt" % len(h)
    fisiere = {f for f, _n in h}
    assert len(fisiere) > 80, "doar %d fișiere scanate" % len(fisiere)
    # operator de MULȚIME, nu apartenență:  crapă pe un șir,  ar trece pe el (METODA §23)
    assert fisiere >= {"main.py"}, "main.py nu e scanat — cititorii direcți din rute nu se văd"


# ── CALIBRARE, ÎN AMBELE DIRECȚII ──────────────────────────────────────────────────────────────

def test_un_temei_care_ajunge_intr_o_declaratie_iese_DEPUS():
    """Cazul cunoscut-bun: poziția 116 din D100 e citită de `d100.py`, adică pleacă la ANAF."""
    inv = _inv()
    cale = "d100_pozitia_116.TEMEI_CAND_SE_DATOREAZA"
    r = C.consumatori(cale, inv.get(cale))
    assert r["verdict"] == "DEPUS", r
    assert any(x.startswith("d100.py::") for x in r["declaratii"]), r["declaratii"]


def test_un_temei_citit_dar_fara_declaratie_iese_CALCULAT():
    """Cazul cunoscut-bun de cealaltă parte: registrul-inventar e cod viu, dar nu produce o
    declarație. `CALCULAT`, nu `DEPUS` — iar deosebirea e chiar ce dă pragul."""
    inv = _inv()
    cale = "registru_inventar.TEMEI_CONTINUT"
    r = C.consumatori(cale, inv.get(cale))
    assert r["verdict"] == "CALCULAT", r
    assert r["directi"] and not r["declaratii"], r


def test_un_temei_pe_care_nu_l_citeste_nimeni_iese_NECUNOSCUT():
    """Direcția inversă: graful nu are voie să inventeze un consumator. O cale către un modul care
    nu există nu poate produce decât `NECUNOSCUT`."""
    r = C.consumatori("modul_inexistent_xyz.TEMEI_INVENTAT")
    assert r["verdict"] == "NECUNOSCUT" and not r["directi"], r


def test_caile_din_registrul_de_cote_nu_trec_pe_aici():
    """`COTE.tva_standard[0][2]` are deja lanțul ei prin `dependenti_act`. Dacă graful ăsta ar
    răspunde și pentru ele, ar exista două surse pentru aceeași întrebare."""
    r = C.consumatori("COTE.tva_standard[0][2]")
    assert r["modul"] is None and r["verdict"] == "NECUNOSCUT", r


def test_ALIASURILE_aceluiasi_temei_se_urmaresc():
    """Același obiect e legat de mai multe nume: `TEMEI` (dicționarul) și `TEMEI_PROFIT`
    (constanta). `scan_citate` raportează primul, codul îl citește pe al doilea.

    Prima formă a grafului potrivea un singur nume și scotea `NECUNOSCUT` pe o valoare cu doi
    cititori — *o sub-aproximare arată exact ca o absență*. Dacă urmărirea aliasurilor se pierde,
    testul ăsta cade."""
    inv = _inv()
    cale = "registru_evidenta_fiscala.TEMEI.profit"
    r = C.consumatori(cale, inv.get(cale))
    assert set(r["nume"]) >= {"TEMEI_PROFIT"}, r["nume"]
    assert r["directi"], "aliasul nu s-a urmărit — verdictul ar fi fals NECUNOSCUT"
    # fără temeiul obiect, se potrivește doar numele din cale, deci NU găsește nimic:
    assert not C.consumatori(cale)["directi"], "fără obiect n-ar trebui să găsească aliasul"


# ── PROPRIETATEA ───────────────────────────────────────────────────────────────────────────────

def test_orice_temei_cu_frecventa_citibila_are_un_consumator():
    """Miezul. Dacă articolul se poate confrunta (deci frecvența e citibilă), atunci trebuie să se
    poată spune și UNDE ajunge valoarea. Un temei fără consumator e ori o urmă de intenție (R23),
    ori o gaură în graf — și niciuna nu are voie să treacă tăcut ca «prag necalculabil»."""
    orfane = [(x["cale"], x["temei"]) for x in R.inventar()
              if x["frecventa"] != "NECUNOSCUT" and x["consecinta"] == "NECUNOSCUT"]
    assert not orfane, (
        "temeiuri cu frecvență citibilă și consecință NECUNOSCUTĂ: %s.\n"
        "Ori nimic din cod nu le citește (atunci e o urmă de intenție — consemneaz-o), ori graful "
        "din `core/consumatori_temei.py` nu le vede (atunci lipsește un drum)." % orfane)
