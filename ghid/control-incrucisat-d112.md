---
title: Control încrucișat D112 față de contabilitatea salariilor
description: Cum verifici că impozitul și contribuțiile declarate în D112 se regăsesc în conturile de datorii salariale, ce diferențe sunt normale și care sunt semnal de problemă.
published: 2026-08-12
modified: 2026-08-12
---

# Cum verifici că D112 se potrivește cu contabilitatea salariilor?

D112 și contabilitatea salariilor pleacă din același stat de plată: aceleași brute, aceleași rețineri, aceleași contribuții. Una se depune la ANAF pe fiecare asigurat, cealaltă se înregistrează în conturi de datorii. Când cele două nu mai spun același lucru — un impozit declarat pe care nicio notă nu-l susține — diferența rămâne a ta. E mai ieftin s-o prinzi în luna respectivă decât s-o explici peste un an.

## Temeiul legal

::: ghid-temei
**Art. 147 din Codul fiscal (Legea 227/2015)** — declarația privind obligațiile de plată a contribuțiilor sociale, impozitului pe venit și evidența nominală a persoanelor asigurate. Acesta e actul din spatele formularului **D112**: o singură declarație care cuprinde, pe fiecare asigurat, impozitul pe veniturile din salarii și contribuțiile sociale datorate. Se depune **lunar, până la data de 25 inclusiv a lunii următoare** celei pentru care se plătesc veniturile.

Sumele au fiecare cota lor în Codul fiscal:

- **Impozit pe veniturile din salarii — art. 64 alin. (1):** *„Cota de impozit este de 10% și se aplică asupra venitului impozabil…"*
- **CAS — art. 138 lit. a):** *„…25% datorată de către persoanele fizice care au calitatea de angajați…"*
- **CASS — art. 156:** *„Cota de contribuție de asigurări sociale de sănătate este de 10%…"*
- **CAM — art. 220^3 alin. (1):** *„Cota contribuției asiguratorii pentru muncă este de 2,25%."*

De aici decurge logica verificării: fiecare obligație declarată trebuie să aibă acoperire în rulajul creditor al contului de datorie corespunzător.
:::

## Regula concretă

Verificarea confruntă patru perechi:

| Ce declari în D112 | Ce trebuie să arate contabilitatea |
|---|---|
| Impozit pe veniturile din salarii | rulaj creditor cont **444** |
| CAS reținut | rulaj creditor **4315** |
| CASS reținut | rulaj creditor **4316** |
| Contribuția asiguratorie pentru muncă | rulaj creditor **436** |

**Ce e diferență normală.** D112 rotunjește la leu pe total, iar contabilitatea ține bani pe fiecare salariat. O abatere de câțiva bani, care crește proporțional cu efectivul, e legitimă.

**Ce nu se compară.** Salariul brut din contul 421 nu se reconciliază unu-la-unu cu baza de contribuții din D112 — sunt mărimi diferite. Concediile medicale, de exemplu, intră altfel în cele două.

**Ce se uită frecvent.** La contractele cu timp parțial, angajatorul datorează contribuții calculate pe salariul minim, nu pe venitul realizat. Suplimentul se contabilizează tot în conturile de contribuție și trebuie inclus în comparație, altfel declarația pare mai mare decât evidența.

**Momentul verificării.** După validarea notei contabile de salarii. Cât timp nota e ciornă, evidența nu conține încă obligația — și orice comparație dă fals.

## Un exemplu

::: ghid-exemplu
**SC Exemplu SRL**, 8 salariați, luna iulie 2026. Totalurile din D112 depusă, față de rulajul creditor al conturilor:

| Obligație | Declarat în D112 | Rulaj credit | Cont |
|---|---|---|---|
| Impozit pe salarii | 2.820 lei | 2.820 lei | 444 |
| CAS | 12.500 lei | 12.500 lei | 4315 |
| CASS | 5.000 lei | **0 lei** | 4316 |
| CAM | 1.125 lei | 1.125 lei | 436 |

Trei din patru coincid la leu. La CASS, D112 declară 5.000 lei iar contul 4316 arată zero.

Nu e diferență de rotunjire. E o obligație declarată la ANAF fără acoperire în evidență: fie nota de salarii a rămas incompletă, fie linia de CASS a fost contabilizată în alt cont.

**Unde se repară.** În contabilitate, nu în declarație. D112 reflectă corect ce datorează firma; evidența e cea care nu ține pasul. O corecție în declarație ar ascunde problema, nu ar rezolva-o.
:::

## Ce se greșește în practică

- **Se compară pe note ciornă.** O notă nevalidată nu e evidență. Verificarea făcută înainte de validare dă diferențe false.
- **Se compară brutul cu baza de contribuții.** Contul 421 și bazele din D112 sunt mărimi diferite; nu se reconciliază direct.
- **Se uită suplimentul la part-time.** Contribuțiile calculate pe salariul minim, peste venitul realizat, se contabilizează în aceleași conturi și trebuie incluse.
- **Se corectează declarația în loc de evidență.** Când declarația e corectă și evidența incompletă, se completează nota contabilă.

## Ce face iConta.eu

Totalurile la nivel de angajator se citesc **direct din fișierul XML al D112 generat** — exact ce se depune, nu o recalculare paralelă — și se confruntă automat cu rulajul creditor al conturilor de datorii salariale din evidența validată.

Numai notele validate contează. O notă ciornă e semnalată ca atare, nu tratată ca dovadă.

Toleranța crește cu numărul de salariați, pentru că rotunjirea la leu produce abateri proporționale cu efectivul.

Rezultatul e un semafor:

::: ghid-semafor
rosu: Ai declarat în D112 impozit sau contribuții pe care conturile de datorii nu le confirmă — tipic, un stat de plată depus dar necontabilizat.
gri: Cifrele diferă parțial, sau totalurile stau pe note încă nevalidate — de investigat, nu eroare sigură.
verde: Totalurile din D112 și rulajul conturilor coincid, în limita toleranței.
:::

Când apare un roșu, îți e arătată cauza și propus remediul — dar corecția în contabilitate rămâne decizia ta. Aplicația nu ajustează niciodată un cont ca să dea verde.

Ce **nu** verifică, spus direct: salariul brut din contul 421. Baza de contribuții din D112 diferă legitim de brutul contabil pe concediile medicale, deci o comparație acolo ar produce alarme false.

Vezi și: [cine suportă indemnizația de concediu medical](/ghid/concediu-medical-cine-suporta) și [salariul minim în 2026](/ghid/salariu-minim-2026), care schimbă baza minimă la part-time.

[iConta.eu](/)
