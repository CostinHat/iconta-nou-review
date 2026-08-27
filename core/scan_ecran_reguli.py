# -*- coding: utf-8 -*-
"""Instrumentul celor două reguli de ecran scrise pe 28.08.2026 — E1 (două nume distincte) și
E2 (confirmarea vizibilă). `DESIGN_SYSTEM.md` cap.26 și cap.27.

DE CE UN MODUL ȘI NU UN REGEX ÎN VERIFICATOR. Clichetul 50 (METODA §23): *o gardă asertează pe
STRUCTURĂ, nu pe text.* Amândouă regulile sunt despre **ce conține un nod** — un nod de randare la
E1, un bloc de execuție la E2 — iar `"șir" in sursă` n-are cum să spună asta: un `arataMesaj` dintr-un
comentariu arată identic cu unul apelat, iar un `<div>` dintr-un șir de ajutor arată identic cu unul
randat. Deci sursa se sparge întâi în **noduri**, și abia pe ele se asertează.

CELE DOUĂ STRUCTURI, și cât de departe merge fiecare:

  1. **Nodul de randare** (E1). Literalii de șablon (`` `...` ``) sunt HTML; se parsează cu
     `html.parser` într-un arbore de elemente cu atribute. Interpolările `${...}` se înlocuiesc cu
     `\\x01` **înainte** de parsare — altfel un `${a > b ? …}` ar rupe arborele, și l-ar rupe tăcut.
     Aserțiunea e pe **descendență**: „nodul care declară perechea conține și cele două surse, și
     nodul care numește efectul".
  2. **Blocul de execuție** (E2). Sursa se tokenizează (identificatori, punctuație, șiruri), sărind
     peste comentarii și peste **conținutul** șirurilor; blocurile `{ … }` dau un arbore de domenii.
     Aserțiunea e pe **conținutul unui bloc `try`**: dacă în el se cheamă o mutație, tot în el
     trebuie chemată o confirmare.

LIMITA, scrisă lângă gardă fiindcă METODA §23 o cere acolo unde structura nu se atinge complet:
**nu e un parser de JavaScript.** Nu construiește arbore sintactic, deci nu știe ce e o expresie și
ce e o instrucțiune; știe doar unde încep și unde se termină blocurile, și ce identificatori se
cheamă. Un `/` de împărțire luat drept început de expresie regulată ar deplasa blocurile — de aceea
regula de distincție e cea standard (după `( , = : [ ! & | ? { } ; return`), iar
`test_reguli_ecran.py` o calibrează pe amândouă formele. Ce **nu** poate: să deosebească un apel
executat de unul dintr-o ramură moartă. Asta rămâne treaba omului.
"""
import io
import os
from html.parser import HTMLParser

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ECRANE = os.path.join("static", "js", "ecrane")

# ─────────────────────────────────────────────────────────── E1: registrul perechilor
#
# O pereche = **un atribut al aceleiași entități, ținut în două locuri**. Cheia din registru e cea
# scrisă în `data-e1` pe ecran; `efect` numește sursa care produce efectul (pleacă pe hârtie, ajunge
# la client, intră în calcul), și e chiar valoarea pe care ecranul trebuie s-o poarte în
# `data-e1-efect`.
#
# R63 (cele două adrese de email ale aceleiași persoane) e scrisă ca instanță lângă regulă, în
# `DESIGN_SYSTEM.md` cap.26, dar **nu e în registrul de mai jos**, și motivul e al deciziei ei:
# acolo Costin a decis (c) — rămân două fiindcă înseamnă lucruri diferite, și trăiesc pe **două
# ecrane diferite** (portalul clientului și fișa firmei din cabinet). Regula „același nod de randare
# le arată pe amândouă" n-are ce să asereze acolo. Ce se aplică e partea de **nume distincte**, care
# nu e mecanică. Se scrie aici ca să nu pară omisiune.
PERECHI = {
    "denumire-firma": {
        "surse": {
            "portofoliu": "public.tenants.nume",
            "fiscal": '"<schema>".firma_profil.nume',
        },
        "efect": "fiscal",
        "de_ce": "pe D100, D101, D205, D301, D390, D394, D406 și pe bilanț pleacă "
                 "`firma_profil.nume` — probat 27.08.2026 pe declarații generate (R81)",
        "instanta": "R81",
    },
}

