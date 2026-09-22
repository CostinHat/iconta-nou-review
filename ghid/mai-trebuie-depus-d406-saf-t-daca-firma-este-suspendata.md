---
title: Mai trebuie depus D406 SAF-T dacă firma este suspendată?
description: Nu — o firmă cu activitate suspendată temporar la Registrul Comerțului (sau cu suspendare aprobată de organismul care a autorizat-o) este exceptată explicit de la obligația D406, pe toată perioada suspendării.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Mai trebuie depus D406 SAF-T dacă firma este suspendată?

Suspendarea temporară a activității este o situație frecventă pentru firmele mici cu activitate sezonieră sau întreruptă temporar. Legea tratează explicit acest caz pentru obligația D406, printr-o excepție dedicată.

## Temeiul legal

::: ghid-temei
"4. Următoarele categorii de contribuabili nu au obligaţia de depunere a fişierului standard
de control fiscal (SAF-T): ... o) persoanele juridice a căror activitate este suspendată temporar
prin înscrierea menţiunilor la registrul comerţului nu au obligaţia de depunere a fişierului
standard de control fiscal (SAF-T) pentru perioada în care activitatea este suspendată
temporar, conform art. 101 alin. (41) din Legea nr. 207/2015 privind Codul de procedură
fiscală, cu modificările şi completările ulterioare; p) alte entităţi care au solicitat
suspendarea activităţii la organismele care le-au autorizat nu au obligaţia de depunere a
fişierului standard de control fiscal (SAF-T) pentru perioada în care activitatea este
suspendată temporar, conform art. 101 alin. (42) din Legea nr. 207/2015 privind Codul de
procedură fiscală, cu modificările şi completările ulterioare;"
(opanaf_407_2025_saft_d406.txt, pct. 4, lit. o-p)
:::

## Ce înseamnă concret exceptarea

Sunt două situații distincte, acoperite de litere diferite:

- **litera o)** — persoana juridică are activitatea suspendată prin înscrierea mențiunii la Registrul Comerțului, temei art. 101 alin. (41) din Codul de procedură fiscală (Legea 207/2015);
- **litera p)** — alte entități care au solicitat suspendarea activității la organismele care le-au autorizat (nu la Registrul Comerțului), temei art. 101 alin. (42) din același Cod de procedură fiscală.

În ambele cazuri, exceptarea este valabilă strict **pentru perioada** în care activitatea este efectiv suspendată — nu este o scutire permanentă. Odată ce mențiunea de suspendare este radiată și firma reia activitatea, obligația de depunere D406 redevine aplicabilă pentru perioadele ulterioare reluării.

::: ghid-exemplu
O firmă are activitatea suspendată la Registrul Comerțului din 1 martie 2026 până în 31 august 2026. Pentru lunile martie–august 2026 nu are obligația de a depune D406. Dacă reia activitatea din septembrie 2026, obligația de raportare D406 se aplică din nou începând cu perioada septembrie 2026 (cu termen de depunere 31 octombrie 2026, dacă raportează lunar).
:::

## Ce se greșește în practică

- Se presupune că suspendarea temporară scutește firma de D406 pe termen nelimitat, inclusiv după reluarea activității.
- Se confundă suspendarea la Registrul Comerțului (litera o) cu suspendarea aprobată de alt organism autorizator (litera p) — temeiurile legale diferă (alin. 41 vs. alin. 42), deși efectul practic e similar.
- Nu se verifică data exactă de înscriere/radiere a mențiunii de suspendare, ceea ce duce la calcularea greșită a perioadei exceptate.
- Se depune totuși un D406 "gol" pentru perioada de suspendare, deși legea nu cere acest lucru — nu este o eroare, dar nici o obligație.

## Ce face iConta.eu

Motorul de generare D406 din aplicație nu conține, în codul verificat, o verificare automată a statutului de suspendare al firmei care să blocheze sau să sară peste generarea declarației pe perioada suspendării — decizia de a nu depune D406 pentru lunile/trimestrele în care activitatea e suspendată rămâne, pe baza informațiilor verificate, în sarcina contabilului, aplicând direct excepția de la literele o) și p) de mai sus. Ce este cablat corect în aplicație este calculul tipului de raportare (lunar/trimestrial) și al termenelor pentru perioadele în care firma este activă și obligată să raporteze.

[iConta.eu](/)
