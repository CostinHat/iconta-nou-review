---
title: "Vânzări fără facturi cât timp codul de TVA a fost anulat: ce faci după reînregistrare?"
description: "După reînregistrare emiți facturi cu TVA distinct pentru vânzările nefacturate din perioada fără cod, declari taxa în D311, secțiunea V, și o plătești cu accesorii de la scadență."
published: 2026-10-02
modified: 2026-10-02
poarta: v1
---

# Vânzări fără facturi cât timp codul de TVA a fost anulat: ce faci după reînregistrare?

Dacă în perioada fără cod de TVA firma a vândut fără să emită facturi și fără să declare taxa, după reînregistrare **emite acum facturile**, cu TVA înscrisă distinct. Taxa din ele nu intră în TVA colectată din decont, dacă nu există diferențe. Se declară în **D311, secțiunea V**, și se plătește cu accesorii de la data la care trebuia plătită.

Spre deosebire de cazul cu facturi emise la timp, aici nu există un document de corectat: factura se emite pentru prima dată, după reînregistrare.

## Temeiul legal

::: ghid-temei
„d) persoana impozabilă nu a colectat TVA pentru livrările de bunuri/prestările de servicii taxabile efectuate în perioada în care a avut codul de înregistrare în scopuri de TVA anulat, respectiv nu a depus declarația privind taxa pe valoarea adăugată colectată care trebuie plătită conform art. 11 alin. (6) și (8) din Codul fiscal și nu a emis facturi. În această situație, facturile emise după reînregistrarea în scopuri de TVA nu se înscriu în decontul de taxă depus conform art. 323 din Codul fiscal, în secțiunea «Taxa pe valoarea adăugată colectată», dacă nu există diferențe [...]"
— HG 1/2016 (Normele metodologice ale Codului fiscal), titlul I, pct. 5^1 alin. (2) lit. d) (sursă: [HG nr. 1/2016 (Normele metodologice ale Codului fiscal)](https://legislatie.just.ro/Public/DetaliiDocument/174822))

„(5) Prevederile alin. (2) nu se aplică în situația în care persoana impozabilă nu are obligația de a emite facturi conform art. 319 din Codul fiscal."
— HG 1/2016, titlul I, pct. 5^1 alin. (5) (sursă: [HG nr. 1/2016 (Normele metodologice ale Codului fiscal)](https://legislatie.just.ro/Public/DetaliiDocument/174822))
:::

::: ghid-temei
„După înregistrarea în scopuri de taxă conform art. 316 alin. (12) , pentru livrările de bunuri/prestările de servicii efectuate în perioada în care au avut codul de înregistrare în scopuri de TVA anulat, persoanele impozabile emit facturi în care înscriu distinct taxa pe valoarea adăugată colectată în perioada respectivă, care nu se înregistrează în decontul de taxă depus conform art. 323 ."
— Codul fiscal (Legea 227/2015), art. 11 alin. (8) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))
:::

Pașii, în ordine:

1. **Identifici operațiunile.** Sunt livrările și prestările taxabile din perioada în care codul a fost anulat din oficiu, în temeiul art. 316 alin. (11) lit. a)-e) sau h).
2. **Emiți facturile.** Facturile cuprind informațiile obligatorii de la art. 319 alin. (20) din Codul fiscal și înscriu distinct TVA aferentă perioadei fără cod.
3. **Declari taxa în D311, secțiunea V.** Instrucțiunile cer aici baza și taxa pentru operațiunile „pentru care nu au fost emise facturi și nu a fost colectată TVA". Perioada de raportare este luna exigibilității taxei care trebuia colectată, nu luna emiterii facturii.
4. **Verifici diferențele.** Dacă taxa înscrisă acum în factură diferă de cea care trebuia colectată, în D300 se trece numai diferența (pct. 5^1 alin. (3)).
5. **Plătești taxa și accesoriile.** Accesoriile se calculează potrivit art. 173 și 181 din Codul de procedură fiscală (Legea 207/2015), de la data la care trebuia plătită taxa până la plată.

Două limite importante:

- **Regula se aplică reînregistrărilor de la 1 ianuarie 2017** (pct. 5^1 alin. (4)).
- **Nu se aplică dacă nu exista obligația de facturare** conform art. 319 (pct. 5^1 alin. (5)). Pentru operațiunile fără obligație de facturare, normele nu mai descriu procedura din alin. (2). Tratamentul acestor operațiuni trebuie analizat separat, caz cu caz.

::: ghid-exemplu
SC Exemplu SRL a avut codul anulat din oficiu de la 1 martie 2026 și a fost reînregistrată în august 2026. În aprilie 2026 a prestat servicii de 20.000 lei către o firmă și în mai 2026 servicii de 15.000 lei către altă firmă. Nu a emis facturi și nu a depus D311.

În august 2026 emite două facturi, cu TVA la cota standard de 21% (art. 291 alin. (1) din Codul fiscal):

- aprilie: 20.000 × 21% = 4.200 lei;
- mai: 15.000 × 21% = 3.150 lei.

Depune două D311 (secțiunea V): una pentru aprilie 2026 (bază 20.000, TVA 4.200) și una pentru mai 2026 (bază 15.000, TVA 3.150). Total de plată: 7.350 lei, plus accesorii calculate separat pentru fiecare lună. Facturile nu intră la TVA colectată în D300 din august.
:::

## Ce se greșește în practică

- Facturile se emit cu data și TVA din luna curentă și se trec în D300, ca vânzări noi.
- Se depune o singură D311 pe luna emiterii, în loc de câte una pentru fiecare lună de exigibilitate.
- Accesoriile se calculează de la reînregistrare, nu de la data la care trebuia plătită taxa.
- Procedura se aplică și operațiunilor pentru care nu exista obligație de facturare, fără să se verifice alin. (5).

## Ce face iConta.eu

În iConta.eu facturile se emit din modulul de facturare, iar D300 are rânduri manuale pentru diferențe. D311 din aplicație acoperă însă doar situația de după anularea codului (secțiunea IV). Secțiunea V, pentru reînregistrare, nu e încă disponibilă, așa că D311 pentru aceste vânzări se întocmește în afara aplicației. Aplicația nu calculează accesoriile și nu marchează separat facturile emise pentru perioada fără cod. Contabilul verifică manual tratamentul lor în decont.

[iConta.eu](/)
