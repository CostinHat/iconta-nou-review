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

# [D10, 18.09.2026] `ON CONFLICT ... DO UPDATE SET col=...` -> `update SET` prinde `set` ca tabel fals;
# la fel `tenant_pontaj_set` da `{'set','pontaj'}`. `set` e în `NU_E_TABEL`, deci se filtrează DUPĂ
# potrivire (nu în regex, unde un lookahead ar consuma spațiul și ar rupe `UPDATE tabel`).
SCRIE = re.compile(r"\b(?:insert\s+into|update|delete\s+from)\s+([a-z_{}\"\.%0-9]+)", re.I)
# [D10] `FROM` din `EXTRACT(... FROM data_pif)` e în paranteză de funcție -> se exclude prin negative
# lookbehind pe `extract(` (aproximativ: orice `(` de funcție care conține FROM). Aici, mai simplu:
# lista `NU_E_TABEL` prinde cuvintele-cheie SQL care nu sunt tabele.
CITESTE = re.compile(r"\b(?:from|join)\s+([a-z_{}\"\.%0-9]+)", re.I)
# Numere/cuvinte care nu sunt tabele: sub-interogări, funcții, tabele temporare de CTE, `SET`
# (din DO UPDATE SET), și numele de câmp de dată prinse fals de `EXTRACT(YEAR FROM ...)`.
NU_E_TABEL = {"", "select", "(", "values", "unnest", "generate_series", "dual", "set"}


def _curata(nume):
    """`{schema}.facturi` / `public.api_chei` / `\"x\".bonuri` → `facturi` / `api_chei` / `bonuri`."""
    n = (nume or "").strip().strip('"').lower()
    n = n.split("(")[0]
    if "." in n:
        n = n.rsplit(".", 1)[1]
    return n.strip('"').strip()


_EXTRACT = re.compile(r"extract\s*\([^)]*\)", re.I)


def _tabele(instructiuni, tipar):
    out = set()
    for s in instructiuni:
        if not isinstance(s, str):
            continue
        # [D10] `EXTRACT(YEAR FROM data_pif)` -> `FROM data_pif` NU e tabel; se scoate expresia
        # EXTRACT înainte de potrivire (FROM-ul din paranteza funcției de dată e argument, nu tabel).
        s = _EXTRACT.sub(" ", s)
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


_ADANCIME_MAX = 6


def _apeluri_modul(cale_rel, nod):
    """{alias: 'core/x.py'} — importuri de modul `core`, la nivel de MODUL (`_module_importate`) plus
    cele LOCALE din corpul nodului (use-case-urile importă des înăuntru)."""
    module = dict(_module_importate(cale_rel))
    for n in ast.walk(nod):
        if isinstance(n, ast.ImportFrom) and (n.module or "") == "core":
            for a in n.names:
                c = "core/%s.py" % a.name
                if os.path.exists(os.path.join(RAD, c)):
                    module[a.asname or a.name] = c
    return module


def _sql_recursiv(cale_rel, nod, _vazute=None, _adancime=0):
    """SQL-ul nodului + al funcțiilor chemate `modul.functie(...)`, RECURSIV până la `_ADANCIME_MAX`
    nivele (D1, 18.09.2026). Înainte se urmărea UN singur nivel, iar o rută care scrie printr-un lanț
    de două-trei module (`wc_sinc` -> `woocommerce.sincronizeaza` -> `facturi_api.emite_factura` ->
    facturi/factura_linii) ieșea cu ZERO tabele și cădea din subsetul fiscal. Ciclurile se opresc prin
    `_vazute` (pereche (modul, funcție)); adâncimea e plafonată ca să nu se blocheze pe recursii lungi."""
    if _vazute is None:
        _vazute = set()
    out = list(_sql.sql_din_nod(cale_rel, nod))
    if _adancime >= _ADANCIME_MAX:
        return out
    module = _apeluri_modul(cale_rel, nod)
    for n in ast.walk(nod):
        if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                and isinstance(n.func.value, ast.Name)):
            cale_mod = module.get(n.func.value.id)
            if not cale_mod:
                continue
            cheie = (cale_mod, n.func.attr)
            if cheie in _vazute:
                continue
            _vazute.add(cheie)
            try:
                for f in ast.walk(_sql._arbore(cale_mod)):
                    if (isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef))
                            and f.name == n.func.attr):
                        out += _sql_recursiv(cale_mod, f, _vazute, _adancime + 1)
            except Exception:
                pass
    return out


