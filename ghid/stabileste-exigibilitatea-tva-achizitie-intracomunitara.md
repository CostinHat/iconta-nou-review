---
title: "Cum se stabilește exigibilitatea TVA la o achiziție intracomunitară?"
description: "Exigibilitatea e data facturii furnizorului, dar niciodată mai târziu de a 15-a zi a lunii următoare celei în care a avut loc livrarea (faptul generator) — art. 284 din Codul fiscal."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se stabilește exigibilitatea TVA la o achiziție intracomunitară?

Data exigibilității decide luna în care operațiunea intră în decont și în D390 — și e cea mai frecventă sursă de confuzie la achizițiile intracomunitare, pentru că nu coincide nici cu data primirii facturii, nici cu data plății.

## Temeiul legal

::: ghid-temei
„CF art. 284 alin. (1)-(2) — Faptul generator la AIC = data la care ar interveni la o livrare similară în statul membru al achiziției; exigibilitatea = data facturii furnizorului (sau autofactura art. 319 alin. 9), cel târziu a 15-a zi a lunii următoare celei a faptului generator.” — `cod_fiscal_227_2015_consolidat.txt` L17785-17793, dosarul F050.
:::

Mecanismul are doi timpi. Întâi, faptul generator — de regulă, data livrării bunurilor. Apoi, exigibilitatea: dacă furnizorul emite factura înainte de a 15-a zi a lunii următoare faptului generator, exigibilitatea e data facturii; dacă nu emite factura până atunci, exigibilitatea „cade” automat pe a 15-a zi a lunii următoare — indiferent când sosește ulterior factura.

## Ce se greșește în practică

- Se ia data primirii facturii (sau data înregistrării în contabilitate) drept dată de exigibilitate — legea nu se raportează la niciuna dintre ele.
- Se așteaptă factura la nesfârșit pentru a înregistra operațiunea, în loc să se aplice termenul limită de 15 zile din lună următoare atunci când factura întârzie.
- Se ignoră decalajele legitime față de partenerul din UE (state membre cu reguli de exigibilitate diferite) și se încearcă „alinierea” cifrelor prin rectificare, deși diferența nu e o eroare.

## Ce face iConta.eu

Ecranul de achiziție intracomunitară are un câmp opțional de „dată faptul generator”, cu ajutor explicit în interfață: „Gol = încadrare pe data facturii. Completat = exigibilitate MIN(dată factură, ziua 15 luna următoare) — art. 284.” Regula celor 15 zile se aplică automat pe baza acestui câmp, fără calcul manual din partea contabilului.

[iConta.eu](/)
