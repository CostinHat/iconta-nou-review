---
title: "Ce diferențe între e-Factura și D406 trebuie corectate?"
description: "De ce apar diferențe între datele din RO e-Factura și fișierul standard de control fiscal D406 (SAF-T) și principiul contabil care obligă la corectarea lor."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce diferențe între e-Factura și D406 trebuie corectate?

RO e-Factura și Declarația informativă D406 (SAF-T) sunt două obligații de raportare distincte, reglementate prin acte normative diferite (OUG 120/2021, respectiv OPANAF 1783/2021), fiecare cu propriile termene și canale de transmitere. Legea nu prevede o procedură explicită de „reconciliere" între cele două, dar ambele trebuie, prin construcție, să reflecte aceleași operațiuni economice reale — orice diferență între ele este, de fapt, un semnal că una dintre cele două raportări nu prezintă corect realitatea contabilă.

## Temeiul legal

::: ghid-temei
„Documentele oficiale de prezentare a activității economico-financiare a persoanelor [...] sunt situațiile financiare anuale, întocmite potrivit reglementărilor contabile aplicabile și care trebuie să ofere o imagine fidelă a poziției financiare, performanței financiare și a altor informații, în condițiile legii, referitoare la activitatea desfășurată."
— Legea 82/1991 (Legea contabilității), art. 9 alin. (1) (sursă: anaf_surse/legea_82_1991_consolidat.txt)
:::

Notă onestă: nu am găsit în corpus un articol care să reglementeze explicit „reconcilierea" dintre RO e-Factura și D406 — cele două obligații sunt reglementate separat (OUG 120/2021 pentru facturarea electronică, OPANAF 1783/2021 pentru SAF-T). Citatul de mai sus este principiul general al imaginii fidele din Legea contabilității, aplicat la această situație, nu un articol specific pe subiect.

- O factură transmisă prin RO e-Factura și înregistrată în contabilitate ar trebui să apară, în perioada corespunzătoare, și în secțiunile de facturi (SalesInvoices/PurchaseInvoices) din fișierul D406 — diferențele apar de regulă din decalaje de perioadă (factură transmisă într-o lună, dar contabilizată în alta), erori de mapare a conturilor sau facturi corectate/stornate doar într-unul dintre cele două fluxuri.
- Fiecare declarație (D406, D394, D112 etc.) are propriile reguli de validare internă (de exemplu, dubla partidă: Σdebit = Σcredit), dar acestea verifică coerența internă a declarației, nu neapărat corespondența ei cu RO e-Factura.
- Principiul din art. 9 al Legii 82/1991 — imaginea fidelă a activității — este temeiul general pentru care orice discrepanță între cele două raportări trebuie investigată și corectată: dacă una dintre ele nu reflectă realitatea economică, nu oferă o imagine fidelă.

## Ce se greșește în practică

- Se presupune că, odată ce o factură a fost transmisă cu succes prin RO e-Factura, ea apare automat corect și în D406 — cele două fluxuri sunt generate separat, din surse de date care pot diverge dacă înregistrarea contabilă nu a fost făcută corect.
- Se ignoră facturile de corecție/stornare emise ulterior — dacă acestea nu ajung, în aceeași perioadă, atât în RO e-Factura, cât și în evidența contabilă din care se generează D406, apar diferențe greu de urmărit ulterior.
- Se depune D406 fără o verificare prealabilă a balanței de rulaje pe conturi, ceea ce poate lăsa nedetectate note contabile lipsă sau duplicate care nu se reflectă corect nici în facturile raportate.

## Ce face iConta.eu

iConta.eu are integrare atât cu RO e-Factura (`efactura_send.py`, `efactura_import.py`), cât și cu generarea Declarației D406 (`d406.py`), fiecare declarație fiscală generată de aplicație (D406, D394, D301, D390, D112 etc.) trecând printr-un modul propriu de reconciliere care recalculează independent balanța și blochează generarea în caz de dezechilibru (de exemplu, `d406_reconciliere.py` verifică Σdebit = Σcredit pe baza notelor contabile, separat de motorul de generare). La verificarea codului nu am găsit însă o funcție dedicată care să compare direct, linie cu linie, facturile din RO e-Factura cu secțiunile de facturi din D406 — reconcilierile existente verifică fiecare declarație împotriva propriei evidențe contabile, nu una față de cealaltă.

[iConta.eu](/)
