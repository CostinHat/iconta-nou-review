---
title: "Cum verific ce pierdere fiscală mai am de recuperat?"
description: "Regula de recuperare a pierderii fiscale anuale — limita de 70% și termenul de 5 ani, în ordinea înregistrării pierderilor."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum verific ce pierdere fiscală mai am de recuperat?

Pierderea fiscală înregistrată într-un an nu se pierde definitiv dacă firma nu are profit imediat — se reportează, dar cu două limite pe care trebuie urmărite an de an: procentul din profitul curent care poate fi acoperit și numărul de ani în care recuperarea mai e posibilă.

## Temeiul legal

::: ghid-temei
„Pierderile fiscale anuale stabilite prin declarația de impozit pe profit, începând cu anul 2024/anul fiscal modificat care începe în anul 2024, după caz, se recuperează din profiturile impozabile realizate, în limita a 70% inclusiv, în următorii 5 ani consecutivi. Recuperarea pierderilor se va efectua în ordinea înregistrării acestora, la fiecare termen de plată a impozitului pe profit."
— Legea 227/2015 (Codul fiscal), art. 31 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.html)
:::

Ce rezultă din text pentru urmărirea corectă a pierderii rămase:

- **Limita de 70%** se aplică profitului impozabil al anului curent — nu se poate acoperi mai mult de 70% din profitul anului cu pierderi reportate, indiferent cât de mare e stocul de pierderi disponibil.
- **Termenul de 5 ani consecutivi** curge de la anul înregistrării pierderii — o pierdere neconsumată integral în acest interval se pierde definitiv la finalul lui.
- **Ordinea de recuperare e cea a înregistrării** — pierderile mai vechi se acoperă înaintea celor mai recente, la fiecare termen de plată a impozitului pe profit, nu la alegerea contribuabilului.
- **Pierderea din sediu permanent** situat într-un stat din afara UE/AELS sau fără convenție de evitare a dublei impuneri urmează o regulă separată, cu deducere doar din veniturile aceluiași sediu, reportată tot pe 5 ani (art. 31, coroborat cu regulile privind sediile permanente).

## Ce se greșește în practică

- Se ține evidența pierderii fiscale ca o singură sumă cumulată, fără să se urmărească separat anul de origine al fiecărei tranșe și termenul ei propriu de 5 ani.
- Se acoperă profitul curent cu mai mult de 70% din pierderea reportată, depășind limita legală într-un an bun, cu profit mare.
- Se recuperează pierderile în altă ordine decât cea a înregistrării (de exemplu, cele mai recente înaintea celor vechi), contrar regulii explicite din art. 31 alin. (1).

## Ce face iConta.eu

iConta.eu calculează rezultatul fiscal curent (profit/pierdere al perioadei) în D101, inclusiv pentru grupul fiscal (D101g), unde pierderea de recuperat din anii precedenți e un câmp introdus de contabil, preluat direct în calcul. Nu am identificat însă în cod un registru automat care să urmărească, an de an, stocul de pierdere fiscală rămas de recuperat pe fiecare tranșă și termenul ei de 5 ani, aplicând singur limita de 70% — această evidență multianuală rămâne, la această dată, în sarcina contabilului, care introduce manual suma de pierdere rămasă de recuperat la fiecare declarație.

[iConta.eu](/)
