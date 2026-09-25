---
title: "Cum se calculează dobânda pentru TVA restant"
description: "Dobânda pentru TVA plătit cu întârziere se calculează la un nivel fix de 0,02% pentru fiecare zi de întârziere, aplicat la suma restantă, potrivit Codului de procedură fiscală."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se calculează dobânda pentru TVA restant

TVA neplătit la scadență generează dobândă de întârziere, calculată zilnic, separat de eventuale penalități de întârziere sau de nedeclarare — cele trei tipuri de accesorii fiscale nu se confundă și nu se calculează la fel.

## Temeiul legal

::: ghid-temei
„(5) Nivelul dobânzii este de 0,02% pentru fiecare zi de întârziere."
— Legea nr. 207/2015 (Codul de procedură fiscală), art. 174 alin. (5) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

- Dobânda se calculează la un nivel fix de **0,02% pe zi** de întârziere, aplicat la suma de TVA rămasă neachitată — nu la un procent anual convertit, ci direct pe zi.
- Dobânda curge din ziua imediat următoare scadenței și până la data stingerii sumei datorate (plată, compensare etc.), inclusiv.
- Dobânda e distinctă de **penalitatea de întârziere** și de **penalitatea de nedeclarare**, reglementate separat în același capitol al Codului de procedură fiscală (art. 173-183) — toate trei se pot cumula pe aceeași sumă restantă, cu reguli proprii de calcul.
- Pentru sumele eșalonate la plată, nivelul dobânzii rămâne același (0,02%/zi), aplicat pe perioada eșalonării, cu excepțiile specifice fondurilor europene.

## Ce se greșește în practică

- Se calculează dobânda ca procent anual împărțit la 365 de zile, în loc să se aplice direct rata fixă de 0,02% pe zi prevăzută explicit de lege.
- Se confundă dobânda cu penalitatea de întârziere sau cu penalitatea de nedeclarare, aplicând o singură sumă „de penalizare" în loc de a calcula corect fiecare componentă.
- Se calculează dobânda până la data plății programate, nu până la data la care suma a fost efectiv stinsă în evidența ANAF, ceea ce poate lăsa câteva zile necalculate sau, dimpotrivă, calculate în plus.

## Ce face iConta.eu

La data acestui ghid, iConta.eu generează declarațiile de TVA (D300) și urmărește scadențele de plată prin modulul de scadențar (`core/scadente.py`, `core/scadentar.py`), care calculează zilele lucrătoare și datele de scadență conform calendarului fiscal. Nu am găsit însă o funcție care să calculeze automat dobânda de 0,02%/zi pentru TVA achitat cu întârziere — acest calcul, inclusiv distincția față de eventualele penalități aplicate de ANAF, rămâne, la acest moment, în sarcina contabilului, pe baza deciziei de calcul accesorii emise de organul fiscal sau a propriei estimări.

[iConta.eu](/)
