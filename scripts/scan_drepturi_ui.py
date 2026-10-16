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
        return tag_al_legarii(txt, linii_inainte, k)
    return None


def tag_al_legarii(txt, linii_inainte, k):
    """Tagul elementului legat pe rândul `k` (`linii_inainte[k]`, rândul legării): selectorul de pe rând sau din definiția
    variabilei de pe rândurile de deasupra; None dacă legătura nu se poate dovedi."""
    linie = linii_inainte[k]
    poz_legare = sum(len(x) + 1 for x in linii_inainte[:k])
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



# ── BUTOANELE DE INTRARE, recunoscute după CE DESCHID, nu după etichetă (04.10.2026) ──────────────────────────────────
# Euristica de mai sus citește eticheta („+ …”, „Adaugă…”, „Emite…”) și n-a văzut „Chei REGES”, „REGES”, „Trimite pe
# email”, „Stornează”, „Inventar”: butoane care deschid formularul unei acțiuni restrânse, rămase vizibile celui care n-o
# poate face. Treapta asta e STRUCTURALĂ: un handler de clic care construiește un element cu `data-actiune` e intrarea în
# formularul acelei acțiuni, deci elementul legat de handler poartă și el o acțiune (de regulă aceeași) sau
# `data-fara-actiune="<motiv>"`. CE NU VEDE: handlerele a căror legare de element nu se poate dovedi static (aceeași
# limită ca `element_al_apelului`; numărate în `nelegate`, cu clichet în `core/test_drepturi_ui.py`).
def _corp_handler(txt, poz):
    """(început, sfârșit) al corpului cu acolade al handlerului legat la `poz`; None pentru o funcție-săgeată fără acolade
    sau o funcție dată prin nume (`addEventListener("click", incarca)`): acolada următoare ar fi a altui cod."""
    mh = re.match(r"[^;]{0,300}?(?:=>|\))\s*\{", txt[poz:poz + 320])
    if not mh:
        return None
    i = poz + mh.end() - 1
    n = 0
    for j in range(i, min(len(txt), i + 20000)):
        if txt[j] == "{":
            n += 1
        elif txt[j] == "}":
            n -= 1
            if n == 0:
                return i, j
    return None


def intrari_in_formular_nemarcate():
    """{nemarcate: [(fișier, linie, acțiunea formularului, tag)], nelegate: [(fișier, linie)]}."""
    nemarcate, nelegate, vazute = [], [], set()
    for f in sorted(glob.glob(os.path.join(JS, "**", "*.js"), recursive=True)):
        txt = io.open(f, encoding="utf-8").read()
        rel = os.path.relpath(f, RAD)
        for m in _LEGARE.finditer(txt):
            c = _corp_handler(txt, m.end())
            if not c:
                continue
            d = re.search(r'data-actiune="([^"]+)"', txt[c[0]:c[1]])
            if not d:
                continue
            linie = txt.count("\n", 0, m.start()) + 1
            tag = element_al_apelului(txt, c[0] + d.start())
            if tag is None:
                nelegate.append((rel, linie))
            elif "data-actiune" not in tag and "data-fara-actiune" not in tag and (rel, tag) not in vazute:
                vazute.add((rel, tag))
                nemarcate.append((rel, linie, d.group(1), tag))
    return {"nemarcate": nemarcate, "nelegate": nelegate}


