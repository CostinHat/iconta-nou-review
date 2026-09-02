# -*- coding: utf-8 -*-
"""GARD (R19): o funcție partajată între clustere NU e proprietatea niciunuia.

CE FACE IMPOSIBIL: ca `graf_clustere` să declare dependență acolo unde e doar co-locație. Filtrul
vechi era `if f in own: continue` — excludea partajarea **cu sine**, nu partajarea **între alții**.
Un utilitar chemat de testele a cinci clustere era „deținut" de toate cinci, iar orice al șaselea
cluster care îl atingea tranzitiv căpăta cinci muchii de dependență. Măsurat 23.08.2026: **70 din
154** de funcții deținute erau deținute de 2+ clustere, iar **960 din muchii** se sprijineau pe ele.

CE NU FACE, declarat: nu verifică dacă muchiile rămase sunt *corecte* — verifică doar că niciuna nu
se sprijină pe o funcție fără proprietar unic. O dependență reală pe care graful n-o vede (literal
ascuns, apel dinamic) rămâne invizibilă — e limita declarată în docstringul lui `graf_clustere`.
"""
import pytest

from core import agenda

# CLICHET: muchiile de la regula nouă, măsurate pe 23.08.2026 (erau 960 cu regula veche).
# Nu poate CREȘTE fără decizie: o creștere înseamnă ori dependențe noi reale, ori regula slăbită.
#
# 111 -> 112 pe 02.09.2026, RIDICAT CONȘTIENT, cu motivul scris: o dependență REALĂ nouă, nu o
# slăbire a regulii. `core/d101.py` cheamă acum `core.pdf_util.bani` — formatorul CANONIC de sume —
# pentru avertismentul „cheltuiala cu impozitul pe profit rămasă nededusă la rd.23" (R124). Muchia e
# chiar ce cere DESIGN_SYSTEM cap.7: o sumă afișată contabilului trece printr-un singur formator, nu
# prin `%d lei` scris local. *Alternativa — să nu existe muchia — ar fi însemnat o a doua formatare
# de bani în cod, adică exact ce numără verificatorul ca BACKEND_UI_BRUT.*
BASELINE_MUCHII = 112


# ────────────────────────────────────────────── calibrarea regulii, pe caz sintetic
def test_functia_partajata_pierde_proprietarul_iar_cea_proprie_il_pastreaza():
    """Calibrare în ambele direcții, pe un caz construit: `u` e chemată de testele a două clustere
    (co-locație) → fără proprietar; `f1`/`f2` rămân ale lor."""
    cf = {"A": {"m.py::f1", "u.py::u"}, "B": {"m.py::f2", "u.py::u"}}
    own = agenda.proprietari_unici(cf)
    assert set(own) == {"m.py::f1", "m.py::f2"}, own
    assert own["m.py::f1"] == {"A"} and own["m.py::f2"] == {"B"}
    assert "u.py::u" not in own, "funcția partajată a rămas proprietate — R19 s-a întors"


def test_o_functie_partajata_nu_primeste_ALT_proprietar():
    """Regula nu mută proprietatea, o ridică: partajata nu primește niciun proprietar."""
    cf = {"A": {"u.py::u"}, "B": {"u.py::u"}, "C": {"u.py::u"}}
    assert agenda.proprietari_unici(cf) == {}


def test_toate_intrarile_au_exact_un_proprietar():
    cf = {"A": {"m.py::f1", "u.py::u"}, "B": {"m.py::f2", "u.py::u"}, "C": {"m.py::f3"}}
    assert all(len(v) == 1 for v in agenda.proprietari_unici(cf).values())


# ────────────────────────────────────────────── pe inventarul REAL
@pytest.fixture(scope="module")
def real():
    from core import graf_temei as _gt
    graf = _gt.construieste_graf()
    rows = agenda.stare_sesiune_a()["rows"]
    cf = agenda.functii_per_cluster(graf, rows)
    toti = {}
    for cl, fns in cf.items():
        for f in fns:
            toti.setdefault(f, set()).add(cl)
    return {"cf": cf, "toti": toti, "unici": agenda.proprietari_unici(cf)}


def test_ANTIVACUU_chiar_exista_functii_partajate_de_exclus(real):
    """Fără funcții partajate în inventarul real, gardul de mai jos ar trece pe zero rânduri și ar
    raporta verde despre o lume pe care n-o vede."""
    partajate = [f for f, v in real["toti"].items() if len(v) > 1]
    assert len(partajate) >= 10, ("doar %d funcții partajate — ori inventarul s-a golit, ori "
                                  "detectorul a orbit" % len(partajate))
    assert real["unici"], "nicio funcție cu proprietar unic — graful ar fi gol prin construcție"


def test_nicio_functie_cu_proprietar_multiplu_nu_supravietuieste(real):
    rele = [f for f, v in real["unici"].items() if len(real["toti"][f]) > 1]
    assert not rele, "funcții partajate rămase proprietate: %r" % rele[:5]


def test_muchiile_nu_cresc_peste_clichet_si_graful_nu_e_gol():
    """Clichet în ambele direcții: nu crește tăcut (regula slăbită), și nu ajunge la zero (graful ar
    deveni vid, iar o secvență topologică pe zero muchii nu ordonează nimic — vezi R18)."""
    e = agenda.graf_clustere()
    n = sum(len(v) for v in e.values())
    assert 0 < n <= BASELINE_MUCHII, (
        "muchii=%d, clichet=%d. Peste clichet: regula proprietății s-a slăbit sau au apărut "
        "dependențe reale noi (coboară/ridică BASELINE_MUCHII conștient). Zero: graful e vid."
        % (n, BASELINE_MUCHII))
