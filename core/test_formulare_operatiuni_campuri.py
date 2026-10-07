# -*- coding: utf-8 -*-
"""GARD — nicio opțiune a unui formular din ecranul Operațiuni nu poate fi imposibil de trimis cu succes
(lot 19, defectul 13, 03.10.2026).

Clasa: formularul arată o opțiune (un `select` — operație / fel / tip), dar ruta, pe ramura acelei opțiuni, citește
un câmp (`corp["x"]`) pe care formularul nu-l afișează pentru ea. Cu date perfect valide, răspunsul e „Lipsește
câmpul x” — opțiunea nu poate reuși NICIODATĂ din interfață. Găsit: Credite bancare › Garanție (sumă, fel, acțiune)
și › Restanță (sumă); Subvenții › Reluare la venituri (valoare activ, subvenție, amortizare lunară). Precedent din
aceeași clasă: R145 (nota-chirie), reparat atunci doar local — fără gardă, clasa a supraviețuit în alte formulare.

Cum citește: pentru fiecare formular, ruta din `main.py` -> funcția din `core/uc_tenants.py`; pentru fiecare opțiune a
fiecărui select, ramura `if/elif <var> == "<opțiune>"` (unde `<var> = corp.get("<select>")`); câmpurile `corp["x"]`
din ramură trebuie să fie vizibile pentru opțiune (fără `cond`, sau cu `cond` pe acel select care include opțiunea).
LIMITA, declarată: vede doar accesul `corp["x"]` (obligatoriu), nu `corp.get` (opțional prin construcție); vede
ramurile scrise ca `if/elif var == "v"`, nu dispecere prin dicționare.
"""
import os
import re
import sys

import pytest

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAD, "scripts"))
# [07.10.2026, „Cele 33 de chei”] Analiza stă în `scripts/scan_formulare_operatiuni.py`: o singură implementare pentru gărzile de aici
# ȘI pentru regula `FAPT_FISCAL_NECERUT` din verificator; clasificarea (ce rămâne în afara ecranului, cu motivul) e date, acolo.
from scan_formulare_operatiuni import (ASCUNSE_PERMISE, BIFA_VALORI, CHEI_IN_AFARA_ECRANULUI, EXCEPTII,  # noqa: E402,F401
                                       OPTIONALE_PERMISE, _citeste, ascunse_pe_ramura, bife_nerespectate, cerute_in,
                                       chei_fara_camp, formulare, functie_uc, lipsuri, masoara, motor_fara_preselectie,
                                       optionale, ramura, selecturi_preselectate)


def _mesaj(r):
    ruta, sel, val, x, fel = r
    unde = "%s › %s=%s" % (ruta, sel, val) if sel else ruta
    return "%s: ruta cere `%s`, formularul %s" % (unde, x, "îl marchează opțional" if fel == "optional" else "nu-l arată")


def test_nicio_optiune_imposibila_din_ecran():
    rele = lipsuri(_citeste("static/js/ecrane/operatiuni_ecran.js"), _citeste("main.py"), _citeste("core/uc_tenants.py"))
    assert rele == [], "opțiuni care nu pot reuși din ecran:\n  " + "\n  ".join(_mesaj(r) for r in rele)


def test_CALIBRARE_prinde_campul_scos():
    js = _citeste("static/js/ecrane/operatiuni_ecran.js")
    i = js.index('ruta: "nota-credit"')
    j = js.index('cheie:', i)
    stricat = js[:i] + re.sub(r'C\("suma"[^\n]*\n', "", js[i:j], count=1) + js[j:]
    rele = lipsuri(stricat, _citeste("main.py"), _citeste("core/uc_tenants.py"))
    assert ("nota-credit", "operatie", "garantie", "suma", "lipsa") in set(rele), rele


