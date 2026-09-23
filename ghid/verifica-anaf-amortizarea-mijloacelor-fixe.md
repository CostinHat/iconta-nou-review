---
title: Ce verifică ANAF la amortizarea mijloacelor fixe?
description: Un control verifică, în esență, trei lucruri — dacă bunul îndeplinea condițiile legale de mijloc fix la data intrării, dacă metoda de amortizare aleasă e permisă pentru categoria lui, și dacă cifrele din contabilitate corespund cu ce se raportează în SAF-T.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Ce verifică ANAF la amortizarea mijloacelor fixe?

Amortizarea nu e un calcul pe care contabilul îl face o singură dată și apoi îl repetă mecanic ani la rând — fiecare element al ei (încadrarea inițială, metoda aleasă, durata) poate fi verificat separat de un control, iar o greșeală la intrarea bunului în evidență se propagă în toate lunile ulterioare.

## Temeiul legal

::: ghid-temei
„Mijlocul fix amortizabil este orice imobilizare corporală care îndeplinește cumulativ următoarele condiții: a) este deținut și utilizat în producția, livrarea de bunuri sau în prestarea de servicii, pentru a fi închiriat terților sau în scopuri administrative; b) la data intrării în patrimoniul contribuabilului, are o valoare fiscală egală sau mai mare decât suma de 5.000 lei; [...] c) are o durată normală de utilizare mai mare de un an."
— Codul fiscal (Legea 227/2015), art. 28 alin. (2)
:::

::: ghid-temei
„Regimul de amortizare pentru un mijloc fix amortizabil se determină conform următoarelor reguli: a) în cazul construcțiilor, se aplică metoda de amortizare liniară; b) în cazul echipamentelor tehnologice [...] contribuabilul poate opta pentru metoda de amortizare liniară, degresivă sau accelerată; c) în cazul oricărui altui mijloc fix amortizabil, contribuabilul poate opta pentru metoda de amortizare liniară sau degresivă."
— Codul fiscal (Legea 227/2015), art. 28 alin. (5)
:::

Primul strat de verificare e la intrarea bunului în evidență: îndeplinea, la acea dată, cele trei condiții cumulative de la alin. (2) — afectare activității, valoare peste pragul legal valabil la acea dată, durată peste un an? Al doilea strat e metoda de amortizare: art. 28 alin. (5) restrânge metodele permise pe categorie de activ — construcțiile, de exemplu, nu pot fi amortizate decât liniar, indiferent de preferința contribuabilului, iar amortizarea superaccelerată introdusă temporar pentru 2026 (alin. (8^1)) se aplică strict echipamentelor tehnologice și activelor biologice puse în funcțiune în acel an. O metodă nepermisă pentru categoria activului produce o cheltuială de amortizare recalculabilă, nu doar o eroare formală.

Al treilea strat ține de coerența raportării: pentru firmele obligate la SAF-T, secțiunea anuală Active din D406 trebuie să reflecte aceleași cifre (valoare de intrare, amortizare cumulată, valoare rămasă) ca evidența contabilă internă — o discrepanță între ele e ușor de identificat printr-un control încrucișat.

## Ce se greșește în practică

- Se aplică o metodă de amortizare accelerată sau superaccelerată pentru o categorie de activ care nu o permite (de exemplu o construcție), fără verificarea prealabilă a art. 28 alin. (5).
- Se calculează amortizarea pe pragul valoric curent, în loc de pragul valabil la data efectivă a intrării bunului în patrimoniu — pragul s-a schimbat în timp (2.500 lei până în 2026, 5.000 lei de la 25.02.2026), iar bunurile mai vechi rămân sub regula valabilă la data lor de intrare.
- Se lasă neconcordanțe între registrul intern de mijloace fixe și cifrele raportate în secțiunea Active a D406, pentru firmele obligate la SAF-T.

## Ce face iConta.eu

Registrul „Firmă > Mijloace fixe" verifică automat, la fiecare calcul, dacă metoda de amortizare a unui activ e permisă pentru categoria lui, derivată din contul de imobilizare folosit — dacă nu e, afișează o eroare explicită pe rândul respectiv, în loc să calculeze tacit o cifră pe o metodă nepermisă. Pragul valoric de încadrare ca mijloc fix se citește dintr-un registru de cote actualizat pe dată, aplicat la data de intrare a fiecărui bun, nu la data curentă. Secțiunea Active din D406 folosește același motor de calcul ca registrul intern, ceea ce reduce riscul de discrepanțe între cele două — dar catalogul oficial de durate normale de funcționare nu e verificat automat de aplicație, iar durata introdusă pentru fiecare activ rămâne responsabilitatea contabilului.

[iConta.eu](/)
