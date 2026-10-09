# -*- coding: utf-8 -*-
"""GARD — textul AFIȘAT pe ecrane e limba contabilului: scanul din browser e proaspăt și curat.

Comanda Costin 09.10.2026 („Retest 2” pct.2, verbatim în DECIZII): „Pct.14 nu e închis. […] Decizie: verificarea se face pe ecranul
afișat, cu valorile din date și din enumerări, nu pe șirurile din codul sursă.” Artefactul `frontend_test/vizual/text_ecran.json`
îl scrie `frontend_test/vizual/text_ecran_scan.py --artefact` (browser, firmele de test, toate cardurile lor, desktopul cabinetului
și declarațiile generate), cu judecata din `core/limba_ecran.py`. Ca `acoperire_vizuala.json`: rulează în afara suitei (cere app
viu + browser), iar suita cere ca el să fie al UI-ului de acum și al instrumentului de acum, și curat.

LIMITĂ declarată: textul trimis de server se schimbă și fără să se schimbe UI-ul (un mesaj din `core/`); pe partea aceea prima plasă
rămâne gardul de sursă (`core/test_text_afisat_limbaj.py`), iar scanul se reface la fiecare lot care atinge ecrane (CLAUDE.md §2.3
pct.11). Ecranele scanate sunt ale firmelor de test — un ecran pe care datele de test nu-l umplu nu-și arată toate textele.
"""
import json
import os
import sys

import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_RAD, "frontend_test", "vizual"))
from acoperire_hash import ui_hash  # noqa: E402
from core.limba_ecran import instrument_hash  # noqa: E402

ARTEFACT = os.path.join(_RAD, "frontend_test", "vizual", "text_ecran.json")


@pytest.fixture(scope="module")
def art():
    if not os.path.exists(ARTEFACT):
        pytest.fail("text_ecran.json lipsește — rulează frontend_test/vizual/text_ecran_scan.py <dir> --artefact")
    return json.load(open(ARTEFACT, encoding="utf-8"))


def test_scanul_e_al_ui_ului_de_acum(art):
    assert art.get("ui_hash") == ui_hash(), "UI-ul s-a schimbat de la ultimul scan al textului — rulează text_ecran_scan.py --artefact"


def test_scanul_e_al_instrumentului_de_acum(art):
    assert art.get("instrument_hash") == instrument_hash(), (
        "detectorul sau lexiconul s-au schimbat de la ultimul scan — rulează text_ecran_scan.py --artefact")


def test_ecranele_sunt_curate(art):
    assert art.get("total_defecte") == 0, "text greșit pe ecran:\n  " + "\n  ".join(
        "%s: [%s] %r <- %r" % (k, d["fel"], d["fragment"], d["rand"][:100]) for k, v in (art.get("defecte") or {}).items() for d in v)
    assert not art.get("erori_navigare"), "ecrane neatinse de scan: %s" % art.get("erori_navigare")


def test_scanul_acopera_ce_a_cerut_comanda(art):
    """Ecranele numite în comandă: Casă, Mijloace fixe, Registru jurnal, Control fiscal, Date firmă, D394, D406, planul de conturi."""
    ecrane = set(art.get("ecrane") or [])
    assert len(ecrane) >= 150, "doar %d ecrane scanate" % len(ecrane)
    for fid in ("fa-casa", "fa-mijloace", "fa-jurnal", "fa-control", "fa-datefirma", "fa-planconturi", "declaratie_d394",
                "declaratie_d406"):
        assert [e for e in ecrane if e.endswith("/" + fid)], fid
