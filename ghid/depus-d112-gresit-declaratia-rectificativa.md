---
title: "Am depus D112 greșit: cum fac declarația rectificativă"
description: "Cum se corectează o declarație D112 depusă greșit, conform OPANAF 605/2026 — și ce nu automatizează încă iConta pe acest pas."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Am depus D112 greșit: cum fac declarația rectificativă

O eroare în D112 — un salariat omis, o bază de calcul greșită, o zi de concediu medical necompletată — nu cere o cerere separată la ANAF. Se corectează prin depunerea unei noi declarații D112, marcată drept rectificativă, pentru aceeași lună.

## Temeiul legal

::: ghid-temei
„Declarația privind obligațiile de plată a contribuțiilor sociale, impozitului pe venit și evidența nominală a persoanelor asigurate poate fi corectată de contribuabili din proprie inițiativă, prin depunerea unei declarații rectificative. [...] Declarația rectificativă se întocmește pe același model de formular ca și declarația care se corectează, bifându-se cu X căsuța aflată pe prima pagină a formularului. Declarația rectificativă se completează integral, înscriindu-se toate datele și informațiile prevăzute de formular, inclusiv cele care nu diferă față de declarația inițială."
— OPANAF 605/95/928/2314/2026, pct. 2.1, 2.3, 2.4 (sursă: anaf_surse/opanaf_605_2026_d112.txt)
:::

Ce trebuie reținut din procedura oficială:

- Corectarea e posibilă **din proprie inițiativă**, oricând — nu e nevoie de o notificare din partea ANAF pentru a rectifica o eroare proprie (deși există și o casetă separată pentru „declarație rectificativă depusă ca urmare a unei notificări de conformare", pentru cazul în care rectificarea vine în urma unui control).
- Declarația rectificativă **nu e parțială** — se completează integral, cu toate datele, nu doar cu rândurile greșite. O rectificativă care ar conține doar corecția, fără restul datelor nemodificate, nu respectă forma cerută.
- Se bifează explicit caseta „Declarație rectificativă" de pe prima pagină a formularului — fără bifă, declarația nouă ar putea fi respinsă ca duplicat al celei inițiale sau ar produce confuzie la ANAF.
- Ca regulă generală de corectare a declarațiilor fiscale (Codul de procedură fiscală art. 105 alin. (1)), corectarea se poate face „pe perioada termenului de prescripție a dreptului de a stabili creanțe fiscale" — 5 ani, calculați de la 1 iulie a anului următor celui pentru care se datorează obligația (CPF art. 110).

## Ce se greșește în practică

- Se presupune că D112 se corectează parțial, doar pentru salariatul sau rândul greșit — legea cere completarea integrală a formularului, inclusiv datele nemodificate.
- Se omite bifarea căsuței „Declarație rectificativă" de pe prima pagină a formularului.
- Se confundă termenul general de prescripție (5 ani) cu o presupusă limită mai scurtă, specifică D112 — declarația nu are un termen propriu de rectificare mai restrictiv decât regula generală din Codul de procedură fiscală, atâta vreme cât nu a intervenit anularea rezervei verificării ulterioare (CPF art. 105 alin. (5)).

## Ce face iConta.eu

Funcționalitatea **Declarația D112** (`core/d112.py`) generează și validează declarația cu DUKIntegrator, validatorul oficial ANAF rulat local — inclusiv concediile medicale, tichetele și facilitatea fiscală, pe aceeași sursă de date ca statul de plată, ca să nu diverge de fluturaș. Contabilul poate corecta datele salariatului (brut, zile, concediu medical etc.) în aplicație și regenera declarația cu cifrele actualizate.

Spre deosebire de alte declarații din ecranul **Declarații** al iConta (D311, D307, D107, D177, D207), care au fiecare o casetă „Declarație rectificativă" bifabilă direct în interfață, **D112 nu are încă acest câmp** — verificat la sursă: nu apare nicio referință la rectificativă în `core/d112.py` sau în panoul D112 din interfață, deși structura oficială XML a formularului conține câmpul `d_rec` pentru exact acest scop. Practic: iConta regenerează corect XML-ul cu datele corectate, dar bifarea căsuței „Declarație rectificativă" pe formular trebuie făcută în afara aplicației — la depunerea efectivă în SPV/portalul ANAF.

[iConta.eu](/)
