---
title: Cum raportez în D394 operațiunile din sistemul TVA la încasare
description: TVA la încasare schimbă doar momentul de exigibilitate al taxei (art. 282 CF); în D394, facturile cu mențiunea „TVA la încasare” se raportează în perioada emiterii (livrări), respectiv a primirii (achiziții), indiferent de data exigibilității.
published: 2026-09-24
modified: 2026-10-13
poarta: v1
---

# Cum raportez în D394 operațiunile din sistemul TVA la încasare

Cea mai frecventă greșeală la D394 pentru firmele cu TVA la încasare: se așteaptă încasarea facturii ca să fie inclusă în declarație. Regula e opusă — D394 urmărește **factura** (emisă sau primită în perioada de raportare), nu exigibilitatea taxei.

## Temeiul legal

::: ghid-temei
**Art. 282 alin. (3) din Codul fiscal (Legea 227/2015)**: *„Prin excepție de la prevederile alin. (1) și alin. (2) lit. a), exigibilitatea taxei intervine la data încasării contravalorii integrale sau parțiale a livrării de bunuri ori a prestării de servicii, în cazul persoanelor impozabile care optează în acest sens..."*

„Declaraţia trebuie să conţină facturile care au fost emise în perioada de raportare, inclusiv cele care au înscrisă menţiunea "taxare inversă" sau "TVA la încasare", indiferent de data la care intervine exigibilitatea TVA.”
— OPANAF 2194/2025, Anexa 2 pct. 1 lit. a) (sursă: [OPANAF nr. 2194/2025 pentru modificarea OPANAF nr. 3769/2015 (declarația informativă D394)](https://legislatie.just.ro/Public/DetaliiDocument/302310))

„Declaraţia trebuie să conţină facturile care au fost primite în perioada de raportare, indiferent de data la care intervine exigibilitatea TVA, inclusiv cele care au înscrisă menţiunea "taxare inversă" sau "TVA la încasare" [...]”
— OPANAF 2194/2025, Anexa 2 pct. 1 lit. b) (sursă: [OPANAF nr. 2194/2025 pentru modificarea OPANAF nr. 3769/2015 (declarația informativă D394)](https://legislatie.just.ro/Public/DetaliiDocument/302310))
:::

## Ce e sigur

TVA la încasare (art. 282 alin. (3)) modifică exclusiv **momentul** la care taxa devine exigibilă — nu modifică factura în sine, valoarea operațiunii, părțile implicate sau natura ei. În decontul de TVA (D300) nu există un rând separat „TVA la încasare”: sumele unei firme cu TVA la încasare ajung tot în rândurile obișnuite de TVA colectată; regimul de exigibilitate schimbă doar perioada în care suma apare în decont, nu structura raportării.

În D394 criteriul e altul, fixat de instrucțiunile formularului:

- **Livrări/prestări (furnizor):** intră facturile **emise** în perioada de raportare, inclusiv cele cu mențiunea „TVA la încasare”, indiferent de data exigibilității. Dacă emiți în septembrie o factură cu „TVA la încasare”, ea intră în D394 pe septembrie — chiar dacă încasarea (și, odată cu ea, exigibilitatea taxei) se produce abia în noiembrie sau nu se produce deloc în acel an.
- **Achiziții (client):** intră facturile **primite** în perioada de raportare, indiferent de data exigibilității, inclusiv cele cu „TVA la încasare”.

D394 e o declarație informativă de tranzacții (cine a facturat cui, cât), nu o declarație de TVA de plată; de aceea urmărește documentul, nu fluxul de numerar. Formularul marchează totuși distinct regimul: în secțiunea 1 se completează căsuța „sistem de TVA la încasare” dacă firma care depune a optat pentru acest sistem, iar la achiziții, pe lângă tipurile de operațiune L/A, există tipul **AÎ** — „achiziții de la persoane impozabile care aplică sistemul de TVA la încasare”.

Achizițiile intracomunitare care se raportează în D390 nu se înscriu și în D394 — instrucțiunile exclud explicit acest dublaj.

## Ce rămâne de verificat

La data acestui ghid nu putem confirma, pentru D394 generată de iConta.eu:

- dacă bifa „sistem de TVA la încasare” și tipul de operațiune AÎ se completează automat;
- dacă perioada în care apar facturile cu „TVA la încasare” urmează data facturii, cum cer instrucțiunile.

Nu prezentăm niciunul din aceste puncte ca fiind confirmat.

## Ce se greșește în practică

- **Se amână raportarea în D394 până la încasare**, prin analogie greșită cu mecanismul TVA la încasare din D300 — criteriul D394 e data facturii.
- **Se presupune, fără verificare, că D394 urmează automat regimul de exigibilitate din D300.** Cele două declarații au reguli de raportare diferite.
- La reconcilierea D394 cu jurnalul de vânzări/cumpărări se filtrează după data plății, nu după data documentului — apar diferențe care nu sunt erori, ci o confuzie de criteriu.
- Mențiunea „TVA la încasare” lipsește de pe factură, iar operațiunea nu mai poate fi identificată corect nici la furnizor, nici la client.

## Ce face iConta.eu

La data acestui ghid nu putem confirma dacă și cum aplicația tratează distinct operațiunile supuse TVA la încasare în D394. Înainte de depunere, verifică pe declarația generată bifa „sistem de TVA la încasare”, tipul AÎ la achizițiile de la furnizori cu TVA la încasare și perioada facturilor, sau cere confirmarea echipei de suport înainte de a considera un comportament ca fiind automatizat.

[iConta.eu](/)
