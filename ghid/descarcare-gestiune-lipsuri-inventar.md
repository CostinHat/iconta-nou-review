---
title: Descărcarea de gestiune pentru lipsurile de la inventar
description: Orice lipsă se descarcă din gestiune la valoarea contabilă (60x=3xx), dar imputarea către vinovat nu generează TVA colectată — legea spune explicit că sumele imputate nu sunt în sfera TVA — în timp ce ajustarea TVA deductibile (635=4426) e obligatorie, indiferent dacă lipsa e imputată sau nu.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se descarcă gestiunea pentru lipsurile constatate la inventar?

O lipsă constatată la inventar înseamnă întotdeauna scoaterea bunului din gestiune la valoarea lui contabilă — asta e pasul comun, indiferent de cauză. Ce diferă radical e ce se întâmplă mai departe cu TVA: imputarea unei sume către vinovat și ajustarea taxei deductibile sunt două operațiuni complet separate, guvernate de reguli diferite, iar confuzia dintre ele e una dintre cele mai costisitoare greșeli la un control.

## Temeiul legal

::: ghid-temei
**OMFP 2861/2009, Anexă, pct. 40 alin. (2)**: *„În cazul constatării unor lipsuri imputabile în gestiune, administratorii trebuie să impute persoanelor vinovate bunurile lipsă la valoarea lor de înlocuire."* — valoarea de înlocuire *„cuprinde prețul de cumpărare practicat pe piață, la care se adaugă taxele nerecuperabile, inclusiv TVA, cheltuielile de transport, aprovizionare și alte cheltuieli, accesorii necesare..."*

**pct. 41 alin. (3)**: *„Pentru pagubele constatate în gestiune răspund persoanele vinovate de producerea lor. Imputarea acestora se face la valoarea de înlocuire."*

**CF (Legea 227/2015) art. 304 alin. (1) lit. c)**: *„persoana impozabilă își pierde sau câștiga dreptul de deducere a taxei pentru bunurile mobile nelivrate și serviciile neutilizate."*

**art. 304 alin. (2) lit. a)**: *„Nu se ajustează deducerea inițială a taxei în cazul: a) bunurilor distruse, pierdute sau furate, în condițiile în care aceste situații sunt demonstrate sau confirmate în mod corespunzător de persoana impozabilă."*

**HG 1/2016 (Norme CF) pct. 78 alin. (6) lit. a)**: *„persoana impozabilă realizează o ajustare pozitivă sau, după caz, trebuie să efectueze o ajustare negativă a taxei deductibile în situații precum: a) bunuri lipsă în gestiune din alte cauze decât cele prevăzute la art. 304 alin. (2) din Codul fiscal. În cazul bunurilor lipsă din gestiune care sunt imputate, sumele imputate nu sunt considerate contravaloarea unor operațiuni în sfera de aplicare a TVA, indiferent dacă pentru acestea este sau nu obligatorie ajustarea taxei."*
:::

## Pasul comun: descărcarea de gestiune

Indiferent dacă lipsa e imputabilă sau nu, bunul iese din gestiune la valoarea lui contabilă: `60x = 3xx` — de exemplu `607 = 371` pentru mărfuri, `601 = 301` pentru materii prime. Asta e o operațiune contabilă simplă, aceeași în toate cazurile.

## Imputarea: o creanță bănească, nu o vânzare

Dacă lipsa e imputabilă, administratorii impută persoanei vinovate bunul lipsă la valoarea de înlocuire (preț de piață + taxe nerecuperabile, inclusiv TVA, + cheltuieli accesorii). Contabil, creanța se înregistrează prin `4282 = 7581` (salariat) sau `461 = 7581` (terț), la valoarea de înlocuire stabilită.

Punctul esențial, spus fără echivoc de normele Codului fiscal: **„sumele imputate nu sunt considerate contravaloarea unor operațiuni în sfera de aplicare a TVA"**. Imputarea nu e o livrare de bunuri sau o prestare de servicii — e recuperarea unui prejudiciu de la persoana vinovată. Deci imputarea, ca atare, **nu generează TVA colectată** pe suma pretinsă gestionarului sau terțului, indiferent dacă valoarea de înlocuire include sau nu, ca element de calcul, echivalentul unei taxe.

## Ajustarea TVA deductibile: o operațiune separată, obligatorie

Lipsa bunului din gestiune poate declanșa totuși o ajustare a TVA deductibile deja exercitate la achiziția lui — dar acest lucru se judecă independent de imputare, după regula de la art. 304 alin. (1) lit. c) și pct. 78 alin. (6) lit. a): orice lipsă din alte cauze decât excepțiile de la art. 304 alin. (2) lit. a) (bun distrus, pierdut sau furat, demonstrat corespunzător) declanșează ajustarea, prin `635 = 4426`. Faptul că lipsa e imputată cuiva **nu scutește** de această ajustare — cele două lucruri nu se exclud reciproc. O lipsă imputabilă, nedovedită ca intrând în excepțiile legale, ar trebui să aibă, în același timp: imputarea creanței către vinovat (fără TVA colectată) **și** ajustarea TVA deductibile pe costul bunului lipsă.

## Ce se greșește în practică

- **Se pune TVA colectată pe valoarea imputată gestionarului**, ca și cum imputarea ar fi o vânzare — norma spune expres contrariul: sumele imputate nu sunt în sfera TVA.
- **Se renunță la ajustarea TVA deductibile pe motiv că lipsa oricum se recuperează de la vinovat** — ajustarea e legată de lipsa bunului din gestiune, nu de faptul că cineva răspunde pentru ea.
- **Se tratează "imputabil" ca sinonim cu "scutit de ajustare TVA"** — cele două noțiuni nu se suprapun. Excepția de la ajustare ține de dovada distrugerii, pierderii sau furtului (art. 304 alin. 2 lit. a), nu de existența unei persoane vinovate.

## Ce face iConta.eu

Pentru orice lipsă, aplicația generează nota de descărcare de gestiune la valoarea contabilă (`60x = 3xx`), pe baza corespondenței dintre contul de stoc și contul de cheltuială. Cota de TVA e un parametru obligatoriu la calculul lipsurilor, fără valoare implicită — aplicația nu ghicește o cotă. Tratamentul de TVA aplicat efectiv pe lipsurile imputabile — atât partea de TVA colectată la imputare, cât și ajustarea TVA deductibile — este în verificare și nu trebuie considerat conform până la confirmare separată; recomandăm ca, până atunci, ajustările de TVA legate de lipsuri imputabile să fie recalculate manual conform art. 304 și pct. 78 din normele Codului fiscal.

[iConta.eu](/)
