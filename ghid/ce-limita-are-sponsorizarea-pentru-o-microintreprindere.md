---
title: Ce limită are sponsorizarea pentru o microîntreprindere?
description: Facilitatea a fost abrogată de la 1 ianuarie 2024, deci în 2026 nu mai există nicio limită de dedus — sponsorizarea nu mai reduce impozitul micro; cât a fost activă (01.04.2019–31.12.2023), limita era 20% din impozitul micro datorat pe trimestrul respectiv.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Ce limită are sponsorizarea pentru o microîntreprindere?

Răspunsul scurt pentru 2026: **niciuna, pentru că facilitatea nu mai există**. Credit fiscal pentru sponsorizări la impozitul pe veniturile microîntreprinderilor a existat, dar a fost abrogat de la 1 ianuarie 2024. Mai jos explicăm ce limită a avut cât timp a fost în vigoare, pentru situațiile în care mai verificați o perioadă din trecut.

## Temeiul legal

::: ghid-temei
„Microîntreprinderile care efectuează sponsorizări, potrivit prevederilor Legii nr. 32/1994, cu modificările și completările ulterioare, pentru susținerea entităților nonprofit și a unităților de cult, care la data încheierii contractului sunt înscrise în Registrul entităților/unităților de cult pentru care se acordă deduceri fiscale potrivit art. 25 alin. (4^1), precum și microîntreprinderile care acordă burse elevilor școlarizați în învățământul profesional-dual... scad sumele aferente din impozitul pe veniturile microîntreprinderilor până la nivelul valorii reprezentând 20% din impozitul pe veniturile microîntreprinderilor datorat pentru trimestrul în care au înregistrat cheltuielile respective.”

— *Codul fiscal, art. 56 alin. (1^1), formă abrogată de la 01.01.2024.*

„(1^1) Abrogat. (la 01-01-2024, Alineatul (1^1), Articolul 56, Titlul III a fost abrogat de Punctul 43., Articolul LIII, Capitolul II din ORDONANȚA DE URGENȚĂ nr. 115 din 14 decembrie 2023...)”

„(2^5) Ultimul an fiscal în care sumele reprezentând sponsorizări/burse și sumele reprezentând achiziția de aparate de marcat electronice fiscale, rămase de reportat, potrivit legii, se scad din impozitul pe veniturile microîntreprinderilor este anul fiscal 2023.”
:::

## Limita, an cu an

- **De la 01.01.2024 (inclusiv 2026)**: nu există limită, pentru că nu mai există facilitate — sponsorizarea unei microîntreprinderi nu mai reduce impozitul pe venit sub nicio formă, indiferent de sumă.
- **01.04.2019 – 31.12.2023**: limita era **20% din impozitul pe veniturile microîntreprinderilor datorat pentru trimestrul** în care s-a înregistrat cheltuiala — nu un procent din cifra de afaceri (spre deosebire de plafonul de la impozitul pe profit) și nu raportat la un impozit anual.
- **01.04.2018 – 31.03.2019**: exista deja un credit similar (tot 20% din impozitul micro trimestrial), dar restrâns doar la sponsorizări către entități nonprofit/unități de cult acreditate ca **furnizori de servicii sociale licențiate** — o categorie mai îngustă decât „orice entitate nonprofit din Registru” — și fără cerința de Registru (care încă nu exista), cu reportare pe 28 de trimestre consecutive pentru sumele nescăzute.

**Notă de prudență privind data exactă „01.04.2019”**: această graniță este cea folosită de motorul iConta.eu și de materialele informative ANAF/DGRFP consultate, dar nu am găsit, în sursele verificate, un text de lege (Legea nr. 30/2019 sau OUG 25/2018 (republicată)) care să stabilească explicit „01.04.2019” drept dată de intrare în vigoare a regulii generalizate — Legea 30/2019 a fost publicată la 17.01.2019, iar 01.04.2019 pare să provină din regula de aplicare pe trimestrul calendaristic următor, nu dintr-o dată de intrare în vigoare citată direct din Monitorul Oficial. Nu schimbă limita de 20%/trimestru de mai sus, dar dacă vă aflați exact la granița martie/aprilie 2019, recomandăm reconfirmarea la sursă.

::: ghid-exemplu
În trimestrul III din 2022, o microîntreprindere datora impozit micro de 2.500 lei. Limita pentru sponsorizări acordate în acel trimestru era 20% × 2.500 = 500 lei, indiferent cât de mare era cifra de afaceri a firmei. Dacă aceeași firmă face o sponsorizare identică în trimestrul III din 2026, nu mai există nicio limită de calculat — suma nu se mai scade din impozitul micro.
:::

## Ce se greșește în practică

- Se calculează un plafon pentru o sponsorizare micro din 2024, 2025 sau 2026, deși facilitatea nu mai există din 01.01.2024.
- Se confundă limita de la micro (20% din impozitul micro trimestrial) cu cea de la impozitul pe profit (0,75% din cifra de afaceri / 20% din impozitul pe profit) — sunt reguli complet diferite.
- Se aplică limita la un impozit micro anual, în loc de cel trimestrial în care s-a înregistrat cheltuiala.
- Pentru perioada 2018–2019, se aplică regula generalizată (orice ONG din Registru) unei sponsorizări dinaintea lui aprilie 2019, când regula era restrânsă doar la furnizori de servicii sociale acreditați.

## Ce face iConta.eu

În `core/sponsorizari.py`, ramura `tip_impozit="micro"` a funcției `credit_sponsorizare()` este activă **doar pentru `la_data` în intervalul 01.04.2019 – 31.12.2023**; în afara acestui interval — inclusiv pentru orice dată din 2024, 2025 sau 2026 — motorul returnează credit 0, cu o notă explicită de inaplicabilitate, ceea ce reflectă corect abrogarea facilității. În interval, limita se calculează ca `20% × impozit_profit`, unde parametrul `impozit_profit` reprezintă, pentru ramura micro, impozitul micro datorat pe trimestru — nu un impozit anual.

Notă: fereastra 01.04.2018 – 31.03.2019 (regula inițială, mai restrânsă, din OUG 25/2018) nu este acoperită de motor — pentru o sponsorizare micro din acea perioadă, calculul trebuie făcut manual.

[iConta.eu](/)
