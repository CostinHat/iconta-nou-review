---
title: Cum tratez o factură Facebook la un PFA neplătitor de TVA?
description: Mecanismul e cel al taxării inverse la beneficiar, dar secțiunea exactă din D301 (4 sau 4.1) depinde de țara de stabilire a entității care emite factura — verificați acest lucru pe document.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum tratez o factură Facebook la un PFA neplătitor de TVA?

Un serviciu de publicitate cumpărat de la Facebook (Meta) de către un PFA neplătitor de TVA are locul prestării în România, deci PFA-ul e obligat la plata taxei prin taxare inversă. Secțiunea exactă din D301 depinde însă de o informație pe care trebuie verificată direct pe factură: entitatea și țara de stabilire ale furnizorului.

## Temeiul legal

::: ghid-temei
"Locul de prestare a serviciilor către o persoană impozabilă (...) este locul unde respectiva persoană care primește serviciile își are stabilit sediul activității sale economice." — Codul fiscal, Legea nr. 227/2015, art. 278 alin. (2)
:::

::: ghid-temei
"Taxa este datorată de orice persoană impozabilă (...) care este beneficiar al serviciilor care au locul prestării în România conform art. 278 alin. (2) și care sunt furnizate de către o persoană impozabilă care nu este stabilită pe teritoriul României (...)" — Codul fiscal, art. 307 alin. (2)
:::

Dacă entitatea Meta/Facebook care a emis factura e stabilită într-un stat membru UE, achiziția merge la secțiunea 4.1 (tip 5) din D301 și apare automat și în D390 (cod S). Dacă e stabilită în afara UE, achiziția merge la secțiunea 4 generală (art. 307 alin. (6)) și nu intră în D390. Nu presupuneți una dintre variante fără să verificați denumirea și adresa furnizorului de pe factură — Meta poate factura din entități diferite, în funcție de context.

Ca și în orice altă achiziție intracomunitară de servicii, PFA-ul trebuie să fie înregistrat special art. 317 înainte de a face achiziția.

## Ce se greșește în practică

- Se tratează automat orice factură Facebook ca "servicii din UE", fără verificarea entității emitente.
- Se amână declararea pentru că suma e mică — nu există un plafon legal pentru această obligație.
- Se uită înregistrarea art. 317, considerându-se că un PFA neplătitor nu are nicio obligație legată de TVA.

## Ce face iConta.eu

Ecranul D301 nu presupune automat tipul operațiunii pentru un furnizor extern — contabilul alege explicit secțiunea (4 sau 4.1), pe baza documentului avut la dispoziție. Câmpurile țară/cod TVA furnizor sunt opționale, dar completarea lor duce automat operațiunea și în D390, cu codul corect, evitând introducerea manuală dublă.

[iConta.eu](/)
