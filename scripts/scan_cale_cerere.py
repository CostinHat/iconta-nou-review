# -*- coding: utf-8 -*-
"""scripts/scan_cale_cerere.py — CARE RUTE pot crește cu numărul de firme, derivat din cod.

**DE CE EXISTĂ.** P3 întreabă ce anume mai crește cu N. Ca să nu măsor rutele pe care mi le
amintesc eu, lista se DERIVĂ: o rută poate crește cu numărul de firme dacă ajunge, direct sau prin
apeluri, la o funcție care enumeră portofoliul. Punctul de plecare e `auth_api.tenantii_userului` —
singura poartă prin care o cerere află „care sunt firmele utilizatorului".

**CUM.** Se parsează `main.py` și `core/*.py` cu `ast`, se construiește un graf de apeluri pe NUME
SIMPLE (același compromis ca `graf_temei` din casă: numele calificate se pierd la import-as, dar
numele simple prind și apelurile prin alias), apoi se caută închiderea tranzitivă a apelanților
semințelor. La final, funcțiile găsite se încrucișează cu decoratorii de rută FastAPI.

**CE NU VEDE, declarat** — și e important, fiindcă lista de mai jos e un PLAFON INFERIOR:
  * apeluri indirecte prin variabile (`f = tenantii_userului; f(...)`) sau `getattr`;
  * omonimii: două funcții cu același nume simplu în module diferite se contopesc, deci pot
    apărea rute care de fapt nu ating portofoliul (fals pozitiv, se vede la măsurare);
  * cereri făcute de ecran în lanț (o pagină care cheamă cinci rute) — aia se derivă din JS,
    separat, cu `--ecrane`.
"""
from __future__ import annotations

import ast
import io
import json
import os
import re
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAD)

#: SEMINȚELE — funcțiile prin care o cerere află „care sunt firmele utilizatorului".
SEMINTE = ("tenantii_userului",)

#: Porțile de autorizare care dau acces la un PORTOFOLIU (mai multe firme). Restul —
#: `cere_client`, `cere_context` — văd firmele unui client, adică una: costul lor nu crește cu N.
POARTA_PORTOFOLIU = ("cere_cabinet", "cere_rol(...)")

#: Fișierele care intră în graf.
def _fisiere():
    out = [os.path.join(RAD, "main.py")]
    core = os.path.join(RAD, "core")
    for n in sorted(os.listdir(core)):
        if n.endswith(".py") and not n.startswith("test_"):
            out.append(os.path.join(core, n))
    return out


def _nume_apel(nod):
    f = nod.func
    if isinstance(f, ast.Name):
        return f.id
    if isinstance(f, ast.Attribute):
        return f.attr
    return None


