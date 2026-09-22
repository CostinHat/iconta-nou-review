---
title: Cum completez D301 pentru achiziții de servicii intracomunitare?
description: Achizițiile de servicii de la furnizori stabiliți în UE (Google, Microsoft, hosting etc.) se declară în Secțiunea 4.1 a D301, prin taxare inversă conform art. 307 alin. (2) Cod fiscal.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum completez D301 pentru achiziții de servicii intracomunitare?

O firmă neplătitoare de TVA (neînregistrată conform art. 316) care primește o factură de servicii de la un furnizor stabilit în alt stat membru UE — de exemplu Google Ireland Limited sau Microsoft Ireland Operations Limited — devine, prin efectul legii, obligată la plata TVA prin taxare inversă. Această operațiune se declară în Secțiunea 4.1 a decontului special D301.

## Temeiul legal

::: ghid-temei
**Articolul 307 alin. (2)**: Taxa este datorată de orice persoană impozabilă [...] care este beneficiar al serviciilor care au locul prestării în România conform art. 278 alin. (2) și care sunt furnizate de către o persoană impozabilă care nu este stabilită pe teritoriul României [...]

**Articolul 278 alin. (2)**: Locul de prestare a serviciilor către o persoană impozabilă care acționează ca atare este locul unde respectiva persoană care primește serviciile își are stabilit sediul activității sale economice. [...]

Instrucțiuni OPANAF 592/2016 — rollup Secțiunea 4→4.1: În secțiunea 4.1 se preiau din secțiunea 4 doar achizițiile de servicii intracomunitare, pentru care beneficiarul este obligat la plata taxei pe valoarea adăugată conform art. 307 alin. (2) din Codul fiscal.

Instrucțiuni OPANAF 592/2016 — condiția furnizorului stabilit în UE: Secțiunea 4.1 [...] se completează de către [...] persoanele juridice neimpozabile care sunt înregistrate conform art. 317 [...], care sunt beneficiare ale serviciilor [...] furnizate de către persoane impozabile care nu sunt stabilite pe teritoriul României conform art. 266 alin. (2) din Codul fiscal, **dar care sunt stabilite în Comunitate** [...]
:::

## De ce servicii precum Google Workspace intră în Secțiunea 4.1

Regula generală B2B ("regula sediului beneficiarului", art. 278 alin. (2)) stabilește că locul prestării serviciului este România, pentru că firma română este cea care primește serviciul. Din acest motiv, deși furnizorul e stabilit în alt stat UE, TVA se datorează în România, iar obligația de plată trece de la furnizor la beneficiar (taxare inversă, art. 307 alin. (2)).

Condiția obligatorie pentru Secțiunea 4.1 este ca furnizorul să fie **stabilit în Comunitate** (UE). Furnizori precum Google Ireland Limited, Microsoft Ireland Operations Limited sau Booking.com B.V. (Olanda) îndeplinesc această condiție. Dacă furnizorul ar fi dintr-un stat din afara UE, operațiunea nu s-ar mai încadra la Secțiunea 4.1, ci la Secțiunea 4 generică, cu alt temei (art. 307 alin. (6)).

::: ghid-exemplu
O firmă neplătitoare primește o factură Google Workspace de 12 EUR, curs BNR la data exigibilității 4,9700 lei/EUR.

Baza = 12 × 4,9700 = 59,64 lei (rotunjit conform regulii aritmetice, nu bancare)
TVA (cotă standard 21%, de la 01.08.2025) = 59,64 × 21% = 12,52 lei

Suma se declară în Secțiunea 4.1 a D301, la baza și TVA-ul aferente lunii în care a luat naștere exigibilitatea taxei.
:::

## Ce se greșește în practică

- Se introduce operațiunea în Secțiunea 4 generică în loc de 4.1, deși furnizorul e stabilit în UE — cele două secțiuni au temeiuri și instrucțiuni diferite.
- Se folosește cursul de schimb de la data plății facturii, nu cursul valabil la data exigibilității taxei (art. 290 alin. (2)).
- Se omite obținerea codului special de TVA (art. 317) înainte de primirea primului serviciu din UE, ceea ce duce la înregistrare din oficiu de către ANAF.
- Se presupune greșit că există un plafon valoric sub care operațiunea nu trebuie declarată — la servicii, taxarea inversă se aplică de la prima factură, indiferent de sumă.
- Se confundă sensul operațiunii: D301 declară doar achiziții, nu și vânzările de servicii către clienți din UE.

## Ce face iConta.eu

Pentru `tip=5` (Secțiunea 4.1), aplicația face rollup automat al bazei și TVA în totalul Secțiunii 4, conform instrucțiunilor OPANAF 592/2016. Baza se calculează automat din `val_valuta × curs`, cu rotunjire aritmetică (`ROUND_HALF_UP`), iar dacă cursul valutar lipsește sau este introdus ca zero, generarea este refuzată explicit — cursul trebuie introdus manual de contabil, aplicația nu îl preia automat de la BNR sau BCE.

Aplicația nu validează însă automat țara furnizorului împotriva unei liste de state membre UE la introducerea unei operațiuni `tip=5` — câmpul de țară al partenerului este opțional și liber. Responsabilitatea încadrării corecte (furnizor stabilit în UE vs. în afara UE) rămâne a contabilului.

[iConta.eu](/)
