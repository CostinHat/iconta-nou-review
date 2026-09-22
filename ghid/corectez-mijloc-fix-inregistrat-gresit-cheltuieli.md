---
title: Cum corectez un mijloc fix înregistrat greșit pe cheltuieli?
description: Un activ cu valoare de intrare peste pragul de 5.000 lei și durată de utilizare peste un an trebuia capitalizat, nu trecut direct pe cheltuială — corecția înseamnă scoaterea sumei de pe cont de cheltuială, trecerea ei pe imobilizare și recalcularea amortizării de la data reală a punerii în funcțiune.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum corectez un mijloc fix înregistrat greșit pe cheltuieli?

O achiziție care îndeplinea, de fapt, condițiile de mijloc fix — valoare peste prag, durată de utilizare peste un an — dar a fost trecută direct pe cheltuială la primire, denaturează rezultatul lunii respective și lasă activul complet în afara registrului de mijloace fixe, fără amortizare calculată deloc.

## Temeiul legal

::: ghid-temei
**Art. 28 alin. (2) din Codul fiscal (Legea 227/2015)** — condițiile pentru mijloc fix amortizabil.

**Lit. b)** (modificată de OUG 8/2026 art. 6 pct. 7, MO 147/25.02.2026, în vigoare de la 25.02.2026): *„la data intrării în patrimoniul contribuabilului, are o valoare fiscală egală sau mai mare decât suma de 5.000 lei; această limită se actualizată anual, în funcție de indicele de inflație, prin hotărâre a Guvernului."*

**Lit. c)** (neschimbată): *„are o durată normală de utilizare mai mare de un an."*

**Art. 28 alin. (1)**: *„Cheltuielile aferente achiziționării, producerii, construirii mijloacelor fixe amortizabile, precum și investițiile efectuate la acestea se recuperează din punct de vedere fiscal prin deducerea amortizării potrivit prevederilor prezentului articol."*
:::

## Regula concretă

Dacă valoarea de intrare și durata de utilizare îndeplinesc simultan condițiile de la lit. b) și lit. c), bunul **trebuia** înregistrat ca mijloc fix, indiferent cum a fost efectiv contat inițial. Alin. (1) e explicit: recuperarea costului se face **prin deducerea amortizării**, nu dintr-o dată, ca o singură cheltuială la achiziție.

**Corecția** presupune trei pași:

1. **Scoaterea sumei** de pe contul de cheltuială pe care a fost înregistrată greșit (ex. 60x/61x), prin stornarea notei inițiale.
2. **Capitalizarea** sumei pe contul de imobilizare corect (21x/213x), cu data reală a punerii în funcțiune a bunului — nu data corecției.
3. **Recalcularea amortizării** de la acea dată reală de punere în funcțiune, cu metoda permisă pentru categoria de cont, și înregistrarea, la data corecției, a amortizării cumulate care ar fi trebuit deja recunoscută (6811 = 2813, pentru diferența dintre cheltuiala inițială greșit înregistrată integral și amortizarea eșalonată corect calculată).

Data de la care pornește amortizarea rămâne data reală a punerii în funcțiune a activului (alin. 12 lit. a: luna următoare acesteia) — corecția nu mută artificial începutul amortizării la data descoperirii greșelii.

## Ce se greșește în practică

- **Se corectează doar prospectiv**, capitalizând activul de la data descoperirii erorii, fără să se recunoască amortizarea care ar fi trebuit deja înregistrată din luna următoare punerii reale în funcțiune — asta lasă o parte din cost nerecuperată fiscal pentru perioada scursă.
- **Se verifică doar valoarea de intrare**, ignorând condiția duratei de utilizare — un bun peste pragul valoric, dar cu durată de utilizare sub un an, e corect încadrat ca obiect de inventar sau cheltuială directă; nu orice sumă mare înseamnă automat mijloc fix.
- **Se folosește pragul curent (5.000 lei)** pentru a judeca retroactiv o achiziție făcută înainte de 25.02.2026 — pentru acele date, pragul aplicabil era cel valabil atunci (2.500 lei, stabilit prin HG 276/2013), nu pragul de azi.

## Ce face iConta.eu

Pragul de încadrare ca mijloc fix se citește în funcție de data intrării activului, nu ca valoare fixă unică — pentru o corecție retroactivă, se aplică pragul valabil la data reală a punerii în funcțiune, nu pragul curent. La import în registru, pragul e citit din aceeași sursă unică folosită și la verificarea manuală a unei achiziții noi, nu redefinit separat.

[iConta.eu](/)
