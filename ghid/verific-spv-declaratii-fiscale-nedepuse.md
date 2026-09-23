---
title: Cum verific în SPV dacă am declarații fiscale nedepuse?
description: SPV e sistemul ANAF, nu iConta.eu — istoricul real al depunerilor se vede acolo. Semaforul iConta oferă o verificare independentă, din contabilitatea firmei, nu o citire a SPV.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum verific în SPV dacă am declarații fiscale nedepuse?

SPV (Spațiul Privat Virtual) e platforma proprie a ANAF — acolo se văd, cu certitudine, declarațiile efectiv înregistrate la stat, cu recipisele lor. E important de clarificat de la început: iConta.eu nu citește SPV și nu preia istoricul de depuneri de acolo. Ce oferă iConta e o verificare independentă, calculată din contabilitatea firmei, comparată cu ce ai confirmat manual că ai depus.

## Temeiul legal

::: ghid-temei
„comunicarea prin mijloace electronice de transmitere la distanţă se realizează prin intermediul serviciului «Spaţiul privat virtual» - serviciu de distribuţie electronică înregistrată care permite transmiterea de date între terţi prin mijloace electronice şi furnizează dovezi referitoare la manipularea datelor transmise, inclusiv dovezi privind trimiterea şi primirea datelor..."

*(OMFP nr. 660/2017 privind aprobarea Procedurii de comunicare prin mijloace electronice, art. 2)*
:::

## Cum verifici direct în SPV

Pentru istoricul oficial al depunerilor, intri în SPV cu certificatul digital sau credențialele contului, la secțiunea de mesaje/istoric declarații — acolo apar, cu recipisă, toate declarațiile efectiv transmise către ANAF, indiferent de aplicația din care au fost generate.

## Ce oferă, diferit, iConta.eu

Semaforul de conformare fiscală (F022) nu se conectează la SPV pentru a citi ce ai depus deja — verificat la sursă, aplicația nu are, la acest moment, un API de transmitere/interogare directă a declarațiilor la ANAF (rămâne depunere manuală în SPV, cu indexul de recipisă înregistrat ulterior în aplicație). Ce face în schimb: calculează, din contabilitatea și profilul fiscal ale firmei, ce declarații ar trebui să existe pentru fiecare perioadă, apoi compară acest calcul cu declarațiile pe care contabilul le-a marcat manual ca „depuse" (cu indexul SPV al recipisei) în fluxul de validare patru-ochi.

## Ce se greșește în practică

- Se presupune că starea „verde"/„la zi" din semaforul iConta echivalează cu o confirmare directă din SPV — de fapt reflectă doar ce a fost marcat manual ca depus în aplicație, nu o interogare live a ANAF.
- Se renunță la verificarea periodică directă în SPV, considerând semaforul intern un substitut complet — cele două sunt complementare, nu interschimbabile: unul arată ce spune calculul contabil, celălalt ce spune efectiv ANAF.

## Ce face iConta.eu

Motorul F022 (`core/control_fiscal_api.py`) marchează roșu orice declarație pentru care termenul a trecut și nu există o confirmare de depunere înregistrată în aplicație — dar acea confirmare vine din marcarea manuală (cu indexul SPV al recipisei), nu dintr-o citire automată a SPV. Fluxul de validare al declarațiilor din iConta.eu (F019, „Coada de validare patru-ochi") duce fiecare declarație prin stări controlate — pregătită, aprobată sau respinsă cu motiv, apoi depusă, cu indexul de recipisă SPV înregistrat manual la acest ultim pas — dar aplicația nu interoghează SPV pentru a confirma independent depunerea. Pentru certitudinea absolută a ce a fost efectiv transmis la ANAF, verificarea directă în SPV rămâne pasul de referință.

[iConta.eu](/)
