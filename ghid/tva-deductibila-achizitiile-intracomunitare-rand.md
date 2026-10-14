---
title: "TVA deductibilă la achizițiile intracomunitare: rând în D300"
description: Pentru achizițiile intracomunitare de bunuri cu taxare inversă, rândul deductibil 20 se derivă automat din factură. Panoul manual din „Rând manual D300” intervine doar pentru regularizări (rândul 21) sau când operațiunea n-a fost captată corect automat.
published: 2026-09-23
modified: 2026-10-13
poarta: v1
---

# TVA deductibilă la achizițiile intracomunitare: rând în D300

Rândul deductibil pentru achizițiile intracomunitare de bunuri cu taxare inversă e rândul 20 din formularul D300. În marea majoritate a cazurilor nu trebuie introdus manual — se derivă automat din factură. Mai jos, ce e automat, ce e manual și când intervine panoul „Rând manual D300”.

## Temeiul legal

::: ghid-temei
„Persoana care efectuează o achiziție intracomunitară de bunuri care este taxabilă, conform prezentului titlu, este obligată la plata taxei.”
— Legea nr. 227/2015 privind Codul fiscal, art. 308 alin. (1) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))

„Pentru exercitarea dreptului de deducere a taxei, persoana impozabilă trebuie să îndeplinească următoarele condiții: [...] e) pentru taxa aferentă unei achiziții intracomunitare de bunuri, să dețină o factură sau documentul prevăzut la art. 320 alin. (1);”
— Legea nr. 227/2015 privind Codul fiscal, art. 299 alin. (1) lit. e) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))
:::

## Ce se derivă automat

Pentru facturile de achiziție cu partener din UE („țara partenerului” în spațiul UE), motorul D300 derivă automat, fără nicio intervenție manuală: rândul 5 la taxa colectată (bază și TVA) și oglinda deductibilă de la rândul 20 (bază și TVA), la cota internă standard — mecanismul de taxare inversă (autolichidare) aplicat direct pe factura de achiziție.

## Ce e strict manual, prin „Rând manual D300”

Rândul 21 — „Regularizări privind achizițiile intracomunitare de bunuri pentru care cumpărătorul este obligat la plata TVA (taxare inversă)" — intră doar în totalul taxei deductibile (rândul 30); aplicația nu îl completează niciodată automat. E 100% manual: orice regularizare ulterioară a unei achiziții IC deja înregistrate se introduce prin panoul „Rând manual D300”, pe rândul 21.

## Fallback: când factura nu a captat corect operațiunea

Dacă achiziția intracomunitară nu a fost captată corect de nicio factură (partener fără CUI IC recunoscut, „țara partenerului” sau clasificare lipsă), gărzile anti-dublă-numărare permit introducerea manuală a rândului 20 (împreună cu oglinda colectată de la rândul 5) prin „Rând manual D300” — dar **doar dacă** operațiunea nu a fost deja derivată automat din facturile perioadei. Dacă a fost, motorul ridică o eroare explicită de dublă numărare, care numește ambele surse.

## Ce se greșește în practică

- Se introduce manual rândul 20 pentru o achiziție deja captată automat dintr-o factură cu partener UE — aplicația respinge cererea, cu mesaj pe câmpul rândului, pentru că ar dubla suma deja derivată.
- Se confundă rândul 20 (rândul de bază, derivat automat) cu rândul 21 (regularizarea lui, exclusiv manuală).

## Ce face iConta.eu

Aplicația derivă automat rândurile 5 și 20 din facturile de achiziție cu partener din UE, la cota internă standard, fără intervenție manuală. Panoul „Rând manual D300” acoperă doar regularizările (rândul 21) și cazurile de fallback în care operațiunea nu a fost captată corect automat — cu validare explicită împotriva dublei numărări față de ce a fost deja derivat din facturile perioadei.

[iConta.eu](/)
