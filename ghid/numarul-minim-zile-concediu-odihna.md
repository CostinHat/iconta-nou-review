---
title: "Numărul minim de zile de concediu de odihnă pe an"
description: "Durata minimă legală a concediului de odihnă anual plătit, conform Codului muncii, și cum se raportează ea la zilele lucrătoare, nu la cele calendaristice."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Numărul minim de zile de concediu de odihnă pe an

Concediul de odihnă anual e un drept garantat oricărui salariat, indiferent de tipul contractului sau de domeniul de activitate — iar durata lui minimă e stabilită direct în Codul muncii, nu lăsată la latitudinea angajatorului.

## Temeiul legal

::: ghid-temei
„Dreptul la concediu de odihnă anual plătit este garantat tuturor salariaţilor."
— Legea 53/2003 (Codul muncii), art. 139 alin. (1)

„Durata minima a concediului de odihnă anual este de 20 de zile lucrătoare."
— Legea 53/2003 (Codul muncii), art. 140 alin. (1)

„Sărbătorile legale în care nu se lucrează, precum şi zilele libere plătite stabilite prin contractul colectiv de muncă aplicabil nu sunt incluse în durata concediului de odihnă anual."
— Legea 53/2003 (Codul muncii), art. 140 alin. (3)
(sursă: anaf_surse/legea_53_2003_codul_muncii.txt:1726-1738)
:::

Câteva precizări care rezultă direct din text:

- Cele **20 de zile** sunt zile **lucrătoare**, nu calendaristice — weekendurile nu se numără în cele 20 de zile.
- Sărbătorile legale nu se scad din durata concediului — dacă o sărbătoare legală cade în perioada de concediu, ea nu consumă o zi din cele 20.
- 20 de zile e un **minim legal** — contractul colectiv de muncă sau cel individual poate stabili o durată mai mare, niciodată mai mică.
- Durata efectivă se acordă **proporțional cu activitatea prestată într-un an calendaristic** (art.140 alin.2) — un salariat angajat la jumătatea anului primește, proporțional, jumătate din concediul anual, nu întregul.
- Anumite categorii au dreptul la concediu suplimentar: salariații care lucrează în condiții grele, periculoase sau vătămătoare, nevăzătorii, alte persoane cu handicap și tinerii sub 18 ani beneficiază de cel puțin 3 zile lucrătoare în plus (art.142).

## Ce se greșește în practică

- Se numără cele 20 de zile ca zile calendaristice, nu lucrătoare — ceea ce reduce, greșit, durata efectivă a concediului acordat.
- Se scad sărbătorile legale din numărul de zile de concediu rămase, deși legea le exclude explicit din durata concediului.
- Se acordă un concediu integral (20 de zile) unui salariat angajat la mijlocul anului, fără proratare pe perioada efectiv lucrată.
- Se confundă concediul de odihnă cu alte tipuri de concediu (medical, fără plată, pentru formare profesională) care au reguli complet diferite de calcul și de plată.

## Ce face iConta.eu

Acest subiect ține de Codul muncii, nu de calculatorul de concediu medical (CM) al aplicației — cercetarea de fond pe care se sprijină acest ghid a vizat motorul de calcul al indemnizației de concediu medical (`core/salarizare.py`, temei OUG 158/2005), care e o instituție juridică complet diferită de concediul de odihnă. Nu s-a verificat, în acest context, dacă vreun alt modul din iConta.eu calculează sau urmărește soldul de zile de concediu de odihnă al unui salariat.

[iConta.eu](/)
