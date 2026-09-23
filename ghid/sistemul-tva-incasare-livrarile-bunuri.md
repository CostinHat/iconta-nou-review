---
title: Sistemul TVA la încasare la livrările de bunuri cu plata în rate
description: La o livrare cu plata eșalonată, TVA la încasare devine exigibilă separat pentru fiecare rată încasată, prin sută mărită — dar cota aplicabilă rămâne cea fixată o singură dată, la faptul generator sau la factură/avans, nu se recalculează la fiecare tranșă.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Sistemul TVA la încasare la livrările de bunuri cu plata în rate

La o vânzare cu plata în rate, firma aflată în sistemul TVA la încasare nu așteaptă ultima rată ca să datoreze TVA, și nici nu tratează fiecare rată ca pe o mini-factură cu cotă proprie. Legea separă clar două întrebări diferite — când devine exigibilă taxa și ce cotă i se aplică — iar cele două răspund la reguli distincte.

## Temeiul legal

::: ghid-temei
**Art. 282 alin. (3) din Codul fiscal (Legea 227/2015)**, modificat prin art. 6 pct. 38 OUG 8/2026 (MO 147/25.02.2026): *„Prin excepție de la prevederile alin. (1) și alin. (2) lit. a), exigibilitatea taxei intervine la data încasării contravalorii integrale sau parțiale a livrării de bunuri ori a prestării de servicii, în cazul persoanelor impozabile care optează în acest sens... Plafonul pentru aplicarea sistemului TVA la încasare este de: a) 5.000.000 lei, în perioada 1 martie-31 decembrie 2026; b) 5.500.000 lei, începând cu data de 1 ianuarie 2027."*

**Art. 282 alin. (8)**: *„fiecare încasare totală sau parțială se consideră că include și taxa aferentă"*.

**Art. 291 alin. (5)**: *„În cazul operațiunilor supuse sistemului TVA la încasare, cota aplicabilă este cea în vigoare la data la care intervine faptul generator, cu excepția situațiilor în care este emisă o factură sau este încasat un avans, înainte de data livrării/prestării, pentru care se aplică cota în vigoare la data la care a fost emisă factura ori la data la care a fost încasat avansul."*
:::

## Ce înseamnă practic pentru o plată în rate

Alin. (3) vorbește explicit despre încasarea contravalorii „integrale **sau parțiale**" — o rată e, din perspectiva TVA, o încasare parțială ca oricare alta. Fiecare rată încasată declanșează deci propriul moment de exigibilitate, separat de celelalte.

Alin. (8) completează mecanismul de calcul: suma încasată (rata) se consideră că include deja TVA — extragerea se face prin sută mărită (`suma încasată × cotă / (100 + cotă)`), nu prin aplicarea cotei peste sumă. Fiecare rată își are propriul calcul, iar rezultatele se agregă pe cotă.

Ce **nu** se schimbă de la o rată la alta e cota aplicabilă. Art. 291 alin. (5) fixează cota o singură dată — la data faptului generator (livrarea bunului), sau la data facturii/avansului dacă acestea au fost emise/încasate înainte de livrare. Indiferent câte rate urmează și pe ce perioadă se întind, toate se raportează la aceeași cotă stabilită la acel moment inițial; cota nu „urmărește" data fiecărei rate.

## Ce se greșește în practică

- **Se aplică pe fiecare rată cota valabilă în ziua încasării ei**, ca și cum fiecare tranșă ar fi o operațiune nouă. Art. 291 alin. (5) fixează cota o singură dată, la faptul generator (sau la factură/avans), nu la fiecare încasare.
- **Se calculează TVA prin aplicarea cotei peste suma ratei**, în loc de sută mărită. Art. 282 alin. (8) e explicit: suma încasată deja include TVA.
- **Se amână întreaga taxare până la ultima rată**, ignorând că fiecare încasare parțială e ea însăși un moment de exigibilitate conform alin. (3).

## Ce face iConta.eu

Motorul de calcul (`core/tva_incasare.py`) extrage TVA exigibil din fiecare sumă încasată prin sută mărită (`suma × cotă/(100+cotă)`) și agregă rezultatele pe cotă pentru mai multe încasări/alocări (`tva_exigibil_alocari`). Alegerea între cota de la faptul generator și cota de la factură/avans (ramura din art. 291 alin. (5)) **nu e dedusă automat** — contabilul o selectează manual, pentru fiecare operațiune, în ecranul dedicat.

[iConta.eu](/)