# ── INTRĂRILE ÎN ECRANE NUMAI-ADMINISTRATOR, prin ALTĂ FUNCȚIE (deficiența 262, 15.10.2026) ──────────────────────────────
# Instanța: „Scoate firma din portofoliu” din fereastra firmei se vedea asistentului — handlerul lui e
# `() => nav.deschide("Scoate firma", (c2) => ecranScoateFirma(c2, nav, t))`: o săgeată fără acolade, care cheamă ALTĂ funcție.
# Treapta de mai sus citește numai corpul cu acolade al handlerului, deci n-avea ce vedea. Treapta asta urmează funcțiile
# numite din handler (cele definite în același fișier și cele importate cu `import { … } from "./…"`), mai departe prin
# funcțiile chemate de ele, și strânge ACȚIUNILE ecranului: marcajele `data-actiune` și apelurile la rute care schimbă ceva
# (orice metodă în afară de GET) sau sunt restrânse. Dacă toate sunt numai ale administratorului (`cere_drept(ADMIN)` sau un
# `cere_rol` fără asistent), elementul legat de handler poartă și el acțiunea (poarta îl ascunde asistentului) sau spune de
# ce nu e una (`data-fara-actiune="<motiv>"`). Un ecran cu măcar o acțiune a asistentului (previzualizarea portalului,
# de pildă) nu se ascunde: rămâne, cu acțiunile de administrator scoase de poartă și motivul spus de ea.
# CE NU VEDE (declarat): o funcție chemată printr-o variabilă sau printr-un obiect (`NODURI[k].deschide(nav)`) nu se poate
# urma static; elementul construit cu `createElement` se recunoaște numai prin `<variabilă>.dataset.actiune = …` /
# `.dataset.faraActiune = …`; handlerele nelegabile de element se numără (`nelegate`) — gardul le cere zero.
_FUNCTIE_SUS = re.compile(r"^(?:export\s+)?(?:async\s+)?function\s*\*?\s*(\w+)\s*\(", re.M)
_FUNCTIE_IMBRICATA = re.compile(r"^[ \t]+(?:async\s+)?function\s*\*?\s*(\w+)\s*\(", re.M)
_IMPORT = re.compile(r"""import\s*\{([^}]*)\}\s*from\s*["'](\.{1,2}/[\w./-]+?\.js)""")
_CUVANT = re.compile(r"\b([A-Za-z_]\w*)\b")
# Transportul, nu un ecran: `api.js` (cererile, reînnoirea tokenului și reautentificarea peste ecran — `POST /auth/…` stă sub
# ORICE ecran, deci n-ar spune nimic despre ecranul la care duce un buton). Funcțiile lui nu se urmează.
_TRANSPORT = {"api.js"}


def _paranteza(txt, i, desc="(", inc=")"):
    """Poziția parantezei care o închide pe cea de la `i`, sau -1."""
    n = 0
    for j in range(i, min(len(txt), i + 200000)):
        if txt[j] == desc:
            n += 1
        elif txt[j] == inc:
            n -= 1
            if n == 0:
                return j
    return -1


def _corp_functiei(txt, m):
    """(început, sfârșit) al corpului `{ … }` al declarației potrivite de `m`, sau None."""
    p = _paranteza(txt, m.end() - 1)
    a = txt.find("{", p) if p > 0 else -1
    b = _paranteza(txt, a, "{", "}") if a > 0 else -1
    return (a, b) if b > 0 else None


def _functii(txt, rx=_FUNCTIE_SUS, de=0, pana=None):
    """{nume: [(început, sfârșit)]} — declarațiile `function nume(…) { … }` dintre `de` și `pana`. Pe fișier se iau numai cele de
    pe coloana 0 (de nivel superior): o funcție imbricată stă deja în textul celei care o cuprinde, iar numele ei se repetă de la
    un ecran la altul (`deseneaza`, `randeazaPrincipal`) — legate pe nume, ar fi adus în același ecran funcțiile altor ecrane."""
    out = {}
    for m in rx.finditer(txt, de, len(txt) if pana is None else pana):
        c = _corp_functiei(txt, m)
        if c:
            out.setdefault(m.group(1), []).append(c)
    return out