def graf():
    """`(apeluri, rute, definitii)` — cine pe cine cheamă, și ce funcție servește ce rută."""
    apeluri, rute, definitii = {}, {}, {}
    for cale in _fisiere():
        rel = os.path.relpath(cale, RAD)
        try:
            arbore = ast.parse(io.open(cale, encoding="utf-8").read())
        except SyntaxError:
            continue
        for nod in ast.walk(arbore):
            if not isinstance(nod, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            definitii.setdefault(nod.name, []).append(rel)
            chemate = apeluri.setdefault(nod.name, set())
            for sub in ast.walk(nod):
                if isinstance(sub, ast.Call):
                    n = _nume_apel(sub)
                    if n:
                        chemate.add(n)
            # POARTA DE AUTORIZARE, din argumentele implicite ale handlerului: `ctx=Depends(X)`.
            # Deosebirea NU e cosmetică — o rută de CABINET vede un portofoliu care crește cu
            # numărul de firme; una de PORTAL vede firmele unui client, adică una. A le măsura
            # împreună ar dilua exact cifra căutată.
            poarta = None
            for arg, impl in zip(nod.args.args[-len(nod.args.defaults):] if nod.args.defaults else [],
                                 nod.args.defaults):
                if (isinstance(impl, ast.Call) and getattr(impl.func, "id", None) == "Depends"
                        and impl.args):
                    a0 = impl.args[0]
                    if isinstance(a0, ast.Name):
                        poarta = a0.id
                    elif isinstance(a0, ast.Call):
                        poarta = "%s(...)" % getattr(a0.func, "id", "?")
            # decoratorii de rută: @app.get("/x") / @app.post("/x")
            for d in nod.decorator_list:
                if (isinstance(d, ast.Call) and isinstance(d.func, ast.Attribute)
                        and d.func.attr in ("get", "post", "put", "delete", "patch")
                        and d.args and isinstance(d.args[0], ast.Constant)):
                    rute.setdefault(nod.name, []).append(
                        (d.func.attr.upper(), d.args[0].value, rel, poarta))
    return apeluri, rute, definitii


def atinge_portofoliul(apeluri, seminte=SEMINTE, adancime_max=12):
    """Închiderea tranzitivă a APELANȚILOR semințelor. Întoarce `{functie: adancime}`."""
    tinte = set(seminte)
    gasit = {s: 0 for s in seminte}
    for pas in range(1, adancime_max + 1):
        noi = {f for f, chemate in apeluri.items() if chemate & tinte} - set(gasit)
        if not noi:
            break
        for f in noi:
            gasit[f] = pas
        tinte |= noi
    return gasit


def rute_care_cresc():
    """`[(metoda, cale, functie, fisier, adancime)]`, sortat. Un PLAFON INFERIOR (v. antet)."""
    apeluri, rute, _def = graf()
    ating = atinge_portofoliul(apeluri)
    out = []
    for fn, lst in rute.items():
        if fn in ating:
            for metoda, cale, fis, poarta in lst:
                out.append({"metoda": metoda, "cale": cale, "functie": fn, "fisier": fis,
                            "adancime": ating[fn], "poarta": poarta,
                            "creste_cu_N": poarta in POARTA_PORTOFOLIU})
    return sorted(out, key=lambda x: (not x["creste_cu_N"], x["cale"], x["metoda"]))


# ============================================================================
#  CE CERE ECRANUL — cealaltă față: ce rute cheamă frontendul, în lanț
# ============================================================================
_FETCH = re.compile(r"""(?:fetch|api|apiGet|apiPost)\s*\(\s*[`'"]([^`'"]+)[`'"]""")


def rute_din_ecrane(director=None):
    """`{fisier_js: [cale, ...]}` — ce cere frontendul. Derivat din apelurile de rețea din JS.

    E cealaltă față a întrebării „request path REAL": graful de mai sus spune ce POATE crește, iar
    asta spune ce se cere DE FAPT când un contabil deschide un ecran."""
    director = director or os.path.join(RAD, "static")
    out = {}
    if not os.path.isdir(director):
        return out
    for rad, _d, fisiere in os.walk(director):
        for n in sorted(fisiere):
            if not n.endswith(".js"):
                continue
            cale = os.path.join(rad, n)
            try:
                text = io.open(cale, encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            cai = sorted({c.split("?")[0] for c in _FETCH.findall(text)
                          if c.startswith("/") and not c.startswith("/static")})
            if cai:
                out[os.path.relpath(cale, RAD)] = cai
    return out


def calibreaza(verbose=True):
    """Instrumentul trebuie să vadă ȘI un apelant direct, ȘI unul indirect, ȘI să NU inventeze.

    Fără direcția a treia, un graf care ar întoarce „toate rutele" ar părea că funcționează."""
    apeluri = {
        "ruta_directa": {"tenantii_userului"},
        "ajutor": {"tenantii_userului"},
        "ruta_indirecta": {"ajutor"},
        "ruta_si_mai_indirecta": {"ruta_indirecta"},
        "ruta_fara_legatura": {"altceva", "json"},
    }
    g = atinge_portofoliul(apeluri)
    direct = "ruta_directa" in g and g["ruta_directa"] == 1
    indirect = g.get("ruta_indirecta") == 2 and g.get("ruta_si_mai_indirecta") == 3
    nu_inventeaza = "ruta_fara_legatura" not in g
    ok = direct and indirect and nu_inventeaza
    if verbose:
        print("CALIBRARE scan_cale_cerere (trei direcții):")
        print("  vede apelantul DIRECT        :", direct)
        print("  vede apelantul INDIRECT (×2) :", indirect)
        print("  NU inventează o rută străină :", nu_inventeaza)
        print("  VERDICT:", "OK" if ok else "PICAT — nicio listă de mai jos n-ar valora nimic")
    return ok, g


if __name__ == "__main__":
    ok, _ = calibreaza()
    if not ok:
        sys.exit(2)
    print()
    r = rute_care_cresc()
    cresc = [x for x in r if x["creste_cu_N"]]
    print("RUTE care ating portofoliul: %d, din care DE CABINET (cresc cu N): %d"
          % (len(r), len(cresc)))
    print()
    for x in r:
        print("  %-3s %-6s %-40s %-32s %-16s adanc %d"
              % ("N+" if x["creste_cu_N"] else "  ", x["metoda"], x["cale"], x["functie"],
                 x["poarta"] or "-", x["adancime"]))
    if "--ecrane" in sys.argv:
        print()
        ec = rute_din_ecrane()
        print("CE CER ECRANELE (%d fișiere JS cu apeluri de rețea):" % len(ec))
        for fis, cai in sorted(ec.items()):
            print("  %s" % fis)
            for c in cai:
                print("      %s" % c)
    if "--json" in sys.argv:
        cale = os.path.join(RAD, "masuratori", "post_p2", "cale_cerere.json")
        os.makedirs(os.path.dirname(cale), exist_ok=True)
        with io.open(cale, "w", encoding="utf-8", newline="") as f:
            json.dump({"rute": r, "ecrane": rute_din_ecrane()}, f,
                      ensure_ascii=False, indent=2, default=str)
        print("\nscris: %s" % cale)
