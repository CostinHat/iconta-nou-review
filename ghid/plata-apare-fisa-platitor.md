---
title: "Ce fac dacă plata nu apare în fișa pe plătitor?"
description: "Ce dată contează legal drept moment al plății unei obligații fiscale prin transfer bancar, chiar dacă fișa pe plătitor din portalul ANAF nu o reflectă încă."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce fac dacă plata nu apare în fișa pe plătitor?

O plată făcută prin internet banking, dar care nu apare (încă) în fișa pe plătitor de pe portalul ANAF, nu înseamnă automat că obligația fiscală e neplătită. Legea leagă momentul plății de data la care banca a debitat contul, nu de data la care sistemul informatic al ANAF procesează și afișează suma.

## Temeiul legal

::: ghid-temei
„(11) În cazul stingerii prin plată a obligațiilor fiscale, bugetare sau a altor sume colectate de instituții publice, în condițiile legii, momentul plății este: [...] d) în cazul plăților efectuate prin decontare bancară, inclusiv internet banking, home banking, mobile banking sau alte mijloace de plată la distanță puse la dispoziția debitorilor de instituțiile de credit, inclusiv tranzacțiile efectuate prin intermediul contului tranzitoriu, data la care băncile debitează contul persoanei care efectuează plata pe baza instrumentelor de decontare specifice, astfel cum această informație este transmisă prin mesajul electronic de plată de către instituția bancară inițiatoare, potrivit reglementărilor specifice în vigoare, cu excepția situației prevăzute la art. 177;"
— Legea nr. 207/2015 (Codul de procedură fiscală), art. 163 alin. (11) lit. d) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Ce trebuie făcut, în ordine, când suma nu apare în fișă:

- Se verifică mai întâi **data la care banca a debitat efectiv contul plătitorului** — aceasta e, prin lege, data plății, indiferent cât durează procesarea și afișarea ei în evidența ANAF.
- Se păstrează extrasul de cont sau confirmarea de plată din aplicația bancară, ca dovadă a momentului plății — legea permite dovedirea plății și pe baza acestor documente, nu doar prin fișa ANAF.
- Dacă plata a fost efectuată în contul unic, se ține cont de faptul că distribuirea sumelor pe tipuri de obligații se face de organul fiscal, în ordinea legală (mai întâi impozite și contribuții cu reținere la sursă, apoi celelalte obligații principale, apoi accesoriile) — o întârziere în distribuire nu înseamnă că plata nu a fost recepționată, ci că nu a fost încă alocată vizibil pe obligația urmărită.
- Dacă banca nu a decontat sumele către bugetul de stat în termen de 3 zile lucrătoare de la debitarea contului contribuabilului, legea prevede expres că această întârziere nu îl exonerează pe contribuabil de plată, dar nici nu îi atrage dobânzi/penalități suplimentare peste acest termen de 3 zile — răspunderea pentru întârzierea decontării revine instituției de credit.

## Ce se greșește în practică

- Se reface plata a doua oară, din grabă, doar pentru că suma nu apare imediat în fișa pe plătitor, riscând o dublă plată.
- Se acceptă fără verificare data la care apare suma în portalul ANAF ca fiind „data plății", deși legea leagă momentul plății de data debitării contului bancar.
- Nu se păstrează dovada bancară a plății (extras de cont, confirmare de transfer), care e documentul relevant în caz de dispută cu organul fiscal privind data reală a plății.

## Ce face iConta.eu

La data acestui ghid, iConta.eu urmărește obligațiile fiscale datorate și termenele de plată prin modulul de control fiscal (`core/control_fiscal_api.py`, funcțiile `obligatii_datorate` și `declaratii_datorate`), pe baza calendarului fiscal al firmei. Aplicația **nu are acces la fișa pe plătitor din portalul ANAF** și nu confirmă automat recepționarea unei plăți de către trezorerie — verificarea datei reale de debitare a contului bancar și, dacă e cazul, transmiterea dovezii de plată către organul fiscal rămân operațiuni pe care contabilul le face în afara aplicației.

[iConta.eu](/)
