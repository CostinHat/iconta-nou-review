---
title: Ce contribuții se datorează pentru concediul medical în 2026?
description: Pe indemnizația de concediu medical se reține CAS de 25% pe majoritatea codurilor, CASS de 10% doar pentru codurile 01, 07 și 10, iar impozitul de 10% nu se aplică pe indemnizațiile expres declarate neimpozabile de Codul fiscal.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Ce contribuții se datorează pentru concediul medical în 2026?

Spre deosebire de salariu, unde CAS, CASS și impozitul se aplică uniform, pe indemnizația de concediu medical reținerile diferă în funcție de codul de boală înscris pe certificat. Nu toate cele trei rețineri se aplică pe fiecare tip de concediu medical.

## Temeiul legal

::: ghid-temei
**Codul fiscal, Articolul 156:** *"Cota de contribuție de asigurări sociale de sănătate este de 10%."*

**Codul fiscal, Articolul 62 lit.c):** *"indemnizațiile pentru: risc maternal, maternitate, creșterea copilului și îngrijirea copilului bolnav, îngrijirea pacientului cu afecțiuni oncologice, potrivit legii;"*

**OUG 158/2005, Articolul 25, alin.(1):** *"Cuantumul brut lunar al indemnizației de maternitate este de 85% din baza de calcul..."*

**OUG 158/2005, Articolul 25, alin.(2):** *"Indemnizația de maternitate se suportă INTEGRAL din bugetul FNUASS."*

**OUG 158/2005, Articolul 30, alin.(1):** *"Cuantumul brut lunar al indemnizațiilor prevăzute la art. 26 alin. (1) și (1^1) este de 85% din baza de calcul..."*
:::

## Cele trei rețineri, pe rând

**CAS (25%)** se reține, în practica administrativă, uniform pe toate codurile de indemnizație — inclusiv pe maternitate și îngrijire copil bolnav, deși nu există un text de lege separat, explicit dedicat acestui caz (vezi ghidul „Se plătește CAS pentru concediul medical?").

**CASS (10%)** nu se reține pe toate codurile, ci doar pe o parte dintre ele — cele asociate concediului medical obișnuit (cod 01), carantinei (cod 07) și reducerii programului de muncă (cod 10). Pentru celelalte coduri (maternitate, îngrijire copil, izolare etc.) CASS nu se aplică.

**Impozitul pe venit (10%)** nu se aplică deloc pe indemnizațiile enumerate expres de Codul fiscal ca fiind neimpozabile: risc maternal, maternitate, creșterea copilului, îngrijirea copilului bolnav, îngrijirea pacientului cu afecțiuni oncologice. Pe restul codurilor (de exemplu boală obișnuită, carantină), impozitul de 10% se aplică pe indemnizația brută rămasă după reținerea CASS.

::: ghid-exemplu
Un salariat cu concediu medical pentru maternitate (cod 08) primește 85% din baza de calcul, suportat integral de FNUASS. Din indemnizația brută se reține CAS (25%, conform practicii administrative), dar NU se reține CASS și NU se reține impozit, pentru că indemnizația de maternitate e expres neimpozabilă conform art.62 lit.c) din Codul fiscal.
:::

## Ce se greșește în practică

- Se reține CASS pe orice tip de concediu medical, fără să se verifice dacă respectivul cod de boală se numără printre cele pentru care CASS chiar se datorează.
- Se reține impozit pe indemnizația de maternitate sau de îngrijire copil, deși acestea sunt expres neimpozabile prin lege.
- Se tratează toate concediile medicale la fel, ignorând că procentul aplicat bazei de calcul (85% pentru maternitate, 100% pentru anumite boli grave, scara 55/65/75% pentru boala obișnuită) diferă de la un cod la altul.
- Se presupune, greșit, că indemnizația de maternitate se suportă parțial de angajator — legea prevede că se suportă INTEGRAL din FNUASS.

## Ce face iConta.eu

Funcția `taxe_cm()` din motorul de calcul aplică rețineri diferențiate pe cod: CAS de 25% uniform pe toate codurile, CASS de 10% doar pentru codurile 01, 07 și 10, iar impozitul de 10% pe (brut − CASS), cu excepția codurilor marcate ca neimpozabile — 08, 09, 15, 17, 91, 92 — conform art.62 lit.c) din Codul fiscal. Procentele aplicate bazei de calcul (85% pentru maternitate/îngrijire copil, 100% pentru bolile grave enumerate expres de lege, scara progresivă pentru boala obișnuită) sunt calculate separat, prin `procent_cm()`, în funcție de codul certificatului.

[iConta.eu](/)
