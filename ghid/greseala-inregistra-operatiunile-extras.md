---
title: "Greșeala de a nu înregistra toate operațiunile din extras"
description: "De ce omiterea unor tranzacții din extrasul de cont la înregistrarea în contabilitate încalcă Legea contabilității și ce riscuri practice generează."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Greșeala de a nu înregistra toate operațiunile din extras

Omiterea unei tranzacții din extrasul de cont bancar la înregistrarea în contabilitate nu este o simplă neglijență administrativă — este o încălcare directă a principiului fundamental al legii contabilității: orice operațiune economico-financiară trebuie consemnată, pe baza documentului justificativ care o atestă, exact în momentul în care are loc.

## Temeiul legal

::: ghid-temei
„(1) Orice operațiune economico-financiară efectuată se consemnează în momentul efectuării ei într-un document care stă la baza înregistrărilor în contabilitate, dobândind astfel calitatea de document justificativ.
(2) Documentele justificative care stau la baza înregistrărilor în contabilitate angajează răspunderea persoanelor care le-au întocmit, vizat și aprobat, precum și a celor care le-au înregistrat în contabilitate, după caz."
— Legea nr. 82/1991 (Legea contabilității), art. 6 alin. (1), (2) (sursă: anaf_surse/legea_82_1991_consolidat.txt)
:::

Consecințele omiterii unor operațiuni din extras, în lumina acestui principiu:

- Extrasul de cont bancar este, el însuși, documentul justificativ pentru operațiunile derulate prin bancă — fiecare linie din extras (încasare, plată, comision, dobândă) corespunde unei operațiuni economico-financiare care trebuie reflectată în contabilitate.
- O tranzacție neînregistrată înseamnă o evidență contabilă incompletă — soldul contabil al contului bancar nu mai corespunde cu soldul real din extras, ceea ce afectează, în lanț, balanța de verificare, rezultatul fiscal și declarațiile depuse pe baza acestor date.
- Potrivit art. 6 alin. (2), răspunderea pentru o astfel de omisiune revine atât persoanelor care au întocmit/vizat/aprobat documentele, cât și celor care le-au (sau nu le-au) înregistrat în contabilitate — inclusiv contabilul care a procesat extrasul incomplet.

## Ce se greșește în practică

- Se înregistrează doar operațiunile „relevante" (facturi mari, plăți către furnizori cunoscuți), omițându-se comisioane bancare mici, dobânzi, taxe de mentenanță cont sau încasări neașteptate — toate acestea sunt, la fel, operațiuni economico-financiare supuse înregistrării.
- Se amână reconcilierea soldului contabil cu soldul din extras până la sfârșitul lunii sau trimestrului, moment în care diferențele acumulate devin greu de identificat linie cu linie.
- Se presupune că o eroare de omisiune se „corectează de la sine" la închiderea exercițiului financiar, deși fiecare operațiune omisă poate afecta TVA, impozitul pe profit/micro și alte declarații depuse deja pentru perioadele intermediare.

## Ce face iConta.eu

La data acestui ghid, iConta.eu are un parser de extrase bancare (`core/banca_parser.py`), care citește fișiere XLS/XLSX/CSV/MT940 de la bănci (testat pe formatul ING) și extrage automat toate liniile de tranzacții din extras, reducând riscul de a omite manual o operațiune la introducerea datelor. Modulul `core/banca.py` (funcția `contabilizeaza_extras`) propune apoi contarea automată a liniilor identificate, pe baza descrierii operațiunii. Validarea finală — confirmarea că toate liniile din extrasul importat au fost efectiv procesate și că soldul rezultat corespunde cu cel din extrasul bancar — rămâne responsabilitatea contabilului.

[iConta.eu](/)
