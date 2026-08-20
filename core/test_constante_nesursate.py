# -*- coding: utf-8 -*-
"""CLICHET (20.08.2026): clasa constantelor fiscale nesursate din PRODUCȚIE nu mai crește.

DE CE UN CLICHET ȘI NU UN XFAIL. Inventarul de pe 31.07 a fost scris ca `xfail` — a *înregistrat*
datoria, n-a *împiedicat-o*. Opt zile mai târziu clasa a produs a cincea apariție. Un xfail e o
notiță; un clichet e o poartă. Datoria existentă rămâne (126 la instalare), dar nu se mai poate mări,
iar arderea ei e vizibilă: fiecare scădere se coboară în BASELINE, deci progresul e ireversibil.

PER FIȘIER, nu global — altfel o reparație într-un modul ar plăti pentru o încălcare nouă în altul,
și totalul ar sta pe loc arătând verde.

CE MĂSOARĂ. `core/scan_constante.py`: literali numerici din modulele fiscale, clasificați după unde
LOCUIESC (constantă de modul / default la lookup / default de parametru / Decimal literal / nume
fiscal), apoi împărțiți după strămoșul sintactic în A=sursat (are `Temei`), B=nomenclator (cod din
XSD/algoritm), C=nesursat, D=precizie. C e ținta.

DIMENSIUNEA CLASEI, măsurată azi: 85 vizibile în teste (inventarul 31.07) + 126 în producție. Partea
invizibilă e mai mare decât cea văzută. Termenele de depunere — motivul pentru care s-a pornit — sunt
4 din 126, deci sursarea lor singură ar fi fost lucru pe un fragment dintr-un întreg nemăsurat.
"""
import pytest

from core import scan_constante

# Instalat 20.08.2026. Se COBOARĂ pe măsură ce constantele primesc temei. Nu se ridică.
BASELINE = {
    "common.py": 9, "control_fiscal_api.py": 1, "cote_tva.py": 2, "d101.py": 8, "d101g.py": 1,
    "d104.py": 4, "d108.py": 2, "d169.py": 1, "d169n.py": 1, "d205.py": 2, "d212_engine.py": 13,
    "d216.py": 1, "d300.py": 5, "d300_reconciliere.py": 5, "d394.py": 9, "d398.py": 1,
    "d401.py": 2, "d402.py": 3, "d403.py": 5, "d406.py": 7, "d406_active.py": 7,
    "d406_stocuri.py": 1, "d407.py": 2, "salariati_api.py": 1, "salarizare.py": 19,
    "scadente.py": 4, "stat_plata_api.py": 1, "tva_agricultori.py": 2, "tva_aur.py": 1,
    "tva_marja.py": 2, "tva_marja_turism.py": 4,
}


@pytest.fixture(scope="module")
def inv():
    return scan_constante.inventar()


def _pe_fisier(inv):
    d = {}
    for h in inv:
        if h["cls"] == "C":
            d[h["f"]] = d.get(h["f"], 0) + 1
    return d


def test_clichetul_nu_creste(inv):
    """Miezul. Un fișier nou fiscal pornește de la 0 — orice constantă nesursată în el pică."""
    acum = _pe_fisier(inv)
    crescut = []
    for f, n in sorted(acum.items()):
        lim = BASELINE.get(f, 0)
        if n > lim:
            noi = [h for h in inv if h["cls"] == "C" and h["f"] == f][lim:]
            crescut.append("  %s: %d > %d  (ex: l.%s `%s` — %s)"
                           % (f, n, lim, noi[0]["l"], noi[0]["v"], noi[0]["txt"][:60]) if noi
                           else "  %s: %d > %d" % (f, n, lim))
    assert not crescut, (
        "constante fiscale NESURSATE în plus față de clichet:\n" + "\n".join(crescut)
        + "\n\nRemediu: atașează un `Temei(...)` (vezi common.COTE) sau mută valoarea în registru."
        + "\nDacă e nomenclator (cod din XSD, pondere de checksum), botează-l ca atare — vezi"
        + " scan_constante.NOM — și scrie de unde vine.")


def test_baseline_nu_e_stat(inv):
    """Anti-datorie-stătută: dacă un fișier a coborât, BASELINE trebuie coborât cu el."""
    acum = _pe_fisier(inv)
    stat = ["  %s: clichet %d, real %d" % (f, n, acum.get(f, 0))
            for f, n in sorted(BASELINE.items()) if acum.get(f, 0) < n]
    assert not stat, (
        "clichetul e mai larg decât realitatea — coboară-l, altfel datoria poate reveni tăcut:\n"
        + "\n".join(stat))


# ─────────── ANTI-VACUU: calibrare în TREI direcții ───────────
# O singură țintă lasă scanul să treacă pe gol în celelalte. Prima versiune a scanului a picat pe
# `25`; a doua a trecut `25` dar a pus `4050` (care ARE Temei) în nesursate. Fiecare direcție a picat
# o dată în construcție — de-aia sunt toate trei aici, nu doar cea care a picat ultima.

def _clasa(inv, fisier, valoare, casa=None):
    r = [h for h in inv if h["f"] == fisier and h["v"] == valoare and (casa is None or h["casa"] == casa)]
    return r[0]["cls"] if r else None


def test_calibrare_vede_nesursatul(inv):
    """`_ZIUA.get(tip, 25)` — ziua de scadență implicită. Nu apare în NICIUN test; e cazul care a
    dovedit că inventarul de pe 31.07 era orb prin construcție."""
    assert _clasa(inv, "scadente.py", "25", "H2") == "C", \
        "scanul nu mai vede ziua 25 din _ZIUA — dacă `scadente.py` s-a schimbat, refă calibrarea"


def test_calibrare_nu_confunda_sursatul(inv):
    """`Decimal("4050")` are `Temei("HG", 1506, 2024)` alături. A raporta-o ca nesursată ar umfla
    datoria cu exact cazurile bune și ar face clichetul de neîncredere."""
    assert _clasa(inv, "common.py", "4050") == "A"


def test_calibrare_separa_nomenclatorul(inv):
    """`_JUD.get(j, 40)` — codul județului. Are sursă, dar e SIRUTA/XSD, nu Cod fiscal; se revizuiește
    altfel. Amestecat în C, ar dilua ținta."""
    assert _clasa(inv, "bilant_api.py", "40", "H2") == "B"


def test_scanul_chiar_vede_toate_clasele(inv):
    """Dacă regexul de module sau parserul se rupe, listele se golesc și clichetul ar trece pe gol."""
    from collections import Counter
    c = Counter(h["cls"] for h in inv)
    assert c["A"] >= 20 and c["B"] >= 100 and c["C"] >= 50, \
        "distribuție implauzibilă — scanul s-a rupt, nu s-a reparat codul: %s" % dict(c)
    assert len({h["f"] for h in inv}) >= 40, "prea puține module fiscale văzute: verifică scan_constante.FIS"
