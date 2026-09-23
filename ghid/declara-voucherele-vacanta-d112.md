---
title: "Cum se declară voucherele de vacanță în D112?"
description: Voucherele de vacanță se declară în D112 la rândul dedicat E3_75, intră integral în baza CASS, dar niciodată în baza CAS, iar excedentul peste plafonul anual se adaugă la venitul salarial obișnuit.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se declară voucherele de vacanță în D112?

Declararea corectă în D112 depinde de trei mecanisme separate care se aplică simultan aceleiași sume: rândul informativ dedicat, includerea în baza CASS și, dacă e cazul, includerea excedentului peste plafon în venitul brut declarat.

## Temeiul legal

::: ghid-temei
Codul fiscal, art. 157 alin. (1) lit. ț): „valoarea nominală a tichetelor cadou, a tichetelor de masă și a voucherelor de vacanță, acordate de angajatori, potrivit legii, prevăzute la art. 76 alin. (3) lit. h)"

*(literă modificată de Legea 296/2023, art. III cap. II pct. 25, de la 01.01.2024)*
:::

Valoarea nominală a voucherelor de vacanță se raportează în D112 la rândul **E3_75**, distinct de tichetele de masă (E3_10), tichetele de creșă (E3_72), tichetele culturale (E3_74) și cadourile (E3_73 — doar partea taxabilă). Aceeași valoare intră și în **baza de calcul a CASS**, alături de tichetele de masă — art. 157 alin. (2) din Codul fiscal retrage explicit excepția de CASS pentru aceste două categorii, spre deosebire de tichetele de creșă și culturale, care rămân în afara bazei CASS. Baza de calcul a **CAS**, în schimb, nu include niciodată voucherele de vacanță (nici tichetele de masă) — sunt scutite de CAS potrivit art. 142 lit. r) din Codul fiscal.

Dacă suma acordată în cursul anului depășește plafonul legal de 6 salarii minime brute (24.300 lei până la 30 iunie 2026, 25.950 lei de la 1 iulie 2026), excedentul nu mai urmează regimul de voucher, ci intră direct în **venitul brut** declarat în D112, ca venit salarial obișnuit — supus, deci, regimului complet (inclusiv CAS/CAM), nu doar CASS și impozit.

## Ce se greșește în practică

- Se raportează valoarea voucherelor de vacanță la același rând cu tichetele de masă, în loc de rândul dedicat E3_75, ceea ce denaturează structura informativă a declarației.
- Se omite includerea voucherelor de vacanță în baza de calcul a CASS, pe motiv că sunt scutite de contribuții sociale în general — scutirea privește doar CAS, nu și CASS.
- Se lasă excedentul peste plafonul anual în afara venitului brut declarat, tratându-l tot ca voucher taxat doar cu CASS+impozit, în loc să fie inclus ca venit salarial obișnuit.

## Ce face iConta.eu

Generarea D112 (`core/d112.py`) populează automat rândul E3_75 cu valoarea nominală a voucherelor de vacanță din luna respectivă, distinct de tichetele de masă și de cadouri, și include această sumă în baza de calcul a CASS împreună cu tichetele de masă — fără să o adauge la baza CAS. Excedentul peste plafonul anual, calculat incremental pe cumulat, este preluat automat în venitul brut declarat, fără a mai fi tratat ca voucher scutit de CAS/CAM. Pentru fluturaș și D112 pe tichete de masă, generarea depinde de confirmarea prealabilă a pontajului lunii respective — dacă pontajul nu e confirmat, aplicația respinge explicit generarea, ca să nu se declare pe date neconfirmate.

[iConta.eu](/)
