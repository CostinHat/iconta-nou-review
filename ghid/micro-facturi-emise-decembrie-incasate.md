---
title: "Micro cu facturi emise în decembrie, încasate în ianuarie"
description: "Impozitul pe veniturile microîntreprinderilor se calculează pe veniturile recunoscute la data facturării, nu la data încasării, ceea ce contează la trecerea dintre doi ani fiscali."
published: 2026-09-26
modified: 2026-10-13
poarta: v1
---

# Micro cu facturi emise în decembrie, încasate în ianuarie

O microîntreprindere care emite o factură pe 20 decembrie și încasează contravaloarea abia în ianuarie anul următor se întreabă firesc în ce an fiscal „intră" venitul respectiv. Răspunsul contează dublu: pentru trimestrul în care se calculează impozitul de 1% și pentru verificarea plafonului anual de venituri care condiționează rămânerea în sistemul micro. Legea dă un răspuns clar, care nu depinde deloc de momentul încasării.

## Temeiul legal

::: ghid-temei
„Baza impozabilă a impozitului pe veniturile microîntreprinderilor o constituie veniturile din orice sursă, din care se scad: [...]"
— Legea nr. 227/2015 (Codul fiscal), Titlul III, art. 53 alin. (1) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))
:::

- Baza de calcul a impozitului micro sunt **veniturile din orice sursă**, așa cum sunt ele înregistrate potrivit reglementărilor contabile — adică la data facturării (venituri realizate, în accepțiunea contabilă), nu la data încasării banilor. Legea nu condiționează recunoașterea veniturilor la calculul impozitului micro de plata efectivă.
- Aceeași logică guvernează și verificarea plafonului anual: la art. 47 alin. (1) lit. c), condiția de a rămâne microîntreprindere este „a realizat venituri care nu au depășit echivalentul în lei a 100.000 euro" — venituri *realizate*, adică înregistrate contabil în anul respectiv, nu încasate.
- O factură emisă pe 20 decembrie intră, prin urmare, în baza de impozitare a trimestrului IV al anului în care a fost emisă și în plafonul anual al acelui an, indiferent dacă banii ajung în cont în decembrie sau abia în ianuarie anul următor.

## Ce se greșește în practică

- Se confundă regimul de recunoaștere a veniturilor la impozitul micro (pe bază de facturare/contabilitate) cu regimul „TVA la încasare" — care e o facilitate separată, aplicabilă doar plătitorilor de TVA înregistrați în acest scop, și privește exclusiv taxa pe valoarea adăugată, nu impozitul pe venitul microîntreprinderii.
- Facturile emise în ultimele zile din decembrie sunt uneori „uitate" la calculul plafonului anual de 100.000 euro, sub argumentul greșit că, necăsând-se până la 31 decembrie, nu s-ar mai fi „realizat" în anul respectiv.
- Se amână greșit calculul și declararea impozitului aferent trimestrului IV până la încasarea facturii, ceea ce poate genera întârzieri la plată și, implicit, accesorii.

## Ce face iConta.eu

Pentru impozitul micro, aplicația ia baza din veniturile înregistrate în contabilitate în trimestrul respectiv (conturile de venituri 70x, 75x, 76x, minus 709), nu din încasări — deci o factură emisă și înregistrată în decembrie intră în trimestrul IV al acelui an, chiar dacă se încasează în ianuarie. Aplicația nu verifică automat plafonul anual de 100.000 euro: încadrarea în regimul micro rămâne cea completată de contabil la Date firmă (Regimul fiscal). Exportul „Export facturi emise către SAGA” doar transferă facturile deja emise, în format XML, către programul SAGA; nu calculează și nu influențează impozitul micro.

[iConta.eu](/)
