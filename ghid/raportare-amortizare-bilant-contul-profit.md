---
title: Raportare amortizare în bilanț și contul de profit 2026
description: Cum ajunge amortizarea calculată lunar în rândurile de active nete din bilanț și în rândul de „ajustări de valoare" din contul de profit și pierdere — pentru varianta prescurtată și pentru cea completă.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Raportare amortizare în bilanț și contul de profit 2026

Amortizarea calculată lunar pentru mijloacele fixe nu apare ca un rând separat, „amortizare", nici în bilanț, nici în contul de profit și pierdere — ea influențează indirect alte rânduri ale formularelor.

## Temeiul legal

::: ghid-temei
Persoanele prevăzute la art. 1 alin. (1)-(4) au obligația să întocmească situații financiare anuale.
— Legea contabilității nr. 82/1991, republicată, art. 28 alin. (1)
:::

Legea impune raportarea la valoare netă (imagine fidelă a patrimoniului), fără să detalieze exact fiecare rând al formularului — conținutul tehnic al S1005/S1003 (unde exact scade amortizarea) e stabilit la nivel de ordin al ministrului finanțelor publice. Temeiul inițial, OMF 107/2025, a fost **abrogat** prin art. 13 din Ordinul nr. 2.036/23.12.2025 (MO nr. 41/20.01.2026); textul actului succesor nu e disponibil în sursele verificate, deci nu îl putem cita aici — descriem mai jos comportamentul efectiv, verificat direct în cod.

## Ce se greșește în practică

- Se caută un rând distinct „amortizare" în bilanț — nu există; imobilizările apar deja la valoare netă (brut minus amortizare cumulată), nu la valoare brută cu amortizarea scăzută separat, vizibil.
- Se dublează amortizarea în contul de profit și pierdere, incluzând-o atât în cheltuielile de exploatare curente, cât și în rândul de „ajustări de valoare", deși cele două trebuie tratate distinct, fără suprapunere.

## Ce face iConta.eu

Confirmat direct în motorul de generare (`core/bilant.py`):

- **În bilanț (F10)** — rândurile de imobilizări necorporale și corporale se calculează net, scăzând din valoarea brută conturile de amortizare și ajustări: **281** (amortizarea imobilizărilor corporale) și **291/2931/2935** (ajustări pentru depreciere), pe lângă conturile similare pentru imobilizări necorporale.
- **În contul de profit și pierdere prescurtat (F20, micro)** — rândul „ajustări de valoare" se calculează ca sumă a conturilor **654, 681, 686** (debit) minus **754, 7812, 7813, 7814, 786** (credit); contul **681** (cheltuieli de exploatare privind amortizările și ajustările) intră direct aici.
- **În contul de profit și pierdere complet (F20, S1003)** — rândul „ajustări de valoare privind imobilizările" se calculează ca **6811 + 6813 + 6817 + 654**, minus **754 + 7813 + 7814**.

Calculul propriu-zis al amortizării lunare (durate normale de utilizare, metodă, data de start) este gestionat de registrul de mijloace fixe; ceea ce descrie acest ghid este exclusiv modul în care rezultatul acelui calcul e preluat și mapat în bilanț și în contul de profit și pierdere.

[iConta.eu](/)
