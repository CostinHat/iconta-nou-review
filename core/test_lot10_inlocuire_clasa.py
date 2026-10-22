# -*- coding: utf-8 -*-
"""[lotul 10, deficiența 426 — GARDUL CLASEI, CICLUL DE NECONFORMITATE pas 4] Comanda Costin 10.1 (verbatim în DECIZII „Comanda 10.1”):
„al doilea import de balanță pentru aceeași firmă o înlocuiește pe prima fără avertisment. Înainte de înlocuire: spune că există deja o
balanță, arată totalurile vechi și noi, cere confirmare […]”.

Clasa: un import de migrare care ȘTERGE sau SUPRASCRIE ce exista (`DELETE FROM …` / `ON CONFLICT … DO UPDATE` în `importa`). Gardul face
reapariția imposibilă pe trei straturi:
  1. depozitul — orice funcție `importa` dintr-un modul din `core/` care conține SQL distructiv are parametrul `inlocuieste` și cheamă
     poarta comună `migrare_api.cere_confirmarea_inlocuirii` ÎNAINTEA primei scrieri distructive (scan AST pe TOATE modulele cu `def
     importa`, nu pe o listă de nume — un import nou intră singur în scan);
  2. use-case-ul — orice apel `<modul>.importa(` din `core/uc_*.py` către un astfel de modul trimite `inlocuieste=` și traduce
     `InlocuireNeconfirmata` în `Conflict` (409); fără asta, refuzul ar ieși 422, iar ecranul n-ar deschide confirmarea;
  3. ecranul — salvarea fiecăruia în `migrare.js` trimite `inlocuieste`, iar previzualizarea folosește helperele comune (caseta cu textul
     serverului, confirmarea, 409 -> aceeași confirmare).
Premise anti-vacuu: scanul vede modulele cunoscute (cu și fără SQL distructiv) și ruta fiecăruia.

EXCEPȚII (clichet): niciuna — `core/asociati_import_api.py` (`DELETE FROM asociati` fără confirmare la corectură) a trecut și el prin
poarta comună în lotul 10. Lista trebuie să fie EXACT încălcările de azi: o excepție nouă se declară aici, cu motivul.

TEMEI: N/A — regulă de produs (comanda 10.1), gard de tooling."""
import ast
import glob
import os
import re

# ecranul se citește din ARBORELE SINTACTIC (acorn): apelul cu argumentele lui, elementul HTML cu atributele lui — nu „șirul apare în
# fișier” (core/test_garzi_pe_text.py). Uneltele sunt cele din test_lot10b_facturi.py (refolosite, nu dublate).
from core.arbore_js import apeluri, arbore_js, elemente_html, functia, noduri

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: încălcările acceptate azi, cu motivul (clichet: trebuie să fie exact încălcările găsite)
EXCEPTII = {}   # [lotul 10, 426] asociati_import_api trece acum prin poarta comună (scoasă din excepții — clichetul)
#: modulele care ÎNLOCUIESC (știute la 20.10.2026) și cele care doar ADAUGĂ (se sar la reimport) — premisa anti-vacuu a scanului
INLOCUITORI_STIUTI = {"core/solduri_api.py", "core/solduri_parteneri_api.py", "core/mijloace_fixe_import_api.py",
                      "core/istoric_declaratii_import_api.py", "core/salariati_import_api.py", "core/asociati_import_api.py"}
ADAUGATORI_STIUTI = {"core/articole_import_api.py", "core/retete_import_api.py", "core/rip_migrare_api.py"}
#: ruta de salvare din ecran a fiecărui import care înlocuiește (cheile = înlocuitorii fără excepții; un înlocuitor nou cere ruta lui)
RUTE = {"core/solduri_api.py": "/solduri`", "core/solduri_parteneri_api.py": "/parteneri`",
        "core/salariati_import_api.py": "/salariati-import`", "core/mijloace_fixe_import_api.py": "/mijloace-fixe-import`",
        "core/istoric_declaratii_import_api.py": "/istoric-declaratii-import`",
        "core/asociati_import_api.py": "/asociati-import`"}   # [lotul 10, 426] ieșit din EXCEPTII, deci cu ruta lui
PORTA = "cere_confirmarea_inlocuirii"


