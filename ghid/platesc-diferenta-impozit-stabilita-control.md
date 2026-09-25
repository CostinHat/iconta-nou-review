---
title: "Cum plătesc o diferență de impozit stabilită la control"
description: "Termenul de plată al unei diferențe de impozit stabilite printr-o decizie de impunere depinde de data la care decizia a fost comunicată, nu de data emiterii ei."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum plătesc o diferență de impozit stabilită la control

După o inspecție fiscală, organul de control emite o decizie de impunere prin care stabilește o diferență de obligații fiscale față de ce a fost declarat inițial. Întrebarea imediată e până când trebuie plătită acea diferență — iar răspunsul nu e „imediat", ci depinde de un calendar fix legat de data la care decizia a fost efectiv comunicată contribuabilului.

## Temeiul legal

::: ghid-temei
„(1) Pentru diferențele de obligații fiscale principale și pentru obligațiile fiscale accesorii, stabilite prin decizie potrivit legii, termenul de plată se stabilește în funcție de data comunicării deciziei, astfel: a) dacă data comunicării este cuprinsă în intervalul 1 - 15 din lună, termenul de plată este până la data de 5 a lunii următoare, inclusiv; b) dacă data comunicării este cuprinsă în intervalul 16 - 31 din lună, termenul de plată este până la data de 20 a lunii următoare, inclusiv."
— Legea nr. 207/2015 privind Codul de procedură fiscală, art. 156 alin. (1) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

- Termenul de plată nu curge de la data emiterii deciziei de impunere, ci de la data la care aceasta a fost **comunicată efectiv** contribuabilului.
- Dacă decizia a fost comunicată în prima jumătate a lunii (1-15), plata trebuie făcută până pe data de 5 a lunii următoare.
- Dacă a fost comunicată în a doua jumătate a lunii (16-31), plata trebuie făcută până pe data de 20 a lunii următoare.
- Decizia de impunere are ea însăși și rol de înștiințare de plată, de la data comunicării — nu mai e nevoie de un document separat pentru a curge termenul.

## Ce se greșește în practică

- Se plătește imediat, din prudență, fără a verifica termenul legal — ceea ce nu e greșit în sine, dar poate crea confuzii în evidența plăților anticipate față de scadența reală.
- Se confundă data emiterii deciziei (afișată pe document) cu data comunicării ei — termenul de plată curge de la comunicare, nu de la emitere.
- Nu se verifică dacă suma stabilită include și obligațiile fiscale accesorii (dobânzi/penalități de întârziere), care au același termen de plată conform art. 156 alin. (1), și se plătește doar obligația principală.

## Ce face iConta.eu

Din verificarea codului sursă, iConta.eu are un modul de urmărire a conformării fiscale (`control_fiscal_api`) care compară declarațiile datorate cu cele efectiv depuse și semnalizează diferențele — dar nu a fost găsită o funcție dedicată înregistrării unei decizii de impunere emise în urma unui control și calculării automate a termenului de plată aferent diferenței stabilite. Urmărirea acestui termen rămâne, la acest moment, o sarcină manuală.

[iConta.eu](/)
