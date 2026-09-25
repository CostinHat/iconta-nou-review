---
title: "Când se declară avansurile în D390?"
description: "Instrucțiunile de completare D390 spun explicit când o factură de avans pentru o operațiune intracomunitară intră în baza declarației."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Când se declară avansurile în D390?

Un avans încasat sau plătit pentru o livrare sau achiziție intracomunitară de bunuri nu așteaptă factura finală ca să intre în D390. Instrucțiunile de completare a declarației spun expres, pentru fiecare tip de operațiune cu bunuri, că suma din factura de avans se include în baza lunii în care ia naștere exigibilitatea taxei.

## Temeiul legal

::: ghid-temei
„a) «Livrări intracomunitare de bunuri» - se înscrie suma totală a livrărilor intracomunitare de bunuri scutite de la plata taxei în condiţiile art. 294 alin. (2) lit. a) şi d) din Codul fiscal, pe fiecare cumpărător, pentru care exigibilitatea taxei ia naştere în luna calendaristică respectivă, **inclusiv sumele din facturile pentru încasări de avansuri pentru livrări intracomunitare de bunuri, scutite**;
c) «Achiziţii intracomunitare de bunuri» - se înscrie suma totală a achiziţiilor intracomunitare de bunuri, pe fiecare furnizor, pentru care persoana impozabilă, care depune declaraţia, este obligată la plata taxei conform art. 308 din Codul fiscal şi pentru care exigibilitatea taxei intervine în luna calendaristică respectivă, **inclusiv sumele din facturile primite pentru plăţi de avansuri pentru achiziţii intracomunitare de bunuri**;"
— OPANAF 705/2020, Anexa 2, Instrucțiuni pct. 1, literele a) și c) (sursă: anaf_surse/opanaf_705_2020_d390.txt)
:::

Regula, așa cum apare explicit în text, se aplică simetric pe toate cele patru tipuri de operațiuni cu bunuri:

- **livrări intracomunitare de bunuri (L)** — avansurile încasate pentru o livrare scutită intră în baza lunii avansului;
- **livrări ulterioare în operațiuni triunghiulare (T)** — la fel, „inclusiv sumele din facturile pentru încasări de avansuri";
- **achiziții intracomunitare de bunuri (A)** — avansurile plătite intră în baza lunii avansului, pe baza facturii primite;
- **livrări în regimul special pentru agricultori (R)** — aceeași regulă, explicit menționată.

Pentru **prestările/achizițiile intracomunitare de servicii (P/S)**, textul instrucțiunilor nu conține aceeași mențiune explicită despre avansuri — baza se raportează la exigibilitate potrivit regulii generale de la art. 278 alin. (2) din Codul fiscal, fără o precizare separată despre facturile de avans.

## Ce se greșește în practică

- Se presupune că avansul „nu se declară", pentru că nu e o livrare/achiziție finalizată — și se declară doar la factura finală, ceea ce poate duce fie la omisiunea sumei din luna corectă, fie la raportarea dublă dacă factura finală reia integral suma deja avansată.
- Se confundă luna facturii de avans cu luna în care ia naștere exigibilitatea taxei — cele două pot să nu coincidă, mai ales la achizițiile intracomunitare.
- Se aplică aceeași logică de „avans declarat separat" și la operațiunile cu servicii (P/S), deși textul citat mai sus le tratează explicit doar pentru bunuri.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu are un tratament separat pentru facturile de avans** în motorul D390. Orice factură emisă sau primită pentru o operațiune intracomunitară — inclusiv una emisă pentru un avans — intră în același motor de clasificare automată descris în ghidul dedicat clasificării manuale D390: e clasificată implicit pe axa bunuri/servicii de pe document (livrare→L, achiziție→A) și poate fi reclasificată manual în pasul 2 al declarației, dacă e cazul.

Nu există în aplicație o verificare separată care să identifice o factură ca fiind „de avans" și să o trateze diferit de o factură obișnuită — corectitudinea includerii sumei în luna corectă a exigibilității rămâne, pentru acest caz, în sarcina contabilului, la fel ca la orice altă factură intracomunitară.

[iConta.eu](/)
