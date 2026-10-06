---
title: "Facturi de corecție după reînregistrarea în scopuri de TVA: cum se declară TVA în D311"
description: "Dacă ai emis facturi fără TVA cât timp codul era anulat și nu ai declarat taxa, după reînregistrare emiți facturi de corecție, iar TVA se declară în secțiunea V a D311, nu în decont."
published: 2026-10-02
modified: 2026-10-02
poarta: v1
---

# Facturi de corecție după reînregistrarea în scopuri de TVA: cum se declară TVA în D311

Situația vizată: cât timp codul de TVA a fost anulat, firma a emis facturi, dar nu a colectat TVA și nu a depus D311. După reînregistrare, firma **emite facturi de corecție** pentru acele livrări și prestări. TVA din facturile de corecție **nu intră în decontul de TVA** dacă nu există diferențe. Se declară în D311, secțiunea V, și se plătește cu accesorii.

Greșeala tipică: facturile de corecție sunt trecute în D300 ca operațiuni ale lunii curente, iar accesoriile nu se mai calculează de la data corectă.

## Temeiul legal

::: ghid-temei
„c) persoana impozabilă nu a colectat TVA pentru livrările de bunuri/prestările de servicii taxabile efectuate în perioada în care a avut codul de înregistrare în scopuri de TVA anulat, respectiv nu a depus declarația privind taxa pe valoarea adăugată colectată care trebuie plătită conform art. 11 alin. (6) și (8) din Codul fiscal, dar a emis facturi. În această situație, după reînregistrarea în scopuri de TVA, persoana impozabilă trebuie să emită facturi de corecție conform art. 330 alin. (1) lit. b) din Codul fiscal."
— HG 1/2016 (Normele metodologice ale Codului fiscal), titlul I, pct. 5^1 alin. (2) lit. c) (sursă: [HG nr. 1/2016 (Normele metodologice ale Codului fiscal)](https://legislatie.just.ro/Public/DetaliiDocument/174822))

„Persoana impozabilă datorează obligații fiscale accesorii conform art. 173 și 181 din Legea nr. 207/2015 privind Codul de procedură fiscală, cu modificările și completările ulterioare, de la data la care avea obligația să plătească TVA aferentă livrărilor de bunuri/prestărilor de servicii taxabile, efectuate în perioada în care a avut codul de înregistrare în scopuri de TVA anulat, și până la data plății taxei"
— HG 1/2016, titlul I, pct. 5^1 alin. (2) lit. c) (sursă: [HG nr. 1/2016 (Normele metodologice ale Codului fiscal)](https://legislatie.just.ro/Public/DetaliiDocument/174822))
:::

::: ghid-temei
„emit facturi de corecție pentru livrările de bunuri/prestările de servicii taxabile efectuate în perioada în care au avut codul de înregistrare în scopuri de TVA anulat, pentru care nu au colectat TVA, dar au emis facturi în acea perioadă"
— OPANAF nr. 188/2018, anexa nr. 2 (instrucțiunile de completare a D311) (sursă: [OPANAF nr. 188/2018 pentru aprobarea formularului 311](https://legislatie.just.ro/Public/DetaliiDocument/197537))
:::

Ce rezultă concret:

- **Cine:** persoanele cu codul anulat în temeiul art. 316 alin. (11) lit. a)-e) sau h) din Codul fiscal (Legea 227/2015), reînregistrate conform art. 316 alin. (12). Regula se aplică reînregistrărilor de la 1 ianuarie 2017 (pct. 5^1 alin. (4)).
- **Ce document:** factura de corecție, emisă conform art. 330 alin. (1) lit. b) din Codul fiscal, în care TVA colectată pentru perioada fără cod apare distinct.
- **Unde se declară taxa:** în D311, secțiunea V, coloanele „Baza impozabilă" și „TVA de plată". Instrucțiunile cer aici baza pentru operațiunile „pentru care au fost emise facturi, dar nu a fost colectată TVA".
- **Diferențele merg în decont.** Dacă TVA din factura de corecție diferă de taxa care trebuia colectată, în D300 se trece numai diferența, la TVA colectată (pct. 5^1 alin. (3)). Taxa care trebuia colectată rămâne în D311.
- **Când se depune:** după reînregistrare, la emiterea facturilor de corecție. Instrucțiunile nu fixează o zi anume pentru această situație.
- **Accesorii:** se datorează de la data la care trebuia plătită taxa până la data plății, potrivit art. 173 și 181 din Codul de procedură fiscală (Legea 207/2015).

::: ghid-exemplu
SC Exemplu SRL a avut codul anulat din oficiu între februarie și iunie 2026 și a fost reînregistrată din iulie 2026. În aprilie 2026 a emis o factură de 10.000 lei, fără TVA, pentru o prestare taxabilă. Nu a depus D311.

După reînregistrare emite o factură de corecție care arată distinct TVA: 10.000 × 21% = 2.100 lei (cota standard, art. 291 alin. (1) din Codul fiscal).

În D311, secțiunea V: baza 10.000 lei, TVA de plată 2.100 lei. Perioada de raportare este aprilie 2026, luna exigibilității. Factura de corecție nu se trece la TVA colectată în D300 din iulie, pentru că nu există diferențe. Accesoriile curg de la data la care trebuia plătită taxa pentru aprilie până la plata celor 2.100 lei.
:::

## Ce se greșește în practică

- Factura de corecție se înscrie la TVA colectată în D300 din luna emiterii. Taxa apare declarată greșit, iar D311 lipsește.
- Se trece în decont întreaga taxă, deși acolo merg numai diferențele.
- Se plătește taxa fără accesorii, ca și cum obligația ar fi apărut abia la reînregistrare.
- Se aplică procedura și la codul anulat la cerere, pentru regimul special de scutire. Pct. 5^1 se referă la lit. a)-e) și h).

## Ce face iConta.eu

În iConta.eu se pot emite facturi, inclusiv storno, iar decontul D300 are rânduri manuale pentru diferențe și regularizări. D311 din aplicație acoperă însă doar situația de după anularea codului (secțiunea IV). Secțiunea V, pentru reînregistrare, nu e încă disponibilă, așa că D311 pentru facturile de corecție se întocmește în afara aplicației. Aplicația nu marchează separat facturile emise pentru perioada fără cod. Contabilul verifică manual ca ele să nu ajungă în TVA colectată din D300 și calculează accesoriile.

[iConta.eu](/)
