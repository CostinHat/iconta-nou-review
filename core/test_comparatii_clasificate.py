# -*- coding: utf-8 -*-
"""GARDA PE DIRECTIA INVERSA: o comparatie pe o valoare de registru e CLASIFICATA. (P11, 22.08.2026)

Cerinta lui Costin: „o comparatie pe o valoare de registru trebuie ori sa fie determinata de temeiul
citat, ori sa poarte o interpretare".

INTREBAREA LUI, SI DE CE SCHIMBA CONSTRUCTIA. „«Determinata de temeiul citat» - cum se verifica
mecanic? Daca e prin prezenta unui text_citat pe intrarea din registru, garda cere doar EXISTENTA
citarii, nu ca ea chiar sa determine comparatia. E a cincea instanta de garda care citeste proza?"

DA, ar fi fost. Deci garda NU se construieste asa. Ce face si ce NU face:

  CE FACE (mecanic, pe COD, verificabil):
    - fiecare comparatie pe o valoare de registru trebuie sa fie CLASIFICATA de autor;
    - clasificarea „determinat de temei" trebuie sa numeasca o CHEIE care se rezolva in registru -
      un LINK verificabil, nu o fraza. Daca cheia nu exista, garda pica;
    - clasificarea „interpretare" trebuie sa numeasca o cheie care se rezolva in registrul de
      interpretari, care la randul lui CERE variantele.

  CE NU FACE, declarat: nu verifica ca temeiul CHIAR determina comparatia. Aia e o judecata
  semantica; nicio masina n-o poate face, iar o garda care ar pretinde ca o face ar fi mai rea decat
  una care nu exista - fiindca ar transforma o citire umana intr-un verde automat.

  Deci garda inchide clasa NECLASIFICAT, nu clasa GRESIT CLASIFICAT. Diferenta e reala si se scrie.

CLICHET, nu interdictie imediata: la instalare exista comparatii neclasificate. Numarul coboara,
nu urca. O comparatie NOUA neclasificata pica din prima.
"""
import ast
import io
import os

import pytest

from core import common
from core.interpretare import Interpretare
from core.registru_interpretari import INTERPRETARI

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SARI = ("test_", "scan_", "migrare_", "conftest", "verificator_conformitate")

# Marcajul, in cod, pe linia comparatiei sau deasupra ei. Payload-ul e VERIFICABIL:
#   # temei-determina: <cheie din common.COTE>
#   # interpretare: <cheie din registru_interpretari.INTERPRETARI>
MARCAJ_TEMEI = "temei-determina:"
MARCAJ_INTERP = "interpretare:"

# Masurat 22.08.2026: 15 comparatii de egalitate stricta pe valori de registru, din care 2 confirmate
# ca interpretari reale la re-citire pe CONTEXT (nu pe linie). Cele doua au fost marcate imediat,
# deci clichetul porneste de la 13.
#
# CE INSEAMNA CIFRA ASTA, si ce NU inseamna: 13 comparatii NECLASIFICATE. Majoritatea sunt aproape
# sigur zgomot (formatare `cota == cota.to_integral_value()`, verificari de zero, stari interne) -
# dar „aproape sigur" nu e o clasificare, si de-aia stau aici. Cine le priveste si le gaseste
# nevinovate le marcheaza `temei-determina:` sau le scoate din domeniu cu motiv; ce ramane e alegere.
BASELINE_NECLASIFICATE = 13


def _fisiere():
    for rad, dirs, fis in os.walk(RAD):
        dirs[:] = [d for d in dirs if d not in ("venv", ".git", "_arhiva", "node_modules",
                                                "__pycache__", "frontend_test", "date_test")]
        for f in fis:
            if f.endswith(".py") and not f.startswith(SARI):
                p = os.path.join(rad, f)
                yield p, os.path.relpath(p, RAD).replace(os.sep, "/")


def _e_registru(x):
    if isinstance(x, ast.Name):
        s = x.id.lower()
        return any(k in s for k in ("sm", "salariu_minim", "plafon", "prag", "cota", "minim"))
    if isinstance(x, ast.Call):
        f = x.func.attr if isinstance(x.func, ast.Attribute) else getattr(x.func, "id", "")
        return f == "cota"
    return False


