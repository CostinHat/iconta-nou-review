# -*- coding: utf-8 -*-
"""scripts/scan_formulare_operatiuni.py — ce CERE ecranul Operațiuni față de ce CITEȘTE serverul. O singură implementare, două porți:
`core/test_formulare_operatiuni_campuri.py` (pytest) și regula `FAPT_FISCAL_NECERUT` din `verificator_conformitate.py`.

Regula (comanda Costin 07.10.2026, DS cap.17): „O cheie care e fapt fiscal (schimbă nota, baza sau impozitul) intră în formular,
cerută explicit, fără preselecție. O cheie strict tehnică, pentru API, rămâne în afara ecranului.”

Ce măsoară, pe fiecare formular din `REGISTRU` (`static/js/ecrane/operatiuni_ecran.js`) și use-case-ul rutei lui (`core/uc_tenants.py`):
  - `lipsuri`             — o opțiune care cere `corp["x"]` pe care formularul nu-l arată (sau îl marchează opțional) pe ramura ei;
  - `chei_fara_camp`      — o cheie citită de server (`corp.get`, `bifa`) pentru care formularul n-are câmp deloc;
  - `ascunse_pe_ramura`   — o cheie citită pe ramura `select=opțiune`, al cărei câmp e ascuns pe acea ramură;
  - `optionale`           — un câmp marcat opțional (golul lui = implicitul serverului);
  - `bife_nerespectate`   — un DA/NU citit prin `bifa` care nu e select Da/Nu obligatoriu, fără preselecție.
Cheile care rămân în afara ecranului / câmpurile care rămân opționale stau mai jos, FIECARE cu motivul ei (ratchet în ambele sensuri).
LIMITE, declarate: ramurile se văd scrise `if/elif var == "v"` (nu dispecere prin dicționare); vizibilitatea pe ramură se judecă pe
condiția directă a câmpului (un câmp condiționat de alt select se socotește vizibil).
"""
import io
import os
import re

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: (rută, select=opțiune, câmp) — o ramură care cere `corp["x"]` neatinsă din ecran, cu motivul.
EXCEPTII = {
    ("nota-inventariere", "operatie=casare", "valoare_bruta"):
        "formularul cere `mijloc_fix_id` (obligatoriu) -> ramura fără el, cu sumele date de mână, e calea API",
    ("nota-inventariere", "operatie=casare", "amortizare_cumulata"): "idem",
    ("nota-sgr", "operatie=virare", "suma"):
        "câmp comun: alternativ la nr. ambalaje la achiziție/vânzare/restituire, obligatoriu doar la virare; motorul de "
        "formulare nu are «opțional pe operație» pentru același câmp, iar refuzul rutei numește câmpul",
    ("achizitie-agricultor", "*", "agricultor"): "citit numai sub `if corp.get(\"agricultor\")` — opțional prin construcție",
}

#: [07.10.2026, comanda Costin — „Cele 33 de chei”] Chei citite de server care RĂMÂN în afara ecranului: nu schimbă nota, baza
#: sau impozitul (testul de încadrare al comenzii). Restul celor 33 au intrat în formular. O cheie nouă fără câmp pică poarta.
CHEI_IN_AFARA_ECRANULUI = {
    "achizitie-agricultor:agricultor":
        "numai text adăugat în explicația notei („- <nume>”); liniile, baza și compensația 8% nu depind de el, iar câmpul "
        "Descriere acoperă explicația",
    "achizitie-necorporala:cod":
        "codul activului în registru; când lipsește se generează `NEC-<tip>` — nu schimbă nota, baza sau amortizarea",
}

#: Chei citite pe o ramură pe care câmpul lor e ASCUNS, care rămân așa — cu motivul.
ASCUNSE_PERMISE = {
    "nota-inventariere:operatie=casare:cont_imobilizare":
        "citit numai pe calea API a casării (fără `mijloc_fix_id`); din ecran casarea alege activul din registru, iar conturile "
        "vin de acolo (C4)",
    "nota-inventariere:operatie=casare:cont_amortizare": "idem",
}

#: Câmpuri care RĂMÂN opționale: golul lor NU e o valoare pe care serverul o pune în locul omului.
OPTIONALE_PERMISE = {
    "nota-asociati:impozit_interimar":
        "cerut de server, numit, exact când e nevoie (interimarele depășesc dividendul anual); altfel nu intră în notă",
    "nota-sgr:nr_ambalaje": "pereche alternativă cu `suma` (una din două); serverul refuză numit dacă lipsesc amândouă",
    "nota-sgr:suma": "idem (la virare e obligatorie — EXCEPTII)",
    "achizitie-neinregistrat:numar":
        "numărul documentului (borderou); când lipsește se numerotează `BORDEROU-<dată>` — nu schimbă nota, baza sau impozitul",
    "achizitie-ic:furnizor_nume": "numele furnizorului; identitatea fiscală e codul de TVA (obligatoriu)",
}


