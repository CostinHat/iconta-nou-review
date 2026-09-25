---
title: "Ce verifică ANAF la achizițiile de servicii din străinătate?"
description: "Regula locului prestării pentru serviciile B2B cumpărate din afara României și de ce taxarea inversă corect aplicată este primul lucru urmărit de organul fiscal."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce verifică ANAF la achizițiile de servicii din străinătate?

Când o firmă românească plătitoare de TVA cumpără un serviciu de la un furnizor din altă țară (consultanță, publicitate online, licențe software, abonamente SaaS), TVA nu se plătește furnizorului — regula generală mută taxarea la cumpărător, prin mecanismul taxării inverse. Tocmai fiindcă banii de TVA nu ajung la buget prin furnizor, acesta e un punct pe care ANAF îl verifică frecvent: dacă beneficiarul din România și-a declarat corect achiziția.

## Temeiul legal

```
::: ghid-temei
„(2) Locul de prestare a serviciilor către o persoană impozabilă care acționează ca atare este locul unde respectiva persoană care primește serviciile își are stabilit sediul activității sale economice. Dacă serviciile sunt furnizate către un sediu fix al persoanei impozabile, aflat în alt loc decât cel în care persoana își are sediul activității sale economice, locul de prestare a serviciilor este locul unde se află respectivul sediu fix al persoanei care primește serviciile. În absența unui astfel de loc sau sediu fix, locul de prestare a serviciilor este locul unde persoana impozabilă care primește aceste servicii își are domiciliul stabil sau reședința obișnuită."
— Legea nr. 227/2015 privind Codul fiscal, art. 278 alin. (2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::
```

Pornind de la această regulă (aplicabilă serviciilor B2B, adică între persoane impozabile), ceea ce ANAF confruntă efectiv la o achiziție de servicii din străinătate este:

- **Dacă locul prestării este corect stabilit în România** — pentru serviciile generale B2B, locul e la sediul beneficiarului (deci în România, dacă firma cumpărătoare are sediul aici), indiferent unde e stabilit prestatorul.
- **Dacă firma și-a autotaxat corect achiziția**, prin taxare inversă: TVA colectată și TVA deductibilă înregistrate simultan, fără plată efectivă către furnizor — art. 331 din Codul fiscal reglementează mecanismul.
- **Dacă achiziția a fost raportată** în decontul de TVA (D300) și, dacă furnizorul e din UE, în declarația recapitulativă (D390); pentru persoanele neînregistrate normal în scopuri de TVA (de exemplu, cele care aplică regimul special de scutire), obligația de autotaxare pentru servicii intracomunitare se declară prin decontul special (D301).
- **Corespondența dintre factura primită și înregistrarea contabilă** — dacă valoarea, data exigibilității și cota aplicată se potrivesc cu documentul justificativ.

## Ce se greșește în practică

- Se plătește TVA furnizorului străin (dacă acesta o facturează, dintr-o confuzie a lui privind regimul aplicabil), în loc să se aplice taxarea inversă în România — ceea ce lasă firma cumpărătoare fără TVA deductibilă legal recunoscută la noi și, adesea, cu o sumă greu de recuperat de la furnizor.
- Se omite includerea achiziției de servicii în decontul special (D301), atunci când firma nu e înregistrată normal în scopuri de TVA (de exemplu, o firmă mică sub plafonul de scutire) și cumpără totuși un serviciu de la un furnizor UE.
- Se aplică regula generală a locului prestării (sediul beneficiarului) și pentru servicii care au reguli speciale — de exemplu, servicii legate de un imobil, unde locul e cel al imobilului, nu al beneficiarului.

## Ce face iConta.eu

La data acestui ghid, funcționalitatea reală din `core/` acoperă generarea declarațiilor de TVA relevante (D300, D301, D390) pe baza operațiunilor înregistrate, inclusiv logica proprie de taxare inversă din modulele de facturare și de decont. Nu a fost găsită însă în cod o verificare automată a locului prestării în funcție de natura specifică a fiecărui tip de serviciu (de exemplu, distincția între regula generală de la art. 278 alin. (2) și excepțiile de la art. 278 alin. (4) pentru servicii legate de imobile, transport, evenimente etc.) — încadrarea corectă a tipului de serviciu rămâne, la acest moment, o verificare pe care contabilul o face manual, aplicația preluând corect consecințele fiscale odată ce încadrarea e stabilită.

[iConta.eu](/)
