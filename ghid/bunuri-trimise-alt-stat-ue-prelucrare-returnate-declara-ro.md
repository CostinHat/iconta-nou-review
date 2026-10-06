---
title: "Bunuri trimise în alt stat UE pentru prelucrare și returnate: cine declară în RO e-Transport?"
description: "Beneficiarul serviciului din România declară ambele transporturi: bunurile trimise la prelucrare în alt stat membru și bunurile rezultate care revin în țară."
published: 2026-09-29
modified: 2026-09-29
poarta: v1
---

# Bunuri trimise în alt stat UE pentru prelucrare și returnate: cine declară în RO e-Transport?

**Firma din România care beneficiază de serviciu.** Când își trimite bunurile într-un alt stat membru pentru prelucrare, reparare sau altă lucrare și le primește înapoi, ea declară în RO e-Transport **ambele transporturi**: plecarea bunurilor din țară și întoarcerea bunurilor rezultate.

Prestatorul din celălalt stat membru nu are obligații în sistemul românesc. Pentru firmă, fiecare drum are nevoie de propriul cod UIT, chiar dacă bunurile nu își schimbă proprietarul și operațiunea nu este, în sens TVA, o livrare intracomunitară.

## Temeiul legal

::: ghid-temei
„Obligația declarării în Sistemul RO e-Transport a datelor prevăzute la art. 4 alin. (1) lit. a) referitoare la transportul internațional de bunuri revine următorilor utilizatori: [...] f) beneficiarului din România, în cazul unor operațiuni comerciale reprezentând un nontransfer atât pentru bunurile expediate din România pentru prestarea de servicii într-un stat membru al Uniunii Europene, cât și pentru bunurile rezultate reexpediate în România;"
— OUG 41/2022, art. 8^1 lit. f) (sursă: [OUG nr. 41/2022 pentru instituirea Sistemului național RO e-Transport](https://legislatie.just.ro/Public/DetaliiDocument/253801))
:::

::: ghid-temei
„f) prestarea de servicii în beneficiul persoanei impozabile, care implică evaluarea bunurilor mobile corporale sau lucrări asupra bunurilor mobile corporale efectuate în statul membru în care se termină expedierea ori transportul bunului, cu condiția ca bunurile, după prelucrare, să fie reexpediate persoanei impozabile din România de la care fuseseră expediate sau transportate inițial;"
— Codul fiscal (Legea 227/2015), art. 270 alin. (12) lit. f) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))
:::

Ce reține contabilul:

- **Declarant pentru ambele sensuri**: beneficiarul din România, adică firma care deține bunurile și comandă serviciul.
- **Segmentul de plecare**: de la locul de încărcare din țară până la punctul de frontieră la ieșire.
- **Segmentul de întoarcere**: de la punctul de frontieră la intrare până la locul de descărcare din țară.
- **Valabilitate de 15 zile** pentru codul UIT, deoarece operațiunile de nontransfer intră la art. 2 pct. 9 lit. j), pentru care art. 11 alin. (2) prevede termenul extins.
- **Orice bunuri**, nu doar cele cu risc fiscal ridicat, pentru că transportul este rutier internațional.
- **Condiția din TVA**: nontransferul presupune ca bunurile prelucrate să revină firmei din România. Dacă această condiție nu mai e îndeplinită, Codul fiscal tratează expedierea ca transfer (art. 270 alin. (13)).

::: ghid-exemplu
SC Exemplu SRL, producător de utilaje din Brașov, trimite în Austria 10 reductoare pentru rectificare. Lucrarea este facturată de prestatorul austriac cu 20.000 lei. După o săptămână, reductoarele revin la Brașov.

- Plecare: SC Exemplu SRL declară cele 10 reductoare pe segmentul fabrica din Brașov → punctul de frontieră Nădlac. Codul UIT e valabil 15 zile.
- Întoarcere: SC Exemplu SRL declară reductoarele rectificate pe segmentul Nădlac → fabrica din Brașov, cu un cod UIT nou.
- În evidența TVA, trimiterea se înregistrează ca nontransfer, nu ca livrare intracomunitară.
:::

## Ce se greșește în practică

- **Se declară doar plecarea bunurilor.** Întoarcerea bunurilor prelucrate se declară separat.
- **Se așteaptă ca prestatorul străin să declare întoarcerea.** Legea numește beneficiarul din România pentru ambele sensuri.
- **Operațiunea e tratată ca livrare intracomunitară** pentru că bunurile ies din țară. Proprietatea nu se transferă, iar în RO e-Transport declarantul este stabilit la lit. f).
- **Se aplică termenul de 5 zile** și se generează coduri inutile. Pentru nontransfer, valabilitatea este de 15 zile.

## Ce face iConta.eu

Pe cardul e-Transport, iConta.eu generează XML-ul notificării, cu tipul de operațiune și scopul aleși de contabil, cu bunurile (cod NC, cantitate, greutăți, valoare), partenerul extern, vehiculul și traseul. Aplicația calculează valabilitatea de 15 zile doar pentru achizițiile intracomunitare. Pentru nontransfer calculează prudent 5 zile, deși termenul legal e de 15 zile. Încadrarea operațiunii rămâne decizia contabilului.

[iConta.eu](/)
