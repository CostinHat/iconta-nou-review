---
title: "Am omis limitarea deductibilității dobânzilor"
description: "Regula ATAD din Codul fiscal: plafonul de 1.000.000 euro și limita de 30% din baza de calcul pentru costurile excedentare ale îndatorării."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Am omis limitarea deductibilității dobânzilor

Nu toate cheltuielile cu dobânzile sunt automat deductibile integral la impozitul pe profit. Codul fiscal impune, pentru costurile excedentare ale îndatorării, o dublă limită: un plafon fix în euro și un procent din baza de calcul — regula transpune directiva europeană ATAD.

## Temeiul legal

::: ghid-temei
„Contribuabilul are dreptul de a deduce, într-o perioadă fiscală, costurile excedentare ale îndatorării până la plafonul deductibil reprezentat de echivalentul în lei al sumei de 1.000.000 euro. [...] diferența dintre costurile excedentare ale îndatorării [...] și plafonul deductibil [...] este dedusă limitat în perioada fiscală în care este suportată, până la nivelul a 30% din baza de calcul."
— Legea 227/2015 (Codul fiscal), art. 40^2 alin. (4) și alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.html)
:::

Cum funcționează mecanismul, din text:

- **Costurile excedentare ale îndatorării** = diferența cu care costurile îndatorării depășesc veniturile din dobânzi și alte venituri echivalente ale contribuabilului.
- **Plafonul de 1.000.000 euro** se deduce integral, indiferent de bază (art. 40^2 alin. 4).
- **Peste acest plafon**, deducerea e limitată la 30% din baza de calcul — diferența dintre veniturile și cheltuielile contabile, din care se scad veniturile neimpozabile și la care se adaugă impozitul pe profit, costurile excedentare ale îndatorării și amortizarea fiscală (art. 40^2 alin. 2).
- **Partea nedeductibilă** dintr-o perioadă fiscală nu se pierde — se reportează fără limită de timp în anii fiscali următori, în aceleași condiții (art. 40^2 alin. 7).
- **Entitățile independente** (fără grup consolidat, fără întreprindere asociată, fără sediu permanent) deduc integral costurile excedentare, fără să aplice cele două plafoane (art. 40^2 alin. 5).

## Ce se greșește în practică

- Se deduce integral orice cheltuială cu dobânda, fără a verifica dacă firma se încadrează la „entitate independentă" (art. 40^2 alin. 5) — singura situație de deducere integrală necondiționată.
- Se aplică o singură limită (fie plafonul de 1.000.000 euro, fie procentul de 30%), în loc de mecanismul cumulativ corect: integral sub plafon, apoi 30% din bază pentru rest.
- Se pierde din vedere reportarea nelimitată în timp a părții nedeductibile (art. 40^2 alin. 7) — o sumă blocată într-un an nu dispare, ci rămâne recuperabilă în anii următori.
- Se calculează baza de calcul din alin. (2) fără a aduna înapoi amortizarea fiscală și costurile excedentare ale îndatorării, obținând o bază mai mică decât cea legală și, implicit, un plafon de 30% subevaluat.

## Ce face iConta.eu

iConta.eu calculează impozitul pe profit (D101) din datele contabile introduse, dar nu am identificat în cod o funcție dedicată limitării costurilor excedentare ale îndatorării conform art. 40^2 (plafonul de 1.000.000 euro combinat cu procentul de 30% din baza de calcul). Această verificare, specifică firmelor cu cheltuieli semnificative cu dobânzile, rămâne în prezent o ajustare pe care contabilul trebuie s-o facă manual, în afara aplicației.

[iConta.eu](/)
