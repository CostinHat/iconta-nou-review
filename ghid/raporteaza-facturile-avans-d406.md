---
title: "Cum se raportează facturile de avans în D406?"
description: "Facturile de avans nu au un tip special în SAF-T (D406) — se raportează ca facturi obișnuite, cu tratamentul de TVA specific avansurilor."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se raportează facturile de avans în D406?

Fișierul standard de control fiscal (SAF-T, declarat prin D406) nu are o categorie separată de „factură de avans" — obligația de raportare vine din Codul de procedură fiscală, iar tratamentul specific al avansurilor ține de exigibilitatea TVA, nu de o structură distinctă în fișier. Practic, o factură de avans intră în D406 ca orice altă factură emisă sau primită, cu contabilizarea ei specifică reflectată în jurnalele contabile transmise.

## Temeiul legal

::: ghid-temei
„Contribuabilul/Plătitorul are obligația de a depune la organul fiscal central o declarație cuprinzând informații din evidența contabilă și fiscală, denumită în continuare fișierul standard de control fiscal."
— Legea 207/2015 (Codul de procedură fiscală), art. 59^1 alin. (1) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

::: ghid-temei
„Prin excepție de la prevederile alin. (1), exigibilitatea taxei intervine: [...] b) la data la care se încasează avansul, pentru plățile în avans efectuate înainte de data la care intervine faptul generator. Avansurile reprezintă plata parțială sau integrală a contravalorii bunurilor și serviciilor, efectuată înainte de data livrării ori prestării acestora."
— Codul fiscal (Legea 227/2015), art. 282 alin. (2) lit. b) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Obligația de a depune D406/SAF-T e generală (art. 59^1 din Codul de procedură fiscală) și nu distinge, la nivel de lege, între tipurile de facturi raportate — orice factură emisă sau primită intră în evidența contabilă și fiscală ce trebuie declarată.
- Ce e specific facturii de avans e momentul exigibilității TVA: taxa devine exigibilă **la încasarea avansului**, nu la livrarea finală (art. 282 alin. 2 lit. b Cod fiscal), spre deosebire de regula generală de la art. 282 alin. (1), unde exigibilitatea urmează faptul generator.
- Din punct de vedere contabil, factura de avans se înregistrează pe conturi distincte de avans (de exemplu 409x pentru avansuri plătite furnizorilor, respectiv 419 pentru avansuri încasate de la clienți), iar la factura finală se face regularizarea — inversarea avansului și recunoașterea integrală a operațiunii.
- Corpusul de legislație verificat nu conține un standard tehnic separat, la nivel de câmp XML din schema SAF-T, dedicat exclusiv facturilor de avans; raportarea lor urmează structura generală de „InvoiceNo" din fișier, la fel ca orice altă factură.

## Ce se greșește în practică

- Se caută un „cod special" pentru avansuri în structura D406, deși schema SAF-T nu prevede un tip distinct de document pentru facturile de avans — ele apar ca facturi obișnuite, în secțiunea de facturi/tranzacții.
- Se raportează avansul la data facturii finale, nu la data încasării — exigibilitatea TVA se stabilește la încasare (art. 282 alin. 2 lit. b), iar decalajul poate produce diferențe între evidența declarată prin D300/D406 și realitatea încasărilor.
- Se omite regularizarea avansului la factura finală (inversarea conturilor de avans), ceea ce duce la duplicarea valorii operațiunii în evidența raportată.
- Se presupune că avansurile plătite și cele încasate au aceeași tratare contabilă — de fapt folosesc conturi și fluxuri diferite (409x pentru avans plătit furnizorului, 419 pentru avans încasat de la client).

## Ce face iConta.eu

Aplicația are un modul dedicat contabilizării avansurilor (facturi de avans plătite și încasate, cu notele contabile aferente pe conturile 409x/419/4426/4427 și regularizarea la factura finală, motivate direct în cod de OMFP 1802/2014 și art. 282 alin. (2) lit. b) din Codul fiscal). Nu am găsit însă, la nivelul modulului de generare D406, vreo secțiune sau cod special dedicat exclusiv facturilor de avans — acestea sunt preluate în fișierul SAF-T ca facturi obișnuite, din aceeași sursă de date ca restul facturilor, tratamentul lor specific fiind vizibil la nivel de contabilitate, nu de structură separată în declarație.

[iConta.eu](/)
