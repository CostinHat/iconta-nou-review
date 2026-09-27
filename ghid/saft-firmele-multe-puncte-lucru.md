---
title: SAF-T pentru firmele cu mai multe puncte de lucru
description: D406 se depune o singură dată, pe CUI-ul firmei, și include operațiunile tuturor punctelor de lucru. Punctele de lucru se pot identifica în fișier prin analitice, centre de cost (AnalysisTypeTable), TaxEntity sau depozite, nu prin declarații separate. Structura e stabilită prin OPANAF 1783/2021, iar natura juridică a punctului de lucru prin Legea 31/1990 art. 43.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# SAF-T pentru firmele cu mai multe puncte de lucru

Firma cu cinci puncte de lucru depune un singur D406 pe perioadă. Fișierul conține operațiunile tuturor sediilor, pentru că obligația aparține contribuabilului, iar punctele de lucru nu sunt contribuabili distincți.

### De ce un singur fișier

Legea 31/1990 art. 43 alin. (3) definește agențiile, punctele de lucru și alte sedii secundare ca „dezmembrăminte fără personalitate juridică ale societăților”, menționate doar în înmatricularea societății. Nici sucursalele nu au personalitate juridică (art. 43 alin. (1)).

Conform anexei 1 la OPANAF 1783/2021, antetul fișierului SAF-T cuprinde „compania în numele căreia este depus SAF-T”. În schema publicată de ANAF, codul de identificare al companiei (RegistrationNumber) este CUI-ul, fără prefixul RO pentru plătitorii de TVA. Există deci un singur antet, cu un singur CUI.

Anexa 5 la OPANAF 1783/2021, modificată prin OPANAF 407/2025, listează separat printre obligați „unităţile fără personalitate juridică din România care aparţin unor persoane juridice cu sediul în străinătate”. Acestea sunt sucursalele firmelor străine, cu cod fiscal propriu. Situația nu se aplică punctelor de lucru ale unui SRL românesc.

### Cum se vede punctul de lucru în fișier

Schema oferă mai multe elemente prin care activitatea poate fi atribuită unui sediu, fără declarații separate:

- **Conturi analitice (AccountID).** Anexa 1 cere raportarea contului analitic folosit efectiv. Dacă țineți 5311 sau 707 pe analitice pe punct de lucru (5311.01 Cluj, 5311.02 Turda), ele apar ca atare, iar balanța fișierului se împacă cu balanța internă.
- **Centre de cost (AnalysisTypeTable).** Anexa 1 descrie subsecțiunea ca „detalii cu privire la structura centrelor de cost implementată de contribuabil”. Codurile de analiză pot fi atașate liniilor din registrul-jurnal (câmpul Analysis).
- **TaxEntity**, în antet: câmp opțional, descris ca „referință pentru companie / divizie / sucursală”.
- **TransactionID**: schema arată că poate include „centre de cost, cum ar fi societatea, divizia, regiunea, grupul și sucursala /departamentul”.
- **Depozite (WarehouseID)**, în secțiunea Stocuri: ID-ul depozitului unde se găsesc bunurile, relevant când ANAF solicită această secțiune.

### Probleme practice frecvente

1. **Programe de facturare diferite pe puncte de lucru.** Datele trebuie consolidate înaintea generării SAF-T, cu aceleași coduri de clienți, furnizori și produse. Același client nu poate avea coduri diferite în MasterFiles.
2. **Serii de facturi pe sedii.** Nu e o problemă, cu condiția ca numerele să fie unice și ca SalesInvoices să cuprindă toate seriile.
3. **Casieriile locale.** Fiecare casierie apare în Payments cu PaymentMethod 01, pe analiticul de casă corespunzător.
4. **Fișiere mari.** Raportarea modală din anexa 3 pct. 26-28 la OPANAF 1783/2021 permite împărțirea pe subsecțiuni, nu pe puncte de lucru. Fiecare fișier trebuie să aibă antetul complet al companiei.

### Exemplu

Un SRL cu sediul în Iași și puncte de lucru în Pașcani și Vaslui ține vânzările pe analitice (707.01, 707.02, 707.03) și casele pe 5311.01-03. D406 pe septembrie are un singur antet, cu CUI-ul SRL-ului. SalesInvoices cuprinde seriile IS, PS și VS, iar GeneralLedgerEntries conține toate analiticele. Totalul pe 707 din fișier este egal cu balanța sintetică a firmei.

### De reținut

- Un singur D406 pe CUI, cu toate punctele de lucru incluse.
- Punctele de lucru nu au personalitate juridică (Legea 31/1990 art. 43 alin. (3)) și nu depun SAF-T separat.
- Sediul se identifică în fișier prin analitice, centre de cost, TaxEntity sau depozite.
- Consolidați nomenclatoarele de parteneri și produse înainte de generarea fișierului.