def _marcaj(linii, ln):
    """Marcajul de pe linia comparatiei sau din blocul de comentarii de deasupra."""
    candidate = [linii[ln - 1]]
    i = ln - 2
    while i >= 0 and linii[i].strip().startswith("#"):
        candidate.append(linii[i])
        i -= 1
    for l in candidate:
        for m in (MARCAJ_TEMEI, MARCAJ_INTERP):
            if m in l:
                return m, l.split(m, 1)[1].strip().split()[0].rstrip(",.;")
    return None, None


def _egalitati():
    """[(fisier, linie, text, marcaj, cheie)] pentru fiecare egalitate stricta pe o valoare de registru."""
    out = []
    for p, rel in sorted(_fisiere(), key=lambda x: x[1]):
        src = io.open(p, encoding="utf-8").read()
        linii = src.split("\n")
        try:
            arb = ast.parse(src)
        except SyntaxError:
            continue
        for n in ast.walk(arb):
            if not isinstance(n, ast.Compare) or not n.ops:
                continue
            if not isinstance(n.ops[0], ast.Eq):
                continue
            if not any(_e_registru(x) for x in [n.left] + list(n.comparators)):
                continue
            m, cheie = _marcaj(linii, n.lineno)
            out.append((rel, n.lineno, linii[n.lineno - 1].strip()[:80], m, cheie))
    return out


@pytest.fixture(scope="module")
def egalitati():
    return _egalitati()


def test_scanul_isi_vede_lumea(egalitati):
    """ANTI-VACUU. Daca detectorul se strica, garda ar trece pe zero randuri (interdictia 19)."""
    assert len(egalitati) >= 10, (
        "doar %d comparatii vazute - detectorul a orbit, nu codul s-a curatat" % len(egalitati))
    assert any(f == "core/salarizare.py" for f, _l, _t, _m, _c in egalitati), (
        "cazul cunoscut (`vbt == sm` din salarizare) nu mai e vazut")


def test_neclasificatele_nu_cresc(egalitati):
    """CLICHET. O comparatie NOUA pe o valoare de registru trebuie clasificata la scriere."""
    necl = [e for e in egalitati if e[3] is None]
    assert len(necl) <= BASELINE_NECLASIFICATE, (
        "comparatii neclasificate pe valori de registru: %d > %d.\n%s"
        % (len(necl), BASELINE_NECLASIFICATE,
           "\n".join("  %s:%d  %s" % (f, l, t) for f, l, t, _m, _c in necl[:8])))


def test_baseline_nu_e_stale(egalitati):
    """DOC↔COD: cand se clasifica una, clichetul coboara. Altfel plafonul minte."""
    necl = [e for e in egalitati if e[3] is None]
    assert len(necl) >= BASELINE_NECLASIFICATE, (
        "neclasificate: %d < %d — coboara BASELINE_NECLASIFICATE" % (len(necl), BASELINE_NECLASIFICATE))


def test_marcajul_de_temei_numeste_o_cheie_care_EXISTA(egalitati):
    """LINK, nu proza: `# temei-determina: salariu_minim` e verificabil - cheia se rezolva in registru
    sau nu. Ce NU se verifica: ca temeiul chiar DETERMINA comparatia. Aia ramane judecata umana, si
    scrie asta in capul fisierului."""
    rele = ["  %s:%d -> cheia %r nu exista in registru" % (f, l, c)
            for f, l, _t, m, c in egalitati if m == MARCAJ_TEMEI and c not in common.COTE]
    assert not rele, "marcaje de temei care nu se rezolva:\n" + "\n".join(rele)


def test_marcajul_de_interpretare_numeste_o_INTERPRETARE_care_exista(egalitati):
    rele = ["  %s:%d -> interpretarea %r nu e in registru" % (f, l, c)
            for f, l, _t, m, c in egalitati if m == MARCAJ_INTERP and c not in INTERPRETARI]
    assert not rele, "marcaje de interpretare care nu se rezolva:\n" + "\n".join(rele)


def test_registrul_de_interpretari_e_chiar_de_Interpretari():
    """Fiecare intrare trece prin constructorul care CERE variantele - altfel registrul ar putea
    contine dicționare libere si regula «fara variante nu e interpretare» ar fi ocolita."""
    assert INTERPRETARI, "registrul de interpretari e gol - garda de mai sus n-ar avea ce verifica"
    for cheie, i in INTERPRETARI.items():
        assert isinstance(i, Interpretare), "intrarea %r nu e o `Interpretare`" % cheie
        assert i.cheie == cheie, "cheia din registru difera de cheia obiectului: %r vs %r" % (cheie, i.cheie)
        assert len(i.variante) >= 2
