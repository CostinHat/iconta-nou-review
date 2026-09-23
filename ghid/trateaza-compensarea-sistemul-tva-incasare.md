---
title: Cum se tratează compensarea în sistemul TVA la încasare?
description: Compensarea între firme e considerată încasare la data compensării — nu la data facturii — cu reguli diferite după cum ambele părți sunt persoane juridice sau nu.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se tratează compensarea în sistemul TVA la încasare?

Compensarea unei datorii cu o creanță echivalează, din perspectiva TVA la încasare, cu o plată efectivă — exigibilitatea taxei se mută la data la care compensarea are loc, cu formalități diferite în funcție de tipul părților implicate.

## Temeiul legal

::: ghid-temei
**Pct. 26 alin. (7) din Normele metodologice de aplicare a Codului fiscal (HG 1/2016)**: „În sensul art. 282 alin. (3) din Codul fiscal, prin încasarea contravalorii livrării de bunuri sau a prestării de servicii se înțelege orice modalitate prin care furnizorul/prestatorul obține contrapartida pentru aceste operațiuni de la beneficiarul său ori de la un terț, precum plata în bani, plata în natură, **compensarea**, cesiunea de creanțe, utilizarea unor instrumente de plată." Sursă: `anaf_surse/hg_1_2016_norme_cod_fiscal.txt`, linia 6558.

**Pct. 26 alin. (9)**: „În cazul compensării datoriilor aferente unor facturi pentru livrări de bunuri/prestări de servicii se consideră că furnizorul/prestatorul a încasat, respectiv beneficiarul a plătit contravaloarea bunurilor/serviciilor, la data la care se sting total sau parțial datoriile, respectiv: a) în cazul compensărilor între persoane juridice, la data compensării realizate conform prevederilor [Ordonanței de urgență a Guvernului nr. 77/1999 și Hotărârii Guvernului nr. 685/1999]; b) în cazul compensărilor în care cel puțin una dintre părți nu este persoană juridică, la data semnării unui proces-verbal de compensare care să cuprindă cel puțin [...] denumirea părților, codul de înregistrare în scopuri de TVA [...], numărul facturii, data emiterii facturii, valoarea facturii, inclusiv taxa pe valoarea adăugată, valoarea compensată, semnătura părților și data semnării procesului-verbal de compensare." Sursă: `anaf_surse/hg_1_2016_norme_cod_fiscal.txt`, liniile 6575-6580.
:::

Când o firmă înscrisă în TVA la încasare stinge o factură prin compensare (nu prin plată efectivă), TVA devine exigibilă exact ca la o încasare obișnuită, dar data de referință diferă după tipul părților: între două persoane juridice, data compensării propriu-zise (conform legislației speciale privind blocajul financiar); dacă cel puțin una din părți nu e persoană juridică, data semnării unui proces-verbal de compensare, cu conținut minim obligatoriu (părți, CUI, factură, valoare, semnături, dată).

Fără acest proces-verbal, pentru compensările care implică o parte care nu e persoană juridică, nu există o dată certă de exigibilitate — de aceea documentul nu e o formalitate opțională, ci elementul care stabilește exact când s-a produs exigibilitatea taxei.

## Ce se greșește în practică

- Se tratează compensarea ca și cum n-ar avea niciun efect asupra exigibilității TVA la încasare, lăsând suma pe 4428 la nesfârșit.
- Se ignoră procesul-verbal de compensare atunci când una din părți nu e persoană juridică, deși norma îl cere explicit ca dovadă a datei de exigibilitate.
- Se confundă data facturii sau data notei contabile de compensare internă cu data reală a compensării, conform legislației speciale.

## Ce face iConta.eu

Cercetarea la sursă a codului F097 (`core/tva_incasare.py`, `core/d300.py`) nu a identificat o ramură dedicată compensării — motorul calculează exigibilitatea pe baza sumelor introduse manual de contabil în ecranul „TVA la încasare" (`nota-tva-incasare`), indiferent de modalitatea de stingere a datoriei. Practic, contabilul introduce suma și data la care compensarea a devenit efectivă (data compensării sau data procesului-verbal), iar aplicația calculează TVA exigibilă cu metoda sutei mărite — dar stabilirea acestei date rămâne responsabilitatea contabilului, nu e automatizată.

[iConta.eu](/)
