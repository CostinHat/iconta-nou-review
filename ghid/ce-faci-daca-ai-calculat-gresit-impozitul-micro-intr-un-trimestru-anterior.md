---
title: Ce faci dacă ai calculat greșit impozitul micro într-un trimestru anterior?
description: O eroare de calcul într-un trimestru anterior de impozit micro se corectează prin rectificarea trimestrului respectiv, nu prin ajustarea trimestrului curent, pentru că fiecare trimestru micro e independent, nu cumulat.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Ce faci dacă ai calculat greșit impozitul micro într-un trimestru anterior?

Pentru că fiecare trimestru de impozit micro este independent (spre deosebire de impozitul pe profit, care e cumulat), o eroare descoperită ulterior trebuie corectată direct la sursă — în trimestrul unde a apărut — nu „absorbită" în calculul trimestrului curent.

## Temeiul legal

::: ghid-temei
**CF art. 51 alin. (1):**
> „Cota de impozit pe veniturile microîntreprinderilor este de 1%."
— sursă: `anaf_surse/cod_fiscal_227_2015_consolidat.html`

**CF art. 53 alin. (1):**
> „Baza impozabilă a impozitului pe veniturile microîntreprinderilor o constituie **veniturile din orice
> sursă**, din care se scad: a) veniturile aferente costurilor stocurilor de produse; b) veniturile
> aferente costurilor serviciilor în curs de execuție; ... j) valoarea reducerilor comerciale acordate
> ulterior facturării, înregistrate în contul «709»..."
— sursă: `anaf_surse/cod_fiscal_227_2015_consolidat.txt:6480-6519`
:::

## De ce nu se poate „repara" în trimestrul curent

Baza impozabilă a fiecărui trimestru micro se determină strict din veniturile acelui trimestru (art. 53 alin. 1) — trimestrele nu se cumulează între ele, așa cum se întâmplă la impozitul pe profit. Din acest motiv, dacă baza unui trimestru anterior a fost calculată greșit (de exemplu, o factură omisă, o deducere aplicată greșit sau un venit înregistrat în perioada greșită), corecția trebuie făcută la nivelul trimestrului unde a apărut eroarea, printr-o declarație rectificativă pentru acel trimestru — nu prin includerea diferenței în calculul trimestrului curent, care ar produce o bază incorectă și pentru trimestrul curent.

Primul pas practic e identificarea sursei erorii: de regulă o înregistrare contabilă lipsă, dublată sau plasată în perioada greșită. Odată corectată înregistrarea contabilă din trimestrul respectiv, suma corectă a obligației poate fi recalculată și redepusă pentru acel trimestru specific.

## Ce se greșește în practică

- Se adaugă diferența descoperită la baza trimestrului curent, în loc de a rectifica trimestrul unde a apărut eroarea — micro nu e cumulativ, deci diferența nu se „recuperează" automat.
- Se corectează doar suma declarată, fără a corecta și înregistrarea contabilă sursă care a produs baza greșită.
- Se ignoră eroarea dacă suma diferă cu puțin, deși orice bază de calcul greșită expune la riscul unei rectificări solicitate ulterior de ANAF.
- Se presupune că o eroare într-un trimestru afectează automat trimestrele următoare — pentru micro, fiecare trimestru fiind independent, nu e cazul (spre deosebire de impozitul pe profit, unde o eroare cumulată chiar propagă efecte în trimestrele următoare).

## Ce face iConta.eu

Pentru fiecare declarație D100 generată, `d100_reconciliere.verifica_reconciliere` recalculează suma obligației pe o cale independentă — direct din tabela `inregistrari_linii`, nu din rezultatul deja calculat — și o confruntă cu suma generatorului înainte de emiterea XML-ului. Această reconciliere obligatorie e mecanismul prin care o eroare de bază (înregistrare contabilă greșită sau omisă) ar fi semnalată înainte ca o declarație incorectă să fie depusă. Dacă eroarea a fost deja depusă într-un trimestru anterior, corectarea înregistrării contabile sursă din trimestrul respectiv și regenerarea D100 pentru acel trimestru specific reflectă suma corectă — motorul de calcul (`deriva_obligatii`) tratează fiecare trimestru izolat, deci o corecție la sursă nu afectează retroactiv trimestrele deja depuse corect.

[iConta.eu](/)
