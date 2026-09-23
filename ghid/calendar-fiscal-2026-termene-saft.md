---
title: "Calendar fiscal 2026: termene pentru SAF-T și D205"
description: Termenele SAF-T (D406) și D205 pentru 2026, cu temeiul legal al fiecăruia — și o precizare importantă despre ce arată efectiv ecranul Termene din iConta.eu pentru fiecare din ele.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Calendar fiscal 2026: termene pentru SAF-T și D205

SAF-T (D406) și D205 au reguli de termen diferite și, în iConta.eu, tratament diferit în ecranul de calendar. Le luăm pe rând.

## Temeiul legal

::: ghid-temei
„Data-limită pentru transmiterea declarațiilor informative D406 privind fișierul standard de control fiscal este ultima zi calendaristică din luna depunerii, reprezentând luna calendaristică imediat următoare perioadei pentru care a fost pregătită declarația informativă."
— OPANAF 1783/2021, Anexa nr. 4, pct. 4
:::

::: ghid-temei
„până în ultima zi a lunii februarie inclusiv a anului curent pentru anul expirat"
— OPANAF 179/2022, pct. 5.1 lit. a)
:::

**SAF-T (D406)**, pentru 2026: termenul e ultima zi calendaristică a lunii următoare perioadei de raportare. Periodicitatea depinde de statutul de TVA — plătitorii raportează în ritmul deconturilor lor de TVA (lunar sau trimestrial), neplătitorii raportează trimestrial. La prima raportare, legea acordă o perioadă de grație (6 luni pentru transmitere lunară, 3 luni pentru transmitere trimestrială, descrescătoare la raportările următoare) — un detaliu esențial de care depinde dacă termenul „nominal" chiar e scadența reală pentru o firmă aflată la începutul obligației.

**D205**, pentru anul 2026: se depune pentru anul 2026 până în ultima zi a lunii februarie 2027. D205 e o declarație informativă privind impozitul reținut la sursă (inclusiv pe dividendele distribuite în cursul anului) — se datorează doar dacă firma a avut, în anul respectiv, plăți supuse acestei rețineri.

## Ce arată efectiv ecranul Termene din iConta.eu

Aici e diferența importantă între cele două declarații:

- **SAF-T apare** în ecranul „Termene" (card-ul cu scadențele pe portofoliu, fereastra viitoare de 60 de zile): motorul de calendar derivă periodicitatea din vectorul fiscal (statut TVA + tip decont) și pune scadența pe listă, cu termenul nominal descris mai sus.
- **D205 NU apare** în ecranul „Termene". Verificat direct în cod: motorul care alimentează acest ecran (`core/termene_api.py` → `control_fiscal_api.obligatii_datorate`) nu calculează D205 deloc. D205 se derivă în altă parte a aplicației, pe „Semafor" (control fiscal), printr-o funcție separată (`declaratii_fapt`) care verifică FAPTUL — rulajul contului 457 (dividende distribuite) — nu doar vectorul fiscal. Motivul pentru care nu e (încă) în calendarul pe 60 de zile: D205 depinde de un eveniment (distribuirea dividendelor), nu de un termen fix derivabil doar din regim/TVA, ca celelalte declarații de pe acel ecran.

Practic: pentru SAF-T, cardul „Termene" e locul corect de verificat. Pentru D205, verifică ecranul „Semafor" — acolo aplicația confruntă rulajul contului 457 cu declarațiile depuse și îți spune dacă ai dividende distribuite fără D205 aferentă.

## Ce se greșește în practică

- Se caută D205 pe ecranul „Termene" și, negăsind-o, se presupune că firma nu o datorează — de fapt înseamnă doar că acel ecran nu urmărește D205 deloc, indiferent de situația firmei.
- Se tratează termenul SAF-T afișat drept scadență fermă pentru o firmă la prima raportare, fără să se scadă perioada de grație legală.
- Se confundă „ultima zi a lunii următoare" (SAF-T, lunar sau trimestrial pe tot anul) cu „ultima zi a lunii februarie" (D205, o singură dată pe an, pentru anul anterior) — sunt reguli diferite, pentru declarații diferite.

## Ce face iConta.eu

Ecranul „Termene" (F093) derivă și afișează scadențele SAF-T pentru fiecare firmă din portofoliu, grupate pe dată, folosind același motor unic de mapare fiscală ca semaforul de control fiscal, dar cu fereastra restrânsă la viitor (60 de zile). Nu calculează perioada de grație de la prima raportare SAF-T — asta rămâne verificare manuală.

Pentru D205, iConta.eu nu îl pune pe calendarul de 60 de zile, dar îl urmărește pe fapt (rulajul contului 457) în ecranul „Semafor", cu explicație clară când nu poate stabili dacă s-au distribuit dividende (lipsă note validate pe anul respectiv).

[iConta.eu](/)
