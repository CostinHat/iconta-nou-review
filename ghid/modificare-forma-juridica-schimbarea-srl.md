---
title: "Modificare formă juridică: schimbarea din SRL în SA"
description: "Cine decide schimbarea formei juridice a unei societăți și ce condiție de capital social trebuie îndeplinită, conform Legii societăților 31/1990."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Modificare formă juridică: schimbarea din SRL în SA

Transformarea unei societăți cu răspundere limitată în societate pe acțiuni nu creează o persoană juridică nouă — societatea rămâne aceeași, doar forma ei juridică se schimbă. Dar decizia și condițiile de capital sunt strict reglementate.

## Temeiul legal

::: ghid-temei
„Adunarea generală extraordinară se întrunește ori de câte ori este necesar a se lua o hotărâre pentru: a) schimbarea formei juridice a societății."
— Legea 31/1990, art. 113 lit. a) (sursă: anaf_surse/legea_31_1990_societatile.txt)
:::

Pe lângă cerința de decizie prin adunarea generală extraordinară, transformarea în SA presupune îndeplinirea condiției specifice de capital a noii forme:

- Decizia de schimbare a formei juridice se ia **exclusiv de adunarea generală extraordinară** a asociaților, cu cvorumul și majoritatea cerute de actul constitutiv/lege pentru acest tip de hotărâre.
- Societatea pe acțiuni are un **capital social minim de 90.000 lei** (art. 10 alin. (1) din Legea 31/1990) — mult peste minimul de 200 de lei valabil pentru SRL. Fără atingerea acestui prag, transformarea nu poate fi înregistrată.
- Fiind o schimbare de formă și nu o dizolvare urmată de o nouă înființare, regimul fiscal de neutralitate prevăzut pentru fuziuni și divizări (art. 32 din Codul fiscal) nici nu este necesar aici — societatea își continuă existența, cu același CUI, fără să se producă un transfer de patrimoniu către o entitate nouă.
- Modificarea se înregistrează la Registrul Comerțului, iar actul constitutiv trebuie adaptat regulilor specifice formei SA (organe de conducere, structura acționariatului etc.).

## Ce se greșește în practică

- Se pornește procesul de transformare fără să se verifice întâi dacă societatea poate atinge capitalul minim de 90.000 lei cerut pentru SA.
- Se tratează schimbarea de formă juridică drept o operațiune similară fuziunii/divizării, aplicând greșit regimul fiscal de neutralitate al reorganizărilor, deși nu există niciun transfer de patrimoniu între entități diferite.
- Se confundă hotărârea AGA extraordinară, obligatorie pentru acest tip de decizie, cu o simplă hotărâre a administratorului sau a AGA ordinară.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu are un flux dedicat pentru schimbarea formei juridice a unei societăți** — nu am găsit în cod (`core/`) o funcționalitate care să gestioneze tranziția SRL→SA (verificare capital social minim, actualizare formă juridică în profilul firmei, generare de documente pentru Registrul Comerțului). O astfel de operațiune se derulează, la acest moment, integral în afara aplicației.

[iConta.eu](/)