# [D1, 18.09.2026] Rute care scriu în tabele de declarație printr-un dispatch pe care analiza STATICĂ
# nu-l poate urmări: modulul care face SQL-ul e PASAT CA PARAMETRU (`wc_sinc` -> `_wc.sincronizeaza`
# -> `_importa(facturi_api, ...)` -> `facturi_api.emite_factura`), sau se alege dinamic. Recursia
# `_sql_recursiv` urmărește `mod.functie(...)` prin importuri, dar nu poate rezolva un modul primit ca
# argument — ar cere analiză de flux de date. Declarate explicit, cu tabelele reale, ca subsetul să nu
# le RATEZE tăcut. *Scris ca să fie o alegere, nu o omisiune.* Confruntat cu sursa 18.09.2026.
_SCRIERI_INDIRECTE = {
    "wc_sinc": {"facturi", "factura_linii"},          # _importa(facturi_api) -> emite_factura
    "stocuri_descarcare": {"inregistrari", "inregistrari_linii"},  # descarca_luna -> _noteaza (SQL local)
}


def scrise_de_ruta(nume_functie):
    """(tabele_scrise, unde) — sau (set(), None) dacă funcția nu se găsește cu corp.
    Reuniunea tabelelor DERIVATE din SQL (recursiv, D1) cu cele DECLARATE pentru dispatch indirect."""
    indirecte = _SCRIERI_INDIRECTE.get(nume_functie, set())
    try:
        cale, nod = _sql.functia(nume_functie)
    except LookupError:
        return (set(indirecte), None) if indirecte else (set(), None)
    return _tabele(_sql_recursiv(cale, nod), SCRIE) | set(indirecte), cale


# [D2a, 18.09.2026] Sub-generatoare care NU potrivesc `^d\d{3}[a-z]?\.py$`: D406 Assets/Stocks se
# generează în `d406_active.py`/`d406_stocuri.py` (mijloace_fixe/reevaluari/miscari_stoc). Fără ele,
# tabelele alea nu intrau în `citite_de_generatoare`, iar rutele care le scriu cădeau din subset.
_GENERATOARE_EXTRA = {"d406_active.py", "d406_stocuri.py"}


def _module_declaratii():
    out = []
    for f in sorted(os.listdir(os.path.join(RAD, "core"))):
        if not f.endswith(".py") or f.startswith(("test_", "repo_", "scan_")):
            continue
        if re.match(r"^d\d{3}[a-z]?\.py$", f) or f in ("bilant.py",) or f in _GENERATOARE_EXTRA:
            out.append("core/" + f)
    return out


# [D2b, 18.09.2026] Tabele citite de generatoare printr-un DRUM pe care scanul de SQL nu-l vede:
# ori prin `FROM %s` (numele tabelului e parametru — `salariu_istoric.py:29`, orbire declarată), ori
# printr-un HELPER chemat de generator (`d112` -> `beneficii`/`pontaj`; `d406_active`/`d406_stocuri`
# construiesc SQL-ul din bucăți). Fără ele, rutele care le scriu (`salariat_beneficiu_lunar`,
# `tenant_pontaj_set`, `mijloace_import_salveaza`, `cv_transfer`, ...) cădeau TĂCUT din subsetul fiscal.
# *Scris ca să fie o alegere, nu o omisiune* — nu se pot deriva din SQL, deci se numesc, cu declarația
# care le citește. Confruntat cu sursa 18.09.2026 (d112.py:723/819/804, d300.py:1058, uc_tenants.py:5062/5092).
_CITITE_DECLARATE = {
    "beneficii_lunare": ["d112"], "pontaj": ["d112"], "salariu_istoric": ["d112"],
    "d300_manual": ["d300"], "mijloace_fixe": ["d406_active"], "reevaluari": ["d406_active"],
    "miscari_stoc": ["d406_stocuri"],
}


def citite_de_generatoare():
    """{tabel: [module de declarație care îl citesc]}. Include sursele DERIVATE din SQL + cele
    DECLARATE (`_CITITE_DECLARATE`), citite pe drumuri pe care scanul nu le vede (D2b)."""
    harta = {}
    for cale in _module_declaratii():
        try:
            instr = _sql.sql_modul(cale)
        except Exception:
            continue
        for t in _tabele(instr, CITESTE):
            harta.setdefault(t, []).append(os.path.basename(cale)[:-3])
    for t, module in _CITITE_DECLARATE.items():
        for m in module:
            if m not in harta.setdefault(t, []):
                harta[t].append(m)
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
