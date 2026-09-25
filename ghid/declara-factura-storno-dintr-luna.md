---
title: "Cum se declară o factură storno dintr-o lună anterioară în D394?"
description: "Regula de declarare a facturilor storno în D394 și în ce lună apare o stornare care corectează o factură emisă anterior."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se declară o factură storno dintr-o lună anterioară în D394?

O factură storno nu „redeschide" luna facturii pe care o corectează. Ea e ea însăși un document nou, cu propria dată de emitere, și se declară în D394 al lunii în care a fost emisă — nu în declarația (deja depusă) a lunii facturii inițiale.

## Temeiul legal

::: ghid-temei
„2.2.1. seria şi numărul facturilor stornate; factura stornată reprezintă factura emisă de persoana impozabilă, a cărei valoare totală este negativă; [...] 6. Coloana «Baza impozabilă» de la lit. C, D, E, F [...] se înscrie valoarea bazei impozabile, în lei, aferentă livrărilor/prestărilor/achiziţiilor, [...] precum şi valoarea bazei impozabile aferentă facturilor de stornare, defalcate pe cote de TVA (24%, 21%, 20%, 19%, 11%, 9%, 5%). În cazul în care baza impozabilă este negativă valoarea totală a acesteia se înscrie cu semnul (-)."
— OPANAF 2194/2025, instrucțiuni de completare D394, pct. 2.2.1 și 6-7 (sursă: anaf_surse/opanaf_2194_2025_d394.txt)
:::

- Factura de stornare e, pentru D394, un document cu identitate proprie — are propriul număr, propria dată de emitere și propria serie — chiar dacă „corectează" o factură din altă lună.
- Baza impozabilă și TVA aferente stornării se înscriu **cu semnul minus**, defalcate pe cotele de TVA ale facturii originale — instrucțiunile D394 precizează explicit convenția de semn, spre deosebire de instrucțiunile D390, care nu o menționează.
- Stornarea unei facturi din luna anterioară nu obligă la o rectificativă a D394 din luna facturii inițiale: baza de calcul a D394 citește toate facturile emise/primite ale perioadei curente, inclusiv stornourile — o factură de stornare cu dată în luna curentă intră firesc în D394 al lunii curente.
- Cota de TVA de pe factura storno e **aceeași** cu cota facturii inițiale, nu una recalculată la data stornării — regula generală de stornare contabilă (OMFP 1802/2014) susține acest principiu: stornarea corectează exact ce s-a facturat greșit sau ce se anulează, nu introduce o valoare nouă.

## Ce se greșește în practică

- Se încearcă redepunerea sau corectarea D394 din luna facturii inițiale, în loc să se declare storno-ul simplu, în luna propriei date de emitere.
- Se omite semnul minus pe baza impozabilă și TVA ale stornării — instrucțiunile D394 îl cer explicit, spre deosebire de alte declarații unde convenția nu e precizată.
- Se recalculează cota de TVA a stornării la data emiterii ei, în loc să se păstreze cota facturii originale.

## Ce face iConta.eu

Motorul de stornare din iConta creează întotdeauna un document nou, cu număr propriu din aceeași serie, care păstrează cota de TVA și clasificarea fiscală ale facturii originale (inclusiv dacă originalul era intracomunitar sau cu taxare inversă) — doar sumele sunt negate. D394 citește toate facturile perioadei, inclusiv facturile storno (cu total negativ), fără o rutare specială: o factură de stornare emisă în luna curentă, pentru o factură din altă lună, apare firesc în D394 al lunii curente, cu bază și TVA negative. Aplicația nu are o funcție separată de „corectare a D394 dintr-o lună anterioară" — nu e nevoie, pentru că mecanismul legal de mai sus nu o cere: stornarea se declară simplu, la data ei, cu semnul minus.

[iConta.eu](/)
