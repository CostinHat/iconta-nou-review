---
title: "Cum contabilizez dobânda plătită pentru descoperitul de cont?"
description: "Ghid practic, pas cu pas, pentru înregistrarea în iConta.eu a dobânzii plătite pentru un descoperit de cont (overdraft)."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum contabilizez dobânda plătită pentru descoperitul de cont?

Spre deosebire de dobânda la un credit clasic, dobânda plătită pentru un descoperit de cont se înregistrează printr-o singură notă contabilă, direct pe cheltuială, fără o etapă anterioară de angajare.

## Temeiul legal

::: ghid-temei
"Cu ajutorul acestui cont [512] se ține evidența disponibilităților în lei și valută aflate în conturi la bănci [...] Contul 512 [...] este un cont bifuncțional. [...] Soldul debitor reprezintă disponibilitățile în lei și în valută, iar soldul creditor creditele primite." — OMFP 1802/2014, monografia contului 512
:::

Nota contabilă pentru dobânda plătită la overdraft este simplă: 666 = 5121 — cheltuiala cu dobânda se înregistrează direct la ieșirea sumei din contul curent, fără trecerea printr-un cont de dobândă angajată (spre deosebire de 1682 sau 5198, folosite la creditele clasice).

## Ce se greșește în practică

Cea mai frecventă greșeală este bifarea/setarea implicită "dobândă angajată" la plata dobânzii de overdraft — dacă se procedează astfel, aplicația va încerca să stingă un cont de dobândă angajată (1682 sau 5198) care nu a fost niciodată alimentat pentru overdraft, ceea ce produce o înregistrare eronată.

O altă greșeală este includerea, din obișnuință, a unei rate de principal sau a unui comision în aceeași notă, deși la overdraft nu există, de regulă, o rată de principal distinctă de urmărit.

## Ce face iConta.eu

Pentru a înregistra dobânda plătită la un overdraft, nota de plată din iConta.eu trebuie completată cu suma dobânzii, cu opțiunea "dobândă angajată" dezactivată și fără rată de principal sau comision — rezultatul este o notă contabilă cu o singură linie: 666 = 5121, pe contul bancar indicat. Aplicația nu are un tip de credit "overdraft" separat; acest rezultat se obține prin nota de plată generică, folosită cu parametrii de mai sus.

[iConta.eu](/)
