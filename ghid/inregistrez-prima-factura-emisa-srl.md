---
title: Cum înregistrez prima factură emisă de un SRL?
description: Prima factură a unui SRL se contabilizează simplu — clientul se debitează cu suma totală, venitul și TVA se creditează separat — dar TVA apare pe factură doar dacă firma e deja înregistrată în scopuri de TVA la data emiterii.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum înregistrez prima factură emisă de un SRL?

Mecanismul contabil pentru orice factură de vânzare e același, indiferent dacă e prima sau a suta — diferența pentru un SRL la început de drum e că trebuie clarificat întâi dacă firma e sau nu înregistrată în scopuri de TVA la data emiterii.

## Temeiul legal

::: ghid-temei
**Codul fiscal, art. 316 alin. (1^1)**: înregistrarea în scopuri de TVA se consideră valabilă începând cu:
- „**data înregistrării fiscale**" sau, pentru firmele care solicită simultan înmatricularea și înregistrarea de TVA, „**data înregistrării [...] în registrul comerţului**";
- „**data depăşirii plafonului de scutire**" prevăzut la art. 310 alin. (1), pentru firmele care devin plătitoare prin depășirea plafonului;
- „**data solicitării**", pentru cazurile de opțiune expresă;
- „**a 5-a zi următoare**" solicitării, pentru alte cazuri de înregistrare prin opțiune.
:::

Data de la care factura trebuie să conțină TVA depinde exact de motivul înregistrării — nu există o singură dată universală „valabilă pentru toată lumea". Un SRL nou-înființat poate fi, la prima factură, fie deja înregistrat în scopuri de TVA (dacă a optat de la înființare), fie neplătitor de TVA (regim obișnuit pentru firmele mici la început) — iar factura arată diferit în cele două cazuri.

Mecanismul contabil, indiferent de regimul de TVA:
- pentru o factură **cu** TVA: clientul (4111) se debitează cu suma totală; venitul (701/703/704/707, după natura operațiunii) se creditează cu baza; TVA colectată (4427, sau 4428 dacă firma aplică TVA la încasare) se creditează cu suma taxei.
- pentru o factură **fără** TVA (firmă neplătitoare): clientul se debitează cu suma totală, venitul se creditează integral, fără nicio linie de TVA.

## Ce se greșește în practică

- Se emit facturi cu TVA înainte ca înregistrarea în scopuri de TVA să fie efectiv valabilă la data respectivă, conform art. 316 alin. (1^1) — de verificat data exactă, nu doar faptul că firma „a depus cererea".
- Se presupune că orice SRL nou trebuie automat să factureze cu TVA — greșit dacă firma nu e (încă) înregistrată în scopuri de TVA.
- Se introduce manual o cotă de TVA pe o factură fără să se verifice dacă firma era înregistrată la data emiterii — aplicația nu blochează introducerea unei cote pe o factură dacă firma nu e (încă) înregistrată de TVA; verificarea rămâne responsabilitatea contabilului.

## Ce face iConta.eu

Motorul de contare al iConta.eu generează automat nota contabilă pentru orice factură emisă: clientul (4111) debitat cu totalul, venitul creditat cu baza, iar TVA colectată (4427 sau 4428, după opțiunea de TVA la încasare) creditată cu suma taxei, dacă factura are linii cu cotă de TVA.

Verificarea datei de la care firma e efectiv înregistrată în scopuri de TVA, conform art. 316 alin. (1^1), nu e făcută automat la contarea facturii — indiferent dacă e prima factură a firmei sau nu, corectitudinea cotei introduse pe fiecare linie rămâne o verificare pe care o face contabilul, pe baza datei reale de înregistrare de TVA a firmei.

[iConta.eu](/)
