---
title: Cum împac gestiunea cu raportul fiscal zilnic
description: Gestiunea global-valorică nu se închide pe fiecare raport Z, ci lunar, pe totalul veniturilor din vânzarea mărfurilor — încercarea de a o „împăca" zilnic cu fiecare Z e o presupunere greșită despre mecanism.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum împac gestiunea cu raportul fiscal zilnic

Întrebarea presupune de multe ori că gestiunea și Raportul Z ar trebui să se potrivească document cu document, zi cu zi. Nu e așa — sunt două ritmuri diferite, iar „împăcarea" se face la nivel de lună, nu de zi.

## Temeiul legal

::: ghid-temei
„Repartizarea diferențelor de preț asupra valorii bunurilor ieșite și asupra stocurilor se efectuează cu ajutorul unui coeficient [...]" — OMFP 1802/2014, pct. 286 alin. (4), metoda coeficientului de repartizare a adaosului comercial (comerțul cu amănuntul)
:::

## De ce nu se potrivesc zi cu zi

Raportul Z e un document **zilnic** — totalul vânzărilor pe cote de TVA și pe tip de plată, dintr-o singură zi fiscală.

Descărcarea de gestiune, pentru firmele care țin evidența mărfurilor global-valoric (tipic pentru restaurant/comerț cu amănuntul, fără articol identificat la fiecare vânzare), e o operațiune **lunară**. Coeficientul de repartizare a adaosului comercial (K) se calculează cumulat de la începutul exercițiului financiar, din soldurile conturilor 378 (adaos), 371 (mărfuri la preț de vânzare) și 4428 (TVA neexigibilă) — nu din datele unei singure zile.

Deci „împăcarea" corectă e: suma veniturilor din vânzarea mărfurilor (707) ale întregii luni, cumulate din toate rapoartele Z ale lunii, trebuie să corespundă cu baza pe care se aplică descărcarea lunară de gestiune — nu fiecare Z în parte cu o descărcare proprie.

## Ce se greșește în practică

Așteptarea unei descărcări de gestiune „pe fiecare Z" — mecanismul global-valoric nu funcționează așa; a forța o descărcare zilnică pe un coeficient K calculat cumulat de la începutul anului ar da rezultate incoerente. A doua greșeală: uitarea descărcării lunare complet, pentru că nu există un declanșator automat legat de fiecare Raport Z introdus — trebuie inițiată explicit, cel puțin o dată pe lună.

## Ce face iConta.eu

Descărcarea de gestiune (butonul „Descarcă gestiunea GV" sau echivalentul din ecranul de stocuri) se calculează pe luna calendaristică aleasă, din soldurile curente ale conturilor 378/371/4428 și din rulajul de credit al contului 707 din acea lună — indiferent din câte rapoarte Z provine acel rulaj. Nu există o legătură automată „un Z = o descărcare"; verificarea corectă e la nivel de lună, comparând totalul 707 din toate notele Z cu baza folosită la descărcare.

[iConta.eu](/)
