---
title: "SAF-T și TVA: cum se corelează cu D300"
description: "Ce date trebuie să coincidă între fișierul SAF-T (D406) și decontul de TVA (D300), conform OPANAF 1783/2021, și de ce discrepanțele atrag atenția ANAF."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# SAF-T și TVA: cum se corelează cu D300

SAF-T (declarația D406) nu e o declarație paralelă cu decontul de TVA — e un fișier de control care conține, la nivel de tranzacție, toate elementele din care se compune D300. ANAF poate compara automat cele două surse, iar o discrepanță între ele iese la iveală imediat.

## Temeiul legal

::: ghid-temei
Declarația D406 — Fișierul Standard de Control Fiscal (SAF-T) — se reglementează prin OPANAF 1783/2021, cu Schema XSD oficială ANAF; structura AuditFile cuprinde secțiunea GeneralLedgerEntries (jurnale și tranzacții contabile, inclusiv codurile de TVA aferente fiecărei linii) și SourceDocuments (facturile de vânzare și achiziție, cu liniile lor de TVA).
— OPANAF 1783/2021, structura declarației SAF-T/D406 (sursă: anaf_surse/opanaf_1783_2021_saft_d406.txt)
:::

Corelarea practică dintre SAF-T și D300 se bazează pe faptul că ambele derivă din aceleași operațiuni economice, dar la niveluri diferite de detaliu:

- **D300** raportează sumele agregate ale TVA colectată și deductibilă, pe categorii (rânduri de decont), pentru perioada fiscală;
- **SAF-T** conține, pentru aceeași perioadă, **fiecare tranzacție** individuală (factură de vânzare, factură de achiziție, notă contabilă) cu codul de TVA aferent (`TaxCode`), din care sumele agregate raportate în D300 ar trebui, teoretic, să poată fi reconstituite prin însumare;
- o discrepanță între totalul rezultat din SAF-T (însumarea liniilor cu un anumit cod de TVA) și rândul corespunzător din D300 semnalează fie o eroare de raportare, fie o factură/operațiune omisă dintr-una din cele două declarații — exact tipul de neconcordanță pe care sistemele de analiză de risc ale ANAF sunt construite să-l detecteze automat;
- codificarea corectă a TVA pe fiecare linie de tranzacție din SAF-T (`TaxCode`) trebuie să reflecte cota și regimul real aplicat facturii (cotă standard, redusă, scutire cu/fără drept de deducere, taxare inversă) — o codificare grosieră sau implicită produce, structural, o sursă de neconcordanță cu D300.

## Ce se greșește în practică

- Se generează SAF-T ca un simplu „export" al balanței contabile, fără corelare reală cu liniile de TVA din facturi — sumele agregate din fișier nu mai reflectă exact structura TVA raportată în D300.
- Se folosește un cod de TVA generic/implicit pentru toate achizițiile în SAF-T, indiferent de deductibilitatea reală, în loc să se reflecte codul corect linie cu linie — discrepanța devine vizibilă la orice verificare încrucișată cu D300.
- Se depune SAF-T pentru o perioadă fără nicio operațiune reală ca fiind „completă" cu date fabricate, în loc să se raporteze corect perioada fără mișcări — orice reconstituire a datelor din SAF-T care nu corespunde realității contabile subminează exact scopul declarat al instrumentului: verificarea încrucișată.

## Ce face iConta.eu

iConta.eu generează declarația SAF-T/D406 (`core/d406.py`) direct din schema XSD oficială ANAF, cu un modul dedicat de reconciliere (`core/d406_reconciliere.py`) care verifică liniile facturilor față de antetul documentelor și față de stocuri. Documentația internă a modulului notează explicit stadiul de acoperire: liniile de facturi (vânzare/achiziție) sunt generate cu date reale din facturi, validate structural pe validatorul oficial DUK; codificarea TVA pentru achiziții rămâne, la data acestui ghid, o zonă de rafinare ulterioară (cod de TVA implicit pentru deductibilitate, nu încă pe cazuri reale complete) — exact tipul de detaliu care poate produce discrepanțe față de D300 dacă nu e verificat manual.

[iConta.eu](/)
