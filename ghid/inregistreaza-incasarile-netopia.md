---
title: "Cum se înregistrează încasările prin Netopia?"
description: Netopia nu are azi nicio integrare automată în iConta.eu. Ca la orice procesator de plăți online, decontarea se identifică manual din extrasul de cont, pe suma netă, iar comisionul reținut se înregistrează separat.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum se înregistrează încasările prin Netopia?

La fel ca alți procesatori de plăți online, Netopia încasează suma brută de la client și virează în contul bancar al firmei suma netă, după reținerea comisionului propriu. Fără o integrare care să citească automat aceste decontări, înregistrarea se face manual, pe baza extrasului de cont bancar.

## Temeiul legal

::: ghid-temei
„Sumele virate sau depuse la bănci ori prin mandat poștal, pe bază de documente prezentate entității și neapărute încă în extrasele de cont, se înregistrează distinct în contabilitate (contul 5125 «Sume în curs de decontare»)." — OMFP 1802/2014, Reglementările contabile, pct. 302 alin. (2)

„Cu ajutorul acestui cont se ține evidența cheltuielilor reprezentând comisioanele datorate [...] comisioanele de intermediere [...]." — OMFP 1802/2014, Reglementările contabile, funcțiunea contului 622 „Cheltuieli privind comisioanele și onorariile"
:::

Procedura, pornind de la extrasul de cont:

1. Se identifică în extras suma virată de Netopia — de regulă o sumă netă, agregată pe mai multe tranzacții dintr-o perioadă (Netopia decontează în tranșe, nu tranzacție cu tranzacție).
2. Pentru intervalul dintre momentul plății clientului și momentul decontării efective în cont, dacă se ține o evidență intermediară, suma brută poate trece prin **cont 5125 „Sume în curs de decontare"** — contul prevăzut exact pentru sume virate, dar neapărute încă în extrasul de cont.
3. La decontarea efectivă, suma netă intră în **cont 5121 „Conturi la bănci în lei"**.
4. Diferența — comisionul reținut de Netopia — se înregistrează ca o cheltuială, în **cont 622 „Cheltuieli privind comisioanele și onorariile"** sau, după politica contabilă a firmei, în **cont 627 „Cheltuieli cu serviciile bancare și asimilate"**. Reglementările contabile definesc ambele conturi generic, nu tranșează care e „corect" pentru comisionul unui procesator de plăți online — alegerea rămâne o convenție internă.

Reconcilierea trebuie făcută pe suma brută a facturii emise, nu pe suma netă din extras — altfel factura rămâne, contabil, parțial neîncasată, în valoarea comisionului.

## Ce se greșește în practică

- Se marchează factura încasată integral pe baza sumei nete din extras, fără să se identifice separat comisionul reținut de Netopia — rezultă o diferență nereconciliată în soldul clientului.
- Se tratează decontarea Netopia ca pe o singură tranzacție, deși de regulă reprezintă mai multe plăți agregate dintr-o perioadă — reconcilierea trebuie făcută pe grupul de facturi corespunzător, nu pe o singură factură.
- Se presupune că aplicația marchează automat facturile plătite prin Netopia ca încasate — fără o sursă de date care să facă această corelare automat, marcarea rămâne o operație manuală, la reconciliere.

## Ce face iConta.eu

iConta.eu nu are, azi, nicio integrare automată cu Netopia — funcționalitatea de link de plată pe factură a fost închisă (decizie din 06.09.2026: „nu se integrează niciun procesator — fluxul real e transfer bancar, confirmat din extras"), iar calea de plată online a fost scoasă din interfață. Încasările prin Netopia se înregistrează manual, la reconcilierea cu extrasul de cont, folosind conturile 5125/5121 pentru sumă și 622 sau 627 pentru comisionul reținut. Marcarea facturii ca încasată rămâne o acțiune manuală în aplicație.

[iConta.eu](/)
