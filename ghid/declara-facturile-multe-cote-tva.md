---
title: "Cum se declară facturile cu mai multe cote de TVA în D394?"
description: D394 nu ține de decontul de TVA (D300) — e o declarație informativă separată, cu propria ei logică de raportare, care descompune o factură cu mai multe cote pe câte o linie pentru fiecare cotă.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se declară facturile cu mai multe cote de TVA în D394?

Această întrebare nu ține de decontul de TVA (D300), deși pare înrudită — D394 e o declarație informativă distinctă, cu propriul modul de calcul în aplicație. Ca să nu amestecăm surse verificate pentru funcționalități diferite, tratăm aici doar ce s-a confirmat explicit despre D394, fără să reproducem detalii negarantate.

## Temeiul legal

::: ghid-temei
**Art. 291 Cod fiscal (Legea 227/2015), modificat de Legea 141/2025 art. II pct. 42:** *„(1) Cota standard se aplică asupra bazei de impozitare pentru operaţiunile impozabile care nu sunt scutite de taxă sau care nu sunt supuse cotei reduse, iar nivelul acesteia este 21%. (2) Cota redusă de 11% se aplică..."* — acesta e temeiul pentru care o factură poate avea, legitim, mai multe cote de TVA pe linii diferite.

Declarația D394 propriu-zisă are temei legal separat (OPANAF 3769/2015), al cărui text nu face parte din sursele verificate pentru acest ghid — de aceea nu îl citim aici.
:::

## Ce e confirmat despre D394

D394 e o funcționalitate distinctă de D300, cu modul propriu de cod (`core/d394.py`). Codul confirmă o logică proprie de împărțire pe cote: comentariul din sursă spune explicit *„Facturile lunii, cu cota din linii. O factura cu doua cote da doua intrari"* — adică o factură cu două cote de TVA generează două înregistrări separate în D394, una pentru fiecare cotă, nu o singură linie cumulată.

Dincolo de acest mecanism de bază, pașii concreți de completare a D394 (câmpuri, secțiuni, termene de depunere) nu fac parte din sursele verificate pentru acest ghid — nu le reproducem aici ca să nu riscăm o afirmație nesusținută.

## Ce se greșește în practică

- **Se caută răspunsul la această întrebare în structura D300** — D300 și D394 sunt declarații diferite, cu module de cod separate.
- **Se presupune că o factură cu mai multe cote se raportează pe o singură linie, cumulat** — mecanismul confirmat e opusul: fiecare cotă generează o intrare proprie.

## Ce face iConta.eu

Pentru facturile cu mai multe cote de TVA, modulul D394 (`core/d394.py`) generează automat câte o intrare separată pentru fiecare cotă prezentă pe factură, pe baza liniilor facturii. Pentru pașii compleți de completare și depunere a D394, recomandăm consultarea unui ghid dedicat acestei declarații — acest ghid acoperă doar D300 (decontul de TVA) în detaliu.

[iConta.eu](/)
