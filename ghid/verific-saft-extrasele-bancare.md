---
title: Cum verific SAF-T cu extrasele bancare?
description: Extrasul bancar se verifică față de D406 în două locuri. Soldurile și rulajele contului 5121 din GeneralLedgerAccounts și GeneralLedgerEntries trebuie să fie egale cu extrasul, iar plățile din Payments trebuie să aibă PaymentMethod 03 și să se regăsească pe extras. Temeiul este schema aprobată prin OPANAF 1783/2021.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum verific SAF-T cu extrasele bancare?

Extrasul de cont este singurul document extern, emis de altcineva decât firma, pe care îl puteți pune lângă D406. Tocmai de aceea e cel mai bun test: dacă SAF-T nu se împacă cu extrasul, problema e în contabilitate sau în generarea fișierului, nu la bancă.

### Unde apare banca în D406

Conform anexei 1 la OPANAF 1783/2021, contul bancar se regăsește în trei zone:

- **GeneralLedgerAccounts** (MasterFiles): fiecare cont analitic, cu soldul inițial și soldul final;
- **GeneralLedgerEntries**: înregistrările contabile la nivel de tranzacție, pe contul analitic (AccountID);
- **Payments** (SourceDocuments): plățile și încasările, cu metoda de plată și liniile aferente.

În nomenclatorul de mecanisme de plată din schema ANAF, operațiunile prin bancă au **PaymentMethod 03 („fără numerar”)**. Pentru PaymentMechanism, codurile recomandate sunt 42 (transfer bancar), 48 (card bancar) și 68 (serviciul de plată online).

### Pasul 1: soldurile

Pentru fiecare cont bancar (analiticele lui 5121, câte unul pe bancă și pe valută):

- soldul inițial din GeneralLedgerAccounts trebuie să fie egal cu soldul de deschidere al primului extras din perioadă;
- soldul final trebuie să fie egal cu soldul de închidere al ultimului extras.

La conturile în valută, comparația se face în lei, la cursul folosit în contabilitate. Diferențele de reevaluare trebuie să apară ca înregistrări distincte în registrul-jurnal.

### Pasul 2: rulajele

Rulajul debitor al contului 5121 în GeneralLedgerEntries trebuie să fie egal cu totalul încasărilor de pe extrase. Rulajul creditor trebuie să fie egal cu totalul plăților. Dacă totalurile diferă, căutați:

- comisioane bancare neînregistrate;
- sume în tranzit (contul 581) înregistrate în altă zi decât pe extras;
- extrase înregistrate de două ori sau lipsă.

### Pasul 3: plățile din Payments

Plățile către furnizori și încasările de la clienți trebuie să apară în Payments. Pe fiecare linie se completează contul analitic (SD.P.20), partenerul (CustomerID sau SupplierID), indicatorul debit sau credit și suma. Verificați prin sondaj:

- că o încasare de pe extras apare în Payments cu codul clientului corect și PaymentMethod 03;
- că liniile care nu privesc un client sau un furnizor (comisioane, dobânzi) poartă codul firmei raportoare în câmpurile de partener, conform observațiilor din schemă.

### Exemplu

Extrasul BT pe august 2026 are sold inițial 84.210,50 lei, încasări de 312.000 lei și plăți de 298.750 lei. D406 arată pe 5121.BT rulaj debitor de 312.000 lei, dar rulaj creditor de doar 298.600 lei. Diferența de 150 lei este suma a trei comisioane de administrare neînregistrate. După înregistrarea lor (627 = 5121) și regenerarea fișierului, soldurile se împacă.

### De reținut

- Soldurile inițiale și finale ale fiecărui analitic 5121 din D406 trebuie să fie egale cu extrasele.
- Rulajele debitor și creditor trebuie să fie egale cu totalurile încasărilor și plăților de pe extras.
- Plățile bancare apar în Payments cu PaymentMethod 03. PaymentMechanism se alege dintre 42, 48 sau 68.
- Comisioanele și sumele în tranzit sunt cauzele cele mai frecvente ale diferențelor.
