---
title: "Am depus SAF-T cu date incomplete"
description: "O declarație D406 (SAF-T) depusă cu date incomplete pentru o lună sau un trimestru se corectează prin depunerea unei declarații rectificative, care trebuie să cuprindă toate datele, nu doar diferența."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Am depus SAF-T cu date incomplete

Dacă îți dai seama, după validare, că fișierul SAF-T (D406) transmis pentru o lună sau un trimestru nu conține toate mișcările/documentele, soluția e simplă în procedură, dar are o capcană: rectificativa trebuie să reia integral declarația, nu doar să adauge ce a lipsit.

## Temeiul legal

::: ghid-temei
„18. Prima Declarație informativă D406 validată, depusă pentru o lună sau un trimestru de către un contribuabil/plătitor este considerată declarație inițială. Declarațiile ulterioare depuse pentru aceeași perioadă (lună/trimestru) sunt automat considerate declarații rectificative. [...] 21. Declarațiile rectificative care se depun pentru corectarea unei erori materiale, omisiuni etc. trebuie să cuprindă toate informațiile din declarația inițială, plus cele asupra cărora s-au efectuat corecții."
— OPANAF nr. 1.783/2021, instrucțiuni de completare D406 (sursă: anaf_surse/opanaf_1783_2021_saft_d406.txt)
:::

- Orice declarație D406 depusă a doua oară pentru **aceeași perioadă** (lună sau trimestru) e considerată **automat rectificativă** — nu trebuie marcată manual ca atare, procesul ANAF o recunoaște după perioadă.
- Rectificativa trebuie să conțină **toate informațiile din declarația inițială**, plus corecțiile — nu se transmite doar diferența (documentele lipsă), pentru că fișierul complet îl înlocuiește pe cel depus anterior.
- După încărcare, se generează un index de încărcare și, ulterior, o recipisă cu rezultatul procesării (validare, erori, avertismente), vizibile și în SPV, dacă firma e înrolată acolo.
- Dacă eroarea e descoperită înainte de termenul de depunere, corectarea e simplă (se redepune complet); dacă apare după termen, se aplică regulile generale de sancționare din Codul de procedură fiscală pentru nedepunere/depunere incorectă, cu excepțiile de grație prevăzute pentru primele raportări.

## Ce se greșește în practică

- Se generează și se transmite doar un fișier cu documentele omise inițial, presupunând că ANAF le „adaugă" la declarația inițială — de fapt, fișierul rectificativ trebuie să fie complet, altfel înlocuiește greșit datele deja corecte.
- Se ignoră recipisa/mesajele de validare din SPV după depunerea rectificativei, presupunând că simpla încărcare fără erori afișate pe ecran înseamnă că fișierul a fost acceptat integral de ANAF.
- Se așteaptă foarte mult până la corectare, deși perioada de grație pentru primele raportări SAF-T e limitată (2-3 luni, în funcție de periodicitate) și nu acoperă erori repetate.

## Ce face iConta.eu

La data acestui ghid, generatorul D406/SAF-T din iConta.eu (`core/d406.py`) construiește fișierul integral din evidența contabilă a lunii/trimestrului respectiv (jurnal, active, stocuri, mișcări), inclusiv o poartă explicită care oprește generarea cu un mesaj clar dacă profilul firmei e incomplet, în loc să trimită un XML respins de ANAF (`erori_generare`, în `core/d406.py`). Regenerarea declarației pentru aceeași perioadă, după completarea datelor lipsă, produce automat un fișier complet — corespunzător cerinței ca rectificativa să conțină toate informațiile, nu doar diferența. Depunerea efectivă și confirmarea recipisei rămân un pas separat, în afara aplicației.

[iConta.eu](/)