def test_bifele_se_citesc_doar_prin_bifa():
    """Clasa (b): `bool("false")` e True. Nicio citire `bool(corp...)` în use-case-uri; selecturile da/nu ale ecranului
    se citesc prin `_uc_comun.bifa`."""
    uc = _citeste("core/uc_tenants.py")
    assert not re.search(r"bool\(corp\b", uc), re.findall(r".*bool\(corp.*", uc)
    js = _citeste("static/js/ecrane/operatiuni_ecran.js")
    da_nu = re.findall(r'C\("(\w+)"[^\n]*optiuni: \[\["(?:true|false|0|1)",', js) + re.findall(r'\bDN\("(\w+)"', js)
    assert len(da_nu) >= 13      # premisă: constructorul `DN(` chiar se vede (altfel bucla de mai jos ar trece în gol)
    for nume in da_nu:
        citiri = re.findall(r'corp(?:\.get\(|\[)"%s"' % nume, uc)
        assert not citiri, "bifa %r citită direct (`corp[...]`/`corp.get`), nu prin _uc_comun.bifa" % nume
        assert '_uc_comun.bifa(corp, "%s"' % nume in uc, "bifa %r nu e citită prin _uc_comun.bifa" % nume


@pytest.mark.parametrize("v,asteptat", [(True, True), (False, False), ("true", True), ("false", False), ("1", True),
                                        ("0", False), ("Da", True), ("nu", False), (1, True), (0, False)])
def test_bifa_citeste_corect(v, asteptat):
    from core import uc_comun
    assert uc_comun.bifa({"x": v}, "x") is asteptat


def test_bifa_refuza_ce_nu_e_da_nu_si_cere_campul_obligatoriu():
    from core import uc_comun
    with pytest.raises(ValueError):
        uc_comun.bifa({"x": "poate"}, "x")
    with pytest.raises(KeyError):
        uc_comun.bifa({}, "x")
    assert uc_comun.bifa({}, "x", True) is True


# =================================================================================================================
# [C6, comanda Costin 07.10.2026] Un DA/NU pe care serverul îl citește prin `bifa` se cere EXPLICIT în ecran.
#
# Instanța: „Dovada export (DVE)” era câmp TEXT — contabilul scria numărul DVE, iar serverul răspundea „acceptă doar da sau
# nu”. Clasa, măsurată pe toate formularele Operațiunilor: 2 câmpuri text, 8 bife pe care formularul nu le avea deloc
# (serverul punea tăcut „nu” — un provizion pe o creanță în faliment ieșea nedeductibil), 3 selecturi cu „Da” preselectat,
# 1 opțional cu „-”. Regula (DS cap.17, DEFAULT_FISCAL_TACIT): faptul fiscal „se cere EXPLICIT … fără preselecție tacită”.
# =================================================================================================================

def test_bifele_serverului_se_cer_explicit_da_nu():
    rele = bife_nerespectate(_citeste("static/js/ecrane/operatiuni_ecran.js"), _citeste("main.py"), _citeste("core/uc_tenants.py"))
    assert rele == [], "bife ale serverului necerute explicit în ecran:\n  " + "\n  ".join("%s › %s: %s" % r for r in rele)


@pytest.mark.parametrize("stricare,asteptat", [
    # instanța C6: câmpul text
    (('DN("dovada_export", "Ai declarația vamală de export (DVE)", ', 'C("dovada_export", "Dovada export (DVE)", "text", '),
     ("export-extracomunitar", "dovada_export", "e câmp „text”, nu DA/NU")),
    # bifa scoasă din formular
    (('    DN("faliment", ', '    C("_scos_", "x", "numar", '), ("nota-provizion", "faliment", "lipsește din formular — serverul pune implicitul fără ca omul să fi ales")),
    # preselecția „Da”
    (('    DN("imputabil", "Imputabil", { ', '    C("imputabil", "Imputabil", "select", { optional: true, optiuni: [["true","Da"],["false","Nu"]], '),
     ("nota-inventariere", "imputabil", "DA/NU fără „— alege —” obligatoriu (preselectat sau opțional)")),
])
def test_CALIBRARE_bifele_prind_fiecare_forma(stricare, asteptat):
    js = _citeste("static/js/ecrane/operatiuni_ecran.js")
    assert js.count(stricare[0]) == 1, stricare[0]
    rele = bife_nerespectate(js.replace(stricare[0], stricare[1]), _citeste("main.py"), _citeste("core/uc_tenants.py"))
    assert asteptat in rele, rele


