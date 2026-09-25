---
title: "Cum corectez un obiect de inventar înregistrat greșit ca mijloc fix?"
description: "Pașii practici de stornare atunci când un bun sub pragul legal a fost pus greșit la amortizare, cu mecanismul de stornare în roșu sau în negru."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum corectez un obiect de inventar înregistrat greșit ca mijloc fix?

Dincolo de principiul general al corectării erorilor contabile, întrebarea practică e: ce notă contabilă scriu efectiv, ca să anulez o amortizare pornită greșit pe un bun care, de fapt, era sub pragul legal? Răspunsul depinde de tehnica de stornare aleasă și de câte luni de amortizare au fost deja înregistrate până la descoperirea greșelii.

## Temeiul legal

::: ghid-temei
„69. - Înregistrarea stornării unei operațiuni contabile aferente exercițiului financiar curent se efectuează fie prin corectarea cu semnul minus a operațiunii inițiale (stornare în roșu), fie prin înregistrarea inversă a acesteia (stornare în negru), în funcție de politica contabilă și programele informatice utilizate."
— OMFP 1802/2014, reglementări contabile, pct. 69 (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.html)
:::

Ce înseamnă, concret, cele două tehnici:

- **Stornare în roșu**: se repetă exact operațiunea inițială (aceleași conturi, aceeași sumă), dar cu semnul minus — anulează efectul fără să mărească artificial rulajele conturilor implicate.
- **Stornare în negru**: se înregistrează operațiunea inversă, cu semnul plus, pe conturile schimbate între ele — are același efect final asupra soldurilor, dar mărește rulajul contabil.
- **Alegerea între cele două** ține de politica contabilă a firmei și de programul informatic folosit — legea nu impune una dintre ele, ci le lasă echivalente ca rezultat.
- Odată stornată amortizarea deja înregistrată, bunul se recunoaște corect ca obiect de inventar: valoarea lui de intrare trece integral pe cheltuială (cont 603), o singură dată, nu eșalonat.
- Dacă amortizarea greșită s-a întins pe mai multe luni sau peste un exercițiu financiar încheiat, se aplică regulile generale de corectare a erorilor (contul curent de profit și pierdere pentru eroarea din anul curent, rezultatul reportat pentru o eroare semnificativă dintr-un an anterior).

## Ce se greșește în practică

- Se oprește pur și simplu calculul amortizării de la luna curentă, fără să se storneze sumele deja înregistrate în lunile anterioare — bunul rămâne cu o valoare netă contabilă parțial amortizată, deși ar fi trebuit să fie deja integral pe cheltuială.
- Se amestecă cele două tehnici de stornare (parțial în roșu, parțial în negru) pe aceeași operațiune, ceea ce îngreunează reconcilierea ulterioară.
- Se uită corectarea fișei/evidenței analitice a mijlocului fix, care rămâne activă în registru deși bunul a fost reclasificat ca obiect de inventar.

## Ce face iConta.eu

Aplicația nu are un buton de „corectează clasificarea" — nici pentru acest sens, nici pentru cel invers. Notele de amortizare generate greșit pentru un bun care era, de fapt, obiect de inventar trebuie stornate manual (în roșu sau în negru, după politica firmei), iar bunul reintrodus corect prin formularul „Obiecte de inventar (303)" din ecranul „Operațiuni speciale", care generează automat nota de dare în folosință (603 = 303) cu evidența extracontabilă aferentă (8035). Pasul de stornare a amortizării anterioare rămâne, la acest moment, în afara automatizării aplicației.

[iConta.eu](/)
