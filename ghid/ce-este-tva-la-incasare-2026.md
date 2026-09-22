---
title: Ce este TVA la încasare și cum funcționează în 2026?
description: TVA la încasare mută momentul exigibilității taxei de la facturare la încasarea efectivă a banilor, pentru firmele eligibile sub plafonul de 5.000.000 lei (01.03-31.12.2026); taxa se extrage din sumă prin suta mărită, cota/(100+cota).
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Ce este TVA la încasare și cum funcționează în 2026?

Pentru majoritatea firmelor plătitoare de TVA, taxa devine exigibilă — adică datorată la stat — în momentul facturării, indiferent dacă banii au ajuns sau nu în cont. TVA la încasare inversează asta pentru firmele care optează: taxa e datorată abia când clientul plătește efectiv, integral sau parțial. E un sistem opțional, nu unul universal, și are un mecanism de calcul și de contare specific, diferit de facturarea obișnuită.

## Temeiul legal

::: ghid-temei
**Art. 282 din Codul fiscal (Legea 227/2015) — Exigibilitatea taxei.**

**Alin. (1)** — regula generală: *„Exigibilitatea taxei intervine la data la care are loc faptul generator."*

**Alin. (3)** (modificat de OUG 8/2026 art. 6 pct. 38, de la 01.03.2026): *„Prin excepție de la prevederile alin. (1) și alin. (2) lit. a), exigibilitatea taxei intervine la data încasării contravalorii integrale sau parțiale a livrării de bunuri ori a prestării de servicii, în cazul persoanelor impozabile care optează în acest sens, denumite în continuare persoane care aplică sistemul TVA la încasare. Plafonul pentru aplicarea sistemului TVA la încasare este de: a) 5.000.000 lei, în perioada 1 martie-31 decembrie 2026; ... b) 5.500.000 lei, începând cu data de 1 ianuarie 2027."*

**Alin. (8)** — mecanismul de calcul: *„Pentru determinarea taxei aferente încasării contravalorii integrale sau parțiale a livrării de bunuri ori a prestării de servicii, care devine exigibilă potrivit prevederilor alin. (3), fiecare încasare totală sau parțială se consideră că include și taxa aferentă."*
:::

## Mecanismul, pas cu pas

**La facturare**, TVA-ul nu e încă exigibil — el intră în contabilitate ca **TVA neexigibilă**, în contul **4428**, nu direct în 4427 (TVA colectată). Nota contabilă tipică pentru o factură emisă: `4111 = 707 + 4428`.

**La încasare**, taxa devine exigibilă exact pe suma efectiv încasată — nu pe toată factura, dacă încasarea e parțială. Alin. (8) spune că suma încasată „se consideră că include și taxa aferentă": taxa se extrage din suma încasată prin suta mărită,

```
TVA exigibil = suma încasată × cotă / (100 + cotă)
```

de exemplu, la cota standard de 21%: `suma × 21 / 121`.

Odată calculat TVA-ul exigibil din acea încasare, se face transferul contabil din TVA neexigibilă în TVA colectată: **4428 = 4427**, cu suma calculată. Simetric, pentru o factură primită de la un furnizor tot la TVA la încasare, TVA-ul deductibil rămâne inițial în 4428 și trece în 4426 abia la plata efectivă către furnizor: **4426 = 4428**.

**Important — contarea nu e automată pentru firmele la TVA la încasare.** Pentru că exigibilitatea depinde de reconcilierea bancară (cine a plătit, cât, când), o factură emisă sau primită de o firmă în acest regim nu poate fi contată complet automat în momentul emiterii — nota contabilă finală depinde de plăți ulterioare, care se produc treptat, uneori pe parcursul mai multor luni. Contarea corectă a acestui transfer cere intervenție manuală a contabilului, corelată cu extrasul de cont.

## Ce se greșește în practică

- **Se pune direct TVA-ul integral în 4427 la facturare**, ca la regimul normal. Corect e 4428 (neexigibilă) la facturare, iar transferul în 4427 se face abia treptat, pe măsura încasării.
- **Se calculează TVA-ul din încasare aplicând cota direct la sumă**, în loc de suta mărită. Suma încasată include deja taxa (alin. (8)) — cota se aplică pe formula `suma × cotă/(100+cotă)`, nu `suma × cotă`.
- **Se presupune că sistemul se aplică tuturor firmelor sub plafon, automat.** E un regim opțional (alin. (3): „persoanele impozabile care optează") — sub plafon poți alege să intri, nu ești obligat.

## Ce face iConta.eu

Plafonul de eligibilitate se verifică pe baza datei: 5.000.000 lei pentru perioada 01.03.2026-31.12.2026, 5.500.000 lei de la 01.01.2027 — identic cu art. 282 alin. (3) lit. a)/b). Formula de calcul a TVA-ului exigibil dintr-o încasare (suta mărită, `suma × cotă/(100+cotă)`, rotunjită la 2 zecimale) e implementată și acoperită de teste.

Pentru firmele marcate în profil ca aplicând TVA la încasare, contarea automată a facturii e refuzată explicit, tocmai pentru că taxa intră inițial pe 4428 și devine exigibilă abia din reconcilierea bancară ulterioară — factura trebuie contată manual, de un om. Menționăm asta pentru că, la data acestui ghid, mecanismul de transfer 4428→4427 nu are încă nicio instanță vie pe firme reale din portofoliu — calibrarea lui rămâne una sintetică, verificată prin teste, nu prin utilizare efectivă la o firmă în regim.

[iConta.eu](/)
