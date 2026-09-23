---
title: "e-Factura pentru încasări cu cardul: cum se emite"
description: Modul de plată (card sau numerar) nu schimbă mecanismul de emitere sau obligația de transmitere prin RO e-Factura — dar plata simultană cu livrarea are o consecință specifică dacă factura nu ajunge la timp în sistem.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# e-Factura pentru încasări cu cardul: cum se emite

O întrebare frecventă, cu un răspuns simplu la bază: cardul e doar un mijloc de plată, nu o categorie separată de facturare. Ce contează pentru e-Factura e cine e clientul și dacă operațiunea are locul în România — nu cum s-a achitat.

## Temeiul legal

::: ghid-temei
„În relaţia comercială B2B, între persoane impozabile stabilite în România conform art. 266 alin. (2) din Legea nr. 227/2015, ... emitentul facturii electronice are obligaţia de transmitere a acesteia către destinatar utilizând sistemul naţional privind factura electronică RO e-Factura, cu respectarea prevederilor art. 4 alin. (1). Fac excepţie facturile simplificate emise conform art. 319 alin. (12) din Legea nr. 227/2015." — OUG nr. 120/2021, art. 10 alin. (1), forma modificată prin Legea nr. 296/2023, art. LXV pct. 4.
:::

## Emiterea propriu-zisă e identică, indiferent de plată

O factură emisă la o încasare cu cardul se generează și se trimite prin exact același mecanism ca oricare alta: generare XML, validare la validatorul public ANAF, verificare că nu există deja o trimitere activă pentru ea, apoi upload. Nu există un tratament tehnic separat pentru „factură plătită cu cardul" — sistemul nu distinge, la nivel de structură, modul de plată.

Ce contează efectiv pentru obligația de transmitere prin e-Factura: dacă factura e emisă către o persoană impozabilă (B2B), obligația e clară și se aplică indiferent de plată. Facturile simplificate emise potrivit art. 319 alin. (12) din Codul fiscal fac excepție de la obligația B2B — dar verifică la sursă dacă documentul tău se încadrează efectiv în acea categorie, pragul și condițiile exacte fiind stabilite de acel articol.

## Vânzarea cu amănuntul, către client neidentificat

Dacă plata cu cardul e o vânzare la casa de marcat, către un client persoană fizică neidentificat, pentru care se emite bon fiscal, nu se naște obligație de e-Factura. **Dacă însă clientul cere factură**, factura respectivă intră în sistem ca oricare alta.

## Când plata e simultană cu livrarea, iar factura întârzie

Situația specifică plăților pe loc — la benzinărie, service, magazin — e exact cea pentru care există procedura formularului 800: dacă plata s-a făcut integral la momentul livrării/prestării, iar factura nu apare în RO e-Factura după expirarea termenului legal de transmitere, beneficiarul poate notifica ANAF prin acest formular, iar emitentul primește obligația să transmită factura electronic în ziua următoare. Formularul nu se aplică pentru plăți în avans, doar pentru plata simultană cu livrarea — exact tiparul unei încasări pe loc, cu cardul.

## Ce se greșește în practică

- Se caută în aplicație o „cale specială" de emitere pentru facturile plătite cu cardul — nu există, mecanismul de generare și trimitere e identic pentru orice factură.
- Se presupune că o factură emisă la o vânzare cu plata pe loc e automat scutită de e-Factura — depinde de cine e clientul (persoană impozabilă sau neidentificată la bon fiscal), nu de metoda de plată.
- Se ignoră formularul 800 ca soluție atunci când furnizorul nu transmite factura la timp pentru o plată simultană cu livrarea — beneficiarul are o cale formală, nu doar așteptarea.

## Ce face iConta.eu

Generează și trimite orice factură prin același flux — validare la ANAF, verificare anti-dublare, upload — indiferent de metoda de plată înregistrată pe document. Nu distinge separat „factură cu plata cardului" ca o categorie de produs, pentru că legea nu o face nici ea.

[iConta.eu](/)
