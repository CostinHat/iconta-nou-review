# -*- coding: utf-8 -*-
"""GARD A2: DUK distinge atentionare (A:, NU blocheaza depunerea) de eroare (E:, blocheaza). Fixturi REALE
capturate live prin serviciu (08.08.2026) pe /declaratii/{tip}/valideaza. Mutatie: inversarea clasificarii
sau retrogradarea unui E: la atentionare -> rosu."""
import os, sys
_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _RAD not in sys.path:
    sys.path.insert(0, _RAD)
from core import duk

# REALE (live): Panificatie d112/aug = atentionare; Ferma Agricultor d112/aug = eroare
ATENTIONARE = "A: asigurat (4) [idAsig = 4] sectiune asiguratB4 (1)\n atentionare regula: SP1B4_1: B4_5P(4325) diferit de suma calculata 3750"
EROARE = "E: angajator (1)\n eroare regula: ACreante: sectiunea Creante este obligatorie pt cif <> cif AJPIS"


def test_atentionare_nu_e_eroare():
    assert duk.severitate(ATENTIONARE) == "atentionare", "A: (atentionare) nu trebuie tratat ca eroare"


def test_eroare_reala_ramane_eroare():
    assert duk.severitate(EROARE) == "eroare", "E: (eroare) trebuie sa ramana eroare"


def test_mixt_A_si_E_ramane_eroare():
    # daca exista MACAR o linie E:, e eroare (nu retrograda din cauza unei atentionari alaturate)
    assert duk.severitate(EROARE + "\n" + ATENTIONARE) == "eroare"
    assert duk.severitate(ATENTIONARE + "\n" + EROARE) == "eroare"


def test_necunoscut_e_eroare_failsafe():
    # output prezent, format nerecunoscut -> eroare (fail-safe: niciodata fals-verde)
    assert duk.severitate("ceva iesire fara prefix A: sau E:") == "eroare"


def test_gol_e_none():
    assert duk.severitate("") is None
    assert duk.severitate("   \n  ") is None
    assert duk.severitate(None) is None


def test_valideaza_expune_severitate_in_contract():
    # orice rezultat al valideaza contine cheia 'severitate' (frontendul se bazeaza pe ea)
    r = duk.valideaza("<x/>", "d112")   # DUK poate fi gri in mediu de test -> severitate None, dar cheia exista
    assert "severitate" in r, "contractul valideaza trebuie sa expuna 'severitate'"


def test_ruta_valideaza_forwardeaza_severitate():
    """Regresie END-TO-END: ruta POST /declaratii/{tip}/valideaza (main.py) trebuie sa FORWARDEZE 'severitate'
    din duk.valideaza catre raspuns - altfel declaratii.js nu-l primeste si A2 n-are efect in UI (fixul unitar
    trece dar integrarea nu). Exact gapul scapat prima data (severitate=None live desi unit-testul era verde)."""
    import ast
    src = open(os.path.join(_RAD, "main.py"), encoding="utf-8").read()
    tree = ast.parse(src)
    fn = next((n for n in ast.walk(tree)
               if isinstance(n, ast.FunctionDef) and n.name == "declaratie_valideaza"), None)
    assert fn is not None, "ruta declaratie_valideaza nu a fost gasita in main.py"
    body = ast.get_source_segment(src, fn)
    assert "severitate" in body, ("ruta declaratie_valideaza NU forwardeaza 'severitate' -> frontendul primeste "
                                  "undefined si atentionarile apar tot ca 'erori' (A2 fara efect)")
