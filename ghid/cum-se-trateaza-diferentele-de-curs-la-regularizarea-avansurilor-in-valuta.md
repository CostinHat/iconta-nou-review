---
title: Cum se tratează diferențele de curs la regularizarea avansurilor în valută?
description: Avansurile în valută (409/419) sunt elemente nemonetare și rămân înregistrate la cursul din ziua plății/încasării, fără reevaluare lunară sau la 31.12; la factura finală doar partea neacoperită de avans se convertește la cursul nou.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se tratează diferențele de curs la regularizarea avansurilor în valută?

Un avans plătit sau încasat în valută ridică o întrebare frecventă: la factura finală, se recalculează tot la cursul zilei sau rămâne o parte din sumă la cursul vechi? Răspunsul ține de natura contabilă a avansului, nu de o alegere discreționară.

## Temeiul legal

::: ghid-temei
"304. ‐ (1) Operațiunile privind încasările şi plățile în valută se înregistrează în contabilitate la cursul de schimb valutar, comunicat de Banca Națională a României, de la data efectuării operațiunii respective. În vederea asigurării unui tratament contabil unitar, prin curs de schimb de la data efectuării operațiunii se înțelege cursul de schimb al pieței valutare, comunicat de Banca Națională a României, din ultima zi bancară anterioară operațiunii, disponibil ca informație la momentul efectuării operațiunii (încasare, plată, emitere de documente)."

"315. ‐ (1) Prin elemente monetare se înțelege disponibilitățile băneşti şi activele/datoriile de primit/de plătit în sume fixe sau determinabile. ... (3) Caracteristica esențială a unui element nemonetar este absența unui drept de a primi (sau a unei obligații de a furniza) un număr fix sau determinabil de unități monetare. Exemplele includ: sumele plătite în avans pentru bunuri şi servicii; imobilizări necorporale; stocuri; imobilizări corporale; şi provizioanele care urmează a fi decontate prin furnizarea unui activ nemonetar."

"316. ‐ (1) La aplicarea pentru prima dată a prezentelor reglementări, sumele reprezentând avansuri acordate pentru imobilizări corporale, respectiv necorporale, se preiau în conturile 4093 «Avansuri acordate pentru imobilizări corporale» şi 4094 «Avansuri acordate pentru imobilizări necorporale»... (2) Începând cu data de 1 ianuarie 2015, sumele înregistrate în conturile menționate la alin. (1), precum şi cele reflectate în conturile 409 «Furnizori ‐ debitori» şi 419 «Clienți ‐ creditori», nu mai fac obiectul evaluării în funcție de cursul valutar, la finele lunii, respectiv la finele exercițiului financiar."

"(2) Dacă elementele folosite pentru stabilirea bazei de impozitare a unei operațiuni, alta decât importul de bunuri, se exprimă în valută, cursul de schimb care se aplică este ultimul curs de schimb comunicat de Banca Națională a României sau ultimul curs de schimb publicat de Banca Centrală Europeană ori cursul de schimb utilizat de banca prin care se efectuează decontările, valabil la data la care intervine exigibilitatea taxei pentru operațiunea în cauză..."
:::

## De ce avansurile nu generează diferențe de curs "clasice"

Diferențele de curs valutar (favorabile sau nefavorabile) apar la elementele **monetare** — creanțe și datorii exprimate într-o sumă fixă de valută, de tipul soldurilor de clienți/furnizori neîncasate/neplătite. Avansurile plătite (409) și cele încasate (419) nu sunt astfel de elemente: pct. 315 alin. (3) din OMFP 1802/2014 le încadrează explicit ca **elemente nemonetare**, alături de stocuri sau imobilizări.

Consecința practică, dată direct de pct. 316 alin. (2): conturile 409 și 419 **nu se reevaluează** la cursul BNR nici lunar, nici la 31.12. Suma înregistrată la data plății/încasării avansului (la cursul din ultima zi bancară anterioară, conform pct. 304) rămâne fixă în lei până la regularizare.

::: ghid-exemplu
O firmă plătește un avans de 10.000 EUR unui furnizor pe 3 martie, la cursul BNR din 2 martie (5,05 lei/EUR) → 50.500 lei înregistrați în 409. Factura finală, de 15.000 EUR, sosește pe 20 aprilie, la cursul din 17 aprilie (5,10 lei/EUR).
- Partea acoperită de avans (10.000 EUR) rămâne la cursul istoric: 50.500 lei — nu se recalculează la 5,10.
- Diferența nefacturată prin avans (5.000 EUR) se convertește la cursul valabil la data exigibilității pentru acea diferență — cursul din data facturii finale: 5.000 × 5,10 = 25.500 lei.
- Total factură finală: 76.000 lei, din care 50.500 lei vin din stornarea avansului (curs istoric) și 25.500 lei din diferența nouă (curs curent).
:::

## Ce se greșește în practică

- Se recalculează întreaga sumă a facturii finale la cursul zilei, "uitând" că partea acoperită de avans trebuie să rămână la cursul istoric al plății/încasării.
- Se reevaluează lunar sau la 31.12 soldurile 409/419, ca și cum ar fi elemente monetare — deși pct. 316 alin. (2) interzice explicit acest lucru.
- Se folosește cursul din data facturii finale pentru toată operațiunea, deși pentru partea de avans exigibilitatea TVA (și deci cursul aplicabil pentru TVA) s-a fixat deja la data încasării/plății avansului.
- Se lasă calculul cursului "pe mai târziu", fără să se documenteze cursul BNR din ziua bancară anterioară plății/încasării avansului, exact cel cerut de pct. 304.

## Ce face iConta.eu

Motorul de avansuri (`core/avansuri.py`) este un motor pur, fără acces la cursul valutar BNR: funcțiile primesc direct `suma_fara_tva`, presupusă deja convertită în lei. Nu există niciun parametru de curs sau monedă în cele patru funcții (`nota_avans_platit`, `nota_regularizare_avans_platit`, `nota_avans_incasat`, `nota_regularizare_avans_incasat`), iar singurul apelant din `core/uc_tenants.py` (`nota_avans`, liniile 3466-3522) transmite suma primită direct de la stratul HTTP, fără nicio conversie valutară.

Onest spus: **iConta.eu nu calculează automat diferența de curs la regularizarea unui avans în valută.** Contabilul trebuie să calculeze el însuși suma în lei — la cursul BNR din ultima zi bancară anterioară datei plății/încasării avansului, respectiv la cursul din data exigibilității pentru orice diferență nefacturată prin avans — și să introducă direct suma în lei rezultată. Motorul respectă corect regula că 409/419 nu se reevaluează (pentru că, oricum, nu are nicio logică de reevaluare), dar responsabilitatea calculului valutar propriu-zis rămâne integral a contabilului.

[iConta.eu](/)
