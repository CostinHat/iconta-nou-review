---
title: Control încrucișat D112 vs contabilitatea salariilor lunare
description: Reconciliază D112 (impozit și contribuții pe salarii) cu evidența contabilă — temei legal, procedură și controlul încrucișat automat care prinde diferențele înainte de ANAF.
published: 2026-08-12
modified: 2026-08-12
---
# Control încrucișat D112 vs contabilitate: cum prinzi diferențele dintre ce ai declarat pe salarii și evidență, înainte de ANAF

Declarația 112 și contabilitatea salariilor pleacă din același stat de plată: aceleași brute, aceleași rețineri, aceleași contribuții ale angajatorului. Numai că una se depune la ANAF pe fiecare asigurat și pe coduri de obligație, iar cealaltă se înregistrează în conturi de datorii. Când depunerea și evidența nu mai spun același lucru — un impozit declarat pe care nicio notă nu-l susține, o contribuție înregistrată dar nedeclarată — diferența rămâne a ta. ANAF confruntă D112 depusă cu plățile și cu istoricul firmei, iar o obligație declarată fără acoperire în contabilitate devine, la un control, o discuție cu documente pe masă. E mai ieftin s-o prinzi în luna respectivă decât s-o explici peste un an.

## Ce se întâmplă azi, fără un control automat

Reconcilierea o faci la mână, în fiecare lună, după ce închizi statul de plată. Iei totalurile din D112 — impozitul pe venituri din salarii, CAS-ul, CASS-ul, contribuția asiguratorie de muncă — și le confrunți cu rulajul conturilor de datorii salariale din balanță. Pentru câțiva salariați e o verificare de câteva minute; la un stat cu zeci de oameni, cu concedii medicale, part-time cu supliment pe baza minimă și facilități, totalurile nu mai coincid la prima vedere și trebuie urmărite pe rânduri. Iar cea mai frecventă scăpare nu e o cifră greșită, ci o omisiune tăcută: statul de plată e generat și D112 e depusă, dar nota contabilă de salarii n-a fost validată încă — declari o obligație pe care evidența n-o are nicăieri.

## Temeiul legal

::: ghid-temei
**Art. 147 din Codul fiscal (Legea 227/2015) — Depunerea Declarației privind obligațiile de plată a contribuțiilor sociale, impozitului pe venit și evidența nominală a persoanelor asigurate.** Acesta este actul din spatele formularului **D112**: o singură declarație care cuprinde, pe fiecare asigurat, impozitul pe veniturile din salarii și contribuțiile sociale datorate. Declarația se depune **lunar, până la data de 25 inclusiv a lunii următoare** celei pentru care se plătesc veniturile.

Sumele din declarație au fiecare temeiul și cota lor în Codul fiscal:

- **Impozitul pe veniturile din salarii — art. 64 alin. (1):** „Cota de impozit este de **10%** și se aplică asupra venitului impozabil…"
- **Contribuția de asigurări sociale (CAS) — art. 138 lit. a):** „…**25%** datorată de către persoanele fizice care au calitatea de angajați…"
- **Contribuția de asigurări sociale de sănătate (CASS) — art. 156:** „Cota de contribuție de asigurări sociale de sănătate este de **10%**…"
- **Contribuția asiguratorie pentru muncă (CAM) — art. 220^3 alin. (1):** „Cota contribuției asiguratorii pentru muncă este de **2,25%**."

Din aceste temeiuri decurge logica reconcilierii: fiecare obligație declarată în D112 trebuie să aibă acoperire în rulajul creditor al contului de datorie corespunzător. Ce declari la ANAF și ce ține evidența trebuie să fie același număr.
:::

## Procedura manuală

::: ghid-procedura
1. Închizi statul de plată al lunii și validezi nota contabilă de salarii — atât timp cât nota e ciornă, evidența nu conține încă obligația.
2. Extragi din D112 totalurile la nivel de angajator, pe fiecare cod de obligație: impozit pe salarii, CAS, CASS și CAM.
3. Iei din balanță rulajul creditor al lunii pe conturile de datorii salariale: impozitul reținut (contul 444), CAS (subcontul 4315), CASS (subcontul 4316) și CAM (contul 436).
4. Confrunți fiecare total din D112 cu rulajul contului lui. La CAS și CASS incluzi și suplimentul angajatorului la part-time (baza minimă), care se contabilizează tot în conturile de contribuție.
5. Tratezi diferențele mici cu bun-simț: D112 rotunjește la leu pe total, iar evidența ține bani per salariat — o abatere de câțiva bani, care crește cu efectivul, e legitimă, nu eroare.
6. Nu confunzi salariul brut (contul 421) cu baza de contribuții din D112: sunt mărimi diferite (concediile medicale intră altfel), așa că brutul nu se reconciliază unu-la-unu cu declarația.
7. Reiei verificarea la fiecare corecție de stat sau notă întârziată și păstrezi dovada.
:::

