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
    """{(metoda, cale): nod} — din decoratorii `@app.<metoda>("<cale>")`.

    [P7 · valul use-case] Nodul intors e PROIECTIA rutei: antetul portii din `main.py` (decorator,
    parametri) cu corpul muncii din `core/uc_*.py`. Fara asta, sonda de evidenta ar citi invelisul
    si ar raporta ca doua rute nu mai produc evidenta — cand ele o produc, in alt fisier.
    """
    from core import scan_sql_efectiv as _ef
    arb = _ef.arbore_aplicatie()
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
    noduri = list(ast.walk(fn))
    for sursa_repo in _surse_repository(fn):
        try:
            noduri += list(ast.walk(ast.parse(sursa_repo)))
        except SyntaxError:
            pass
    for n in noduri:
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


_REPO = {}


def _surse_repository(fn):
    """Sursele funcțiilor de repository chemate direct de rută.

    [P7 · V1+V2, 13.09.2026] Instrucțiunile au plecat sub stratul HTTP; întrebarea sondei e despre
    ce PRODUCE ruta, nu despre unde stă textul. Un nivel, nu mai mult.
    """
    if not _REPO:
        baza = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "core")
        for f in sorted(os.listdir(baza)):
            if not (f.startswith("repo_") or f == "tranzactie.py") or not f.endswith(".py"):
                continue
            try:
                src = io.open(os.path.join(baza, f), encoding="utf-8").read()
                arb = ast.parse(src)
            except (OSError, SyntaxError):
                continue
            for n in ast.walk(arb):
                if isinstance(n, ast.FunctionDef):
                    _REPO[(f[:-3], n.name)] = ast.get_source_segment(src, n) or ""
    out = []
    for c in ast.walk(fn):
        if (isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute)
                and isinstance(c.func.value, ast.Name)):
            s = _REPO.get((c.func.value.id, c.func.attr))
            if s:
                out.append(s)
    return out


def atinge_credentiale(fn):
    """Ruta SCRIE într-o tabelă/câmp de credențiale ale unui sistem extern?"""
    corp = ast.unparse(fn) + "\n" + "\n".join(_surse_repository(fn))
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
