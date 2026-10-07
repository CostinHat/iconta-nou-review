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
    # [C6, 07.10.2026] `DN(...)` se citește din DEFINIȚIA lui în ecran (opțiunile și „— alege —”), nu se presupune: un constructor
    # schimbat (ex. fără `neales`) trebuie să se vadă în fiecare câmp DA/NU. Fără definiție, `DN(` nu e DA/NU.
    dn_def = re.search(r'const DN = [^\n]*', js)
    dn_def = dn_def.group(0) if dn_def else ""
    parti = dn_def.split("optiuni:", 1)
    dn_opt = re.findall(r'\["([^"]*)",', parti[1]) if len(parti) == 2 else None
    dn_neales = re.search(r"\bneales: ", dn_def) is not None
    starts = list(re.finditer(r'cheie: "([^"]+)", titlu: "([^"]+)", ruta: "([^"]+)"', js))
    for k, m in enumerate(starts):
        corp = js[m.end():(starts[k + 1].start() if k + 1 < len(starts) else len(js))]
        multi = re.match(r'\s*,\s*multi: "(\w+)"', corp)
        corp = corp.split("subcampuri:")[0]
        poz = [x.start() for x in re.finditer(r'\b(?:C|DN)\("', corp)] + [len(corp)]
        campuri = []
        for a, b in zip(poz, poz[1:]):
            buc = corp[a:b]
            m_c = re.match(r'(C|DN)\("(\w+)"(?:, "[^"]*"(?:, "(\w+)")?)?', buc)
            nume, dn = m_c.group(2), m_c.group(1) == "DN"
            cm = re.search(r'cond: \{ camp: "(\w+)", val: (\[[^\]]*\]|"[^"]*") \}', buc)
            opt = re.search(r'optiuni: \[(.*?)\]\]', buc)
            # [C6, 07.10.2026] `DN(...)` = select Da/Nu cu „— alege —” (constructorul din operatiuni_ecran.js); `tip`/`neales`
            # se citesc, ca garda bifelor să vadă CE fel de câmp cere un DA/NU.
            campuri.append({"nume": nume, "optional": re.search(r"\boptional: true\b", buc) is not None, "cond": (cm.group(1), re.findall(r'"([^"]*)"', cm.group(2))) if cm else None,
                            "optiuni": dn_opt if dn else (re.findall(r'\["([^"]*)",', opt.group(1) + "]") if opt else None),
                            "tip": ("select" if dn_opt else "?") if dn else (m_c.group(3) or "numar"),
                            "neales": dn_neales if dn else re.search(r"\bneales: ", buc) is not None})
        if multi:   # cheia `multi` e lista de rânduri, completată din subcâmpuri
            campuri.append({"nume": multi.group(1), "optional": False, "cond": None, "optiuni": None, "tip": "multi", "neales": False})
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

#: valorile pe care `uc_comun.bifa` le înțelege — orice altă opțiune a unui select DA/NU ar fi refuzată de server
BIFA_VALORI = {"true", "false", "1", "0", "da", "nu"}


def bife_nerespectate(js, main, uc):
    out = []
    for _cheie, ruta, campuri in formulare(js):
        src = functie_uc(ruta, main, uc)
        if not src:
            continue
        dupa_nume = {c["nume"]: c for c in campuri}
        for b in sorted(set(re.findall(r'bifa\(corp, "(\w+)"', src))):
            c = dupa_nume.get(b)
            if c is None:
                out.append((ruta, b, "lipsește din formular — serverul pune implicitul fără ca omul să fi ales"))
            elif c["tip"] != "select":
                out.append((ruta, b, "e câmp „%s”, nu DA/NU" % c["tip"]))
            elif c["optional"] or not c["neales"]:
                out.append((ruta, b, "DA/NU fără „— alege —” obligatoriu (preselectat sau opțional)"))
            elif not set(c["optiuni"] or []) <= BIFA_VALORI:
                out.append((ruta, b, "opțiuni pe care `bifa` le refuză: %s" % sorted(set(c["optiuni"]) - BIFA_VALORI)))
    return out


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
    (('    DN("imputabil", "Imputabil", { ', '    C("imputabil", "Imputabil", "select", { optiuni: [["true","Da"],["false","Nu"]], '),
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


#: [07.10.2026] Cheile OPȚIONALE (`corp.get`) pe care rutele Operațiunilor le citesc și formularul nu le are — fiecare primește pe
#: server implicitul ei. Unele sunt calea API, intenționat (EXCEPTII sus); care intră în ecran e DECIZIE DE PRODUS (DECIZII
#: 07.10.2026, „C5 și C6”). Ratchet în AMBELE sensuri: o cheie nouă fără câmp pică; una care primește câmp se scoate de aici.
CHEI_OPTIONALE_FARA_CAMP_07_10 = {
    "achizitie-agricultor:agricultor", "achizitie-necorporala:cod", "decontare-valuta:cont_banca", "export-extracomunitar:cont_venit",
    "nota-asociati:cu_plata", "nota-asociati:dobanda", "nota-credit:comision", "nota-credit:dobanda_angajata",
    "nota-decont-deplasare:curs", "nota-decont-deplasare:diurna_bugetara", "nota-inventariere:vinovat",
    "nota-leasing:cont_cheltuiala", "nota-lichidare:cont_amortizare", "nota-lichidare:cont_imobilizare",
    "nota-ong:sursa", "nota-productie:coef_348", "nota-provizion:cont_ajustare",
    "nota-sgr:catre", "nota-sgr:garantii_returnate", "nota-sgr:tarif_gestionare", "nota-sponsorizare:beneficiar_in_registru",
    "nota-subventie:cont_venit", "reevaluare-imobilizare:pierdere_655_anterioara", "reevaluare-imobilizare:sold_105_activ",
    "vanzare-aur-investitii:an_emisie", "vanzare-aur-investitii:optiune_taxare", "vanzare-aur-investitii:pret_unitar",
    "vanzare-aur-investitii:valoare_aur", "vanzare-ic:cont_venit", "vanzare-marja-turism:intermediar",
    "vanzare-marja-turism:locuri", "vanzare-marja-turism:optiune_normal", "vanzare-marja-turism:tva_inclus",
}


def chei_optionale_fara_camp(js, main, uc):
    out = set()
    for _cheie, ruta, campuri in formulare(js):
        src = functie_uc(ruta, main, uc)
        if src:
            citite = set(re.findall(r'corp\.get\("(\w+)"', src)) | set(re.findall(r'bifa\(corp, "(\w+)"', src))
            out |= {"%s:%s" % (ruta, k) for k in citite - {c["nume"] for c in campuri}}
    return out


def test_cheile_optionale_fara_camp_nu_cresc():
    """MUTAȚIE: „Zile de la scadență” scos din formularul provizionului -> `nota-provizion:zile_depasire` apare -> pică."""
    acum = chei_optionale_fara_camp(_citeste("static/js/ecrane/operatiuni_ecran.js"), _citeste("main.py"), _citeste("core/uc_tenants.py"))
    assert sorted(acum - CHEI_OPTIONALE_FARA_CAMP_07_10) == [], "cheie citită de server, fără câmp în formular"
    assert sorted(CHEI_OPTIONALE_FARA_CAMP_07_10 - acum) == [], "cheie care are acum câmp: scoate-o din listă"
