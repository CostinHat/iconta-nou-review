# -*- coding: utf-8 -*-
"""scripts/scan_contract_ecran.py — contractul ECRAN ↔ RUTĂ, măsurat.

De ce există. Ipoteza pusă în față: *„ecranul trimite un câmp, ruta cere altul, iar diferența
e o literă"*. Ca s-o poți confirma sau infirma, trebuie o cifră pe TOATE perechile, nu o
impresie de pe una. Instrumentul compară, pentru fiecare apel `api.post/api.put` din
`static/js/`, **cheile trimise** cu **câmpurile modelului** rutei.

CE COMPARĂ, în două direcții:
  - **CERUT ȘI NETRIMIS** — modelul are un câmp obligatoriu (fără valoare implicită) pe care
    ecranul nu-l trimite. Ăsta e defectul: ruta răspunde 422, iar omul vede un refuz.
  - **TRIMIS ȘI NECERUT** — ecranul trimite o cheie pe care modelul n-o are. Pydantic o
    **ignoră tăcut**, deci e mai rea decât un refuz: pare că merge.

CE NU VEDE, declarat, ca să nu se citească drept „zero probleme":
  - apelurile al căror corp e o **variabilă** (`api.post(url, payload)`) — se numără separat,
    ca domeniu neatins, nu ca fiind în regulă;
  - cheile **calculate** (`[cheie]: val`) și răspândirile (`...x`) — la fel;
  - rutele fără model pydantic (`corp: dict = Body(...)`) — acolo nu există contract de
    verificat, iar asta e în sine o observație: nu se poate spune ce cer;
  - **nu execută nimic** — un câmp trimis corect poate fi tot greșit ca valoare.
"""
import ast
import json
import os
import re
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JS = os.path.join(RAD, "static", "js")
MAIN = os.path.join(RAD, "main.py")

# api.post(`/cale/${x}/y`, { a: 1, b: 2 })  |  api.put("/cale", {...})
RE_APEL = re.compile(
    r"api\.(post|put)\(\s*[`\"']([^`\"']+)[`\"']\s*,\s*(\{)", re.S)


def _obiect(src, i):
    """Textul obiectului literal care începe la `{` de pe poziția i. None dacă nu se închide."""
    adanc, j, n = 0, i, len(src)
    while j < n:
        c = src[j]
        if c == "{":
            adanc += 1
        elif c == "}":
            adanc -= 1
            if adanc == 0:
                return src[i:j + 1]
        j += 1
    return None


def _chei_top(obj):
    """Cheile de PRIMUL nivel, in AMBELE forme JS.

    Prima forma a functiei vedea doar `cheie: valoare` si rata prescurtarea ES6
    (`{ an, luna }`) — care e forma cea mai des folosita in ecrane. Rezultatul: 30 de
    „diferente", din care primele trei verificate erau toate false. Interdictia 76:
    instrumentul se calibreaza pe felul in care POATE gresi, iar felul lui era exact asta.
    """
    chei, adanc, i, n = [], 0, 0, len(obj)
    astept_cheie = False
    while i < n:
        c = obj[i]
        if c in "{[(":
            adanc += 1
            astept_cheie = (adanc == 1)
            i += 1
            continue
        if c in "}])":
            adanc -= 1
            i += 1
            continue
        if adanc == 1 and c == ",":
            astept_cheie = True
            i += 1
            continue
        if adanc == 1 and astept_cheie and not c.isspace():
            m = re.match(r"([A-Za-z_$][A-Za-z0-9_$]*)\s*(:|,|\})", obj[i:])
            if m:
                chei.append(m.group(1))
            astept_cheie = False
            # sare pana la capatul valorii de la nivelul asta
            j, ad2 = i, 0
            while j < n:
                d = obj[j]
                if d in "{[(":
                    ad2 += 1
                elif d in "}])":
                    if ad2 == 0:
                        break
                    ad2 -= 1
                elif d == "," and ad2 == 0:
                    break
                elif d in "\"'`":
                    q = d
                    j += 1
                    while j < n and obj[j] != q:
                        j += 2 if obj[j] == "\\" else 1
                j += 1
            i = j
            continue
        i += 1
    return chei


