---
title: "Cum se transferă materiale între șantiere?"
description: Șantierele sunt, prin natura lor, gestiuni dispersate teritorial - documentul obligatoriu pentru transportul materialelor între ele este avizul de însoțire a mărfii, nu bonul de transfer intern. Costul mediu rămâne unic pe firmă.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum se transferă materiale între șantiere?

Două șantiere ale aceleiași firme, chiar dacă sunt gestiuni distincte în evidența de stoc, se află aproape întotdeauna la adrese diferite. Asta le încadrează direct la categoria „gestiuni dispersate teritorial", cu consecință directă asupra documentului obligatoriu pe drum.

## Temeiul legal

::: ghid-temei
„Avizul de însoțire a mărfii servește ca: [...] dispoziție de transfer al valorilor materiale de la o gestiune la alta, dispersate teritorial, ale aceleiași entități; [...] În cazul transferului de bunuri între gestiunile aceleiași entități, dispersate teritorial, [...] Avizul de însoțire a mărfii va purta mențiunea «Fără factură», după caz."

— OMFP 2634/2015, Anexa 2, pct. 199 (Avizul de însoțire a mărfii, cod 14-3-6A)

„O diferență în localizarea geografică nu este suficientă pentru a justifica alegerea de metode diferite [de determinare a costului]."

— OMFP 1802/2014, Anexa 1 (Reglementări contabile), pct. 287 alin. (4)
:::

Primul text fixează documentul: pentru un transfer de materiale între două șantiere, dispersate teritorial prin definiție, documentul obligatoriu de însoțire pe timpul transportului este **Avizul de însoțire a mărfii (14-3-6A)**, cu mențiunea „Fără factură" — nu e o vânzare, deci nu se emite factură pentru mișcarea internă. Al doilea text arată de ce nu are sens un cost diferit pe fiecare șantier doar pentru că sunt la distanțe diferite unul de altul: metoda de determinare a costului rămâne unică la nivel de firmă, indiferent de câte puncte de lucru/șantiere există.

## Ce se greșește în practică

- Se folosește Bonul de predare-transfer-restituire (14-3-3A) pentru mișcări între șantiere aflate la adrese diferite — formularul e rezervat explicit gestiunilor „din incinta aceleiași entități", nu se aplică unui transport pe drum public între două șantiere distincte.
- Se transportă materiale (ciment, oțel-beton, cablu etc.) de pe un șantier pe altul fără niciun document, expunând transportul la un control rutier sau ITM fără justificare a încărcăturii.
- Se așteaptă ca fiecare șantier să aibă propriul cost mediu ponderat, ca și cum ar fi gestiuni independente cu evidență de cost separată — costul rămâne, conform textului de mai sus, unic la nivelul firmei.

## Ce face iConta.eu

Transferul între gestiuni din iConta.eu (F138) tratează un șantier ca pe orice altă locație de stoc: înregistrează o ieșire din șantierul sursă și o intrare în șantierul destinație, la costul mediu ponderat (CMP) curent al firmei — un singur CMP, global, indiferent de câte șantiere/locații aveți active. Aplicația nu diferențiază automat, la nivel de cod, dacă două locații sunt „în aceeași incintă" sau „dispersate teritorial" — tratează orice pereche de locații identic, ca simplă etichetă text. Decizia privind documentul corect (14-3-6A pentru șantiere, în marea majoritate a cazurilor) rămâne de luat de dvs., pe baza distanței reale dintre punctele de lucru, iar iConta.eu nu generează formularul respectiv ca document tipizat — doar înregistrarea internă de stoc.

[iConta.eu](/)
