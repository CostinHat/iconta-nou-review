---
title: "Cum se înregistrează o factură Google primită de un SRL din România?"
description: "Serviciile electronice facturate de Google către un SRL românesc au locul prestării în România, cu obligația de plată a TVA prin taxare inversă, în sarcina beneficiarului."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se înregistrează o factură Google primită de un SRL din România?

Un SRL din România primește o factură de la Google (de regulă de la entitatea din Irlanda) pentru publicitate online sau alte servicii electronice, de obicei fără TVA menționat. Nu e o scăpare a Google — e regula normală pentru servicii B2B intracomunitare: TVA-ul se datorează în România, de către beneficiar, prin taxare inversă.

## Temeiul legal

::: ghid-temei
„Locul de prestare a serviciilor către o persoană impozabilă care acționează ca atare este locul unde respectiva persoană care primește serviciile își are stabilit sediul activității sale economice. [...] Taxa este datorată de orice persoană impozabilă, inclusiv de către persoana juridică neimpozabilă înregistrată în scopuri de TVA conform art. 316 sau 317, care este beneficiar al serviciilor care au locul prestării în România conform art. 278 alin. (2) și care sunt furnizate de către o persoană impozabilă care nu este stabilită pe teritoriul României."
— Codul fiscal (Legea 227/2015), art. 278 alin. (2) și art. 307 alin. (2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Mecanismul e taxarea inversă intracomunitară pentru servicii, distinctă de taxarea inversă internă de la art. 331:

- Fiind un serviciu B2B, **locul prestării e la sediul beneficiarului** — SRL-ul din România — indiferent unde e stabilit Google.
- Beneficiarul, dacă e **înregistrat în scopuri de TVA** (art. 316 sau 317), e obligat la plata taxei prin taxare inversă: colectează și deduce simultan TVA-ul aferent (nota contabilă 4426 = 4427), fără ca Google să fi facturat vreo taxă.
- Această achiziție de servicii se raportează separat de achizițiile de bunuri: în **declarația recapitulativă D390**, la categoria S (achiziții intracomunitare de servicii), și în **decontul de TVA (D300)**, ca taxă colectată și dedusă simultan.

## Ce se greșește în practică

- Se caută TVA pe factura Google și, negăsindu-l, se înregistrează factura ca și cum ar fi scutită de TVA — de fapt taxa e datorată de beneficiar, prin taxare inversă, nu e o operațiune scutită.
- Se confundă taxarea inversă intracomunitară pentru servicii (art. 307 alin. (2)) cu taxarea inversă internă (art. 331), care se aplică doar pe teritoriul României, pentru categorii de bunuri/servicii enumerate limitativ.
- Nu se raportează achiziția în D390, deși e o achiziție intracomunitară de servicii care trebuie inclusă în declarația recapitulativă, la categoria S.

## Ce face iConta.eu

iConta.eu oferă mecanismul contabil general de **taxare inversă** la înregistrarea unei facturi de achiziție (nota 4426 = 4427), pe care contabilul îl aplică la introducerea facturii Google. Aplicația **nu identifică automat** o factură de la un prestator din alt stat membru ca fiind supusă taxării inverse — încadrarea corectă rămâne o alegere a contabilului la introducerea facturii, după care aplicația preia automat operațiunea în D300 și în D390.

[iConta.eu](/)