def _citeste(p):
    return io.open(os.path.join(RAD, p), encoding="utf-8").read()


def motor_fara_preselectie(js):
    """Motorul formularului pune „— alege —” pe ORICE select obligatoriu? Se citește din codul lui, nu se presupune."""
    return re.search(r'const gol = c\.optional \? \'<option value="">-</option>\'\s*:\s*`<option value="" selected>\$\{esc\(c\.neales \|\| "— alege —"\)\}</option>`;', js) is not None


def formulare(js):
    """(cheie, rută, câmpuri) pentru fiecare formular. Un câmp: nume, cheia trimisă (`trimiteCa`), opțional, cond, opțiuni,
    tip, neales. `DN(...)` se citește din DEFINIȚIA lui în ecran (nu se presupune), iar „— alege —” al unui select obligatoriu
    din codul MOTORULUI (`motor_fara_preselectie`). Blocul `multi` e un câmp (cu `multiCond`)."""
    motor = motor_fara_preselectie(js)
    dn_def = re.search(r'const DN = [^\n]*', js)
    dn_def = dn_def.group(0) if dn_def else ""
    parti = dn_def.split("optiuni:", 1)
    dn_opt = re.findall(r'\["([^"]*)",', parti[1]) if len(parti) == 2 else None
    dn_neales = re.search(r"\bneales: ", dn_def) is not None
    starts = list(re.finditer(r'cheie: "([^"]+)", titlu: "([^"]+)", ruta: "([^"]+)"', js))
    for k, m in enumerate(starts):
        corp = js[m.end():(starts[k + 1].start() if k + 1 < len(starts) else len(js))]
        antet = corp.split("campuri:")[0]
        multi = re.search(r'\bmulti: "(\w+)"', antet)
        mcond = re.search(r'multiCond: \{ camp: "(\w+)", val: (\[[^\]]*\]|"[^"]*") \}', antet)
        corp = corp.split("subcampuri:")[0]
        poz = [x.start() for x in re.finditer(r'\b(?:C|DN)\("', corp)] + [len(corp)]
        campuri = []
        for a, b in zip(poz, poz[1:]):
            buc = corp[a:b]
            m_c = re.match(r'(C|DN)\("(\w+)"(?:, "[^"]*"(?:, "(\w+)")?)?', buc)
            nume, dn = m_c.group(2), m_c.group(1) == "DN"
            cm = re.search(r'cond: \{ camp: "(\w+)", val: (\[[^\]]*\]|"[^"]*") \}', buc)
            opt = re.search(r'optiuni: \[(.*?)\]\]', buc)
            tc = re.search(r'trimiteCa: "(\w+)"', buc)
            campuri.append({"nume": nume, "cheie": tc.group(1) if tc else nume,
                            "optional": re.search(r"\boptional: true\b", buc) is not None,
                            "cond": (cm.group(1), re.findall(r'"([^"]*)"', cm.group(2))) if cm else None,
                            "optiuni": dn_opt if dn else (re.findall(r'\["([^"]*)",', opt.group(1) + "]") if opt else None),
                            "tip": ("select" if dn_opt else "?") if dn else (m_c.group(3) or "numar"),
                            "neales": dn_neales if dn else (re.search(r"\bneales: ", buc) is not None or motor)})
        if multi:   # cheia `multi` e lista de rânduri, completată din subcâmpuri
            campuri.append({"nume": multi.group(1), "cheie": multi.group(1), "optional": False,
                            "cond": (mcond.group(1), re.findall(r'"([^"]*)"', mcond.group(2))) if mcond else None,
                            "optiuni": None, "tip": "multi", "neales": False})
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
    câmp — `cota_ceruta(corp)` / `cota_ceruta({**corp, …})` cere `cota`; `cere_cont(…corp.get("x"), "x")` FĂRĂ implicit cere `x`."""
    c = set(re.findall(r'corp\["(\w+)"\]', cod))
    if re.search(r"cota_ceruta\((?:\{\*\*)?corp\b", cod):
        c.add("cota")
    c |= set(re.findall(r'cere_cont\(conn, schema, corp\.get\("(\w+)"\), "\w+"\)', cod))
    return c - {"data"}


def citite_optional(cod):
    return set(re.findall(r'corp\.get\("(\w+)"', cod)) | set(re.findall(r'bifa\(corp, "(\w+)"', cod))


def _surse():
    return _citeste("static/js/ecrane/operatiuni_ecran.js"), _citeste("main.py"), _citeste("core/uc_tenants.py")


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
                vizibile = {c["cheie"] for c in campuri
                            if c["cond"] is None or c["cond"][0] != sel["nume"] or val in c["cond"][1]}
                optionale = {c["cheie"] for c in campuri if c["optional"]}
                for x in sorted(cerute & vizibile & optionale):
                    if (ruta, "%s=%s" % (sel["nume"], val), x) not in EXCEPTII:
                        out.append((ruta, sel["nume"], val, x, "optional"))
                for x in sorted(cerute - vizibile):
                    if (ruta, "%s=%s" % (sel["nume"], val), x) in EXCEPTII:
                        continue
                    out.append((ruta, sel["nume"], val, x, "lipsa"))
        if not ramificat:   # formular cu o singură operație: tot corpul rutei
            for x in sorted(cerute_in(src) & {c["cheie"] for c in campuri if c["optional"]}):
                if (ruta, "*", x) not in EXCEPTII:
                    out.append((ruta, None, None, x, "optional"))
            for x in sorted(cerute_in(src) - {c["cheie"] for c in campuri}):
                if (ruta, "*", x) not in EXCEPTII:
                    out.append((ruta, None, None, x, "lipsa"))
    return out


def chei_fara_camp(js, main, uc):
    out = set()
    for _cheie, ruta, campuri in formulare(js):
        src = functie_uc(ruta, main, uc)
        if src:
            out |= {"%s:%s" % (ruta, k) for k in citite_optional(src) - {c["cheie"] for c in campuri}}
    return out


def ascunse_pe_ramura(js, main, uc):
    out = set()
    for _cheie, ruta, campuri in formulare(js):
        src = functie_uc(ruta, main, uc)
        if not src:
            continue
        chei = {c["cheie"] for c in campuri}
        for sel in (c for c in campuri if c["optiuni"]):
            vm = re.search(r'(\w+) = corp\.get\("%s"' % sel["nume"], src)
            if not vm:
                continue
            for val in sel["optiuni"]:
                br = ramura(src, vm.group(1), val)
                if br is None:
                    continue
                viz = {c["cheie"] for c in campuri if c["cond"] is None or c["cond"][0] != sel["nume"] or val in c["cond"][1]}
                out |= {"%s:%s=%s:%s" % (ruta, sel["nume"], val, k) for k in (citite_optional(br) & chei) - viz}
    return out


def optionale(js):
    return {"%s:%s" % (ruta, c["cheie"]) for _k, ruta, cs in formulare(js) for c in cs
            if c["optional"] and c["cheie"] != "descriere"}


#: valorile pe care `uc_comun.bifa` le înțelege — orice altă opțiune a unui select DA/NU ar fi refuzată de server
BIFA_VALORI = {"true", "false", "1", "0", "da", "nu"}


def bife_nerespectate(js, main, uc):
    out = []
    for _cheie, ruta, campuri in formulare(js):
        src = functie_uc(ruta, main, uc)
        if not src:
            continue
        dupa_cheie = {c["cheie"]: c for c in campuri}
        for b in sorted(set(re.findall(r'bifa\(corp, "(\w+)"', src))):
            c = dupa_cheie.get(b)
            if c is None:
                out.append((ruta, b, "lipsește din formular — serverul pune implicitul fără ca omul să fi ales"))
            elif c["tip"] != "select":
                out.append((ruta, b, "e câmp „%s”, nu DA/NU" % c["tip"]))
            elif c["optional"] or not c["neales"]:
                out.append((ruta, b, "DA/NU fără „— alege —” obligatoriu (preselectat sau opțional)"))
            elif not set(c["optiuni"] or []) <= BIFA_VALORI:
                out.append((ruta, b, "opțiuni pe care `bifa` le refuză: %s" % sorted(set(c["optiuni"]) - BIFA_VALORI)))
    return out


def selecturi_preselectate(js):
    """Un select OBLIGATORIU fără „— alege —” vine cu prima opțiune aleasă — o preselecție tacită (DS cap.17)."""
    return {"%s:%s" % (ruta, c["cheie"]) for _k, ruta, cs in formulare(js) for c in cs
            if c["tip"] == "select" and not c["optional"] and not c["neales"]}


def masoara():
    """Încălcările regulii, pentru verificator: [(rută:cheie, ce)]. Goală = conform."""
    js, main, uc = _surse()
    out = []
    for k in sorted(chei_fara_camp(js, main, uc) - set(CHEI_IN_AFARA_ECRANULUI)):
        out.append((k, "cheie citită de server, fără câmp în formular"))
    for k in sorted(ascunse_pe_ramura(js, main, uc) - set(ASCUNSE_PERMISE)):
        out.append((k, "cheie citită pe ramură, câmp ascuns pe ea"))
    for k in sorted(optionale(js) - set(OPTIONALE_PERMISE)):
        out.append((k, "câmp opțional: golul lui = implicitul serverului"))
    for r, b, ce in bife_nerespectate(js, main, uc):
        out.append(("%s:%s" % (r, b), ce))
    for k in sorted(selecturi_preselectate(js)):
        out.append((k, "select obligatoriu cu prima opțiune aleasă de ecran (preselecție tacită)"))
    return out


if __name__ == "__main__":
    for k, ce in masoara():
        print("%-55s %s" % (k, ce))
