---
title: Verificarea mapării conturilor pentru D406 (SAF-T)
description: Explică ce înseamnă maparea conturilor analitice pe secțiunea GeneralLedgerAccounts din fișierul SAF-T (D406) și ce trebuie verificat pentru ca declarația să nu fie respinsă.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Verificarea mapării conturilor pentru D406 (SAF-T)

Cea mai frecventă sursă de erori la D406 nu e conținutul tranzacțiilor, ci maparea greșită sau incompletă a conturilor contabile în secțiunea GeneralLedgerAccounts. Iată ce trebuie verificat.

### Ce cere structura SAF-T pentru conturi

Fișierul standard de control fiscal (D406), reglementat prin OPANAF 1783/2021, are în secțiunea MasterFiles subsecțiunea **GeneralLedgerAccounts** ("Conturi contabile Registrul-jurnal"). Aceasta conține informații despre fiecare cont folosit — descriere, tip, sold inițial/final debitor și creditor.

Punctul esențial pentru mapare: în această subsecțiune se raportează **atât contul analitic folosit de contribuabil pentru înregistrarea tranzacțiilor, conform planului de conturi aplicabil legislației românești (câmpul AccountID), cât și, opțional, contul contabil pe baza standardului folosit în ERP-ul intern al contribuabilului (câmpul StandardAccountID)**.

Practic:
- **AccountID** trebuie să corespundă exact contului analitic din planul de conturi românesc aplicat de firmă — cel reglementat prin OMFP 1802/2014 pentru firmele care aplică reglementările contabile conforme cu directivele europene.
- **StandardAccountID** e opțional — se completează doar dacă firma folosește intern o clasificare de conturi diferită (ERP internațional) și dorește să o coreleze cu AccountID-ul românesc.

### Ce se verifică concret la mapare

1. **Fiecare cont analitic folosit în perioada de raportare are un corespondent declarat în GeneralLedgerAccounts.** Un cont mișcat în GeneralLedgerEntries dar absent din lista de conturi din MasterFiles produce o inconsistență structurală a fișierului.
2. **Soldurile debitoare și creditoare se raportează ca sume pozitive**, alternativ — nu se raportează solduri negative pentru elementul relevant (regula explicită din OPANAF 1783/2021: „informațiile cu privire la soldurile debitoare, respectiv creditoare se raportează alternativ, ca sume pozitive pentru elementul relevant").
3. **Suma soldurilor finale din GeneralLedgerAccounts trebuie să corespundă cu balanța de verificare reală a firmei** la finalul perioadei — orice cont folosit în tranzacții dar cu sold nereconciliat semnalează o eroare de extragere din contabilitate, nu neapărat de completare a fișierului.
4. **Conturile de clienți și furnizori (Customers/Suppliers) trebuie să conțină contul analitic în care este înregistrat soldul partenerului respectiv** — o mapare greșită aici (cont de furnizor mapat pe un cont de client, de exemplu) generează erori de validare la nivelul secțiunilor Customers/Suppliers, distincte de GeneralLedgerAccounts, dar cu aceeași sursă: planul de conturi analitic folosit intern.

### Termenele care contează pentru verificare

Declarația D406 se transmite lunar sau trimestrial, în funcție de perioada fiscală aplicabilă pentru TVA a contribuabilului, cu termen-limită ultima zi calendaristică a lunii următoare perioadei de raportare (OPANAF 1783/2021, Anexa 4, pct.1-2). Contribuabilii nu sunt sancționați contravențional dacă depun o D406 validă în perioada de grație stabilită (până la 6 luni pentru prima raportare lunară, respectiv 3 luni pentru prima raportare trimestrială) — o fereastră utilă pentru a corecta problemele de mapare descoperite la primele depuneri, fără sancțiune, conform art.337^1 din Codul de procedură fiscală (Legea 207/2015), citat explicit în anexa 4 a OPANAF 1783/2021.

### La eroare semnalată de ANAF

Dacă declarația transmisă are erori identificate de ANAF și a fost comunicată recipisa aferentă, contribuabilul **retransmite integral** D406 corectată — nu sunt admise corecții parțiale prin transmiterea selectivă a înregistrărilor sau câmpurilor corectate (OPANAF 1783/2021, Anexa 4, pct.11-12). Deci verificarea mapării trebuie făcută înainte de transmitere, la nivelul întregului fișier, nu doar la nivelul înregistrării semnalate ca eronată.