ATR_PERECHE = "data-e1"
ATR_SURSA = "data-e1-sursa"
ATR_EFECT = "data-e1-efect"
# A patra formă, și e cea care ține regula onestă. Un ecran nu are întotdeauna **amândouă**
# valorile: lista de firme vine din `GET /tenants`, care citește numai `public`, deci denumirea
# fiscală nu ajunge acolo. Regula nu cere valoarea — cere **să nu se aleagă tăcut**. Deci o sursă
# lipsă e acceptată dacă ecranul o DECLARĂ lipsă, cu `data-e1-absent`, pe nodul care spune asta în
# limba omului. Ce rămâne interzis: să nu se pomenească deloc.
ATR_ABSENT = "data-e1-absent"

# ─────────────────────────────────────────────────────────── E2: ce e act și ce e confirmare
#
# **Act** = un apel care schimbă starea unei entități pe server. Se citește ca apel de membru pe
# `api` — `api.post`, `api.put`, `api.del`, `api.patch` —, nu ca șir: un `"api.post"` scris într-un
# text de ajutor n-are voie să conteze.
MUTATII = ("post", "put", "del", "patch")

# **Domeniul**, declarat. „Act de nivel firmă" = act asupra firmei ca ENTITATE — nu asupra datelor
# din ea. Distincția nu se poate citi din forma căii: `/tenants/{}/activare` și `/tenants/{}/vector`
# arată identic, iar al doilea e o dată a firmei, nu firma. Deci se **declară**, iar declarația e
# chiar suprafața pe care a fost măsurat R82 (27.08.2026: 4 din 6 fără confirmare).
# Anti-vacuu: numărul actelor găsite pe domeniul ăsta e el însuși clichetat — o rută redenumită ar
# goli clasa, iar clichetul ar coborî la zero arătând ca o reparație.
ACTE_DE_FIRMA = (
    "/tenants",                  # creare
    "/tenants/{}",               # redenumire (PUT) și scoatere definitivă (DELETE)
    "/tenants/{}/activare",      # dezactivare / reactivare
    "/tenants/{}/nume-ales",     # alegerea de denumire (R77)
)

# Clichetele stau AICI, într-un singur loc, fiindcă le citesc doi consumatori — garda
# `core/test_reguli_ecran.py` și `verificator_conformitate.py`. Două clichete pe același lucru se
# pot despărți în tăcere; instanța din care s-a învățat asta e R62 (*regula era în două locuri și
# diferită*).
#
# **28.08.2026, măsurat cu instrumentul de mai jos:** 4 acte fără confirmare din 7. Cifra din R82
# era *4 din 6* — numărată cu mâna, pe un singur fișier. Cele patru sunt aceleași; al șaptelea act
# e `PUT /tenants/{}` din `date_firma.js`, care **confirmă**, și pe care numărătoarea de atunci nu
# l-a văzut fiindcă se uita în `firme.js`. Deci numitorul se corectează, numărătorul nu.
CLICHET_E2_FARA_CONFIRMARE = 4
CLICHET_E2_ACTE = 7

# **Confirmare** = un apel care lasă ceva pe ecran după ce actul a reușit. Cele două forme din
# aplicație: `arataMesaj(...)` (DS cap.6) și bannerele `_banner…(...)`. `nav.acasa()` **nu e**
# confirmare — demontarea ecranului arată identic cu „a reușit" și cu „s-a rupt ceva" (DS cap.27).
def e_confirmare(nume):
    return nume == "arataMesaj" or (nume.startswith("_banner") and len(nume) > 7)


# ─────────────────────────────────────────────────────────── tokenizarea
FEL_IDENT, FEL_PUNCT, FEL_SIR, FEL_SABLON = "ident", "punct", "sir", "sablon"

_IDENT0 = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_$")
_IDENTN = _IDENT0 | set("0123456789")
# Un `/` e început de expresie regulată dacă ultimul token util e unul dintre astea (regula
# standard: după ele nu poate sta un operand, deci nu poate fi împărțire).
_INAINTE_DE_REGEX = set("(,=:[!&|?{};+-*%~^<>") | {"return", "typeof", "case", "in", "of", "new",
                                                   "delete", "void", "instanceof", "do", "else"}


