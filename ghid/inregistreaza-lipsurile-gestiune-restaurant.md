---
title: Cum se înregistrează lipsurile de gestiune într-un restaurant?
description: Nota contabilă de minus la inventar diferă după cum lipsa e imputabilă unui salariat, unui terț, sau neimputabilă — și, în acest ultim caz, după cum e sau nu dovedită.
published: 2026-09-24
modified: 2026-10-13
poarta: v1
---

# Cum se înregistrează lipsurile de gestiune într-un restaurant?

O lipsă constatată la inventar (marfă, materii prime, produse finite) nu se înregistrează niciodată la fel indiferent de cauză. Contabilitatea trebuie să răspundă întâi la o întrebare: cine răspunde de lipsă — și dacă răspunde cineva.

## Temeiul legal

::: ghid-temei
"cheltuielile privind bunurile de natura stocurilor sau a mijloacelor fixe amortizabile constatate lipsă din gestiune ori degradate, neimputabile, precum și taxa pe valoarea adăugată aferentă, dacă aceasta este datorată potrivit prevederilor titlului VII. Aceste cheltuieli sunt deductibile în următoarele situații/condiții: [...]" — Codul fiscal (Legea 227/2015, consolidat), art. 25 alin. (4) lit. c)
:::

Regula generală e strictă: cheltuiala cu bunul lipsă, **neimputabil**, e nedeductibilă, cu excepția a șapte situații enumerate limitativ în lege (calamitate naturală/forță majoră, bunuri asigurate, degradare calitativă dovedită prin distrugere, alimente aproape de expirare transferate conform normelor de reducere a risipei alimentare, și alte câteva cazuri similare). O lipsă "pur și simplu", fără nicio dovadă și fără asigurare, nu e automat deductibilă.

Pentru TVA, tratamentul depinde de aceeași distincție — dovedit/nedovedit, nu doar asigurat/neasigurat:

::: ghid-temei
"Nu se ajustează deducerea inițială a taxei în cazul: a) bunurilor distruse, pierdute sau furate, în condițiile în care aceste situații sunt demonstrate sau confirmate în mod corespunzător de persoana impozabilă. În cazul bunurilor furate, persoana impozabilă demonstrează furtul bunurilor pe baza actelor doveditoare emise de organele judiciare." — Codul fiscal, art. 304 alin. (2) lit. a)
:::

Dacă lipsa nu poate fi demonstrată/confirmată, se pierde dreptul de deducere a TVA aferente bunurilor lipsă (art. 304 alin. (1) lit. c)) și taxa se ajustează.

Pentru partea **imputabilă** (lipsa recuperată de la salariatul sau terțul vinovat), regimul e diferit: cheltuiala cu descărcarea de gestiune e compensată de venitul din imputare, iar acest caz nu intră sub excepțiile de deductibilitate ale art. 25 alin. (4) lit. c), care vizează explicit lipsurile "neimputabile".

## Ce se greșește în practică

- Se înregistrează orice lipsă direct pe cheltuială deductibilă, fără verificarea celor șapte condiții limitative din art. 25 alin. (4) lit. c).
- Se presupune că lipsa e "automat" scutită de ajustare TVA dacă marfa era asigurată — legea cere ca situația să fie **demonstrată sau confirmată corespunzător**, nu doar existența unei polițe de asigurare.
- Se confundă imputarea către salariat cu o simplă notare administrativă, fără înregistrarea creanței (4282 sau 461 = 7581) — sau, invers, se colectează TVA pe valoarea de imputare, deși sumele imputate pentru bunuri lipsă nu sunt în sfera de aplicare a TVA (HG nr. 1/2016, titlul VII, pct. 78 alin. (6) lit. a)).

## Ce face iConta.eu

Operația "Minus" din ecranul de inventariere cere obligatoriu cota de TVA — aplicația nu propune o cotă implicită, tocmai ca să nu aplice tacit o cotă depășită după o schimbare a legii. Ecranul distinge:

- **minus imputabil** — salariat (4282 = 7581) sau terț (461 = 7581), la valoarea de imputare, fără TVA: sumele imputate pentru bunuri lipsă nu sunt considerate contravaloarea unor operațiuni în sfera de aplicare a TVA (HG nr. 1/2016, titlul VII, pct. 78 alin. (6) lit. a));
- **minus pentru un bun neasigurat sau nedemonstrat ca distrus** — pe lângă descărcarea de gestiune, se generează și ajustarea TVA deduse (635 = 4426), calculată cu cota introdusă, pe costul bunului lipsă, fie că lipsa e imputabilă, fie că nu;
- **minus pentru un bun asigurat sau dovedit distrus** — fără linia de ajustare TVA.

Pentru operația "Minus", formularul cere: valoarea (costul bunului lipsă), contul de stoc, „Imputabil” (Da/Nu — la Da apar „Valoare imputare” și „Cui se impută”: salariat sau terț), „Cota TVA %” și „Bunul lipsă era asigurat sau a fost distrus” (Da/Nu). „Cota TVA %” e obligatorie și la lipsurile imputabile: cifra 21 afișată în câmpul gol e doar un exemplu, nu o valoare completată, iar fără cotă scrisă nota nu se generează. Cota se folosește numai la ajustarea TVA deduse pe bunul lipsă (635 = 4426), când la „asigurat sau distrus” ați răspuns Nu; suma imputată nu poartă TVA.

[iConta.eu](/)
