---
title: "Ajustările pentru deprecierea stocurilor: deductibilitate"
description: "De ce ajustările contabile pentru deprecierea stocurilor nu sunt, ca regulă, deductibile fiscal la calculul impozitului pe profit."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ajustările pentru deprecierea stocurilor: deductibilitate

Contabil, o entitate poate — și, potrivit principiului prudenței, chiar trebuie — să înregistreze ajustări pentru deprecierea stocurilor atunci când valoarea lor de inventar scade sub costul de achiziție. Fiscal însă, lucrurile stau altfel: Codul fiscal tratează deductibilitatea provizioanelor și ajustărilor pentru depreciere ca pe o listă închisă, iar stocurile nu apar pe ea.

## Temeiul legal

::: ghid-temei
„(1) Contribuabilul are dreptul la deducerea rezervelor și provizioanelor/ajustărilor pentru depreciere, numai în conformitate cu prezentul articol, astfel: a) rezerva legală [...]; b) provizioanele pentru garanții de bună execuție acordate clienților [...]; c) ajustările pentru deprecierea creanțelor [...] în limita unui procent de 30% [...]"
— Legea nr. 227/2015 privind Codul fiscal, art. 26 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Art. 26 alin. (1) este formulat expres ca listă **limitativă** („numai în conformitate cu prezentul articol"): rezerva legală, provizioane pentru garanții de bună execuție, ajustări pentru deprecierea creanțelor (client, în anumite condiții), provizioane specifice ale instituțiilor financiare, rezerve tehnice de asigurare etc.
- **Ajustările pentru deprecierea stocurilor nu se regăsesc printre literele a)-n) ale art. 26 alin. (1)** — deci, deși sunt corecte și obligatorii contabil, nu sunt deductibile la calculul rezultatului fiscal.
- Consecința practică e dată de art. 25 alin. (3) lit. g): cheltuiala cu ajustarea e „cheltuială cu deductibilitate limitată... în limita prevăzută la art. 26" — cum art. 26 nu prevede nimic pentru stocuri, limita practică e zero, iar suma se adună înapoi (element similar cheltuielilor nedeductibile) la calculul profitului impozabil, prin declarația 101.
- Simetric, la momentul în care ajustarea se anulează (stocul e vândut, consumat sau se reface valoarea), reluarea la venituri a ajustării nu mai este venit impozabil, pentru că suma nu a fost dedusă inițial (evită dubla impunere).

## Ce se greșește în practică

- Se dă deducere directă cheltuielii cu ajustarea de valoare a stocurilor, presupunând că orice cheltuială contabilă corectă e automat deductibilă fiscal.
- Se confundă ajustările pentru deprecierea stocurilor cu ajustările pentru deprecierea creanțelor (art. 26 lit. c), care sunt parțial deductibile) — regimul fiscal e complet diferit.
- La anularea unei ajustări nededuse inițial, se impozitează eronat reluarea la venituri, deși suma nu a generat niciodată o deducere fiscală.
- Se omite reflectarea corectă în D101 a sumei nedeductibile, ceea ce denaturează rezultatul fiscal declarat.

## Ce face iConta.eu

iConta.eu **are o funcție dedicată** pentru exact acest caz: `nota_ajustare_stoc` din `core/provizioane.py` generează nota contabilă de constituire/reluare a ajustării de valoare a stocurilor (6814=39x, respectiv 39x=7814) și marchează explicit rezultatul cu `deductibil: False`, cu comentariul din cod „nedeductibil fiscal (nu figurează în art. 26)" — exact regula descrisă mai sus. Aplicația are și un modul consistent de gestiune a stocurilor (`stocuri.py`, `stocuri_api.py`, `stocuri_cv.py`) pentru mișcări, cantități și valori. Nu am găsit însă, în modulele verificate, o legătură automată între acest marcaj `deductibil: False` și completarea efectivă a rândului corespunzător din declarația 101 — reportarea sumei ca element similar cheltuielilor nedeductibile în D101 rămâne, la acest moment, o verificare manuală a contabilului.

[iConta.eu](/)