def tokenizeaza(js):
    """(tokens, sabloane). `tokens` = [(poz, fel, text)]; conținutul comentariilor nu produce
    token-uri, iar conținutul șirurilor stă în textul token-ului, nu în fluxul de identificatori.
    `sabloane` = [(poz, html)] — literalii de șablon, cu `${…}` înlocuit cu `\\x01`.
    """
    tokens, sabloane = [], []
    n = len(js)
    i = 0
    # stiva de contexte: ("cod",) sau ("sablon", buffer, poz_start). `${` deschide un „cod" nou
    # peste șablon; `}`-ul lui îl închide și se revine în șablon.
    stiva = [["cod", None, None, 0]]     # fel, buffer, poz, adancime_acolade
    while i < n:
        top = stiva[-1]
        c = js[i]
        if top[0] == "sablon":
            if c == "\\":
                top[1] += js[i:i + 2]     # escape-ul rămâne întreg: `ă` e text, nu structură
                i += 2
                continue
            if c == "`":
                sabloane.append((top[2], top[1]))
                tokens[top[4]] = (top[2], FEL_SABLON, top[1])
                stiva.pop()
                i += 1
                continue
            if c == "$" and i + 1 < n and js[i + 1] == "{":
                top[1] += "\x01"
                stiva.append(["cod", None, None, 0])
                i += 2
                continue
            top[1] += c
            i += 1
            continue
        # context de cod
        if c == "/" and i + 1 < n and js[i + 1] == "/":
            i = js.find("\n", i)
            if i < 0:
                break
            continue
        if c == "/" and i + 1 < n and js[i + 1] == "*":
            j = js.find("*/", i + 2)
            i = n if j < 0 else j + 2
            continue
        if c in "'\"":
            j = i + 1
            while j < n:
                if js[j] == "\\":
                    j += 2
                    continue
                if js[j] == c:
                    break
                j += 1
            tokens.append((i, FEL_SIR, js[i + 1:j]))
            i = j + 1
            continue
        if c == "`":
            # token-ul șablonului se rezervă ACUM, la poziția lui de început, ca argumentul unui
            # apel să rămână primul token de după `(` chiar dacă are interpolări înăuntru.
            tokens.append((i, FEL_SABLON, ""))
            stiva.append(["sablon", "", i, 0, len(tokens) - 1])
            i += 1
            continue
        if c == "/":
            ant = _ultimul_util(tokens)
            if ant in _INAINTE_DE_REGEX or ant is None:
                j = i + 1
                in_clasa = False
                while j < n:
                    if js[j] == "\\":
                        j += 2
                        continue
                    if js[j] == "[":
                        in_clasa = True
                    elif js[j] == "]":
                        in_clasa = False
                    elif js[j] == "/" and not in_clasa:
                        break
                    elif js[j] == "\n":
                        break
                    j += 1
                i = j + 1
                continue
            tokens.append((i, FEL_PUNCT, "/"))
            i += 1
            continue
        if c in _IDENT0:
            j = i
            while j < n and js[j] in _IDENTN:
                j += 1
            tokens.append((i, FEL_IDENT, js[i:j]))
            i = j
            continue
        if c == "{":
            top[3] += 1
            tokens.append((i, FEL_PUNCT, "{"))
            i += 1
            continue
        if c == "}":
            if top[3] == 0 and len(stiva) > 1:
                stiva.pop()          # se închide un `${…}` — se revine în șablon
                i += 1
                continue
            top[3] -= 1
            tokens.append((i, FEL_PUNCT, "}"))
            i += 1
            continue
        if c.isspace():
            i += 1
            continue
        tokens.append((i, FEL_PUNCT, c))
        i += 1
    # șabloanele care au fost tokenizate în interiorul unui `${…}` se adaugă și ele
    for t in stiva[1:]:
        if t[0] == "sablon":
            sabloane.append((t[2], t[1]))
    return tokens, sabloane


def _ultimul_util(tokens):
    if not tokens:
        return None
    _p, fel, text = tokens[-1]
    if fel == FEL_IDENT:
        return text
    if fel == FEL_PUNCT:
        return text
    return "sir"


def linia(sursa, poz):
    return sursa.count("\n", 0, poz) + 1


# ─────────────────────────────────────────────────────────── blocuri
def bloc_de_la(tokens, k):
    """Indicele token-ului `}` care închide `{`-ul de la indicele `k`. None dacă nu se închide."""
    adanc = 0
    for j in range(k, len(tokens)):
        if tokens[j][1] != FEL_PUNCT:
            continue
        if tokens[j][2] == "{":
            adanc += 1
        elif tokens[j][2] == "}":
            adanc -= 1
            if adanc == 0:
                return j
    return None


def _apeluri(tokens, a, b):
    """Numele apelate în intervalul de token-uri [a, b): un IDENT urmat de `(`, plus membrii
    `obiect.metoda(`. Un nume dintr-un comentariu sau dintr-un șir nu ajunge aici."""
    out = []
    for j in range(a, b):
        poz, fel, text = tokens[j]
        if fel != FEL_IDENT or j + 1 >= b:
            continue
        if tokens[j + 1][1] == FEL_PUNCT and tokens[j + 1][2] == "(":
            obiect = None
            if j >= 2 and tokens[j - 1][2] == "." and tokens[j - 2][1] == FEL_IDENT:
                obiect = tokens[j - 2][2]
            out.append((poz, obiect, text, j))
    return out


