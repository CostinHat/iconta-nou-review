---
title: "Cum se contabilizează un mijloc fix complet amortizat?"
description: "Ce se întâmplă contabil și fiscal cu un mijloc fix la finalul duratei normale de utilizare: rămâne în evidență, cu valoare zero, până la scoaterea din gestiune."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se contabilizează un mijloc fix complet amortizat?

Un mijloc fix pentru care amortizarea cumulată a ajuns la valoarea de intrare nu dispare din evidența contabilă și nici din cea fiscală — el rămâne înregistrat, cu valoare contabilă netă zero, atât timp cât firma îl mai folosește. Amortizarea încetează pur și simplu să se mai calculeze, pentru că nu mai există valoare de recuperat.

## Temeiul legal

::: ghid-temei
„Amortizarea fiscală se calculează după cum urmează: a) începând cu luna următoare celei în care mijlocul fix amortizabil se pune în funcțiune, prin aplicarea regimului de amortizare prevăzut la alin. (5) [...]"
— Legea 227/2015, art. 28 alin. (12) lit. a) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce se întâmplă, practic, la finalul duratei normale de utilizare:

- **Amortizarea lunară încetează** din luna în care valoarea de intrare a fost integral recuperată prin amortizare cumulată — nu se mai înregistrează cheltuială cu amortizarea pentru acel activ.
- **Activul rămâne în evidență**, la valoarea de intrare (brută), cu amortizarea cumulată egală cu valoarea de intrare și valoarea contabilă netă zero, atât timp cât firma continuă să îl folosească — nu se scoate automat din gestiune doar pentru că e complet amortizat.
- **Dacă activul continuă să fie folosit**, nu apare nicio cheltuială suplimentară de amortizare, dar activul rămâne relevant pentru inventarierea anuală (trebuie inclus în listele de inventariere, chiar cu valoare contabilă zero) și pentru declarația D406/SAF-T, secțiunea de active.
- **Scoaterea din evidență** (casare, vânzare, donație) se face separat, ca operațiune distinctă, cu nota contabilă specifică — pentru un activ complet amortizat, nota de casare nu mai generează pierdere din elemente de imobilizări, pentru că nu mai există valoare neamortizată de recuperat.
- **Dacă se fac investiții ulterioare** la un mijloc fix complet amortizat, pentru care durata normală de utilizare e expirată, amortizarea fiscală a investiției se calculează pe baza duratei stabilite de o comisie tehnică internă sau un expert tehnic independent, nu pe durata inițială a activului.

## Ce se greșește în practică

- Se scoate activul din evidență doar pentru că e complet amortizat, deși firma continuă să îl folosească — activul trebuie păstrat în evidență, cu valoare zero, atât timp cât e în folosință.
- Se omite activul complet amortizat din listele de inventariere anuală, considerându-l „irelevant" pentru că nu mai are valoare contabilă — obligația de inventariere se aplică indiferent de valoarea rămasă.
- La investiții ulterioare asupra unui activ cu durata expirată, se continuă amortizarea pe fosta durată normală de utilizare, în loc să se stabilească o durată nouă prin comisie tehnică sau expert independent.

## Ce face iConta.eu

Modulul de mijloace fixe din iConta.eu (`core/d406_active.py`, funcția `amortizat_la_data`) calculează amortizarea cumulată și oprește automat generarea de cheltuială cu amortizarea odată ce valoarea de intrare a fost integral recuperată, iar activul rămâne vizibil în evidență și în declarația D406 (secțiunea de active) chiar și cu valoare contabilă zero. Scoaterea din evidență (casare) are notă contabilă dedicată (`core/inventariere.py`, funcția `nota_casare_mf`). La data acestui ghid, aplicația **nu recalculează automat o durată nouă de amortizare** pentru investițiile ulterioare la un activ cu durata normală de utilizare expirată — stabilirea acestei durate, prin comisie tehnică internă sau expert independent, rămâne un pas manual.

[iConta.eu](/)
