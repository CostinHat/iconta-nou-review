---
title: "Cum completează o II Declarația Unică D212?"
description: "O întreprindere individuală completează D212 la fel ca un PFA — categoria de venit, modul de stabilire (sistem real sau normă) și forma de organizare se declară pe capitolul corespunzător."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum completează o II Declarația Unică D212?

O întreprindere individuală (II) nu are un formular separat de D212 — completează aceeași declarație unică pe care o depune orice persoană fizică ce realizează venituri din activități independente, cu mențiunea formei de organizare la capitolul de venit corespunzător modului în care își stabilește venitul net.

## Temeiul legal

::: ghid-temei
„Contribuabilii au obligația depunerii Declarației unice privind impozitul pe venit și contribuțiile sociale la organul fiscal competent, pentru fiecare an fiscal, în cazul în care realizează, individual sau într-o formă de asociere, venituri/pierderi, după caz, din următoarele categorii de venit: a) activități independente; [...]"
— Codul fiscal (Legea 227/2015), art. 122 alin. (1) lit. a) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Structural, D212 grupează veniturile din activități independente pe capitole distincte, selectate în funcție de modul de determinare a venitului net, nu de forma juridică a titularului:

- **cap11** — sistem real (venit brut minus cheltuieli deductibile, conform art. 68 Cod fiscal).
- **cap12** — normă de venit, cu subcâmpul `norma_forma_org` care indică exact forma de organizare (PFA, II sau IF).
- **cap14** — venituri realizate în străinătate, dacă e cazul.

Contribuțiile aferente (CAS și CASS) se declară separat, la capitolul `oblig_realizat`, calculate pe baza venitului net rezultat din capitolul de venit completat, nu într-un formular distinct pentru II.

## Ce se greșește în practică

- Se caută un formular sau o secțiune separată „pentru întreprinderi individuale" — D212 nu are așa ceva; toată deosebirea e la câmpul care indică forma de organizare.
- Se completează cap11 (sistem real) când activitatea e la normă de venit, sau invers, fără să se verifice modul real de stabilire a venitului net declarat anterior.
- Se omite declararea CAS/CASS separat de impozitul pe venit, deși ambele obligații se stabilesc prin aceeași declarație.

## Ce face iConta.eu

Generatorul D212 al iConta.eu (`core/d212.py`) e o declarație **manuală**: aplicația nu are registru de persoane fizice, deci venitul brut, cheltuielile deductibile sau norma de venit pentru o II se introduc direct în declarație, prin dict-ul `manual` transmis generatorului. Structura respectă întocmai câmpurile validate de ANAF (D212Validator), inclusiv `norma_forma_org` pentru declararea corectă a formei de organizare la capitolul de normă de venit.

Pentru contribuabilii la sistem real, `core/rip_api.py` (funcția `fisa_d212`) calculează automat CAS, CASS și impozitul pornind de la operațiunile validate din Registrul-jurnal de încasări și plăți (OMFP 170/2015) ținut în aplicație — dar doar pentru veniturile anilor 2025 și 2026, singurii pentru care plafoanele sunt verificate la sursă. Pentru normă de venit, aplicația nu calculează automat baza — valoarea normei se introduce manual, conform nomenclatorului DGRFP.

[iConta.eu](/)
