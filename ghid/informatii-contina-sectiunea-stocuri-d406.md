---
title: "Ce informații trebuie să conțină secțiunea Stocuri din D406?"
description: "Câmpurile pe care schema SAF-T le cere pentru secțiunea PhysicalStock, și ce anume generează azi iConta.eu din ele — cu limitele cunoscute, spuse direct."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce informații trebuie să conțină secțiunea Stocuri din D406?

Secțiunea „Stocuri" (PhysicalStock) din fișierul standard de control fiscal (SAF-T, D406) cere o structură precisă: identificarea depozitului și a produsului, încadrarea tarifară, cantitățile și valorile de la începutul și de la finalul perioadei raportate. Nu e o listă liberă — schema oficială definește exact ce câmpuri trebuie completate pentru fiecare articol aflat în stoc.

## Temeiul legal

::: ghid-temei
„PhysicalStock (Stocuri) Conţine detalii cu privire la stocuri, precum ID-ul depozitului unde se găsesc bunurile, codul de identificare al produsului, detalii despre proprietarul stocurilor, codul de încadrare tarifară (codul NC), detalii privind cantitatea la început şi la final de perioadă de raportare, valoarea stocului la început şi la final de perioadă de raportare etc."
— OPANAF 1783/2021, Anexa la ordin (descrierea structurii SAF-T, secțiunea MasterFiles → PhysicalStock) (sursă: anaf_surse/opanaf_1783_2021_saft_d406.txt)
:::

Pe scurt, ce cere structura oficială pentru fiecare articol aflat în stoc:

- **identificarea locației**: depozitul unde se află bunurile (WarehouseID);
- **identificarea produsului**: codul intern al produsului (ProductCode);
- **încadrarea tarifară**: codul NC (nomenclator combinat vamal) — un cod distinct de contul contabil de stoc, folosit pentru clasificarea vamală/statistică a bunului;
- **proprietarul stocurilor** (OwnerID — de regulă CUI-ul firmei);
- **cantități și valori la deschidere și la închidere** de perioadă, pentru fiecare articol cu mișcări în intervalul raportat.

## Ce se greșește în practică

- Se presupune că orice cod numeric asociat unui articol (de exemplu contul contabil de stoc, 371) poate ține locul codului NC cerut de schemă — cele două sunt concepte diferite: unul e un cont contabil, celălalt un cod vamal/tarifar.
- Se raportează doar soldurile finale, fără soldul de deschidere, deși structura cere explicit ambele momente ale perioadei.
- Se ignoră unitatea de măsură și factorul de conversie, deși schema cere și aceste elemente pentru fiecare articol.

## Ce face iConta.eu

iConta.eu generează structura de bază cerută — WarehouseID, ProductCode, ProductType, OwnerID, unitate de măsură cu factor de conversie, preț unitar și cantitățile/valorile de deschidere și închidere — calculate ca sold cumulat al mișcărilor de stoc (intrare/ieșire) până la data cerută, pentru firmele care țin gestiune cantitativ-valorică.

Spus onest, ca să nu descriem o funcționalitate mai completă decât e azi: aplicația **nu completează un cod NC (de încadrare tarifară) real** — câmpul destinat acestei informații e populat, la data acestui ghid, cu același cod folosit pentru contul contabil de stoc al articolului, nu cu un cod vamal/tarifar propriu-zis; nu am putut confirma dacă validatorul oficial ANAF acceptă această valoare ca atare. În plus, aplicația nu emite o metodă de evaluare (FIFO/LIFO/CMP) explicită per articol și nu generează mișcările individuale de stoc (secțiunea `StockMovement`/`MovementType` din schema SAF-T) — doar soldurile agregate de deschidere/închidere. Unitatea de măsură e preluată ca text liber introdus de utilizator, nu ca un cod normalizat. Dacă ai nevoie de o structură validată integral pe validatorul oficial pentru un raspuns la o solicitare ANAF reală, verifică fiecare din aceste puncte înainte de a considera fragmentul complet.

[iConta.eu](/)