class _Module:
    """Fișierele JS, cu funcțiile de nivel superior și importurile lor, citite o dată; acțiunile fiecărui corp, calculate o dată."""

    def __init__(self, rx_garzi):
        self.cache, self.rx = {}, rx_garzi
        self.exact = {"%s %s" % (m, c): g for m, c, _rr, g in rx_garzi}
        self._ruta, self._directe = {}, {}

    def modul(self, cale):
        cale = os.path.normpath(cale)
        if cale not in self.cache:
            try:
                txt = io.open(cale, encoding="utf-8").read()
            except OSError:
                txt = ""
            importuri = {}
            for m in _IMPORT.finditer(txt):
                tinta = os.path.normpath(os.path.join(os.path.dirname(cale), m.group(2)))
                for nume in m.group(1).split(","):
                    bucati = nume.strip().split(" as ")
                    if bucati[0].strip():
                        importuri[bucati[-1].strip()] = (tinta, bucati[0].strip())
            self.cache[cale] = (txt, _functii(txt), importuri)
        return self.cache[cale]

    def corpuri(self, cale, nume):
        """[(fișierul, (început, sfârșit))] al funcției de nivel superior `nume`, văzute din `cale` (definită acolo sau importată)."""
        cale = os.path.normpath(cale)
        _, fn, imp = self.modul(cale)
        if nume in fn:
            return [(cale, c) for c in fn[nume]]
        if nume in imp and os.path.basename(imp[nume][0]) not in _TRANSPORT:
            tinta, orig = imp[nume]
            return [(tinta, c) for c in self.modul(tinta)[1].get(orig, [])]
        return []

    def garda(self, met, ruta):
        k = (met, ruta)
        if k not in self._ruta:
            pot = sorted([(c, g) for m, c, rr, g in self.rx if m == met and rr.match(ruta)], key=lambda p: p[0].count("{"))
            self._ruta[k] = ("%s %s" % (met, pot[0][0]), pot[0][1]) if pot else ("%s %s" % (met, ruta), None)
        return self._ruta[k]

    def directe(self, txt):
        """{„METODĂ /cale”: garda} scrise chiar în `txt`: marcajele și apelurile care nu sunt simple citiri."""
        if txt not in self._directe:
            acts = {a: self.exact.get(a) for a in declarate_in(txt)}
            for mt in _APEL.finditer(txt):
                ruta = _normalizeaza(mt.group("sir"))
                if not ruta.startswith("/"):
                    continue
                met = _metoda(mt.group("m"), mt.group("fel"), txt[mt.end():])
                a, g = self.garda(met, ruta)
                if met == "GET" and not restransa(g):
                    continue   # o citire a oricui nu e o acțiune a ecranului
                acts[a] = g
            self._directe[txt] = (acts, set(_CUVANT.findall(txt)))
        return self._directe[txt]


def actiunile_ecranului(module, cale, regiune, locale=None):
    """{„METODĂ /cale”: garda} — acțiunile la care duce `regiune` (codul unui handler), direct sau prin funcțiile pe care le
    numește, urmate până la capăt. `locale` = funcțiile imbricate vizibile din handler ({nume: [(început, sfârșit)]}, în
    fișierul `cale`). O acțiune pe o cale necunoscută (dinamică) intră cu garda None — nu e a administratorului."""
    cale = os.path.normpath(cale)
    acts, vazute, de_vazut, prima = {}, set(), [(cale, regiune)], True
    while de_vazut:
        c, txt = de_vazut.pop()
        directe, cuvinte = module.directe(txt)
        acts.update(directe)
        for nume in cuvinte:
            gasite = module.corpuri(c, nume)
            if prima and locale and nume in locale:
                gasite = gasite + [(cale, x) for x in locale[nume]]
            for c2, (a, b) in gasite:
                if (c2, a) not in vazute:
                    vazute.add((c2, a))
                    de_vazut.append((c2, module.modul(c2)[0][a:b + 1]))
        prima = False
    return acts


