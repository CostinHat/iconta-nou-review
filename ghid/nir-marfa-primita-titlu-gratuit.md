---
title: "Cum se face NIR pentru marfa primită cu titlu gratuit?"
description: "Pașii de recepție și monografia contabilă pentru marfa primită cu titlu gratuit, când NIR-ul e necesar, conform OMFP 2634/2015 și OMFP 1802/2014."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se face NIR pentru marfa primită cu titlu gratuit?

Când marfa primită gratuit cade sub una dintre situațiile care impun NIR — sosește fără document de livrare, prezintă diferențe la recepție, sau gestiunea beneficiarului ține evidența la preț de vânzare — întocmirea lui urmează aceleași reguli tehnice ca la orice NIR, cu o singură diferență reală: valoarea de intrare.

## Temeiul legal

::: ghid-temei
„În situația în care se constată diferențe la recepție, entitățile trebuie să stabilească prin proceduri proprii informațiile care trebuie să fie înscrise în Nota de recepție și constatare de diferențe (ex: cantitatea și valoare constatate plus/minus, persoanele care au făcut recepția și alte mențiuni, în funcție de necesități)."
— OMFP 2634/2015, Anexa 2, Cod 14-3-1A (sursă: anaf_surse/omfp_2634_2015_anexa2_norme_specifice.txt)

„75. - (1) La data intrării în entitate, bunurile se evaluează și se înregistrează în contabilitate la valoarea de intrare, care se stabilește astfel: [...] d) la valoarea justă - pentru bunurile obținute cu titlu gratuit sau constatate plus la inventariere."
— OMFP 1802/2014, pct. 75 alin. (1) lit. d) (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Pașii, pentru cazul în care NIR-ul e necesar:

1. **Se completează cantitatea** primită efectiv, verificată la recepție împotriva documentului de însoțire (aviz cu mențiunea „Fără factură") sau, în lipsa oricărui document, pe baza constatării comisiei de recepție.
2. **Se stabilește valoarea de intrare la valoare justă** — nu există preț de achiziție, deci se folosește prețul de piață al unor bunuri similare sau valoarea declarată de cedent în actul de donație/sponsorizare.
3. **Se înregistrează contabil intrarea în gestiune** cu contrapartida contul 758 "Alte venituri din exploatare" (materii prime, materiale, ambalaje) — planul de conturi precizează explicit, la conturile de stocuri, că valoarea bunurilor „primite cu titlu gratuit" se înregistrează în corespondență cu 758.

## Ce se greșește în practică

- Se lasă valoarea de intrare pe NIR la zero, pentru că marfa "nu a costat nimic" — obligația e evaluarea la valoare justă, nu la valoare nulă, iar o intrare la zero denaturează gestiunea și rezultatul.
- Se înregistrează contravaloarea în contul de furnizori (401), ca la o achiziție normală, deși nu există nicio datorie de plată — contrapartida corectă e un cont de venituri (758), nu de datorii.
- Se omite documentarea sursei valorii juste (ofertă de preț, evaluare, valoare din actul de cedare) — la un control, absența justificării face imposibilă verificarea corectitudinii sumei înscrise pe NIR.

## Ce face iConta.eu

La data acestui ghid, `core/stocuri.py` conține motorul `nir_gv()` pentru NIR global-valoric (cu adaos comercial și TVA neexigibilă) și `core/stocuri_cv_api.py` oferă funcția `intrare()` pentru încărcarea cantitativă în gestiune. Ambele acceptă orice valoare unitară introdusă de utilizator, deci pot procesa tehnic o intrare la valoare justă — dar aplicația nu are un flux dedicat „marfă gratuită" care să sugereze automat contul de venituri 758 ca și contrapartidă sau să ceară documentarea sursei valorii juste. Determinarea valorii și alegerea contului de contrapartidă rămân, azi, decizii ale contabilului.

[iConta.eu](/)
