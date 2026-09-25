---
title: "Cum se raportează importurile în SAF-T?"
description: "Baza legală a raportării prin fișierul standard de control fiscal (D406/SAF-T) și limitele informației disponibile despre tratamentul specific al importurilor."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se raportează importurile în SAF-T?

Fișierul standard de control fiscal (SAF-T), depus prin D406, cere transferul electronic al evidenței contabile și fiscale către ANAF. Întrebarea „cum raportez importurile" ține însă de structura tehnică XML a fișierului (schema XSD oficială), nu doar de textul ordinului care instituie obligația — o distincție importantă pentru orice contribuabil care importă mărfuri din afara UE.

## Temeiul legal

::: ghid-temei
„1. Fişierul standard de control fiscal (SAF-T), prevăzut la art. 59^1 alin. (1) din Legea nr. 207/2015 privind Codul de procedură fiscală, cu modificările şi completările ulterioare, reprezintă un standard internaţional utilizat pentru transferul electronic de date din evidenţa contabilă şi fiscală, de la contribuabili/plătitori către autorităţile fiscale şi auditori."
— OPANAF 1783/2021, anexa 1, pct. 1 (sursă: anaf_surse/opanaf_1783_2021_saft_d406.txt)
:::

Ce se poate confirma din sursele disponibile:

- Obligația de raportare SAF-T acoperă evidența contabilă și fiscală **în ansamblu** — operațiunile de import, ca achiziții de bunuri, intră în această evidență la fel ca orice altă achiziție, fiind înregistrate contabil pe baza documentului de recepție și a declarației vamale de import (DVI).
- Termenele de transmitere D406 diferă pe categorii de contribuabili (mari, mijlocii, mici) — stabilite prin anexele ordinului, nu printr-un termen unic pentru toți.
- Structura tehnică exactă (secțiunea XML în care se încadrează o achiziție prin import — de regulă în `SourceDocuments > PurchaseInvoices`, cu referință la documentul vamal, dar posibil cu câmpuri specifice) e dată de **schema XSD oficială SAF-T**, un document tehnic de validare, nu un act normativ, și nu se regăsește într-o formă citabilă verbatim în sursele consultate aici.

**Limitare onestă:** nu am găsit, în sursele disponibile, un text normativ care să detalieze explicit tratamentul distinct al importurilor față de achizițiile interne/intracomunitare în structura D406. Regulile de validator (XSD) nu sunt normă fiscală și cer verificare separată, direct pe schema oficială — nu pe presupuneri.

## Ce se greșește în practică

- Se raportează importul ca achiziție internă simplă, fără referință la documentul vamal care îl individualizează.
- Se presupune că importurile au o secțiune SAF-T complet separată de achizițiile interne, deși structura generală de „achiziții" din SourceDocuments e comună.
- Se ignoră corelarea dintre baza de impozitare TVA la import (stabilită conform art. 289 din Codul fiscal) și valoarea raportată în SAF-T, care trebuie să coincidă cu evidența contabilă.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu are un tratament distinct pentru importuri** în generatorul de D406/SAF-T — nu există, în codul modulelor `core/d406.py`, `core/d406_active.py` sau `core/d406_stocuri.py`, o secțiune dedicată operațiunilor de import sau declarațiilor vamale. Importurile ajung în declarație pe același flux ca orice altă achiziție înregistrată contabil.

[iConta.eu](/)
