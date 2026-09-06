# -*- coding: utf-8 -*-
"""GARD (06.09.2026) — arborele de navigare al asistentului si cardurile lui nu pot diverge.

CERINTA lui Costin: *„Fiecare nod duce la același loc unde duce cardul corespunzător azi."* Asta e o
afirmatie despre COMPORTAMENT, si nu se poate proba citind sursa: `"randeazaControl" in text` e
adevarat si intr-o lume in care nodul nu cheama nimic. Se probeaza in browser, apasand — o face
`frontend_test/proba_r175_arbore_asistent.py`, care deschide fereastra din nod, ii citeste firul, o
inchide, apasa cardul si citeste iar. Doua drumuri, acelasi capat, pe toate cele noua.

CE FACE GARDA ASTA: tine proba VIE. Fara cuplare, un artefact comis o data devine o amintire —
exact clasa scrisa in METODA (*„o cifra care nu se poate recalcula nu e o masuratoare"*). Aici
artefactul poarta `ui_hash`, aceeasi amprenta pe care o foloseste `test_acoperire_vizuala`: daca
`asistent.js` sau `stil.css` se schimba dupa proba, garda PICA si cere reprobarea. Nu „e veche" —
e INVALIDA.

ANTI-VACUU: daca artefactul ar fi gol, ar trece orice. De-aia se cere si continutul — noua noduri,
trei grupe, perechi cate noduri.

DE CE NU E IN `nav_ecrane.ECRANE`. Cele trei unelte vizuale plimba un SINGUR cont peste lista de
ecrane; desktopul asistentului cere alt ROL, iar `app.js` alege desktopul din `sesiune.rol()` la
pornirea filei — deci al doilea cont inseamna al doilea CONTEXT de browser, nu un ecran in plus.
"""
import json
import os
import sys

import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_RAD, "frontend_test", "vizual"))
from acoperire_hash import ui_hash  # noqa: E402

ARTEFACT = os.path.join(_RAD, "frontend_test", "proba_r175_arbore_asistent.json")
NODURI_ASTEPTATE = ["firme", "control", "termene", "declaratii", "validat", "pachete",
                    "raport", "recomanda", "setari"]
GRUPE_ASTEPTATE = ["Firmele mele", "Lucrarea lunii", "Contul meu"]


def _proba():
    if not os.path.exists(ARTEFACT):
        pytest.fail("proba arborelui lipseste — ruleaza "
                    "frontend_test/proba_r175_arbore_asistent.py")
    return json.load(open(ARTEFACT, encoding="utf-8"))


def test_proba_e_proaspata():
    """UI-ul nu s-a schimbat de la ultima probare a arborelui."""
    assert _proba().get("ui_hash") == ui_hash(), (
        "asistent.js / stil.css s-au schimbat de la ultima probare a arborelui — ruleaza "
        "frontend_test/proba_r175_arbore_asistent.py si comite artefactul")


def test_arborele_si_cardurile_au_aceeasi_ordine():
    """Ordinea citita din ARBORELE DE RANDARE, nu din sursa: secventa `data-nod` din panou fata de
    secventa `data-cheie` din grila. Amandoua se randeaza din aceeasi lista; daca s-ar despica,
    egalitatea cade."""
    p = _proba()
    assert p["noduri"] == p["carduri"]
    assert p["noduri"] == NODURI_ASTEPTATE
    assert p["ordine_identica"] is True


def test_grupele_sunt_cele_derivate_din_carduri():
    """Trei grupe, in ordinea fluxului: ce e zilnic, ce e lunar, ce e administrativ."""
    assert _proba()["grupe"] == GRUPE_ASTEPTATE


def test_fiecare_nod_duce_unde_duce_cardul():
    """Cerinta, verbatim. Perechile sunt masurate APASAND, nu citind."""
    p = _proba()
    perechi = p["perechi"]
    assert len(perechi) == len(NODURI_ASTEPTATE)          # anti-vacuu: nu o lista goala
    assert [x["cheie"] for x in perechi] == NODURI_ASTEPTATE
    rele = [x for x in perechi if not x["la_fel"]]
    assert not rele, "noduri care nu duc unde duce cardul: %s" % rele


def test_ecranul_e_curat_la_privire():
    """F6 pe ecranul ATINS: axe (desktop), title-only, si mobilul — arborele NU dispare pe telefon,
    fiindca e navigare, iar o navigare ascunsa muta functionalitati in nicaieri."""
    p = _proba()
    assert p["axe"]["violari"] == []
    to = p["axe"]["title_only"]
    assert sum(len(v) for v in to.values()) == 0, to
    m = p["mobil"]
    assert m["arbore_vizibil"] is True
    assert m["noduri"] == len(NODURI_ASTEPTATE)
    assert m["revarsare_x"] is False
    assert m["tinte_sub_24"] == 0