def _distructiv(text):
    """SQL care șterge (`DELETE FROM`) sau suprascrie (`ON CONFLICT … DO UPDATE`): pe CUVINTE consecutive, nu pe sub-șir."""
    cuv = text.upper().replace("(", " ( ").split()
    perechi = set(zip(cuv, cuv[1:]))
    return ("DELETE", "FROM") in perechi or (("ON", "CONFLICT") in perechi and ("DO", "UPDATE") in perechi)


def _nume_apel(n):
    f = n.func
    return f.attr if isinstance(f, ast.Attribute) else (f.id if isinstance(f, ast.Name) else "")


def analiza_importa(sursa):
    """-> None (modulul n-are `importa` distructiv) sau {inlocuieste: bool, poarta: linia apelului porții sau None, scriere: prima linie
    distructivă}. PURĂ (calibrată mai jos)."""
    arbore = ast.parse(sursa)
    for fn in arbore.body:
        if not (isinstance(fn, ast.FunctionDef) and fn.name == "importa"):
            continue
        scrieri = [n.lineno for n in ast.walk(fn) if isinstance(n, ast.Constant) and isinstance(n.value, str) and _distructiv(n.value)]
        if not scrieri:
            return None
        args = [a.arg for a in fn.args.args + fn.args.kwonlyargs]
        porti = [n.lineno for n in ast.walk(fn) if isinstance(n, ast.Call) and _nume_apel(n) == PORTA]
        return {"inlocuieste": {"inlocuieste"} <= set(args), "poarta": min(porti) if porti else None, "scriere": min(scrieri)}
    return None


def incalcare(a):
    """Textul încălcării pentru analiza `a`, sau None."""
    if a is None:
        return None
    if not a["inlocuieste"]:
        return "importa nu primește `inlocuieste` (confirmarea de pe ecran)"
    if a["poarta"] is None:
        return "importa nu cheamă `migrare_api.%s`" % PORTA
    if a["poarta"] > a["scriere"]:
        return "poarta (linia %d) vine DUPĂ prima scriere distructivă (linia %d)" % (a["poarta"], a["scriere"])
    return None


def _module_cu_importa():
    out = {}
    for f in sorted(glob.glob(os.path.join(RAD, "core", "*.py"))):
        rel = os.path.relpath(f, RAD)
        if os.path.basename(f).startswith("test_"):
            continue
        src = open(f, encoding="utf-8").read()
        if re.search(r"^def importa\(", src, re.M):
            out[rel] = analiza_importa(src)
    return out


def test_def_426_clasa_orice_import_care_inlocuieste_cere_confirmare():
    mod = _module_cu_importa()
    # premisa anti-vacuu: scanul vede și înlocuitorii știuți, și importurile care doar adaugă
    inlocuitori = {m for m, a in mod.items() if a is not None}
    assert INLOCUITORI_STIUTI <= inlocuitori, "scanul nu mai vede înlocuitorii știuți: %s" % sorted(INLOCUITORI_STIUTI - inlocuitori)
    assert ADAUGATORI_STIUTI <= set(mod) - inlocuitori, "scanul nu vede importurile care doar adaugă: %s" % sorted(ADAUGATORI_STIUTI)
    rele = {m: incalcare(a) for m, a in mod.items() if incalcare(a)}
    noi = {m: v for m, v in rele.items() if m not in EXCEPTII}
    # comanda 10.1: „Înainte de înlocuire: spune că există deja […], cere confirmare” — pe ORICE import care înlocuiește
    assert not noi, "import de migrare care înlocuiește fără confirmare (deficiența 426, clasa):\n  " + "\n  ".join(
        "%s: %s" % kv for kv in sorted(noi.items()))
    assert set(rele) == set(EXCEPTII), "excepție reparată — scoate-o din EXCEPTII (clichet): %s" % sorted(set(EXCEPTII) - set(rele))


def _alias_module(sursa, module):
    """{nume local -> modul} pentru `from core import x [as y]` din sursă, numai pentru `module` (căi `core/<x>.py`)."""
    out = {}
    for n in ast.walk(ast.parse(sursa)):
        if isinstance(n, ast.ImportFrom) and n.module == "core":
            for a in n.names:
                rel = "core/%s.py" % a.name
                if rel in module:
                    out[a.asname or a.name] = rel
    return out


def _nume_final(n):
    """`a.b.C` / `C` -> „C” (numele clasei prinse / ridicate), altfel None."""
    return n.attr if isinstance(n, ast.Attribute) else (n.id if isinstance(n, ast.Name) else None)


