---
title: "Cum se înregistrează comisionul pentru retragerea de numerar?"
description: "Nota contabilă pentru comisionul bancar reținut la retragerea de numerar din contul firmei, potrivit planului de conturi OMFP 1802/2014."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se înregistrează comisionul pentru retragerea de numerar?

Când o firmă retrage numerar din contul bancar pentru alimentarea casieriei, banca reține de regulă un comision, vizibil separat pe extrasul de cont. Contabil, operațiunea are două componente distincte: transferul de disponibilități din bancă în casă (care nu e o cheltuială) și comisionul reținut de bancă pentru acest serviciu (care este o cheltuială).

## Temeiul legal

::: ghid-temei
„Contul 627 «Cheltuieli cu serviciile bancare și asimilate» Cu ajutorul acestui cont se ține evidența cheltuielilor cu serviciile bancare și asimilate. În debitul contului 627 «Cheltuieli cu serviciile bancare și asimilate» se înregistrează: – valoarea serviciilor bancare și asimilate plătite (471, 512) [...]"
— OMFP 1802/2014, reglementările contabile, planul de conturi general (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Înregistrarea corectă, în două note distincte:

- **Ridicarea numerarului din bancă** — se înregistrează ca transfer intern între disponibilități: 581 „Viramente interne" = 5121 „Conturi la bănci în lei" pentru ieșirea din bancă, apoi 5311 „Casa în lei" = 581 pentru intrarea în casă, conform circuitului standard al viramentelor interne.
- **Comisionul reținut de bancă** pentru operațiunea de retragere se înregistrează separat, ca și cheltuială, pe 627 „Cheltuieli cu serviciile bancare și asimilate" = 5121, pe baza extrasului de cont — documentul justificativ e extrasul, fără a fi nevoie de o factură separată de la bancă.
- Suma retrasă efectiv în casă (5311) trebuie să corespundă cu suma ieșită din bancă **minus** comisionul, dacă banca reține comisionul din aceeași operațiune — altfel apare o diferență nejustificată între soldul așteptat al casei și soldul real.

## Ce se greșește în practică

- Comisionul de retragere se include, fără să fie separat, în suma înregistrată ca intrare în casă, ceea ce face ca soldul de casă din registru să nu mai corespundă cu numerarul fizic existent.
- Se înregistrează comisionul direct pe cheltuieli generale (658) în loc de contul specific 627, dedicat serviciilor bancare.
- Nu se verifică dacă banca a aplicat comisionul ca procent din suma retrasă sau ca sumă fixă, ceea ce poate genera diferențe de rotunjire necontabilizate între extrasul bancar și registrul de casă.

## Ce face iConta.eu

Modulul de bancă din iConta.eu (`core/banca.py`) detectează automat, din descrierea liniei de extras, operațiunile de tip „numerar" (transfer intern) și aplică nota contabilă corespunzătoare pe contul 581, separat de operațiunile de tip „comision" (cont 627). Modulul de casierie (`core/casa_api.py`) oferă categoria predefinită „ridicare_banca" (5311 = 581), prin care contabilul înregistrează manual, în registrul de casă, intrarea numerarului ridicat din bancă. La data acestui ghid, aplicația **nu separă automat comisionul bancar de suma retrasă** atunci când extrasul importat prezintă operațiunea ca o singură linie netă — dacă banca afișează comisionul distinct pe extras, alocarea acestuia pe contul 627 se face manual, la contarea extrasului.

[iConta.eu](/)
