---
title: De ce diferă D390 de D300?
description: R1_1 și R5_1 din D300 se derivă din aceleași facturi ca D390 — o diferență reală vine aproape mereu din decalaj temporal, nu dintr-o eroare de calcul dublă.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# De ce diferă D390 de D300?

Când D390 și D300 arată cifre diferite pentru aceleași operațiuni intracomunitare, prima întrebare firească e „care dintre ele a calculat greșit?". Răspunsul, de cele mai multe ori, e niciuna — pentru că cele două nici măcar nu sunt surse independente.

## Temeiul legal

::: ghid-temei
**Art. 325 din Codul fiscal (Legea 227/2015)** — obligația de a declara lunar, prin declarația recapitulativă, livrările intracomunitare scutite (lit. a) și achizițiile intracomunitare taxabile (lit. d).

Structura oficială a formularului D300 confirmă rândurile **R1_1** (livrări intracomunitare) și **R5_1** (achiziții intracomunitare) ca puncte de comparație cu bazele echivalente din D390.

Art. 284 din Codul fiscal (exigibilitatea taxei) e motivul pentru care o diferență de cifre între D390 și D300 rămâne, de regulă, un semnal de verificat, nu o eroare confirmată — fără să existe un text unic de citat aici pentru decalajul de exigibilitate în sine.
:::

Rândul R1_1 (livrări) și rândul R5_1 (achiziții) din D300 nu sunt completate independent de D390 — ambele se derivă automat din **aceleași facturi intracomunitare**, cu partener identificat prin cod de TVA UE. Practic, dacă o factură intră o singură dată în sistem, ea alimentează în același fel și baza D390, și rândul corespunzător din D300.

De aici rezultă ceva important: comparația D390 ↔ D300 **nu prinde o eroare pe care ambele calcule o fac la fel** — de exemplu o factură clasificată greșit ca intracomunitară de la bun început va apărea identic, și greșit, în ambele declarații, fără nicio diferență de sesizat.

Ce produce, atunci, o diferență reală:

- **Decalaj temporal.** D300 se depune pentru o perioadă anterioară; dacă între depunerea D300 și momentul verificării au apărut facturi noi (introduse ulterior, cu exigibilitate în acea perioadă), D390 recalculat acum poate arăta mai mult decât D300-ul depus atunci.
- **Corectare manuală ulterioară** a uneia dintre declarații — de exemplu o rectificativă de D300 după depunerea inițială, sau o corecție a bazei D390.

## Ce se greșește în practică

- Se presupune că o diferență D390-D300 înseamnă automat o eroare de calcul — cele două pornesc, de regulă, din aceleași facturi, deci o eroare de clasificare la sursă nu produce nicio diferență între ele.
- Se compară D390 recalculat acum cu un D300 „aproximat", nu cu cel efectiv depus — comparația corectă e mereu pe versiunea depusă, nu pe una reconstituită mental.
- Se ignoră faptul că direcția diferenței contează: D390 mai mare decât D300 sugerează o operațiune apărută ulterior depunerii D300; D300 mai mare decât D390 sugerează altceva (de regulă o corecție ulterioară la nivel de evidență).

## Ce face iConta.eu

Aplicația confruntă baza D390 (recalculată pe perioada relevantă) cu rândurile R1_1 (livrări) și R5_1 (achiziții) din D300-ul efectiv depus prin aplicație pentru cea mai recentă perioadă disponibilă. Rezultatul e verde dacă valorile coincid, roșu dacă D390 arată o operațiune pe care D300 depus nu o confirmă deloc (cu propunere de remediu, confirmată de tine), și gri pentru orice altă diferență de cifre — tratată ca decalaj de exigibilitate, regularizare sau rotunjire, niciodată ca eroare automat confirmată.

Ce nu verifică: o eroare de clasificare făcută o singură dată, la nivelul facturii, care se propagă identic în ambele declarații — aceasta rămâne responsabilitatea verificării facturii la sursă, nu a comparației D390-D300.

[iConta.eu](/)