def _blocuri(tokens):
    """[(deschidere, inchidere, e_try)] pentru fiecare pereche `{ }` din fluxul de token-uri."""
    stiva, out = [], []
    for j, (_p, fel, text) in enumerate(tokens):
        if fel != FEL_PUNCT:
            continue
        if text == "{":
            stiva.append(j)
        elif text == "}" and stiva:
            d = stiva.pop()
            e_try = d >= 1 and tokens[d - 1][1] == FEL_IDENT and tokens[d - 1][2] == "try"
            out.append((d, j, e_try))
    return out


def ruta_normalizata(text):
    """Calea unui apel, fără interpolări și fără șirul de interogare: `/tenants/{}/activare`.
    Ce rămâne e **forma** căii — singurul lucru care se poate compara între apeluri."""
    return text.split("?")[0].replace("\x01", "{}")


def acte(sursa, domeniu):
    """Actele din `domeniu` care se cheamă în sursă, cu starea confirmării fiecăruia.

    `domeniu` — mulțimea de căi normalizate care contează. E o **declarație**, nu o deducție, și
    de asta e a apelantului: „act de nivel firmă" nu se poate citi din forma căii
    (`/tenants/{}/activare` și `/tenants/{}/vector` arată la fel), se declară.

    Întoarce [(linie, apel, ruta, confirmat, in_try)].
    """
    tokens, _sab = tokenizeaza(sursa)
    blocuri = _blocuri(tokens)
    out = []
    for poz, obiect, nume, j in _apeluri(tokens, 0, len(tokens)):
        if obiect != "api" or nume not in MUTATII:
            continue
        ruta = ruta_normalizata(_primul_argument(tokens, j))
        if ruta not in domeniu:
            continue
        # blocul care contează e cel mai interior `try` care îl cuprinde; dacă nu e niciunul, cel
        # mai interior bloc. Un act **fără** `try` se raportează ca atare — acolo nici calea de
        # eroare nu vorbește.
        cuprind = [(d, f, t) for d, f, t in blocuri if d < j < f]
        in_try = any(t for _d, _f, t in cuprind)
        alese = [(d, f) for d, f, t in cuprind if t] or [(d, f) for d, f, _t in cuprind]
        confirmat = False
        if alese:
            d, f = max(alese)
            confirmat = any(e_confirmare(m) for _p, _ob, m, _j in _apeluri(tokens, d, f))
        out.append((linia(sursa, poz), "api." + nume, ruta, confirmat, in_try))
    return out


def _primul_argument(tokens, j):
    """Textul primului argument al apelului al cărui nume stă la indicele `j`, dacă e un literal.
    Șir sau șablon; altfel „" — un argument calculat nu se poate citi static, și se spune."""
    if j + 2 < len(tokens) and tokens[j + 2][1] in (FEL_SIR, FEL_SABLON):
        return tokens[j + 2][2]
    return ""


# ─────────────────────────────────────────────────────────── arborele de randare (E1)
class _Arbore(HTMLParser):
    """Elementele unui fragment HTML, fiecare cu lista descendenților. Etichetele nu se închid
    întotdeauna în șabloanele noastre (`<br>`, `<li>` fără `</li>`), deci arborele se construiește
    tolerant: un element se închide la eticheta lui de închidere, sau la sfârșitul fragmentului."""

    def __init__(self):
        HTMLParser.__init__(self, convert_charrefs=True)
        self.radacina = {"eticheta": "#", "atr": {}, "copii": [], "poz": 0}
        self.stiva = [self.radacina]

    def handle_starttag(self, tag, attrs):
        nod = {"eticheta": tag, "atr": dict(attrs), "copii": [], "poz": self.getpos()[0]}
        self.stiva[-1]["copii"].append(nod)
        if tag not in ("br", "hr", "img", "input", "meta", "link"):
            self.stiva.append(nod)

    def handle_endtag(self, tag):
        for k in range(len(self.stiva) - 1, 0, -1):
            if self.stiva[k]["eticheta"] == tag:
                del self.stiva[k:]
                return


def arbore(html):
    p = _Arbore()
    p.feed(html)
    p.close()
    return p.radacina


def descendenti(nod):
    for c in nod["copii"]:
        yield c
        for d in descendenti(c):
            yield d


