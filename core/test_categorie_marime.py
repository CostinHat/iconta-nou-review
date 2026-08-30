# -*- coding: utf-8 -*-
"""GARD — categoria de mărime nu se rotunjește la „micro", și pragurile citează actul.

DE CE EXISTĂ (30.08.2026, R3, lista 3). `POST /tenants/{id}/s1005-valideaza` și perechea `s1003`
produceau situații financiare **fără să poată ști dacă e cea datorată**: regimul se alegea dintr-un
`<select>`. Cerința lui Costin, 26.08.2026: *„dacă aceasta nu există ca dimensiune, ruta nu poate ști
ce datorează firma — se declară, nu se presupune."*

CE FACE IMPOSIBIL, și fiecare punct e un mod de eșec al unei implementări naive:

  1. **Ca încadrarea să se facă pe UN singur exercițiu.** pct. 13 alin. (2)-(3): categoria se
     schimbă *doar dacă în două exerciții consecutive* se depășesc criteriile. O derivare pe anul
     curent nu e încadrarea cerută de normă — e indicatorul anului ăluia.
  2. **Ca lipsa datelor să se rotunjească la «micro».** Fără exercițiul precedent, răspunsul e
     `nedeterminata`, cu motiv. *Micro e cea mai mică — deci exact valoarea spre care alunecă o
     implementare care tratează necunoscutul ca zero* (interdicția 32).
  3. **Ca pragul să se decidă pe UN criteriu.** pct. 9: *„nu depășesc limitele a cel puțin două
     dintre următoarele trei criterii"*.
  4. **Ca pragurile să fie literale nesursate.** Fiecare poartă `Temei` cu actul, alineatul, data
     intrării în vigoare și lanțul de acte modificatoare.

CALIBRARE ÎN AMÂNDOUĂ DIRECȚIILE (METODA §22): o firmă clar micro trebuie să iasă `micro`, una clar
mare trebuie să iasă `mijlocii_mari` — altfel „nedeterminata" ar fi un răspuns care trece la orice.

CE NU VERIFICĂ, declarat: dacă indicatorii sunt corecți pe datele unei firme (aia e probă, nu gard),
și dacă `nr_mediu_salariati` e numărul mediu din metodologia oficială — **nu e**, e o aproximare
lunară, declarată ca atare în modul și marcată în răspuns când ea decide încadrarea.
"""
from decimal import Decimal

import pytest

from core import categorie_marime as cm
from core.common import Temei

MIC = {"total_active": Decimal("100000"), "cifra_afaceri_neta": Decimal("200000"),
       "nr_mediu_salariati": 2}
MARE = {"total_active": Decimal("30000000"), "cifra_afaceri_neta": Decimal("60000000"),
        "nr_mediu_salariati": 80}
MIJLOCIU = {"total_active": Decimal("10000000"), "cifra_afaceri_neta": Decimal("20000000"),
            "nr_mediu_salariati": 30}


def test_o_firma_clar_mica_iese_micro():
    """Calibrare pozitivă: fără ea, `nedeterminata` ar fi un răspuns care trece la orice."""
    cat, _motiv, cod = cm.incadreaza(MIC, MIC)
    assert cat == "micro" and cod == "aceeasi_incadrare"


def test_o_firma_clar_mare_iese_mijlocii_mari():
    cat, _motiv, _cod = cm.incadreaza(MARE, MARE)
    assert cat == "mijlocii_mari"


def test_intre_praguri_iese_entitate_mica():
    cat, _motiv, _cod = cm.incadreaza(MIJLOCIU, MIJLOCIU)
    assert cat == "mici", cat


def test_fara_exercitiul_precedent_NU_se_rotunjeste_la_micro():
    """Modul de eșec pentru care există fișierul ăsta: micro e cea mai mică, deci e valoarea spre
    care alunecă o implementare care tratează necunoscutul ca zero.

    Se asertează pe COD, nu pe proza motivului: un test care caută cuvinte în mesaj păzește
    formularea, iar formularea se poate rescrie fără ca nimic să cadă (clichetul 50 / METODA §23).
    """
    cat, _motiv, cod = cm.incadreaza(MIC, None)
    assert cat == "nedeterminata", cat
    assert cat != "micro"
    assert cod == "fara_exercitiu_precedent", cod


