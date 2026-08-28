# -*- coding: utf-8 -*-
"""GARD [Z, 28.08.2026]: mesajul de commit nu poate purta octeți de control.

DE UNDE VINE, și e din aceeași zi cu regula. Am scris un escape de tip BACKSPACE într-un literal
Python **ne-raw**, într-un script de patch, iar el a ajuns în fișier ca octet de control.
`core/test_octeti_invizibili.py` l-a prins **în cod**, și poarta a picat — corect. Apoi am scris
**exact aceeași greșeală în MESAJUL DE COMMIT care descria prima greșeală**, unde nu o prindea
nimic. Am văzut-o cu ochii, la recitire.

Mesajul de commit e singurul artefact de tip raport care rămâne pe disc. Un octet de control în el
**nu se vede la citire** — terminalul îl consumă —, dar corupe fișierul și orice căutare peste
istoric. *„Verificat caracter cu caracter după fiecare commit"* exista ca **practică**; de azi e
**poartă**.

CE FACE IMPOSIBIL: un mesaj de commit cu BACKSPACE, VT, FF, ESC, NUL sau alt octet de control.

CE NU FACE, declarat:
  - **nu se uită la conținut** — aia e treaba celorlalte trei porți din `commit-msg`;
  - **n-are escape motivat**, spre deosebire de ele: nu există mesaj legitim cu octeți de control,
    deci nu există motiv de ocolit;
  - **nu acoperă mesajele deja scrise în istoric.** Ce e scris e scris.
"""
import io
import os
import subprocess
import tempfile

import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_HOOK = os.path.join(_RAD, "scripts", "githooks", "commit-msg")


def _ruleaza(continut_bytes):
    """Rulează hook-ul pe un mesaj dat, într-un depozit git GOL.

    De ce depozit gol, și nu cel real: celelalte trei porți din `commit-msg` citesc
    `git diff --cached`. Într-un depozit real, rezultatul lor ar depinde de ce e în stage în
    momentul rulării — adică testul ar măsura starea mea de lucru, nu hook-ul. Într-unul gol,
    singura poartă care se poate aprinde e cea verificată aici.
    """
    with tempfile.TemporaryDirectory() as d:
        subprocess.run(["git", "init", "-q", "."], cwd=d, check=True, capture_output=True)
        io.open(os.path.join(d, "MSG"), "wb").write(continut_bytes)
        r = subprocess.run(["sh", _HOOK, "MSG"], cwd=d, capture_output=True, text=True)
        return r.returncode, (r.stdout or "") + (r.stderr or "")


def test_hookul_exista_si_e_executabil():
    assert os.path.exists(_HOOK), "`scripts/githooks/commit-msg` a dispărut"
    assert os.access(_HOOK, os.X_OK), "hook-ul nu mai e executabil"


def test_un_mesaj_cu_BACKSPACE_e_RESPINS():
    cod, iesire = _ruleaza(b"reparatie mica\n\nun octet aici: \x08 si atat\n")
    assert cod == 1, "hook-ul a acceptat un mesaj cu BACKSPACE (exit %d):\n%s" % (cod, iesire)
    assert iesire.count("OCTETI DE CONTROL"), (
        "a respins, dar din alt motiv — mesajul nu numește clasa:\n%s" % iesire)


@pytest.mark.parametrize("octet", [b"\x0b", b"\x0c", b"\x1b", b"\x00", b"\x07"])
def test_si_restul_clasei_e_RESPINS(octet):
    """Nu doar BACKSPACE: clasa întreagă. Un gard scris pe instanța care a durut și atât ar fi
    lăsat afară exact octetul următor."""
    cod, _iesire = _ruleaza(b"mesaj\n\ncu octet" + octet + b" in el\n")
    assert cod == 1, "octetul %r a trecut" % octet


# Un mesaj REAL, cu tot ce poartă mesajele mele: diacritice, ghilimele românești, tab, rânduri
# goale, trailer. Se construiește din bucăți ca să nu depindă de citate în literal — ghilimeaua
# românească de închidere într-un literal cu ghilimele duble e chiar greșeala de sintaxă pe care am
# făcut-o de cinci ori în două zile (METODA §10, „Ghilimelele românești rup șirul Python").
_GHIL_D = "„"          # „
_GHIL_I = "”"          # ”
_MESAJ_NORMAL = (
    "Reparație cu diacritice: șțăîâ ȘȚĂÎÂ\n\n"
    + "Un citat: " + _GHIL_D + "așa a spus" + _GHIL_I + ", și un tab:\tcoloană.\n"
    + "Un rând gol mai jos.\n\n"
    + "Co-Authored-By: cineva <x@y.z>\n"
).encode("utf-8")


def test_un_mesaj_NORMAL_trece():
    """Direcția cealaltă, și e cea care contează: un gard care respinge tot n-ar fi un gard."""
    cod, iesire = _ruleaza(_MESAJ_NORMAL)
    assert cod == 0, "un mesaj normal a fost respins (exit %d):\n%s" % (cod, iesire)


def test_CALIBRARE_newline_si_tab_NU_sunt_in_clasa():
    """Amândouă sunt octeți de control după standard, și amândouă sunt legitime într-un mesaj.
    Dacă ar intra în clasă, **niciun** mesaj n-ar mai trece — iar un gard care respinge tot se
    citește la fel de ușor ca unul care merge, până încerci."""
    cod, _iesire = _ruleaza(b"linie unu\n\tindentat\n\nlinie trei\n")
    assert cod == 0


def test_CALIBRARE_gardul_NU_inghite_celelalte_trei_porti():
    """Anti-vacuu de al doilea fel: hook-ul are patru porți, iar cea nouă e ULTIMA. Dacă ar fi pusă
    înaintea celorlalte și ar ieși devreme, le-ar stinge fără ca nimic să spună. Se probează pe o
    poartă veche: un mesaj care semnalează un defect nereparat, fără să spună unde e consemnat."""
    cod, iesire = _ruleaza("am observat ca ceva nu merge, si ramane asa\n".encode("utf-8"))
    assert cod == 1 and iesire.count("un loc"), (
        """poarta „un defect mentionat are un loc” nu se mai aprinde: exit %d\n%s"""
        % (cod, iesire))
