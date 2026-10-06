---
title: "Produsele accizabile transportate cu e-DA sau e-DAS trebuie declarate și în RO e-Transport?"
description: "Nu. Produsele accizabile care circulă în regim suspensiv sau cu accize plătite în statul de expediție, cu e-DA sau e-DAS emis prin EMCS, sunt exceptate de la RO e-Transport."
published: 2026-09-29
modified: 2026-09-29
poarta: v1
---

# Produsele accizabile transportate cu e-DA sau e-DAS trebuie declarate și în RO e-Transport?

Nu, dacă transportul circulă efectiv sub un document administrativ electronic emis prin EMCS: e-DA (regim suspensiv de accize) sau e-DAS (accize plătite în statul membru de expediție). OUG 41/2022 exceptează aceste transporturi de la toate prevederile sale, deci nu se generează cod UIT pentru ele.

Contează în practică pentru distribuitorii de băuturi alcoolice, bere, vin sau carburanți. Băuturile (codurile NC 2201–2208) sunt pe lista bunurilor cu risc fiscal ridicat. Excepția acoperă însă doar mișcările care au deja propriul sistem de urmărire, EMCS. Aceleași produse, vândute în țară după eliberarea pentru consum și fără e-DA, intră din nou sub RO e-Transport.

## Temeiul legal

::: ghid-temei
„Fac excepție de la prevederile prezentei ordonanțe de urgență următoarele transporturi: [...] b) transportul produselor accizabile care circulă în regim suspensiv de accize sau cu accize plătite în statul membru de expediție, potrivit titlului VIII „Accize și alte taxe speciale“ din Legea nr. 227/2015 , cu modificările și completările ulterioare, respectiv prin utilizarea sistemului de control al mișcărilor cu produse accizabile, denumit EMCS, pentru emiterea documentului administrativ electronic e-DA sau a documentului administrativ electronic simplificat e-DAS;"
— OUG 41/2022, art. 16 lit. b) (sursă: [OUG nr. 41/2022 pentru instituirea Sistemului național RO e-Transport](https://legislatie.just.ro/Public/DetaliiDocument/253801))
:::

::: ghid-temei
„Băuturi, lichide alcoolice și oțet […], care se încadrează la codurile NC de la 2201 la 2208 inclusiv"
— Ordinul ANAF nr. 802/2022, anexa, pct. 3 (sursă: [OPANAF nr. 802/2022 privind bunurile cu risc fiscal ridicat monitorizate prin RO e-Transport](https://legislatie.just.ro/Public/DetaliiDocument/254608))
:::

Ce trebuie îndeplinit ca excepția să se aplice:

- **Produs accizabil** în sensul titlului VIII din Codul fiscal.
- **Regim de circulație**: regim suspensiv de accize **sau** accize plătite în statul membru de expediție.
- **Document EMCS**: e-DA (regim suspensiv) sau e-DAS (accize plătite). Fără acest document, nu există excepție.

Dacă o condiție lipsește, se revine la regula generală. Pentru băuturile cu risc fiscal ridicat transportate în țară, furnizorul din România declară transportul și obține codul UIT (art. 8 alin. (1) lit. c)).

Excepția figurează în art. 16, care se aplică întregii ordonanțe. Prin urmare, ea privește atât transporturile naționale de bunuri cu risc fiscal ridicat, cât și transporturile rutiere internaționale, de exemplu o achiziție intracomunitară de vin sub e-DAS.

::: ghid-exemplu
SC Exemplu SRL, antrepozitar autorizat, expediază 10.000 l de vin în regim suspensiv către un antrepozit din alt județ, cu e-DA emis în EMCS. Pentru acest transport nu se generează cod UIT.

Ulterior, aceeași firmă vinde 2.000 l de vin eliberat pentru consum către un magazin, fără e-DA, într-un transport de 30.000 lei fără TVA. Vinul intră la codurile NC 2201–2208, deci SC Exemplu SRL, ca furnizor, declară transportul în RO e-Transport și transmite codul UIT transportatorului înainte de plecare.
:::

## Ce se greșește în practică

- **Excepția se aplică tuturor produselor accizabile, indiferent de document.** Contează documentul EMCS efectiv emis pentru acel transport, nu natura produsului.
- **Se omite RO e-Transport după eliberarea pentru consum.** Băuturile vândute în țară fără e-DA/e-DAS rămân bunuri cu risc fiscal ridicat.
- **Se generează cod UIT pentru o mișcare deja acoperită de e-DA.** Legea nu o cere, iar declarația dublă poate crea neconcordanțe între cele două sisteme dacă datele diferă.
- **Nu se verifică partida mixtă.** Dacă în același camion sunt și bunuri fără e-DA (de exemplu apă minerală, cod NC 2201) care nu circulă sub EMCS, pentru ele excepția nu operează.

## Ce face iConta.eu

iConta.eu are un card e-Transport care generează XML-ul notificării (structura oficială v2) pentru obținerea codului UIT: tipul operațiunii, bunurile cu cod tarifar, cantitate, greutăți și valoare, partenerul, vehiculul, locurile de încărcare și descărcare. Aplicația nu gestionează documente EMCS (e-DA/e-DAS) și nu decide dacă un transport este exceptat. Încadrarea în art. 16 lit. b) rămâne decizia contabilului, pe baza documentului de circulație al fiecărui transport.

[iConta.eu](/)
