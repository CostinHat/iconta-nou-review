---
title: "Deducerea integrală a laptopurilor sub plafon: condiții 2026"
description: "Din 25.02.2026, pragul de la care un bun devine mijloc fix amortizabil a crescut la 5.000 lei — sub această valoare, cheltuiala se deduce integral, nu se mai amortizează."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Deducerea integrală a laptopurilor sub plafon: condiții 2026

Un laptop cumpărat de firmă nu trebuie automat trecut pe amortizare pe mai mulți ani — dacă valoarea lui de intrare e sub pragul legal, costul se deduce integral, dintr-o dată, ca orice altă cheltuială. În 2026 acest prag s-a schimbat.

## Temeiul legal

::: ghid-temei
„Mijlocul fix amortizabil este orice imobilizare corporală care îndeplinește cumulativ următoarele condiții: [...] b) la data intrării în patrimoniul contribuabilului, are o valoare fiscală egală sau mai mare decât suma de 5.000 lei; această limită se actualizată anual, în funcție de indicele de inflație, prin hotărâre a Guvernului[.]"
— Codul fiscal (Legea 227/2015), art. 28 alin. (2) lit. b), astfel cum a fost modificată de OUG nr. 8/2026, aplicabilă începând cu anul fiscal 2026 (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Condițiile efective pentru deducerea integrală în 2026:

- Bunul trebuie să aibă o valoare fiscală de intrare **sub 5.000 lei** — vechiul prag, de 2.500 lei, s-a aplicat până la 31.12.2025/ultima zi a anului fiscal modificat care s-a încheiat în 2026.
- Trebuie îndeplinite și celelalte condiții cumulative ale unui mijloc fix amortizabil (deținere și utilizare în activitatea economică, durată normală de utilizare mai mare de un an) — dacă lipsește oricare, discuția despre plafonul valoric nici nu se mai pune, bunul nefiind mijloc fix indiferent de valoare.
- Pentru bunurile deja aflate în patrimoniu la 31.12.2025, cu valoare fiscală de intrare între 2.500 și 5.000 lei, legea nu permite trecerea retroactivă pe deducere integrală: valoarea fiscală rămasă neamortizată se recuperează în continuare pe durata normală de utilizare rămasă.

## Ce se greșește în practică

- Se aplică vechiul prag de 2.500 lei și pentru achiziții din 2026, amortizând inutil bunuri care, de fapt, se deduc integral sub noul plafon de 5.000 lei.
- Se trece pe deducere integrală, în 2026, un mijloc fix cumpărat și pus în funcțiune înainte de 2026, cu valoare între 2.500 și 5.000 lei — deși legea cere recuperarea lui pe durata rămasă, nu deducerea dintr-o dată.
- Se ignoră celelalte condiții cumulative (durata de utilizare peste un an, deținerea și utilizarea în activitatea economică) și se deduce integral orice bun sub 5.000 lei, chiar dacă prin natura lui ar trebui tratat ca mijloc fix.

## Ce face iConta.eu

iConta.eu are o funcționalitate reală pentru acest prag, în `core/obiecte_inventar.py`: funcția `prag_mf(la_data)` citește pragul valabil la data intrării dintr-un registru de cote versionat (`COTE["plafon_mijloc_fix"]`), cu valoarea de 5.000 lei aplicabilă de la 25.02.2026 (OUG nr. 8/2026, art. 28 alin. (2) lit. b)) și 2.500 lei pentru datele anterioare, iar `e_obiect_inventar()` decide, pe baza acestui prag și a duratei de utilizare, dacă bunul intră pe cheltuială integrală (303/603) sau trebuie amortizat. Fiindcă pragul e citit la data efectivă de intrare a bunului, un bun intrat înainte de 25.02.2026 e verificat automat față de vechiul plafon de 2.500 lei, fără să fie nevoie de o regulă separată pentru bunurile deja aflate în patrimoniu. La importul mijloacelor fixe (`core/mijloace_fixe_import_api.py`), aplicația semnalează automat, pentru fiecare bun, dacă valoarea lui e sub pragul de mijloc fix valabil la data intrării.

[iConta.eu](/)
