---
title: "Cum verific dacă o mașină second-hand din UE este facturată în regim de marjă?"
description: "Mențiunea obligatorie pe factură prin care se identifică o achiziție intracomunitară de bun second-hand taxată în regimul special al marjei de profit."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum verific dacă o mașină second-hand din UE este facturată în regim de marjă?

Când cumperi o mașină second-hand de la un dealer din alt stat membru UE, modul în care este taxată operațiunea depinde de regimul aplicat de vânzător: regimul normal de TVA sau regimul special de marjă a profitului. Diferența contează pentru tratamentul tău fiscal (nu se aplică taxare inversă la achiziția intracomunitară dacă vânzătorul a aplicat regimul de marjă) și se verifică direct pe factură, printr-o mențiune standardizată.

## Temeiul legal

::: ghid-temei
„dacă se aplică unul dintre regimurile speciale pentru bunuri second-hand, opere de artă, obiecte de colecție și antichități, una dintre mențiunile «regimul marjei - bunuri second-hand», «regimul marjei - opere de artă» sau «regimul marjei - obiecte de colecție și antichități», după caz"
— Codul fiscal (Legea nr. 227/2015), art. 319 (elementele facturii) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Prima verificare este simplă: caută pe factură mențiunea **„regimul marjei - bunuri second-hand"**. Dacă apare, vânzătorul a aplicat regimul special de la art. 312 din Codul fiscal, iar TVA nu este evidențiată distinct pe factură (este inclusă în marja de profit a revânzătorului).
- Regimul special se aplică de „persoana impozabilă revânzătoare" — cea care, în cursul activității economice, achiziționează bunuri second-hand (inclusiv mașini) în scopul revânzării, indiferent dacă acționează în nume propriu sau ca intermediar.
- Marja profitului, potrivit definiției legale, este „diferența dintre prețul de vânzare aplicat de persoana impozabilă revânzătoare și prețul de cumpărare" — pe această diferență se calculează TVA-ul inclus, nu pe prețul total al mașinii.
- Dacă factura **nu** conține mențiunea de marjă, ci arată TVA colectată distinct (sau, dimpotrivă, o mențiune de scutire/taxare inversă), operațiunea este taxată în regim normal, cu consecințe fiscale diferite pentru cumpărătorul din România (de regulă, o achiziție intracomunitară supusă taxării inverse).

## Ce se greșește în practică

- Se presupune, fără să se verifice factura, că orice mașină second-hand cumpărată din UE e automat în regim de marjă — de fapt regimul e opțional pentru revânzător și depinde de sursa de la care a achiziționat bunul (persoană neimpozabilă, persoană scutită sau altă întreprindere mică, potrivit art. 312 alin. (2)).
- Se tratează greșit ca achiziție intracomunitară cu taxare inversă o factură care, de fapt, e emisă în regim de marjă — ceea ce duce la autofacturare eronată în evidența TVA.
- Se caută TVA-ul „ascuns" în totalul facturii, deși regimul de marjă interzice explicit înscrierea distinctă a TVA pe factură.
- Se ignoră faptul că mențiunea trebuie să fie exact una dintre formulările prevăzute de lege — o factură fără nicio mențiune specială ridică suspiciunea unei erori de facturare din partea vânzătorului.

## Ce face iConta.eu

Din verificarea codului sursă, iConta.eu are un motor dedicat regimului special de marjă (`core/tva_marja.py`), care calculează marja și TVA-ul aferent (formula sutei mărite) **atunci când firma din iConta vinde ea însăși** bunuri în acest regim — motorul este documentat explicit cu temeiul „art. 312 CF", iar rezultatul e folosit pentru a genera o notă contabilă (înregistrare de tip „ciornă") cu descrierea operațiunii. Modulul nu generează însă, la acest moment, o factură PDF cu mențiunea legală „regimul marjei - bunuri second-hand" tipărită pe document (generatorul de facturi al aplicației, `core/factura_pdf.py`, nu conține nicio referire la acest regim) — mențiunea rămâne, pentru facturile emise de firmă, de verificat/adăugat manual. Modulul nu este, oricum, gândit pentru verificarea facturilor **primite** de la furnizori din UE: pentru o achiziție de mașină second-hand dintr-un alt stat membru, verificarea rămâne, la acest moment, una manuală — se citește mențiunea de pe factura vânzătorului, conform explicației de mai sus.

[iConta.eu](/)
