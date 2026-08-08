# -*- coding: utf-8 -*-
"""GARD G10 (DESIGN_SYSTEM cap.6 v2.30) — rollout mecanism A (eroare LANGA campul care a cauzat-o, via
`eroareCamp`) pe formularele multi-camp. Lista se EXTINDE la fiecare batch. Verifica dupa fiecare batch ca
gardul vede noile formulare. e-Transport = batch 3 (restructurare randuri dinamice), EXPLICIT in afara listei."""
import os

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Formularele multi-camp migrate la mecanismul A (eroareCamp). Se adauga cate un batch:
#   pilot: flux_concediu (validat 5/5)
#   batch 1: date_firma (date fiscale ANAF), firme.js (salariat nou, id-uri sn-*)
#   batch 2 (viitor): emitere + al 5-lea
_G10_A_FORME = [
    "flux_concediu.js",
    "date_firma.js",
    "firme.js",
    "declaratii.js",  # batch 2: D301-manual (#d301-*) + D390-manual (#man-*)
]

# EXPLICIT in afara listei pana la batch 3 (restructurare, nu plasare): randuri dinamice, campuriLipsaCorp
# intoarce etichete, nu id-uri. Ramane pe B (mesaj colectat vizibil - "niciodata tacere"). Vezi GARZI.
_G10_A_EXCLUSE = ["etransport_ecran.js"]


def test_formularele_G10A_folosesc_eroareCamp():
    for fisier in _G10_A_FORME:
        src = open(os.path.join(_RAD, "static/js/ecrane", fisier), encoding="utf-8").read()
        assert "eroareCamp" in src, "%s: nu importa eroareCamp (mecanism A - eroare langa camp)" % fisier
        assert "eroareCamp(" in src, "%s: importa eroareCamp dar nu-l cheama" % fisier


def test_backend_contract_erori_campuri_wired():
    """[G10 rule2/4] api.js poarta erori_campuri din raspuns; ruta salariat trimite {mesaj, erori_campuri}."""
    apijs = open(os.path.join(_RAD, "static/js/api.js"), encoding="utf-8").read()
    assert "_erisCampuri" in apijs and "erori_campuri: _erisCampuri" in apijs, \
        "api.js nu mai poarta erori_campuri din raspuns (contract G10 rule2/4)"
    main = open(os.path.join(_RAD, "main.py"), encoding="utf-8").read()
    assert 'detail={"mesaj": str(e), "erori_campuri"' in main, \
        "ruta salariat nu mai trimite erori_campuri (contract G10)"


def test_etransport_ramane_in_afara_pana_la_batch3():
    """e-Transport NU intra in lista G10-A pana la batch 3 (restructurare). Daca cineva il muta acum -> pica,
    ca sa nu se amestece restructurarea cu rollout-ul de plasare."""
    for f in _G10_A_EXCLUSE:
        assert f not in _G10_A_FORME, "%s trebuie tratat separat (batch 3), nu in rollout-ul standard" % f
