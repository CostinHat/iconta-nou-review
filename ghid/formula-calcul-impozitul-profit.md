---
title: Care este formula de calcul pentru impozitul pe profit?
description: Impozit pe profit = 16% din profitul impozabil, unde profitul impozabil se construiește din rezultatul contabil plus cheltuielile nedeductibile minus deducerile fiscale (amortizare, rezervă legală, sponsorizare). Formula detaliată pe structura reală a D101.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Care este formula de calcul pentru impozitul pe profit?

Formula de bază e simplă — 16% din profitul impozabil — dar profitul impozabil în sine e o sumă construită din mai multe componente, nu preluat direct din balanță.

## Temeiul legal

::: ghid-temei
**Art. 17 din Codul fiscal**: „Cota de impozit pe profit care se aplică asupra profitului impozabil este de 16%."
:::

## Formula, pe componente

**Profit impozabil = rezultatul contabil + cheltuieli nedeductibile − deduceri fiscale**, unde:

- **Cheltuielile nedeductibile** (adăugate înapoi la bază) includ, printre altele, cheltuiala cu impozitul pe profit însuși (cont 691), dacă nu e altfel tratată, și alte cheltuieli neconforme cu regulile de deductibilitate.
- **Deducerile fiscale** (scăzute din bază) includ amortizarea fiscală (calculată separat de amortizarea contabilă), rezerva legală constituită în limita a minimului dintre 5% din baza de calcul și 20% din capitalul social minus rezerva deja existentă, și sponsorizarea, în limita minimului dintre 20% din impozitul pe profit datorat și 0,75% din cifra de afaceri.

**Impozit pe profit = 16% × profit impozabil.**

Pentru firmele mari (cifră de afaceri peste 50.000.000 EUR anul precedent), se calculează suplimentar, pe o formulă separată, impozitul minim pe cifra de afaceri (IMCA) — un mecanism distinct de cel de mai sus, nu o variantă a formulei standard.

## Ce se greșește în practică

Cea mai frecventă eroare e tratarea profitului contabil ca bază directă de calcul, fără ajustările fiscale. A doua: introducerea unei singure componente a amortizării (doar cea fiscală, sau doar add-back-ul contabil), când formula cere ambele valori separat.

## Ce face iConta.eu

D101 aplică exact această formulă, reconstruind profitul impozabil din structura oficială a declarației (P1–P53). Rezerva legală se calculează automat dacă nu e introdusă manual, sponsorizarea se validează pe ambele plafoane simultan, iar aplicația emite un avertisment explicit dacă soldul contului 691 e pozitiv fără să fi fost adăugat înapoi la baza impozabilă. Amortizarea fiscală și contabilă rămân valori introduse manual — contabilul trebuie să le calculeze și să le introducă pe ambele.

[iConta.eu](/)
