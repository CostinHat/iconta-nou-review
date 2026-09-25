---
title: "Cum se raportează stocurile în SAF-T?"
description: "Regulile OPANAF 1783/2021 pentru secțiunea de Stocuri din Declarația informativă D406 — o raportare la cerere, nu automată, ca restul SAF-T."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se raportează stocurile în SAF-T?

Spre deosebire de restul fișierului SAF-T, secțiunea de Stocuri din D406 nu se depune periodic din oficiu — se transmite doar la solicitarea punctuală a organului fiscal central, pentru perioada indicată de acesta.

## Temeiul legal

::: ghid-temei
„Informațiile privind «stocurile de produse» și «producție în curs» sunt transmise pe baza unei solicitări specifice din partea organelor fiscale centrale. În funcție de perioada pentru care se solicită furnizarea informațiilor privind stocurile prin fișierul standard de control fiscal (SAF-T), contribuabilii furnizează una sau mai multe declarații informative cuprinzând subsecțiunile din fișierul SAF-T relevante pentru «Stocuri», separate pentru fiecare dintre lunile/trimestrele calendaristice cuprinse în perioada pentru care a fost trimisă solicitarea din partea organelor fiscale centrale. Declarațiile informative D406 pentru «Stocuri» se depun în termenul stabilit de organul fiscal central, care nu poate fi mai mic de 30 de zile calendaristice de la data solicitării."
— OPANAF nr. 1.783/2021, Anexa 5, pct. 9-10 (sursă: anaf_surse/opanaf_1783_2021_saft_d406.txt)
:::

Ce rezultă concret:

- Secțiunea „Stocuri" (fișierul PhysicalStock din SAF-T) **nu se raportează la fiecare depunere lunară/trimestrială a D406**, ca secțiunile de bază (GeneralLedgerEntries, facturi etc.) — ea se activează doar când ANAF trimite o cerere specifică.
- La primirea solicitării, firma are un termen **de minimum 30 de zile calendaristice** pentru a pregăti și depune raportarea — termenul exact e stabilit de organul fiscal, dar nu poate fi mai scurt de 30 de zile.
- Raportarea se face separat, pe fiecare lună sau trimestru calendaristic din perioada solicitată — nu ca un singur fișier cumulat pentru tot intervalul cerut.
- Secțiunea de „Active" (mijloace fixe) are un regim diferit, tot special: se transmite o singură dată pe an, până la data depunerii situațiilor financiare anuale — nici aceasta nu urmează calendarul lunar/trimestrial obișnuit al D406.

## Ce se greșește în practică

- Se presupune că secțiunea de Stocuri trebuie inclusă în fiecare depunere periodică de D406, generând fișiere inutil de mari — norma spune expres că se transmite doar la cerere.
- Se răspunde la solicitarea ANAF cu un singur fișier cumulat pe toată perioada cerută, în loc de câte o declarație separată pentru fiecare lună/trimestru din interval, așa cum cere pct. 9.
- Se subestimează termenul de pregătire, presupunând un termen scurt, standard — legea garantează minimum 30 de zile calendaristice de la solicitare, nu de la o dată arbitrară aleasă de firmă.

## Ce face iConta.eu

Generatorul de SAF-T din iConta.eu (`core/d406_stocuri.py`) construiește secțiunea PhysicalStock pe baza mișcărilor de stoc înregistrate pentru fiecare articol, calculând soldurile de deschidere și închidere pentru perioada cerută. Aplicația generează fișierul la cererea contabilului, pentru perioada indicată de acesta — declanșarea propriu-zisă a raportării rămâne legată de solicitarea primită de la ANAF, pe care contabilul o introduce manual ca reper de perioadă.

[iConta.eu](/)
