# -*- coding: utf-8 -*-
"""scripts/scan_drepturi_ui.py — ce apeluri din interfață lovesc o rută RESTRÂNSĂ și dacă fișierul își
declară elementul care o declanșează (`data-actiune`).

DE CE. Decizia Costin 04.10.2026: *„Interfața urmează serverul: orice acțiune refuzată rolului nu se
afișează (derivat din gărzile rutelor)”.* Serverul spune, prin `GET /eu/drepturi`, ce acțiuni îi refuză
utilizatorului; interfața scoate din pagină elementele marcate `data-actiune="METODĂ /cale"`. Golul pe
care-l închide instrumentul: un buton NOU care cheamă o rută restrânsă, dar nu poartă marcajul — se
afișează asistentului și abia la clic primește refuzul. Regula, verificată de `core/test_drepturi_ui.py`:
**orice fișier JS care cheamă o rută restrânsă conține, literal, `METODĂ /cale` (șablonul din main.py).**

CE NU VEDE (limita declarată, ca să nu pară completitudine):
  - leagă apelul de FIȘIER, nu de elementul exact: dovedește că marcajul există, nu că stă pe butonul
    care face apelul. Partea asta o probează proba din browser (`frontend_test/proba_asistent_drepturi.py`);
  - căile construite dinamic (o variabilă întreagă, nu un șablon) nu se pot lega static — se NUMĂRĂ
    (`nerezolvate`) și se țin într-un clichet, nu se înghit.

Rutele și gărzile se citesc din `main.py` pe AST (fără să pornească aplicația) — `Depends(cere_drept(
_drepturi.NIVEL))` și `Depends(cere_rol(...))`. `core/test_drepturi_ui.py` confruntă citirea asta cu
derivarea vie (`core/drepturi.garzi_rute(app)`), ca cele două să nu poată diverge.
"""
import ast
import glob
import io
import os
import re

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN = os.path.join(RAD, "main.py")
JS = os.path.join(RAD, "static", "js")

METODE = ("get", "post", "put", "patch", "delete")
# Nivelurile care pot fi refuzate unui actor de cabinet (CITIRE nu se refuză niciunuia).
NIVELURI_RESTRANSE = ("PREGATI", "VALIDA", "DEPUNE", "ADMIN")


def garzi_din_main():
    """{(METODĂ, cale): ("drept", NIVEL) | ("rol", (roluri...))} — din decoratorii lui main.py."""
    arb = ast.parse(io.open(MAIN, encoding="utf-8").read())
    out = {}
    for fn in ast.walk(arb):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        rute = [(d.func.attr.upper(), d.args[0].value) for d in fn.decorator_list
                if isinstance(d, ast.Call) and isinstance(d.func, ast.Attribute)
                and isinstance(d.func.value, ast.Name) and d.func.value.id == "app"
                and d.func.attr in METODE and d.args and isinstance(d.args[0], ast.Constant)]
        if not rute:
            continue
        garda = None
        for n in ast.walk(fn.args):
            if not isinstance(n, ast.Call):
                continue
            f = getattr(n.func, "id", None) or getattr(n.func, "attr", None)
            if f == "cere_drept" and n.args and isinstance(n.args[0], ast.Attribute):
                garda = ("drept", n.args[0].attr)
            elif f == "cere_rol":
                garda = ("rol", tuple(a.value for a in n.args if isinstance(a, ast.Constant)))
        for r in rute:
            out[r] = garda
    return out


def restransa(garda):
    """Garda poate refuza unui actor de cabinet (administrator sau asistent)?"""
    if not garda:
        return False
    fel, val = garda
    if fel == "drept":
        return val in NIVELURI_RESTRANSE
    # cere_rol: restrânsă pentru cabinet dacă admite administratorul dar NU asistentul
    return "admin_firma" in val and "angajat" not in val


def _regex_cale(cale):
    """Șablonul rutei -> regex peste calea NORMALIZATĂ din JS (parametrii devin `{}`)."""
    bucati = re.split(r"\{[^}]+\}", cale)
    return re.compile("^" + r"(?:\{\})".join(re.escape(b) for b in bucati) + "$")


_APEL = re.compile(
    r"""(?P<fel>api\.(?P<m>get|post|put|del|patch)|cereBlob|descarca|deschide|cereForm|fetch)\(\s*"""
    r"""(?P<sir>`[^`]*`|"[^"\n]*"(?:\s*\+\s*[\w.()\[\]]+\s*\+\s*"[^"\n]*")*|'[^'\n]*')""")


