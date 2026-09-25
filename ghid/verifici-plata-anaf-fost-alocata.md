---
title: "Cum verifici dacă plata către ANAF a fost alocată corect?"
description: "Ordinea legală de stingere a obligațiilor fiscale când o plată nu acoperă toate datoriile, și cum se verifică alocarea într-un extras/certificat fiscal."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum verifici dacă plata către ANAF a fost alocată corect?

Când o firmă are mai multe tipuri de obligații fiscale (TVA, impozit pe profit, contribuții) și plătește o sumă care nu le acoperă pe toate, ANAF nu alocă suma la întâmplare — există o ordine legală de stingere, iar dacă suma plătită nu corespunde exact cu ce se aștepta să acopere, diferența poate genera accesorii (dobânzi, penalități) pe obligația rămasă neacoperită.

## Temeiul legal

::: ghid-temei
„(1) Dacă un debitor datorează mai multe tipuri de obligații fiscale, iar suma plătită nu este suficientă pentru a stinge toate obligațiile, atunci se stinge obligația fiscală pe care o indică debitorul, potrivit legii, sau care este distribuită potrivit prevederilor art. 163, după caz, stingerea efectuându-se, de drept, în următoarea ordine: [...]"
— Legea 207/2015, art. 165 alin. (1) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Cum verifici, concret, dacă o plată a fost alocată corect:

- **Solicită sau consultă în SPV fișa pe plătitor / certificatul de atestare fiscală**, care arată, pe fiecare tip de obligație, sumele datorate, plătite și rămase de plată la o dată de referință.
- **Verifică ordinea de stingere aplicată** — dacă ai indicat explicit, la plată, obligația pe care vrei să o stingi (posibil potrivit art. 163), verifică dacă ANAF a respectat această indicație; dacă nu ai indicat nimic, se aplică ordinea legală implicită (de regulă: obligații principale în ordinea vechimii, apoi accesorii).
- **Compară data plății cu data scadenței** — o plată alocată corect valoric poate totuși genera accesorii dacă a fost făcută după scadență, chiar dacă suma coincide exact cu obligația.
- **Pentru debitorii cu eșalonare la plată sau aflați în insolvență**, ordinea de stingere e diferită de regula generală (art. 165 alin. (4) și (6)) — verificarea trebuie făcută ținând cont de regimul special aplicabil.
- Dacă identifici o alocare greșită, se poate solicita organului fiscal corectarea, cu explicarea în scris a diferenței constatate.

## Ce se greșește în practică

- Se presupune că suma plătită acoperă automat obligația „cea mai recentă" sau „cea mai importantă", fără a verifica ordinea legală de stingere, care poate aloca suma altfel decât se aștepta contribuabilul.
- Nu se verifică periodic fișa pe plătitor din SPV, ci doar cu ocazia unei notificări sau somații de plată — moment în care accesoriile s-au acumulat deja pe o obligație considerată greșit stinsă.
- Se ignoră faptul că o plată efectuată cu întârziere, chiar dacă suma e corectă, generează dobânzi/penalități de întârziere calculate de la scadență, nu de la data plății.

## Ce face iConta.eu

iConta.eu ține evidența contabilă a obligațiilor fiscale calculate în aplicație (impozite, TVA, contribuții) și a plăților înregistrate prin modulul de bancă (`core/banca.py`, tipul „impozit_profit", „tva" etc., recunoscut din descrierea extrasului). La data acestui ghid, aplicația **nu are o conexiune directă cu fișa pe plătitor din SPV** pentru a compara automat alocarea reală făcută de ANAF cu obligațiile calculate intern — verificarea alocării plăților rămâne un proces manual, prin consultarea certificatului de atestare fiscală sau a fișei pe plătitor din Spațiul Privat Virtual.

[iConta.eu](/)
