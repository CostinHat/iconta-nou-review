---
title: Cum verific D406 cu jurnalul de cumpărări?
description: Verificarea D406 cu jurnalul de cumpărări se face în trei straturi. Întâi numărul și totalurile facturilor din PurchaseInvoices, apoi codurile de taxă pe grade de deductibilitate și, la final, corespondența cu registrul-jurnal. Temeiul este Codul fiscal art. 321 (evidența operațiunilor) și schema aprobată prin OPANAF 1783/2021.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum verific D406 cu jurnalul de cumpărări?

Jurnalul de cumpărări și subsecțiunea PurchaseInvoices din D406 descriu aceleași facturi. Între ele nu ar trebui să existe diferențe neexplicate. Verificarea are sens pe trei niveluri: totaluri, coduri de taxă și legătura cu contabilitatea.

### De ce trebuie să se potrivească

Codul fiscal art. 321 alin. (1) obligă persoanele impozabile stabilite în România să țină „evidențe corecte și complete ale tuturor operațiunilor”. Alin. (2) extinde obligația la orice operațiune reglementată de titlul TVA. SAF-T este extras din aceleași evidențe. Anexa 1 la OPANAF 1783/2021 descrie PurchaseInvoices ca subsecțiunea cu informații despre „numărul de intrări/facturi, total debit, total credit, informaţii despre furnizor, data facturii, termen de plată, liniile din factură, indicatorul privind autofacturarea, codul de taxă”.

### Nivelul 1: numărul de facturi și totalurile

Schema cere pentru PurchaseInvoices:

- **Number of entries** (SD.PI.1): numărul de facturi;
- **Total Debit / Total Credit** (SD.PI.2, SD.PI.3): totalurile în lei.

Comparați numărul de facturi din jurnal cu SD.PI.1, pentru aceeași perioadă. O diferență înseamnă de obicei o factură lipsă, o factură dublată sau una înregistrată în altă lună decât cea raportată.

### Nivelul 2: codurile de taxă

Legenda codurilor de taxă din schema ANAF împarte achizițiile în familii:

- 300nnn–309nnn: achiziții deductibile 100%;
- 320nnn–329nnn: deductibile 50% cu pro-rata;
- 340nnn–349nnn: deductibile 50%;
- 350nnn–359nnn: nedeductibile 100%;
- 390nnn–399nnn: nedeductibile 50%.

Pentru importuri, schema prevede că factura de import se raportează în PurchaseInvoices cu TaxType 000 și TaxCode 000000.

Grupați jurnalul de cumpărări pe aceleași categorii (deducere integrală, 50%, fără deducere) și comparați baza și TVA pe fiecare categorie cu totalurile pe coduri din D406. O achiziție pe care o tratați cu deducere 50% (de exemplu, un autoturism folosit mixt), dar care e raportată cu un cod 300nnn, arată corect în total și greșit pe categorie.

### Nivelul 3: legătura cu registrul-jurnal

Fiecare factură din PurchaseInvoices trebuie să aibă o înregistrare în GeneralLedgerEntries, pe contul de furnizor (401, 404 etc.), cu același cod de partener (SupplierID). Verificați:

- rulajul creditor al conturilor de furnizori pe perioadă față de totalul facturilor de achiziție;
- rulajul contului 4426 față de TVA din facturile deductibile;
- ca SupplierID să fie identic în MasterFiles, PurchaseInvoices și GeneralLedgerEntries.

### Exemplu

Pe septembrie 2026, jurnalul de cumpărări are 148 de facturi, cu bază de 612.400 lei și TVA de 118.300 lei. D406 are 147 de facturi, cu bază de 604.900 lei. Diferența de o factură, cu baza de 7.500 lei, e o factură de combustibil primită pe 30 septembrie și înregistrată în contabilitate pe 2 octombrie. Soluția este fie reclasificarea în contabilitate, fie acceptarea diferenței de perioadă. Sursa de adevăr trebuie să fie aceeași pentru jurnal și pentru D406.

### De reținut

- Comparați întâi numărul de facturi (SD.PI.1), apoi totalurile, apoi codurile de taxă pe familii de deductibilitate.
- Importurile au TaxType 000 și TaxCode 000000 în PurchaseInvoices.
- Fiecare factură trebuie să aibă corespondent în registrul-jurnal, pe contul de furnizor, cu același SupplierID.
- O diferență corectă ca total, dar greșită pe categorie de deducere, se vede doar la nivelul codurilor de taxă.
