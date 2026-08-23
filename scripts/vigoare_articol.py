# -*- coding: utf-8 -*-
"""VERIFICAREA VIGORII PE ARTICOL (Partea 0, pasul 2) — la sursa externa, nu din corpus.

  vigoare.py <id_portal> <art> [<art> ...]

Pentru fiecare articol raporteaza: exista in forma consolidata? · e ABROGAT? · ce marcaje de
modificare poarta („(la <data>, ... a fost modificat de ...)") · data ultimei consolidari a actului.

Ce NU face, declarat: nu spune ca articolul SPUNE ce ii atribuim — aia e pasul 3, si e o citire.
Verifica STAREA articolului la data de azi, pe forma consolidata publicata de Ministerul Justitiei.
"""
import os
import io
import hashlib
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

# MOD FISIER LOCAL (23.08.2026). Portalul NU serveste actele mari ca pagina unica: pentru Codul
# fiscal, `DetaliiDocument` da un CIOT de 4.392 de caractere cu 0 titluri de articol, iar JS-ul
# paginii nu incarca niciun text (verificat: singurele apeluri sunt actiuniSuferite / actiuniInduse /
# referaPe / referitDe). Dar actul E DEJA IN CORPUS, adus si amprentat - iar copia poarta aceleasi
# marcaje de consolidare „(la ZZ-LL-AAAA, ... a fost modificat de ...)". Deci se citeste de acolo.
# Amprenta ramane garda: `test_corpus_amprenta` verifica la fiecare poarta ca fisierul e cel adus.
if os.path.exists(ident):
    _brut = io.open(ident, "rb").read()
    t = text(_brut.decode("utf-8", "replace"))
    print("ACT din corpus: %s | amprenta %s | %d caractere"
          % (os.path.basename(ident), hashlib.sha256(_brut).hexdigest()[:16], len(t)))
    cons = re.findall(r"\d{2}\.\d{2}\.\d{4}", t[:4000])
else:
    t = text(ia("https://legislatie.just.ro/Public/DetaliiDocument/%s" % ident))
    m = re.search(r"istoric consolid[ăa]ri\s*(.{0,200})", t, re.S | re.I)
    cons = re.findall(r"\d{2}\.\d{2}\.\d{4}", m.group(1)) if m else []
    print("ACT id=%s | ultima consolidare: %s | %d caractere"
          % (ident, cons[0] if cons else "?", len(t)))

# ANTI-VACUU (23.08.2026). Pagina `DetaliiDocument` contine textul integral pentru actele MICI, dar
# pentru cele mari e un CIOT: Codul fiscal a venit in 4.407 caractere, iar instrumentul a raspuns
# „NEGASIT" pentru toate cele cinci articole cerute — cu incredere. Un „negasit" despre un act
# neadus nu e un raspuns, e o tacere care arata ca un raspuns.
# Criteriul nu e lungimea (arbitrara), ci daca actul adus ARE articole: daca nu vedem niciun titlu
# de articol, nu putem spune nimic despre al nostru.
_titluri = re.findall(r"(?im)^\s*Articolul\s+[\dIVXLC]", t)
if len(_titluri) < 2:
    print("")
    print("REFUZ: in documentul adus se vad %d titluri de articol. Pagina `DetaliiDocument` e un CIOT"
          % len(_titluri))
    print("pentru actele mari — forma consolidata sta la ALT id. Orice raspuns despre un articol ar fi")
    print("vid. Cauta forma consolidata cu `scripts/portal_legislativ.py cauta ...` si da ID-UL EI.")
    sys.exit(2)
print("   (%d titluri de articol vazute in document)" % len(_titluri))

i = t.find("Forma printabilă")
corp = t[i:] if i > 0 else t

for a in arts:
    esc = re.escape(a)
    # Terminatorul cerea `Articolul <CIFRA ARABA>`. Actele MODIFICATOARE (OUG, legi de
    # modificare) isi numeroteaza articolele cu cifre ROMANE — „Articolul III", „Articolul LXVI" —
    # deci dupa articolul cautat nu urma niciodata o cifra araba, potrivirea nu se putea incheia
    # in fereastra de 2600 de caractere, si iesea NEGASIT. Exact articolele care poarta
    # schimbarile fiscale. Prins 23.08.2026, dupa ce refuzul anti-vacuu a separat cele doua
    # defecte: pana atunci „negasit" putea insemna si „n-am adus actul".
    # Titlul se recunoaste dupa marcajul "+" al portalului, NU dupa pozitia in linie: forma reala e
    # ") \n + \n Articolul III (1) Prin derogare...". Si se EXCLUDE forma de CITARE, "Articolul III
    # din LEGEA nr. 173...", unde articolul e al actului MODIFICATOR - fara asta, art.III al lui
    # OUG 89/2025 a primit un "modificat la 16-08-2026" care apartinea art. XXXVI, si a produs o
    # alarma falsa pe trei valori din registru.
    #
    # FARA FEREASTRA FIXA. Forma dinainte capta cel mult 2600 de caractere si cerea ca URMATORUL
    # titlu sa incapa in ele; un articol mai lung de-atat nu se putea incheia, deci iesea NEGASIT -
    # si tocmai articolele lungi sunt cele cu conditii, adica cele care poarta valori. Acum se cauta
    # titlul, apoi urmatorul titlu, si se taie intre ele.
    _tit = re.compile(r"(?:\+\s*|(?:^|\n)\s*)Articol(?:ul)?\s*%s\b(?!\^)(?!\s*\^)(?!\s+din\b)" % esc)
    _oricare = re.compile(r"(?:\+\s*|(?:^|\n)\s*)Articol(?:ul)?\s*[\dIVXLC]+(?:\^\d+)?\b(?!\s+din\b)")
    _m0 = _tit.search(corp)
    m = None
    if _m0:
        _urm = _oricare.search(corp, _m0.end())
        _sf = _urm.start() if _urm else len(corp)

        class _F:
            def __init__(self, s):
                self._s = s

            def group(self, _i):
                return self._s
        m = _F(corp[_m0.end():_sf])
    if m is None:
        m = re.search(r"ART\.\s*%s\b(.{0,2600}?)(?=ART\.\s*\d|\Z)" % esc, corp, re.S)
    print("\n=== art. %s ===" % a)
    if m is None:
        print("   NEGASIT in forma consolidata (tiparul de titlu nu potriveste — de privit manual)")
        continue
    # Fragmentul se OPRESTE la urmatorul titlu de articol, oricum ar fi numerotat. Fara asta,
    # fereastra de 2600 de caractere trecea peste sfarsitul articolului si imprumuta marcaje de la
    # articolele urmatoare: pe OUG 89/2025, art.III a primit astfel un „modificat la 16-08-2026" care
    # apartinea de fapt art. XXXVI, si a produs o alarma falsa pe trei valori din registru. Un
    # instrument care atribuie gresit modificarile ar fabrica alarme la scara.
    _brut = m.group(1)
    _stop = re.search(r"\n?\s*\+?\s*Articol(?:ul)?\s*[\dIVXLC]", _brut)
    if _stop:
        _brut = _brut[:_stop.start()]
    frag = re.sub(r"\s+", " ", _brut).strip()
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