def apeluri_uc(sursa, module):
    """[(modul, funcția use-case, trimite `inlocuieste`, prinde `InlocuireNeconfirmata` -> Conflict)] pentru apelurile `<alias>.importa(`."""
    alias = _alias_module(sursa, module)
    out = []
    for fn in ast.walk(ast.parse(sursa)):
        if not isinstance(fn, ast.FunctionDef):
            continue
        # `except <…>.InlocuireNeconfirmata` al cărui corp ridică `<…>.Conflict(...)` — pe nodurile clauzei, nu pe textul ei
        prinde = any(isinstance(h, ast.ExceptHandler) and _nume_final(h.type) == "InlocuireNeconfirmata"
                     and any(isinstance(r, ast.Raise) and isinstance(r.exc, ast.Call) and _nume_final(r.exc.func) == "Conflict"
                             for r in ast.walk(h))
                     for h in ast.walk(fn))
        for c in ast.walk(fn):
            if (isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute) and c.func.attr == "importa"
                    and isinstance(c.func.value, ast.Name) and c.func.value.id in alias):
                out.append((alias[c.func.value.id], fn.name, any(k.arg == "inlocuieste" for k in c.keywords), prinde))
    return out


def test_def_426_clasa_use_case_urile_trimit_confirmarea_si_raspund_409():
    mod = _module_cu_importa()
    protejate = {m for m, a in mod.items() if a is not None}
    gasite, rele = set(), []
    for f in sorted(glob.glob(os.path.join(RAD, "core", "uc_*.py"))):
        for m, fn, trimite, prinde in apeluri_uc(open(f, encoding="utf-8").read(), protejate):
            gasite.add(m)
            if m not in EXCEPTII and not (trimite and prinde):
                rele.append("%s:%s -> %s.importa (inlocuieste=%s, 409=%s)" % (os.path.basename(f), fn, m, trimite, prinde))
    assert set(RUTE) <= gasite, "anti-vacuu: use-case-urile importurilor nu se mai văd: %s" % sorted(set(RUTE) - gasite)
    assert not rele, "use-case care nu trimite confirmarea sau nu răspunde 409 la înlocuire (426):\n  " + "\n  ".join(rele)


