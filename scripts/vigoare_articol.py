# -*- coding: utf-8 -*-
"""VERIFICAREA VIGORII PE ARTICOL (Partea 0, pasul 2) — la sursa externa sau din corpus.

  vigoare_articol.py <id_portal|cale_fisier> <art> [<art> ...]

Pentru fiecare articol raporteaza: exista in forma consolidata? · e ABROGAT? · ce marcaje de
modificare poarta („(la <data>, ... a fost modificat de ...)") · data ultimei consolidari a actului.

Ce NU face, declarat: nu spune ca articolul SPUNE ce ii atribuim — aia e pasul 3, si e o citire.
Verifica STAREA articolului la data de azi, pe forma consolidata publicata de Ministerul Justitiei.

LOGICA DE LOCALIZARE NU MAI STA AICI (31.08.2026). A trecut in `core/articol_in_act.py`, cu cele
patru reparatii ale ei si cu motivele lor. Motivul mutarii: la nivel de script, sub `sys.argv`, nu
se putea importa — deci cine avea nevoie de ea o RE-SCRIA, iar amandoua copiile pe care le-am facut
au dat cifre gresite. Aici a ramas doar CLI-ul: de unde se ia documentul, si cum se tipareste.
Modulul e confruntat cu scriptul pe toate perechile din registru: zero dezacorduri.
"""
import os
import sys
import urllib.request
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import articol_in_act as A  # noqa: E402

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/126.0 Safari/537.36")


def ia(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return r.read().decode("utf-8", "replace")


# NU se pastreaza un alias `text = A.text` "pentru scripturile vechi": fisierul asta ruleaza la
# import (citeste sys.argv la nivel de modul), deci NIMENI nu-l poate importa. Un nume pastrat
# pentru un apelant imposibil e o urma de intentie, nu o decizie (R23). Cine are nevoie de `text`
# il ia din `core.articol_in_act`.

ident = sys.argv[1]
arts = sys.argv[2:]

# MOD FISIER LOCAL (23.08.2026). Portalul NU serveste actele mari ca pagina unica: pentru Codul
# fiscal, `DetaliiDocument` da un CIOT de 4.392 de caractere cu 0 titluri de articol, iar JS-ul
# paginii nu incarca niciun text. Dar actul E DEJA IN CORPUS, adus si amprentat - iar copia poarta
# aceleasi marcaje de consolidare. Deci se citeste de acolo.
# Amprenta ramane garda: `test_corpus_amprenta` verifica la fiecare poarta ca fisierul e cel adus.
if os.path.exists(ident):
    t, amprenta = A.din_fisier(ident)
    print("ACT din corpus: %s | amprenta %s | %d caractere"
          % (os.path.basename(ident), amprenta, len(t)))
else:
    t = A.text(ia("https://legislatie.just.ro/Public/DetaliiDocument/%s" % ident))
    m = re.search(r"istoric consolid[ăa]ri\s*(.{0,200})", t, re.S | re.I)
    cons = re.findall(r"\d{2}\.\d{2}\.\d{4}", m.group(1)) if m else []
    print("ACT id=%s | ultima consolidare: %s | %d caractere"
          % (ident, cons[0] if cons else "?", len(t)))

# ANTI-VACUU (23.08.2026). Un „negasit" despre un act neadus nu e un raspuns, e o tacere care arata
# ca un raspuns. Criteriul nu e lungimea (arbitrara), ci daca actul adus ARE articole.
_n = A.titluri(t)
if A.e_ciot(t):
    print("")
    print("REFUZ: in documentul adus se vad %d titluri de articol. Pagina `DetaliiDocument` e un CIOT"
          % _n)
    print("pentru actele mari — forma consolidata sta la ALT id. Orice raspuns despre un articol ar fi")
    print("vid. Cauta forma consolidata cu `scripts/portal_legislativ.py cauta ...` si da ID-UL EI.")
    sys.exit(2)
print("   (%d titluri de articol vazute in document)" % _n)

for a in arts:
    print("\n=== art. %s ===" % a)
    frag = A.fragment(t, a)
    if frag is None:
        print("   NEGASIT in forma consolidata (tiparul de titlu nu potriveste — de privit manual)")
        continue
    print("   stare: %s | %d caractere"
          % ("ABROGAT" if A.abrogat(frag) else "in vigoare", len(frag)))
    print("   text : %s" % frag[:260])
    mk = A.marcaje(frag)
    if mk:
        for d, ce in mk[:4]:
            print("   modificat la %s: %s" % (d, ce[:150]))
    else:
        print("   fara marcaj de modificare in corpul articolului")
