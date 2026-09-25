---
title: "Poate ANAF să blocheze toate conturile firmei?"
description: "Ce prevede legea despre poprirea bancară aplicată de ANAF: câte conturi poate viza, cât din sumele existente se blochează efectiv și ce plăți rămân totuși posibile."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Poate ANAF să blocheze toate conturile firmei?

Poprirea bancară e una dintre cele mai temute măsuri de executare silită, dar realitatea ei legală e mai nuanțată decât „ANAF blochează tot". Legea distinge între suma efectiv indisponibilizată și modul în care banca tratează, practic, restul operațiunilor din cont până la stingerea datoriei.

## Temeiul legal

::: ghid-temei
„(1) Sunt supuse executării silite prin poprire orice sume urmăribile reprezentând venituri și disponibilități bănești în lei și în valută, titluri de valoare sau alte bunuri mobile necorporale, deținute și/sau datorate, cu orice titlu, debitorului de către terțe persoane [...].
(12) Pentru stingerea creanțelor fiscale, debitorii titulari de conturi bancare pot fi urmăriți prin poprire asupra sumelor din conturile bancare [...].
(13) În măsura în care este necesar, pentru achitarea sumei datorate la data sesizării instituției de credit, [...] sumele existente, precum și cele viitoare provenite din încasările zilnice în conturile în lei și în valută sunt indisponibilizate în limita sumei necesare pentru realizarea obligației ce se execută silit, astfel cum aceasta rezultă din adresa de înființare a popririi. [...]
(14) Din momentul indisponibilizării [...] instituțiile de credit nu procedează la decontarea documentelor de plată primite, respectiv la debitarea conturilor debitorilor și nu acceptă alte plăți din conturile acestora până la achitarea integrală a obligațiilor fiscale înscrise în adresa de înființare a popririi, cu excepția: a) sumelor necesare plății drepturilor salariale, inclusiv a impozitelor și contribuțiilor aferente acestora, reținute la sursă, dacă [...] debitorul nu deține alte disponibilități bănești; b) sumelor necesare plății accizelor de către antrepozitarii autorizați [...]; c) sumelor necesare plății accizelor, în numele antrepozitarilor autorizați, de către cumpărătorii de produse energetice; d) sumelor necesare plății obligațiilor fiscale de care depinde menținerea valabilității înlesnirii."
— Legea 207/2015 (Codul de procedură fiscală), art. 236 alin. (1), (12), (13) și (14) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Ce rezultă concret din text:

- **ANAF poate institui poprire pe orice cont bancar** al firmei, la orice instituție de credit unde firma are disponibilități — legea nu limitează poprirea la un singur cont sau la o singură bancă, deci, dacă e cazul, se poate institui simultan pe toate conturile cunoscute.
- **Suma efectiv indisponibilizată e limitată la ce e necesar** pentru stingerea creanței înscrise în adresa de înființare a popririi — nu tot soldul contului, ci doar partea necesară acoperirii datoriei (alin. (13)).
- **În practică, banca blochează totuși toate celelalte plăți din cont** până la achitarea integrală a datoriei — nu doar suma indisponibilizată, ci orice altă decontare, cu excepția celor patru situații enumerate expres: salarii (dacă firma nu are alte disponibilități), accize pentru antrepozitari, accize plătite de cumpărători în numele antrepozitarilor, și sumele necesare menținerii unei înlesniri la plată în vigoare.
- **Conturile valutare intră și ele sub incidența popririi** — instituțiile de credit sunt autorizate să convertească sumele în valută în lei, fără acordul titularului, la cursul zilei.

## Ce se greșește în practică

- Se presupune că poprirea blochează automat un plafon fix sau întregul sold, indiferent de suma datorată — legal, indisponibilizarea e limitată la suma necesară stingerii creanței, deși consecința practică (blocarea altor plăți) poate părea similară cu un blocaj total.
- Se ignoră excepțiile de la alin. (14) — mai ales cea privind plata salariilor, care rămâne posibilă dacă firma declară pe propria răspundere că nu are alte disponibilități bănești pentru acest scop.
- Se crede că poprirea se aplică o singură dată, pe un singur cont — dacă firma are conturi la mai multe bănci, ANAF poate transmite adrese de înființare a popririi simultan către toate instituțiile unde deține disponibilități.
- Se omite verificarea posibilității de a menține o înlesnire la plată — sumele necesare pentru respectarea unui eșalonare/reeșalonare rămân disponibile, dar doar dacă firma prezintă documentul care atestă înlesnirea aprobată.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu are nicio funcționalitate legată de poprirea bancară sau de executarea silită** — aplicația e un instrument de contabilitate și declarații fiscale, nu de gestionare a raporturilor de executare cu ANAF. Modulele de bancă (`core/banca.py`, `core/banca_parser.py`) prelucrează extrasele bancare pentru înregistrarea operațiunilor contabile, dar nu detectează și nu marchează distinct sumele indisponibilizate printr-o poprire. Gestionarea unei popriri active (identificarea sumei blocate, urmărirea excepțiilor legale de plată) rămâne complet în afara aplicației, în relația directă a firmei cu banca și cu ANAF.

[iConta.eu](/)
