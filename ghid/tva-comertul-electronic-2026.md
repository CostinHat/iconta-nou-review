---
title: "TVA pentru comerțul electronic în 2026"
description: "Pragul unic de 10.000 euro pentru vânzările la distanță intracomunitare și serviciile electronice B2C, sub care se aplică TVA din țara de origine — potrivit Codului fiscal."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# TVA pentru comerțul electronic în 2026

Un magazin online care vinde către clienți persoane fizice din alte state UE nu trebuie automat să se înregistreze în fiecare țară — legea prevede un prag unic, la nivelul întregii UE, sub care rămâne aplicabilă TVA din România.

## Temeiul legal

::: ghid-temei
„Valoarea totală, fără TVA, a operațiunilor prevăzute la lit. b) nu depășește, în anul calendaristic curent, 10.000 euro sau echivalentul acestei sume în moneda națională și nici nu a depășit această sumă în cursul anului calendaristic precedent. [...] Atunci când, în cursul unui an calendaristic, pragul prevăzut la alin. (1) lit. c) este depășit, prevederile art. 275 alin. (2) și art. 278 alin. (5) lit. h) se aplică de la momentul depășirii pragului."
— Legea nr. 227/2015 (Codul fiscal), art. 278^1 alin. (1) lit. c) și alin. (2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce înseamnă acest prag pentru un magazin online în 2026:

- Pragul de **10.000 euro** este unic pentru întreaga Uniune Europeană și se aplică **cumulat** vânzărilor la distanță de bunuri și serviciilor electronice/de telecomunicații/radiodifuziune către persoane neimpozabile din alte state membre — nu separat pentru fiecare țară de destinație.
- Sub acest prag, TVA se aplică potrivit regulilor din statul membru al furnizorului (România) — deci un magazin mic, cu vânzări reduse către alte state UE, poate continua să factureze cu TVA românesc.
- **Odată depășit pragul** (fie în anul curent, fie dacă a fost depășit deja în anul anterior), se aplică TVA din statul membru al clientului, de la momentul depășirii — nu retroactiv pentru tot anul, dar de la acel moment înainte.
- Peste prag, firma poate opta pentru **regimul special OSS (One Stop Shop)**, care permite declararea centralizată a TVA datorată în toate statele membre de consum, fără înregistrare separată în fiecare țară.

## Ce se greșește în practică

- Se calculează pragul de 10.000 euro separat pe fiecare țară de destinație, deși legea îl definește ca plafon unic, cumulat la nivelul întregii UE.
- Se ignoră vânzările din anul calendaristic anterior la verificarea pragului — dacă acesta a fost depășit deja anul trecut, regula de TVA din țara clientului se aplică din nou de la începutul anului curent, nu abia după o nouă depășire.
- Se amână înregistrarea în regimul OSS după depășirea pragului, continuând să se factureze eronat cu TVA românesc pentru vânzările care ar trebui taxate în țara clientului.

## Ce face iConta.eu

iConta.eu emite facturi pentru vânzările online și urmărește volumul de vânzări introdus în aplicație. Aplicația are un modul dedicat pentru declarația D398 (regimurile speciale OSS/IOSS, `core/d398.py`), care generează XML-ul de declarație, dar sumele pe fiecare stat de consum se introduc manual — aplicația **nu calculează automat, la data acestui ghid, depășirea pragului unic de 10.000 euro** pentru vânzările la distanță către alte state UE și nu ține evidența automată a operațiunilor pe stat/cotă străină — aceste verificări rămân în sarcina utilizatorului/contabilului, pe baza datelor de vânzări din aplicație.

[iConta.eu](/)