def nume_citite_numeric():
    """Numele pe care codul le citește ca NUMĂR (`_numar(x, …)`, `_d(x)`, `Decimal(str(x))`, `float(x)`, `int(x)`, și la fel pe
    `corp["x"]`). LIMITA, declarată: după NUME — un parametru numit altfel decât cheia din corp nu se vede."""
    n = set()
    for f in sorted(os.listdir(os.path.join(RAD, "core"))):
        if f.endswith(".py") and not f.startswith("test_"):
            s = _citeste("core/" + f)
            n |= set(re.findall(r'\b(?:_numar|_d|Decimal|float|int)\(\s*(?:str\()?([a-z_][a-z0-9_]*)\b\s*[,)]', s))
            n |= set(re.findall(r'\b(?:_numar|_d|Decimal|float|int)\(\s*(?:str\()?corp(?:\["|\.get\(")([a-z0-9_]+)"', s))
    return n


def test_campul_text_nu_e_citit_ca_numar():
    """Vecinul de tip al lui C6 (aceeași rădăcină: tipul câmpului ≠ tipul citit). Găsit: „Puritate (ex. 995)” era text, iar
    `tva_aur._numar` o citește ca număr. MUTAȚIE: puritatea pusă la loc pe "text" -> pică."""
    js = _citeste("static/js/ecrane/operatiuni_ecran.js")
    text = {c["nume"] for _k, _r, cs in formulare(js) for c in cs if c["tip"] == "text"}
    assert len(text) > 10                                # premisă: tipurile chiar se citesc
    assert sorted(text & nume_citite_numeric()) == []


# =================================================================================================================
# [comanda Costin 07.10.2026, „Cele 33 de chei”] DS cap.17: „O cheie care e fapt fiscal (schimbă nota, baza sau impozitul) intră în
# formular, cerută explicit, fără preselecție. O cheie strict tehnică, pentru API, rămâne în afara ecranului.” Clasificarea e în
# `scripts/scan_formulare_operatiuni.py` (31 au intrat; 2 rămân, cu motivul). Fiecare garda de mai jos e ratchet în AMBELE sensuri.
# =================================================================================================================

def test_cheile_fara_camp_sunt_exact_cele_clasificate():
    """MUTAȚIE: câmpul „Cont venit” scos de la export -> `export-extracomunitar:cont_venit` fără câmp -> pică."""
    acum = chei_fara_camp(*_surse_())
    assert sorted(acum - set(CHEI_IN_AFARA_ECRANULUI)) == [], "cheie citită de server, fără câmp în formular și neclasificată"
    assert sorted(set(CHEI_IN_AFARA_ECRANULUI) - acum) == [], "cheie clasificată «în afara ecranului» care are acum câmp: scoate-o"
    assert all(len(m) > 60 for m in CHEI_IN_AFARA_ECRANULUI.values())


def test_nicio_cheie_citita_pe_o_ramura_unde_campul_e_ascuns():
    """Varianta (b) a clasei: `nota-credit` › plată citea dobânda, câmpul se vedea numai la „Dobândă”. MUTAȚIE: dobânda înapoi
    doar pe „dobanda” -> pică."""
    acum = ascunse_pe_ramura(*_surse_())
    assert sorted(acum - set(ASCUNSE_PERMISE)) == [], "cheie citită pe o ramură pe care câmpul ei e ascuns"
    assert sorted(set(ASCUNSE_PERMISE) - acum) == []


def test_campurile_optionale_sunt_exact_cele_permise():
    """Varianta (c): un câmp opțional = golul lui devine implicitul serverului (accize 0, cont 371, data notei…). MUTAȚIE: „Accize”
    pus la loc opțional -> pică."""
    acum = optionale(_surse_()[0])
    assert sorted(acum - set(OPTIONALE_PERMISE)) == [], "câmp opțional al cărui gol e un implicit al serverului"
    assert sorted(set(OPTIONALE_PERMISE) - acum) == []


