# -*- coding: utf-8 -*-
"""core/test_g9_oblig_backend.py — GARD care ÎNCHIDE CLASA (nu doar instanțele): un câmp marcat
obligatoriu în UI trebuie să aibă corespondent backend, și invers. (C-5 G9.)

Corespondența complet-enumerabilă e ecranul date_firma: setul `ob: true` (câmpuri firma_profil) ==
`firma_profil_api.OBLIGATORII` EXACT. Orice drift — .oblig UI fără backend SAU backend cere fără .oblig —
PICĂ. (Cross-ecran general = neenumerabil static, vezi P7; aici se închide clasa pe ecranul enumerabil +
se pin-uiesc deciziile G9.)
"""
import io
import re


def _read(p):
    return io.open(p, encoding="utf-8").read()


def test_date_firma_oblig_egal_backend_obligatorii():
    from core.firma_profil_api import OBLIGATORII
    src = _read("static/js/ecrane/date_firma.js")
    ui_ob = set(re.findall(r'k:\s*"(\w+)"[^\n]*\bob:\s*true', src))
    # regim_fiscal/platitor_tva = camp de VECTOR (vector_fiscal_api), nu firma_profil -> excluse din comparatie
    firma_profil_ui = ui_ob - {"regim_fiscal", "platitor_tva"}
    assert firma_profil_ui == set(OBLIGATORII), (
        "Drift .oblig<->backend pe date_firma: UI(firma_profil)=%s vs OBLIGATORII=%s"
        % (sorted(firma_profil_ui), sorted(OBLIGATORII)))


def test_g9_decizii_backend_enforce():
    """G9: cele 3 cazuri unde asteriscul RAMANE -> backend-ul enforce (nu mai minte)."""
    assert "Data de sfarsit a concediului medical e obligatorie" in _read("core/salariati_api.py"), "cm-sfarsit"
    assert 'b{i}-valoare_fara_tva' in _read("core/etransport.py"), "etransport valoare_fara_tva"
    assert "Denumirea beneficiarului e obligatorie" in _read("main.py"), "em-nume"


def test_g9_decizii_asterisc_dispare():
    """G9: cele 2 cazuri unde asteriscul FALS a fost scos (backend nu cere)."""
    assert '<span class="camp-eticheta">CUI<span class="oblig">' not in _read("static/js/ecrane/login.js"), "reg-cui"
    assert '"salariu_brut", "Salariu brut", "numar", { obligatoriu: true }' not in _read("static/js/ecrane/firme.js"), "sn-salariu_brut"
