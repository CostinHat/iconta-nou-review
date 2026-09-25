---
title: "Firmele cu puncte de încasare cash 2026: reguli"
description: "Cum se aplică plafoanele legale de încasări și plăți în numerar atunci când firma are mai multe casierii sau sedii secundare cu casierie proprie."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Firmele cu puncte de încasare cash 2026: reguli

O firmă cu mai multe puncte de lucru care încasează cash — magazine, showroom-uri, puncte de service — nu împarte un singur plafon zilnic pe toată firma. Legea aplică plafoanele de încasări/plăți în numerar **pe fiecare casierie în parte**, ceea ce schimbă complet modul în care se calculează depășirile.

## Temeiul legal

::: ghid-temei
„Articolul 7
În cazul persoanelor prevăzute la art. 1 alin. (1) care au organizate mai multe casierii, plafoanele prevăzute la art. 3 alin. (1) lit. a) și b) și la art. 4 alin. (1) sunt aplicabile pe fiecare casierie în parte.
Articolul 8
Sucursalele și alte sedii secundare ale persoanelor juridice care au casierie proprie și/sau cont deschis la o instituție de credit aplică în mod corespunzător prevederile prezentului capitol."
— Legea 70/2015, art. 7 și art. 8 (sursă: anaf_surse/legea_70_2015_consolidat.txt)
:::

Din text rezultă regimul aplicabil firmelor cu mai multe puncte de încasare:

- **Plafonul de încasări de 5.000 lei/zi de la o persoană** (art. 3 alin. (1) lit. a)) și cel de **10.000 lei/zi** pentru magazinele de tip cash and carry (lit. b)) se calculează separat, pentru fiecare casierie, nu cumulat pe firmă.
- **Plafonul de 10.000 lei/zi pentru încasări de la persoane fizice** (art. 4 alin. (1)) — de exemplu contravaloarea unor livrări sau cesiuni de creanțe — se aplică la fel, pe casierie.
- **Sucursalele și sediile secundare cu casierie proprie** intră sub aceleași reguli ca sediul principal — fiecare casierie a fiecărui sediu secundar are propriile plafoane, verificate independent.
- Condiția-cheie e existența unei **casierii proprii** la punctul respectiv — un punct de lucru fără casierie proprie și fără cont bancar propriu nu generează un plafon separat, ci rămâne sub casieria centralizatoare.

## Ce se greșește în practică

- Se cumulează încasările tuturor punctelor de lucru într-un singur plafon zilnic pe firmă, când legea le tratează separat, pe fiecare casierie — o firmă cu trei magazine poate încasa legal 5.000 lei de la aceeași persoană în fiecare magazin, în aceeași zi, dacă operațiunile sunt distincte și fiecare are casierie proprie.
- Se aplică plafonul de 10.000 lei (cash and carry) unui magazin obișnuit, fără să se verifice dacă activitatea se încadrează efectiv în definiția legală a magazinului de tip cash and carry.
- Se presupune că orice sediu secundar are automat casierie proprie, deși art. 8 condiționează aplicarea regulilor de existența efectivă a unei casierii sau a unui cont bancar propriu la acel sediu.
- Se ignoră interdicția de fragmentare: chiar dacă fiecare punct are propriul plafon, încasările fragmentate în numerar de la aceeași persoană, pentru aceeași factură/tranzacție, rămân interzise indiferent prin câte casierii ar fi împărțite artificial.

## Ce face iConta.eu

La data acestui ghid, iConta.eu verifică plafoanele de încasări și plăți în numerar prin `core/casa.py` (`verifica_plafon()`), cu constantele legale — 5.000 lei încasare de la persoană juridică, 10.000 lei pentru cash and carry, 10.000 lei încasare/plată de la persoană fizică — și cu soldul zilnic de casă preluat dinamic din registrul de cote (`c.cota("plafon_sold_casa", la_data)`). Calculul funcționează însă la nivelul unei singure casierii, pe tenant (schema firmei) — codul nu are conceptul de casierii multiple sau puncte de lucru separate (nu există câmp de tip „casierie_id" sau „punct_lucru" în modulul de casă). O firmă cu mai multe puncte de încasare distincte, fiecare cu casierie proprie conform art. 7-8, trebuie să urmărească separat, în afara aplicației, încadrarea în plafon pentru fiecare punct de lucru.

[iConta.eu](/)
