# -*- coding: utf-8 -*-
"""Lotul 12 — pachetul d112b: în D112, „Baza de calcul al indemnizaţiei de şomaj” (B1_10 / B4_3) = baza CAM a salariatului (B1_5), iar
„Venitul brut … realizat” (B1_sal2) = „Total venit brut” (E3_8) — în luna cu concediu medical fără salariul zilelor de concediu, la
tipul 1.11.2 fără suma netaxabilă de 200 de lei în baza de șomaj. Pașii contabilului pe aplicația din index, pe baza de TEST: statul
lunii trecute (ecranul Salariați) -> „Concediu” -> certificatul pe ecranul „Concediu medical” -> Declarații -> D112 -> DUKIntegrator ->
„Vezi XML-ul generat”.

Temeiul (citat integral în `core/test_lot12_d112b_somaj_brut_cm.py`): OPANAF 605/2026 anexa 2, B.1 rândul 11 și B.4 rândul 8; Legea
76/2002 art.39 alin.(2^1); HG 174/2002 (normele) art.19^1 alin.(1) — baza indemnizației de șomaj = baza de calcul a CAM; Legea 53/2003
art.49 alin.(2) + art.50 lit.b); structura D112 câmpul 14b „A_sal2=E3_8-E3_69”.

Numele testelor poartă `d112b` până primesc numărul C din DEFICIENTE.md (sesiunea principală le redenumește, împreună cu mut json-ul).
Date de pornire: firmă sintetică + salariat pe ruta salariaților (`e2e_lot11_s9._firma_cu_salariat`), certificatul pe ecran
(`e2e_lot12_ctrl_d112._certificat_01`)."""
import pytest

from conftest import _scoate_firmele_e2e
from e2e_bloc_d import LUNA_TRECUTA
from e2e_lot11_s9 import _d112_xml, _firma_cu_salariat, _singurul, _un
from e2e_lot12_ctrl_d112 import _certificat_01


@pytest.fixture
def firma_d112b_cm():
    f = _firma_cu_salariat("L12S", salariu_brut=6000)
    try:
        yield f
    finally:
        _scoate_firmele_e2e(f["tenant_id"])


def test_def_c173_baza_somaj_si_venitul_realizat_in_luna_cu_cm(patron, firma_d112b_cm):
    """Pașii: salariat cu 6.000 lei -> statul lunii trecute -> „Concediu” -> „+ Certificat nou”: cod 01, INIȚIAL, 1–9 ale lunii trecute ->
    „Calculează și salvează” -> Declarații -> D112: „fără erori”; în XML, baza de șomaj B1_10 = B4_3 = baza CAM B1_5 = salariul realizat
    (B2_5) + indemnizația angajatorului (Σ D_20), iar B1_sal2 = E3_8, sub 6.000. Înainte: B1_10 = B4_3 = B1_sal2 = 6.000 (salariul întreg,
    cu zilele de concediu)."""
    _certificat_01(patron, firma_d112b_cm, 9, "1121")
    a = _singurul(_d112_xml(patron, firma_d112b_cm))   # _d112_xml cere „fără erori” la DUKIntegrator și lasă captura XML-ului
    b1, b2, b4, e3 = _un(a, "asiguratB1"), _un(a, "asiguratB2"), _un(a, "asiguratB4"), _un(a, "asiguratE3")
    d20 = sum(int(x["D_20"]) for x in a.get("asiguratD", []))
    assert d20 > 0 and int(b2["B2_5"]) < 6000, (a.get("asiguratD"), b2)
    # HG 174/2002 norme art.19^1 alin.(1): baza indemnizației de șomaj = baza de calcul a CAM; structura „B4_3=ΣB1_10”
    assert int(b1["B1_10"]) == int(b4["B4_3"]) == int(b1["B1_5"]) == int(b2["B2_5"]) + d20, (b1, b2, b4, d20)
    # Legea 53/2003 art.49 alin.(2): pe zilele de concediu nu se plătește salariu; structura 14b „A_sal2=E3_8-E3_69”
    assert int(b1["B1_sal2"]) == int(e3["E3_8"]) < 6000, (b1, e3)


@pytest.fixture
def firma_d112b_minim():
    from core.common import salariu_minim_luna
    f = _firma_cu_salariat("L12M", salariu_brut=int(salariu_minim_luna(LUNA_TRECUTA)[0]))
    try:
        yield f
    finally:
        _scoate_firmele_e2e(f["tenant_id"])


def test_def_c173_tipul_1_11_2_fara_suma_netaxabila_in_baza_somaj(patron, firma_d112b_minim):
    """Pașii: salariat cu salariul minim al lunii trecute, normă întreagă -> Declarații -> D112: „fără erori”; tipul de asigurat 1.11.2
    (B1_1 = 51) și baza de șomaj B1_10 = B4_3 = B1_5 = salariul minim − suma netaxabilă (B2_5S), iar B1_sal2 = E3_8 = salariul minim.
    Înainte: B1_10 = B4_3 = salariul minim (cu suma netaxabilă). Temeiul: OPANAF 605/2026 anexa 2, B.1 rândul 11 — „în baza de calcul al
    indemnizaţiei de şomaj, nu este inclusă suma de 200 lei”."""
    from core.common import salariu_minim_luna
    sm = int(salariu_minim_luna(LUNA_TRECUTA)[0])
    a = _singurul(_d112_xml(patron, firma_d112b_minim))
    b1, b2, b4, e3 = _un(a, "asiguratB1"), _un(a, "asiguratB2"), _un(a, "asiguratB4"), _un(a, "asiguratE3")
    assert b1["B1_1"] == "51" and int(b2["B2_5S"]) > 0, (b1, b2)
    assert int(b1["B1_10"]) == int(b4["B4_3"]) == int(b1["B1_5"]) == sm - int(b2["B2_5S"]), (b1, b2, b4, sm)
    assert int(b1["B1_sal2"]) == int(e3["E3_8"]) == sm, (b1, e3, sm)
