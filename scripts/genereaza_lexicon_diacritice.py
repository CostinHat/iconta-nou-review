# -*- coding: utf-8 -*-
"""Lexiconul DIACRITICELOR, derivat din corpusul legislativ (`anaf_surse/`), nu scris de mână.

Comanda Costin 09.10.2026 („Retest 2” pct.2): textele fără diacritice de pe ecrane. Lista de declanșatori scrisă de mână
(`test_diacritice_afisate._TRIGGERE`) prinde câteva zeci de cuvinte; un text pe jumătate corectat („Ocupația … lucratoare”) trece.
Lexiconul spune, pentru o formă fără diacritice, care e forma scrisă — numai când corpusul o dovedește:

  · se citesc numai documentele SCRISE cu diacritice (în ele „fără/după/către/și/în” apar, formele ASCII aproape deloc);
  · o formă ASCII intră doar dacă în acele documente apare (aproape) numai cu diacritice — sub 0,5% din apariții (zgomot de
    transcriere) — și forma cu diacritice dominantă are cel puțin 95%;
  · formele cu DOUĂ citiri corecte rămân pe dinafară: „plata” (articulat) / „plată”, „verifica” (infinitiv) / „verifică” — se
    exclud singure, fiindcă apar des fără diacritice în corpus; cele rare în corpus, dar ambigue în aplicație, sunt în AMBIGUE.

Ieșire: `core/lexicon_diacritice.json` ({forma_ascii: forma_corecta}). Uz: python scripts/genereaza_lexicon_diacritice.py --scrie"""
import collections
import glob
import html
import io
import json
import os
import re
import sys
import unicodedata

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IESIRE = os.path.join(RAD, "core", "lexicon_diacritice.json")
#: ambigue în textele aplicației, deși rare în corpus: „pe tine”, „firma sa”, „lipsa X”, „în afara”, „cheltuiala X”, „a exista”
AMBIGUE = {"tine", "sa", "lipsa", "afara", "cheltuiala", "exista", "ca", "sau", "data", "luna", "baza", "cota", "suma", "nota",
           "taxa", "factura", "perioada", "plata", "sarcina", "marfa", "vanzare", "intrare", "iesire"}
_W = re.compile(r"[A-Za-zĂÂÎȘȚăâîșțŞŢşţ]+")


def _norm(w):
    return w.lower().replace("ş", "ș").replace("ţ", "ț")


def _fold(w):
    return "".join(c for c in unicodedata.normalize("NFKD", w) if not unicodedata.combining(c))


def genereaza():
    cand, ascii_cnt = collections.defaultdict(collections.Counter), collections.Counter()
    for p in sorted(glob.glob(os.path.join(RAD, "anaf_surse", "*.txt")) + glob.glob(os.path.join(RAD, "anaf_surse", "*.html"))):
        if "GRESIT" in os.path.basename(p):
            continue
        t = io.open(p, encoding="utf-8", errors="ignore").read()
        if p.endswith(".html"):
            t = html.unescape(re.sub(r"<[^>]+>", " ", t))
        ws = [_norm(w) for w in _W.findall(t)]
        d = sum(1 for w in ws if w in ("fără", "după", "către", "și", "în"))
        a = sum(1 for w in ws if w in ("fara", "dupa", "catre", "si", "in"))
        if d < 20 or a > d * 0.05:
            continue
        for w in ws:
            f = _fold(w)
            if f == w:
                ascii_cnt[f] += 1
            else:
                cand[f][w] += 1
    lex = {}
    for f, c in cand.items():
        tot = sum(c.values())
        w, k = c.most_common(1)[0]
        if len(f) < 2 or f in AMBIGUE or k < 2 or k / tot < 0.95 or ascii_cnt[f] > 0.005 * (tot + ascii_cnt[f]):
            continue
        lex[f] = w
    return dict(sorted(lex.items()))


if __name__ == "__main__":
    lex = genereaza()
    if "--scrie" in sys.argv:
        json.dump(lex, io.open(IESIRE, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print("lexicon: %d forme" % len(lex))
