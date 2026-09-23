---
title: Cum corectez o notă contabilă introdusă greșit?
description: În iConta.eu, o notă contabilă se corectează liber cât timp e ciornă. Odată validată, devine imutabilă — nu există funcție de „devalidare"; singura cale de corecție e o notă nouă de stornare. Perioada contabilă închisă blochează ambele operații.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum corectez o notă contabilă introdusă greșit?

Regula de aur a notelor contabile din iConta.eu e simplă și fără excepții: cât timp o notă e ciornă, se corectează liber; odată validată, se închide definitiv. Nu există în aplicație o funcție care să „devalideze" o notă și să o readucă la ciornă.

## Temeiul legal

::: ghid-temei
„În cazul completării documentelor prin utilizarea sistemelor informatice de prelucrare automată a datelor, corecturile sunt admise numai înainte de prelucrarea acestora." — OMFP 2634/2015, pct. 16

„Înregistrarea stornării unei operațiuni contabile aferente exercițiului financiar curent se efectuează fie prin corectarea cu semnul minus a operațiunii inițiale (stornare în roșu), fie prin înregistrarea inversă a acesteia (stornare în negru), în funcție de politica contabilă și programele informatice utilizate." — OMFP 1802/2014, Anexa 1 – Reglementări contabile, pct. 69
:::

„Prelucrarea" din text corespunde, în aplicație, momentului validării: până atunci, nota e un draft modificabil; după, e o înregistrare definitivă în Registrul-jurnal, corectabilă doar prin document nou.

## Cum corectez în iConta.eu

- **Nota e ciornă** → se editează liber: descriere, dată, conturi, sume pe linii. Condițiile rămân aceleași ca la creare — cel puțin o linie, debit și credit completate, conturi existente în planul firmei, sumă strict pozitivă pe fiecare linie.
- **Nota e validată** → orice încercare de editare sau ștergere e refuzată de aplicație, cu mesajele exacte „doar ciornele se pot edita" / „doar ciornele se pot șterge". Singura corecție posibilă e o notă nouă, cu sumele/sensul inversat (stornare), pe principiul pct. 69 de mai sus.
- **Perioada contabilă** contează separat de statutul notei: chiar și o notă-ciornă nu se poate edita, șterge sau valida dacă luna ei e închisă administrativ — aplicația refuză cu „Perioada e blocată (luna închisă). Cere-i administratorului cabinetului să o redeschidă sau înregistrează în luna curentă."
- Dacă nota e chiar evidența contabilă a unei facturi (nota de contare), ea nu se poate „dezlega" de factură ca și cum ar fi o plată greșit atașată — aplicația refuză explicit acest tip de operație pentru notele de contare, cu mesajul „Nota E chiar evidența contabilă a facturii, nu o plată. [...] Dacă factura trebuie corectată, se stornează." Corecția trece atunci prin stornarea facturii, nu prin desfacerea notei.

## Ce se greșește în practică

- Se încearcă modificarea unei note deja validate, așteptând ca aplicația să o permită — validarea e ireversibilă în cod, nu există buton de „revenire la ciornă".
- Se confundă „dezlegarea" unei note (utilă pentru o plată legată greșit de o factură) cu corectarea unei note de contare — pentru nota de contare, dezlegarea e refuzată explicit, corecția fiind exclusiv prin stornarea facturii.
- Se ignoră poarta de perioadă: chiar dacă nota e ciornă, dacă luna ei a fost închisă între timp, corecția rămâne blocată până la redeschiderea perioadei sau până se lucrează în luna curentă.

## Ce face iConta.eu

O notă contabilă se corectează liber cât e ciornă — descriere, conturi, sume, dată — direct din Registrul jurnal. Odată validată, devine imutabilă: nu există în aplicație o funcție de „devalidare", iar orice corecție ulterioară se face printr-o notă nouă de stornare. Perioada contabilă închisă blochează ambele tipuri de operații, indiferent de statutul notei.

[iConta.eu](/)
