---
title: "Cum înregistrez rambursarea principalului unui credit?"
description: "Explică nota contabilă pentru rambursarea ratei de principal la un credit bancar pe termen lung sau scurt, și reclasificarea ratelor neplătite la scadență."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum înregistrez rambursarea principalului unui credit?

Rambursarea ratei de principal la un credit bancar se înregistrează distinct de plata dobânzii, pe contul de credit corespunzător tipului acestuia (termen lung sau termen scurt).

## Temeiul legal

::: ghid-temei
"Cu ajutorul acestui cont [162] se ține evidența creditelor bancare pe termen lung primite de entitate. Contul 162 [...] este un cont de pasiv. În creditul contului 162 [...] se înregistrează: – suma creditelor pe termen lung primite (512); [...] În debitul contului 162 [...] se înregistrează: – suma creditelor pe termen lung rambursate (512); [...] Soldul contului reprezintă creditele bancare pe termen lung nerambursate." — OMFP 1802/2014, monografia contului 162
:::

Pentru un credit pe **termen lung**, rambursarea unei rate de principal se înregistrează 1621 = 5121. Pentru un credit pe **termen scurt**, mecanismul e simetric, pe contul analitic 5191: rambursarea se înregistrează 5191 = 5121. Rata de principal este independentă de dobândă și de eventualul comision bancar, chiar dacă, în practică, toate trei pot fi plătite prin aceeași notă compusă, în aceeași zi.

Dacă o rată nu este plătită la scadență, ea se reclasifică din creditul curent în restanță, pe analiticul dedicat: 1621 = 1622 (termen lung), respectiv 5191 = 5192 (termen scurt). Existența acestor analitice de restanță (1622, 5192) este confirmată de planul de conturi, deși OMFP 1802/2014 nu descrie explicit, în text narativ, mecanica exactă a acestei reclasificări interne — e o practică uzuală de contabilizare, nu o prevedere citabilă cuvânt cu cuvânt pentru acest pas.

## Ce se greșește în practică

O greșeală frecventă este amestecarea ratei de principal cu dobânda într-o singură linie contabilă pe 666, în loc de a le trata separat: rata reduce datoria de credit (1621 sau 5191), în timp ce dobânda este o cheltuială (666).

O altă greșeală este omiterea reclasificării ratei neplătite la scadență în contul de restanță (1622/5192) — fără această reclasificare, soldul creditului curent nu mai reflectă corect ce este restant și ce este încă în termen.

## Ce face iConta.eu

Nota de plată din iConta.eu generează automat linia de rambursare a principalului corespunzătoare tipului de credit — 1621 = 5121 pentru termen lung, 5191 = 5121 pentru termen scurt — și poate combina, în aceeași notă compusă, rata, dobânda (dacă a fost angajată anterior) și comisionul bancar. Pentru ratele neplătite la scadență, aplicația oferă o notă separată de reclasificare la restanță: 1621 = 1622, respectiv 5191 = 5192.

[iConta.eu](/)
