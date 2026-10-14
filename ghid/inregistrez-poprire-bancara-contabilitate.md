---
title: "Cum înregistrez o poprire bancară în contabilitate?"
description: "Ce înseamnă indisponibilizarea sumelor din cont printr-o poprire fiscală și cum apare, în practică, o astfel de operațiune pe extrasul bancar din iConta.eu."
published: 2026-09-24
modified: 2026-10-13
poarta: v1
---

# Cum înregistrez o poprire bancară în contabilitate?

Poprirea bancară e o măsură de executare silită prin care organul fiscal indisponibilizează sumele din contul unei firme debitoare, direct la bancă, fără intervenția instanței. Pentru contabil, ea nu e o factură și nu vine de la un partener comercial — apare pe extras ca o reținere sau un transfer către trezorerie, cu o descriere specifică băncii, și trebuie tratată corect ca operațiune distinctă, nu ca o plată obișnuită.

## Temeiul legal

::: ghid-temei
„(12) Pentru stingerea creanțelor fiscale, debitorii titulari de conturi bancare pot fi urmăriți prin poprire asupra sumelor din conturile bancare, prevederile alin. (5) aplicându-se în mod corespunzător."
— Legea 207/2015 (Codul de procedură fiscală), art. 236 alin. (12) (sursă: [Legea nr. 207/2015 privind Codul de procedură fiscală](https://legislatie.just.ro/Public/DetaliiDocument/170007))

„(13) În măsura în care este necesar, pentru achitarea sumei datorate la data sesizării instituției de credit, [...] sumele existente, precum și cele viitoare provenite din încasările zilnice în conturile în lei și în valută sunt indisponibilizate în limita sumei necesare [...]. Instituțiile de credit au obligația să plătească sumele indisponibilizate în contul indicat de organul de executare silită în termen de 3 zile lucrătoare de la indisponibilizare.
(14) Din momentul indisponibilizării [...], instituțiile de credit nu procedează la decontarea documentelor de plată primite, respectiv la debitarea conturilor debitorilor și nu acceptă alte plăți din conturile acestora până la achitarea integrală a obligațiilor fiscale înscrise în adresa de înființare a popririi, cu excepția: a) sumelor necesare plății drepturilor salariale, inclusiv a impozitelor și contribuțiilor aferente acestora, reținute la sursă [...]"
— Legea 207/2015 (Codul de procedură fiscală), art. 236 alin. (13)-(14) lit. a) (sursă: [Legea nr. 207/2015 privind Codul de procedură fiscală](https://legislatie.just.ro/Public/DetaliiDocument/170007))
:::

Alte elemente relevante ale mecanismului, verificate în același articol:

- Adresa de înființare se comunică direct băncii (terțul poprit), firma fiind doar înștiințată (art. 236 alin. (5)); poprirea se consideră **înființată din momentul primirii adresei** de către bancă (alin. (8)), nu de la data emiterii ei și nici de când află contabilul de ea.
- Odată înființată, poprirea acoperă și **sumele viitoare** din încasările zilnice, nu doar soldul existent la momentul comunicării (alin. (13)) — practic, banca reține și ce intră ulterior în cont, până la stingerea integrală a datoriei.
- Banca are **3 zile lucrătoare** de la indisponibilizare pentru a vira sumele în contul indicat de organul de executare silită (alin. (13)) — ce apare pe extras e, de regulă, deja virarea efectivă către buget, nu doar un blocaj.
- **Excepția salariilor**: banca poate totuși deconta sumele necesare plății drepturilor salariale nete, cu impozitele și contribuțiile aferente, dacă debitorul declară pe propria răspundere că nu are alte disponibilități (alin. (14) lit. a)) — o poprire nu blochează, deci, automat plata salariilor. Tot ca excepții, banca decontează și plata accizelor de către antrepozitarii autorizați și plata obligațiilor fiscale de care depinde menținerea unei înlesniri la plată (alin. (14) lit. b) și d)).
- Poprirea **nu e supusă validării** (alin. (6)) — produce efecte de îndată, spre deosebire de alte măsuri asigurătorii.

## Ce se greșește în practică

- Se tratează suma reținută prin poprire ca pe o plată obișnuită către un „furnizor", pierzând legătura cu obligația fiscală restantă pe care o stinge de fapt.
- Nu se identifică exact datoria fiscală stinsă prin poprire (TVA, impozit pe profit, contribuții etc.) — fără ea, nota contabilă nu poate închide corect obligația respectivă în evidență.
- Se amână înregistrarea până la o „notificare separată", deși suma poate apărea direct debitată din cont — banca nu așteaptă confirmarea firmei înainte de a executa.
- Se așteaptă o factură sau un document de la bancă pentru a justifica operațiunea — actul justificativ real e adresa de înființare a popririi, comunicată de organul fiscal, nu un document emis de bancă.
- Se confundă poprirea executorie (pentru o creanță fiscală deja stabilită și scadentă) cu poprirea asigurătorie (măsură preventivă, înainte de stabilirea definitivă a creanței) — regimul sumelor acceptate la plată diferă între cele două (art. 236 alin. (7) și alin. (15)).

## Ce face iConta.eu

O poprire bancară ajunge pe extrasul de cont ca o linie de ieșire, de regulă fără CUI de partener în descriere și fără o factură deschisă asociată. La reconcilierea bancară, iConta.eu caută în descrierea fiecărei linii CUI-ul unui partener ca s-o potrivească cu o factură emisă sau primită; fără CUI, potrivirea automată nu se încearcă deloc și linia apare cu status **roșu** (nepotrivită). Aplicația recunoaște din descrierea liniei comisioanele, dobânzile, creditele, salariile, impozitul pe profit, TVA-ul sau numerarul și propune pentru ele o notă contabilă, dar nu recunoaște poprirea ca tip distinct de operațiune.

Practic, linia rămâne pe roșu, iar contabilul o clarifică printr-o **notă contabilă manuală** din Jurnal (nu prin înregistrarea automată din reconciliere), stingând obligația fiscală restantă (de regulă pe contul de datorii bugetare corespunzător) din contul de trezorerie/disponibilități, folosind ca document justificativ adresa de înființare a popririi primită de la organul fiscal, nu extrasul bancar singur.

[iConta.eu](/)
