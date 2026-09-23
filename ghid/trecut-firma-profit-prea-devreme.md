---
title: Ce fac dacă am trecut firma la profit prea devreme?
description: Trecerea prematură la impozit pe profit se corectează la loc, la micro, dacă firma încă îndeplinește condițiile de eligibilitate — verificarea eligibilității rămâne însă manuală.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Ce fac dacă am trecut firma la profit prea devreme?

Dacă ai schimbat regimul fiscal la profit înainte ca firma să fi depășit efectiv plafonul (sau altă condiție de eligibilitate pentru micro), corecția e posibilă — dar depinde de verificarea manuală a condițiilor, pentru că aplicația nu le validează automat.

## Temeiul legal

::: ghid-temei
**Art. 47 alin. (1) lit. c) CF** (condiție de eligibilitate micro): „a realizat venituri care nu au depășit echivalentul în lei a 100.000 euro. Cursul de schimb pentru determinarea echivalentului în euro este cel valabil la închiderea exercițiului financiar în care s-au înregistrat veniturile." Sursă: `anaf_surse/cod_fiscal_227_2015_consolidat.txt`, linia 6095 (modificat de OUG 8/2026, art. 6 pct. 15).

Alte condiții de eligibilitate micro, din același articol: nedepunerea în termen a situațiilor financiare anuale (linia 6422), pierderea condiției salariatului — art. 47 alin. 1 lit. g) (liniile 6427-6429), condiția „o singură microîntreprindere" la asociați care dețin peste 25% la firme legate (linia 6471).
:::

Dacă firma a fost trecută la profit din eroare (de exemplu, o estimare greșită a veniturilor, sau o confuzie cu o altă condiție de eligibilitate), și la verificare se dovedește că îndeplinea toate condițiile de la art. 47 (venituri sub 100.000 euro, situații financiare depuse la timp, condiția salariatului, „o singură microîntreprindere" la asociați cu participații peste 25% la firme legate), regimul poate fi corectat înapoi la micro.

Verificarea acestor condiții e integral manuală — iConta nu are nicio constantă de plafon micro sau vreo logică de „întreprinderi legate" în motorul de calcul, deci nu validează și nu contestă alegerea regimului fiscal introdus de contabil.

Corectarea propriu-zisă urmează aceeași regulă generală: dacă firma nu are perioade fiscale închise în intervalul afectat, e o simplă resalvare a câmpului `regim_fiscal`; dacă are, trebuie parcursă calea de redeschidere → corectare → închidere la loc.

## Ce se greșește în practică

- Se presupune că, odată trecută la profit, firma nu mai poate reveni la micro în cursul aceluiași an, deși legea nu interzice corectarea unei erori de aplicare a regimului.
- Se verifică doar condiția de venituri (100.000 euro), ignorând celelalte condiții de eligibilitate din art. 47 (situații financiare, salariat, întreprinderi legate).
- Se schimbă vectorul înapoi la micro fără verificarea prealabilă manuală a tuturor condițiilor — aplicația nu semnalează nicio eroare dacă alegerea nu e, de fapt, corectă legal.

## Ce face iConta.eu

Schimbarea `regim_fiscal` e o editare directă în Vector fiscal, validată tehnic (valoare în „micro"/"profit", rol `admin_firma` necesar, regula perioadelor închise), dar **fără nicio verificare a condițiilor de eligibilitate din Codul fiscal** — motorul nu conține nicio constantă de plafon micro sau vreo logică legată de întreprinderi legate. Responsabilitatea verificării eligibilității rămâne integral a contabilului.

[iConta.eu](/)
