---
title: "Ce transporturi se declară în RO e-Transport: doar bunurile cu risc fiscal ridicat sau și cele internaționale?"
description: "Ambele. RO e-Transport monitorizează transporturile naționale de bunuri cu risc fiscal ridicat și toate transporturile rutiere internaționale de bunuri, indiferent de marfă."
published: 2026-09-29
modified: 2026-09-29
poarta: v1
---

# Ce transporturi se declară în RO e-Transport: doar bunurile cu risc fiscal ridicat sau și cele internaționale?

Ambele categorii. RO e-Transport a pornit ca sistem pentru bunurile cu risc fiscal ridicat, dar forma în vigoare a OUG 41/2022 monitorizează două tipuri de transporturi: transporturile rutiere pe teritoriul național ale bunurilor cu risc fiscal ridicat și transporturile rutiere internaționale de bunuri. La cele internaționale, obligația nu depinde de natura mărfii.

Diferența contează pentru clienții cabinetului care fac achiziții sau livrări intracomunitare, importuri ori exporturi cu mărfuri „obișnuite" (mobilier, piese, textile): și acestea se declară, iar lipsa codului UIT se sancționează la fel.

## Temeiul legal

::: ghid-temei
„(2) Prin Sistemul RO e-Transport sunt monitorizate transporturile rutiere pe teritoriul național ale bunurilor cu risc fiscal ridicat și transporturile rutiere internaționale de bunuri."
— OUG 41/2022, art. 1 alin. (2) (sursă: [OUG nr. 41/2022 pentru instituirea Sistemului național RO e-Transport](https://legislatie.just.ro/Public/DetaliiDocument/253801))

„(3) Utilizatorii prevăzuți la art. 8^1 sunt obligați să declare în Sistemul RO e-Transport datele referitoare la transporturile internaționale de bunuri, astfel încât să poată fi identificate prin codul UIT."
— OUG 41/2022, art. 9 alin. (3) (sursă: [OUG nr. 41/2022 pentru instituirea Sistemului național RO e-Transport](https://legislatie.just.ro/Public/DetaliiDocument/253801))
:::

Cine declară, pe tipuri de transport:

- **Transport național de bunuri cu risc fiscal ridicat** — bunurile sunt cele stabilite prin ordin al președintelui ANAF; declară, după caz, furnizorul din România în tranzacțiile interne, operatorul economic care își transportă propriile bunuri între locații sau alți utilizatori din art. 8 alin. (1).
- **Transport internațional, orice marfă** (art. 8^1): destinatarul din declarația vamală de import sau expeditorul din declarația de export; beneficiarul din România la achiziții intracomunitare; furnizorul din România la livrări intracomunitare; depozitarul la bunurile în tranzit; plus cazurile de nontransfer și stocuri la dispoziția clientului.
- **Traseul monitorizat** este doar porțiunea de pe teritoriul național, de exemplu de la punctul de trecere a frontierei până la locul de descărcare, la o achiziție intracomunitară (art. 2 pct. 9).

Excepții (art. 16): transporturile pentru misiuni diplomatice, organizații internaționale și forțe armate NATO/UE în condițiile legii, produsele accizabile care circulă cu e-DA sau e-DAS în EMCS și coletele poștale transportate de prestatorii de servicii poștale.

::: ghid-exemplu
SC Exemplu SRL cumpără din Germania mobilier de birou în valoare de 50.000 lei. Mobilierul nu e bun cu risc fiscal ridicat, dar transportul e o achiziție intracomunitară, deci internațional. SC Exemplu SRL, ca beneficiar din România, declară transportul și obține codul UIT, pe care îl pune la dispoziția transportatorului înainte ca vehiculul să intre în țară.
:::

## Ce se greșește în practică

- Se verifică doar lista bunurilor cu risc fiscal ridicat și, dacă marfa nu e pe listă, se concluzionează că nu există obligație, deși transportul e intracomunitar.
- Se lasă declararea în seama transportatorului străin; obligația e a beneficiarului sau furnizorului din România.
- Se crede că la livrările intracomunitare declară clientul din celălalt stat; declară furnizorul din România.
- Se aplică excepția pentru accizabile și la produse care nu circulă cu e-DA sau e-DAS.

## Ce face iConta.eu

Cardul e-Transport din iConta.eu generează XML-ul notificării în structura oficială v2 (tipul operațiunii, bunurile cu cod tarifar, cantitate, greutăți și valoare, partenerul, locurile de încărcare și descărcare, vehiculul) și verifică fereastra de timp a codului UIT. Încadrarea transportului ca național cu risc fiscal ridicat sau internațional și alegerea tipului de operațiune rămân decizia contabilului.

[iConta.eu](/)
