---
title: "Ce nomenclatoare ANAF se folosesc pentru SAF-T în 2026?"
description: "Nomenclatoarele oficiale ANAF folosite la completarea fișierului standard de control fiscal (SAF-T / D406) — coduri de taxă, unități de măsură și tipuri de mișcări de stoc."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce nomenclatoare ANAF se folosesc pentru SAF-T în 2026?

Fișierul standard de control fiscal (SAF-T, raportat prin D406) nu acceptă text liber pe majoritatea câmpurilor sale de clasificare — fiecare element trebuie mapat la un cod dintr-un nomenclator oficial publicat de ANAF, iar folosirea unui cod inventat sau a unei mapări aproximative produce erori de validare la depunere.

## Temeiul legal

::: ghid-temei
„Tax Table (Tabelă taxe) - Conţine informaţii specifice despre taxe. În funcţie de tipul de taxă (de exemplu, TVA), contribuabilul/plătitorul va selecta codurile de taxă din nomenclatorul Coduri de taxă TVA pentru operaţiuni, asociate operaţiunilor incluse în fişierul SAF-T. [...]
UOMTable (Tabela unităţilor de măsură - UOM) - Conţine detalii cu privire la unităţile de măsură, pentru situaţiile în care este necesară conversia stocurilor între diverse unităţi de măsură, conform nomenclatorului Unităţi de măsură, care face parte integrantă din schema SAF-T. [...]
MovementType Table (Tabelă tipuri mişcări) - Conţine tipurile de mişcare şi subtipurile de mişcare asociate mişcărilor privind stocurile, definite prin nomenclatorul Codificare mişcări de produse în stocuri, care face parte integrantă din schema SAF-T."
— OPANAF 1783/2021, Anexa privind procedura de depunere a Declarației informative D406, descrierea structurii MasterFiles (sursă: anaf_surse/opanaf_1783_2021_saft_d406.txt)
:::

Nomenclatoarele relevante, așa cum sunt descrise în documentația tehnică oficială:

- **TaxCode** — nomenclatorul codurilor de taxă, folosit pentru clasificarea TVA a fiecărei linii de operațiune (cotă, scutire, taxare inversă etc.).
- **UnitOfMeasure** — nomenclatorul unităților de măsură; important de reținut că nu e nomenclatorul unităților românești uzuale, ci cel bazat pe recomandarea internațională UN/ECE Recommendation 20.
- **MovementType / StockMovementType** — nomenclatorul oficial al codificării mișcărilor de stoc, cu un set fix de coduri pentru tipurile de mișcare de produse (intrare, ieșire, transfer etc.).
- **PaymentMethod** — nomenclatorul metodelor de plată, cod de două cifre, folosit la secțiunea de documente sursă (detaliat în anexa cu structura tehnică a fișierului SAF-T, nu în textul propriu-zis al OPANAF 1783/2021).

## Ce se greșește în practică

- Se folosesc unități de măsură românești uzuale (buc, kg) direct, fără mapare la codul UN/ECE cerut de nomenclatorul oficial UnitOfMeasure.
- Se completează un cod de mișcare de stoc „aproximativ" pentru o operațiune care nu are corespondent exact, în loc să se verifice nomenclatorul complet al celor 19 coduri oficiale.
- Se raportează pe o structură XML/nomenclatoare vechi, fără verificarea ultimei versiuni publicate de ANAF pentru anexa tehnică a D406 (structura de bază e aprobată prin OPANAF 1783/2021; modificările ulterioare, cum e OPANAF 407/2025, pot viza alte elemente ale procedurii, de exemplu categoriile și datele de la care se aplică obligația, nu neapărat nomenclatoarele XML).

## Ce face iConta.eu

iConta.eu mapează automat operațiunile firmei (facturi, mișcări de stoc, metode de plată) la codurile din nomenclatoarele oficiale ANAF pentru SAF-T, folosind sursele publicate de ANAF, nu o listă proprie aproximativă. Acolo unde nomenclatorul ANAF nu conține o mapare directă pentru o sursă de date din aplicație, diferența e păstrată vizibil ca atare, nu completată cu o valoare inventată.

[iConta.eu](/)
