---
title: "Vânzare în țară de bunuri cu risc fiscal ridicat: furnizorul sau clientul declară în RO e-Transport?"
description: "Furnizorul din România. La tranzacțiile interne cu bunuri cu risc fiscal ridicat, el declară transportul, obține codul UIT și îl transmite transportatorului înainte de plecare."
published: 2026-09-29
modified: 2026-09-29
poarta: v1
---

# Vânzare în țară de bunuri cu risc fiscal ridicat: furnizorul sau clientul declară în RO e-Transport?

**Furnizorul din România.** La o tranzacție internă cu bunuri cu risc fiscal ridicat, obligația de declarare în RO e-Transport îi revine lui, indiferent cine organizează transportul. Clientul nu declară nimic, nici atunci când vine cu propria mașină să ridice marfa.

În practică, furnizorul obține codul UIT și îl transmite transportatorului sau șoferului clientului până la plecarea vehiculului. Dacă furnizorul nu declară, sancțiunea îl privește pe el, ca utilizator obligat de lege, nu pe client.

## Temeiul legal

::: ghid-temei
„(1) Obligația declarării în Sistemul RO e-Transport a datelor prevăzute la art. 4 alin. (1) lit. a) referitoare la transportul bunurilor cu risc fiscal ridicat revine următorilor utilizatori: [...] c) furnizorului din România, în cazul tranzacțiilor interne sau al livrărilor intracomunitare de bunuri cu risc fiscal ridicat, după caz;"
— OUG 41/2022, art. 8 alin. (1) lit. c) (sursă: [OUG nr. 41/2022 pentru instituirea Sistemului național RO e-Transport](https://legislatie.just.ro/Public/DetaliiDocument/253801))

„(2) Utilizatorii prevăzuți la alin. (1) sunt obligați să pună la dispoziția operatorului de transport rutier codul UIT aferent bunurilor transportate, direct sau prin intermediul organizatorului transportului, după caz, până cel târziu la prezentarea vehiculului în punctul rutier de trecere a frontierei la intrarea în România sau la locul de import, respectiv la punerea efectivă în mișcare a vehiculului, după caz."
— OUG 41/2022, art. 8 alin. (2) (sursă: [OUG nr. 41/2022 pentru instituirea Sistemului național RO e-Transport](https://legislatie.just.ro/Public/DetaliiDocument/253801))
:::

Ce face furnizorul, pas cu pas:

- **Verifică încadrarea**: bunurile sunt pe lista stabilită prin ordin al președintelui ANAF (codurile NC), iar transportul are punctul de plecare și punctul de sosire în România (art. 2 pct. 2).
- **Declară datele** (partener, bunuri, cantități, valoare, traseu, vehicul) cu cel mult 3 zile calendaristice înainte de data declarată pentru începerea transportului, dar până la punerea efectivă în mișcare a vehiculului (art. 11 alin. (1)).
- **Transmite codul UIT** transportatorului, direct sau prin organizatorul transportului, cel târziu la plecarea vehiculului.
- **Declară toată partida** dacă în ea sunt și bunuri din afara listei (art. 12 alin. (1)).

Codul UIT este valabil 5 zile calendaristice de la data declarată pentru începerea transportului (art. 11 alin. (2)).

::: ghid-exemplu
SC Exemplu SRL, producător de îmbrăcăminte din Iași, vinde 1.200 de tricouri (NC 6109) către SC Client SRL din Timișoara, cu 36.000 lei fără TVA plus TVA 21%. Clientul trimite propriul camion la depozitul din Iași.

- Declarant: SC Exemplu SRL, ca furnizor, chiar dacă transportul e organizat de client.
- SC Exemplu SRL declară transportul în ziua încărcării și îi dă șoferului clientului codul UIT înainte ca acesta să plece.
- SC Client SRL nu depune nicio declarație RO e-Transport pentru această achiziție internă.
:::

## Ce se greșește în practică

- **Se consideră că declară cel care plătește transportul.** Legea leagă obligația de calitatea de furnizor, nu de condiția de livrare sau de cine a comandat transportul.
- **Furnizorul lasă declararea în seama clientului care ridică marfa.** Obligația legală rămâne a furnizorului.
- **Codul se transmite după plecare.** Termenul-limită este punerea efectivă în mișcare a vehiculului.
- **Se confundă cu achiziția intracomunitară.** Acolo declară beneficiarul din România (art. 8^1 lit. b)), nu furnizorul străin.

## Ce face iConta.eu

Pe cardul e-Transport al firmei-furnizor, iConta.eu generează XML-ul notificării pentru tipul de operațiune „Transport național”, cu partenerul, bunurile (cod NC, cantitate, greutăți, valoare), vehiculul și traseul. Aplicația verifică fereastra de timp față de data transportului (cel mult 3 zile înainte, valabilitate de 5 zile) și semnalează o notificare făcută prea devreme sau cu cod expirat. Transmiterea codului UIT către transportator rămâne în sarcina furnizorului.

[iConta.eu](/)
