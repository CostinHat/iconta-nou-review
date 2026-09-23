---
title: Cum verific D300 înainte de depunere?
description: Un verde nu e mereu garanție — dacă lipsesc simetric facturi din declarație și din contabilitate, verificarea le poate rata pe amândouă. Un checklist pe cele cinci conturi, înainte de a depune D300.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum verific D300 înainte de depunere?

Înainte de a depune D300, cea mai sigură verificare e compararea ei directă cu balanța contabilă, pe conturile de TVA — nu doar o recitire a declarației în sine. Pașii de mai jos urmează exact logica folosită de verificarea automată.

## Temeiul legal

::: ghid-temei
Art. 281 din Codul fiscal (Legea 227/2015) — "Faptul generator pentru livrări de bunuri și prestări de servicii" — stabilește momentul de la care se naște obligația de TVA. D300 se calculează pe facturile lunii (fapt generator); balanța pe înregistrările contabile efectiv făcute. O diferență între cele două, la data depunerii, poate semnala fie o eroare, fie doar o evidență rămasă în urmă. Titlul și numărul articolului sunt confirmate în sursele legale folosite de aplicație; textul integral nu e citat literal aici.
:::

## Checklist, pe cele cinci conturi

1. **4427** (credit) vs rândul TOTAL TAXĂ COLECTATĂ (R17_2).
2. **4426** (debit) vs rândul TOTAL TAXĂ DEDUCTIBILĂ (R27_2) — nu rândul de ajustări/pro-rata.
3. **4423** (credit) vs Sold TVA de plată la sfârșitul perioadei (R41_2) — relevant doar dacă unul din cele două e nenul.
4. **4424** (debit) vs Soldul sumei negative de TVA de recuperat (R42_2) — la fel, relevant doar dacă unul e nenul.
5. **4428** (net, TVA neexigibilă) — verificare informativă, nu obligatorie; nu se așteaptă potrivire exactă, doar plauzibilitate.

Pentru fiecare, verifică mai întâi dacă toate notele contabile relevante sunt **validate** — o notă lăsată în ciornă nu contează ca evidență și poate produce o diferență falsă.

## Ce înseamnă fiecare stare

- **verde** — sumele coincid (în limita a 1 leu, diferența de rotunjire dintre D300 și contabilitate).
- **roșu** — diferență reală, cu cifrele afișate.
- **gri** — nu s-a putut verifica (de regulă lipsesc date); tratată separat, nu ca un verde tacit.

**Atenție la un verde fals-pozitiv**: dacă există facturi neînregistrate care lipsesc simetric — atât din rulajul contabil, cât și din D300 (de exemplu neregenerat) — comparația poate ieși „verde" fără să însemne că totul e corect; coincidența, în acest caz, nu spune nimic despre facturile lipsă. Situația e degradată de sistem la gri tocmai pentru a nu da o asigurare falsă, dar merită oricum o verificare manuală suplimentară dacă suspectezi facturi neînregistrate.

## Ce se greșește în practică

- Se depune D300 fără să se compare mai întâi cu balanța, bazându-se doar pe generarea automată a declarației.
- Se ignoră notele lăsate în ciornă, considerând că, odată introduse în jurnal, contează deja ca evidență.
- Se tratează 4428 ca pe celelalte patru conturi, așteptând o potrivire exactă — e doar informativ.

## Ce face iConta.eu

Aplicația rulează automat comparația de mai sus înainte de generarea finală a D300, pe cele cinci conturi, folosind doar notele validate și o toleranță de 1 leu, și afișează starea verde/roșu/gri pentru fiecare. Când există risc de facturi neînregistrate simetric absente din ambii termeni, comparația e degradată explicit la gri, în loc să afișeze un verde care ar putea induce în eroare.

[iConta.eu](/)
