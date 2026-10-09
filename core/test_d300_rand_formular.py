# -*- coding: utf-8 -*-
"""GARD — rândul din formularul D300 numit pe ecran e rândul din FORMULARUL ÎN VIGOARE, nu numărul din atributul XML.

Neconformitatea (retest 09.10.2026, „Retest 2” pct.2): ecranul spunea „rândul 17.2” pentru `R17_2` și „rd.26” pentru achizițiile
scutite (`R26_1`). În formularul OPANAF 174/2026 `R17` e „TOTAL TAXĂ COLECTATĂ” = rd.19, iar `R26` e rd.29: de la vânzările la
distanță (rd.17, rd.18) formularul a renumerotat, atributele XML au rămas. Gardul citește formularul (`anaf_surse/
opanaf_174_2026_d300.txt`) și cere ca, la fiecare rând din `core.d300_randuri.RAND_FORMULAR`, textul formularului să fie cel al
rândului: eticheta oficială a rândului manual (`d300_manual_api.ETICHETE`), iar la rândurile calculate titlul lor din formular.
"""
import io
import os
import re
import unicodedata

from core.d300_randuri import RAND_FORMULAR, rand_formular
from core.d300_manual_api import ETICHETE

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#: rândurile CALCULATE (fără etichetă de introducere manuală): titlul lor din formular, verbatim (OPANAF 174/2026)
TITLURI_CALCULATE = {17: "TOTAL TAXĂ COLECTATĂ", 27: "TOTAL TAXĂ DEDUCTIBILĂ", 28: "SUB-TOTAL TAXĂ DEDUSĂ",
                     32: "TOTAL TAXĂ DEDUSĂ", 33: "Suma negativă a TVA în perioada de raportare",
                     34: "Taxa de plată în perioada de raportare", 37: "TVA de plată cumulat",
                     40: "Suma negativă a TVA cumulate", 41: "Sold TVA de plată la sfârşitul perioadei",
                     42: "Soldul sumei negative de TVA la sfârşitul perioadei"}


def _norm(s):
    s = "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c)).lower()
    return re.sub(r"[^a-z0-9%]+", " ", s).strip()


def _radacini(text, n=5):
    return [w[:7] for w in _norm(text).split()[:n]]


def randuri_formular():
    """{„19”: „TOTAL TAXĂ COLECTATĂ (sumă …”} din tabelul formularului (rândul și textul de pe linia lui)."""
    t = io.open(os.path.join(_RAD, "anaf_surse", "opanaf_174_2026_d300.txt"), encoding="utf-8").read()
    a = t.index("TAXA PE VALOAREA ADĂUGATĂ COLECTATĂ")
    b = t.index("Soldul sumei negative de TVA la sfârşitul perioadei de raportare", a) + 80
    out = {}
    for ln in t[a:b].splitlines():
        m = re.match(r"^\s{0,3}(\d{1,2}(?:\.\d)?)\s+(\S.+)$", ln)
        if m and m.group(1) not in out:
            out[m.group(1)] = m.group(2)
    return out


def test_formularul_se_citeste():
    f = randuri_formular()
    assert len(f) >= 50, "anti-vacuu: doar %d rânduri citite din formular" % len(f)
    assert _norm(f["19"]).startswith(_norm("TOTAL TAXĂ COLECTATĂ")) and _norm(f["34"]).startswith(_norm("Ajustări conform pro-rata"))


def test_fiecare_rand_manual_cade_pe_textul_lui_din_formular():
    f = randuri_formular()
    gresite = []
    for cod, eticheta in sorted(ETICHETE.items()):
        n = int(cod[1:])
        if n not in RAND_FORMULAR:
            continue                     # cote din perioade trecute: fără rând în formularul de azi, se numesc prin etichetă
        rand = str(RAND_FORMULAR[n])
        # primele cinci cuvinte, pe rădăcină (7 litere): eticheta vine din structură, formularul acordă uneori altfel
        # („achiziţii” / „achiziţiile”) — rădăcina rămâne, iar un rând greșit are alte cuvinte de la primul
        if rand not in f or _radacini(f[rand]) != _radacini(eticheta.split(" — ")[0]):
            gresite.append("%s -> rd.%s: formularul spune %r, eticheta %r" % (cod, rand, f.get(rand, "")[:70], eticheta[:70]))
    assert not gresite, "rânduri D300 numite greșit pe ecran:\n  " + "\n  ".join(gresite)


def test_randurile_calculate_cad_pe_titlul_lor():
    f = randuri_formular()
    gresite = ["R%d -> rd.%s: %r" % (n, RAND_FORMULAR[n], f.get(str(RAND_FORMULAR[n]), "")[:60])
               for n, titlu in TITLURI_CALCULATE.items()
               if not _norm(f.get(str(RAND_FORMULAR[n]), "")).startswith(_norm(titlu))]
    assert not gresite, "rânduri calculate D300 numite greșit:\n  " + "\n  ".join(gresite)


def test_textul_rândului():
    assert rand_formular("R17_2") == "rândul 19, coloana TVA"          # OPANAF 174/2026: rd.19 TOTAL TAXĂ COLECTATĂ
    assert rand_formular("R26_1") == "rândul 29, coloana Valoare"      # rd.29 achiziții scutite sau neimpozabile
    assert rand_formular("R12_1_1") == "rândul 12.1, coloana Valoare"
    assert rand_formular("R75_2").startswith("rândul „Achiziții")      # fără rând în formularul de azi: eticheta oficială
    assert rand_formular("R99_1") == "R99_1"                           # nu e atribut D300: rămâne cum e (eroare de program)