def test_categoria_NU_se_schimba_dintr_un_singur_exercitiu():
    """pct. 13 alin. (2): schimbarea cere DOUĂ exerciții consecutive. O firmă care sare de la mic la
    mare într-un an rămâne în categoria precedentă."""
    cat, _motiv, cod = cm.incadreaza(MARE, MIC)
    assert cat == "micro", cat
    assert cod == "nu_se_schimba", cod


def test_codurile_de_motiv_sunt_dintr_un_nomenclator_inchis():
    """Un cod produs în afara nomenclatorului ar fi la fel de opac ca proza pe care o înlocuiește."""
    perechi = [(MIC, MIC), (MIC, None), (MARE, MIC), ({}, MIC)]
    for a, b in perechi:
        _cat, _motiv, cod = cm.incadreaza(a, b)
        assert set(cm.MOTIVE) >= {cod}, cod


def test_pragul_se_decide_pe_DOUA_criterii_nu_pe_unul():
    """O firmă care depășește UN singur criteriu rămâne micro — pct. 9 cere «cel puțin două»."""
    un_singur = dict(MIC, cifra_afaceri_neta=Decimal("9000000"))   # peste 4.5M, restul sub prag
    cat, _m, _c = cm.incadreaza(un_singur, un_singur)
    assert cat == "micro", cat
    doua = dict(un_singur, total_active=Decimal("3000000"))        # acum două din trei
    cat2, _m2, _c2 = cm.incadreaza(doua, doua)
    assert cat2 == "mici", cat2


def test_un_indicator_necunoscut_NU_se_citeste_ca_sub_prag():
    """`None` înseamnă necunoscut, nu «nu depășește» — altfel orice gol împinge firma spre micro."""
    d = cm.depaseste({"total_active": None, "cifra_afaceri_neta": Decimal("1"),
                      "nr_mediu_salariati": 1}, cm.PRAGURI["micro"])   # tuplu (valoare, temei)
    assert d["total_active"] is None
    assert d["cifra_afaceri_neta"] is False


@pytest.mark.parametrize("categorie", ["micro", "mici"])
def test_fiecare_prag_isi_poarta_temeiul(categorie):
    """Un prag fiscal fără `Temei` e o cifră fără sursă — clasa pe care o păzește clichetul de
    constante nesursate. Se cere structural: obiectul lipit de valoare, nu un comentariu și nu o
    cheie-soră (forma dintâi a fost chiar asta, și scanul a numărat șase constante nesursate)."""
    for c in cm.CRITERII:
        t = cm.temei(categorie, c)
        assert isinstance(t, Temei), (c, type(t))
        assert t.tip == "OMFP" and t.nr == 1802 and t.an == 2014
        assert t.nivel_sursa == "MO"
        # Citarile sunt acum PER LITERA (a/b/c), deci mai scurte decat una comuna — pragul cere ca
        # ele sa existe si sa numeasca actul, nu sa fie lungi.
        assert len((t.text_citat or "").strip()) > 30, (c, t.text_citat)
        assert len((t.lant_acte or "").strip()) > 30, (c, t.lant_acte)
        assert cm.prag(categorie, c) is not None


def test_pragurile_sunt_cele_din_actul_citat():
    """Cifrele se confruntă cu textul citat în chiar temeiul lor — dacă cineva schimbă un prag și
    uită citarea, sau invers, se vede."""
    for categorie in ("micro", "mici"):
        for c in cm.CRITERII:
            t = cm.temei(categorie, c)
            v = cm.prag(categorie, c)
            # 2250000 -> "2.250.000"; 10 -> "10"
            ca_text = "{:,}".format(int(v)).replace(",", ".")
            assert ca_text in t.text_citat, (categorie, c, ca_text, t.text_citat)


def test_nomenclatorul_categoriilor_e_inchis_si_contine_nedeterminata():
    assert set(cm.CATEGORII) == {"micro", "mici", "mijlocii_mari", "nedeterminata"}


def test_incadrarea_e_afirmatie_tipata_nu_dict_de_proza():
    """`categorie()` produce o afirmație despre datele firmei (decizia din 21.08): cheamă
    `afirmatie(...)`, deci poartă `fel`, `tip`, `motiv` și temeiul de completitudine."""
    import ast
    import io
    import os
    rad = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    arb = ast.parse(io.open(os.path.join(rad, "core", "categorie_marime.py"), encoding="utf-8").read())
    fn = next(n for n in ast.walk(arb) if isinstance(n, ast.FunctionDef) and n.name == "categorie")
    chemate = {n.func.id for n in ast.walk(fn) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
    assert chemate >= {"afirmatie"}, sorted(chemate)
