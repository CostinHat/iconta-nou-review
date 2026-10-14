---
title: "Cum se stabilește exigibilitatea TVA la o achiziție intracomunitară?"
description: "Exigibilitatea e data facturii furnizorului, dar niciodată mai târziu de a 15-a zi a lunii următoare celei în care a avut loc livrarea (faptul generator) — art. 284 din Codul fiscal."
published: 2026-09-26
modified: 2026-10-13
poarta: v1
---

# Cum se stabilește exigibilitatea TVA la o achiziție intracomunitară?

Data exigibilității decide luna în care operațiunea intră în decont și în D390 — și e cea mai frecventă sursă de confuzie la achizițiile intracomunitare, pentru că nu coincide nici cu data primirii facturii, nici cu data plății.

Mecanismul are doi timpi. Întâi, faptul generator — de regulă, data livrării bunurilor. Apoi, exigibilitatea: dacă furnizorul emite factura înainte de a 15-a zi a lunii următoare faptului generator, exigibilitatea e data facturii; dacă nu emite factura până atunci, exigibilitatea „cade” automat pe a 15-a zi a lunii următoare — indiferent când sosește ulterior factura.

## Temeiul legal

::: ghid-temei
„(1) În cazul unei achiziții intracomunitare de bunuri, faptul generator intervine la data la care ar interveni faptul generator pentru livrări de bunuri similare, în statul membru în care se face achiziția. (2) În cazul unei achiziții intracomunitare de bunuri, exigibilitatea taxei intervine la data emiterii facturii prevăzute în legislația altui stat membru la articolul care transpune prevederile art. 222 din Directiva 112 sau, după caz, la data emiterii autofacturii prevăzute la art. 319 alin. (9) ori în cea de-a 15-a zi a lunii următoare celei în care a intervenit faptul generator, dacă nu a fost emisă nicio factură/autofactură până la data respectivă.”
— Legea nr. 227/2015 privind Codul fiscal, art. 284 alin. (1) și (2) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))

„(1) Orice persoană impozabilă înregistrată în scopuri de TVA conform art. 316 sau 317 trebuie să întocmească și să depună la organele fiscale competente o declarație recapitulativă în care menționează: [...] d) achizițiile intracomunitare de bunuri taxabile, pentru care exigibilitatea de taxă a luat naștere în luna calendaristică respectivă;”
— Legea nr. 227/2015 privind Codul fiscal, art. 325 alin. (1) lit. d) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))
:::

## Ce se greșește în practică

- Se ia data primirii facturii (sau data înregistrării în contabilitate) drept dată de exigibilitate — legea nu se raportează la niciuna dintre ele.
- Se așteaptă factura la nesfârșit pentru a înregistra operațiunea, în loc să se aplice termenul limită de 15 zile din lună următoare atunci când factura întârzie.
- Se ignoră decalajele legitime față de partenerul din UE (state membre cu reguli de exigibilitate diferite) și se încearcă „alinierea” cifrelor prin rectificare, deși diferența nu e o eroare.

## Ce face iConta.eu

Ecranul de achiziție intracomunitară are un câmp opțional de „dată faptul generator”, cu ajutor explicit în interfață: „Gol = încadrare pe data facturii. Completat = exigibilitate MIN(dată factură, ziua 15 luna următoare) — art. 284.” Regula celor 15 zile se aplică automat pe baza acestui câmp, fără calcul manual din partea contabilului.

[iConta.eu](/)
