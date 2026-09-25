---
title: "Garanția de bună execuție reținută în contract: TVA și impozit"
description: "Cum se tratează fiscal, la impozit pe profit și TVA, garanția de bună execuție pe care beneficiarul o reține din contravaloarea unei lucrări sau a unui contract de servicii."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Garanția de bună execuție reținută în contract: TVA și impozit

Când un client reține contractual un procent din valoarea unei lucrări sau a unui contract de servicii, cu titlu de garanție de bună execuție, apar două întrebări fiscale separate: cum se tratează la impozitul pe profit provizionul pe care furnizorul îl constituie pentru eventualele remedieri, și dacă TVA se datorează pe întreaga valoare facturată sau doar pe suma efectiv încasată.

## Temeiul legal

::: ghid-temei
„(1) Contribuabilul are dreptul la deducerea rezervelor și provizioanelor/ajustărilor pentru depreciere, numai în conformitate cu prezentul articol, astfel: [...] b) provizioanele pentru garanții de bună execuție acordate clienților. Provizioanele pentru garanții de bună execuție acordate clienților se deduc trimestrial/anual numai pentru bunurile livrate, lucrările executate și serviciile prestate în cursul trimestrului/anului respectiv pentru care se acordă garanție în perioadele următoare, la nivelul cotelor prevăzute în convențiile încheiate sau la nivelul procentelor de garantare prevăzut în tariful lucrărilor executate ori serviciilor prestate."
— Legea nr. 227/2015 privind Codul fiscal, art. 26 alin. (1) lit. b) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Din articolul de mai sus rezultă tratamentul la **impozitul pe profit**:

- Furnizorul care acordă garanție de bună execuție poate constitui un **provizion deductibil fiscal**, dar numai la nivelul cotei prevăzute în contract sau în tariful lucrării, și numai pentru lucrările/serviciile efectiv livrate/prestate în trimestrul sau anul respectiv.
- Deductibilitatea e condiționată de existența unei convenții/tarif care să prevadă expres procentul de garantare — un provizion constituit fără o astfel de bază contractuală nu se încadrează la art. 26 alin. (1) lit. b).

Pentru **TVA**, Codul fiscal actual nu prevede un regim special, distinct, pentru sumele reținute cu titlu de garanție de bună execuție (regula specifică pentru lucrările de construcții-montaj a existat doar tranzitoriu, pentru garanții constituite până la 31 decembrie 2006). Regula generală rămâne cea din definiția faptului generator și a exigibilității (art. 280): taxa devine exigibilă la data faptului generator (livrare/prestare), regim aplicabil întregii contravalori facturate — reținerea contractuală a unei părți din sumă afectează doar fluxul de numerar dintre părți, nu momentul sau baza de calcul a TVA, cu excepția situației în care furnizorul aplică sistemul de TVA la încasare, caz în care exigibilitatea urmează încasarea efectivă a fiecărei sume, inclusiv a garanției eliberate ulterior.

## Ce se greșește în practică

- Se constituie provizion pentru garanție de bună execuție fără să existe o clauză contractuală sau un tarif care să precizeze procentul de garantare — condiție obligatorie pentru deductibilitate conform art. 26 alin. (1) lit. b).
- Se amână colectarea TVA pentru suma reținută drept garanție, presupunând că taxa devine exigibilă abia la eliberarea garanției — dacă firma nu aplică sistemul de TVA la încasare, taxa e exigibilă la data faptului generator, pe întreaga valoare facturată, indiferent de reținerea contractuală.
- Se confundă tratamentul contabil al provizionului (constituire pe cheltuieli, cont 1512) cu deductibilitatea lui fiscală — provizionul contabil poate exista și fără să fie deductibil, dacă nu respectă condițiile de la art. 26.

## Ce face iConta.eu

iConta.eu are o funcționalitate reală pentru provizioanele de garanție de bună execuție, în `core/provizioane.py`: notele de constituire/reluare a provizionului folosesc explicit contul 1512 (din nomenclatorul `PROVIZIOANE`) și aplicația marchează deductibilitatea fiscală **doar** pentru tipul „garantii" (`deductibil = (tip == "garantii")`), conform art. 26 alin. (1) lit. b) citat mai sus — celelalte tipuri de provizioane din nomenclator (litigii, dezafectare) sunt tratate ca nedeductibile.

Ce nu automatizează astăzi aplicația: nu există o regulă specifică pentru exigibilitatea TVA pe suma reținută drept garanție — pentru că, la verificarea la sursă, Codul fiscal în vigoare nu prevede un regim distinct pentru această situație (regula generală de exigibilitate se aplică integral). Calculul procentului de garantare aplicabil, pe baza contractului, rămâne o valoare introdusă de contabil, nu determinată automat din text contractual.

[iConta.eu](/)
