---
title: Laptopul cumpărat pe firmă e cheltuială sau mijloc fix?
description: Un laptop devine mijloc fix (cont 214) doar dacă valoarea de intrare e cel puțin 5.000 lei și durata de utilizare depășește un an; sub oricare din cele două praguri e obiect de inventar (cont 303) sau cheltuială directă.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Laptopul cumpărat pe firmă este cheltuială sau mijloc fix?

Un laptop de 3.000 lei și unul de 8.000 lei nu se contează la fel, deși ambele ajung pe biroul aceluiași angajat. Diferența nu ține de bunul-simț contabil, ci de un prag fix din Codul fiscal, care s-a schimbat recent — și care decide dacă achiziția intră direct pe cheltuieli sau se amortizează în timp.

## Temeiul legal

::: ghid-temei
**Art. 28 alin. (2) din Codul fiscal (Legea 227/2015)** — condițiile pentru mijloc fix amortizabil.

**Lit. b)** (modificată de OUG 8/2026 art. 6 pct. 7, MO 147/25.02.2026, în vigoare de la 25.02.2026): *„la data intrării în patrimoniul contribuabilului, are o valoare fiscală egală sau mai mare decât suma de 5.000 lei; această limită se actualizată anual, în funcție de indicele de inflație, prin hotărâre a Guvernului."*

**Lit. c)** (neschimbată): *„are o durată normală de utilizare mai mare de un an."*
:::

## Regula concretă

Un bun e mijloc fix amortizabil doar dacă îndeplinește **simultan** ambele condiții de mai sus:

- valoarea de intrare este **≥ 5.000 lei** (prag valabil de la 25.02.2026 — până atunci pragul era 2.500 lei, stabilit prin HG 276/2013);
- durata normală de utilizare depășește **1 an**.

Pentru un laptop, asta înseamnă:

- **sub 5.000 lei** SAU cu durată de utilizare estimată sub 1 an → **obiect de inventar**, cont **303**, indiferent de preț;
- **≥ 5.000 lei** ȘI durată peste 1 an → **mijloc fix**, cont **214 „Mobilier, aparatură birotică..."**, se amortizează pe durata normală de funcționare, prin una din metodele permise pentru echipamente/aparatură (liniară sau degresivă).

Data care contează pentru încadrare e data intrării în patrimoniu (punerea în funcțiune/recepția), nu data facturii sau data plății. Pentru un laptop achiziționat înainte de 25.02.2026, pragul aplicabil la acea dată era 2.500 lei — schimbarea de prag nu retroactivează achizițiile deja făcute.

## Un exemplu

::: ghid-exemplu
Firma cumpără două laptopuri în aceeași lună, ambele cu durată de utilizare estimată de 3 ani:

- **Laptop A: 4.200 lei** — sub pragul de 5.000 lei → obiect de inventar, cont 303, se dă în consum integral (nu se amortizează).
- **Laptop B: 6.500 lei** — peste prag → mijloc fix, cont 214, amortizat pe durata normală de funcționare aleasă pentru categoria de birotică, prin metoda liniară sau degresivă.

Diferența de 2.300 lei în preț schimbă complet tratamentul contabil: unul e cheltuială/consum imediat, celălalt se recuperează fiscal eșalonat, lună de lună, prin amortizare.
:::

## Ce se greșește în practică

- **Se folosește reflex pragul vechi de 2.500 lei** pentru achiziții făcute după 25.02.2026 — pragul curent e 5.000 lei; folosirea celui vechi trece eronat un bun pe mijloc fix când ar trebui obiect de inventar (sau invers, pentru achiziții mai vechi).
- **Se ignoră condiția duratei de utilizare.** Un laptop de 6.000 lei cumpărat pentru un proiect de 6 luni, cu intenția clară de a fi casat după aceea, nu îndeplinește condiția „durată mai mare de un an" — nu devine automat mijloc fix doar pentru că depășește valoric pragul.
- **Se aplică pragul curent retroactiv** peste mijloace fixe deja înregistrate la un prag mai vechi. Regula tranzitorie (CF art. 45 alin. (21^3)) spune expres că activele existente la 31.12.2025 cu valoare de intrare între 2.500 și 5.000 lei **nu se reclasifică** — rămân mijloace fixe și se amortizează pe durata rămasă.

## Ce face iConta.eu

Pragul de încadrare ca mijloc fix are o singură sursă în aplicație, citită prin funcția care întoarce valoarea corectă în funcție de data intrării activului — nu pragul curent aplicat orbește peste toate datele. Pentru un activ intrat înainte de 25.02.2026, se aplică pragul de atunci (2.500 lei); pentru unul intrat de la acea dată încolo, pragul de 5.000 lei. Un test mecanic din cod verifică permanent că niciun alt modul nu redefinește separat această valoare.

[iConta.eu](/)