def doar_administrator(garda):
    """Garda refuză ORICE asistent, indiferent de bife (`cere_drept(ADMIN)`, sau `cere_rol` fără asistent)?"""
    if not garda:
        return False
    fel, val = garda
    return val == "ADMIN" if fel == "drept" else ("admin_firma" in val and "angajat" not in val)


def _regiune_legarii(txt, m):
    """(început, sfârșit) al codului handlerului: argumentele lui `addEventListener(…)`, sau corpul lui `.onclick = …`."""
    if "addEventListener" in m.group(0):
        a = txt.rfind("(", 0, m.end())
        b = _paranteza(txt, a)
        return (a, b) if b > 0 else None
    c = _corp_handler(txt, m.end())
    if c:
        return c
    b = txt.find(";", m.end())
    return (m.end(), b) if b > 0 else None


def intrari_in_ecrane_doar_admin(rad_js=None):
    """{nemarcate: [(fișier, linie, acțiunile ecranului, tag)], nelegate: [(fișier, linie, acțiunile)]} — butoanele care
    deschid (prin altă funcție) un ecran ale cărui acțiuni sunt toate numai ale administratorului, fără `data-actiune` /
    `data-fara-actiune`."""
    rad_js = rad_js or JS
    garzi = garzi_din_main()
    module = _Module([(m, c, _regex_cale(c), g) for (m, c), g in garzi.items()])
    nemarcate, nelegate = [], []
    for f in sorted(glob.glob(os.path.join(rad_js, "**", "*.js"), recursive=True)):
        txt, sus, _ = module.modul(f)
        rel = os.path.relpath(f, RAD)
        for m in _LEGARE.finditer(txt):
            reg = _regiune_legarii(txt, m)
            if not reg:
                continue
            regiune = txt[reg[0]:reg[1] + 1]
            if 'data-actiune="' in regiune:
                continue   # formularul se construiește chiar în handler: treapta `intrari_in_formular_nemarcate`
            # funcțiile imbricate din funcția de nivel superior care cuprinde legarea (`randeazaFormular` din ecranul Acces client)
            cuprinde = [c for cs in sus.values() for c in cs if c[0] < m.start() < c[1]]
            locale = _functii(txt, _FUNCTIE_IMBRICATA, cuprinde[0][0], cuprinde[0][1]) if cuprinde else None
            acts = actiunile_ecranului(module, f, regiune, locale)
            if not acts or not all(doar_administrator(g) for g in acts.values()):
                continue
            linie = txt.count("\n", 0, m.start()) + 1
            linii = txt[:m.start()].split("\n")
            k = len(linii) - 1
            capat = txt.find("\n", m.start())
            linii[k] = linii[k] + txt[m.start():capat if capat >= 0 else len(txt)]
            tag = tag_al_legarii(txt, linii, k)
            if tag is None:
                v = re.search(r"(\w+)\s*\.(?:addEventListener|onclick)", linii[k])
                # elementul construit cu `createElement`: marcajul pus pe variabilă, în cele 40 de rânduri de deasupra legării
                sus40 = txt[sum(len(x) + 1 for x in linii[:max(0, k - 40)]):m.start()]
                if v and re.search(r"\b%s\.dataset\.(?:actiune|faraActiune)\s*=" % re.escape(v.group(1)), sus40):
                    continue
                nelegate.append((rel, linie, sorted(acts)))
            elif "data-actiune" not in tag and "data-fara-actiune" not in tag:
                nemarcate.append((rel, linie, sorted(acts), tag))
    return {"nemarcate": nemarcate, "nelegate": nelegate}


if __name__ == "__main__":
    r = masoara()
    print("legate (declarate):", len(r["legate"]))
    print("LIPSĂ (apel la rută restrânsă fără data-actiune în fișier):", len(r["lipsa"]))
    for x in r["lipsa"]:
        print("  %s:%d  %s  [%s]" % (x[0], x[1], x[2], x[3][1]))
    print("nerezolvate (cale dinamică / fără rută):", len(r["nerezolvate"]))
