# -*- coding: utf-8 -*-
"""core/test_sonde_stare.py — clichetul interdicției 78: o sondă care nu poate spune dacă a reușit.

**Ce păzește.** `scripts/scan_sonde_stare.py` numără locurile în care o sondă de măsurare întoarce
și starea răspunsului, iar apelantul o aruncă. Clichetul e **0**: clasa e goală azi, și n-are voie
să crească.

**De ce nu e un test vacuu, deși cifra e 0.** Trei lucruri, fiecare cu proba lui:
  1. calibrarea rulează **în suită**, în ambele direcții — zece probe, cinci pozitive și cinci
     negative, pe corpus sintetic;
  2. instrumentul trebuie să **vadă** populația: dacă n-ar găsi nicio pereche sondă↔apelant, cifra
     0 ar fi despre o lume pe care n-o vede, nu despre casă;
  3. clasa vecină, **NEJUDECATA**, e pinată separat — nu plafonată, dar pinată: dacă apare una
     nouă, se vede, fiindcă altfel un defect adevărat s-ar putea ascunde acolo.

*Cifra 0 fără (1) și (2) ar fi exact felul de verde despre care interdicția 76 vorbește.*
"""
import os
import sys

import pytest

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAD not in sys.path:
    sys.path.insert(0, RAD)
sys.path.insert(0, os.path.join(RAD, "scripts"))

import scan_sonde_stare as S  # noqa: E402

#: clichet. Măsurat pe 10.09.2026, pe commitul valului 1, cu cenzus COMPLET (populația e 6, sub 30).
CLICHET_PIERDUTA = 0

#: clasa vecină: starea supraviețuiește în artefact, dar nimeni n-o judecă. Se PINEAZĂ, nu se
#: plafonează — a plafona-o ar cere o judecată pe care instrumentul n-o poate face.
NEJUDECATA_PINATA = {
    ("scripts/masoara_p3.py", "curba"),
    ("scripts/masoara_p3.py", "masoara_pe_real"),
    ("scripts/masoara_rute_portofoliu.py", "curba"),
}


@pytest.fixture(scope="module")
def rezultat():
    return S.scaneaza()


def test_calibrarea_e_verde_in_ambele_directii():
    """Cinci cazuri care TREBUIE găsite, cinci care NU trebuie. Fără asta, cifra n-ar valora nimic."""
    probe = S.probe_calibrare()
    assert len(probe) >= 10, "prea puține probe de calibrare: %d" % len(probe)
    picate = [n for n, ok in probe if not ok]
    assert not picate, "calibrare picată:\n  " + "\n  ".join(picate)


def test_instrumentul_chiar_vede_populatia(rezultat):
    """ANTI-VACUU: o cifră 0 pe o populație goală e o afirmație despre nimic."""
    assert len(S.fisiere()) >= 5, "domeniul s-a golit: %d fișiere" % len(S.fisiere())
    assert len(rezultat) >= 5, (
        "instrumentul n-a găsit decât %d perechi sondă↔apelant — ori sondele au dispărut, ori "
        "el a orbit. Clichetul de mai jos n-ar spune nimic despre casă." % len(rezultat))


def test_nicio_sonda_nu_arunca_starea(rezultat):
    """Clichetul propriu-zis: `PIERDUTA` rămâne la %d.""" % CLICHET_PIERDUTA
    pierdute = [(f, a, s) for f, a, s, _p, cls, _g in rezultat if cls == "PIERDUTA"]
    assert len(pierdute) == CLICHET_PIERDUTA, (
        "sonde care aruncă starea răspunsului: %s\n"
        "O durată există și pe 500 — o măsurătoare care nu-și poate numi ramura nu e o măsurătoare."
        % pierdute)


def test_clasa_vecina_e_pinata(rezultat):
    """`NEJUDECATA` se numără, nu se plafonează — dar se pinează, ca să nu ascundă ceva nou."""
    vazute = {(f, a) for f, a, _s, _p, cls, _g in rezultat if cls == "NEJUDECATA"}
    assert vazute == NEJUDECATA_PINATA, (
        "mulțimea celor care poartă starea fără s-o judece s-a mutat:\n"
        "  apărut: %s\n  dispărut: %s"
        % (sorted(vazute - NEJUDECATA_PINATA), sorted(NEJUDECATA_PINATA - vazute)))


def test_bancul_p5_isi_judeca_starea(rezultat):
    """Instanța care a produs clasa, pinată pe nume: cele două curbe ale bancului P5 DUC starea.

    *O interdicție al cărei caz de origine nu e pinat poate reveni exact acolo de unde a plecat.*
    """
    duc = {(f, a) for f, a, _s, _p, cls, _g in rezultat if cls == "DUCE"}
    for a in ("curba_async", "curba_sync"):
        assert ("scripts/masoara_p5.py", a) in duc, (
            "%s nu mai duce starea — a recăzut chiar în defectul care a deschis interdicția" % a)
