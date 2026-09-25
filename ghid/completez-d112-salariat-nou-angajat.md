---
title: "Cum completez D112 pentru un salariat nou angajat"
description: "Ce cere legea la depunerea Declarației 112 pentru luna în care un salariat a fost angajat — și de ce data angajării este câmpul critic."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum completez D112 pentru un salariat nou angajat

D112 nu e doar o declarație de contribuții — e, prin denumirea ei oficială, și „evidența nominală a persoanelor asigurate". Pentru un salariat nou angajat, corectitudinea declarației depinde în primul rând de data angajării, corect introdusă și corelată cu perioada raportată.

## Temeiul legal

::: ghid-temei
„(1) Persoanele fizice și juridice care au calitatea de angajatori sau sunt asimilate acestora [...] sunt obligate să depună lunar, până la data de 25 inclusiv a lunii următoare celei pentru care se plătesc veniturile, Declarația privind obligațiile de plată a contribuțiilor sociale, impozitului pe venit și evidența nominală a persoanelor asigurate."
— Cod fiscal, art. 147 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Modelul, conținutul și procedura de depunere efectivă a formularului 112 sunt aprobate separat, prin ordin comun ANAF – Casa Națională de Pensii Publice – Casa Națională de Asigurări de Sănătate – Agenția Națională pentru Ocuparea Forței de Muncă (Ordinul 605/95/928/2.314/2026, în vigoare la data acestui ghid), emis „având în vedere dispozițiile art. 147 alin. (17)" din Codul fiscal.

Pentru un salariat nou angajat, în luna angajării:

- **Data angajării trebuie completată corect** în declarație — e câmpul pe baza căruia se calculează proporțional zilele lucrate, baza de calcul a contribuțiilor și, dacă e cazul, media pentru concedii medicale (calculată pe ultimele 6 luni anterioare angajării, dacă există istoric relevant).
- Dacă angajarea are loc **în cursul lunii**, nu de la data de 1, veniturile și contribuțiile se raportează proporțional cu perioada efectiv lucrată în luna respectivă, nu pentru luna întreagă.
- Salariatul nou trebuie inclus în **evidența nominală a persoanelor asigurate** din declarație — parte separată, dar corelată, de secțiunea privind obligațiile de plată.
- Declarația se depune **lunar, până la data de 25 inclusiv a lunii următoare** celei pentru care se plătesc veniturile — un termen unic, indiferent dacă e vorba de un salariat nou sau de restul echipei.
- Anterior sau concomitent cu prima zi de muncă, angajatorul are și obligația distinctă de a raporta contractul de muncă în registrul general de evidență a salariaților (REGES-ONLINE), potrivit HG 295/2025 — o obligație separată de D112, dar cu date care trebuie să corespundă (aceeași dată de angajare).

## Ce se greșește în practică

- Se completează data angajării greșit sau se lasă necompletată, ceea ce poate produce erori la calculul proporțional al bazei de contribuții sau la calculul mediei pentru concedii medicale.
- Se raportează venitul integral pe lună întreagă pentru un salariat angajat, de exemplu, în data de 20, deși contribuțiile și impozitul trebuie calculate proporțional cu perioada efectiv lucrată.
- Se presupune că raportarea în REGES-ONLINE (înainte de prima zi de muncă) ține loc și de declararea D112 — sunt două obligații distincte, cu termene și scopuri diferite.

## Ce face iConta.eu

iConta.eu generează D112 din datele salariaților introduse în aplicație, iar `data_angajare` e un câmp obligatoriu — aplicația refuză generarea declarației dacă acest câmp lipsește pentru un salariat activ în perioada raportată, pentru a evita transmiterea unei declarații cu date incomplete către ANAF. Pe baza datei de angajare, aplicația calculează automat proporționalizarea perioadei lucrate în luna angajării și media necesară pentru concediile medicale (dacă e cazul). Raportarea în REGES-ONLINE rămâne, la data acestui ghid, în afara fluxului automatizat — vezi ghidul dedicat modificărilor de contract în REGES.

[iConta.eu](/)
