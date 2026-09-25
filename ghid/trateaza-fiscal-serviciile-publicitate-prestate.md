---
title: "Cum se tratează fiscal serviciile de publicitate prestate unei platforme străine?"
description: "Pentru serviciile B2B, precum publicitatea, locul prestării e la sediul beneficiarului — ceea ce, pentru o platformă străină nestabilită în România, mută taxarea TVA în afara României."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se tratează fiscal serviciile de publicitate prestate unei platforme străine?

Când o firmă românească prestează servicii de publicitate către o platformă stabilită în altă țară, regula generală pentru serviciile B2B din Codul fiscal mută locul prestării — și, odată cu el, obligația de taxare — la sediul beneficiarului, nu la sediul prestatorului.

## Temeiul legal

::: ghid-temei
„(2) Locul de prestare a serviciilor către o persoană impozabilă care acționează ca atare este locul unde respectiva persoană care primește serviciile își are stabilit sediul activității sale economice."
— Legea nr. 227/2015 (Codul fiscal), art. 278 alin. (2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Pentru serviciile prestate către o **persoană impozabilă** (regula B2B), locul prestării e considerat a fi **acolo unde beneficiarul își are sediul activității economice** — nu unde e stabilit prestatorul.
- Dacă platforma străină e stabilită într-un alt stat (membru UE sau terț) și nu are sediu fix în România, serviciul de publicitate prestat de firma română are **locul prestării în afara României** — operațiune neimpozabilă din perspectiva TVA românesc, fără TVA colectată de prestatorul român.
- Firma română trebuie totuși să declare operațiunea corect (de regulă în declarația recapitulativă D390, pentru servicii prestate către persoane impozabile din alt stat membru), chiar dacă nu colectează TVA.
- Situația e diferită dacă firma română este cea care **primește** servicii de publicitate de la o platformă străină (de exemplu Google Ads, Meta Ads): atunci taxarea inversă prevăzută la art. 307 alin. (2) obligă beneficiarul din România să autolichideze TVA, tratament complet distinct de cel descris mai sus.

## Ce se greșește în practică

- Se aplică TVA românesc pe factura emisă către platforma străină, deși regula B2B mută locul prestării la sediul beneficiarului, iar operațiunea nu e taxabilă în România.
- Se omite declararea operațiunii în declarația recapitulativă (D390), considerând că, din moment ce nu se colectează TVA, nu există nicio obligație declarativă.
- Se confundă situația în care firma română e **prestator** de publicitate (locul prestării la beneficiarul străin) cu situația inversă, în care firma română e **beneficiar** al unor servicii de publicitate cumpărate de la o platformă străină (taxare inversă, cu autolichidare de TVA în România).

## Ce face iConta.eu

La data acestui ghid, modulul de facturare din iConta.eu permite emiterea facturilor către parteneri externi, iar declarația D390 (`core/d390.py`) preia operațiunile intracomunitare din evidența facturilor pentru raportare. Nu am găsit însă o regulă automată care să clasifice o factură de publicitate emisă către o platformă străină drept operațiune cu locul prestării în afara României și să o direcționeze corect spre D390, fără TVA colectată — încadrarea corectă a fiecărei operațiuni (locul prestării, regimul TVA aplicabil) rămâne o decizie a contabilului la emiterea facturii.

[iConta.eu](/)