def _normalizeaza(sir):
    s = sir[1:-1] if sir[0] in "`'" else sir
    if sir[0] == '"':                       # "a" + x + "b"  ->  a{}b
        s = re.sub(r'"\s*\+\s*[\w.()\[\]]+\s*\+\s*"', "{}", sir)[1:-1]
    s = re.sub(r"\$\{[^}]*\}", "{}", s)
    s = s.split("?", 1)[0]
    s = re.sub(r"(?<=[^/])\{\}$", "", s)     # `/jurnal${qp}` — interogarea lipită de cale, nu un segment
    s = re.sub(r"\{\}[^/]*", "{}", s)        # `${id}.pdf` ține de un singur segment
    return s


def _metoda(m, fel, rest):
    if m:
        return {"del": "DELETE"}.get(m, m.upper())
    if fel == "cereForm":
        return "POST"
    # fetch / cereBlob / descarca / deschide: metoda stă în opțiuni (`{ method: "POST" }`), implicit GET.
    # Se citește numai până la capătul apelului, ca metoda apelului URMĂTOR să nu fie luată drept a lui.
    capat = rest.find(");")
    mm = re.search(r"""(?:method|metoda)\s*:\s*["'](\w+)["']""", rest[:capat if capat >= 0 else 300][:300])
    return mm.group(1).upper() if mm else "GET"


def apeluri():
    """[(fișier_relativ, linie, METODĂ, cale_normalizată)] din static/js."""
    out = []
    for f in sorted(glob.glob(os.path.join(JS, "**", "*.js"), recursive=True)):
        txt = io.open(f, encoding="utf-8").read()
        rel = os.path.relpath(f, RAD)
        for mt in _APEL.finditer(txt):
            cale = _normalizeaza(mt.group("sir"))
            if not cale.startswith("/"):
                continue
            linie = txt.count("\n", 0, mt.start()) + 1
            out.append((rel, linie, _metoda(mt.group("m"), mt.group("fel"), txt[mt.end():]), cale))
    return out


def masoara():
    garzi = garzi_din_main()
    rx = [(m, c, _regex_cale(c), g) for (m, c), g in garzi.items()]
    texte = {}
    legate, lipsa, nerezolvate = [], [], []
    for rel, linie, m, cale in apeluri():
        potriviri = [(rm, rc, g) for rm, rc, rr, g in rx if rm == m and rr.match(cale)]
        if not potriviri:
            nerezolvate.append((rel, linie, m, cale))
            continue
        # cea mai specifică potrivire (mai puțini parametri) — `/tenants/{}/facturi` nu e `/tenants/{}`
        rm, rc, g = sorted(potriviri, key=lambda p: p[1].count("{"))[0]
        if not restransa(g):
            continue
        actiune = "%s %s" % (rm, rc)
        if rel not in texte:
            texte[rel] = declarate_in(io.open(os.path.join(RAD, rel), encoding="utf-8").read())
        rand = (rel, linie, actiune, g)
        # Potrivire EXACTĂ pe acțiunile declarate — nu subșir: „POST /tenants” e conținut în orice
        # „POST /tenants/{tenant_id}/…”, iar „GET /tipare” în „GET /tipare/ai” (prima formă a instrumentului
        # a raportat astfel legate apeluri care nu erau declarate nicăieri).
        (legate if actiune in texte[rel] else lipsa).append(rand)
    return {"garzi": garzi, "legate": legate, "lipsa": lipsa, "nerezolvate": nerezolvate}


# Unde se declară o acțiune: atributul (`data-actiune` / `data-actiune-camp`, cu `|` între mai multe, inclusiv
# în ramurile unui `${cond ? "A" : "B"}`), `dataset.actiune = "…"` și `permis("…")` — forma pentru butoanele a
# căror rută depinde de stare (blocarea / deblocarea lunii).
_DECL = re.compile(r"""data-actiune(?:-camp)?=|dataset\.actiune\s*=|permis\(""")
_ACT = re.compile(r"(?:GET|POST|PUT|PATCH|DELETE) /[^\s\"'`|]*")