def test_def_426_clasa_ecranul_cere_confirmarea_la_fiecare_import_care_inlocuieste():
    mod = _module_cu_importa()
    protejate = {m for m, a in mod.items() if a is not None} - set(EXCEPTII)
    assert protejate == set(RUTE), "înlocuitor fără ruta ecranului în RUTE (sau rută moartă): %s" % sorted(protejate ^ set(RUTE))
    arb, cod = arbore_js("migrare.js")
    # helperele comune: caseta cu textul serverului, confirmarea înainte, 409 -> aceeași confirmare
    caseta = functia(arb, "_casetaInlocuire")
    assert [cod(c["test"]) for c in noduri(caseta, "ConditionalExpression")] == ["date.avertisment_inlocuire"]
    # [lotul 11, 446] zona avertismentului e goală în șablon și o umple `arataMesaj(…, "avert")` (DS cap.6: avertismentul, nu eroarea)
    assert elemente_html(caseta) == [("div", {"id": "mig-inlocuire", "role": "status"})]
    assert apeluri(functia(arb, "_arataInlocuirea"), cod, "arataMesaj") == [("z", "date.avertisment_inlocuire", '"avert"')]
    confirma = functia(arb, "_confirmaInlocuirea")
    # [446] confirmarea e întrebarea scurtă, nu încă o dată avertismentul (care stă deja sus)
    assert apeluri(confirma, cod, "_confirmaInLoculButonului") == [("zona", "esc(intrebare)", "textOk", "() => salveaza(true)")]
    assert apeluri(confirma, cod, "salveaza") == [("false",), ("true",)]   # fără avertisment: direct; cu el: numai după „da”
    la409 = functia(arb, "_inlocuire409")
    assert [cod(i["test"]) for i in noduri(la409, "IfStatement")] == ["!(e && e.cod === 409 && !inlocuieste)"]
    assert apeluri(la409, cod, "_confirmaInLoculButonului") == [("zona", 'esc(e.mesaj || "")', "textOk", "() => salveaza(true)")]
    # [446] cât confirmarea e deschisă, butonul principal e ascuns (o singură acțiune activă); „Renunță” îl readuce
    inloc = functia(arb, "_confirmaInLoculButonului")
    assert len(apeluri(inloc, cod, "confirmaCaseta")) == 1
    atribuiri = sorted(cod(a) for a in noduri(inloc, "AssignmentExpression"))
    assert atribuiri == ["buton.hidden = false", "buton.hidden = false", "buton.hidden = true"], atribuiri
    # fiecare salvare: apelul `api.post` pe ruta importului, în funcția de previzualizare de nivel superior care îl conține
    functii = [n for n in arb["body"] if n["type"] == "FunctionDeclaration"] + [
        n["declaration"] for n in arb["body"] if n["type"] == "ExportNamedDeclaration" and (n.get("declaration") or {}).get("type")
        == "FunctionDeclaration"]
    rele = []
    for m, ruta in sorted(RUTE.items()):
        post = [c for c in noduri(arb, "CallExpression") if cod(c["callee"]) == "api.post"
                and cod(c["arguments"][0]) == "`/tenants/${firma.tenant_id}%s" % ruta]
        assert len(post) == 1, "anti-vacuu: salvarea %s apare de %d ori în migrare.js" % (ruta, len(post))
        corp = post[0]["arguments"][1] if len(post[0]["arguments"]) > 1 else {}
        chei = {cod(p["key"]) for p in corp.get("properties", []) if p.get("type") == "Property"}
        gazda = [f for f in functii if f["start"] <= post[0]["start"] < f["end"]]
        assert len(gazda) == 1, (ruta, len(gazda))
        lipsa = [] if {"inlocuieste"} <= chei else ["inlocuieste în corpul cererii"]
        lipsa += [n for n in ("_casetaInlocuire", "_arataInlocuirea", "_confirmaInlocuirea", "_inlocuire409")
                  if not apeluri(gazda[0], cod, n)]
        if lipsa:
            rele.append("%s (%s): %s" % (ruta, m, ", ".join(lipsa)))
    assert not rele, "previzualizare care salvează fără confirmarea înlocuirii (426):\n  " + "\n  ".join(rele)


# ── CALIBRARE: instrumentul vede încălcarea și ramurile ei ─────────────────────────────────────────────────────────────────────
def test_CALIBRARE_scanul_vede_formele_incalcarii():
    tacut = 'def importa(conn, randuri):\n    with conn.cursor() as cur:\n        cur.execute("DELETE FROM x")\n'
    assert incalcare(analiza_importa(tacut)).startswith("importa nu primește")
    fara_poarta = 'def importa(conn, randuri, inlocuieste=False):\n    cur.execute("DELETE FROM x")\n'
    assert incalcare(analiza_importa(fara_poarta)) == "importa nu cheamă `migrare_api.cere_confirmarea_inlocuirii`"
    tarziu = ('def importa(conn, r, inlocuieste=False):\n    cur.execute("INSERT INTO x VALUES (1) ON CONFLICT (a)\\n DO UPDATE SET a=1")\n'
              '    _mig.cere_confirmarea_inlocuirii(True, inlocuieste, "t")\n')
    assert incalcare(analiza_importa(tarziu)) == "poarta (linia 3) vine DUPĂ prima scriere distructivă (linia 2)"
    bun = ('def importa(conn, r, inlocuieste=False):\n    _mig.cere_confirmarea_inlocuirii(True, inlocuieste, "t")\n'
           '    cur.execute(f"DELETE FROM {s}.x")\n')
    assert incalcare(analiza_importa(bun)) is None
    assert analiza_importa('def importa(conn, r):\n    cur.execute("INSERT INTO x VALUES (1)")\n') is None   # doar adaugă
    uc = ('from core import solduri_api as _s\nfrom core import erori as _e\n'
          'def f(d):\n    try:\n        return _s.importa(1, inlocuieste=d.inlocuieste)\n'
          '    except migrare_api.InlocuireNeconfirmata as e:\n        raise _e.Conflict(str(e))\n'
          'def g(d):\n    try:\n        return _s.importa(1)\n    except ValueError as e:\n        raise _e.DateInvalide(str(e))\n')
    assert apeluri_uc(uc, {"core/solduri_api.py"}) == [("core/solduri_api.py", "f", True, True), ("core/solduri_api.py", "g", False, False)]
