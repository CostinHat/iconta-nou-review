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
import io
import os
import re

import pytest

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: (rută, select=opțiune, câmp) acceptate, cu motivul: ramura care-l cere NU e atinsă din ecran.
EXCEPTII = {
    ("nota-inventariere", "operatie=casare", "valoare_bruta"):
        "formularul cere `mijloc_fix_id` (obligatoriu) -> ramura fără el, cu sumele date de mână, e calea API",
    ("nota-inventariere", "operatie=casare", "amortizare_cumulata"): "idem",
    ("vanzare-marja-turism", "*", "componente"):
        "regimul normal (art.311 alin.(10)) se alege prin `optiune_normal`, pe care ecranul nu-l are: din ecran se "
        "ajunge numai la regimul special — ramura e calea API",
    ("vanzare-marja-turism", "*", "comision"): "idem, regimul de intermediar (`intermediar`)",
    ("nota-sponsorizare", "*", "cifra_afaceri"): "citit numai sub `if corp.get(\"cifra_afaceri\") is not None` — calcul opțional",
    ("nota-sgr", "operatie=virare", "suma"):
        "câmp comun: alternativ la nr. ambalaje la achiziție/vânzare/restituire, obligatoriu doar la virare; motorul de "
        "formulare nu are «opțional pe operație» pentru același câmp, iar refuzul rutei numește câmpul",
    ("achizitie-agricultor", "*", "agricultor"): "citit numai sub `if corp.get(\"agricultor\")` — opțional prin construcție",
}


def _citeste(p):
    return io.open(os.path.join(RAD, p), encoding="utf-8").read()


def formulare(js):
    starts = list(re.finditer(r'cheie: "([^"]+)", titlu: "([^"]+)", ruta: "([^"]+)"', js))
    for k, m in enumerate(starts):
        corp = js[m.end():(starts[k + 1].start() if k + 1 < len(starts) else len(js))]
        multi = re.match(r'\s*,\s*multi: "(\w+)"', corp)
        corp = corp.split("subcampuri:")[0]
        poz = [x.start() for x in re.finditer(r'\bC\("', corp)] + [len(corp)]
        campuri = []
        for a, b in zip(poz, poz[1:]):
            buc = corp[a:b]
            nume = re.match(r'C\("(\w+)"', buc).group(1)
            cm = re.search(r'cond: \{ camp: "(\w+)", val: (\[[^\]]*\]|"[^"]*") \}', buc)
            opt = re.search(r'optiuni: \[(.*?)\]\]', buc)
            campuri.append({"nume": nume, "optional": re.search(r"\boptional: true\b", buc) is not None, "cond": (cm.group(1), re.findall(r'"([^"]*)"', cm.group(2))) if cm else None,
                            "optiuni": re.findall(r'\["([^"]*)",', opt.group(1) + "]") if opt else None})
        if multi:   # cheia `multi` e lista de rânduri, completată din subcâmpuri
            campuri.append({"nume": multi.group(1), "optional": False, "cond": None, "optiuni": None})
        yield m.group(1), m.group(3), campuri


def functie_uc(ruta, main, uc):
    m = re.search(r'@app\.post\("/tenants/\{tenant_id\}/%s"\)\ndef \w+\(' % re.escape(ruta), main)
    if not m:
        return None
    f = re.search(r'_uc_tenants\.(\w+)\(', main[m.end():main.find("\n@app", m.end())])
    if not f or ("def %s(" % f.group(1)) not in uc:
        return None
    i = uc.index("def %s(" % f.group(1))
    return uc[i:uc.find("\ndef ", i + 5)]


def ramura(src, var, val):
    m = re.search(r'\n( *)(?:if|elif) %s == "%s":' % (re.escape(var), re.escape(val)), src)
    if not m:
        return None
    ind = len(m.group(1))
    linii = []
    for l in src[m.end():].split("\n")[1:]:
        if l.strip() and len(l) - len(l.lstrip(" ")) <= ind:
            break
        linii.append(l)
    return "\n".join(linii)


def cerute_in(cod):
    """Câmpurile pe care un bloc de cod le cere OBLIGATORIU: acces direct `corp["x"]` și ajutoarele care refuză fără
    câmp — `cota_ceruta(corp)` cere `cota`; `cere_cont(conn, schema, corp.get("x"), "x")` FĂRĂ implicit cere `x`."""
    c = set(re.findall(r'corp\["(\w+)"\]', cod))
    if re.search(r"cota_ceruta\(corp\)", cod):
        c.add("cota")
    c |= set(re.findall(r'cere_cont\(conn, schema, corp\.get\("(\w+)"\), "\w+"\)', cod))
    return c - {"data"}


def lipsuri(js, main, uc):
    out = []
    for cheie, ruta, campuri in formulare(js):
        src = functie_uc(ruta, main, uc)
        if not src:
            continue
        ramificat = False
        for sel in (c for c in campuri if c["optiuni"]):
            vm = re.search(r'(\w+) = corp\.get\("%s"' % sel["nume"], src)
            if not vm:
                continue
            ramificat = True
            for val in sel["optiuni"]:
                br = ramura(src, vm.group(1), val)
                if br is None:
                    continue
                cerute = cerute_in(br)
                vizibile = {c["nume"] for c in campuri
                            if c["cond"] is None or c["cond"][0] != sel["nume"] or val in c["cond"][1]}
                optionale = {c["nume"] for c in campuri if c["optional"]}
                for x in sorted(cerute & vizibile & optionale):
                    if (ruta, "%s=%s" % (sel["nume"], val), x) not in EXCEPTII:
                        out.append((ruta, sel["nume"], val, x, "optional"))
                for x in sorted(cerute - vizibile):
                    if (ruta, "%s=%s" % (sel["nume"], val), x) in EXCEPTII:
                        continue
                    out.append((ruta, sel["nume"], val, x, "lipsa"))
        if not ramificat:   # formular cu o singură operație: tot corpul rutei
            for x in sorted(cerute_in(src) & {c["nume"] for c in campuri if c["optional"]}):
                if (ruta, "*", x) not in EXCEPTII:
                    out.append((ruta, None, None, x, "optional"))
            for x in sorted(cerute_in(src) - {c["nume"] for c in campuri}):
                if (ruta, "*", x) not in EXCEPTII:
                    out.append((ruta, None, None, x, "lipsa"))
    return out


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
    for nume in re.findall(r'C\("(\w+)"[^\n]*optiuni: \[\["(?:true|false|0|1)",', js):
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
