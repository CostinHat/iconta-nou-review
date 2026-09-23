---
title: "Pot amâna plata TVA până când încasez factura?"
description: "Explică mecanismul legal prin care TVA colectată devine exigibilă abia la încasarea facturii, în sistemul TVA la încasare."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Pot amâna plata TVA până când încasez factura?

Da — dar numai dacă firma e înscrisă în sistemul TVA la încasare, iar tranzacția nu face parte din categoriile excluse prin lege.

## Temeiul legal

::: ghid-temei
Art. 282 alin. (3) Cod fiscal: „Prin excepție de la prevederile alin. (1) și alin. (2) lit. a), exigibilitatea taxei intervine la data încasării contravalorii integrale sau parțiale a livrării de bunuri ori a prestării de servicii, în cazul persoanelor impozabile care optează în acest sens... Plafonul pentru aplicarea sistemului TVA la încasare este de: a) 5.000.000 lei, în perioada 1 martie-31 decembrie 2026; b) 5.500.000 lei, începând cu data de 1 ianuarie 2027." (`cod_fiscal_227_2015_consolidat.txt`)
:::

Regula generală (art. 282 alin. 1) e că TVA devine exigibilă la faptul generator (livrare/prestare), indiferent dacă ați fost plătit. Pentru firmele care optează pentru TVA la încasare și se încadrează sub plafon (eligibilitate detaliată la art. 282 alin. 3^1 — înregistrare TVA conform art. 316, sediu în România), regula se schimbă: TVA devine exigibilă abia la data încasării, integrale sau parțiale.

Mecanic, art. 282 alin. (8) precizează că „fiecare încasare totală sau parțială se consideră că include și taxa aferentă" — adică TVA se extrage din suma încasată prin sută mărită (sumă × cotă/(100+cotă)), nu se adaugă separat.

Amânarea nu e însă universală. Art. 282 alin. (6) exclude explicit din mecanism, chiar și pentru firmele înscrise: operațiunile cu taxare inversă (art. 307 alin. 2-6 sau art. 331), livrările scutite, regimurile speciale (art. 311-313) și livrările către persoane afiliate. Pentru aceste operațiuni, TVA rămâne exigibilă la faptul generator, ca la regula generală.

O întrebare firească e cât de mult se poate amâna plata dacă clientul, o firmă, pur și simplu nu plătește. Conform art. 287, un mecanism de ajustare a bazei există doar pentru falimentul/reorganizarea judiciară confirmată a debitorului (lit. d) sau, separat, pentru creanțe neîncasate de la **persoane fizice**, în 12 luni de la termenul de plată (lit. f). Pentru o factură emisă către o altă firmă care nu e în faliment sau reorganizare, legea nu prevede niciun mecanism de exigibilitate forțată — TVA rămâne pur și simplu neexigibilă, indiferent cât timp trece.

## Ce se greșește în practică

O confuzie frecventă e amestecarea exigibilității (CÂND se datorează TVA, art. 282) cu cota aplicabilă (CE PROCENT se aplică, art. 291 alin. 5) — sunt două reguli distincte în lege. O altă greșeală e presupunerea că amânarea se aplică și operațiunilor cu taxare inversă sau către afiliați, deși art. 282 alin. (6) le exclude explicit.

## Ce face iConta.eu

Motorul (`core/tva_incasare.py`) calculează TVA exigibilă din suma încasată prin sută mărită, exact conform art. 282 alin. (8). În decont (`core/d300.py`), pentru firmele cu flagul `tva_la_incasare` activ, sumele calculate ajung în rândurile obișnuite de TVA colectată (R9_1/R9_2, R10, R11) — nu există un rând D300 separat pentru „TVA la încasare". Codul aplică explicit excepția pentru taxare inversă, care „rămâne pe calea de emitere" chiar și pentru o firmă înscrisă în sistem. Contul 4428 (TVA neexigibilă) rămâne intern, în afara decontului, până la încasarea efectivă.

[iConta.eu](/)