def declarate_in(txt):
    """Mulțimea acțiunilor declarate EXACT într-un fișier JS.

    Declarația se citește de la marcaj până la capătul tagului (`>`) sau al instrucțiunii (`;` / rând nou), nu
    până la prima ghilimea — altfel `data-actiune="${cond ? "A" : "B"}"` și `permis(cond ? "A" : "B")` ar
    pierde a doua ramură."""
    out = set()
    for mt in _DECL.finditer(txt):
        rest = txt[mt.end():mt.end() + 600]
        capat = min([k for k in (rest.find(">"), rest.find(";"), rest.find("\n")) if k >= 0] or [len(rest)])
        out.update(a.strip() for a in _ACT.findall(rest[:capat]))
    return out


# ── LEGAREA PE ELEMENT (a doua treaptă): handlerul care CONȚINE apelul -> tagul elementului legat de el ────────
# Verificarea pe fișier nu deosebește butonul corect de altul din același fișier care declară aceeași acțiune
# (mutația care a arătat-o: marcajul scos de pe „Adaugă firma”, rămas pe „+ Adaugă firmă” — gard verde). Aici, unde
# legătura se poate DOVEDI, se cere marcajul pe ACEL element. Dovada are trei condiții, toate structurale:
#   1. apelul stă ÎNĂUNTRUL corpului handlerului (acoladele dintre legare și apel nu se închid sub nivelul ei) —
#      nu doar „deasupra lui”; o funcție chemată din mai multe butoane (ex. depunerea) NU se leagă de primul găsit;
#   2. selectorul handlerului e `#id`, `[data-x]` sau `.clasa`, scris pe linia legării sau în definiția variabilei;
#   3. tagul cu acel selector se găsește în fișier (cel mai apropiat înaintea legării).
# Ce nu se poate dovedi rămâne pe treapta fișierului și se NUMĂRĂ (`nelegate_pe_element`), nu se înghite.
_LEGARE = re.compile(r"""addEventListener\(\s*["'](?:click|change|submit)["']|\.onclick\s*=""")
_SELECTOR = re.compile(r"""querySelector(?:All)?\(\s*["'`]([^"'`]+)["'`]\s*\)""")


def _token(sel):
    sel = sel.strip()
    m = re.fullmatch(r"#([\w-]+)", sel)
    if m:
        return r'id=["\']%s["\']' % re.escape(m.group(1))
    m = re.search(r"\[(data-[\w-]+)", sel)
    if m:
        return r"%s=" % re.escape(m.group(1))
    m = re.search(r"\.([\w-]+)$", sel)
    if m:
        # granița de clasă e spațiul sau ghilimeaua, nu `\b` — cratima e graniță de cuvânt, deci `\bdec-recl\b` ar
        # potrivi și `dec-recl-suma` (prima formă a legat astfel un `<select>` de suma de lângă el)
        return r"""class=["'](?:[^"']*\s)?%s(?=[\s"'])""" % re.escape(m.group(1))
    return None


def _in_handler(txt, poz_legare, poz_apel):
    """Apelul e ÎNĂUNTRUL corpului deschis după legare? (acoladele nu revin sub nivelul de la legare)"""
    nivel, intrat = 0, False
    for ch in txt[poz_legare:poz_apel]:
        if ch == "{":
            nivel += 1
            intrat = True
        elif ch == "}":
            nivel -= 1
            # sub nivelul de la legare = am ieșit din funcția în care stă legarea: apelul e în ALTĂ funcție
            if nivel < 0 or (intrat and nivel <= 0):
                return False
    return intrat and nivel > 0


def element_al_apelului(txt, poz_apel):
    """Tagul elementului al cărui handler conține apelul, sau None dacă legătura nu se poate dovedi."""
    linii_inainte = txt[:poz_apel].split("\n")
    start = len(linii_inainte) - 1
    for k in range(start, max(-1, start - 80), -1):
        linie = linii_inainte[k]
        if not _LEGARE.search(linie):
            continue
        poz_legare = sum(len(x) + 1 for x in linii_inainte[:k])
        if not _in_handler(txt, poz_legare, poz_apel):
            continue
        m = _SELECTOR.search(linie)
        if not m:
            v = re.search(r"(\w+)\s*\.(?:addEventListener|onclick)", linie)
            if v:
                for j in range(k, max(-1, k - 40), -1):
                    # și în declarația multiplă: `const info = …, btn = corp.querySelector("#fn-salveaza")`
                    mm = re.search(r"(?:(?:const|let|var)\s+|,\s*)%s\s*=\s*[\w.]*querySelector(?:All)?\(\s*[\"'`]([^\"'`]+)"
                                   % re.escape(v.group(1)), linii_inainte[j])
                    if mm:
                        m = mm
                        break
        tok = _token(m.group(1)) if m else None
        if not tok:
            return None
        sus = txt[:poz_legare]
        gas = list(re.finditer(tok, sus))
        if not gas:
            gas = list(re.finditer(tok, txt[poz_legare:poz_legare + 6000]))
            if not gas:
                return None
            g = gas[0]
            off = poz_legare
        else:
            g = gas[-1]
            off = 0
        a = txt.rfind("<", 0, off + g.start())
        b = txt.find(">", off + g.end())
        return txt[a:b + 1] if a >= 0 and b > 0 else None
    return None


