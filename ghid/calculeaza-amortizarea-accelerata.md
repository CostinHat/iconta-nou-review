---
title: Cum se calculează amortizarea accelerată?
description: Amortizarea accelerată permite cel mult 50% din valoarea fiscală de intrare în primul an de utilizare, restul recuperându-se liniar, pe valoarea și durata rămase - disponibilă doar pentru echipamente tehnologice, mașini, unelte și instalații de lucru.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se calculează amortizarea accelerată?

Amortizarea accelerată concentrează cea mai mare parte a cheltuielii în primul an de utilizare — maximum 50% din valoarea fiscală de intrare — iar restul se recuperează liniar, raportând valoarea rămasă la durata rămasă, în fiecare an următor.

## Temeiul legal

::: ghid-temei
a) pentru primul an de utilizare, amortizarea nu poate depăși 50% din valoarea fiscală de la data intrării în patrimoniul contribuabilului a mijlocului fix; [...] b) pentru următorii ani de utilizare, amortizarea se calculează prin raportarea valorii rămase de amortizare a mijlocului fix la durata normală de utilizare rămasă a acestuia.

— Codul fiscal (Legea 227/2015), art.28 alin.(8)
:::

Regula are două etape distincte: anul 1 poate lua **cel mult** 50% din valoarea fiscală de intrare (contribuabilul poate opta și pentru un procent mai mic, dar nu mai mult), iar din anul 2 încolo formula devine simplă — valoarea rămasă de amortizat se împarte la numărul de ani rămași din durata normală de funcționare, în mod egal.

**Exemplu numeric**: același echipament tehnologic, valoare fiscală **24.000 lei**, durată **4 ani**.

- **anul 1**: maximum 50% din 24.000 = **12.000 lei**; valoare rămasă = 12.000 lei, ani rămași = 3;
- **anul 2**: 12.000 / 3 = **4.000 lei**; valoare rămasă = 8.000 lei, ani rămași = 2;
- **anul 3**: 8.000 / 2 = **4.000 lei**; valoare rămasă = 4.000 lei, an rămas = 1;
- **anul 4**: 4.000 / 1 = **4.000 lei**;
- total: 12.000 + 4.000 + 4.000 + 4.000 = **24.000 lei**, exact valoarea de intrare, integral recuperată.

## Ce se greșește în practică

- Se aplică metoda accelerată unei categorii de active care n-o permite — legea o rezervă echipamentelor tehnologice, mașinilor, uneltelor și instalațiilor de lucru (inclusiv calculatoare); construcțiile, de exemplu, admit doar amortizare liniară.
- Se depășește procentul de 50% în primul an, presupunând că e un minim obligatoriu, nu un plafon maxim — legea spune "nu poate depăși 50%", nu "trebuie să fie 50%".
- Se recalculează greșit anii următori pe baza valorii inițiale de intrare, în loc de valoarea rămasă după anul 1.

## Ce face iConta.eu

Amortizarea accelerată e implementată conform formulei legale — maximum 50% din valoarea fiscală de intrare în anul 1, apoi valoarea rămasă raportată la durata rămasă, în fiecare an următor — folosind același motor de calcul pentru registru, nota lunară, D406/SAF-T, casare și reevaluare. Dacă activul e clasificat pe o categorie pentru care legea nu permite metoda accelerată (de exemplu, mobilier sau alte active din categoria generică "orice alt mijloc fix"), aplicația refuză calculul cu eroare pe rând, în loc să aplice tacit o altă metodă.

[iConta.eu](/)
