---
title: Mobilierul de birou este cheltuială deductibilă sau se amortizează?
description: Cum decide valoarea la achiziție dacă mobilierul de birou se deduce integral sau se amortizează ca mijloc fix, plus categoria de amortizare aplicabilă și ce controlează automat iConta.eu.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Mobilierul de birou este cheltuială deductibilă sau se amortizează?

Depinde exclusiv de un singur criteriu: **valoarea de la data intrării în patrimoniu**. Sub
prag, mobilierul poate fi trecut direct pe cheltuieli. La sau peste prag, devine mijloc fix
amortizabil.

## Temeiul legal

::: ghid-temei
la data intrării în patrimoniul contribuabilului, are o valoare fiscală egală sau mai mare
decât suma de 5.000 lei; această limită se actualizată anual, în funcție de indicele de
inflație, prin hotărâre a Guvernului;

— Codul fiscal (Legea 227/2015), art.28 alin.(2) lit.b, forma consolidată la 25.02.2026
:::

::: ghid-temei
Astfel mijloacele fixe amortizabile au fost clasificate în trei grupe principale și anume:
– Grupa 1 - Construcții; ... – Grupa 2 - Instalații tehnice, mijloace de transport, animale și
plantații; ... – Grupa 3 - Mobilier, aparatura birotica, echipamente de protecție a valorilor
umane și materiale și alte active corporale.

— HG 2139/2004, Catalogul privind clasificarea și duratele normale de funcționare a mijloacelor
fixe, cap.I, pct.3
:::

Mobilierul de birou intră, ca și clasificare, în **Grupa 3** a catalogului legal de mijloace
fixe. Dacă valoarea unei piese (sau a unui set, dacă e achiziționat și pus în funcțiune ca
ansamblu) este sub pragul de 5.000 lei (de la 25.02.2026; anterior 2.500 lei), firma poate opta
pentru deducerea integrală la achiziție, conform art.28 alin.(21). Dacă valoarea egalează sau
depășește pragul, mobilierul devine mijloc fix amortizabil obligatoriu, pe categoria "orice alt
mijloc fix amortizabil" (art.28 alin.5 lit.c) — metodă liniară sau degresivă, fără accelerată.

## Ce se greșește în practică

- Se cumulează mai multe piese de mobilier de valoare mică (ex. scaune, birouri individuale)
  într-o singură factură mare și se aplică pragul pe totalul facturii, deși fiecare piesă
  funcțională separat ar trebui evaluată individual.
- Se amortizează pe o durată aleasă "din burtă", fără a consulta plaja de ani permisă de
  catalog pentru Grupa 3 — aplicația nu validează automat dacă durata introdusă e în intervalul
  legal.
- Se alege metoda accelerată pentru mobilier, deși aceasta nu e permisă legal pentru categoria
  "orice alt mijloc fix amortizabil" din care face parte mobilierul (doar liniară sau
  degresivă).

## Ce face iConta.eu

Pragul mijlocului fix se verifică automat la înregistrarea ca obiect de inventar
(`nota-obiect-inventar`): dacă valoarea depășește pragul valabil la data achiziției, operațiunea
e refuzată și trebuie înregistrată ca mijloc fix. Odată intrat în registrul `Firma > Mijloace
fixe`, motorul unic de amortizare respinge automat, cu eroare pe rând (nu o cifră inventată), o
metodă nepermisă pentru categorie — deci nu puteți amortiza accidental mobilierul cu metodă
accelerată.

De spus deschis: **catalogul HG 2139/2004 (plajele de durată pe categorie) nu e cablat în
aplicație**. Durata normală de utilizare (`dnf_luni`) e un câmp complet liber, introdus manual —
iConta.eu nu oferă un lookup automat al plajei corecte pentru Grupa 3 și nu avertizează dacă
durata aleasă e în afara intervalului legal. Alegerea duratei rămâne responsabilitatea
contabilului.

[iConta.eu](/)
