---
title: "Autorizarea firmei la ITM: obligații 2026"
description: "Precizare de temei: firma nu are nevoie de o autorizare formală de la Inspectoratul Teritorial de Muncă; obligația reală e înregistrarea salariaților în REGES-ONLINE înainte de începerea activității."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Autorizarea firmei la ITM: obligații 2026

Precizare importantă înainte de orice altceva: în 2026 nu există o „autorizare de la ITM" ca procedură prealabilă de obținut înainte de a începe activitatea cu angajați — regimul de autorizare prealabilă a fost înlocuit de-a lungul anilor cu obligații declarative. Nu am găsit, în sursele verificate, un act normativ care să impună o „autorizare" formală a firmei la Inspectoratul Teritorial de Muncă; ceea ce există real, cu temei clar, e obligația de **înregistrare a salariaților în Registrul general de evidență a salariaților (REGES-ONLINE)** înainte de începerea activității primului salariat, plus obligațiile de securitate și sănătate în muncă. Ghidul de mai jos redirecționează spre aceste obligații verificate, în locul unei „autorizări" care nu are temei legal identificat.

## Temeiul legal

::: ghid-temei
„Articolul 7 Angajatorii au obligația de a completa și de a transmite datele în Registru cel târziu în ziua anterioară începerii activității de către primul salariat."
— HG 295/2025 (privind registrul general de evidență a salariaților), art. 7 (sursă: anaf_surse/hg_295_2025_reges_online_registru_salariati.txt)

„b) să întocmească un plan de prevenire și protecție compus din măsuri tehnice, sanitare, organizatorice și de altă natură, bazat pe evaluarea riscurilor, pe care să îl aplice corespunzător condițiilor de muncă specifice unității;"
— Legea 319/2006 (securitatea și sănătatea în muncă), art. 13 lit. b) (sursă: anaf_surse/legea_319_2006_consolidat.txt)
:::

Ce trebuie să facă real o firmă înainte de a angaja primul salariat:

- **Înregistrarea în REGES-ONLINE**, cel târziu în ziua anterioară începerii activității de către primul salariat (art. 7 HG 295/2025) — aceasta e obligația cu efect practic echivalent unei „autorizări", pentru că fără ea contractul de muncă nu e opozabil legal. Netransmiterea datelor înainte de prima zi (art. 4 alin. (2) lit. a)-j)) se sancționează potrivit art. 9 alin. (1), prin trimitere la art. 260 alin. (1) lit. e^1) din Legea 53/2003; separat, art. 9 alin. (2) lit. a) prevede o amendă între 3.000 și 5.000 lei pentru fiecare persoană neînregistrată, pentru netransmiterea elementelor contractului individual de muncă în termenul prevăzut la art. 5 alin. (1) lit. a).
- **Evaluarea riscurilor de securitate și sănătate în muncă** și întocmirea unui plan de prevenire și protecție, obligatorie pentru orice angajator (Legea 319/2006, art. 13 lit. b) — nu e condiționată de mărimea firmei sau de domeniul de activitate.
- **Instruirea lucrătorilor** privind securitatea și sănătatea în muncă (instructaj introductiv general, la locul de muncă și periodic) — parte din aceleași obligații generale ale Legii 319/2006.

Notă: HG 295/2025 (care a înlocuit vechea HG 905/2017, cunoscută popular sub numele „REVISAL") a fost contestată în instanță și anulată în primă instanță de Curtea de Apel Constanța; decizia nu e definitivă, iar obligațiile descrise mai sus rămân în vigoare până la o hotărâre finală.

## Ce se greșește în practică

- Se caută o „autorizare de funcționare de la ITM" ca document separat de obținut — nu există o astfel de procedură; obligația reală e declarativă (înregistrarea în Registru), nu una de aprobare prealabilă.
- Se angajează primul salariat și se transmit datele în REGES-ONLINE abia după prima zi de muncă efectivă, deși termenul legal e „cel târziu în ziua anterioară" — o zi de întârziere înseamnă deja contravenție.
- Se ignoră obligațiile de securitate și sănătate în muncă (evaluarea riscurilor, instructajul), considerându-le opționale pentru firme mici — Legea 319/2006 nu face nicio distincție după numărul de salariați.

## Ce face iConta.eu

iConta.eu are integrare directă cu REGES-ONLINE (`core/reges_client.py`), care generează și trimite mesajul de înregistrare a identității salariatului (`mesaj_inregistrare_salariat`) și mesajul de adăugare a contractului individual de muncă (`mesaj_adaugare_contract`), din ecranul Stat de plată — acoperind exact obligația de la art. 7 din HG 295/2025. Obligațiile de securitate și sănătate în muncă (evaluarea riscurilor, planul de prevenire, instructajul) **nu sunt gestionate de aplicație** — ele țin de un domeniu separat de expertiză (SSM), nu de contabilitate, și rămân în sarcina firmei sau a unui furnizor specializat.

[iConta.eu](/)
