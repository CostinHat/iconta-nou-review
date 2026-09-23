---
title: Firmă cu TVA la încasare și livrări intracomunitare
description: Livrările intracomunitare scutite rămân pe regulile generale de exigibilitate, chiar dacă firma e înscrisă în sistemul TVA la încasare.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Firmă cu TVA la încasare și livrări intracomunitare

O firmă poate fi simultan înscrisă în TVA la încasare și poate efectua livrări intracomunitare — dar cele două regimuri nu se amestecă: pentru livrările intracomunitare, exigibilitatea taxei urmează o regulă complet separată.

## Temeiul legal

::: ghid-temei
**Art. 282 alin. (6) lit. b) CF**: „Persoanele impozabile care optează pentru aplicarea sistemului TVA la încasare [...] nu aplică sistemul respectiv pentru următoarele operațiuni care intră sub incidența regulilor generale privind exigibilitatea TVA: [...] b) livrările de bunuri/prestările de servicii care sunt scutite de TVA." Sursă: `anaf_surse/cod_fiscal_227_2015_consolidat.txt`, liniile 17694-17701.

**Art. 283 alin. (1) CF**, „Exigibilitatea pentru livrări intracomunitare de bunuri, scutite de taxă": „Prin excepție de la prevederile art. 282, în cazul unei livrări intracomunitare de bunuri, scutite de taxă conform art. 294 alin. (2), exigibilitatea taxei intervine la data emiterii facturii prevăzute la art. 319 alin. (15) sau, după caz, la emiterea autofacturii prevăzute la art. 319 alin. (9) ori în cea de-a 15-a zi a lunii următoare celei în care a intervenit faptul generator, dacă nu a fost emisă nicio factură/autofactură până la data respectivă." Sursă: `anaf_surse/cod_fiscal_227_2015_consolidat.txt`, liniile 17781-17786.
:::

Livrările intracomunitare de bunuri scutite de taxă (art. 294 alin. 2) se încadrează la „livrări scutite de TVA" de la art. 282 alin. (6) lit. b) — deci, chiar dacă firma e înscrisă în sistemul TVA la încasare, aceste livrări specifice nu urmează regula exigibilității la încasare, ci regula proprie de la art. 283: exigibilitatea intervine la data facturii (sau autofacturii), sau cel târziu în a 15-a zi a lunii următoare faptului generator, dacă nu s-a emis nicio factură până atunci.

Practic, o firmă cu TVA la încasare continuă să aplice mecanismul de încasare pentru vânzările interne, dar tratează livrările intracomunitare separat, ca și cum n-ar fi înscrisă în sistem pentru acele operațiuni. Nu e nevoie de niciun calcul special legat de momentul plății primite de la clientul din UE — data care contează e cea a facturii.

## Ce se greșește în practică

- Se așteaptă încasarea de la clientul intracomunitar înainte de a raporta livrarea în decont/D390, deși exigibilitatea e legată de data facturii, nu de plată.
- Se presupune că o firmă cu operațiuni intracomunitare nu poate fi înscrisă în TVA la încasare — eligibilitatea nu exclude firmele cu operațiuni intracomunitare, doar tratamentul acestor operațiuni specifice diferă.
- Se raportează livrarea intracomunitară pe rândurile de TVA la încasare, în loc de rândurile normale de operațiuni scutite cu drept de deducere.

## Ce face iConta.eu

Codul confirmă separarea: `core/d300.py` exclude explicit din calculul prin `tva_incasare.tva_din_incasare()` operațiunile care nu intră sub mecanismul de încasare, iar comentariul din sursă precizează regula pentru taxarea inversă (art. 282 alin. 6) — aceeași logică de excludere se aplică oricărei operațiuni de la alin. (6), inclusiv livrărilor scutite. Cercetarea de față nu a verificat separat, linie cu linie, raportarea specifică a livrărilor intracomunitare în D390 din perspectiva TVA la încasare — pentru situații punctuale, recomandăm verificarea directă în aplicație.

[iConta.eu](/)
