---
title: "Cum se descarcă gestiunea pentru lipsurile constatate la inventar?"
description: "Cum tratează iConta.eu descărcarea de gestiune pentru un minus de inventar, în funcție de imputabilitate și de cota de TVA aplicabilă."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se descarcă gestiunea pentru lipsurile constatate la inventar?

Descărcarea de gestiune pentru o lipsă constatată la inventariere nu înseamnă o singură notă contabilă standard — tratamentul diferă după cum lipsa e imputabilă unei persoane sau nu, și dacă e demonstrată ca fiind cauzată de furt, distrugere sau calamitate.

## Temeiul legal

::: ghid-temei
"Nu se ajustează deducerea inițială a taxei în cazul: a) bunurilor distruse, pierdute sau
furate, în condițiile în care aceste situații sunt demonstrate sau confirmate în mod
corespunzător de persoana impozabilă. În cazul bunurilor furate, persoana impozabilă
demonstrează furtul bunurilor pe baza actelor doveditoare emise de organele judiciare."
— Codul fiscal, art. 304 alin. (2) lit. a)
:::

Regula de bază pentru TVA: dacă bunul lipsă nu e demonstrat ca fiind distrus, pierdut sau furat în condiții confirmate corespunzător, deducerea inițială de TVA trebuie ajustată (art. 304 alin. 1 lit. c). Dacă lipsa e demonstrată/confirmată — inclusiv, pentru furt, cu acte doveditoare emise de organele judiciare — ajustarea nu se face. Nuanța contează: nu e vorba de "asigurat sau neasigurat", ci de "demonstrat sau nu".

## Ce se greșește în practică

- Se tratează orice lipsă la fel din punct de vedere fiscal, fără să se distingă între imputabilă (recuperată de la vinovat) și neimputabilă.
- Se omite ajustarea de TVA pentru o lipsă neimputabilă și nedemonstrată ca fiind distrusă/furată/calamitate.
- Se face ajustarea de TVA și pentru o lipsă demonstrată corespunzător (asigurată sau cu dovadă de distrugere), deși legea o exceptează explicit.

## Ce face iConta.eu

Ecranul "Inventariere anuală", operația Minus, acceptă doar conturi de stoc din lista {371, 301, 302, 303, 345, 381} și cere obligatoriu cota de TVA aplicabilă — aplicația refuză explicit operațiunea dacă nu se transmite cota, tocmai pentru că o cotă fixă scrisă în aplicație s-ar putea rupe tăcut de lege la prima schimbare de cotă.

În funcție de datele introduse, aplicația generează:

- pentru lipsa **imputabilă**: nota de descărcare de gestiune către contul de venit din imputare (4282 pentru salariat, 461 pentru terț), plus TVA calculat pe valoarea de imputare;
- pentru lipsa **neimputabilă, nedemonstrată ca asigurată sau distrusă**: descărcarea de gestiune, plus o linie separată de ajustare a TVA (635=4426);
- pentru lipsa **neimputabilă, asigurată sau cu distrugere dovedită**: doar descărcarea de gestiune, fără ajustare de TVA.

Ca și la celelalte operațiuni de inventariere, nota nu actualizează automat stocul din modulul de gestiune — doar jurnalul contabil.

[iConta.eu](/)
