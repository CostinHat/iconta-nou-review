---
title: "Cum se tratează dobânzile la overdraft"
description: "Explică de ce dobânda la overdraft se înregistrează direct pe cheltuială, fără un cont de dobândă angajată dedicat, spre deosebire de creditele bancare clasice."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se tratează dobânzile la overdraft

Descoperitul de cont (overdraft) nu are un cont dedicat în planul de conturi și nu presupune recunoașterea unui principal separat, așa cum se întâmplă la un credit bancar clasic — de aceea și dobânda lui se tratează diferit.

## Temeiul legal

::: ghid-temei
"Cu ajutorul acestui cont [512] se ține evidența disponibilităților în lei și valută aflate în conturi la bănci [...] Contul 512 [...] este un cont bifuncțional. [...] – creditele bancare pe termen lung și scurt încasate (162, 519); [...] Soldul debitor reprezintă disponibilitățile în lei și în valută, iar soldul creditor creditele primite." — OMFP 1802/2014, monografia contului 512
:::

Termenul "descoperit de cont" sau "overdraft" nu apare verbatim în OMFP 1802/2014. Baza pentru tratamentul lui este caracterul **bifuncțional** al contului 512: un sold creditor al contului curent reprezintă, în esență, o sumă trasă peste disponibil, adică un credit implicit — spre deosebire de creditele clasice (162 pe termen lung, 519 pe termen scurt), care au conturi de pasiv dedicate, cu recunoașterea separată a principalului.

Din această cauză, dobânda la overdraft nu se angajează separat pe un cont de tip 1682 sau 5198, așa cum se întâmplă la un credit clasic. Ea se recunoaște direct pe cheltuială, în momentul plății: 666 = 5121.

## Ce se greșește în practică

O greșeală tipică este folosirea, prin analogie cu creditele clasice, a conturilor de dobândă angajată 1682 sau 5198 și pentru overdraft — acestea nu au corespondent la overdraft, pentru că nu există niciun principal recunoscut separat față de care să se angajeze o dobândă.

O altă greșeală este așteptarea unei note de "primire a creditului" (similară cu 5121 = 1621/5191 de la creditele clasice) și la deschiderea unei facilități de overdraft — la overdraft nu se înregistrează o astfel de primire, doar cheltuiala cu dobânda, atunci când apare.

## Ce face iConta.eu

Aplicația nu are un tip de credit dedicat "overdraft" — motorul de credite acceptă strict tipurile `lung` și `scurt`. Tratamentul specific overdraft-ului (666 = 5121, fără angajare separată de dobândă) se obține ca efect al notei de plată, atunci când dobânda nu a fost angajată în prealabil pe un cont dedicat: se plătește direct din contul curent, fără rată de principal și fără comision asociat.

[iConta.eu](/)
