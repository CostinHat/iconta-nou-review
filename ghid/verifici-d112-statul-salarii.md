---
title: "Cum verifici D112 cu statul de salarii?"
description: "De ce, într-o aplicație unde D112 și statul de plată pornesc din aceeași sursă de date, verificarea utilă de făcut nu e între ele două, ci între D112 și contabilitate."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum verifici D112 cu statul de salarii?

Întrebarea „cum verific D112 cu statul de salarii" pornește de la o presupunere firească — că cele două ar putea diverge și că merită comparate. Legea nu cere, de fapt, o astfel de verificare separată; ce cere e ca declarația depusă lunar să corespundă exact veniturilor plătite efectiv salariaților în luna respectivă.

## Temeiul legal

::: ghid-temei
„Persoanele fizice și juridice care au calitatea de angajatori sau sunt asimilate acestora, instituțiile prevăzute la art. 136 lit. d)-f), precum și persoanele fizice care realizează în România venituri din salarii sau asimilate salariilor de la angajatori din state care nu intră sub incidența legislației europene aplicabile în domeniul securității sociale [...] sunt obligate să depună lunar, până la data de 25 inclusiv a lunii următoare celei pentru care se plătesc veniturile, Declarația privind obligațiile de plată a contribuțiilor sociale, impozitului pe venit și evidența nominală a persoanelor asigurate."
— Legea 227/2015 (Codul fiscal), art. 147 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.html)
:::

- Obligația legală e ca declarația să reflecte corect veniturile **plătite** (sau datorate, după caz) în luna la care se referă — nu există o cerință legală explicită de „reconciliere D112 vs. stat de plată" ca pas separat.
- Statul de plată e documentul intern prin care angajatorul calculează și evidențiază salariile; D112 e declarația fiscală prin care aceleași date ajung la ANAF. Dacă ambele sunt calculate corect din aceleași date de intrare, ele descriu aceeași realitate, nu două realități de comparat.
- Când apare totuși o diferență reală (de exemplu o corecție retroactivă), mecanismul legal de aliniere e declarația rectificativă (CF art. 147 alin. 3), nu o „reconciliere" manuală lună de lună.

## Ce se greșește în practică

- Se tratează statul de plată și D112 ca pe două surse independente care ar putea, prin natura lor, să diveargă — de fapt, într-un sistem corect construit, ele sunt două ieșiri ale aceluiași calcul, nu două calcule separate.
- Se pierde timp verificând manual, salariat cu salariat, corespondența dintre fluturaș și declarație, în loc să se verifice ce chiar poate diverge: înregistrarea în contabilitate a obligațiilor rezultate din salarii.
- Se ignoră riscul real: nu că D112 ar diferi de statul de plată (generate din același calcul), ci că **suma din declarație să nu corespundă cu ce a fost efectiv înregistrat în contabilitate** — de exemplu o notă contabilă omisă sau înregistrată pe alt cont.

## Ce face iConta.eu

În iConta, D112 și statul de plată sunt generate din exact același motor de calcul al salarizării, cu aceiași parametri pentru fiecare salariat — o aliniere construită explicit tocmai ca cele două să nu poată diverge structural în funcționare normală. De aceea, aplicația nu oferă un ecran dedicat de „comparare D112 vs. stat de plată" — nu pentru că ar lipsi o funcție, ci pentru că, prin construcție, nu există ce să compari acolo.

Verificarea automată reală, disponibilă azi în aplicație, se face pe altă axă: **D112 față de conturile contabile ale datoriilor salariale** (421, 444, 436 și altele), într-un ecran dedicat de control fiscal încrucișat. Dacă vrei să te asiguri că declarația e corectă, verificarea utilă e aceea — vezi ghidul dedicat despre controlul încrucișat D112 față de contabilitatea salariilor pentru pașii concreți.

[iConta.eu](/)
