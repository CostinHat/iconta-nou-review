# -*- coding: utf-8 -*-
"""Valori FISCALE scrise literal in TEXTUL AFISAT de ecrane.

Intrebarea lui Costin, 24.08.2026: «ce alte valori au fost corecte in ianuarie si
nu mai sunt?». Clasa nu e formula (aia s-a masurat: 3), ci VALOAREA SCRISA IN
ETICHETA — cifra vine corecta de la server, iar textul de langa ea imbatraneste
singur.

CUM POATE GRESI SCANUL ASTA — scris INAINTE de prima masuratoare (interdictia 76):
  M1  o valoare cu separator de mii («4.050 lei») nu se potriveste cu \\d+ simplu;
  M2  o valoare INTERPOLATA (`${d.cota}%`) NU e hardcodata — e a serverului, si
      daca intra in numaratoare cifra creste fals;
  M3  numerele din `style=` (latimi, culori, px) nu sunt fiscale — zgomot pur;
  M4  un AN (2025, 2026) nu e o cota, dar arata la fel pentru un tipar de cifre;
  M5  un text construit prin CONCATENARE pe mai multe randuri se rupe, deci se
      pierde — limita ramane, se declara;
  M6  domeniul e `static/js/`; `.html` nu intra — masurat separat.
"""
import io
import os
import re
import sys

import os
BAZA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static", "js")

# M1: separatorul de mii intra in tipar. M4: anii se exclud explicit.
NUMAR = re.compile(r"(?<![\w.])(\d{1,3}(?:[.\s]\d{3})+|\d+(?:[,.]\d+)?)(?![\w])")
ANI = {"2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022",
       "2023", "2024", "2025", "2026", "2027"}
# vocabularul care face dintr-un numar unul FISCAL
FISCAL = re.compile(
    r"(?i)(tva|cot[ăa]|impozit|cas\b|cass|contribu|deduc|plafon|salariu minim|"
    r"sm\b|acciz|scutir|facilitat|prag|norm[ăa]|micro|dividend|garan[țt]i)")
# M3, CORECTAT dupa prima rulare: NU se arunca sirul care contine `class=`/`style=`.
# In codul asta textul afisat traieste INAUNTRUL sabloanelor HTML, deci filtrul de
# stil a aruncat chiar cazul cunoscut (rip_ecran.js:145, «sm 4.050 lei») — un fals
# negativ pe singurul caz pe care il stiam dinainte. Se scot ETICHETELE, ramane TEXTUL.
ETICHETA = re.compile(r"<[^>]*>")
COD = re.compile(r"(?i)(px|rem|#[0-9a-f]{3,6}|var\(--)")


def siruri(src):
    """Sirurile literale, cu numarul liniei. M2: `${...}` se marcheaza, nu se ignora."""
    out, i, n, linie = [], 0, len(src), 1
    while i < n:
        c = src[i]
        if c == "\n":
            linie += 1
            i += 1
            continue
        d = src[i:i + 2]
        if d == "//":
            j = src.find("\n", i)
            i = n if j < 0 else j
            continue
        if d == "/*":
            j = src.find("*/", i + 2)
            j = n if j < 0 else j + 2
            linie += src[i:j].count("\n")
            i = j
            continue
        if c in "\"'`":
            j, q, start_linie = i + 1, c, linie
            while j < n:
                if src[j] == "\\":
                    j += 2
                    continue
                if src[j] == "\n":
                    linie += 1
                if src[j] == q:
                    break
                j += 1
            out.append((start_linie, src[i + 1:j]))
            i = j + 1
            continue
        i += 1
    return out


fisiere = []
for rad, _, nume in os.walk(BAZA):
    for f in sorted(nume):
        if f.endswith(".js"):
            fisiere.append(os.path.join(rad, f))

gasite, interpolate = [], 0
for f in fisiere:
    src = io.open(f, encoding="utf-8").read()
    rel = f.replace("/home/costin/iconta_nou/", "")
    for nr, s in siruri(src):
        # M3 corectat: se scot ETICHETELE (cu atributele lor), ramane textul citit de om
        text = ETICHETA.sub(" ", s)
        # M2: ce vine din interpolare e al SERVERULUI, nu hardcodat
        text = re.sub(r"\$\{[^}]*\}", "\x00", text)
        if not FISCAL.search(text) or COD.search(text):
            continue
        nums = [x for x in NUMAR.findall(text.replace("\x00", " ")) if x not in ANI]
        if not nums:
            if "\x00" in text:
                interpolate += 1
            continue
        gasite.append((rel, nr, nums, " ".join(text.split())[:120]))

w = sys.stdout.write
w("FISIERE: %d\n" % len(fisiere))
w("SIRURI cu vocabular fiscal SI valoare literala: %d\n" % len(gasite))
w("(pentru contrast, siruri cu procent INTERPOLAT de la server: %d)\n\n" % interpolate)
for rel, nr, nums, s in gasite:
    w("%s:%d  %s\n     %s\n" % (rel, nr, ",".join(nums), s))
