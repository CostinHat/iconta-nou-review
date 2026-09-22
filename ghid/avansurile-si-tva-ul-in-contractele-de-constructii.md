---
title: Avansurile și TVA-ul în contractele de construcții?
description: TVA-ul avansurilor din construcții devine exigibilă la fiecare încasare parțială, iar la o schimbare de cotă între avans și situația finală, regularizarea se face după cota valabilă la data livrării/recepției, nu la data avansului sau a regularizării.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Avansurile și TVA-ul în contractele de construcții?

Contractele de construcții implică, de regulă, mai multe plăți eșalonate — avansuri succesive, situații de plată intermediare — ceea ce ridică întrebări specifice despre momentul exigibilității TVA și despre ce cotă se aplică dacă legislația se schimbă pe parcursul lucrării.

## Temeiul legal

::: ghid-temei
"(2) Prin excepție de la prevederile alin. (1), exigibilitatea taxei intervine: ... b) la data la care se încasează avansul, pentru plățile în avans efectuate înainte de data la care intervine faptul generator. Avansurile reprezintă plata parțială sau integrală a contravalorii bunurilor și serviciilor, efectuată înainte de data livrării ori prestării acestora;"

"(4) Cota aplicabilă este cea în vigoare la data la care intervine faptul generator, cu excepția cazurilor prevăzute la art. 282 alin. (2), pentru care se aplică cota în vigoare la data exigibilității taxei."

"(6) În cazul schimbării cotei se va proceda la regularizare pentru a se aplica cota în vigoare la data livrării de bunuri sau prestării de servicii, pentru cazurile prevăzute la art. 282 alin. (2), precum și în situația prevăzută la alin. (5)."
:::

## Cota la avans versus cota la regularizare

Fiecare avans (sau situație de plată intermediară asimilată avansului) generează exigibilitate TVA imediată, la propria cotă în vigoare la data încasării/plății — art. 291 alin. (4) trimite explicit la excepția de la art. 282 alin. (2). Dacă între momentul avansului și recepția finală a lucrării se schimbă cota de TVA (situație care s-a mai întâmplat în legislația românească), art. 291 alin. (6) impune o **regularizare**: la finalizarea lucrării, întreaga operațiune trebuie adusă la cota în vigoare la data livrării — adică la data recepției/finalizării, nu la data fiecărui avans în parte și nu la data la care se face efectiv regularizarea contabilă.

::: ghid-exemplu
O firmă de construcții încasează un avans de 100.000 lei în decembrie, la cota de 19%, apoi cota crește la 21% din ianuarie. Lucrarea se recepționează în februarie, la valoare totală de 300.000 lei. La regularizare, întreaga bază de 300.000 lei trebuie taxată la cota de 21% (cea de la data recepției), inclusiv partea deja facturată ca avans la 19% — diferența de cotă pentru cei 100.000 lei se regularizează separat.
:::

## Ce se greșește în practică

- Se aplică la factura finală aceeași cotă folosită la avans, fără verificarea cotei în vigoare la data efectivă a livrării/recepției — greșit dacă între timp s-a schimbat cota.
- Se cumulează greșit sumele avansurilor succesive la momentul regularizării — pentru contracte cu mai multe situații de plată, suma corectă de regularizat e cea cumulată a tuturor avansurilor aferente facturii finale, calcul care nu se face automat de niciun sistem.
- Se confundă situația de plată intermediară (care poate fi, fiscal, un avans în sensul art. 282 alin. 2 lit. b) cu o simplă factură parțială emisă fără efect de exigibilitate distinctă.
- Se ignoră regularizarea de cotă atunci când între data avansului și data livrării/recepției a intervenit efectiv o schimbare de cotă — art. 291 alin. (6) o impune expres în acest caz, indiferent dacă schimbarea a fost sau nu vizibilă/observată de contabil la momentul respectiv.

## Ce face iConta.eu

Orchestrarea din `core/uc_tenants.py::nota_avans` (liniile 3466-3522) cere explicit data livrării (`data_livrare`) pentru orice operație al cărei tip începe cu `"regularizare"`, exact conform cerinței art. 291 alin. (6): cota de regularizare se calculează prin `_common.cota_ceruta({**corp, "data": _data_cota})`, adică pe data livrării, nu pe data la care se operează efectiv regularizarea. Descrierea notei contabile generate poartă explicit mențiunea "- art. 282(2)b CF".

O limitare importantă pentru contractele de construcții cu plăți eșalonate: modulul `avansuri.py` **nu agregă** mai multe avansuri pe aceeași comandă/factură finală — fiecare apel produce o notă separată, iar suma corectă pentru regularizare (cumulul tuturor avansurilor/situațiilor de plată anterioare) trebuie calculată și transmisă corect de utilizator sau de stratul care apelează motorul. Dacă suma cumulată e greșită la intrare, motorul nu are context despre facturile anterioare și nu poate detecta eroarea.

[iConta.eu](/)
