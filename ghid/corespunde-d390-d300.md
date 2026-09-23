---
title: De ce nu corespunde D390 cu D300?
description: Pas cu pas — de unde vine fiecare cifră, ce înseamnă starea gri față de cea roșie și ce pași verifici înainte să tragi concluzia că e o eroare.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# De ce nu corespunde D390 cu D300?

Când vezi o neconcordanță între D390 și D300 pentru aceeași perioadă, cel mai eficient e să nu pornești de la „am greșit ceva", ci să verifici întâi trei lucruri: ce perioadă compară de fapt aplicația, ce stare a primit semnalul (roșu sau gri) și dacă diferența are o cauză temporală evidentă.

## Temeiul legal

::: ghid-temei
**Art. 325 din Codul fiscal (Legea 227/2015)** — obligația de a declara lunar, prin declarația recapitulativă (D390), livrările intracomunitare scutite (lit. a) și achizițiile intracomunitare taxabile (lit. d).

Structura oficială a formularului D300 confirmă rândurile **R1_1** (livrări intracomunitare) și **R5_1** (achiziții intracomunitare) ca puncte de comparație.
:::

**Pasul 1 — ce perioadă compară aplicația.** Fereastra verificării D390 ↔ D300 nu e luna curentă a ecranului (D300 se depune cu o lună întârziere), ci cea mai recentă perioadă pentru care există un D300 depus prin aplicație. Etichetă/mesaj arată explicit perioada folosită — verifică-o înainte să compari cifrele „din cap".

**Pasul 2 — ce stare are semnalul.** Roșu apare doar când D390 arată o operațiune pe care D300-ul depus nu o confirmă deloc (rândul corespunzător, R1_1 sau R5_1, e zero sau lipsă). Orice altă diferență de cifre, cu ambele valori pozitive, rămâne gri — tratată ca decalaj de exigibilitate (art. 284), regularizare sau rotunjire, nu ca eroare confirmată.

**Pasul 3 — dacă nu există deloc D300 depus prin aplicație** în fereastra relevantă, semnalul e gri cu mesajul „nu există D300 depus" — nu înseamnă o diferență reală, ci lipsa unei surse de comparație (de exemplu D300-ul a fost depus istoric, în afara aplicației, fără rânduri persistate).

**De ce nu e, de regulă, o eroare de calcul dublă.** Rândurile R1_1/R5_1 din D300 se derivă din aceleași facturi intracomunitare ca baza D390 — nu sunt două surse independente. O eroare de clasificare la nivelul facturii s-ar propaga identic în ambele, fără să producă nicio diferență de sesizat aici. Diferența reală vine, aproape mereu, din decalaj temporal (facturi apărute după depunerea D300) sau dintr-o corecție ulterioară a uneia dintre declarații.

## Ce se greșește în practică

- Se compară cifrele fără să se verifice mai întâi perioada afișată — o diferență „aparentă" poate fi doar rezultatul comparării unor perioade diferite din greșeală.
- Se tratează starea gri ca pe un roșu ratat — gri înseamnă „de investigat", nu „confirmat greșit".
- Se caută sursa diferenței în calculul D390 sau D300, când de fapt ambele pornesc din aceleași facturi — sursa reală e aproape mereu temporală, nu aritmetică.

## Ce face iConta.eu

Aplicația recalculează baza D390 pe perioada cea mai recentă cu D300 depus prin ea, o confruntă cu rândurile R1_1/R5_1 din acel D300 și afișează starea rezultată — verde, gri sau roșu — cu perioada folosită indicată explicit, ca să știi exact ce s-a comparat.

Nu recalculează un D300 „ipotetic" pentru comparație și nu presupune o valoare când nu există niciun D300 depus prin aplicație — în acel caz starea rămâne gri, cu mesajul care spune exact de ce.

[iConta.eu](/)
