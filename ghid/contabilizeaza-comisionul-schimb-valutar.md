---
title: "Cum se contabilizează comisionul de schimb valutar?"
description: "Înregistrarea contabilă a comisionului perceput de bancă la o operațiune de schimb valutar și diferența față de diferențele de curs valutar."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se contabilizează comisionul de schimb valutar?

Când o firmă schimbă valută la bancă (de exemplu, transformă euro încasați de la un client extern în lei), banca reține de regulă un comision separat de cursul de schimb aplicat. Cele două sume — comisionul și eventuala diferență de curs — au tratament contabil diferit, iar confuzia între ele e frecventă.

## Temeiul legal

::: ghid-temei
„Contul 627 «Cheltuieli cu serviciile bancare și asimilate». Cu ajutorul acestui cont se ține evidența cheltuielilor cu serviciile bancare și asimilate. În debitul contului 627 «Cheltuieli cu serviciile bancare și asimilate» se înregistrează: valoarea serviciilor bancare și asimilate plătite (471, 512)."
— OMFP 1802/2014, planul de conturi (sursă: anaf_surse/omfp_1802_2014.txt)
:::

Comisionul de schimb valutar e un **serviciu prestat de bancă**, nu un rezultat al fluctuației cursului — de aceea intră la conturile de cheltuieli cu serviciile bancare (627), separat de conturile 665/765 „Cheltuieli/Venituri din diferențe de curs valutar", care înregistrează exclusiv efectul variației cursului asupra creanțelor, datoriilor sau disponibilităților în valută.

Practic:
- **Comisionul de schimb** se înregistrează 627 = 512 (sau 5124, contul de disponibilități în valută), la valoarea reținută de bancă, de regulă direct din extrasul de cont.
- **Diferența de curs** (dacă suma schimbată era deja înregistrată la un curs anterior, de exemplu o încasare de la un client extern) se înregistrează separat, pe 665 sau 765, după cum diferența e nefavorabilă sau favorabilă.

## Ce se greșește în practică

- Se înregistrează întreaga sumă reținută de bancă (comision + eventuală diferență de curs) pe un singur cont, de obicei 665, fără să se separe cele două componente.
- Se omite complet înregistrarea comisionului ca o cheltuială distinctă, tratându-l ca parte „invizibilă" a cursului de schimb aplicat de bancă.
- Se confundă comisionul de schimb valutar (serviciu bancar, cont 627) cu diferența de curs (cont 665/765) — deși legea contabilă le tratează separat, ca naturi economice diferite.

## Ce face iConta.eu

Acest ghid nu descrie o funcționalitate dedicată a iConta.eu — nu există în aplicație un ecran separat pentru „comision de schimb valutar". Suma comisionului se introduce ca orice altă cheltuială bancară, prin nota contabilă generică sau din extrasul de cont importat, pe contul 627, la fel ca alte servicii bancare (comisioane de administrare cont, comisioane de transfer). Contabilul rămâne cel care separă, pe baza extrasului bancar, suma comisionului de o eventuală diferență de curs valutar aferentă aceleiași operațiuni.

[iConta.eu](/)