def apeluri_din_ecrane():
    out, necitibile = [], []
    for rad, _, fis in os.walk(JS):
        for f in sorted(fis):
            if not f.endswith(".js"):
                continue
            cale = os.path.join(rad, f)
            src = open(cale, encoding="utf-8").read()
            rel = os.path.relpath(cale, RAD)
            for m in RE_APEL.finditer(src):
                obj = _obiect(src, m.start(3))
                if obj is None:
                    continue
                if "..." in obj:
                    necitibile.append((rel, m.group(2), "răspândire `...`"))
                    continue
                out.append({"fisier": rel, "metoda": m.group(1).upper(),
                            "url": m.group(2), "chei": sorted(set(_chei_top(obj))),
                            "linia": src[:m.start()].count("\n") + 1})
            # apeluri cu corp VARIABILA — domeniu neatins, se numara
            for m in re.finditer(r"api\.(post|put)\(\s*[`\"']([^`\"']+)[`\"']\s*,\s*([A-Za-z_]\w*)\s*\)", src):
                necitibile.append((rel, m.group(2), "corp = variabila `%s`" % m.group(3)))
    return out, necitibile


def modele_rute():
    """{(metoda, cale_normalizata): (obligatorii, toate) } din main.py."""
    src = open(MAIN, encoding="utf-8").read()
    arb = ast.parse(src)
    modele = {}
    for n in ast.walk(arb):
        if isinstance(n, ast.ClassDef) and any(
                getattr(b, "id", None) == "BaseModel" for b in n.bases):
            oblig, toate = set(), set()
            for st in n.body:
                if isinstance(st, ast.AnnAssign) and isinstance(st.target, ast.Name):
                    toate.add(st.target.id)
                    if st.value is None:
                        oblig.add(st.target.id)
            modele[n.name] = (oblig, toate)
    rute = {}
    for fn in ast.walk(arb):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        cai = [(d.func.attr, d.args[0].value) for d in fn.decorator_list
               if isinstance(d, ast.Call) and getattr(d.func, "attr", None) in ("post", "put")
               and d.args and isinstance(d.args[0], ast.Constant)]
        if not cai:
            continue
        model = None
        for a in list(fn.args.args) + list(fn.args.kwonlyargs):
            if a.annotation is not None and getattr(a.annotation, "id", None) in modele:
                model = a.annotation.id
                break
        for metoda, cale in cai:
            rute[(metoda.upper(), re.sub(r"\{[^}]+\}", "{}", cale))] = model
    return rute, modele


def normalizeaza_url(u):
    u = re.sub(r"\$\{[^}]*\}", "{}", u)
    return u.split("?")[0].rstrip("/") or "/"


def main():
    apeluri, necitibile = apeluri_din_ecrane()
    rute, modele = modele_rute()
    potrivite, fara_ruta, fara_model, diferente = 0, [], [], []
    for a in apeluri:
        cheie = (a["metoda"], normalizeaza_url(a["url"]))
        if cheie not in rute:
            fara_ruta.append(a)
            continue
        model = rute[cheie]
        if model is None:
            fara_model.append(a)
            continue
        oblig, toate = modele[model]
        potrivite += 1
        lipsa = sorted(oblig - set(a["chei"]))
        in_plus = sorted(set(a["chei"]) - toate)
        if lipsa or in_plus:
            diferente.append({**a, "model": model, "cerut_netrimis": lipsa,
                              "trimis_necerut": in_plus})
    if "--json" in sys.argv:
        print(json.dumps({"perechi": potrivite, "diferente": diferente,
                          "fara_model": len(fara_model), "fara_ruta": len(fara_ruta),
                          "necitibile": len(necitibile)}, ensure_ascii=False, indent=1))
        return 0
    print("PERECHI ecran↔rută comparabile: %d" % potrivite)
    print("  fără model pydantic (`corp: dict`), deci fără contract: %d" % len(fara_model))
    print("  apel fără rută potrivită (calc dinamic / rută dispărută): %d" % len(fara_ruta))
    print("  corp necitibil (variabilă sau răspândire): %d" % len(necitibile))
    print()
    print("DIFERENȚE: %d" % len(diferente))
    for d in diferente:
        print("  %s:%d  %s %s  [%s]" % (d["fisier"], d["linia"], d["metoda"],
                                        normalizeaza_url(d["url"]), d["model"]))
        if d["cerut_netrimis"]:
            print("      CERUT ȘI NETRIMIS : %s   <- 422 la om" % ", ".join(d["cerut_netrimis"]))
        if d["trimis_necerut"]:
            print("      TRIMIS ȘI NECERUT : %s   <- ignorat TĂCUT" % ", ".join(d["trimis_necerut"]))
    for a in fara_ruta:
        print("  (fără rută) %s:%d  %s %s" % (a["fisier"], a["linia"], a["metoda"], a["url"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
