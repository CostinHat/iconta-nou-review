---
title: "Cum se contabilizează plățile prin PayPal într-un magazin online?"
description: "Principiul contabil care stă la baza înregistrării încasărilor prin PayPal sau alte procesatoare de plăți online, în lipsa unei reglementări specifice."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se contabilizează plățile prin PayPal într-un magazin online?

Legislația română nu are un articol dedicat pentru „încasări prin PayPal" — și nici nu e nevoie de unul. PayPal, Stripe, Netopia sau orice alt procesator de plăți online sunt, contabil, doar un alt cont bancar/de trezorerie prin care trec bani, iar principiul care guvernează înregistrarea lor e cel general, valabil pentru orice operațiune economico-financiară: nu se înregistrează nimic în contabilitate fără un document justificativ.

## Temeiul legal

::: ghid-temei
„(1) Orice operațiune economico-financiară efectuată se consemnează în momentul efectuării ei într-un document care stă la baza înregistrărilor în contabilitate, dobândind astfel calitatea de document justificativ. (2) Documentele justificative care stau la baza înregistrărilor în contabilitate angajează răspunderea persoanelor care le-au întocmit, vizat și aprobat, precum și a celor care le-au înregistrat în contabilitate, după caz."
— Legea contabilității nr. 82/1991, art. 6 alin. (1)-(2) (sursă: anaf_surse/legea_82_1991_consolidat.txt)
:::

Notă onestă: legea nu menționează explicit PayPal sau conturile de merchant online — principiul de mai sus e general și se aplică prin analogie, ca pentru orice instrument de încasare (POS, virament, cont escrow). În practică, aplicarea lui la PayPal înseamnă:

- Contul PayPal (sau contul de merchant al procesatorului) se tratează similar unui cont bancar — de regulă analitic distinct al contului 5121 „Conturi la bănci în lei" sau 5124 (valută), pentru trasabilitate.
- Documentul justificativ pentru fiecare încasare e extrasul/raportul de tranzacții emis de PayPal, coroborat cu factura sau bonul fiscal emis către client.
- Comisionul reținut de PayPal la fiecare tranzacție e o cheltuială financiară/de exploatare distinctă (de regulă 627 „Cheltuieli cu serviciile bancare și asimilate"), nu se scade „net" din venit fără evidențiere separată.
- Transferul periodic din contul PayPal către contul bancar real al firmei e un transfer intern între conturi de trezorerie, nu o nouă încasare.

## Ce se greșește în practică

- Se înregistrează venitul „net" (după comisionul PayPal), pierzându-se evidența separată a cheltuielii cu comisionul.
- Se amână înregistrarea până la transferul banilor în contul bancar real, deși încasarea (și obligația de TVA, dacă e cazul) se produce la data confirmării plății de către procesator, nu la data transferului.
- Se ignoră diferențele de curs valutar, când contul PayPal e în valută iar contabilitatea se ține în lei.
- Se consideră că un extras PayPal, fără factura/bonul emis către client, e suficient ca document justificativ.

## Ce face iConta.eu

La data acestui ghid, iConta.eu nu are o funcționalitate dedicată de import sau reconciliere automată a extraselor PayPal — nu am găsit nicio mențiune la „PayPal" în codul aplicației. Încasările prin procesatoare de plăți online se pot introduce manual sau, dacă banca emite un extras unificat, prin modulul general de bancă. Dacă lucrezi cu volume mari de tranzacții PayPal/Stripe, tratează contul procesatorului ca pe un cont de trezorerie separat și înregistrează comisionul distinct, conform principiilor de mai sus.

[iConta.eu](/)
