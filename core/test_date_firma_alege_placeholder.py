# -*- coding: utf-8 -*-
"""core/test_date_firma_alege_placeholder.py — GARD (jumatatea frontend a defectului „default fabricat"
pe selecturile vectorului din ecranul Date firma; pereche cu core/test_vector_platitor_tva_oblig.py).

DEFECT (audit vizual tenant_001, 17.08.2026): selecturile obligatorii regim_fiscal / platitor_tva /
operatiuni_ic NU aveau optiune-placeholder. La valoare NULL browserul afisa PRIMA optiune reala
(„Microintreprindere" / „Nu") ca aleasa, iar salvarea trimitea `value === "da"` -> false tacit. Backendul
nu poate distinge un „Nu" ales de un „Nu" fabricat -> se persista o alegere pe care contabilul n-a facut-o
(Regula 4). Fix in static/js/ecrane/date_firma.js: `alege:true` + placeholder „— alege —" + tri-stare
(null cand neales) + validare preventiva langa camp.

TEMEI: Regula 4 (fara valori implicite fabricate) + DS cap.6 (validari preventive cu mesaj langa camp) +
DECIZII 23.07 („frontendul distinge 'nesetat' de 'Nu', fara preselectie").

Sursa-scan (ca celelalte garzi de ecran): pin-uieste invariantele care, daca dispar, readuc defectul.
"""
import io
import re

_F = "static/js/ecrane/date_firma.js"


def _src():
    return io.open(_F, encoding="utf-8").read()


def test_selecturi_vector_obligatorii_au_alege():
    """regim_fiscal / platitor_tva / operatiuni_ic sunt marcate alege:true (placeholder + validare)."""
    src = _src()
    for k in ("regim_fiscal", "platitor_tva", "operatiuni_ic"):
        # blocul definitiei campului: { k: "<k>", ... alege: true ... }
        m = re.search(r'\{\s*k:\s*"' + k + r'"[^}]*\balege:\s*true', src)
        assert m, "selectul '%s' trebuie marcat alege:true (placeholder + cerere alegere explicita)" % k


def test_placeholder_randat_la_valoare_lipsa():
    """campVector pune optiunea placeholder cand alege && valoare lipsa (altfel browserul arata prima optiune)."""
    src = _src()
    assert re.search(r'c\.alege\s*&&\s*!v', src), "campVector trebuie sa detecteze alege && valoare lipsa"
    assert 'selected disabled hidden' in src, "placeholderul trebuie afisat (selected) dar neselectabil (disabled hidden)"


def test_salvare_tri_stare_nu_coerce_fals_tacit():
    """La salvare, platitor_tva/operatiuni_ic NU se citesc cu `=== \"da\"` (pierde null -> false fabricat);
    se foloseste tri-stare care trimite null cand neales."""
    src = _src()
    # nu mai exista coercia veche care transforma placeholder-ul in false
    assert 'querySelector("#vf-platitor_tva").value === "da"' not in src, \
        "platitor_tva nu trebuie coerce cu === 'da' (null -> false fabricat); foloseste tri-stare"
    assert 'querySelector("#vf-operatiuni_ic").value === "da"' not in src, \
        "operatiuni_ic nu trebuie coerce cu === 'da' (null -> false fabricat); foloseste tri-stare"
    # tri-stare prezenta: "" -> null
    assert "triBool" in src, "trebuie folosita o functie tri-stare (da/nu/null) pentru selecturile vectorului"


def test_regim_nu_se_cere_la_partida_simpla():
    """PFA/II/PFL (partida simpla) n-are micro/profit -> regimul nu se pretinde acolo (fapt din payload)."""
    src = _src()
    assert "partida_simpla" in src, "cerinta regimului trebuie sa tina cont de partida_simpla (nu forta regim la PFA)"
