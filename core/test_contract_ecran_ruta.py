# -*- coding: utf-8 -*-
"""GARD: contractul ECRAN ↔ RUTĂ nu se rupe tăcut.

Un câmp pe care ecranul îl trimite și modelul nu-l are e **ignorat de pydantic**, iar ruta
răspunde 200. Asta e mai rău decât un refuz: omul vede „salvat" și nu s-a salvat nimic.
Instanța care a produs gardul (R51): ecranul de salariați trimitea `data_incetare`,
`SalariatEdit` n-o avea, ruta întorcea `{"ok": true, "neschimbat": true}` — iar salariatul
plecat rămânea în serviciu și continua să apară în D112.

Clichet, nu zero: rămân perechi pe care instrumentul NU le poate citi (corp variabilă,
răspândire) și rute fără model. Alea se numără separat, ca domeniu neatins — nu ca fiind în
regulă.

Calibrarea instrumentului, în AMBELE direcții (METODA §22, interdicția 76):
  - prima formă a extractorului vedea doar `cheie: valoare` și rata prescurtarea ES6
    (`{ an, luna }`) — a raportat **30** de diferențe, din care primele trei verificate erau
    toate false. Aici se probează că prescurtarea se citește;
  - și că o diferență REALĂ chiar iese, altfel „1 diferență" n-ar dovedi nimic.
"""
import importlib.util
import os

import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SCAN = os.path.join(_RAD, "scripts", "scan_contract_ecran.py")

# Diferențe cunoscute la 25.08.2026. Scade la reparație; nu crește.
_CLICHET = 0


def _scan():
    spec = importlib.util.spec_from_file_location("scan_contract_ecran", _SCAN)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def sc():
    return _scan()


def test_prescurtarea_ES6_se_citeste(sc):
    """Calibrare pe modul propriu de eșec: `{ an, luna }` are DOUĂ chei, nu zero."""
    assert sorted(sc._chei_top("{ an, luna }")) == ["an", "luna"]
    assert sorted(sc._chei_top("{ email, nume: x.value, poate_valida: c.checked }")) == \
        ["email", "nume", "poate_valida"]


def test_cheile_din_obiecte_imbricate_nu_urca(sc):
    """Doar primul nivel: o cheie dintr-un obiect imbricat nu e un câmp al corpului."""
    chei = sc._chei_top("{ a: 1, b: { c: 2, d: 3 }, e }")
    assert sorted(chei) == ["a", "b", "e"], chei


def test_sirurile_nu_produc_chei_false(sc):
    """Un `:` dintr-un șir (o oră, un URL) nu e o cheie."""
    chei = sc._chei_top('{ mesaj: "ora 12:30", url: "http://x/y" }')
    assert sorted(chei) == ["mesaj", "url"], chei


def test_numarul_de_diferente_nu_creste(sc):
    d = _rezultat(sc)
    assert len(d["diferente"]) <= _CLICHET, (
        "contracte ecran↔rută rupte: %d (clichet %d). Un câmp trimis și necerut e ignorat "
        "TĂCUT de pydantic — ruta răspunde 200 și nu salvează nimic.\n%s"
        % (len(d["diferente"]), _CLICHET,
           "\n".join("  %s:%s %s %s -> %s" % (x["fisier"], x["linia"], x["metoda"], x["url"],
                                              x["cerut_netrimis"] + x["trimis_necerut"])
                     for x in d["diferente"])))


def test_domeniul_nu_se_ingusteaza(sc):
    """Anti-vacuu: dacă extractorul se strică și nu mai citește nimic, `diferente` ajunge la
    zero și testul de mai sus trece. Se cere ca perechile COMPARATE să rămână multe."""
    d = _rezultat(sc)
    assert d["perechi"] >= 60, (
        "instrumentul compară doar %d perechi ecran↔rută — s-a îngustat domeniul, iar un "
        "zero pe diferențe nu mai dovedește nimic" % d["perechi"])


def _rezultat(sc):
    apeluri, necitibile = sc.apeluri_din_ecrane()
    rute, modele = sc.modele_rute()
    perechi, dif = 0, []
    for a in apeluri:
        cheie = (a["metoda"], sc.normalizeaza_url(a["url"]))
        model = rute.get(cheie)
        if cheie not in rute or model is None:
            continue
        oblig, toate = modele[model]
        perechi += 1
        lipsa = sorted(oblig - set(a["chei"]))
        in_plus = sorted(set(a["chei"]) - toate)
        if lipsa or in_plus:
            dif.append({**a, "cerut_netrimis": lipsa, "trimis_necerut": in_plus})
    return {"perechi": perechi, "diferente": dif, "necitibile": len(necitibile)}
