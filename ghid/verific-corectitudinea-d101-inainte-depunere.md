---
title: "Cum verific corectitudinea D101 înainte de depunere"
description: "D101 trece prin validări de identitate, plafoane legale și un avertisment dedicat contului 691 înainte de a fi generată."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum verific corectitudinea D101 înainte de depunere

Înainte de depunere, merită știut ce verifică efectiv aplicația — și ce rămâne, în continuare, responsabilitatea contabilului.

## Temeiul legal

::: ghid-temei
"Avertisment cont 691 [...]: dacă soldul debitor al contului 691 (cheltuială cu impozitul pe profit) e >0 și rd.23 (P23, cheltuieli nedeductibile) e 0, se emite avertisment — cheltuiala e nedeductibilă (CF art.25 alin.(4) lit.a) și trebuie adăugată înapoi, altfel impozitul declarat iese subevaluat." — dosarul de cercetare F027, pe baza `core/d101.py` liniile 502–529.
:::

Acest avertisment nu e teoretic: pe portofoliul monitorizat (tenant_005, 2025), omisiunea a scăzut impozitul declarat cu 2.432 de lei, fără niciun semnal înainte ca acest gard să fie introdus.

Pe lângă acest avertisment, funcția `erori_generare()` (liniile 366–388) blochează generarea declarației dacă lipsesc: CUI valid (verificat prin checksum, `core.identitate.valideaza_cui`), denumire, adresă sau cod CAEN pe 4 cifre, plus eventualele erori de la profilul declarantului. Separat, `_erori_valori_p` (liniile 147–189) verifică non-negativitatea rândurilor unde legea o cere, faptul că subtotalurile „din care" sunt cel puțin egale cu suma componentelor, și plafoanele V1–V7 pentru credite fiscale, sponsorizare și reduceri.

## Ce se greșește în practică

Cea mai riscantă greșeală e ignorarea avertismentului legat de contul 691: dacă acesta are sold debitor pozitiv, dar rândul de cheltuieli nedeductibile (P23) rămâne pe 0, impozitul rezultat este, aproape sigur, subevaluat.

## Ce face iConta.eu

La generare, `genereaza()` (liniile 470–538) rulează și o reconciliere independentă a bazei contabile (`core/d101_reconciliere.py`) și verifică `totalPlata_A` emis (`core/reconciliere_emis.py`), pe lângă validările și avertismentul descrise mai sus.

[iConta.eu](/)
