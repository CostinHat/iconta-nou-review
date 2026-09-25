---
title: "SAF-T pentru vânzările online și OSS"
description: "Cum se reflectă vânzările online și operațiunile raportate prin regimurile speciale OSS în fișierul standard de control fiscal SAF-T (declarația D406)."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# SAF-T pentru vânzările online și OSS

SAF-T nu este o declarație separată pentru comerțul online — este oglinda contabilă a tuturor facturilor emise de firmă, indiferent de canal. Întrebarea reală e cum se leagă ea de raportarea specifică OSS, care are propriul circuit.

## Temeiul legal

::: ghid-temei
„Fișierul standard de control fiscal (SAF-T), prevăzut la art. 59^1 alin. (1) din Legea nr. 207/2015 privind Codul de procedură fiscală, cu modificările și completările ulterioare, reprezintă un standard internațional utilizat pentru transferul electronic de date din evidența contabilă și fiscală, de la contribuabili/plătitori către autoritățile fiscale și auditori."
— OPANAF nr. 1783/2021, anexa 1, pct. 1 (sursă: anaf_surse/opanaf_1783_2021_saft_d406.txt), cu referire la Legea nr. 207/2015, art. 59^1 alin. (1)
:::

Ce înseamnă asta pentru un magazin online:

- Obligația de depunere a D406 (SAF-T) se raportează la calitatea de contribuabil/plătitor, nu la faptul că firma vinde online — termenele diferă în funcție de categoria de contribuabil (mari, mijlocii, mici), stabilite prin ordin ANAF și publicate în ghidul contribuabilului.
- Vânzările online se regăsesc în SAF-T ca orice altă factură emisă — prin secțiunea de tranzacții (`GeneralLedgerEntries`) și, unde e cazul, prin secțiunea de documente sursă (`SourceDocuments`).
- SAF-T **nu înlocuiește** raportarea OSS: TVA-ul declarat prin regimul special (D398/D399, pe stat de consum) rămâne o raportare separată, cu structură și validator propriu, chiar dacă tranzacțiile de bază apar și în SAF-T ca livrări ale firmei.

## Ce se greșește în practică

- Se crede că depunerea SAF-T „acoperă" și obligațiile de raportare OSS — sunt două fluxuri distincte, cu declarații și termene diferite.
- Se omite verificarea încadrării corecte a facturilor de vânzare la distanță în SAF-T atunci când firma nu are un sistem de facturare care distinge automat TVA-ul intern de cel aferent OSS.
- Se ignoră faptul că o lună fără mișcări din comerțul online tot trebuie raportată în SAF-T — declarația „pe zero" nu se omite, doar secțiunile fără conținut rămân goale.

## Ce face iConta.eu

La data acestui ghid, iConta.eu generează declarația D406 (SAF-T) din registrele contabile ale firmei, inclusiv facturile importate din comerțul electronic (de exemplu, sincronizarea comenzilor WooCommerce, `core/woocommerce.py`), validate structural față de schema oficială ANAF. Aplicația **nu are** o secțiune dedicată operațiunilor OSS în cadrul SAF-T — vânzările online apar ca facturi obișnuite, iar corelarea lor cu sumele raportate separat prin D398/D399 rămâne o verificare manuală a contabilului, aplicația netratând automat legătura dintre cele două raportări.

[iConta.eu](/)
