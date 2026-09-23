---
title: "Cum se taxează voucherele de vacanță acordate de firmă?"
description: Voucherele de vacanță se taxează cu CASS 10% și impozit 10%, fără CAS și fără CAM, indiferent dacă suma acordată se încadrează sau nu sub plafonul anual legal — plafonul nu e o scutire.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se taxează voucherele de vacanță acordate de firmă?

Voucherele de vacanță acordate salariaților sunt un beneficiu impozabil, nu unul scutit — inclusiv atunci când suma acordată se încadrează sub plafonul legal anual. Confuzia vine tocmai din faptul că acest plafon are alt rol decât cel de scutire fiscală.

## Temeiul legal

::: ghid-temei
Codul fiscal, art. 157 alin. (2): „Nu se cuprind în baza lunară de calcul al contribuției de asigurări sociale de sănătate sumele prevăzute la art. 76 alin. (4) lit. d), art. 141 lit. d) și art. 142, cu excepția sumelor reprezentând valoarea nominală a biletelor de valoare sub forma tichetelor de masă și a voucherelor de vacanță, acordate potrivit legii."

*(alineat modificat de Legea 296/2023, art. III cap. II pct. 26, de la 01.01.2024)*
:::

Concret, voucherele de vacanță sunt scutite de CAS (art. 142 lit. r) din Codul fiscal), dar **nu** și de CASS — art. 157 alin. (2) retrage explicit excepția de CASS tocmai pentru tichetele de masă și voucherele de vacanță (nu și pentru tichetele de creșă sau culturale, care rămân în afara CASS). Peste CASS, se aplică și impozitul pe venit de 10% (art. 78 alin. (2) lit. a) din Codul fiscal), calculat pe baza rămasă după scăderea CASS — nu pe valoarea nominală brută.

Nivelul maxim al voucherelor ce pot fi acordate într-un an fiscal e stabilit separat, la 6 salarii de bază minime brute pe țară (OUG 8/2009, art. 1 alin. (4)). Pentru 2026, din cauza majorării salariului minim la 1 iulie, plafonul anual are două praguri: **24.300 lei** până la 30 iunie 2026 (6 × 4.050 lei) și **25.950 lei** de la 1 iulie 2026 (6 × 4.325 lei). Acest plafon limitează **cât** se poate acorda legal sub formă de vouchere, nu determină o parte scutită de taxare — suma acordată sub plafon se taxează la fel ca suma care ar depăși plafonul (care, în plus, intră ca venit salarial obișnuit pentru excedent).

## Ce se greșește în practică

- Se presupune că voucherele de vacanță sunt neimpozabile, ca tichetele cadou sub 300 de lei — de fapt sunt taxate integral cu CASS 10% + impozit 10%, indiferent de sumă.
- Se calculează impozitul de 10% pe valoarea nominală brută a voucherului, în loc de baza rămasă după scăderea CASS — diferența nu e o rotunjire, e o eroare de formulă care umflă reținerea reală.
- Se tratează plafonul anual (6 salarii minime) ca fiind fix pe tot anul 2026, fără să se țină cont că salariul minim crește de la 1 iulie 2026, ceea ce ridică plafonul de la 24.300 la 25.950 lei.

## Ce face iConta.eu

Motorul de salarizare (`core/salarizare.py`) calculează CASS 10% pe valoarea nominală integrală a voucherelor de vacanță (cumulată cu tichetele de masă, dacă există), apoi impozitul 10% pe baza rămasă după scăderea acestei CASS — fără CAS și fără CAM pe vouchere, conform mecanismului confirmat în cod. Plafonul anual de 6 salarii minime brute se citește dinamic din salariul minim valabil la data fiecărei perioade, astfel încât cele două praguri din 2026 (24.300 lei / 25.950 lei) sunt aplicate automat, fără intervenție manuală. Excedentul peste plafon este calculat incremental, pe cumulat anual, și intră automat ca venit salarial obișnuit în stat de plată.

[iConta.eu](/)
