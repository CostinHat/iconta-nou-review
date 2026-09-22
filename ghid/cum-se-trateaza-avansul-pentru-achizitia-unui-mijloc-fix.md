---
title: Cum se tratează avansul pentru achiziția unui mijloc fix?
description: Avansul pentru imobilizări corporale se înregistrează distinct, în contul 4093, dar contrapartida sa oficială poate fi 401 sau 404 — iConta.eu folosește întotdeauna 401, chiar și pentru avansurile de imobilizări.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se tratează avansul pentru achiziția unui mijloc fix?

Avansurile acordate pentru achiziția unui mijloc fix (imobilizare corporală) se contabilizează separat de avansurile "obișnuite" pentru stocuri sau servicii, în conturi analitice dedicate.

## Temeiul legal

::: ghid-temei
"311. - (1) Avansurile acordate furnizorilor, precum și cele primite de la clienți se înregistrează în contabilitate în conturi distincte. (2) Avansurile acordate furnizorilor de imobilizări se reflectă distinct de avansurile acordate altor furnizori. ..."

"Contul 409 «Furnizori ‐ debitori» — Cu ajutorul acestui cont se ține evidența avansurilor acordate furnizorilor pentru cumpărări de bunuri de natura stocurilor, prestări de servicii, imobilizări corporale sau necorporale. Contul 409 «Furnizori ‐ debitori» este un cont de activ. În debitul contului 409 se înregistrează: ‐ valoarea avansurilor acordate (401, 404); ... În creditul contului 409 se înregistrează: ‐ valoarea avansurilor acordate furnizorilor, cu ocazia regularizării plăților cu aceştia (401, 404); ..."

"(2) Prin excepție de la prevederile alin. (1), exigibilitatea taxei intervine: ... b) la data la care se încasează avansul, pentru plățile în avans efectuate înainte de data la care intervine faptul generator. Avansurile reprezintă plata parțială sau integrală a contravalorii bunurilor și serviciilor, efectuată înainte de data livrării ori prestării acestora;"
:::

## Contul analitic corect și contrapartida

Pentru un avans acordat unui furnizor de mijloace fixe, contul folosit este `4093 "Avansuri acordate pentru imobilizări corporale"` — distinct atât de avansurile pentru stocuri (`4091`), cât și de cele pentru servicii (`4092`), conform pct. 311 alin. (2). TVA aferentă avansului devine exigibilă la data plății, exact ca la orice alt avans (art. 282 alin. 2 lit. b), fără nicio derogare pentru imobilizări.

Un detaliu important, adesea trecut cu vederea: sursa oficială (pct. 8, funcțiunea contului 409) listează **două** conturi posibile ca și contrapartidă a avansului — `401` "Furnizori" **sau** `404` "Furnizori de imobilizări". În practică, pentru avansurile de mijloace fixe, mulți contabili preferă contrapartida `404`, pentru ca soldul acestui cont să reflecte inclusiv obligațiile legate de imobilizări, separat de furnizorii curenți din `401`.

## Ce se greșește în practică

- Se înregistrează avansul pentru un mijloc fix direct în `4091` sau `4092`, în loc de contul analitic corect `4093` — pct. 311 alin. (2) cere distincție explicită.
- Se folosește `401` ca și contrapartidă chiar dacă firma ține evidența furnizorilor de imobilizări separat pe `404`, ceea ce face soldul `404` incomplet și greu de reconciliat cu avansurile efectiv acordate.
- Se capitalizează avansul direct ca parte a valorii mijlocului fix înainte de recepția/punerea în funcțiune a acestuia, în loc să rămână în `4093` până la factura finală.
- Se omite regularizarea avansului la factura finală (stornarea 4093), lăsând soldul contului "agățat" după ce mijlocul fix a fost deja pus în funcțiune.

## Ce face iConta.eu

Funcția `nota_avans_platit(suma_fara_tva, cota, destinatie="stocuri")` acceptă parametrul `destinatie`, mapat prin dicționarul `CONT_AVANS` pe conturile analitice corecte: `stocuri → 4091`, `servicii → 4092`, `imobilizari → 4093`, `imobilizari_necorporale → 4094`. Pentru un avans de mijloc fix, alegerea `destinatie="imobilizari"` generează corect linia pe `4093`.

**Important de știut**: indiferent de `destinatie` aleasă, contrapartida generată de motor este întotdeauna `401` — inclusiv pentru avansurile de imobilizări. Codul nu oferă opțiunea `404`, deși sursa (pct. 8) o listează ca variantă valabilă. Nu este o eroare legală (401 e o contrapartidă acceptată explicit), dar dacă țineți evidența furnizorilor de mijloace fixe separat pe 404, soldul acelui cont nu va reflecta avansurile înregistrate prin iConta.eu — rămâneți cu opțiunea de a urmări avansurile de imobilizări prin analiticul 4093, indiferent de contrapartida 401 folosită de motor.

[iConta.eu](/)
