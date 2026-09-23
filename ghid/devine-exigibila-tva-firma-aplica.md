---
title: Când devine exigibilă TVA pentru o firmă care aplică TVA la încasare?
description: Exigibilitatea intervine la încasare, integrală sau parțială — dar patru categorii de operațiuni fac excepție și rămân pe regulile generale, chiar dacă firma e înscrisă în sistem.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Când devine exigibilă TVA pentru o firmă care aplică TVA la încasare?

Regula pare simplă — TVA devine exigibilă la încasare, nu la facturare — dar patru categorii de operațiuni fac excepție și rămân pe regulile generale, chiar și pentru o firmă înscrisă în sistem.

## Temeiul legal

::: ghid-temei
**Art. 282 alin. (1) CF**: „Exigibilitatea taxei intervine la data la care are loc faptul generator." (regula generală)

**Art. 282 alin. (3) CF**: „Prin excepție de la prevederile alin. (1) și alin. (2) lit. a), exigibilitatea taxei intervine la data încasării contravalorii integrale sau parțiale a livrării de bunuri ori a prestării de servicii, în cazul persoanelor impozabile care optează în acest sens [...]"

**Art. 282 alin. (6) CF**: „Persoanele impozabile care optează pentru aplicarea sistemului TVA la încasare [...] nu aplică sistemul respectiv pentru următoarele operațiuni care intră sub incidența regulilor generale privind exigibilitatea TVA: a) livrările [...] pentru care beneficiarul este persoana obligată la plata taxei conform art. 307 alin. (2)-(6) sau art. 331; b) livrările [...] care sunt scutite de TVA; c) operațiunile supuse regimurilor speciale prevăzute la art. 311-313; d) livrările [...] pentru care beneficiarul este o persoană afiliată [...]"

Sursă: `anaf_surse/cod_fiscal_227_2015_consolidat.txt`, liniile 17621, 17635, 17694-17706.
:::

Pentru marea majoritate a operațiunilor unei firme înscrise în sistem, exigibilitatea TVA e legată strict de momentul încasării — total sau parțial, indiferent dacă factura a fost emisă cu mult timp înainte. Contul 4428 „TVA neexigibilă" ține evidența sumelor facturate, dar neîncasate încă.

Cele patru excepții de la alin. (6) rămân însă pe regulile generale (faptul generator, respectiv facturare/avans): taxarea inversă, livrările scutite de TVA, operațiunile pe regimuri speciale (art. 311-313) și livrările către persoane afiliate. Pentru acestea, exigibilitatea nu așteaptă încasarea — se calculează ca și cum firma n-ar fi înscrisă în sistem.

## Ce se greșește în practică

- Se aplică mecanismul de încasare și pentru operațiunile exceptate la alin. (6) (mai ales taxare inversă și livrări scutite), ceea ce raportează greșit momentul exigibilității în decont.
- Se confundă data facturii cu data exigibilității, deși pentru TVA la încasare cele două nu mai coincid.
- Se ignoră că o încasare parțială generează exigibilitate parțială, nu integrală, la momentul respectiv.

## Ce face iConta.eu

În `core/d300.py`, motorul separă explicit cele două fluxuri: pentru firmele cu flagul „TVA la încasare" activ, sumele încasate/plătite sunt trecute prin funcția care aplică sută mărită doar pentru operațiunile eligibile — cu excepție explicită, comentată direct în cod, pentru taxarea inversă („taxarea inversă e exigibilă la faptul generator, NU la încasare"). Rezultatul calculat ajunge în rândurile obișnuite de TVA colectată din decont — nu există un rând D300 separat pentru „TVA la încasare"; contul 4428 rămâne pur intern, în afara decontului, până la momentul încasării.

[iConta.eu](/)