## Un exemplu

::: ghid-exemplu
**SC Exemplu SRL**, 8 salariați, luna iulie 2026. Totalurile la nivel de angajator din D112 depusă, față de rulajul creditor al conturilor:

| Obligație (D112) | Declarat în D112 | Rulaj credit cont | Cont |
| --- | --- | --- | --- |
| Impozit pe salarii | 2.820 lei | 2.820 lei | 444 |
| CAS | 12.500 lei | 12.500 lei | 4315 |
| CASS | 5.000 lei | **0 lei** | 4316 |
| CAM | 1.125 lei | 1.125 lei | 436 |

Impozitul, CAS-ul și CAM-ul coincid la leu. La CASS însă D112 declară **5.000 lei**, iar contul 4316 are **0** — linia de contribuție de sănătate n-a fost înregistrată, deși obligația a fost deja declarată la ANAF. Nu e o diferență de rotunjire: e o obligație declarată fără acoperire în evidență. Fie nota de salarii a rămas incompletă, fie a fost contabilizată greșit. Remediul e în contabilitate — se completează înregistrarea — nu în declarație, care reflectă corect ce datorează firma.
:::

## Manual față de iConta.eu

::: ghid-comparatie
| Fără iConta.eu | Cu iConta.eu |
| --- | --- |
| Extragi totalurile din D112 și rulajele din balanță și le confrunți la mână, cod cu cod | Totalurile declarate se citesc direct din XML-ul D112 generat și se confruntă automat cu rulajul conturilor |
| Uiți ușor de suplimentul angajatorului la part-time sau de CAM | Fiecare cod de obligație e mapat pe contul lui, inclusiv suprataxa part-time |
| O notă de salarii rămasă ciornă trece neobservată | Doar notele validate contează ca evidență; ciorna e semnalată, nu tratată ca dovadă |
| Cauți prin balanță de ce nu se potrivesc cifrele | Semafor cu temei — roșu, gri sau verde — fiecare stare cu motivul ei |
:::

## Ce face iConta.eu

iConta.eu citește totalurile la nivel de angajator direct din XML-ul D112 generat — exact ce se depune — și le confruntă automat cu rulajul creditor al conturilor de datorii salariale din evidența validată: impozitul cu contul 444, CAS cu 4315, CASS cu 4316, CAM cu 436. Numai notele validate contează; o notă ciornă nu ține loc de evidență. Toleranța crește cu numărul de salariați, fiindcă D112 rotunjește la leu iar contabilitatea ține bani. Rezultatul e un semafor, fiecare stare cu temeiul ei:

::: ghid-semafor
rosu: Ai declarat în D112 impozit sau contribuții pe care conturile de datorii salariale nu le confirmă — tipic, un stat de plată depus dar necontabilizat (obligația e la ANAF, dar nu și în evidență).
gri: Cifrele diferă parțial, sau totalurile stau doar pe note ciornă încă nevalidate — de investigat, nu eroare sigură.
verde: Totalurile din D112 și rulajul creditor al conturilor coincid, în limita toleranței.
:::

O diferență nu se trece automat pe roșu: rotunjirea la leu și abaterile mici per salariat sunt legitime. Când apare un roșu, iConta.eu îți arată cauza și îți propune remediul — dar corecția în contabilitate rămâne decizia ta; instrumentul niciodată nu „ajustează" un cont ca să dea verde. Un semnal onest: iConta.eu verifică impozitul și contribuțiile declarate, nu salariul brut (contul 421), fiindcă baza de contribuții din D112 diferă legitim de brutul contabil pe concedii medicale. Declarația o generezi și o validezi pe validatorul oficial ANAF (DUK), iar depunerea o faci tu din SPV, cu XML-ul deja verificat.

[Deschide-ți cont pe iConta.eu](/) și pune reconcilierea D112 cu contabilitatea salariilor pe un control care se reface singur, în fiecare lună.
