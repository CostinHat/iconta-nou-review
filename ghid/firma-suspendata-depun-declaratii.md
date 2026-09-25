---
title: "Firmă suspendată: mai depun declarații"
description: "Ce se întâmplă cu obligațiile declarative ale unei firme cu mențiune de inactivitate temporară la registrul comerțului — scutirea nu este totală și nu e retroactivă."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Firmă suspendată: mai depun declarații

Înscrierea mențiunii de inactivitate temporară la registrul comerțului nu oprește imediat și complet toate obligațiile declarative ale firmei. Răspunsul scurt: pentru perioada de suspendare propriu-zisă, nu — dar cu excepții importante legate de moment și de obligațiile anterioare.

## Temeiul legal

::: ghid-temei
„(4^1) Entitățile înregistrate în registrul comerțului, pentru care există înscrise mențiuni privind inactivitatea temporară, nu au obligația depunerii declarațiilor fiscale pentru perioada în care se află în inactivitate temporară, începând cu data de 1 a lunii următoare înscrierii mențiunii privind inactivitatea temporară în registrul comerțului. [...] (4^3) Aplicarea prevederilor alin. (4^1) și (4^2) încetează la data reluării activității sau la împlinirea unui termen de 3 ani de la data înregistrării în registrul comerțului a mențiunii privind inactivitatea temporară sau a mențiunii privind suspendarea activității în registrul contribuabililor. (4^4) Obligațiile de declarare, aferente activității desfășurate anterior înregistrării inactivității temporare/suspendării, se mențin."
— Legea 207/2015 (Codul de procedură fiscală), art. 101 alin. (4^1), (4^3), (4^4) (sursă: anaf_surse/legea_207_2015_consolidat.txt)

„d) inactivitatea temporară înscrisă la registrul comerțului;"
— Legea 207/2015 (Codul de procedură fiscală), art. 92 alin. (1) lit. d) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Din text rezultă două reguli distincte:

- Entitățile înregistrate la registrul comerțului (inclusiv SRL) cu mențiune de inactivitate temporară nu au obligația depunerii declarațiilor fiscale pentru perioada de inactivitate, **începând cu data de 1 a lunii următoare** celei în care a fost înscrisă mențiunea. Scutirea nu e permanentă — încetează fie la reluarea activității, fie, cel târziu, după 3 ani de la înscrierea mențiunii.
- Obligațiile de declarare aferente activității desfășurate **anterior** înregistrării inactivității temporare rămân valabile — orice declarație scadentă pentru o perioadă în care firma încă funcționa normal trebuie depusă, indiferent dacă termenul ei de depunere cade după data suspendării.

Practic, scutirea privește doar declarațiile pentru perioada de inactivitate efectivă, nu un efect retroactiv asupra obligațiilor mai vechi.

## Ce se greșește în practică

- Se presupune că suspendarea „resetează" toate obligațiile restante, inclusiv pe cele din perioada anterioară — fals, obligațiile din perioada de activitate normală rămân scadente.
- Se depune mențiunea la ONRC, dar se ratează corelarea cu data de la care începe efectiv scutirea (1 a lunii următoare înscrierii) — rezultatul e fie o declarație omisă în luna în care firma încă datora, fie panica pentru o lună în care de fapt obligația chiar mai exista.
- Se crede că scutirea e nelimitată în timp, deși curge un termen maxim (reluarea activității sau 3 ani, ce survine primul).
- Se ignoră că, dacă firma continuă în fapt să desfășoare activitate economică sub mențiunea de inactivitate, obligațiile de declarare și plată nu dispar.

## Ce face iConta.eu

Trebuie spus onest: mecanismul din spatele generării declarațiilor fiscale în iConta (rutare, validare de formă, generare XML pentru cele ~50 de tipuri de declarații pe care aplicația le poate produce) nu are nicio cunoștință proprie despre statutul de inactivitate al unei firme la ONRC sau la ANAF, și nu decide singur ce declarații datorează o firmă. Aplicația nu inițiază, nu înregistrează și nu urmărește automat o mențiune de inactivitate temporară — cine trebuie să decidă dacă o declarație se mai depune sau nu, pentru o firmă suspendată, rămâne contabilul, aplicând regula de mai sus.

Ce compară totuși aplicația, indiferent de statutul de suspendare: modulul de conformitate fiscală urmărește diferența dintre declarațiile pe care o firmă le datorează (după profilul ei — TVA, salariați, regim de impozitare) și cele efectiv depuse, semnalând scadențele neonorate. Dacă firma e suspendată și scutită conform regulii de mai sus, contabilul trebuie să știe asta separat — aplicația nu retrage automat din calendar declarațiile pentru care a intervenit scutirea de inactivitate.

[iConta.eu](/)
