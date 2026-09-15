# -*- coding: utf-8 -*-
"""Care rute SCRIU în tabele din care se calculează cifre de declarație.

DE CE. Din cele 131 de rute care scriu fără probă în suită (`scripts/scan_rute_fara_proba.py`), nu
toate sunt la fel de grele. O rută care schimbă o preferință de ecran greșește vizibil și local; una
care schimbă un rând din care se ridică D300 greșește **într-un fișier depus la ANAF**. Subsetul
ăsta se derivă din **cod**, nu din apreciere: tabelele scrise de rută ∩ tabelele citite de
generatoarele de declarații.

CUM. Trei pași, fiecare mecanic:

1. **Ce scrie o rută.** Corpul ei real (`scan_sql_efectiv.functia` — învelișul HTTP nu e corpul),
   plus SQL-ul prin depozitul nominal, plus **un nivel** de apeluri către alte module ale
   aplicației (`mod.functie(...)` unde `mod` e un modul din `core/`). Din fiecare instrucțiune se
   iau tabelele din `INSERT INTO`, `UPDATE`, `DELETE FROM`.
2. **Ce citesc generatoarele.** Aceleași unelte, pe modulele de declarații (`core/d*.py`,
   `core/bilant.py`) — tabelele din `FROM` și `JOIN`.
3. **Intersecția**, pe nume de tabel curățat de schemă (`{schema}.facturi` → `facturi`).

UNDE E OARBĂ, scris ca să nu fie citită mai larg decât e:
  * **Un nivel de apeluri**, nu recursiv. O rută care scrie printr-un lanț de trei module apare cu
    zero tabele — deci instrumentul greșește spre **a rata**, nu spre a inventa. Câte rute ies cu
    zero tabele se **raportează** (`fara_tabele`), nu se ascunde.
  * SQL-ul construit din bucăți la rulare nu se vede. La fel `%s` în locul numelui de tabel.
  * „Tabel citit de generator" nu înseamnă „cifra depinde de rândul ăsta": un generator poate citi
    o coloană și ignora alta. Instrumentul spune **unde se ating**, nu cât de tare.
"""
from __future__ import annotations

import ast
import os
import re
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAD not in sys.path:
    sys.path.insert(0, RAD)

from core import scan_sql_efectiv as _sql  # noqa: E402
from scripts import scan_rute_fara_proba as _rute  # noqa: E402

SCRIE = re.compile(r"\b(?:insert\s+into|update|delete\s+from)\s+([a-z_{}\"\.%0-9]+)", re.I)
CITESTE = re.compile(r"\b(?:from|join)\s+([a-z_{}\"\.%0-9]+)", re.I)
# Nume care nu sunt tabele: sub-interogări, funcții, tabele temporare de CTE.
NU_E_TABEL = {"", "select", "(", "values", "unnest", "generate_series", "dual"}


def _curata(nume):
    """`{schema}.facturi` / `public.api_chei` / `\"x\".bonuri` → `facturi` / `api_chei` / `bonuri`."""
    n = (nume or "").strip().strip('"').lower()
    n = n.split("(")[0]
    if "." in n:
        n = n.rsplit(".", 1)[1]
    return n.strip('"').strip()


def _tabele(instructiuni, tipar):
    out = set()
    for s in instructiuni:
        if not isinstance(s, str):
            continue
        for m in tipar.findall(s):
            t = _curata(m)
            if t and t not in NU_E_TABEL and not t.startswith("%"):
                out.add(t)
    return out


def _module_importate(cale_rel):
    """{alias: 'core/x.py'} pentru `from core import x as y` / `from core import x`."""
    out = {}
    for n in ast.walk(_sql._arbore(cale_rel)):
        if isinstance(n, ast.ImportFrom) and (n.module or "") == "core":
            for a in n.names:
                cale = "core/%s.py" % a.name
                if os.path.exists(os.path.join(RAD, cale)):
                    out[a.asname or a.name] = cale
        elif isinstance(n, ast.Import):
            for a in n.names:
                if a.name.startswith("core."):
                    cale = a.name.replace(".", "/") + ".py"
                    if os.path.exists(os.path.join(RAD, cale)):
                        out[a.asname or a.name.split(".")[-1]] = cale
    return out


def _sql_cu_un_nivel(cale_rel, nod):
    """SQL-ul nodului + al funcțiilor chemate `modul.functie(...)`, UN nivel."""
    out = list(_sql.sql_din_nod(cale_rel, nod))
    module = _module_importate(cale_rel)
    # importurile locale (în corpul funcției) contează: use-case-urile importă des înăuntru
    for n in ast.walk(nod):
        if isinstance(n, ast.ImportFrom) and (n.module or "") == "core":
            for a in n.names:
                c = "core/%s.py" % a.name
                if os.path.exists(os.path.join(RAD, c)):
                    module[a.asname or a.name] = c
    for n in ast.walk(nod):
        if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                and isinstance(n.func.value, ast.Name)):
            cale_mod = module.get(n.func.value.id)
            if not cale_mod:
                continue
            try:
                for f in ast.walk(_sql._arbore(cale_mod)):
                    if (isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef))
                            and f.name == n.func.attr):
                        out += _sql.sql_din_nod(cale_mod, f)
            except Exception:
                pass
    return out


def scrise_de_ruta(nume_functie):
    """(tabele_scrise, unde) — sau (set(), None) dacă funcția nu se găsește cu corp."""
    try:
        cale, nod = _sql.functia(nume_functie)
    except LookupError:
        return set(), None
    return _tabele(_sql_cu_un_nivel(cale, nod), SCRIE), cale


def _module_declaratii():
    out = []
    for f in sorted(os.listdir(os.path.join(RAD, "core"))):
        if not f.endswith(".py") or f.startswith(("test_", "repo_", "scan_")):
            continue
        if re.match(r"^d\d{3}[a-z]?\.py$", f) or f in ("bilant.py",):
            out.append("core/" + f)
    return out


def citite_de_generatoare():
    """{tabel: [module de declarație care îl citesc]}."""
    harta = {}
    for cale in _module_declaratii():
        try:
            instr = _sql.sql_modul(cale)
        except Exception:
            continue
        for t in _tabele(instr, CITESTE):
            harta.setdefault(t, []).append(os.path.basename(cale)[:-3])
    return harta


def subsetul(doar_neprobate=True):
    """[(cale, metoda, functie, [tabele], [declaratii])] — rutele ale căror scrieri ating cifre."""
    citite = citite_de_generatoare()
    tinta = (_rute.nenumite(doar_suita=True) if doar_neprobate else _rute.rute())
    out, fara_tabele = [], []
    for cale, metoda, nume in tinta:
        scrise, _unde = scrise_de_ruta(nume)
        if not scrise:
            fara_tabele.append((cale, metoda, nume))
            continue
        ating = sorted(scrise & set(citite))
        if ating:
            decl = sorted({d for t in ating for d in citite[t]})
            out.append((cale, metoda, nume, ating, decl))
    return out, fara_tabele


if __name__ == "__main__":
    sub, fara = subsetul()
    citite = citite_de_generatoare()
    print("tabele citite de generatoare: %d" % len(citite))
    print("rute neprobate care scriu: %d" % len(_rute.nenumite(doar_suita=True)))
    print("  din care fara niciun tabel vazut (punct orb declarat): %d" % len(fara))
    print("SUBSET — scriu in tabele din care se calculeaza declaratii: %d" % len(sub))
    for cale, metoda, nume, tabele, decl in sub:
        print("  %-6s %-52s %-28s %s  ->  %s"
              % (metoda, cale, nume, ",".join(tabele), ",".join(decl)))
