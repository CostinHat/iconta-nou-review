# -*- coding: utf-8 -*-
"""core/scan_rol_pe_efect.py — INSTRUMENT: ce face fiecare rută, ca să se poată cere rolul după
EFECT, nu după nume.

DE CE E UN INSTRUMENT SEPARAT, nu cod în gardă. Sonda trebuie să citească **SQL**, iar SQL-ul e
text — nu există un AST al lui în codul ăsta. Un gard care caută șiruri e chiar ce interzice
clichetul 50, și pe drept: aserțiunea trebuie să stea pe structură. Separarea rezolvă amândouă —
instrumentul citește textul SQL-ului (singurul mod), iar gardul asertează pe ce întoarce el.
Același tipar ca `scan_module_nelegate` + `test_module_nelegate`.

MODURILE DE EȘEC, scrise ÎNAINTE de prima măsurătoare (interdicția 76) — răspuns la întrebarea lui
Costin, *„ce mod de eșec are un gard care verifică roluri pe nume de rută?"*:

  E1  **Lista fixă de nume.** Un gard cu o listă scrisă a rutelor „care trebuie să aibă rol" nu
      vede a 41-a rută. **Închis prin construcție**: mulțimea se DERIVĂ; lista din gardă e doar o
      AȘTEPTARE, ca să se vadă când mulțimea se schimbă.
  E2  **Rolul mutat din decorator în corp.** Un gard care citește doar `Depends(cere_rol(...))` ar
      raporta „fără rol" deși există. **Închis**: se citește și verificarea din corp.
  E3  **`cere_rol` chemat cu rol calculat**, nu literal. Nu se poate citi static. **NEÎNCHIS**, dar
      nu se înghite în nicio direcție: se întoarce `ROL_CALCULAT`, un marcaj propriu.
  E4  **Inversarea.** Un clichet pe NUMĂR ar trece dacă o rută pierde rolul și alta îl câștigă.
      Se închide în gardă, prin aserțiune pe mulțime.
  E5  **Ruta redenumită.** Cheia e calea + metoda — contractul cu exteriorul — nu numele funcției.
  E6  **Starea scrisă din PARAMETRU**, nu literal. Sonda n-o vede. **NEÎNCHIS**; cazul cunoscut
      (`salarii-contare`, de la R33) e pinat în gardă cu motivul.
"""
import ast
import io
import os
import re

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN = os.path.join(RAD, "main.py")

ROL_CALCULAT = "(ROL CALCULAT)"        # E3
ROL_DIN_CORP = "(verificat-in-corp)"   # E2
METODE = ("GET", "POST", "PUT", "PATCH", "DELETE")

# Tabele/câmpuri care sunt CREDENȚIALE ale unui sistem extern, nu date ale firmei.
SEMNE_CREDENTIALE = ("reges_chei", "spv_token", "wc_ck", "wc_cs", "api_chei")

_TABELA = "inregistrari"
_LINII = "inregistrari_linii"
_VALIDATA = "'validata'"


def _sursa():
    return io.open(MAIN, encoding="utf-8").read()


def rute():
    """{(metoda, cale): nod} — din decoratorii `@app.<metoda>("<cale>")`."""
    arb = ast.parse(_sursa())
    out = {}
    for n in ast.walk(arb):
        if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for d in n.decorator_list:
            if not (isinstance(d, ast.Call) and isinstance(d.func, ast.Attribute)
                    and isinstance(d.func.value, ast.Name) and d.func.value.id == "app"):
                continue
            if d.func.attr.upper() not in METODE:
                continue
            if d.args and isinstance(d.args[0], ast.Constant):
                out[(d.func.attr.upper(), d.args[0].value)] = n
    return out


def roluri(fn):
    """Rolurile cerute de o rută: din `Depends(cere_rol(...))` SAU verificate în corp (E2)."""
    gasite = set()
    for n in ast.walk(fn):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "cere_rol":
            for arg in n.args:
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    gasite.add(arg.value)
                else:
                    gasite.add(ROL_CALCULAT)
    if re.search(r'ctx\[[\'"]rol[\'"]\]\s*!=\s*[\'"]\w+[\'"]', ast.unparse(fn)):
        gasite.add(ROL_DIN_CORP)
    return gasite


def _sql(nod):
    if isinstance(nod, ast.Constant) and isinstance(nod.value, str):
        return nod.value
    if isinstance(nod, ast.JoinedStr):
        return "".join(str(v.value) if isinstance(v, ast.Constant) else "{}" for v in nod.values)
    if isinstance(nod, ast.BinOp):
        return _sql(nod.left) + " " + _sql(nod.right)
    return ""


def scrie_validata(fn):
    """Ruta scrie, ÎN CORPUL EI, o `inregistrari` cu status literal `validata`?

    Se sare peste `inregistrari_linii` — alt tabel, care n-are stare. Se citește doar bucata
    `VALUES (...)`, ca un `WHERE status='validata'` să nu treacă drept scriere."""
    for n in ast.walk(fn):
        if not (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                and n.func.attr in ("execute", "executemany") and n.args):
            continue
        s = _sql(n.args[0])
        if "INSERT" not in s.upper() or _TABELA not in s or _LINII in s:
            continue
        m = re.search(r"VALUES\s*\((.*?)\)", s, re.S | re.I)
        if m and _VALIDATA in m.group(1):
            return True
    return False


def atinge_credentiale(fn):
    """Ruta SCRIE într-o tabelă/câmp de credențiale ale unui sistem extern?"""
    corp = ast.unparse(fn)
    if not re.search(r"\b(INSERT|UPDATE|DELETE)\b", corp, re.I):
        return False
    return any(s in corp for s in SEMNE_CREDENTIALE)


def masoara():
    """{rute, scriu_validata, cu_credentiale, fara_rol_validata, fara_rol_credentiale}."""
    r = rute()
    sv = {k for k, fn in r.items() if k[0] != "GET" and scrie_validata(fn)}
    cc = {k for k, fn in r.items() if k[0] != "GET" and atinge_credentiale(fn)}
    return {"rute": r,
            "scriu_validata": sv,
            "cu_credentiale": cc,
            "fara_rol_validata": {k for k in sv if not roluri(r[k])},
            "fara_rol_credentiale": {k for k in cc if not roluri(r[k])}}
