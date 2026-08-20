# -*- coding: utf-8 -*-
"""GARD DE CLASĂ (21.08.2026): „niciun X înregistrat" nu poate deveni „nu se datorează".

DE CE UN GARD ȘI NU O A PATRA REPARAȚIE. Clasa a apărut de patru ori în două zile — trei D301 (R2′,
20.08) și D205 (21.08, forțată de o depunere care contrazicea verdictul). Discriminatorul e
FORMULAREA, observat de Costin: *„niciun X înregistrat" e aproape întotdeauna `absenta_observatie`*.
Absența unei înregistrări într-o sursă a NOASTRĂ nu e absența unui fapt din lume; criteriul de
separare e REMEDIUL — „verifică dacă faptul a existat" aparține lui «Nu pot verifica», NICIODATĂ lui
«Nu se datorează». Precedent: tenant_006, unde tiparul a produs „nu se datorează" pe o firmă cu
achiziții intracomunitare reale.

CE MĂSOARĂ. Fiecare șir din `control_fiscal_api` care spune «nu se datorează» (motivele care ajung
la contabil, nu docstringuri). Dacă e formulat ca absență, trebuie să fie într-un registru de
excepții MOTIVATE — fiecare cu poarta care face absența măsurată, nu presupusă.

CE NU FACE. Nu judecă dacă poarta e destul de bună; judecă doar că a fost NUMITĂ. O poartă slabă
scrisă în registru se vede și se poate contesta; una nescrisă nu.
"""
import ast
import io
import os
import re

import pytest

_FIS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "control_fiscal_api.py")

# Formularea-simptom: absența unei observații, prezentată ca fapt despre lume.
_ABSENTA = re.compile(r"niciun\b|nicio\b|fără\s+(venituri|rulaj|operațiun|înregistr|not[ăe])"
                      r"|nu\s+are\s+operațiun|lipsesc", re.I)

# Excepții MOTIVATE: absență + poartă de completitudine numită, SAU absență care își numește sursa.
# Cheia = o bucată din șir; valoarea = poarta, scrisă ca s-o poată contesta cineva.
_ABSENTA_MOTIVATA = {
    "fără venituri în trimestru":
        "Poartă reală: `d100_fapt` distinge False (trimestru genuin gol — fără venituri ȘI fără "
        "facturi emise) de None (venituri 0 dar există facturi emise → gri). Absența e MĂSURATĂ.",
    "nicio operațiune intracomunitară în lună":
        "Poartă: se confirmă doar pe LUNA ÎNCHISĂ, și doar pe ultima închisă; sursa faptului e "
        "reuniunea facturi IC + operațiuni manuale + d301, nu o bifă.",
    "Vectorul fiscal declară că firma nu are operațiuni intracomunitare":
        "Nu afirmă despre lume: își numește SURSA (bifa din Vector) și poartă remediul "
        "(„corectează Vectorul fiscal”). Selectorul are nevoie de o decizie binară.",
}


def _siruri_vizibile():
    """Șirurile literale din modul, FĂRĂ docstringuri (alea explică, nu afirmă către contabil)."""
    src = io.open(_FIS, encoding="utf-8").read()
    arb = ast.parse(src)
    doc = set()
    for n in ast.walk(arb):
        if isinstance(n, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            corp = getattr(n, "body", None)
            if corp and isinstance(corp[0], ast.Expr) and isinstance(corp[0].value, ast.Constant) \
               and isinstance(corp[0].value.value, str):
                doc.add(id(corp[0].value))
    out = []
    for n in ast.walk(arb):
        if isinstance(n, ast.Constant) and isinstance(n.value, str) and id(n) not in doc:
            out.append((getattr(n, "lineno", 0), n.value))
        elif isinstance(n, ast.JoinedStr):
            buc = "".join(p.value for p in n.values
                          if isinstance(p, ast.Constant) and isinstance(p.value, str))
            out.append((getattr(n, "lineno", 0), buc))
    return out


@pytest.fixture(scope="module")
def motive():
    return [(l, s) for l, s in _siruri_vizibile() if "nu se datorează" in s]


def test_niciun_motiv_nou_formulat_ca_absenta(motive):
    """Miezul. Un motiv nou care spune «niciun/nicio/fără X» pică — sau își numește poarta în
    `_ABSENTA_MOTIVATA`, sau se mută la «Nu pot verifica»."""
    rele = []
    for ln, s in motive:
        if not _ABSENTA.search(s):
            continue
        if any(k in s for k in _ABSENTA_MOTIVATA):
            continue
        rele.append("  control_fiscal_api.py:%d  «%s»" % (ln, " ".join(s.split())[:110]))
    assert not rele, (
        "motiv «nu se datorează» formulat ca ABSENȚĂ, fără poartă numită:\n" + "\n".join(rele)
        + "\n\nAbsența unei înregistrări nu e absența unui fapt. Ori muți intrarea în `neclar` "
        "(«nu pot verifica») cu remediul «verifică dacă faptul a existat», ori — dacă absența e "
        "măsurată — adaugi poarta în `_ABSENTA_MOTIVATA`, scrisă ca s-o poată contesta cineva.")


def test_d205_nu_mai_e_nu_se_datoreaza(motive):
    """A patra instanță, legată. „Niciun rulaj pe 457" a fost «nu se datorează» până pe 21.08, când
    o depunere reală (BETA PROFIT, D205/12-2025) a contrazis verdictul."""
    assert not [s for _, s in motive if "457" in s], \
        "D205 e iar «nu se datorează» pe absența rulajului pe 457"
    src = io.open(_FIS, encoding="utf-8").read()
    assert "nu pot verifica: am note validate" in src, \
        "reîncadrarea D205 a dispărut — trebuie să rămână în «nu pot verifica», cu remediul scris"


def test_d301_pe_fapt_a_ramas_reincadrat():
    """A doua-a-treia instanță (R2′, 20.08), ca să nu se întoarcă tăcut."""
    src = io.open(_FIS, encoding="utf-8").read()
    assert "Absența înregistrărilor" in src and "nu dovedește absența operațiunilor" in src


# ─────────── ANTI-VACUU ───────────

def test_scanul_chiar_gaseste_motive(motive):
    """Un gard care nu găsește nimic TRECE. Dacă parserul sau formularea se schimbă, lista se
    golește și gardul ar păzi o lume pe care n-o vede."""
    assert len(motive) >= 8, "prea puține motive «nu se datorează» găsite: %d" % len(motive)
    assert any(_ABSENTA.search(s) for _, s in motive), \
        "niciun motiv formulat ca absență — dacă e adevărat, `_ABSENTA_MOTIVATA` trebuie golit"


def test_exceptiile_nu_imbatranesc(motive):
    """Anti-vacuu pe exceptare: o poartă scrisă pentru un șir care nu mai există e o notă despre o
    lume dispărută."""
    text = " ".join(s for _, s in motive)
    moarte = [k for k in _ABSENTA_MOTIVATA if k not in text]
    assert not moarte, "excepții care nu mai corespund niciunui motiv — scoate-le: %s" % moarte


def test_fiecare_exceptie_isi_scrie_poarta():
    """O excepție fără motiv scris e o listă în care se pot ascunde intrări noi."""
    goale = [k for k, v in _ABSENTA_MOTIVATA.items() if len((v or "").strip()) < 40]
    assert not goale, "excepții fără poartă scrisă: %s" % goale
