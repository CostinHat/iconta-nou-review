---
title: "Cum se determină veniturile totale pentru IMCA când firma acordă reduceri comerciale după facturare?"
description: "Veniturile totale (VT) din formula IMCA sunt veniturile înregistrate contabil din care se scad reducerile comerciale acordate ulterior facturării; abia apoi se scad Vs, I și A și se aplică cota."
published: 2026-09-29
modified: 2026-09-29
poarta: v1
---

# Cum se determină veniturile totale pentru IMCA când firma acordă reduceri comerciale după facturare?

La impozitul minim pe cifra de afaceri (IMCA), indicatorul „venituri totale" (VT) nu este suma brută a veniturilor facturate. Din totalul veniturilor înregistrate după reglementările contabile se scad reducerile comerciale acordate după facturare, cum sunt rabaturile, remizele și risturnele de final de perioadă. VT este deci un venit net de aceste reduceri.

Diferența contează la firmele mari, cu politici de bonusare a clienților. Fără scăderea reducerilor, baza IMCA și impozitul minim ies supraevaluate.

## Temeiul legal

::: ghid-temei
„a) indicatorul «venituri totale (VT)» prevăzut la art. 18^1 alin. (3) din Codul fiscal reprezintă totalul veniturilor înregistrate potrivit reglementărilor contabile aplicabile, din care au fost scăzute reducerile comerciale acordate ulterior facturării; în același mod se determină și indicatorul «venituri totale (VT)» prevăzut la art. 18^3 alin. (2) din Codul fiscal;"
— HG 1/2016 (Normele Codului fiscal), Titlul II, pct. 4^1 alin. (1) lit. a) (sursă: [HG nr. 1/2016 (Normele metodologice ale Codului fiscal)](https://legislatie.just.ro/Public/DetaliiDocument/174822))

„Impozitul minim pe cifra de afaceri se determină astfel: IMCA = 1% x (VT – Vs – I – A), unde indicatorii au următoarea semnificație: IMCA - impozit minim pe cifra de afaceri, determinat cumulat de la începutul anului fiscal/anului fiscal modificat până la sfârșitul trimestrului/anului de calcul;"
— Codul fiscal (Legea 227/2015), art. 18^1 alin. (3) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))

„Pentru anul fiscal 2026/anul fiscal modificat care începe în anul 2026, cota de impozit din cadrul formulei prevăzute la alin. (3) este 0,5%."
— Codul fiscal (Legea 227/2015), art. 18^1 alin. (16) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))
:::

Cum se aplică:

- **VT se construiește din contabilitate**: toate veniturile înregistrate cumulat de la începutul anului până la sfârșitul trimestrului sau anului de calcul, minus reducerile comerciale acordate după facturare.
- **Doar reducerile acordate ulterior facturării** se scad separat. Reducerile înscrise direct pe factura inițială diminuează deja venitul înregistrat și nu se mai scad a doua oară.
- **Pașii următori ai formulei** rămân aceiași: din VT se scad veniturile din lista Vs (neimpozabile, stocuri, servicii în curs, producție de imobilizări, subvenții, despăgubiri de la asigurători, accize), apoi I și A.
- **Cota** este 0,5% pentru anul fiscal 2026. Formula de bază din alin. (3) menționează 1%, cota anilor anteriori. Art. 18^1 se aplică până la 31 decembrie 2026 inclusiv, respectiv până la sfârșitul anului fiscal modificat care se încheie în 2027 (alin. (17)).
- **Pragul de aplicare**: IMCA privește doar contribuabilii cu o cifră de afaceri de peste 50.000.000 euro în anul precedent (alin. (1)).
- **Aceeași regulă pentru ICAS**: normele spun expres că VT se determină la fel și pentru impozitul specific pe cifra de afaceri de la art. 18^3.

::: ghid-exemplu
SC Exemplu SA, peste pragul de 50.000.000 euro, are cumulat până la 30 iunie 2026:

- venituri înregistrate: 300.000.000 lei;
- reduceri comerciale acordate ulterior facturării (bonusuri de volum): 6.000.000 lei;
- Vs: 4.000.000 lei; I și A: 0.

VT = 300.000.000 − 6.000.000 = 294.000.000 lei.
IMCA cumulat = 0,5% × (294.000.000 − 4.000.000) = 0,5% × 290.000.000 = 1.450.000 lei.

Dacă reducerile nu s-ar scădea, IMCA ar ieși 0,5% × 296.000.000 = 1.480.000 lei, cu 30.000 lei mai mult.
:::

## Ce se greșește în practică

- VT se ia din veniturile facturate brut, fără scăderea bonusurilor și risturnelor acordate ulterior.
- Aceeași reducere se scade de două ori: o dată pe factura inițială și încă o dată ca reducere ulterioară.
- Se aplică în 2026 cota de 1% din formula de bază, deși alin. (16) o reduce la 0,5%.
- VT se calculează doar pe trimestrul curent, deși indicatorul se determină cumulat de la începutul anului.

## Ce face iConta.eu

iConta.eu calculează IMCA în declarația D101, validată pe validatorul oficial ANAF. Cota e aleasă după anul fiscal (0,5% pentru 2026) și impozitul pe profit se compară cu impozitul minim. Indicatorii VT, Vs, I și A se introduc de contabil. Aplicația nu îi derivă din balanță, deci și scăderea reducerilor comerciale ulterioare din VT o face contabilul. Dacă cifra de afaceri a anului precedent, introdusă de contabil, depășește pragul, aplicația nu generează D101 fără valoarea IMCA.

[iConta.eu](/)
