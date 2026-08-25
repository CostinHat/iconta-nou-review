# -*- coding: utf-8 -*-
"""GARD: inventarul traseelor nu îmbătrânește tăcut, iar instrumentul lui nu minte.

`TRASEE.md` spune pe unde trece un document. Până azi era proză: o rută nouă putea
apărea fără ca vreun traseu s-o cuprindă, iar cifrele („câte trasee", „câte se pot
scrie din cod") erau amintiri. `scripts/scan_trasee.py` le calculează; testul ăsta nu
lasă rezultatul lui să se strice.

Ce ține:
  1. ACOPERIREA — fiecare rută din `main.py` intră fie într-un traseu, fie într-o
     suprafață declarată ca ne-documentară. Zero orfane.
  2. Fiecare rută într-un SINGUR traseu (altfel cifrele se numără de două ori).
  3. Clichetul pe clase — MECANIC/PARȚIAL/MANUAL. Nu se poate muta un traseu dintr-o
     clasă în alta fără să se schimbe cifra aici, deliberat.
  4. Calibrare NEGATIVĂ, două direcții (METODA §22): instrumentul trebuie să vadă o
     rută nouă orfană ȘI să nu inventeze una când nu e.

Ce NU ține, scris ca să nu se creadă altceva: că un traseu e CORECT. Testul spune că
harta acoperă codul, nu că drumul e bun.
"""
import importlib.util
import os

import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SCAN = os.path.join(_RAD, "scripts", "scan_trasee.py")

# Clichet la 25.08.2026, pe commitul care introduce inventarul. Se schimbă DELIBERAT.
_CLICHET = {"MECANIC": 27, "PARTIAL": 3, "MANUAL": 5}
_TRASEE_TOTAL = 35


def _scan():
    spec = importlib.util.spec_from_file_location("scan_trasee", _SCAN)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def st():
    return _scan()


@pytest.fixture(scope="module")
def d(st):
    return st.construieste(cu_db=False)


def test_nicio_ruta_in_afara_inventarului(d):
    assert not d["orfane"], (
        "rute care nu aparțin niciunui traseu și nici unei suprafețe declarate "
        "ne-documentare: %s. Adaugă ruta la traseul ei în scripts/scan_trasee.py:TRASEE, "
        "sau la NEDOCUMENTARE cu eticheta ei." % d["orfane"])


def test_nicio_ruta_in_doua_trasee(d):
    assert not d["dublate"], (
        "rute prinse de tiparele a două trasee — cifrele s-ar număra de două ori: %s"
        % d["dublate"])


def test_numarul_de_trasee_e_clichet(d):
    assert len(d["trasee"]) == _TRASEE_TOTAL, (
        "inventarul de trasee s-a schimbat (%d, clichet %d). Dacă e deliberat, schimbă "
        "clichetul ȘI scrie traseul nou în TRASEE.md."
        % (len(d["trasee"]), _TRASEE_TOTAL))


def test_clasele_sunt_clichet(d):
    from collections import Counter
    c = Counter(t["clasa"] for t in d["trasee"])
    acum = {k: c.get(k, 0) for k in _CLICHET}
    assert acum == _CLICHET, (
        "clasificarea traseelor s-a schimbat: %s (clichet %s). Un traseu care trece din "
        "PARȚIAL în MECANIC înseamnă că s-a construit persistența — se scrie în TRASEE.md."
        % (acum, _CLICHET))


def test_fiecare_traseu_are_cel_putin_o_ruta(d):
    """Anti-vacuu: un traseu cu zero rute nu măsoară nimic și ar trece verde degeaba."""
    goale = [t["id"] for t in d["trasee"] if t["rute"] == 0]
    assert not goale, ("trasee fără nicio rută — tiparele nu mai potrivesc nimic: %s"
                       % goale)


def test_marginile_declarate_exista(st):
    """Lista de module-margine e scrisă cu mâna (cu motivul lângă fiecare). Dacă un modul
    din ea dispare din `core/`, lista minte — și `module_margine` trebuie să cadă."""
    mod = st.citeste_module()
    lipsa = sorted(set(st.MARGINI) - set(mod))
    assert not lipsa, "MARGINI numește module care nu mai există în core/: %s" % lipsa


def test_nemarginile_declarate_exista(st):
    mod = st.citeste_module()
    lipsa = sorted(set(st.NEMARGINI) - set(mod))
    assert not lipsa, "NEMARGINI numește module care nu mai există în core/: %s" % lipsa


def test_calibrare_negativa_vede_o_ruta_orfana(st):
    """RED-proof, direcția «ratează»: o cale care nu seamănă cu niciun traseu TREBUIE să
    iasă ca orfană. Fără proba asta, `orfane == []` poate însemna «n-am căutat»."""
    falsa = {"metoda": "POST", "cale": "/inventat/pe-nicaieri",
             "norm": "/inventat/pe-nicaieri", "fn": "x", "linie": 0,
             "garzi": [], "roluri": [], "fine": [], "module": [],
             "scrie_inline": {}, "refuzuri": 0}
    _, orfane, _, _ = st.acoperire([falsa])
    assert orfane == [("POST", "/inventat/pe-nicaieri")], (
        "instrumentul NU vede o rută în afara inventarului — deci un «zero orfane» pe "
        "cod real nu dovedește nimic. Rezultat: %s" % orfane)


def test_calibrare_negativa_nu_inventeaza_orfane(st):
    """RED-proof, direcția «raportează fals»: o cale care aparține clar unui traseu NU
    trebuie să apară ca orfană. Un instrument care greșește în AMBELE direcții n-are
    niciun plafon (METODA §22)."""
    buna = {"metoda": "POST", "cale": "/tenants/{tenant_id}/casa/operatiuni",
            "norm": "/tenants/{}/casa/operatiuni", "fn": "x", "linie": 0,
            "garzi": ["cere_cabinet"], "roluri": [], "fine": [], "module": [],
            "scrie_inline": {}, "refuzuri": 0}
    per, orfane, dublate, _ = st.acoperire([buna])
    assert not orfane and not dublate and per["T09"], (
        "o rută care aparține traseului casei a fost raportată greșit: orfane=%s "
        "dublate=%s" % (orfane, dublate))


def test_aliasul_local_bate_pe_cel_de_modul(st):
    """Mutația pe propriul mod de eșec al instrumentului. Ruta de NIR își importă modulul
    ÎN CORP (`from core import stocuri_api as _s`), iar `_s` e refolosit de zeci de ori
    în main.py pentru module diferite. Prima formă a instrumentului atribuia rutei de NIR
    modulul `salarizare` — o atribuire FALSĂ, mai rea decât o absență."""
    rute = st.citeste_rute()
    nir = [r for r in rute if r["norm"] == "/tenants/{}/stocuri/nir"
           and r["metoda"] == "POST"]
    assert nir, "ruta POST /tenants/{}/stocuri/nir a dispărut din main.py"
    assert set(nir[0]["module"]) == {"stocuri_api"}, (
        "ruta de NIR nu mai e legată exact de `stocuri_api`, ci de %s — harta aliasurilor "
        "locale s-a stricat" % sorted(nir[0]["module"]))
