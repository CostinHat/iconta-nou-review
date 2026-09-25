---
title: "Cum se înregistrează numerarul retras de la bancă pentru casierie?"
description: "Documentul justificativ și înregistrarea contabilă a numerarului ridicat din contul bancar al firmei și depus în casierie, conform normelor privind documentele financiar-contabile."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se înregistrează numerarul retras de la bancă pentru casierie?

Ridicarea de numerar din contul bancar al firmei, pentru alimentarea casieriei, este o operațiune de trezorerie internă — banii nu părăsesc patrimoniul entității, doar trec dintr-un cont de disponibilități în altul. Documentul care justifică intrarea sumei în Registrul de casă, atunci când nu există alt document care să dispună operațiunea, este dispoziția de plată/încasare către casierie.

## Temeiul legal

::: ghid-temei
„Dispoziția de plată/încasare către casierie servește ca: [...] document justificativ de înregistrare în Registrul de casă și în contabilitate, în cazul plăților în numerar efectuate fără alt document justificativ. Dispoziția de plată/încasare către casierie se întocmește: [...] în cazul utilizării ca dispoziție de încasare, când nu există alte documente prin care se dispune încasarea (avize de plată, somații de plată etc.)."
— OMFP nr. 2634/2015 privind documentele financiar-contabile, Anexa 2 — Norme specifice, document cod 14-4-4 (sursă: anaf_surse/omfp_2634_2015_anexa2_norme_specifice.txt)
:::

Câteva precizări pentru operațiunea propriu-zisă:

- Ridicarea de numerar din bancă pentru casierie este o mișcare de trezorerie internă, nu o încasare sau o plată către un terț — de aceea nu intră sub incidența plafoanelor de încasări/plăți în numerar din Legea nr. 70/2015 (acele plafoane vizează relațiile cu alte persoane fizice sau juridice, nu operațiunile proprii ale entității cu banca sau Trezoreria Statului).
- Documentul justificativ pentru intrarea în casă este dispoziția de încasare către casierie (cod 14-4-4), pe baza căreia se face și înregistrarea în contabilitate.
- Suma trebuie să corespundă cu cea retrasă efectiv din extrasul de cont bancar al zilei respective — orice diferență se investighează imediat, nu la închiderea lunii.

## Ce se greșește în practică

- Se înregistrează suma direct în Registrul de casă, fără dispoziția de încasare aferentă, considerând extrasul de cont bancar drept document justificativ suficient — extrasul dovedește ieșirea din bancă, nu intrarea în casă.
- Se confundă ridicarea de numerar din bancă (mișcare internă de trezorerie) cu o încasare de la un client, aplicându-i greșit plafoanele zilnice din Legea nr. 70/2015.
- Se întârzie înregistrarea în Registrul de casă până la sfârșitul zilei sau al săptămânii, deși practica corectă e înregistrarea cronologică, pe măsură ce numerarul intră fizic în casierie.

## Ce face iConta.eu

Da — iConta.eu are un modul dedicat casieriei (`core/casa.py`), care tratează explicit operațiunea de „ridicare_banca" ca mișcare de trezorerie internă, prin contul de viramente interne: nota contabilă generată este Casă (5311/5314) = 581 „Viramente interne", urmată de 581 = Bancă (5121/5124). Modulul citează explicit ca sursă Legea nr. 70/2015 (plafoanele de numerar) și OMFP nr. 1802/2014 (planul de conturi și monografiile contabile), și este construit special ca operațiunile de ridicare/depunere din/în bancă să nu fie confundate cu încasările sau plățile către clienți/furnizori, care au propriile plafoane legale.

[iConta.eu](/)
