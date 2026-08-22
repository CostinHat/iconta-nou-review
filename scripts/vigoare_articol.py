# -*- coding: utf-8 -*-
"""VERIFICAREA VIGORII PE ARTICOL (Partea 0, pasul 2) — la sursa externa, nu din corpus.

  vigoare.py <id_portal> <art> [<art> ...]

Pentru fiecare articol raporteaza: exista in forma consolidata? · e ABROGAT? · ce marcaje de
modificare poarta („(la <data>, ... a fost modificat de ...)") · data ultimei consolidari a actului.

Ce NU face, declarat: nu spune ca articolul SPUNE ce ii atribuim — aia e pasul 3, si e o citire.
Verifica STAREA articolului la data de azi, pe forma consolidata publicata de Ministerul Justitiei.
"""
import html as _html
import re
import sys
import urllib.request

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/126.0 Safari/537.36")


def ia(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return r.read().decode("utf-8", "replace")


def text(h):
    h = re.sub(r"(?is)<(script|style).*?</\1>", " ", h)
    h = re.sub(r"(?i)<br\s*/?>", "\n", h)
    h = re.sub(r"(?i)</(p|div|tr|li|h[1-6])>", "\n", h)
    h = re.sub(r"<[^>]+>", " ", h)
    h = _html.unescape(h)
    h = re.sub(r"[ \t\xa0]+", " ", h)
    return re.sub(r"\n\s*\n+", "\n\n", h).strip()


ident = sys.argv[1]
arts = sys.argv[2:]
t = text(ia("https://legislatie.just.ro/Public/DetaliiDocument/%s" % ident))

m = re.search(r"istoric consolid[ăa]ri\s*(.{0,200})", t, re.S | re.I)
cons = re.findall(r"\d{2}\.\d{2}\.\d{4}", m.group(1)) if m else []
print("ACT id=%s | ultima consolidare: %s | %d caractere"
      % (ident, cons[0] if cons else "?", len(t)))

i = t.find("Forma printabilă")
corp = t[i:] if i > 0 else t

for a in arts:
    esc = re.escape(a)
    m = re.search(r"(?:\+\s*)?Articol(?:ul)?\s*%s\b(?!\^)(?!\s*\^)(.{0,2600}?)"
                  r"(?=\n?\s*\+?\s*Articol(?:ul)?\s*\d|\Z)" % esc, corp, re.S)
    if m is None:
        m = re.search(r"ART\.\s*%s\b(.{0,2600}?)(?=ART\.\s*\d|\Z)" % esc, corp, re.S)
    print("\n=== art. %s ===" % a)
    if m is None:
        print("   NEGASIT in forma consolidata (tiparul de titlu nu potriveste — de privit manual)")
        continue
    frag = re.sub(r"\s+", " ", m.group(1)).strip()
    abrogat = bool(re.match(r"^\(?1?\)?\s*Abrogat", frag, re.I)) or \
        bool(re.search(r"^\s*Abrogat", frag, re.I))
    marcaje = re.findall(r"\(la (\d{2}-\d{2}-\d{4}),(.{0,190}?)\)", frag)
    print("   stare: %s | %d caractere" % ("ABROGAT" if abrogat else "in vigoare", len(frag)))
    print("   text : %s" % frag[:260])
    if marcaje:
        for d, ce in marcaje[:4]:
            print("   modificat la %s: %s" % (d, re.sub(r"\s+", " ", ce).strip()[:150]))
    else:
        print("   fara marcaj de modificare in corpul articolului")