def perechi_pe_ecran(sursa):
    """Nodurile care declară o pereche E1, cu ce lipsește din fiecare.

    Întoarce [(linie, cheie, lipsuri)], unde `lipsuri` e o listă de perechi **(cod, mesaj)** —
    goală înseamnă nod conform. Codul există ca să se poată aserta pe el: o gardă care ar compara
    fraza mesajului s-ar rupe la prima reformulare, și s-ar rupe în direcția comodă (verde).
    """
    _t, sabloane = tokenizeaza(sursa)
    out = []
    for poz, html in sabloane:
        rad = arbore(html)
        for nod in descendenti(rad):
            cheie = nod["atr"].get(ATR_PERECHE)
            if cheie is None:
                continue
            ln = linia(sursa, poz) + nod["poz"] - 1
            decl = PERECHI.get(cheie)
            if decl is None:
                out.append((ln, cheie, [("nedeclarata",
                                         "ecranul declară perechea `%s`, registrul `PERECHI` n-o "
                                         "cunoaște" % cheie)]))
                continue
            surse = {d["atr"][ATR_SURSA] for d in descendenti(nod) if ATR_SURSA in d["atr"]}
            absente = {d["atr"][ATR_ABSENT] for d in descendenti(nod) if ATR_ABSENT in d["atr"]}
            efecte = {d["atr"][ATR_EFECT] for d in descendenti(nod) if ATR_EFECT in d["atr"]}
            lipsuri = []
            for s in sorted(decl["surse"]):
                if s not in surse and s not in absente:
                    lipsuri.append(("sursa-tacuta",
                                    "nu spune nimic despre sursa `%s` (%s) — nici arătată (`%s`), "
                                    "nici declarată lipsă (`%s`)"
                                    % (s, decl["surse"][s], ATR_SURSA, ATR_ABSENT)))
            if not surse:
                lipsuri.append(("fara-valoare",
                                "declară perechea și nu arată nicio valoare — atunci nodul nu e "
                                "locul unde omul vede diferența, e doar o etichetă"))
            if surse & absente:
                lipsuri.append(("dubla", "aceeași sursă e și arătată și declarată lipsă: %s"
                                % sorted(surse & absente)))
            if decl["efect"] not in efecte:
                lipsuri.append(("efect", "nu numește care sursă produce efectul (`%s=%s`)"
                                % (ATR_EFECT, decl["efect"])))
            out.append((ln, cheie, lipsuri))
    return out


def _fisiere_ecran():
    baza = os.path.join(RAD, ECRANE)
    return [os.path.join(baza, f) for f in sorted(os.listdir(baza)) if f.endswith(".js")]


def scaneaza_e1():
    """(neconforme, nerandate). `neconforme` = noduri care declară o pereche și nu o duc până la
    capăt; `nerandate` = perechi din registru pe care niciun ecran nu le mai arată — anti-vacuu:
    o pereche ștearsă din ecran ar face gardul verde fără să mai păzească nimic."""
    neconforme, vazute = [], set()
    for cale in _fisiere_ecran():
        sursa = io.open(cale, encoding="utf-8").read()
        rel = os.path.relpath(cale, RAD).replace(os.sep, "/")
        for ln, cheie, lipsuri in perechi_pe_ecran(sursa):
            if cheie in PERECHI:
                vazute.add(cheie)
            for cod, mesaj in lipsuri:
                neconforme.append((rel, ln, cheie, cod, mesaj))
    nerandate = [k for k in sorted(PERECHI) if k not in vazute]
    return neconforme, nerandate


def scaneaza_e2():
    """(fara_confirmare, toate). `toate` e anti-vacuul: dacă mulțimea de acte de nivel firmă se
    golește — o rută redenumită, un ecran rescris —, clichetul ar coborî la zero și ar arăta ca o
    reparație. Numărul actelor găsite se verifică separat, în gardă."""
    fara, toate = [], []
    for cale in _fisiere_ecran():
        sursa = io.open(cale, encoding="utf-8").read()
        rel = os.path.relpath(cale, RAD).replace(os.sep, "/")
        for ln, apel, ruta, confirmat, in_try in acte(sursa, ACTE_DE_FIRMA):
            toate.append((rel, ln, apel, ruta, confirmat, in_try))
            if not confirmat:
                fara.append((rel, ln, apel, ruta))
    return fara, toate


if __name__ == "__main__":
    nec, ner = scaneaza_e1()
    print("E1 noduri neconforme: %d" % len(nec))
    for r in nec:
        print("   ", r)
    print("E1 perechi nerandate: %s" % ner)
    fara, toate = scaneaza_e2()
    print("E2 acte de nivel firmă: %d, din care fără confirmare: %d" % (len(toate), len(fara)))
    for r in toate:
        print("   ", r)
