---
title: Cum se înregistrează un avans plătit în numerar furnizorului?
description: Un avans plătit în numerar unui furnizor (persoană juridică/PFA) respectă plafonul de 5.000 lei/zi/furnizor, dar nu mai mult de 10.000 lei/zi total, cu interdicție expresă de fragmentare a plăților pentru a evita plafonul.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se înregistrează un avans plătit în numerar furnizorului?

Avansurile în numerar sunt frecvente la furnizorii mici sau la achizițiile urgente, dar Legea 70/2015 impune plafoane stricte pentru plățile cash între entități — plafoane care se aplică inclusiv avansurilor, nu doar facturilor finale.

## Temeiul legal

::: ghid-temei
"(1) Operațiunile de încasări și plăți efectuate de persoane juridice, persoane fizice autorizate, întreprinderi individuale, întreprinderi familiale, liber profesioniști, persoane fizice care desfășoară activități în mod independent, asocieri și alte entități cu sau fără personalitate juridică de la/către oricare dintre aceste categorii de persoane se vor realiza numai prin instrumente de plată fără numerar, definite potrivit legii."

"(1) Prin excepție de la prevederile art. 1 alin. (1) se pot efectua operațiuni de încasări și plăți în numerar, în următoarele condiții: ... c) plăți către persoanele prevăzute la art. 1 alin. (1), în limita unui plafon zilnic de 5.000 lei/persoană, dar nu mai mult de un plafon total de 10.000 lei/zi; ..."

"(3) Sunt interzise plățile fragmentate în numerar către furnizorii de bunuri și servicii pentru facturile a căror valoare este mai mare de 5.000 lei..."

"(2) Prin excepție de la prevederile alin. (1), exigibilitatea taxei intervine: ... b) la data la care se încasează avansul, pentru plățile în avans efectuate înainte de data la care intervine faptul generator. Avansurile reprezintă plata parțială sau integrală a contravalorii bunurilor și serviciilor, efectuată înainte de data livrării ori prestării acestora;"
:::

## Plafonul aplicabil și fragmentarea interzisă

Regula generală (art. 1 alin. 1) impune plăți fără numerar între entități economice. Excepția care permite numerar (art. 3 alin. 1 lit. c) fixează două limite simultane: **5.000 lei/zi către același furnizor** și **10.000 lei/zi în total** (indiferent de câți furnizori sunt plătiți cash în ziua respectivă). Legea interzice explicit fragmentarea — plata unui avans mare "spartă" în tranșe zilnice succesive, exact ca să se rămână sub plafon, e o încălcare directă a art. 3 alin. (3).

Din punct de vedere fiscal, avansul plătit în numerar generează aceeași exigibilitate TVA ca orice alt avans (art. 282 alin. 2 lit. b) — modalitatea de plată (cash, transfer bancar) nu schimbă regimul TVA, ci doar impune respectarea plafonului de numerar.

::: ghid-exemplu
O firmă vrea să plătească un avans de 8.000 lei cash unui furnizor. Plafonul e 5.000 lei/zi/furnizor — deci suma nu poate fi plătită integral cash într-o singură zi către acel furnizor. Plata în două zile consecutive (4.000 + 4.000 lei), doar ca să se evite plafonul, este considerată fragmentare interzisă. Soluția legală e plata parțial cash (până la 5.000 lei) și restul prin instrument fără numerar (transfer bancar).
:::

## Ce se greșește în practică

- Se plătește un avans mare integral cash, depășind plafonul de 5.000 lei/zi/furnizor, considerând greșit că plafonul se aplică doar facturilor finale, nu și avansurilor.
- Se fragmentează plata unui avans mare pe mai multe zile consecutive exact pentru a rămâne sub plafon — interzis explicit de art. 3 alin. (3).
- Se ignoră plafonul total de 10.000 lei/zi când se plătesc cash mai mulți furnizori diferiți în aceeași zi, deși fiecare plată individuală respectă limita de 5.000 lei/furnizor.
- Se presupune că un avans plătit cash nu are niciun efect asupra exigibilității TVA până la factura finală — greșit, exigibilitatea intervine la data plății avansului, indiferent de modalitatea de plată.

## Ce face iConta.eu

Înregistrarea contabilă a avansului plătit cash folosește aceeași funcție ca orice alt avans plătit: `nota_avans_platit(suma_fara_tva, cota, destinatie="stocuri")`, generând `409x + 4426 = 401`. Modulul nu face nicio distincție internă între plata prin numerar sau prin bancă — contrapartida contabilă (401) e aceeași, diferența de instrument de plată se reflectă abia la decontarea ulterioară a contului 401.

Important de reținut: `core/avansuri.py` **nu verifică plafonul de numerar** din Legea 70/2015. Motorul nu are nicio validare a limitei de 5.000 lei/zi/furnizor sau a plafonului total de 10.000 lei/zi — aplicația nu vă va avertiza automat dacă introduceți un avans mare plătit cash care depășește plafonul legal. Respectarea plafonului și evitarea fragmentării rămân integral responsabilitatea profesională a contabilului la momentul înregistrării plății.

[iConta.eu](/)
