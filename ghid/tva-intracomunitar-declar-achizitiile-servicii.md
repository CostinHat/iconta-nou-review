---
title: "TVA intracomunitar: cum declar achizițiile de servicii"
description: "Regula locului prestării pentru serviciile B2B intracomunitare — locul unde beneficiarul e stabilit — și obligația de taxare inversă care rezultă de aici pentru firma din România."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# TVA intracomunitar: cum declar achizițiile de servicii

Spre deosebire de achiziția intracomunitară de bunuri, la servicii nu există o taxă „la frontieră" — regula de bază e alta: TVA se datorează acolo unde e stabilit beneficiarul, iar firma din România care primește serviciul de la un prestator dintr-un alt stat membru trebuie să-și autoliciteze taxa, prin mecanismul taxării inverse.

## Temeiul legal

::: ghid-temei
„(2) Locul de prestare a serviciilor către o persoană impozabilă care acționează ca atare este locul unde respectiva persoană care primește serviciile își are stabilit sediul activității sale economice. [...] În absența unui astfel de loc sau sediu fix, locul de prestare a serviciilor este locul unde persoana impozabilă care primește aceste servicii își are domiciliul stabil sau reședința obișnuită."
— Legea nr. 227/2015 (Codul fiscal), art. 278 alin. (2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Mecanismul de declarare pentru o firmă românească plătitoare de TVA care achiziționează servicii de la un prestator dintr-un alt stat membru UE:

- Pentru serviciile **B2B** (prestate către o persoană impozabilă), regula generală de la art. 278 plasează locul prestării la **sediul beneficiarului** — deci în România, chiar dacă prestatorul e stabilit în alt stat membru.
- Firma din România, ca beneficiar, are obligația să aplice **taxare inversă**: colectează și deduce simultan TVA-ul aferent, prin autofactură/înregistrare directă în decontul de TVA, fără ca prestatorul străin să factureze TVA românesc.
- Operațiunea trebuie evidențiată și în **declarația recapitulativă D390**, ca achiziție intracomunitară de servicii, distinct de operațiunile cu bunuri — omiterea acestei raportări e frecvent sancționată la controale, chiar și atunci când TVA a fost corect dedusă în D300.

## Ce se greșește în practică

- Se așteaptă o factură cu TVA românesc de la prestatorul din alt stat membru, deși regula B2B cere ca prestatorul să factureze fără TVA, iar taxa să fie autolichidată de beneficiar în România.
- Se aplică taxarea inversă în decontul D300, dar se omite raportarea aceleiași operațiuni în D390, deși cele două declarații au scopuri diferite și ambele sunt obligatorii pentru achizițiile intracomunitare de servicii.
- Se tratează identic toate serviciile achiziționate din UE, ignorând excepțiile de la regula generală a locului prestării (de exemplu, serviciile legate de bunuri imobile, care au loc de prestare diferit, la locul unde e situat imobilul).

## Ce face iConta.eu

La data acestui ghid, iConta.eu preia automat facturile de achiziții de servicii intracomunitare pentru calculul D301 (`core/d390.py`, funcția `achizitii_d301`), pe baza operațiunilor deja înregistrate în contabilitate. Aplicația **nu clasifică automat** fiecare serviciu în funcție de excepțiile de la regula locului prestării — contabilul trebuie să verifice, la contarea facturii, dacă operațiunea respectă regula generală B2B sau intră sub o excepție cu loc de prestare diferit.

[iConta.eu](/)
