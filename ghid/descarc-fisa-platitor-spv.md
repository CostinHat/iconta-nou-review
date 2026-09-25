---
title: "Cum descarc fișa pe plătitor din SPV"
description: "Ce este Spațiul Privat Virtual, temeiul lui legal, și cum se comunică documentele fiscale prin acest canal, conform OMFP 660/2017."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum descarc fișa pe plătitor din SPV

Spațiul Privat Virtual (SPV) nu e doar un portal de vizualizare — e definit legal ca un serviciu de comunicare electronică cu valoare probatorie, prin care ANAF transmite documente contribuabilului și invers.

## Temeiul legal

::: ghid-temei
„În scopul prezentului ordin comunicarea prin mijloace electronice de transmitere la distanţă se realizează prin intermediul serviciului «Spaţiul privat virtual» - serviciu de distribuţie electronică înregistrată care permite transmiterea de date între terţi prin mijloace electronice şi furnizează dovezi referitoare la manipularea datelor transmise, inclusiv dovezi privind trimiterea şi primirea datelor [...]."
— OMFP 660/2017, art. 2 (sursă: anaf_surse/omfp_660_2017.txt)
:::

Ce rezultă din acest temei pentru accesul la datele fiscale ale unui contribuabil:

- SPV e cadrul legal prin care Ministerul Finanțelor/organul fiscal central comunică electronic **informații și înscrisuri** contribuabilului (art. 3 lit. b) din același ordin) — printre documentele comunicate astfel se numără decizii de impunere, decizii referitoare la obligații de plată accesorii și alte acte administrativ-fiscale;
- documentele comunicate prin SPV sunt semnate de Ministerul Finanțelor cu semnătură electronică extinsă/sigiliu electronic calificat (art. 4, art. 11) — ceea ce le conferă valoare probatorie egală cu comunicarea pe suport hârtie;
- **fișa pe plătitor** ca funcționalitate specifică de extragere/descărcare din portalul SPV nu e detaliată nominal în OMFP 660/2017 — ordinul reglementează cadrul general al serviciului de comunicare electronică, nu fiecare raport sau document disponibil ulterior în interfața portalului; disponibilitatea exactă a acestei funcționalități și modul ei de accesare țin de interfața tehnică pusă la dispoziție de ANAF pe portalul SPV, nu de un articol de lege distinct identificat în sursele verificate pentru acest ghid.
- accesul la SPV se face pe baza înregistrării ca utilizator, identificat prin certificat calificat sau alte mijloace de identificare electronică prevăzute de procedura anexă la ordin.

## Ce se greșește în practică

- Se presupune că orice document afișat în SPV are automat valoare de „comunicare oficială" din partea ANAF — regula legală (art. 4) leagă valoarea probatorie de semnătura/sigiliul electronic calificat aplicat de Ministerul Finanțelor, nu de simpla afișare a informației în portal.
- Se confundă fișa sintetică (rezumat al situației fiscale) cu fișa pe plătitor detaliată (evidența analitică a obligațiilor și plăților) — cele două rapoarte au conținut diferit, deși ambele sunt accesibile prin același portal.
- Se așteaptă actualizarea în timp real a datelor din SPV — evidența analitică a organului fiscal se actualizează periodic, nu instantaneu cu fiecare plată sau declarație depusă.

## Ce face iConta.eu

iConta.eu are un conector unic pentru autentificarea OAuth2 cu SPV/ANAF (`core/spv_conector.py`), folosit pentru transmiterea și primirea facturilor electronice (RO e-Factura) prin API-ul ANAF. Documentația internă a modulului precizează explicit că acest conector **nu** acoperă alte funcționalități ale portalului SPV, precum descărcarea fișei pe plătitor — aceasta rămâne o operațiune pe care utilizatorul o face direct din portalul SPV, în afara aplicației.

[iConta.eu](/)