def test_niciun_select_obligatoriu_nu_vine_preselectat():
    """Varianta (d): 36 de selecturi obligatorii veneau cu prima opțiune aleasă. Regula e a MOTORULUI acum. MUTAȚIE: motorul fără
    „— alege —” implicit -> pică."""
    js = _surse_()[0]
    assert motor_fara_preselectie(js)
    assert sorted(selecturi_preselectate(js)) == []


def test_verificatorul_si_testul_folosesc_aceeasi_masuratoare():
    assert masoara() == []


def _surse_():
    return _citeste("static/js/ecrane/operatiuni_ecran.js"), _citeste("main.py"), _citeste("core/uc_tenants.py")


@pytest.mark.parametrize("stricare,asteptat", [
    (('    C("cont_venit", "Cont venit", "text", { sugestie: "707" }),\n', ''), "export-extracomunitar:cont_venit"),
    (('C("comision", "Comision bancar (627)", "numar", { cond: { camp: "operatie", val: "plata" } }),', ''), "nota-credit:comision"),
])
def test_CALIBRARE_cheia_scoasa_din_formular_e_prinsa(stricare, asteptat):
    js, main, uc = _surse_()
    assert js.count(stricare[0]) == 1, stricare[0]
    assert asteptat in chei_fara_camp(js.replace(stricare[0], stricare[1]), main, uc)


def test_CALIBRARE_ramura_ascunsa_e_prinsa():
    js, main, uc = _surse_()
    a = 'C("dobanda", "Dobândă", "numar", { cond: { camp: "operatie", val: ["dobanda", "plata"] } }),'
    assert js.count(a) == 1
    stricat = js.replace(a, 'C("dobanda", "Dobândă", "numar", { cond: { camp: "operatie", val: "dobanda" } }),')
    assert {"nota-credit:operatie=plata:dobanda"} <= ascunse_pe_ramura(stricat, main, uc)


def test_CALIBRARE_preselectia_e_prinsa():
    js = _surse_()[0]
    a = '`<option value="" selected>${esc(c.neales || "— alege —")}</option>`;'
    assert js.count(a) == 1
    stricat = js.replace(a, '(c.neales ? `<option value="" selected>${esc(c.neales)}</option>` : "");')
    assert not motor_fara_preselectie(stricat)
    assert {"nota-credit:tip"} <= selecturi_preselectate(stricat)


def motorul_onoreaza_registrul(js):
    """Ce declară registrul (`trimiteCa`, `lista`, `multiCond`, condiția în lanț) trebuie să-l și facă motorul — altfel
    garda de mai sus ar judeca un formular pe care ecranul nu-l trimite așa. Întoarce ce lipsește din motor."""
    cerinte = {
        "trimiteCa": r"corpReq\[c\.trimiteCa \|\| c\.nume\]",
        "lista": r"c\.lista \? \[val\] : val",
        "multiCond": r'opCurenta\.multiCond \? ` data-cond-camp="\$\{opCurenta\.multiCond\.camp\}"',
        "multi ascuns netrimis": r'blocMulti\.style\.display !== "none"',
        "lanț": r'const vizibil = parinte && parinte\.style\.display !== "none";',
    }
    return sorted(k for k, rx in cerinte.items() if not re.search(rx, js))


def test_motorul_onoreaza_trimiteCa_lista_multiCond_si_lantul():
    """[07.10.2026] Probat în browser (`frontend_test/proba_chei_optionale.py`): bacșișul distribuit în numerar -> 462 = 5311;
    turismul normal trimite `componente` și `locuri` ca listă; „Cui se impută” apare numai la Minus + Imputabil: Da.
    MUTAȚIE: oricare din cele cinci scoasă din motor -> pică."""
    assert motorul_onoreaza_registrul(_surse_()[0]) == []
