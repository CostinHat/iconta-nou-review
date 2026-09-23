---
title: "Am calculat greșit impozitul pe dividende"
description: "Cota de impozit pe dividende s-a schimbat de mai multe ori în ultimii ani, iar cea mai frecventă greșeală de calcul este aplicarea cotei din anul curent în loc de cota de la data distribuirii."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Am calculat greșit impozitul pe dividende

Cota de impozit pe dividende nu a fost constantă — s-a schimbat de patru ori din 2016 până acum. Un calcul greșit apare aproape mereu din aplicarea cotei nepotrivite pentru perioada de distribuire a dividendului.

## Temeiul legal

::: ghid-temei
"(2) În cazul dividendelor distribuite în baza situațiilor financiare interimare întocmite în cursul anului 2025/anului fiscal modificat care începe în anul 2025, cota de impozit pe dividende este de 10%, fără recalcularea impozitului pe dividendele respective, după regularizarea acestora pe baza situațiilor financiare anuale aferente exercițiului financiar 2025 [...], aprobate potrivit legii."
— Legea 141/2025, art. VII alin. (2)
:::

Istoricul cotelor de impozit pe dividende:

| Perioadă | Cotă |
|---|---|
| de la 01.01.2026 | 16% |
| 01.01.2025 – 31.12.2025 | 10% |
| 01.01.2023 – 31.12.2024 | 8% |
| 01.01.2016 – 31.12.2022 | 5% |

Regula de bază: cota aplicabilă este cea valabilă la data la care dividendul a fost distribuit (aprobat), nu cea de la data plății și nici cea de la 31 decembrie al anului de declarare.

## Ce se greșește în practică

Cea mai frecventă greșeală este aplicarea cotei valabile în anul curent (de exemplu 16% în 2026) pentru un dividend distribuit într-un an anterior, la o cotă mai mică — deși legea prevede explicit că un dividend distribuit în baza situațiilor financiare din 2025 rămâne impozitat cu 10%, fără recalculare, chiar dacă este plătit ulterior.

O a doua sursă de eroare apare la plățile eșalonate: dacă un dividend distribuit este plătit în mai multe tranșe, fiecare tranșă trebuie să folosească cota de la data distribuirii din care provine — un calcul care aplică o singură cotă, unică, la toată suma plătită într-un an, poate fi greșit dacă tranșele provin din distribuiri făcute în ani (sau perioade) diferite.

## Ce face iConta.eu

Cota de impozit pe dividende este ținută într-un registru central, aplicată în funcție de perioadă, pe baza datei distribuirii. Pentru plățile eșalonate sau distribuite într-un an și plătite în altul, aplicația potrivește automat fiecare tranșă de plată cu distribuirile deschise (metodă FIFO), folosind cota de la data fiecărei distribuiri — același calcul fiind folosit atât la generarea declarației, cât și pe o cale independentă de reconciliere, care recalculează separat baza și impozitul per beneficiar din contul 457 și blochează generarea în caz de divergență.

O eroare de acest tip a existat, de altfel, în istoricul aplicației: la un moment dat lipsea din registru cota de 10% aferentă anului 2025, iar calculul aplica greșit 8%. Eroarea a fost identificată și corectată, cu teste dedicate care confirmă acum aplicarea cotei corecte pentru fiecare perioadă.

[iConta.eu](/)
