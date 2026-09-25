---
title: "Cum se tratează veniturile din chirii la micro vs profit"
description: "Diferența dintre tratamentul veniturilor din chirii obținute de o firmă plătitoare de impozit pe veniturile microîntreprinderilor și una plătitoare de impozit pe profit."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se tratează veniturile din chirii la micro vs profit

Când o firmă (nu o persoană fizică) încasează chirii — de exemplu pentru un spațiu deținut și închiriat unor terți — modul în care venitul respectiv e impozitat depinde exclusiv de regimul fiscal al firmei, nu de natura chiriei în sine. Nu există o regulă specială pentru veniturile din chirii la microîntreprinderi: ele intră în baza de impozitare la fel ca orice alt venit.

## Temeiul legal

::: ghid-temei
„Baza impozabilă
Baza impozabilă a impozitului pe veniturile microîntreprinderilor o constituie veniturile din orice sursă, din care se scad: [...]"
— Legea nr. 227/2015 privind Codul fiscal, art. 53 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- **La microîntreprindere**: venitul din chirii intră, ca orice alt venit din exploatare, în baza impozabilă de la art. 53 — se impozitează la cota de micro (1% sau 3%, în funcție de îndeplinirea condițiilor legale) aplicată la valoarea brută a chiriei încasate/de încasat, fără a scădea cheltuielile aferente (întreținere, amortizare, reparații) — regimul micro nu permite deducerea cheltuielilor, spre deosebire de impozitul pe profit.
- **La impozit pe profit**: venitul din chirii intră în veniturile totale, dar impozitul de 16% se aplică asupra profitului — adică venitul din chirii minus cheltuielile deductibile aferente (amortizarea imobilului, întreținere, asigurări, utilități nerefacturate etc.).
- Firma trebuie să verifice și condițiile de încadrare ca microîntreprindere de la art. 47 (plafonul de venituri, existența a cel puțin un salariat, structura acționariatului etc.) — veniturile din chirii se cumulează cu restul veniturilor firmei la verificarea acestor praguri, la fel ca orice altă sursă.
- Dacă activitatea de închiriere e singura sau principala activitate a firmei, alegerea între micro și profit devine, practic, o decizie de optimizare: la marje mari (cheltuieli reduse față de chiria încasată), micro poate fi mai avantajos; la marje mici sau cheltuieli mari (credit ipotecar, renovări majore), impozitul pe profit poate ieși mai mic, pentru că se calculează pe profitul net, nu pe venitul brut.

## Ce se greșește în practică

- Se presupune că veniturile din chirii au un regim special la microîntreprinderi (cotă diferită sau bază de calcul diferită) — nu există așa ceva; se aplică regula generală de la art. 53.
- Se scad cheltuielile cu întreținerea sau amortizarea imobilului din baza de impozitare a microîntreprinderii, deși regimul micro nu permite deduceri de acest fel.
- Se confundă veniturile din chirii obținute de o firmă (venit din exploatare, impozitat conform titlului III sau II din Codul fiscal) cu veniturile din cedarea folosinței bunurilor obținute de o persoană fizică din patrimoniul personal (impozitate separat, conform Titlului IV) — regimurile și bazele legale sunt complet diferite.
- Se ignoră faptul că veniturile din chirii se cumulează cu restul veniturilor firmei la verificarea plafonului de încadrare ca microîntreprindere.

## Ce face iConta.eu

iConta.eu are un motor dedicat pentru chirii și comodat (`comodat_chirii`), care generează notele contabile corecte pentru chiria plătită (cont 612) și chiria încasată ca activitate (cont 4111 = 706 + 4427, cu TVA), inclusiv pentru refacturarea utilităților către chiriaș. Aplicația **nu decide automat** dacă un venit din chirii e mai avantajos impozitat la regimul micro sau la profit — acesta rămâne un calcul de optimizare fiscală pe care contabilul îl face separat, folosind cifrele de venituri și cheltuieli evidențiate în aplicație.

[iConta.eu](/)
