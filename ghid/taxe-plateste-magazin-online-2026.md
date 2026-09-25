---
title: "Ce taxe plătește un magazin online în 2026?"
description: "Structura de bază a taxelor pe care le datorează un magazin online din România — impozit pe venit/profit, TVA și contribuții — și pragul de 100.000 euro care decide regimul de impozitare."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce taxe plătește un magazin online în 2026?

Un magazin online nu are un regim fiscal special doar pentru că vinde prin internet. Firma care îl operează plătește aceleași taxe ca orice alt comerciant — impozit pe veniturile microîntreprinderii sau pe profit, TVA colectat la vânzări, contribuții pentru eventualii angajați — iar ce se schimbă, de la un an la altul, sunt pragurile și cotele aplicabile.

## Temeiul legal

::: ghid-temei
„(1) În sensul prezentului titlu, o microîntreprindere este o persoană juridică română care îndeplinește cumulativ următoarele condiții, la data de 31 decembrie a anului fiscal precedent: [...] c) a realizat venituri care nu au depășit echivalentul în lei a 100.000 euro. Cursul de schimb pentru determinarea echivalentului în euro este cel valabil la închiderea exercițiului financiar în care s-au înregistrat veniturile;"
— Legea nr. 227/2015 (Codul fiscal), art. 47 alin. (1) lit. c) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Pentru un magazin online organizat ca SRL, structura taxelor din 2026 arată astfel:

- **Impozitul pe venit sau pe profit** — sub pragul de 100.000 euro venituri anuale (și celelalte condiții cumulative de la art. 47), firma poate aplica impozitul pe veniturile microîntreprinderilor; peste prag, trece obligatoriu la impozit pe profit, cu o bază de calcul mai complexă (venituri minus cheltuieli deductibile).
- **TVA** — dacă firma e înregistrată în scopuri de TVA (obligatoriu peste plafonul de scutire), colectează TVA la fiecare vânzare către clienți din România și, pentru vânzările către consumatori din alte state UE, aplică regulile pragului de 10.000 euro și, eventual, regimul OSS.
- **Contribuții sociale** — dacă magazinul are angajați (chiar și asociatul unic care lucrează efectiv în firmă, prin contract de muncă), se datorează contribuțiile sociale obligatorii aferente salariilor.
- **RO e-Factura** — pentru operațiunile B2B (către alte firme), facturile trebuie transmise prin sistemul național RO e-Factura, potrivit obligației generale aplicabile persoanelor impozabile stabilite în România.
- **Taxe locale, dacă e cazul** — impozit pe clădiri/terenuri pentru eventualul spațiu de depozitare sau sediu deținut în proprietate.

## Ce se greșește în practică

- Se presupune că un magazin online rămâne la impozitul micro indiferent de cifra de afaceri, fără să se monitorizeze pragul de 100.000 euro pe parcursul anului.
- Se ignoră obligațiile de TVA pentru vânzările către clienți din alte state UE, tratând toate vânzările ca operațiuni interne, supuse doar TVA românesc.
- Se confundă obligația de facturare electronică (B2B, prin RO e-Factura) cu vânzările B2C către consumatori finali, care nu intră sub aceeași obligație de transmitere.

## Ce face iConta.eu

La data acestui ghid, iConta.eu urmărește regimul fiscal declarat al firmei (micro sau profit) și generează declarațiile aferente — D100 pentru regimul micro, D101 pentru impozitul pe profit (`core/d100.py`, `core/d101.py`) — precum și deconturile de TVA (`core/d300.py`). Pentru magazinele online conectate la un magazin propriu, aplicația poate importa automat comenzile prin conectorul WooCommerce (`core/woocommerce.py`), generând facturi pe baza lor. Aplicația nu decide însă strategia fiscală a firmei (de exemplu momentul optim de trecere de la micro la profit) — aceasta rămâne o analiză pe care contabilul o face pe baza cifrelor reale ale magazinului.

[iConta.eu](/)
