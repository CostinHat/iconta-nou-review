---
title: "Cum contabilizez un overdraft bancar?"
description: "Explică, la nivel general, cum se reflectă în contabilitate un descoperit de cont (overdraft) și prin ce diferă de un credit bancar clasic."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum contabilizez un overdraft bancar?

Un overdraft bancar (descoperit de cont) nu se contabilizează ca un credit clasic, cu recunoașterea unui principal primit — el se reflectă doar prin cheltuiala cu dobânda, atunci când apare.

## Temeiul legal

::: ghid-temei
"Cu ajutorul acestui cont [512] se ține evidența disponibilităților în lei și valută aflate în conturi la bănci [...] Contul 512 [...] este un cont bifuncțional. [...] – creditele bancare pe termen lung și scurt încasate (162, 519); [...] Soldul debitor reprezintă disponibilitățile în lei și în valută, iar soldul creditor creditele primite." — OMFP 1802/2014, monografia contului 512
:::

Spre deosebire de creditele bancare clasice — care au conturi de pasiv dedicate (162 pe termen lung, 519 pe termen scurt) și o notă explicită de primire a principalului (5121 = 1621 sau 5121 = 5191) — overdraft-ul nu are un cont propriu în planul de conturi. Baza pentru tratamentul lui este caracterul bifuncțional al contului 512: soldul creditor al contului curent reprezintă, practic, suma trasă peste disponibil. Termenul "descoperit de cont"/"overdraft" nu apare, ca atare, în OMFP 1802/2014; tratamentul de mai jos e o interpretare rezonabilă a acestei prevederi, nu un text explicit dedicat overdraft-ului.

În consecință, la overdraft nu se înregistrează o notă de primire a creditului și nu se urmărește contabil o limită de overdraft utilizată — singura înregistrare este cea a cheltuielii cu dobânda, în momentul plății: 666 = 5121.

## Ce se greșește în practică

O greșeală frecventă este tratarea overdraft-ului ca pe un credit pe termen scurt obișnuit, cu o notă de primire de tip 5121 = 5191 — acest lucru ar fi corect pentru un credit bancar clasic pe termen scurt, dar nu pentru overdraft, unde nu există o asemenea recunoaștere de principal.

O altă greșeală este căutarea unui cont sau a unei funcționalități dedicate "overdraft" în aplicație sau în planul de conturi — nu există un asemenea cont dedicat, doar interpretarea soldului creditor al contului 512.

## Ce face iConta.eu

Motorul de credite din iConta.eu acceptă strict tipurile de credit "lung" și "scurt" — nu există un al treilea tip "overdraft". Comportamentul specific overdraft-ului (fără notă de primire, doar cheltuiala cu dobânda: 666 = 5121) se obține prin nota de plată generică, folosită fără angajare prealabilă de dobândă și fără rată de principal, nu printr-o funcție dedicată.

[iConta.eu](/)