def masoara_pe_element():
    """{gresite: [(fișier, linie, acțiune, tag)], nelegate: [(fișier, linie, acțiune)]} pe apelurile restrânse."""
    r = masoara()
    gresite, nelegate = [], []
    texte = {}
    for rel, linie, act, g in r["legate"]:
        if rel not in texte:
            texte[rel] = io.open(os.path.join(RAD, rel), encoding="utf-8").read()
        txt = texte[rel]
        poz = sum(len(x) + 1 for x in txt.split("\n")[:linie - 1])
        cap = txt.find("\n", poz)
        apel = txt.find("(", poz, cap if cap > 0 else len(txt))   # începutul apelului de pe linie
        # Apelul PĂZIT chiar de `permis("<acțiunea lui>")` (pe rândul lui sau în condiția de deasupra, ≤ 400 de
        # caractere) e legat prin chiar condiția care îl face sau nu: nu există un element de ascuns.
        if any(act in declarate_in(m.group(0)) for m in re.finditer(r"permis\([^)]*\)", txt[max(0, poz - 400):cap])):
            continue
        tag = element_al_apelului(txt, apel if apel > 0 else poz)
        if tag is None:
            nelegate.append((rel, linie, act))
        elif act not in declarate_in(tag) and "permis(" not in txt[poz - 600:poz]:
            gresite.append((rel, linie, act, " ".join(tag.split())[:140]))
    return {"gresite": gresite, "nelegate": nelegate}


# ── BUTOANELE DE INTRARE într-un formular („+ Notă nouă”, „Adaugă…”, „Emite…”) ─────────────────────────────────────
# Nu cheamă singure nicio rută (deschid formularul; salvarea e cea marcată), deci treptele de mai sus nu le văd. Găsit
# pe producție: Ana, fără niciun drept, vedea „+ Notă nouă” — un editor pe care nu-l putea salva. Regula: butonul de
# intrare poartă acțiunea formularului la care duce (`data-actiune`), sau spune de ce nu e o acțiune
# (`data-fara-actiune="<motiv>"`: rând în formular, navigare, portalul clientului).
# CE NU VEDE: butoanele construite cu `createElement` (eticheta pusă prin `textContent`).
# eticheta poate sta direct după `<button>` SAU într-un element-titlu interior (opțiunile de meniu `firme-optiune`, cu
# iconiță înainte): „Emite factură” e tot o intrare într-un formular de lucru
_BUTON_CREARE = re.compile(r"<button([^>]*)>(?:\s*|(?:(?!</button>).){0,900}?-titlu\">\s*)((?:\+|Adaug|Emite)[^<]{0,60})", re.S)


def butoane_creare_nemarcate():
    out = []
    for f in sorted(glob.glob(os.path.join(JS, "**", "*.js"), recursive=True)):
        txt = io.open(f, encoding="utf-8").read()
        for mt in _BUTON_CREARE.finditer(txt):
            if "data-actiune" in mt.group(1) or "data-fara-actiune" in mt.group(1):
                continue
            out.append((os.path.relpath(f, RAD), txt.count("\n", 0, mt.start()) + 1, mt.group(2).strip()[:40]))
    return out


if __name__ == "__main__":
    r = masoara()
    print("legate (declarate):", len(r["legate"]))
    print("LIPSĂ (apel la rută restrânsă fără data-actiune în fișier):", len(r["lipsa"]))
    for x in r["lipsa"]:
        print("  %s:%d  %s  [%s]" % (x[0], x[1], x[2], x[3][1]))
    print("nerezolvate (cale dinamică / fără rută):", len(r["nerezolvate"]))
