---
title: "Triunghiular cu firma din România ca intermediar: obligații"
description: "Ca 'cumpărător revânzător' într-o operațiune triunghiulară, firma din România nu declară achiziția intracomunitară, dar trebuie să raporteze livrarea ulterioară cu cod T în declarația recapitulativă."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Triunghiular cu firma din România ca intermediar: obligații

Măsura de simplificare a operațiunii triunghiulare există exact pentru cazul în care o firmă din România cumpără bunuri dintr-un stat membru și le revinde, fără transport prin România, direct către un client dintr-un al treilea stat membru. Simplificarea scutește intermediarul de o înregistrare suplimentară în statul de sosire a bunurilor, dar nu-l scutește de obligațiile de raportare.

## Temeiul legal

::: ghid-temei
„Nu sunt considerate operațiuni impozabile în România: [...] achiziția intracomunitară de bunuri, efectuată în cadrul unei operațiuni triunghiulare, pentru care locul este în România în conformitate cu prevederile art. 276 alin. (1), atunci când sunt îndeplinite următoarele condiții: 1. achiziția de bunuri este efectuată de către o persoană impozabilă, denumită cumpărător revânzător, care nu este stabilită în România, dar este înregistrată în scopuri de TVA în alt stat membru; [...] 5. beneficiarul livrării ulterioare a fost desemnat în conformitate cu art. 307 alin. (4) ca persoană obligată la plata taxei pentru livrarea efectuată de cumpărătorul revânzător prevăzut la pct. 1."
— Codul fiscal (Legea 227/2015), art. 268 alin. (8) lit. b) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„Orice persoană impozabilă înregistrată în scopuri de TVA [...] trebuie să întocmească și să depună la organele fiscale competente o declarație recapitulativă în care menționează: [...] b) livrările de bunuri efectuate în cadrul unei operațiuni triunghiulare prevăzute la art. 276 alin. (5) efectuate în statul membru de sosire a bunurilor și care se declară drept livrări intracomunitare cu cod T, pentru care exigibilitatea de taxă a luat naștere în luna calendaristică respectivă."
— Codul fiscal, art. 325 alin. (1) lit. b) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Textul de mai sus descrie cazul opus — firma română ca beneficiar final. Când firma din **România e intermediarul** (cumpărătorul revânzător), rolurile se inversează, iar obligațiile ei sunt:

- **Nu declară o achiziție intracomunitară taxabilă** în statul de sosire a bunurilor — condiția 5 de mai sus arată de ce: obligația de plată a taxei trece la beneficiarul final, prin desemnare expresă (echivalentul art. 307 alin. (4), aplicat în statul membru de sosire).
- **Declară totuși livrarea ulterioară către beneficiarul final** în declarația recapitulativă (D390 în România, echivalentul ei local), cu codul special „T", nu cu codul obișnuit de livrare intracomunitară „L" (art. 325 alin. (1) lit. b)).
- Factura emisă către beneficiarul final trebuie să menționeze explicit că operațiunea e o livrare triunghiulară, cu bunurile expediate direct din statul furnizorului către beneficiar, fără să tranziteze România.
- Firma română trebuie să dețină cod de TVA valabil în statul membru din care se face achiziția inițială (sau, dacă operează prin codul RO, condițiile simplificării nu se mai aplică identic) — verificarea acestui aspect ține de fiecare tranzacție.

## Ce se greșește în practică

- Se declară achiziția intracomunitară ca operațiune taxabilă obișnuită, cu taxare inversă, deși condițiile triunghiularei o exceptează de la impozitare în statul de sosire.
- Se raportează livrarea ulterioară cu codul obișnuit „L" în loc de codul special „T", ceea ce nu reflectă corect natura de operațiune triunghiulară față de autoritățile fiscale.
- Se presupune că simplificarea se aplică automat, fără verificarea celor cinci condiții cumulative (identitatea cumpărătorului revânzător, scopul achiziției, transportul direct, statutul beneficiarului, desemnarea acestuia ca plătitor).

## Ce face iConta.eu

`core/d390.py`, modulul de declarație recapitulativă VIES al iConta.eu, susține explicit codul „T" pentru livrările efectuate în cadrul unei operațiuni triunghiulare, ca tip distinct de operațiune (alături de L, A, P, S, R), inclus corect în formula oficială a totalului de plată. Clasificarea unei facturi emise ca „T" în loc de „L" nu se face automat din datele facturii — modulul o tratează explicit ca **clasificare manuală a contabilului**, prin parametrul `manual` al funcției de calcul.

`core/intracomunitar.py`, modulul de operațiuni intracomunitare al aplicației, acoperă livrarea intracomunitară standard (cu verificare VIES) și taxarea inversă generică la achiziții, dar nu are o funcție dedicată care să valideze cele cinci condiții ale simplificării triunghiulare sau să determine automat că o tranzacție se califică drept operațiune triunghiulară — încadrarea rămâne o evaluare a contabilului.

[iConta.eu](/)
