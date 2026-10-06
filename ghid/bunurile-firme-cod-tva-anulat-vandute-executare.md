---
title: "Bunurile unei firme cu cod TVA anulat, vândute prin executare silită: cine depune D311?"
description: "D311 o depune firma executată, al cărei cod de TVA a fost anulat din oficiu. Plata TVA o face însă organul de executare silită sau, după caz, cumpărătorul, nu firma."
published: 2026-10-02
modified: 2026-10-02
poarta: v1
---

# Bunurile unei firme cu cod TVA anulat, vândute prin executare silită: cine depune D311?

D311 o depune **firma executată silit**, adică debitorul al cărui cod de TVA a fost anulat din oficiu. Normele separă însă declararea de plată: firma declară taxa, dar **TVA se plătește de organul de executare silită sau de cumpărător**, nu din contul firmei.

Confuzia apare des: firma executată nu mai încasează banii și crede că nu mai are obligații, iar executorul virează TVA fără să se ocupe de declarațiile debitorului.

## Temeiul legal

::: ghid-temei
„Persoanele impozabile care se află în situațiile prevăzute la art. 11 alin. (6) și (8) din Codul fiscal, care efectuează livrări de bunuri prin organele de executare silită, depun declarația prevăzută la art. 324 alin. (10) din Codul fiscal, dar plata taxei se efectuează de organul de executare silită sau, după caz, de cumpărător, conform prevederilor pct. 96 ."
— HG 1/2016 (Normele metodologice ale Codului fiscal), titlul VII, pct. 104 alin. (2) (sursă: [HG nr. 1/2016 (Normele metodologice ale Codului fiscal)](https://legislatie.just.ro/Public/DetaliiDocument/174822))

„În cazul în care la data livrării debitorul executat silit nu este înregistrat în scopuri de TVA conform art. 316 din Codul fiscal ca urmare a anulării codului său de înregistrare în scopuri de TVA în condițiile prevăzute la art. 316 alin. (11) lit. a)-e) și h) din Codul fiscal, organul de executare silită are obligația să emită factura cu TVA dacă livrarea bunurilor ar fi fost taxabilă în situația în care respectivul debitor executat silit ar fi fost înregistrat în scopuri de TVA conform art. 316 din Codul fiscal."
— HG 1/2016, titlul VII, pct. 96 alin. (5) (sursă: [HG nr. 1/2016 (Normele metodologice ale Codului fiscal)](https://legislatie.just.ro/Public/DetaliiDocument/174822))
:::

::: ghid-temei
„până la data de 25 inclusiv a lunii următoare celei în care a intervenit exigibilitatea taxei pentru livrările de bunuri efectuate prin organele de executare silită"
— OPANAF nr. 188/2018, anexa nr. 2 (instrucțiunile de completare a D311) (sursă: [OPANAF nr. 188/2018 pentru aprobarea formularului 311](https://legislatie.just.ro/Public/DetaliiDocument/197537))
:::

Cum se împart obligațiile:

- **Firma executată depune D311.** Obligația vizează persoanele cu codul anulat din oficiu în temeiul art. 316 alin. (11) lit. a)-e) sau h) din Codul fiscal (Legea 227/2015), aflate în situațiile de la art. 11 alin. (6) și (8).
- **Executorul emite factura cu TVA.** O emite pe numele și în contul debitorului, cu mențiunea că facturarea este realizată de organul de executare silită (pct. 96 alin. (5)). TVA apare pe factură dacă livrarea ar fi fost taxabilă în cazul unui debitor înregistrat.
- **Executorul virează taxa.** Dacă încasează prețul cu tot cu TVA, o virează la buget în 5 zile lucrătoare de la adjudecare (pct. 96 alin. (6)). Dacă taxa o plătește direct cumpărătorul, executorului nu-i mai revin obligații de plată (pct. 96 alin. (7)).
- **Unde se trec sumele în D311.** Secțiunea IV.A, rândul 1, conține expres baza și TVA „aferentă tuturor livrărilor de bunuri efectuate prin organele de executare silită, după anularea, din oficiu, a înregistrării în scopuri de TVA".
- **Termen:** 25 a lunii următoare celei în care a intervenit exigibilitatea.

Debitorul înregistrează factura transmisă de executor în evidența proprie (pct. 96 alin. (9)). Dacă își recapătă ulterior codul, factura și documentul de plată a taxei se înscriu în primul decont depus ca persoană înregistrată (pct. 96 alin. (6) și (9)).

::: ghid-exemplu
SC Exemplu SRL are codul de TVA anulat din oficiu din martie 2026. Pe 14 mai 2026, executorul vinde la licitație un utilaj cu 80.000 lei plus TVA. Factura emisă de executor în numele firmei:

- baza: 80.000 lei;
- TVA la cota standard de 21% (art. 291 alin. (1) din Codul fiscal): 80.000 × 21% = 16.800 lei;
- total încasat de la adjudecatar: 96.800 lei.

Executorul virează cei 16.800 lei la buget în 5 zile lucrătoare de la adjudecare. SC Exemplu SRL depune D311 pentru mai 2026, până pe 25 iunie 2026, cu 80.000 lei la bază și 16.800 lei TVA în secțiunea IV.A, rândul 1. Firma nu plătește încă o dată taxa.
:::

## Ce se greșește în practică

- Se crede că, după ce executorul a virat TVA, D311 nu mai e necesar. Normele cer declarația de la firmă chiar dacă plata o face altcineva.
- Firma plătește TVA a doua oară, fiindcă nu urmărește documentul de plată al executorului.
- Factura executorului nu se înregistrează în evidența debitorului, iar vânzarea lipsește din contabilitate.
- D311 se depune pe luna adjudecării, fără să se verifice luna exigibilității taxei.
- Se aplică aceeași regulă la codul anulat la cerere (lit. g). Pct. 104 alin. (2) privește doar situațiile de la art. 11 alin. (6) și (8).

## Ce face iConta.eu

În iConta.eu, D311 se generează din formularul „Situația fiscală după anularea codului de TVA". Contabilul completează data anulării, motivul (din oficiu sau la cerere) și bazele și TVA pe situații. Livrarea prin executare silită se trece la „Livrări de bunuri / prestări de servicii". Aplicația calculează totalul de control, refuză declarația fără sume și validează XML-ul pe validatorul oficial ANAF. Aplicația nu preia automat factura emisă de executor și nu urmărește dacă executorul a virat taxa. Contabilul verifică aceste documente, iar depunerea în SPV o face tot el.

[iConta.eu](/)
