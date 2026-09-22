---
title: Cum aleg codul de taxă corect în SAF-T?
description: Codul de taxă (TaxCode) se alege dintr-un nomenclator oficial pe 6 cifre, dependent de cota de TVA și de data facturii pentru livrări; pentru achiziții, codul folosit e simplificat și nu reflectă gradul real de deductibilitate.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum aleg codul de taxă corect în SAF-T?

Fiecare linie de factură din SAF-T trebuie asociată cu un cod de taxă (`TaxCode`) din nomenclatorul oficial ANAF, format din 6 cifre. Regula diferă semnificativ între livrări și achiziții, iar aici se ascunde una dintre limitările cunoscute ale generării automate.

## Temeiul legal

::: ghid-temei
"|Tax Table (Tabelă taxe)| Conţine informaţii specifice despre taxe. În funcţie de tipul de
taxă (de exemplu, TVA), contribuabilul/plătitorul va selecta codurile de taxă din
nomenclatorul Coduri de taxă TVA pentru operaţiuni, asociate operaţiunilor incluse în
fişierul SAF-T."
(opanaf_1783_2021_saft_d406.txt, Anexa 1, pct. 5, tabelul cu structura AuditFile)
:::

## Livrări vs. achiziții — două logici diferite

Pentru **livrări**, codul de taxă se determină pe baza cotei reale de TVA de pe factură și a datei facturii, pentru că nomenclatorul oficial s-a schimbat odată cu majorarea cotelor de TVA prin Legea 141/2025:

- pentru facturi înainte de 1 august 2025: cotele vechi (19/9/5/0%) mapate pe codurile `310309`/`310310`/`310311`/`310312`;
- pentru facturi de la 1 august 2025: cotele noi (21/11/9/5/0%) mapate pe codurile `310344`/`310351`/`310357`/`310311`/`310312`.

O cotă necunoscută în tabela epocii respective nu blochează generarea, ci se raportează pe codul de taxare inversă (`310312`) și este semnalată nominal în avertismentele declarației — nu este ignorată tacit.

Pentru **achiziții**, regula este mult mai simplă și, deocamdată, simplificată: se folosește codul `300101` pentru taxare inversă sau cotă 0%, și codul `300501` fix, pentru tot restul — indiferent de gradul real de deductibilitate a TVA-ului (deducere integrală, pro-rata, nedeductibil).

::: ghid-exemplu
O achiziție cu TVA deductibil integral 100% primește codul `300501`. O achiziție cu deducere parțială pro-rata de 50% primește TOT codul `300501`, deoarece generarea automată nu diferențiază încă pe grade reale de deductibilitate — codul emis nu reflectă procentul real de deducere.
:::

Notele contabile fără document sursă (operațiuni de bancă, casă, creanțe fără TVA) și liniile de plată folosesc un cod separat, `380304` — singurul cod din familia notelor contabile fără TVA cu cotă 0 din nomenclatorul oficial.

## Ce se greșește în practică

- Se presupune că și codul de taxă pentru achiziții reflectă gradul real de deductibilitate — de fapt e simplificat, la doar două variante (`300101` / `300501`).
- Nu se verifică manual codul emis pentru achiziții cu deducere parțială (pro-rata), unde generarea automată nu diferențiază.
- Se ignoră avertismentele privind cotele de livrare necunoscute în tabela epocii, care sunt semnalate nominal, nu tăcut.
- Se aplică vechile coduri de cotă (19/9/5%) pentru facturi emise după 1 august 2025, când s-au schimbat cotele conform Legii 141/2025.
- Se confundă codul pentru note contabile fără document sursă (`380304`) cu un cod de operațiune comercială obișnuită.

## Ce face iConta.eu

Pentru livrări, codul de taxă este generat automat, ținând cont de data facturii (period-aware) — aplică tabela de cote corectă în funcție de dacă factura e emisă înainte sau după 1 august 2025 (Legea 141/2025), iar o cotă neobișnuită e semnalată nominal în avertismente, nu ignorată. Pentru achiziții, aplicația generează un cod simplificat (`300101` pentru taxare inversă/cotă 0, `300501` fix pentru rest) — acest lucru este recunoscut explicit ca o limitare curentă a modulului: codul de taxă pentru achiziții pe deductibilitate reală nu este încă implementat, iar orice contabil cu achiziții cu deducere parțială (pro-rata) trebuie să verifice manual codul emis înainte de depunere. Pentru notele contabile fără TVA, aplicația aplică automat codul dedicat `380304`.

[iConta.eu](/)
