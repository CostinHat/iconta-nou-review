---
title: "Care este plafonul pentru plățile cash and carry în 2026?"
description: "Plățile în numerar către magazinele de tipul cash and carry au un plafon zilnic dublu față de plafonul general — 10.000 lei, față de 5.000 lei pentru restul furnizorilor."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Care este plafonul pentru plățile cash and carry în 2026?

Magazinele de tipul cash and carry (comerț cu ridicata pentru profesioniști) beneficiază, prin lege, de un plafon de numerar mai mare decât cel aplicabil tranzacțiilor obișnuite cu furnizori — o excepție explicită față de regula generală de 5.000 lei.

## Temeiul legal

::: ghid-temei
„Prin excepție de la prevederile art. 1 alin. (1) se pot efectua operațiuni de încasări și plăți în numerar, în următoarele condiții: [...] d) plăți către magazinele de tipul cash and carry, care sunt organizate și funcționează în baza legislației în vigoare, în limita unui plafon zilnic total de 10.000 lei."
— Legea nr. 70/2015 pentru întărirea disciplinei financiare privind operațiunile de încasări și plăți în numerar, art. 3 alin. (1) lit. d) (sursă: anaf_surse/legea_70_2015_consolidat.txt)
:::

- Plafonul pentru plăți către magazinele cash and carry este de **10.000 lei pe zi, total** (nu per persoană, ci ca plafon global către acel magazin) — dublu față de plafonul general de 5.000 lei/persoană pentru alți furnizori.
- Este interzisă **fragmentarea plăților** pentru a evita depășirea plafonului — facturile cu valoare mai mare de 10.000 lei, în cazul magazinelor cash and carry, nu pot fi achitate integral în numerar, indiferent cum sunt împărțite plățile.
- Peste plafonul de 10.000 lei, diferența se poate achita **numai prin instrumente de plată fără numerar** (transfer bancar, card etc.) — nu în numerar, nici măcar fracționat pe mai multe zile pentru aceeași factură.
- Regulile se aplică și operațiunilor efectuate în valută pe teritoriul României, plafonul convertindu-se la cursul BNR din data operațiunii.

## Ce se greșește în practică

- Se aplică plafonul general de 5.000 lei și magazinelor cash and carry, deși legea prevede expres un plafon dublu, de 10.000 lei, pentru acest tip de furnizor.
- Se împart plățile pe mai multe zile sau pe mai multe chitanțe pentru aceeași factură care depășește plafonul, ignorând interdicția explicită de fragmentare a plăților.
- Se confundă plafonul de încasare (când firma vinde către alte persoane, tot 5.000 lei/persoană, respectiv 10.000 lei pentru cash and carry) cu plafonul de plată, deși regulile sunt simetrice, dar se aplică pe sensuri diferite ale tranzacției.

## Ce face iConta.eu

La data acestui ghid, modulul de casierie din iConta.eu (`core/casa.py`, funcția `verifica_plafon`) verifică automat, pe zi și pe partener, plafoanele din Legea nr. 70/2015, cu un parametru explicit `cash_and_carry` care comută plafonul de încasare de la 5.000 lei (`PLAFON_INCASARE_PJ`) la 10.000 lei (`PLAFON_INCASARE_PJ_CC`) și verifică separat plafonul total de plată de 10.000 lei/zi (`PLAFON_PLATA_PJ_TOTAL`) pentru acest tip de furnizor. Aplicația emite avertismente (nu blochează operațiunea) atunci când o zi sau un partener depășește plafonul aplicabil — decizia finală, inclusiv modul de decontare a diferenței peste plafon, rămâne la utilizator.

[iConta.eu](/)
