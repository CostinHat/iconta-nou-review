---
title: "Cum se descarcă gestiunea pentru mostre?"
description: "Regimul de TVA și documentele pentru scoaterea din gestiune a bunurilor acordate gratuit ca mostre, conform art. 270 alin. (8) lit. b) din Codul fiscal."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se descarcă gestiunea pentru mostre?

Precizare importantă: legea nu reglementează procedura contabilă de „descărcare de gestiune" ca atare — asta ține de organizarea internă (bon de consum, notă de predare, proces-verbal). Ce reglementează explicit legea e regimul de TVA al bunurilor scoase din stoc și date gratuit ca mostre, pentru că de acolo vine întrebarea reală: se colectează TVA sau nu la ieșirea mostrelor din gestiune?

## Temeiul legal

::: ghid-temei
„(8) Nu constituie livrare de bunuri, în sensul alin. (1):
[...]
b) acordarea în mod gratuit de bunuri în scop de reclamă sau în scopul stimulării vânzărilor sau, mai general, în scopuri legate de desfășurarea activității economice, în condițiile stabilite prin normele metodologice;"
— Legea 227/2015 (Codul fiscal), art. 270 alin. (8) lit. b) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„b) bunurile acordate în scop de reclamă cuprind, fără a se limita la acestea, bunurile oferite în mod gratuit în cadrul campaniilor promoționale, mostre acordate pentru încercarea produselor sau pentru demonstrații la punctele de vânzare."
— HG 1/2016 (Normele metodologice de aplicare a Codului fiscal), pct. 7 alin. (10) lit. b) (sursă: anaf_surse/hg_1_2016_norme_cod_fiscal.txt)
:::

Consecința practică, din combinarea celor două texte:

- Bunurile scoase din stoc pentru a fi date gratuit ca **mostre** (pentru încercarea produselor, demonstrații la punctul de vânzare) **nu se consideră livrare de bunuri** din punctul de vedere al TVA — deci **nu se colectează TVA** la ieșirea lor din gestiune.
- Condiția implicită din normele metodologice: mostrele trebuie să fie de același fel cu bunurile pe care firma le produce/comercializează în mod obișnuit, sau să se poată dovedi obiectiv legătura cu produsele/serviciile pe care le vinde firma.
- Din punctul de vedere al impozitului pe profit, cheltuiala cu bunurile acordate ca mostre în cadrul unei campanii publicitare intră la cheltuieli de reclamă și publicitate — deductibile integral, ca cheltuială efectuată în scopul activității economice (HG 1/2016, pct. 13 alin. 1 lit. a).
- Descărcarea propriu-zisă din gestiune se face pe baza unui document intern (bon de consum, notă de predare-transfer sau proces-verbal de acordare mostre), la cost, nu la preț de vânzare — documentul justifică ieșirea din stoc, dar forma lui exactă nu e stabilită printr-un act normativ specific, ci prin practica de gestiune a fiecărei firme.

## Ce se greșește în practică

- Se colectează TVA la scoaterea mostrelor din gestiune, ca la o vânzare, deși art. 270 alin. (8) lit. b) exclude explicit acordarea gratuită de bunuri în scop de reclamă din sfera livrărilor de bunuri.
- Se dau ca „mostre" bunuri care nu au legătură cu activitatea firmei sau nu sunt de același fel cu cele comercializate — caz în care condiția din normele metodologice nu mai e îndeplinită, iar operațiunea riscă să fie recalificată drept livrare cu titlu gratuit, impozabilă.
- Nu se păstrează niciun document justificativ pentru ieșirea din stoc, ceea ce face imposibilă, la un control, dovedirea că bunurile au ieșit efectiv pentru scop de reclamă și nu au fost, de fapt, vândute la negru.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu are un tip de mișcare de stoc dedicat pentru „mostre"**. Modulul de gestiune (`core/stocuri.py`) gestionează intrările (NIR) și ieșirile generice de marfă; o ieșire pentru mostre acordate gratuit se înregistrează manual de contabil ca notă de consum/transfer, la fel ca orice altă ieșire fără factură de vânzare, fără colectare automată de TVA — deci nu există în cod o validare care să verifice automat condiția „de același fel cu bunurile comercializate" din normele metodologice; aceasta rămâne o evaluare pe care contabilul o face la introducerea documentului.

[iConta.eu](/)
