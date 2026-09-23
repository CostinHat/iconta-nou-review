---
title: "Cum mă pregătesc pentru prima depunere SAF-T"
description: Calendarul obligației D406 pe categorii de contribuabili, perioada de grație pentru prima raportare potrivit OPANAF 1783/2021 și ce merită verificat înainte de prima depunere.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum mă pregătesc pentru prima depunere SAF-T

Prima D406 nu e doar o formalitate tehnică — legea îi dă un statut special (declarație inițială) și o perioadă de grație, dar obligația de a o depune la timp rămâne intactă din prima zi în care devine activă.

## Temeiul legal

::: ghid-temei
„Contribuabilii/Plătitorii transmit Declaraţia informativă D406 lunar sau trimestrial, urmând perioada fiscală aplicabilă pentru taxa pe valoarea adăugată (TVA). Contribuabilii care au ca perioadă fiscală aplicabilă pentru taxa pe valoarea adăugată semestrul sau anul transmit Declaraţia informativă D406 trimestrial." — OPANAF nr. 1783/2021, Anexa 4, pct. 2.

Pentru prima raportare, ordinul prevede o perioadă de grație: „6 (şase) luni pentru prima raportare, respectiv cinci (cinci) luni pentru a doua raportare, 4 (patru) luni pentru a treia raportare, 3 (trei) luni pentru a patra raportare, 2 (două) luni pentru a cincea raportare", pentru depunătorii lunari, respectiv „3 (trei) luni pentru prima raportare" pentru cei trimestriali (Anexa 4, pct. 5(1)), calculată „pornind de la ultima zi a perioadei de raportare pentru care aceasta se acordă" (pct. 5(2)).
:::

## Ce contează, practic, înainte de prima depunere

Obligația de depunere D406 a fost eșalonată pe categorii de contribuabili prin OPANAF 407/2025: mari contribuabili din ianuarie, respectiv iulie 2022, mijlocii din 1 ianuarie 2023, iar contribuabilii mici — ultima categorie — de la 1 ianuarie 2025. Nerezidenții înregistrați doar în scopuri de TVA în România intră la aceeași dată de referință ca și contribuabilii mici.

Prima raportare urmează aceleași reguli de periodicitate ca decontul de TVA (lunar sau trimestrial), iar transmiterea se poate face „începând cu prima zi calendaristică a lunii următoare perioadei pentru care obligaţia devine activă, până la data-limită de depunere" (Anexa 3, pct. 13).

Trei lucruri merită verificate dinainte:

- **Perioada de grație nu anulează obligația de depunere**, doar amână sancțiunea — fișierul tot trebuie generat și transmis la termen; calendarul de la pct. 5(1) se aplică doar amenzii.
- **Nu există variantă „anuală" pentru raportarea periodică** — e strict lunar sau trimestrial, în funcție de vectorul de TVA. Chiar și o firmă cu TVA semestrial sau anual e mapată forțat la trimestrial (Anexa 4, pct. 2). Singura componentă cu adevărat anuală e secțiunea Active, depusă separat, la termenul situațiilor financiare.
- **Prima generare a fișierului scoate de obicei la iveală lipsuri în evidență** — parteneri fără cod de identificare complet, conturi nemapate corect, produse fără unitate de măsură — care merită reparate înainte de prima transmitere, nu în ultima zi.

## Ce se greșește în practică

- Se amână complet pregătirea, bazându-se doar pe perioada de grație — grația privește sancțiunea, nu termenul de depunere.
- Se presupune că o firmă cu TVA la semestru sau an depune D406 tot semestrial sau anual — Anexa 4, pct. 2 o mapează forțat la trimestrial.
- Se lasă validarea fișierului pentru ultima zi, deși prima generare e cea mai predispusă la erori de date.

## Ce face iConta.eu

iConta.eu generează Header, MasterFiles și GeneralLedgerEntries complet, conform schemei XSD, direct din evidența existentă, iar SourceDocuments (facturile de vânzare și achiziție) cu liniile reale pe produs, reconciliate obligatoriu cu antetul. Fișierul se validează cu DUKIntegrator, validatorul folosit de ANAF, înainte de a fi pus la dispoziție. Două limite rămân, la stadiul curent: secțiunea Payments nu se emite (lipsă sursă de mapare a plăților), iar Movement of Goods și Asset Transactions rămân, de asemenea, neacoperite — fișierul e valid pe zero-plăți, dar incomplet pentru o firmă cu plăți de raportat.

[iConta.eu](/)
