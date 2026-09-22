---
title: Cum se raportează clienții străini în SAF-T?
description: Clienții din UE se raportează cu prefixul "01"+țară+cod TVA (excepție Grecia, "EL"), iar cei din afara UE cu prefixul "02"+țară+cod, potrivit formatului oficial S.C.1 din schema ANAF.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se raportează clienții străini în SAF-T?

Fișierul SAF-T folosește un format standardizat de identificare a partenerilor, diferit pentru firmele din România, cele din UE și cele din afara UE. Pentru clienții străini, alegerea prefixului greșit este una dintre cele mai comune cauze de eroare la validarea declarației.

## Temeiul legal

::: ghid-temei
"|Customers (Clienţi) | Conţine informaţii despre clienţi, precum detaliile de identificare
(denumire, adresa, cod de înregistrare fiscală), contul analitic în care este înregistrat
soldul clientului respectiv, soldul iniţial debitor/creditor, sold final debitor/creditor
etc."
(opanaf_1783_2021_saft_d406.txt, Anexa 1, pct. 5, tabelul cu structura AuditFile)

**Notă onestă privind temeiul**: formatul exact al prefixelor de identificare a clienților străini (`01`+țară+cod pentru UE, `02`+țară+cod pentru non-UE, excepția Greciei unde se folosește prefixul VIES `EL`, nu ISO-ul `GR`) nu a fost găsit ca citat verbatim în actele normative citite integral pentru acest dosar (OPANAF 1783/2021, OPANAF 407/2025). Formatul provine din schema tehnică oficială ANAF (foaia "5. Structures" a fișierului `d406_schema_anaf.xlsx`), verificată direct în codul aplicației — nu dintr-un text de lege redat ca atare în sursele parcurse aici. Detaliile tehnice sunt descrise mai jos, în secțiunea explicativă.
:::

## Distincția UE vs. non-UE

Regula e simplă în principiu, dar are o excepție care se ratează des:

- Client din UE (altul decât România) → cod `01` + codul ISO al țării + codul de TVA înregistrat în VIES;
- Excepție: client din Grecia → codul folosit nu este ISO-ul de țară `GR`, ci prefixul VIES `EL` — schema ANAF exemplifică explicit acest format ca `01EL123456789`;
- Client din afara UE (ex. UK, SUA, Elveția) → cod `02` + codul de țară + identificatorul fiscal local.

::: ghid-exemplu
Un client din Franța cu cod de TVA `FR12345678901` se raportează ca `01FR12345678901`. Un client din Grecia cu cod de TVA `EL123456789` se raportează ca `01EL123456789` — nu ca `01GR123456789`.
:::

## Ce se greșește în practică

- Se aplică codul ISO `GR` pentru clienții din Grecia, în loc de prefixul VIES `EL`.
- Se raportează clienți din afara UE cu prefixul `01`, rezervat exclusiv statelor membre UE.
- Se presupune că adresa completă a clientului (stradă, număr) iese corect în SAF-T — în prezent doar localitatea (`City`) e transmisă din nomenclator, câmpul de stradă rămâne placeholder pe Customer/Supplier.
- Se transmite codul de TVA fără prefixul de țară, ca șir numeric brut.

## Ce face iConta.eu

Codul de identificare al clienților străini se construiește automat, prin `_partener_registration_number`: pentru un client din UE se generează `01`+prefix de țară+cod, iar maparea de la codul ISO la prefixul VIES este cablată explicit pentru excepția Greciei (`GR` → `EL`), astfel încât rezultatul respectă exact formatul cerut de schema oficială ANAF. Pentru clienții din afara UE se generează automat prefixul `02`. Rămâne de reținut: câmpul de adresă completă a partenerului (stradă) e în prezent un placeholder în secțiunea Customers/Suppliers — doar localitatea e populată din nomenclator, adresa detaliată a firmei proprii fiind singura raportată complet.

[iConta.eu](/)
