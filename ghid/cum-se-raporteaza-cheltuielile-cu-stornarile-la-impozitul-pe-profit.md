---
title: Cum se raportează cheltuielile cu stornările la impozitul pe profit
description: O stornare din exercițiul financiar curent afectează normal contul de profit și pierdere al perioadei; una pentru o factură dintr-un an anterior deja închis ar trebui să treacă prin 1174, nu direct prin venituri curente — distincție pe care motorul de storno nu o face automat.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se raportează cheltuielile cu stornările la impozitul pe profit

O stornare nu e neapărat o „cheltuială" în sensul clasic — e o corecție de venit, cu semn minus. Dar efectul ei asupra rezultatului fiscal impozitat cu impozit pe profit depinde decisiv de un singur lucru: dacă factura originală aparține exercițiului financiar curent sau unuia anterior, deja închis prin depunerea situațiilor financiare.

## Temeiul legal

::: ghid-temei
„65. ‐ (1) Erorile constatate în contabilitate se pot referi fie la exercițiul financiar curent, fie la exercițiile financiare precedente. (2) Corectarea erorilor se efectuează la data constatării lor."

„67. ‐ (1) Corectarea erorilor aferente exercițiului financiar curent se efectuează pe seama contului de profit și pierdere. (2) Corectarea erorilor semnificative aferente exercițiilor financiare precedente se efectuează pe seama rezultatului reportat (contul 1174 «Rezultatul reportat provenit din corectarea erorilor contabile»). (3) Erorile nesemnificative aferente exercițiilor financiare precedente se corectează, de asemenea, pe seama rezultatului reportat. Totuși, potrivit politicilor contabile aprobate, erorile nesemnificative pot fi corectate pe seama contului de profit și pierdere." — OMFP 1802/2014, secțiunea 2.5.2, pct. 65-68

„Articolul 36^2 Erorile constatate după depunerea situațiilor financiare anuale se corectează la data constatării lor, potrivit reglementărilor contabile emise de instituțiile prevăzute la art. 4 alin. (1) și (3), după caz." — Legea contabilității nr. 82/1991, art. 36^2
:::

## Diferența dintre exercițiul curent și unul închis

Când factura originală aparține exercițiului financiar curent, corecția (stornarea, cu minus, a venitului) intră firesc în contul de profit și pierdere al perioadei curente — reduce rezultatul contabil curent, deci și baza impozitului pe profit curent. E situația „normală", acoperită de mecanismul de stornare obișnuit.

Când factura originală aparține unui an financiar deja închis, cu situații financiare depuse, regula se schimbă: pct. 67 alin. (2) cere ca eroarea semnificativă să fie corectată pe seama rezultatului reportat (contul 1174), nu pe seama contului de profit și pierdere curent. Practic, o astfel de corecție **nu ar trebui să afecteze impozitul pe profit al perioadei curente** — ea privește rezultatul fiscal al anului în care factura a fost emisă inițial, care se corectează separat, de regulă printr-o declarație rectificativă pentru acel an. Pentru erorile nesemnificative, politica contabilă proprie a firmei poate permite totuși corecția directă pe contul de profit și pierdere curent — dar aceasta e o alegere documentată, nu regula implicită.

::: ghid-exemplu
O factură de 20.000 lei emisă acum doi ani se stornează azi. Dacă suma intră, cu minus, direct în veniturile anului curent (707), rezultatul fiscal curent scade artificial cu 20.000 lei — deși venitul respectiv a fost deja impozitat, corect, în anul emiterii. Tratamentul corect: corecția trece prin 1174 (dacă e eroare semnificativă), iar impactul asupra impozitului pe profit se rezolvă printr-o rectificare a declarației aferente anului în care a fost emisă factura originală.
:::

## Ce se greșește în practică

- Se raportează automat orice storno ca o reducere a cheltuielilor/veniturilor perioadei fiscale curente, indiferent de anul facturii originale.
- Nu se face distincția între eroare semnificativă și nesemnificativă, deși tratamentul contabil diferă (1174 obligatoriu vs. opțional pe P&L curent, conform politicii contabile).
- Nu se depune declarație rectificativă de impozit pe profit pentru anul în care factura originală a fost efectiv emisă și impozitată.
- Se așteaptă ca sistemul să semnaleze automat „factură din an anterior" la storno — motorul nu face această verificare.

## Ce face iConta.eu

Funcția de storno (`storneaza`) creează întotdeauna documentul nou cu data curentă, indiferent de anul facturii originale, iar nota automată generată din liniile cu cantitate negativă scrie mereu pe conturile de venit curent (707/701/703/704) — niciodată pe 1174. Sistemul nu verifică exercițiul financiar al facturii originale la storno. Pentru facturi din ani anteriori, distincția dintre corecție pe P&L curent și corecție pe 1174, precum și eventuala rectificare a declarației de impozit pe profit pentru anul corect, rămân responsabilitatea contabilului — sunt pași manuali, în afara motorului automat de contare.

[iConta.eu](/)
