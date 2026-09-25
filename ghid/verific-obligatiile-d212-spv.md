---
title: "Cum verific obligațiile din D212 în SPV?"
description: "Spațiul Privat Virtual (SPV) e canalul oficial prin care ANAF comunică situația fiscală proprie a contribuabilului, inclusiv obligațiile rezultate din D212 — accesarea lui e opțională, dar exclude alte moduri de comunicare."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum verific obligațiile din D212 în SPV?

Spațiul Privat Virtual nu e doar o cutie poștală electronică — e definit legal ca spațiul prin care se comunică, între contribuabil și organul fiscal, situația financiară sau fiscală proprie a acestuia, inclusiv obligațiile rezultate din declarațiile depuse, precum D212.

## Temeiul legal

::: ghid-temei
„SPV constă în punerea la dispoziţia persoanelor fizice, persoanelor juridice şi altor entităţi fără personalitate juridică a unui spaţiu virtual, aflat pe serverele Ministerului Finanţelor Publice/Agenţiei Naţionale de Administrare Fiscală, prin intermediul căruia se efectuează comunicarea electronică a informaţiilor şi înscrisurilor între Ministerul Finanţelor Publice/organul fiscal central şi persoana fizică, persoana juridică sau altă entitate fără personalitate juridică în legătură cu situaţia financiară sau fiscală proprie a acesteia."
— OMFP 660/2017, art. 1 alin. (6) (sursă: anaf_surse/omfp_660_2017.txt)

„Accesarea SPV reprezintă opţiune în sensul art. 47 alin. (3) din Legea nr. 207/2015 privind Codul de procedură fiscală [...] În cazul utilizării SPV nu se mai utilizează şi altă modalitate de comunicare a actului administrativ-fiscal."
— OMFP 660/2017, art. 1 alin. (3)-(4) (sursă: anaf_surse/omfp_660_2017.txt)
:::

Ce înseamnă practic pentru verificarea obligațiilor din D212:

- SPV e canalul prin care ANAF pune la dispoziție „fișa sintetică" a contribuabilului, unde apar obligațiile de plată rezultate din declarațiile depuse, inclusiv D212 — nu doar actele comunicate oficial, ci și alte informații deținute de minister (art. 1 alin. (2)).
- Accesarea SPV e o opțiune, nu o obligație legală — dar odată aleasă, exclude comunicarea prin altă modalitate a actelor administrative fiscale (art. 1 alin. (4)).
- Prin SPV se pot transmite și cereri sau documente către organul fiscal (art. 1 alin. (5)), deci verificarea obligațiilor din D212 poate fi urmată, dacă apare o discrepanță, de o solicitare de clarificare pe același canal.
- Autentificarea în SPV, pentru persoane fizice, se face cu certificat calificat sau alte mijloace de identificare electronică prevăzute în procedură — un pas premergător verificării propriu-zise.

## Ce se greșește în practică

- Se presupune că obligațiile afișate în SPV apar instant după depunerea D212 — procesarea declarației de către sistemele ANAF durează, iar verificarea imediat după depunere poate arăta o situație incompletă.
- Se ignoră SPV și se așteaptă o notificare pe altă cale (poștă, telefon) — odată optat pentru SPV, comunicarea oficială a actelor administrative fiscale se face exclusiv acolo.
- Se confundă „Buletinul informativ" (informații publice generale, art. 2 din OMFP 660/2017) cu fișa personală de obligații din SPV — sunt servicii diferite, cu scop diferit.

## Ce face iConta.eu

D212 e o declarație manuală în iConta.eu (`core/d212.py`) — aplicația generează fișierul declarației conform structurii validate de ANAF, dar nu are integrare cu Spațiul Privat Virtual și nu preia automat situația obligațiilor înregistrate de ANAF. Verificarea obligațiilor rezultate din D212 se face separat, direct în SPV, în afara aplicației.

[iConta.eu](/)
