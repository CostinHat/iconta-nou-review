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
    "etransport_ecran.js",  # batch 3a: randuri dinamice, backend autoritar (422.campuri) + eroareCamp (cap.24)
    "emitere_ecran.js",  # batch 3b: randuri dinamice, backend autoritar (facturi_api.linii_campuri_lipsa) + eroareCamp
]

# Dupa batch 3b (emitere), G10 NU mai are exceptii: TOATE formularele multi-camp folosesc mecanismul A.
# e-Transport a intrat la 3a, emitere la 3b. O exceptie noua cere un batch dedicat (vezi GARZI / cap.24).
_G10_A_EXCLUSE = []


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


def test_g10_fara_exceptii_dupa_batch3b():
    """Dupa batch 3b (emitere), rollout-ul G10-A NU mai are exceptii: toate formularele multi-camp folosesc
    mecanismul A (eroare langa camp). O exceptie noua fara batch dedicat -> pica aici."""
    assert _G10_A_EXCLUSE == [], "G10 nu mai are exceptii dupa 3b; o exceptie noua cere batch dedicat"
