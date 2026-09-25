---
title: "Cum închid un SRL cu salariați?"
description: "Temeiul legal al concedierii pentru desființarea locului de muncă la închiderea unei firme — și de ce lichidarea propriu-zisă e o funcționalitate separată de evidența salariaților."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum închid un SRL cu salariați?

Închiderea unei firme care are salariați angajați presupune, printre altele, încetarea legală a contractelor lor de muncă — un proces reglementat distinct de restul procedurii de lichidare/radiere. Concret, temeiul care se aplică aici e cel al concedierii pentru motive care nu țin de persoana salariatului, pentru că desființarea firmei duce, aproape întotdeauna, la desființarea posturilor.

## Temeiul legal

::: ghid-temei
„Concedierea pentru motive care nu ţin de persoana salariatului reprezintă încetarea contractului individual de muncă, determinata de desfiinţarea locului de muncă ocupat de salariat ca urmare a dificultăţilor economice, a transformărilor tehnologice sau a reorganizării activităţii. [...] Desfiinţarea locului de muncă trebuie să fie efectivă şi să aibă o cauza reală şi serioasă, dintre cele prevăzute la alin. (1)."
— Legea 53/2003 (Codul Muncii), art. 65 alin. (1)-(2) (sursă: anaf_surse/legea_53_2003_codul_muncii.txt)
:::

- Concedierea legată de închiderea firmei se încadrează la „motive care nu țin de persoana salariatului" — nu e o sancțiune și nu are legătură cu performanța angajatului.
- Desființarea locului de muncă trebuie să fie **efectivă** și să aibă o **cauză reală și serioasă** — reorganizarea sau încetarea activității din cauza lichidării firmei se încadrează aici.
- Concedierea pentru acest motiv poate fi **individuală sau colectivă** (art. 66); dacă numărul de salariați disponibilizați într-o perioadă de 30 de zile atinge pragurile de la art. 68, devine concediere colectivă, cu obligația de notificare a sindicatului/reprezentanților salariaților cu cel puțin 45 de zile calendaristice înainte de emiterea deciziilor.

## Ce se greșește în practică

- Se derulează procedura de lichidare/radiere a firmei fără a încheia formal contractele salariaților — fără decizie de concediere, fără data de încetare actualizată în evidența internă și fără transmiterea corespunzătoare în REGES-ONLINE.
- Se tratează orice concediere legată de închiderea firmei ca „individuală", deși pragurile numerice de la art. 68 pot încadra situația la concediere colectivă, cu o procedură de notificare complet diferită.
- Se presupune că o aplicație de contabilitate care ține evidența salariaților gestionează și partea de lichidare a firmei (monografii contabile de dizolvare, partaj, radiere) — sunt procese distincte.

## Ce face iConta.eu

Închiderea propriu-zisă a unui SRL — monografiile contabile de lichidare, dizolvare și radiere — e acoperită de o **funcționalitate separată** din iConta.eu, dedicată lichidării societăților, nu de evidența salariaților. Funcționalitatea de Salariați (CRUD) intervine aici doar la un nivel strict tehnic: pentru fiecare salariat concediat ca urmare a închiderii firmei, trebuie completată data încetării contractului din butonul „Încetare" (devine „Plecat <dată>" odată completat) al salariatului, în ecranul **Stat de plată** — pasul minim care oprește calculul salarial ulterior pentru acea persoană. Onest: iConta.eu **nu generează** decizia de concediere, **nu calculează** preavizul sau compensațiile prevăzute de lege, **nu gestionează** notificarea către sindicat/ITM în cazul concedierii colective și **nu are nicio legătură** cu motorul de lichidare a firmei — toate acestea rămân în sarcina utilizatorului sau a altor funcționalități dedicate.

[iConta.eu](/)
