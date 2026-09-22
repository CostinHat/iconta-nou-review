---
title: Ce obligații TVA are un SRL neplătitor care cumpără servicii din UE?
description: Un SRL neplătitor care cumpără servicii de la un furnizor stabilit în UE trebuie să se înregistreze special conform art. 317 înainte de primirea serviciului și să declare taxarea inversă în Secțiunea 4.1 a D301.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Ce obligații TVA are un SRL neplătitor care cumpără servicii din UE?

Un SRL care nu este înregistrat normal în scopuri de TVA (nu depășește plafonul de scutire de la art. 316) nu este scutit de toate obligațiile TVA doar pentru că nu emite facturi cu TVA colectat. De îndată ce firma cumpără un serviciu de la un furnizor stabilit în alt stat membru UE, intră sub incidența taxării inverse și a obligațiilor conexe.

## Temeiul legal

::: ghid-temei
**Articolul 307 alin. (2)**: Taxa este datorată de orice persoană impozabilă [...] care este beneficiar al serviciilor care au locul prestării în România conform art. 278 alin. (2) și care sunt furnizate de către o persoană impozabilă care nu este stabilită pe teritoriul României [...]

**Articolul 317 alin. (1) lit. c)**: [...] persoana impozabilă [...] dacă primesc de la un prestator, persoană impozabilă stabilită în alt stat membru, servicii pentru care sunt obligate la plata taxei în România conform art. 307 alin. (2), **înaintea primirii serviciilor respective**.

**Alin. (10)**: Înregistrarea în scopuri de TVA conform prezentului articol nu conferă persoanei calitatea de persoană înregistrată normal în scopuri de TVA, acest cod fiind utilizat numai pentru operațiunile prevăzute la alin. (1)-(2^1).

**Articolul 324 alin. (2)**: [...] se depune până la data de 25 inclusiv a lunii următoare celei în care ia naștere exigibilitatea operațiunilor menționate la alin. (1). Decontul special de taxă trebuie depus numai pentru perioadele în care ia naștere exigibilitatea taxei.
:::

## Cele două obligații: înregistrarea și declararea

Prima obligație apare **înainte** de primirea propriu-zisă a serviciului: art. 317 alin. (1) lit. c) cere solicitarea codului special de TVA înaintea primirii serviciilor pentru care firma va fi obligată la plata taxei conform art. 307 alin. (2). În practică, acest lucru înseamnă că, teoretic, firma ar trebui să obțină codul special înainte de a primi prima factură de la un furnizor UE — de exemplu, înainte de a activa un abonament software sau de a începe să folosească un serviciu de publicitate online furnizat din alt stat UE. Dacă firma nu solicită la timp acest cod, organul fiscal o poate înregistra din oficiu.

A doua obligație este declararea propriu-zisă: fiecare achiziție de servicii de la un furnizor stabilit în UE se declară în Secțiunea 4.1 a D301, cu taxare inversă conform art. 307 alin. (2), până la data de 25 a lunii următoare celei în care a luat naștere exigibilitatea taxei. Codul special de TVA obținut conform art. 317 nu transformă firma într-un plătitor de TVA "normal" — ea rămâne neplătitoare pentru operațiunile sale interne, dar are, punctual, obligații de declarare pentru achizițiile intracomunitare.

## Ce se greșește în practică

- Se solicită codul special de TVA (art. 317) abia după ce apar mai multe facturi de la furnizori UE, nu înainte de primul serviciu primit, cum cere legea.
- Se presupune că, pentru servicii, există un plafon valoric sub care declararea nu e necesară — spre deosebire de achizițiile de bunuri, la servicii nu există un asemenea plafon.
- Se confundă înregistrarea specială art. 317 cu înregistrarea normală în scopuri de TVA (art. 316), și se cred eronat obligate la colectarea TVA pe facturile emise clienților interni.
- Se depune D301 și pentru lunile în care nu a existat nicio operațiune cu exigibilitate în acea perioadă, deși legea cere depunerea doar pentru perioadele în care ia naștere exigibilitatea taxei.

## Ce face iConta.eu

Introducerea unei operațiuni D301 este blocată de aplicație dacă firma este marcată în vectorul fiscal drept plătitoare de TVA — D301 este rezervat exclusiv neplătitorilor. Pentru achizițiile de servicii intracomunitare (Secțiunea 4.1), aplicația calculează automat baza de impozitare din valoarea în valută și cursul introdus, aplică cota validă pentru perioadă și face rollup-ul cerut de instrucțiunile OPANAF 592/2016 în totalul Secțiunii 4.

Marcajul `pers_inreg` (indicând înregistrarea conform art. 317) nu este dedus automat de aplicație din simplul fapt că există operațiuni intracomunitare introduse — el trebuie completat explicit de contabil în profilul firmei, după ce codul special a fost obținut de la ANAF. Dacă acest marcaj lipsește, deși există operațiuni de tip achiziție de bunuri intracomunitare, aplicația emite doar un avertisment, nu blochează generarea.

[iConta.eu](/)
