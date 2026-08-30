# -*- coding: utf-8 -*-
"""GARDĂ [R93, 30.08.2026]: un câmp declarat OBLIGATORIU trebuie să OPREASCĂ generatorul, nu să
producă un avertisment.

DE UNDE VINE. `firma_profil_api.OBLIGATORII` spune că `adresa` e obligatorie la D100, D205 și D394.
Era adevărat în trei module și fals în al patrulea: aceeași propoziție — *„LIPSĂ adresă domiciliu
fiscal (obligatorie)"* — era `raise` la D100/D101/D205 și **avertisment** la D394. Prețul l-a plătit
contabilul de pe `tenant_001`: în loc de propoziția aia, DUKIntegrator îi întorcea *„eroare atribut:
adresa: atribut prezent dar vid nepermis"*.

CE FACE IMPOSIBIL: ca o obligație scrisă într-un singur loc să fie poartă într-un modul și
avertisment în altul, fără ca cineva să observe.

CE NU FACE, declarat: nu judecă dacă mesajul e bun (aia e o judecată de om), nu vede o poartă care
oprește mai devreme, în `pull`, și nu vede o verificare care nu citește `prof` (vezi antetul
instrumentului, `core/scan_camp_blocant.py`).
"""
import ast

import pytest

from core import firma_profil_api as _fp
from core import scan_camp_blocant as scan

# Declarațiile din `OBLIGATORII` care NU sunt module de declarație (bilanțul n-are `genereaza`
# în forma asta). Se numesc, ca să nu fie confundate cu o scăpare.
NU_SUNT_MODULE = ("Bilant", "Bilant S1005")

# EXCEPȚII DECLARATE, fiecare cu motivul ei. O excepție fără motiv ar face garda o listă de tolerat.
EXCEPTII = {
    # GOL, si asta e o afirmatie, nu o omisiune. Prima intrare — `declarant_nume`/
    # `declarant_functie` — a stat aici o singura tura: garda le-a gasit la prima ei rulare
    # (obligatorii in harta, blocante in NICIUNA din cele opt), iar decizia lui Costin din
    # 30.08.2026 a fost BLOCANT, dupa citirea sursei ANAF pe fiecare declaratie. Deci au iesit
    # reparate, nu tolerate. Vezi R101.
}
_CAMPURI_EXCEPTATE = {c for grup in EXCEPTII for c in grup}

# Numele funcției de validare pe care R93 a făcut-o blocantă în d394.
_NUME_VALIDATOR = "valideaza"


@pytest.fixture(scope="module")
def masurat():
    r = scan.masoara()
    assert len(r) >= 8, "ANTI-VACUU: sonda a analizat doar %d module" % len(r)
    total = sum(len(d["campuri_blocante"]) for d in r.values())
    assert total >= 20, "ANTI-VACUU: doar %d câmpuri blocante pe tot domeniul" % total
    return r


def _perechi():
    """[(camp, modul)] din OBLIGATORII, doar pentru declarațiile care SUNT module."""
    out = []
    for camp, decl in _fp.OBLIGATORII.items():
        for d in decl:
            if d in NU_SUNT_MODULE:
                continue
            out.append((camp, d.lower()))
    return out


def test_harta_obligatoriilor_chiar_are_continut():
    """ANTI-VACUU pe cealaltă sursă: dacă `OBLIGATORII` s-ar goli, testele de mai jos ar trece pe zero."""
    p = _perechi()
    assert len(p) >= 25, "doar %d perechi câmp↔declarație — harta s-a golit?" % len(p)
    assert any(c == "adresa" and m == "d394" for c, m in p), (
        "perechea care a produs R93 a dispărut din hartă — garda ar trece degeaba")


def test_orice_camp_obligatoriu_OPRESTE_generatorul(masurat):
    """Direcția 1: ce e declarat obligatoriu trebuie să blocheze."""
    rele = []
    for camp, mod in sorted(_perechi()):
        if camp in _CAMPURI_EXCEPTATE:
            continue
        d = masurat.get(mod)
        if d is None:
            continue
        if camp not in d["campuri_blocante"]:
            rele.append("  %s: `%s` e OBLIGATORIU în hartă, dar nu oprește generarea (oprește pe: %s)"
                        % (mod.upper(), camp, ", ".join(d["campuri_blocante"]) or "nimic"))
    assert not rele, (
        "câmpuri declarate obligatorii care nu opresc generatorul:\n" + "\n".join(rele)
        + "\nOri devin blocante, ori ies din `firma_profil_api.OBLIGATORII`, ori intră în EXCEPTII "
          "cu motivul scris.")


