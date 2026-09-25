---
title: "Cum se înregistrează situațiile de lucrări emise către beneficiar"
description: "Pentru serviciile cu decontări succesive, precum lucrările de construcții-montaj, situația de lucrări este documentul care stabilește, din punct de vedere al TVA, data la care serviciul se consideră prestat."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se înregistrează situațiile de lucrări emise către beneficiar

În construcții, consultanță sau alte servicii facturate pe etape, factura nu se emite pur și simplu „când e gata treaba" — legea leagă momentul exigibilității taxei de un document intermediar: situația de lucrări. Înțelegerea corectă a acestui moment evită atât emiterea prea devreme a facturii, cât și întârzierile care generează accesorii.

## Temeiul legal

::: ghid-temei
„Prestările de servicii care determină decontări sau plăți succesive, cum sunt serviciile de construcții-montaj, consultanță, cercetare, expertiză și alte servicii similare, sunt considerate efectuate la data la care sunt emise situații de lucrări, rapoarte de lucru, alte documente similare pe baza cărora se stabilesc serviciile efectuate sau, după caz, în funcție de prevederile contractuale, la data acceptării acestora de către beneficiari."
— Legea nr. 227/2015 (Codul fiscal), Titlul VII, art. 281 alin. (7) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Pentru servicii de tipul lucrărilor de construcții-montaj, faptul generator al TVA (momentul în care serviciul „se consideră prestat" din punct de vedere fiscal) e legat de **emiterea situației de lucrări**, nu de finalizarea efectivă pe teren, nici de emiterea facturii.
- Dacă totuși contractul prevede expres că serviciul se consideră prestat doar la **acceptarea** situației de lucrări de către beneficiar, atunci acea dată de acceptare, nu data emiterii, marchează faptul generator — clauza contractuală primează.
- De acest moment depinde și termenul de emitere a facturii: potrivit art. 319 alin. (16) din Codul fiscal, factura trebuie emisă cel târziu până în a 15-a zi a lunii următoare celei în care ia naștere faptul generator stabilit conform situației de lucrări.

## Ce se greșește în practică

- Se emite factura la data la care lucrarea a fost fizic terminată, ignorând că faptul generator legal e legat de situația de lucrări (sau de acceptarea ei contractuală), care poate fi o dată ulterioară.
- Se confundă situația de lucrări cu procesul-verbal de recepție a lucrării — sunt documente diferite, cu roluri diferite (unul stabilește faptul generator al TVA, celălalt ține de recepția tehnică/contractuală a lucrării).
- Se omite verificarea clauzei contractuale de acceptare: dacă părțile au convenit ca serviciul să fie considerat prestat abia la acceptarea situației de lucrări, emiterea facturii înainte de acea acceptare poate crea o factură emisă prematur față de faptul generator legal.

## Ce face iConta.eu

Dosarul de cercetare care stă la baza acestui ghid documentează o singură funcționalitate legată de facturile emise — F171, exportul lor tehnic în format XML către programul de contabilitate SAGA, care operează exclusiv pe facturi deja înregistrate în aplicație (`{schema}.facturi`/`factura_linii`) și nu are nicio legătură cu emiterea, calculul faptului generator sau înregistrarea situațiilor de lucrări. Nu s-a găsit, în codul verificat pentru acest dosar, nicio funcționalitate dedicată situațiilor de lucrări ca document distinct de factură, așa că nu putem afirma dacă și cum tratează iConta.eu acest tip de document — orice afirmație în acest sens ar depăși ce a fost efectiv verificat în cod.

[iConta.eu](/)
