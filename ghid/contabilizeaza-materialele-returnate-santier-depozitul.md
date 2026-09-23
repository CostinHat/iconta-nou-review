---
title: "Cum se contabilizează materialele returnate de pe șantier în depozitul central?"
description: Din punct de vedere al evidenței de stoc, o returnare de materiale de pe șantier e un transfer obișnuit, doar cu direcția inversată - același document, aceeași regulă de dispersare teritorială.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum se contabilizează materialele returnate de pe șantier în depozitul central?

Materialele rămase nefolosite pe un șantier, aduse înapoi la depozitul central, nu au un regim contabil separat de un transfer obișnuit — direcția mișcării (de la șantier spre depozit, nu invers) nu schimbă nici documentul, nici modul de evidențiere a stocului.

## Temeiul legal

::: ghid-temei
„Avizul de însoțire a mărfii servește ca: [...] dispoziție de transfer al valorilor materiale de la o gestiune la alta, dispersate teritorial, ale aceleiași entități; [...] În cazul transferului de bunuri între gestiunile aceleiași entități, dispersate teritorial, [...] Avizul de însoțire a mărfii va purta mențiunea «Fără factură», după caz."

— OMFP 2634/2015, Anexa 2, pct. 199 (Avizul de însoțire a mărfii, cod 14-3-6A)
:::

Textul nu face nicio distincție între direcția „ducere" (de la depozit spre șantier) și direcția „returnare" (de la șantier spre depozit) — se referă generic la „transfer al valorilor materiale de la o gestiune la alta, dispersate teritorial". Un șantier și depozitul central sunt, aproape întotdeauna, la adrese diferite, deci gestiuni dispersate teritorial: documentul de transport obligatoriu pentru returnarea materialelor e **Avizul de însoțire a mărfii (14-3-6A)**, cu mențiunea „Fără factură" — nu e o vânzare, materialele revin în același patrimoniu al firmei.

## Ce se greșește în practică

- Se consideră că, fiind o „returnare" și nu un transfer propriu-zis, materialele nu au nevoie de document de însoțire pe drum — regula de document rămâne cea de la orice transfer între gestiuni dispersate teritorial.
- Se lasă materialele nefolosite pe șantier la finalul lucrării, fără să fie readuse formal în evidența depozitului central — stocul faptic al depozitului rămâne, în acest caz, subevaluat față de realitate.
- Se confundă returnarea de materiale (mișcare internă, între gestiuni ale aceleiași firme) cu o retur către furnizor — sunt operațiuni complet diferite, cu documente și tratamente distincte.

## Ce face iConta.eu

Funcția de transfer între gestiuni din iConta.eu (F138) e simetrică — nu diferențiază între „ducere" și „returnare": aceeași funcție tratează ambele direcții identic, cu locația sursă și locația destinație pur și simplu inversate. Pentru o returnare de pe șantier în depozitul central, înregistrați un transfer cu locația sursă „șantier" și locația destinație „depozit central" — sistemul face o ieșire din șantier și o intrare în depozit, la costul mediu ponderat curent, fără notă contabilă. Documentul de circulație a materialelor pe drum (avizul de însoțire, conform textului de mai sus, pentru majoritatea situațiilor de tip șantier–depozit) rămâne de întocmit separat — aplicația nu generează formularul tipizat.

[iConta.eu](/)
