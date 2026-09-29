---
title: "Bunuri primite din UE pentru prestarea unui serviciu în România: cine le declară în RO e-Transport?"
description: "Prestatorul de servicii din România declară atât bunurile primite pentru prelucrare sau reparare, cât și bunurile rezultate trimise înapoi partenerului din alt stat membru."
published: 2026-09-29
modified: 2026-09-29
poarta: v1
---

# Bunuri primite din UE pentru prestarea unui serviciu în România: cine le declară în RO e-Transport?

**Prestatorul de servicii din România.** Când un client din alt stat membru trimite bunuri în România pentru a fi prelucrate, reparate sau transformate, fără ca proprietatea să se transfere, operațiunea este un **nontransfer**. Prestatorul român declară în RO e-Transport **ambele drumuri**: sosirea bunurilor și reexpedierea bunurilor rezultate către client.

Clientul străin nu are obligații în sistemul românesc. Nici transportatorul nu devine declarant, el doar primește codul UIT. Pentru un atelier de lohn, o fabrică de confecții sau un service care lucrează pentru clienți din UE, fiecare camion la intrare și la ieșire are nevoie de cod UIT.

## Temeiul legal

::: ghid-temei
„Obligația declarării în Sistemul RO e-Transport a datelor prevăzute la art. 4 alin. (1) lit. a) referitoare la transportul internațional de bunuri revine următorilor utilizatori: [...] e) prestatorului de servicii din România, în cazul unor operațiuni comerciale reprezentând un nontransfer atât pentru bunurile descărcate pe teritoriul României pentru prestarea de servicii, cât și pentru bunurile rezultate reexpediate în statul partenerului comercial;"
— OUG 41/2022, art. 8^1 lit. e) (sursă: anaf_surse/oug_41_2022.txt)

„j) transportul pe teritoriul național al bunurilor în cadrul unor operațiuni comerciale reprezentând un nontransfer și transportul bunurilor reprezentând stocuri la dispoziția clientului conform art. 270 alin. (12) lit. f) și art. 270^1 din Legea nr. 227/2015 privind Codul fiscal , cu modificările și completările ulterioare;"
— OUG 41/2022, art. 2 pct. 9 lit. j) (sursă: anaf_surse/oug_41_2022.txt)
:::

Ce reține contabilul prestatorului:

- **Două declarații**, câte una pentru fiecare transport: la sosirea bunurilor, pentru segmentul frontieră → locul prestării, și la reexpediere, pentru segmentul locul prestării → frontieră.
- **Valabilitate de 15 zile** pentru codul UIT, deoarece operațiunile de la art. 2 pct. 9 lit. j) beneficiază de termenul extins (art. 11 alin. (2)).
- **Termen de declarare**: cel mult 3 zile înainte de data declarată pentru începerea transportului, dar până la intrarea în țară, respectiv până la plecarea vehiculului (art. 11 alin. (1)).
- **Orice bunuri**, nu doar cele cu risc fiscal ridicat, pentru că e vorba de transport rutier internațional.

Faptul că operațiunea nu e o livrare sau o achiziție intracomunitară, în sens TVA, nu scutește de RO e-Transport. Ordonanța tratează nontransferul ca operațiune distinctă, cu declarant propriu, pe ambele sensuri.

::: ghid-exemplu
SC Exemplu SRL, fabrică de confecții din Bacău, lucrează în lohn pentru un client din Italia. Clientul trimite 2.000 m de material și accesorii. SC Exemplu SRL le coase în 1.000 de sacouri și le trimite înapoi. Serviciul se facturează cu 50.000 lei.

- Sosire: SC Exemplu SRL declară materialul primit, pe segmentul punctul de frontieră → fabrica din Bacău.
- Reexpediere: SC Exemplu SRL declară cele 1.000 de sacouri (NC 6203) pe segmentul fabrica din Bacău → punctul de frontieră.
- Ambele coduri UIT sunt valabile 15 zile de la data declarată a transportului.
:::

## Ce se greșește în practică

- **Se așteaptă codul UIT de la clientul străin**, ca și cum ar fi o livrare. Declarantul este prestatorul din România.
- **Se declară doar sosirea bunurilor.** Reexpedierea bunurilor rezultate se declară separat.
- **Operațiunea e tratată ca achiziție intracomunitară.** Proprietatea nu se transferă, deci declarantul nu e „beneficiarul” în sensul art. 8^1 lit. b).
- **Se consideră că bunurile obișnuite nu intră în sistem.** Transportul rutier internațional se declară pentru orice bunuri.

## Ce face iConta.eu

Pe cardul e-Transport, iConta.eu generează XML-ul notificării, cu tipul de operațiune și scopul aleși de contabil, cu bunurile (cod NC, cantitate, greutăți, valoare), partenerul, vehiculul și traseul. Aplicația calculează valabilitatea de 15 zile doar pentru achizițiile intracomunitare. Pentru nontransfer calculează prudent 5 zile, deși termenul legal e de 15 zile. Alegerea tipului de operațiune potrivit rămâne decizia contabilului.

[iConta.eu](/)
