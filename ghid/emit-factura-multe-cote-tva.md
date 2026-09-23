---
title: "Cum emit o factură cu mai multe cote de TVA în e-Factura?"
description: Emiterea unei facturi în e-Factura e o întrebare de facturare electronică, nu de decontul de TVA (D300) — acest ghid confirmă doar temeiul legal pentru existența mai multor cote pe o factură, nu pașii tehnici din fluxul e-Factura.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum emit o factură cu mai multe cote de TVA în e-Factura?

Această întrebare ține de emiterea și transmiterea facturii electronice, nu de decontul de TVA — sunt funcționalități diferite ale aplicației, cu surse verificate diferite. Ca să nu riscăm o citare inventată despre un mecanism pe care nu l-am verificat direct, spunem clar unde se oprește acoperirea acestui ghid.

## Temeiul legal

::: ghid-temei
**Art. 291 Cod fiscal (Legea 227/2015), modificat de Legea 141/2025 art. II pct. 42:** *„(1) Cota standard se aplică asupra bazei de impozitare pentru operaţiunile impozabile care nu sunt scutite de taxă sau care nu sunt supuse cotei reduse, iar nivelul acesteia este 21%. (2) Cota redusă de 11% se aplică..."* — temeiul pentru care o factură poate conține, legitim, mai multe linii cu cote diferite de TVA.

Sursele verificate pentru acest ghid nu acoperă structura tehnică a fluxului e-Factura (format UBL, transmitere SPV) — nu reproducem aici detalii tehnice nesusținute din surse verificate.
:::

## Ce e confirmat și ce nu

Confirmat: baza legală pentru care o factură poate avea mai multe cote de TVA (21%, 11%, sau, tranzitoriu, alte cote reglementate distinct) e art. 291 Cod fiscal — fiecare linie a facturii poate purta cota corespunzătoare bunului sau serviciului facturat, iar acest lucru e independent de canalul prin care factura ajunge la client (hârtie, PDF, e-Factura).

Neconfirmat aici: pașii tehnici concreți pentru introducerea mai multor cote pe o factură în fluxul e-Factura al aplicației (ecrane, câmpuri, structura UBL trimisă către SPV). Funcționalitatea de e-Factura e un modul separat de decontul de TVA (D300), cu surse de cod proprii, care nu au fost verificate pentru acest ghid.

## Ce se greșește în practică

- **Se presupune că o factură cu mai multe cote necesită un regim special în e-Factura** — legea (art. 291) permite oricând mai multe cote pe aceeași factură, indiferent de canalul de emitere.
- **Se caută răspunsul la această întrebare în sursele despre D300** — decontul de TVA și emiterea facturii electronice sunt funcționalități separate ale aplicației.

## Ce face iConta.eu

Pentru partea de decont de TVA, aplicația citește automat cotele facturilor deja emise (21/11/9%) și le distribuie pe rândurile corespunzătoare din D300. Pentru emiterea propriu-zisă a facturilor cu mai multe cote în fluxul e-Factura, iConta.eu are o funcționalitate dedicată, separată — recomandăm un ghid specific despre e-Factura pentru pașii concreți, susținuți din sursele acelui modul.

[iConta.eu](/)
