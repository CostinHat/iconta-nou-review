#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""versioneaza_assets.py -- versionare prin HASH DE CONTINUT a asseturilor front-end (?v=<hash>).

PROBLEMA (dovedita): disciplina ?v= era NEGARDATA. Un modul JS/CSS atins fara bump de ?v=
ramanea STATUT in cache-ul browserului pentru un utilizator care revine. Concret: selectoarele
"Clasificare TVA (D300)" nu apareau fiindca facturi_ecran.js importa emitere_ecran.js?v=6, iar
commitul care a schimbat emitere_ecran.js NU a incrementat ?v=6 -> browserul servea modulul VECHI.

DESIGN (fara cascada de hash-uri):
  token(asset) = sha1( continut_asset cu TOATE ?v=<token> NORMALIZATE/scoase )[:10]
  Hash-ul unui fisier NU depinde de versiunile importatorilor lui (?v= e scos INAINTE de hash),
  deci: schimbarea CODULUI lui X schimba token(X) -> toate referintele la X se actualizeaza;
  DAR actualizarea unei referinte (care contine ?v=) NU schimba tokenul fisierului care o contine
  -> punct-fix intr-o SINGURA trecere, fara cascada.

  token(fisier) = sha1( continut fara toate tokenele ?v=... )[:10]

Rulare:  python3 versioneaza_assets.py           (dry-run: listeaza ce ar schimba)
         python3 versioneaza_assets.py --scrie   (rescrie/adauga ?v= in HTML + JS)
Idempotent: a doua rulare = 0 schimbari.
Referinta catre asset INEXISTENT -> EROARE vizibila (exit != 0), nu tacere.

core/test_versionare_assets.py importa functiile de aici (sursa unica; nu duplica logica).
"""
import os
import re
import sys
import hashlib

_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC = os.path.join(_DIR, "static")
JS_DIR = os.path.join(STATIC, "js")

# Normalizare: scoate orice token ?v=... (pana la ghilimea / backtick / spatiu / paranteza).
_RE_TOKEN = re.compile(r"""\?v=[^"'`\s)]*""")

# Referinte in JS: from/import/import() catre un .js RELATIV (optional cu ?v=).
_RE_JS = re.compile(
    r"""(?P<lead>(?:from|import)\s*\(?\s*)(?P<q>["'])"""
    r"""(?P<spec>(?:\.\.?)/[^"'`?\s]+\.js)(?P<ver>\?v=[^"'`\s)]*)?(?P=q)""")

# Referinte in HTML: src= / href= catre /static/....(js|css) (optional cu ?v=).
_RE_HTML = re.compile(
    r"""(?P<lead>(?:src|href)\s*=\s*)(?P<q>["'])"""
    r"""(?P<spec>/static/[^"'`?\s]+\.(?:js|css))(?P<ver>\?v=[^"'`\s)]*)?(?P=q)""")


def _citeste(path):
    with open(path, "rb") as f:
        return f.read().decode("utf-8")


def hash_asset(path):
    """Token de continut, STABIL fata de ?v= din corpul fisierului (normalizat inainte de hash)."""
    norm = _RE_TOKEN.sub("", _citeste(path))
    return hashlib.sha1(norm.encode("utf-8")).hexdigest()[:10]


def _tinta_js(src_file, spec):
    return os.path.normpath(os.path.join(os.path.dirname(src_file), spec))


def _tinta_html(spec):
    # /static/xxx -> STATIC/xxx
    return os.path.normpath(os.path.join(STATIC, spec[len("/static/"):]))


def _fisiere_html():
    return sorted(os.path.join(STATIC, f) for f in os.listdir(STATIC) if f.endswith(".html"))


def _fisiere_js():
    out = []
    for root, _, fs in os.walk(JS_DIR):
        for fn in fs:
            if fn.endswith(".js"):
                out.append(os.path.join(root, fn))
    return sorted(out)


def _tinta(src, spec, kind):
    return _tinta_js(src, spec) if kind == "js" else _tinta_html(spec)


def _refs_din(src, text, rx, kind):
    for m in rx.finditer(text):
        spec = m.group("spec")
        tinta = _tinta(src, spec, kind)
        ver = m.group("ver")
        exista = os.path.isfile(tinta)
        yield {
            "src": src,
            "lineno": text.count("\n", 0, m.start()) + 1,
            "spec": spec,
            "tinta": tinta,
            "exista": exista,
            "token_curent": ver[3:] if ver else None,      # fara "?v="
            "token_asteptat": hash_asset(tinta) if exista else None,
        }


def descopera():
    """Toate referintele la asseturi locale (HTML + JS), fiecare cu tokenul curent si cel asteptat."""
    refs = []
    for f in _fisiere_html():
        refs += list(_refs_din(f, _citeste(f), _RE_HTML, "html"))
    for f in _fisiere_js():
        refs += list(_refs_din(f, _citeste(f), _RE_JS, "js"))
    return refs


def _rescrie(src, text, rx, kind, erori):
    def repl(m):
        spec = m.group("spec")
        tinta = _tinta(src, spec, kind)
        if not os.path.isfile(tinta):
            erori.append((src, spec, tinta))
            return m.group(0)   # nu atinge; eroarea se raporteaza
        return "%s%s%s?v=%s%s" % (m.group("lead"), m.group("q"), spec,
                                  hash_asset(tinta), m.group("q"))
    return rx.sub(repl, text)


def stampileaza(scrie):
    """Returneaza (erori, modificate). Scrie doar daca scrie=True."""
    erori = []
    modificate = []
    plan = [(f, _RE_HTML, "html") for f in _fisiere_html()] + \
           [(f, _RE_JS, "js") for f in _fisiere_js()]
    for src, rx, kind in plan:
        text = _citeste(src)
        nou = _rescrie(src, text, rx, kind, erori)
        if nou != text:
            modificate.append(src)
            if scrie:
                with open(src, "w", encoding="utf-8", newline="") as fh:
                    fh.write(nou)
    return erori, modificate


def main(argv):
    scrie = "--scrie" in argv
    refs = descopera()
    lipsa = [r for r in refs if not r["exista"]]
    if lipsa:
        print("EROARE: referinte catre asseturi INEXISTENTE:")
        for r in lipsa:
            print("  %s:%d -> %s (%s)" % (r["src"], r["lineno"], r["spec"], r["tinta"]))
        return 2
    schimbari = [r for r in refs if r["token_curent"] != r["token_asteptat"]]
    adaugate = [r for r in schimbari if r["token_curent"] is None]
    print("referinte: %d ; deja corecte: %d ; de schimbat: %d (din care ?v= LIPSA: %d)"
          % (len(refs), len(refs) - len(schimbari), len(schimbari), len(adaugate)))
    for r in sorted(schimbari, key=lambda x: (x["src"], x["lineno"])):
        rel = os.path.relpath(r["src"], _DIR)
        print("  %s:%d  %s  %s -> %s"
              % (rel, r["lineno"], r["spec"], r["token_curent"], r["token_asteptat"]))
    if not scrie:
        print("(dry-run; ruleaza cu --scrie pentru a aplica)")
        return 0
    erori, modificate = stampileaza(True)
    if erori:
        print("EROARE la scriere (asset inexistent): %s" % erori)
        return 2
    print("scrise: %d fisiere" % len(modificate))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