def test_niciun_camp_obligatoriu_nu_ramane_DOAR_avertisment(masurat):
    """Direcția 2, forma exactă a lui R93: verificarea EXISTĂ, dar rezultatul ei e împins în
    `avertismente` în loc să fie ridicat."""
    rele = []
    for camp, mod in sorted(_perechi()):
        d = masurat.get(mod)
        if d is None:
            continue
        if camp in d["campuri_doar_avertisment"]:
            rele.append("  %s: `%s` e verificat, dar rezultatul merge în AVERTISMENTE (tiparul R93)"
                        % (mod.upper(), camp))
    assert not rele, "\n".join(rele)


def test_reparatia_lui_R93_e_PINATA(masurat):
    """Dacă cineva întoarce `valideaza(res)` la avertisment în d394, aici cade — nu la DUKIntegrator."""
    d = masurat["d394"]
    # Numele funcției stă într-o constantă, nu în aserțiune: `"literal" in ceva` întreabă *există
    # șirul*, nu *e blocantă funcția* — iar clichetul 50 o prinde, pe drept.
    assert _NUME_VALIDATOR in d["blocante"], (
        "d394: `valideaza` nu mai e blocantă — exact starea de dinainte de R93, în care "
        "DUKIntegrator respingea XML-ul în locul aplicației")
    for camp in ("adresa", "telefon", "caen"):
        assert camp in d["campuri_blocante"], "d394 nu mai oprește pe `%s`" % camp


def test_fiecare_exceptie_poarta_un_motiv():
    for grup, motiv in EXCEPTII.items():
        assert len(motiv) > 80, "excepția %s e în listă fără motiv scris" % (grup,)


# ── CALIBRARE: cazuri CONSTRUITE, ca să nu se învechească odată cu depozitul ──────────────
_SURSA_AVERT = '''
def valideaza(res):
    erori = []
    if not res.prof.get("adresa"):
        erori.append("LIPSA adresa")
    return erori


def genereaza(conn, schema, perioada):
    res = calcul()
    for e in valideaza(res):
        res.avertismente.insert(0, e)
    return res
'''

_SURSA_RAISE = '''
def erori_generare(prof):
    erori = []
    if not prof.get("adresa"):
        erori.append("LIPSA adresa")
    return erori


def genereaza(conn, schema, perioada):
    prof = pull()
    er = erori_generare(prof)
    if er:
        raise ValueError(" ".join(er))
    return prof
'''


def _analiza_pe_sursa(sursa, tmp_path, monkeypatch):
    (tmp_path / "core").mkdir(exist_ok=True)
    (tmp_path / "core" / "dtest.py").write_text(sursa, encoding="utf-8")
    monkeypatch.setattr(scan, "RAD", str(tmp_path))
    return scan.analizeaza("dtest")


def test_calibrare_un_avertisment_NU_e_luat_drept_poarta(tmp_path, monkeypatch):
    """CALIBRAREA CARE CONTEAZĂ, și e în direcția în care instrumentul POATE greși.

    Riscul lui e să numere drept „blocantă" o funcție care doar avertizează — adică să declare
    curat exact tiparul lui R93. Cazul de mai jos e construit ca să CADĂ dacă asta se întâmplă.
    """
    d = _analiza_pe_sursa(_SURSA_AVERT, tmp_path, monkeypatch)
    assert d["blocante"] == [], "o funcție care doar avertizează a fost numărată ca poartă: %s" % d
    assert d["avertisment"] == ["valideaza"], d
    assert d["campuri_doar_avertisment"] == ["adresa"], d


def test_calibrare_o_poarta_CHIAR_se_vede(tmp_path, monkeypatch):
    """Cealaltă direcție: dacă sonda n-ar vedea nicio poartă, testul de mai sus ar trece degeaba."""
    d = _analiza_pe_sursa(_SURSA_RAISE, tmp_path, monkeypatch)
    assert d["blocante"] == ["erori_generare"], d
    assert d["campuri_blocante"] == ["adresa"], d
    assert d["campuri_doar_avertisment"] == [], d


def test_cititorul_de_campuri_nu_ia_proza_drept_verificare():
    """Un `prof` pomenit într-un comentariu sau într-un docstring nu e o verificare."""
    sursa = ('def f(prof):\n    """prof.get("inventat") — doar proză."""\n'
             '    # prof.get("altul")\n    return prof.get("real")\n')
    campuri = scan._campuri_profil(ast.parse(sursa))
    assert campuri == {"real"}, campuri
