---
title: Trebuie depusă D390 pentru comisioanele unei platforme de livrare din UE?
description: Da, cu codul S (achiziție intracomunitară de servicii), dar numai dacă entitatea platformei care emite factura de comision este stabilită într-un stat membru UE — dacă e stabilită în afara UE, comisionul nu intră în D390, chiar dacă apare la taxare inversă în decontul de TVA.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Trebuie depusă D390 pentru comisioanele unei platforme de livrare din UE?

Firmele care lucrează cu platforme de livrare (food-delivery, curierat, marketplace) plătesc adesea un comision facturat de entitatea care operează platforma. Dacă acea entitate e stabilită într-un alt stat membru UE, comisionul e o achiziție intracomunitară de servicii și trebuie raportată în D390 — dar verificarea locului de stabilire al platformei e pasul care se sare cel mai des.

## Temeiul legal

::: ghid-temei
**Art. 278 alin. (2)**: „Locul de prestare a serviciilor către o persoană impozabilă care acționează ca atare este locul unde respectiva persoană care primește serviciile își are stabilit sediul activității sale economice. [...]"

**Art. 307 alin. (2)**: „Taxa este datorată de orice persoană impozabilă, inclusiv de către persoana juridică neimpozabilă înregistrată în scopuri de TVA conform art. 316 sau 317, care este beneficiar al serviciilor care au locul prestării în România conform art. 278 alin. (2) și care sunt furnizate de către o persoană impozabilă care nu este stabilită pe teritoriul României [...]"

**OPANAF 705/2020, anexa 2**: „e) «Achiziții intracomunitare de servicii» - se înscrie suma totală a achizițiilor intracomunitare de servicii pentru care se aplică prevederile art. 278 alin. (2) din Codul fiscal, altele decât cele scutite de TVA, pe fiecare prestator în parte, care este stabilit în Uniunea Europeană, pentru care exigibilitatea taxei intervine în luna calendaristică respectivă. Nu vor fi declarate prestările de servicii prevăzute la art. 278 alin. (2) din Codul fiscal, dacă prestatorul serviciului este o persoană impozabilă care nu este stabilită pe teritoriul Comunității;"
:::

## De ce contează unde e stabilită platforma

Comisionul reținut de o platformă de livrare e, din punct de vedere fiscal, un serviciu B2B cu locul prestării la sediul beneficiarului (art. 278 alin. (2)) — firma din România datorează taxa prin taxare inversă (art. 307 alin. (2)). Până aici, operațiunea e la fel indiferent de unde e stabilită platforma. Diferența apare la D390: instrucțiunile de completare exclud explicit din declarație serviciile al căror prestator nu e stabilit pe teritoriul UE.

Multe platforme de livrare mari operează prin entități înregistrate în afara UE (sau prin filiale UE care facturează în numele unei entități-mamă non-UE). Dacă entitatea emitentă a facturii de comision nu e stabilită într-un stat membru UE, comisionul respectiv rămâne o taxare inversă validă în decontul de TVA (D300/D301), dar **nu intră în D390**.

## Ce se greșește în practică

- Se presupune că orice comision plătit unei platforme „europene" (după nume sau piață) trebuie automat în D390, fără verificarea sediului entității facturante.
- Se raportează în S toate comisioanele de platformă, inclusiv cele de la entități stabilite în afara UE, care ar trebui excluse din D390.
- Nu se marchează factura de comision ca „serviciu" la introducere, iar operațiunea ajunge implicit clasificată ca achiziție de bunuri (A), nu ca achiziție de servicii (S).
- Se confundă taxarea inversă din decontul de TVA (care se aplică oricărui prestator non-rezident, UE sau non-UE) cu obligația de raportare în D390 (limitată strict la prestatori stabiliți în UE).

## Ce face iConta.eu

O factură primită e implicit clasificată ca achiziție de bunuri (cod A); pentru ca un comision de platformă să apară corect ca achiziție de servicii (cod S), factura trebuie marcată explicit cu axa „servicii" la introducere, sau reclasificată manual în ecranul D390 — o factură primită nu poate deveni niciodată L, T, P sau R, doar A sau S. Aplicația nu verifică automat țara de stabilire a platformei emitente față de lista de state UE; această verificare rămâne în responsabilitatea contabilului, la introducerea facturii.

[iConta.eu](/)
