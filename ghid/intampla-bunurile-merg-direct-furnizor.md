---
title: "Ce se întâmplă dacă bunurile merg direct de la furnizor la client în alt stat UE?"
description: "Într-o tranzacție în lanț cu transport unic, direct de la primul furnizor la ultimul client, transportul se atribuie unei singure livrări din lanț — de regulă, cea către operatorul intermediar."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce se întâmplă dacă bunurile merg direct de la furnizor la client în alt stat UE?

O firmă românească cumpără bunuri de la un furnizor dintr-un stat membru și le revinde unui client din alt stat membru — dar marfa nu trece fizic prin România, ci merge direct de la furnizor la clientul final. E o tranzacție în lanț, iar legea are o regulă specifică pentru a decide cărei livrări din lanț i se atribuie transportul, deci care livrare e scutită ca intracomunitară.

## Temeiul legal

::: ghid-temei
„În cazul în care aceleași bunuri sunt livrate succesiv și sunt expediate sau transportate dintr-un stat membru în alt stat membru direct de la primul furnizor la ultimul client din lanț, expedierea sau transportul este atribuit numai livrării efectuate către operatorul intermediar. [...] Prin excepție [...] expedierea sau transportul este atribuit numai livrării de bunuri efectuate de către operatorul intermediar în cazul în care operatorul intermediar a comunicat furnizorului său codul său de înregistrare în scopuri de TVA care i-a fost eliberat de către statul membru din care sunt expediate sau transportate bunurile."
— Codul fiscal (Legea 227/2015), art. 275 alin. (9)-(10) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Regula rezolvă o problemă altfel ambiguă: cu un singur transport fizic, dar mai multe livrări „pe hârtie", doar una poate fi calificată drept livrare intracomunitară scutită:

- **Regula de bază**: transportul se atribuie livrării **către operatorul intermediar** (firma din mijlocul lanțului, care cumpără și revinde, fără să fie primul furnizor) — acea livrare e cea intracomunitară scutită; livrarea următoare, de la operatorul intermediar la clientul final, devine o livrare internă, impozabilă în statul de destinație.
- **Excepția**: dacă operatorul intermediar comunică furnizorului lui **codul de TVA din statul de plecare** al bunurilor, transportul se atribuie livrării **făcute de el** (a doua livrare din lanț) — iar prima livrare, către el, devine livrare internă în statul de plecare.
- Alegerea codului de TVA comunicat de operatorul intermediar decide, așadar, care dintre cele două livrări e scutită — o alegere cu efect direct asupra cui datorează TVA și unde.

## Ce se greșește în practică

- Se tratează greșit ambele livrări din lanț ca fiind scutite ca intracomunitare, deși regula de atribuire a transportului permite scutirea unei singure livrări din lanț.
- Operatorul intermediar comunică, din neatenție, codul de TVA din statul de destinație (nu din cel de plecare), ceea ce schimbă regula aplicabilă și poate lăsa livrarea greșit calificată.
- Nu se documentează cărei livrări îi aparține efectiv transportul (contracte de transport, Incoterms), deși de această atribuire depinde integral tratamentul de TVA al fiecărei livrări din lanț.

## Ce face iConta.eu

iConta.eu **nu determină automat** cărei livrări dintr-un lanț de tranzacții îi este atribuit transportul — încadrarea rămâne o analiză a contabilului, pe baza codurilor de TVA comunicate și a documentelor de transport. Facturile emise/primite, odată clasificate corect, sunt preluate automat în declarația recapitulativă D390, cu tipul de operațiune corespunzător (L pentru livrare intracomunitară, T pentru livrare în cadrul unei operațiuni triunghiulare).

[iConta.eu](/)
