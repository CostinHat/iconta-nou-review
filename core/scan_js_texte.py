# -*- coding: utf-8 -*-
"""SCANNER de FRAZE DE INTERFATA din JavaScript (23.08.2026) — instrumentul pentru interdictiile
29 (fraza fara cheie si loc unic), 30 (doua stari cu aceeasi eticheta) si 31 (eticheta aleasa de
cine randeaza).

DE CE EXISTA. Cinci interdictii stau nemasurate fiindca lucrul cautat traieste in `static/js/`:
37 de fisiere, 15.125 de randuri, pe care niciun instrument din proiect nu le citeste. Punctul orb
declarat la interdictia 16 e chiar asta.

CE MASOARA. Sirurile literale care ajung la OM, grupate pe textul lor normalizat. O fraza care apare
in DOUA locuri distincte n-are „loc unic" - se schimba intr-unul si ramane veche in celalalt, exact
efectul scris la 29.

────────────────────────────────────────────────────────────────────────────────────────────
CALIBRAREA NEGATIVA, SCRISA INAINTE DE PRIMA MASURATOARE (interdictia 76, aplicata INAINTE).

Interdictia 76 are patru instante si toate au fost prinse TARZIU. Aici se scrie intai pe ce moduri
poate gresi un scan care citeste JavaScript, apoi se construieste. Fiecare mod are un caz in
`core/test_scan_js_texte.py`, iar cele pe care scanul NU le acopera sunt declarate, nu tacute.

  M1  BACKTICK. `Text ${x}` nu e prins de un regex pe ghilimele. -> ACOPERIT: template literals se
      citesc, iar `${...}` se normalizeaza la un simbol, ca doua fraze identice cu variabile
      diferite sa se recunoasca.
  M2  COMENTARIU. O fraza dintr-un `//` sau `/* */` nu ajunge la om. -> ACOPERIT: comentariile se
      scot cu o masina de stari care stie ca `//` dintr-un sir NU incepe un comentariu (si invers).
      Un regex simplu greseste exact aici, pe orice URL: `https://`.
  M3  ZGOMOT. Selectoare, clase, chei, URL-uri, nume de evenimente - sunt masa sirurilor si ar
      ineca semnalul. -> ACOPERIT euristic: cere spatiu SI un cuvant de minimum trei litere
      romanesti. LIMITA: o eticheta de un singur cuvant („Salveaza") NU e vazuta - fals negativ
      DECLARAT, nu ascuns.
  M4  CONCATENARE. `"Nu s-a putut " + verb` - fraza exista, dar nu ca un literal. -> NEACOPERIT,
      declarat. Cifra e un PLAFON INFERIOR.
  M5  ALT FISIER. Aceeasi fraza in `.html` sau in Python nu e vazuta, deci o duplicare reala poate
      fi raportata ca „loc unic". -> NEACOPERIT pe .html, declarat.
  M6  SCAN GOL. Daca regexul de fisiere sau masina de stari se rup, listele se golesc si scanul ar
      raporta „nicio duplicare" - adica verde din vacuitate. -> ACOPERIT prin aserțiune anti-vacuu
      in garda (numar minim de fisiere si de siruri vazute).
────────────────────────────────────────────────────────────────────────────────────────────
"""
import os
import re
from collections import defaultdict

RAD = "/home/costin/iconta_nou/static/js"
# minimum un cuvant de 3+ litere (cu diacritice) SI un spatiu: o fraza, nu un identificator
_CUVANT = re.compile(r"[A-Za-zĂÂÎȘȚăâîșț]{3,}")
_ZGOMOT = re.compile(r"^[#.\[]|^https?:|^/|^[a-z0-9_-]+$|^\s*$")


def _fara_comentarii(src):
    """Scoate comentariile FARA sa strice sirurile. O masina de stari, nu un regex: `//` dintr-un
    sir (orice URL) nu incepe un comentariu, iar `"` dintr-un comentariu nu deschide un sir."""
    out = []
    i, n = 0, len(src)
    stare = None          # None | "'" | '"' | '`' | "//" | "/*"
    while i < n:
        c = src[i]
        d = src[i:i + 2]
        if stare is None:
            if d == "//":
                stare = "//"; i += 2; continue
            if d == "/*":
                stare = "/*"; i += 2; continue
            if c in "'\"`":
                stare = c; out.append(c); i += 1; continue
            out.append(c); i += 1; continue
        if stare == "//":
            if c == "\n":
                stare = None; out.append(c)
            i += 1; continue
        if stare == "/*":
            if d == "*/":
                stare = None; i += 2; continue
            if c == "\n":
                out.append(c)
            i += 1; continue
        # in interiorul unui sir
        if c == "\\" and i + 1 < n:
            out.append(src[i:i + 2]); i += 2; continue
        if c == stare:
            stare = None
        out.append(c); i += 1
    return "".join(out)


