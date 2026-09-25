---
title: "Corectarea facturilor intracomunitare emise cu TVA eronat"
description: "Mecanismul general de corectare a facturilor din Codul fiscal, aplicat livrărilor intracomunitare pe care s-a aplicat greșit TVA în loc de scutire — sau invers."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Corectarea facturilor intracomunitare emise cu TVA eronat

Codul fiscal nu prevede o procedură separată pentru corectarea facturilor intracomunitare — se aplică regula generală de corectare a facturilor, de la art. 330, indiferent dacă eroarea constă în aplicarea greșită a TVA pe o livrare intracomunitară scutită, sau în omiterea TVA pe o operațiune care de fapt nu se califica pentru scutire.

## Temeiul legal

::: ghid-temei
„(1) Corectarea informațiilor înscrise în facturi sau în alte documente care țin loc de factură se efectuează astfel:
a) în cazul în care factura nu a fost transmisă către beneficiar, aceasta se anulează și se emite o nouă factură;
b) în cazul în care factura a fost transmisă beneficiarului, fie se emite o nouă factură care trebuie să cuprindă, pe de o parte, informațiile din factura inițială, numărul și data facturii corectate, valorile cu semnul minus [...], iar, pe de altă parte, informațiile și valorile corecte, fie se emite o nouă factură conținând informațiile și valorile corecte și concomitent se emite o factură cu valorile cu semnul minus [...], în care se înscriu numărul și data facturii corectate."
— Legea 227/2015 (Codul fiscal), art. 330 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Aplicat la o livrare intracomunitară cu TVA eronat:

- **Dacă TVA a fost aplicat greșit** pe o livrare care de fapt îndeplinea condițiile de scutire (art. 294 din Codul fiscal — livrare intracomunitară către un cumpărător înregistrat în scopuri de TVA în alt stat membru, cu transportul dovedit), factura se corectează prin una din cele două metode de la art. 330 alin. (1) lit. b): fie o factură nouă care anulează valorile eronate (cu semnul minus) și le înlocuiește cu cele corecte, fie o factură corectă nouă însoțită de o factură de stornare separată.
- **Dacă scutirea a fost aplicată greșit** (operațiunea nu îndeplinea de fapt condițiile de scutire intracomunitară — de exemplu, cumpărătorul nu era înregistrat valid în scopuri de TVA în statul membru de destinație), corectarea se face în sens invers: se emite factura corectă cu TVA aplicat, prin aceeași procedură de la art. 330.
- **Ambele facturi** (cea inițială stornată și cea corectă) se transmit beneficiarului și se reflectă în decontul de TVA aferent perioadei în care se face corectarea, nu retroactiv în perioada facturii inițiale.

## Ce se greșește în practică

- Se anulează pur și simplu factura greșită, fără să se emită factura de stornare cu valorile negative — procedura corectă presupune fie factură nouă cu stornare inclusă, fie factură corectă însoțită de o factură de stornare separată, nu doar o simplă „ștergere".
- Se corectează retroactiv decontul de TVA din luna facturii inițiale, în loc să se reflecte corectarea în perioada în care aceasta a fost efectiv emisă — regula generală de corectare nu presupune rectificarea automată a perioadelor anterioare.
- Se omite verificarea prealabilă a valabilității codului de TVA al cumpărătorului din alt stat membru (prin sistemul VIES) înainte de a aplica scutirea intracomunitară — o verificare simplă, care ar preveni multe corectări ulterioare.

## Ce face iConta.eu

iConta.eu permite emiterea de facturi de corecție/stornare conform mecanismului de la art. 330 din Codul fiscal; verificarea validității codului de TVA al partenerului intracomunitar (VIES) și decizia privind aplicarea sau nu a scutirii rămân, la data acestui ghid, în responsabilitatea utilizatorului la momentul facturării.

[iConta.eu](/)