def _siruri(src):
    """[(text, linie)] - siruri literale, cu backtick inclus. Se ruleaza pe sursa FARA comentarii."""
    out = []
    i, n, linie = 0, len(src), 1
    while i < n:
        c = src[i]
        if c == "\n":
            linie += 1; i += 1; continue
        if c in "'\"`":
            q, j, buf = c, i + 1, []
            while j < n and src[j] != q:
                if src[j] == "\\" and j + 1 < n:
                    buf.append(src[j:j + 2]); j += 2; continue
                if src[j] == "\n":
                    linie += 1
                buf.append(src[j]); j += 1
            out.append(("".join(buf), linie))
            i = j + 1; continue
        i += 1
    return out


def normalizeaza(txt):
    """Textul CARE AJUNGE LA OM, scos din invelisul lui de cod.

    Trei pasi, fiecare adaugat dupa ce prima forma a euristicii a lasat sa treaca zgomot - masurat
    INAINTE de a raporta cifra, nu dupa:
      - escape-urile unicode se DECODEAZA: altfel aceeasi fraza apare de doua ori, sub doua forme;
      - ETICHETELE HTML se scot: invelisul difera intre ecrane fara ca fraza sa difere;
      - `${...}` -> «·», spatii colapsate: doua fraze identice cu variabile diferite trebuie sa se
        recunoasca, altfel duplicarea nu se vede.
    """
    t = re.sub(r"\\u([0-9a-fA-F]{4})",
               lambda m: chr(int(m.group(1), 16)), txt)
    t = re.sub(r"\$\{[^}]*\}", "·", t)
    t = re.sub(r"<[^>]*>", " ", t)
    return re.sub(r"\s+", " ", t).strip()


# Fragmente de COD ramase dupa scoaterea etichetelor: `=> b.addEventListener(`, `: ""} `, `class=`.
_COD = re.compile(r"=>|\(\)|=\s*[\"\']|\{|\}|\bfunction\b|\.\w+\(|\bclass=")


def e_fraza_de_om(txt):
    """Euristica DECLARATA: dupa scoaterea invelisului, textul are un spatiu SI un cuvant de 3+
    litere, nu arata a selector/URL/cheie si nu mai contine sintaxa de cod.

    LIMITELE, scrise (M3/M4 din antet): o eticheta de UN SINGUR cuvant („Salveaza") nu e vazuta; o
    fraza construita prin concatenare nu e vazuta. Cifra e un PLAFON INFERIOR."""
    t = normalizeaza(txt)
    if len(t) < 6 or " " not in t:
        return False
    if _ZGOMOT.match(t) or _COD.search(t):
        return False
    if all(re.fullmatch(r"[a-z0-9-]+", w) for w in t.split()):
        return False          # clase CSS separate prin spatiu
    return bool(_CUVANT.search(t))


def inventar(rad=RAD):
    """{fraza_normalizata: [(fisier, linie), ...]} pentru frazele care ajung la om."""
    gasite = defaultdict(list)
    for dirpath, _d, files in os.walk(rad):
        for f in sorted(files):
            if not f.endswith(".js"):
                continue
            p = os.path.join(dirpath, f)
            with open(p, encoding="utf-8", errors="replace") as fh:
                src = fh.read()
            rel = os.path.relpath(p, os.path.dirname(rad))
            for txt, linie in _siruri(_fara_comentarii(src)):
                if e_fraza_de_om(txt):
                    gasite[normalizeaza(txt)].append((rel, linie))
    return dict(gasite)


def duplicate(rad=RAD):
    """Frazele care apar in DOUA sau mai multe LOCURI - adica fara «loc unic» (interdictia 29)."""
    return {t: loc for t, loc in inventar(rad).items() if len({l[0] for l in loc}) > 1 or len(loc) > 1}


if __name__ == "__main__":
    inv = inventar()
    dup = duplicate()
    print("fraze de interfata: %d | in mai multe locuri: %d" % (len(inv), len(dup)))
    for t, loc in sorted(dup.items(), key=lambda x: -len(x[1]))[:20]:
        print("  %-58s %d locuri: %s" % (t[:58], len(loc), ", ".join("%s:%s" % l for l in loc[:3])))
