---
title: Cum se raportează furnizorii din afara UE în SAF-T
description: Explică unde apar furnizorii extracomunitari în fișierul SAF-T (D406) — în secțiunea Suppliers și în Purchase Invoices — și cum se separă achizițiile din import de cele intracomunitare.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se raportează furnizorii din afara UE în SAF-T

Fișierul standard de control fiscal nu are o secțiune separată pentru „furnizori din afara UE" — ei intră în aceleași subsecțiuni ca orice alt furnizor, cu diferența că operațiunile asociate lor trebuie încadrate corect ca import, nu ca achiziție intracomunitară.

### Unde apar furnizorii, indiferent de țară

Declarația informativă D406, reglementată prin OPANAF 1783/2021, cere raportarea tuturor furnizorilor în subsecțiunea **Suppliers (Furnizori)** din MasterFiles — care conține „informații despre furnizori, precum detaliile de identificare (denumire, adresă, cod de înregistrare fiscală), contul analitic în care este înregistrat soldul furnizorului respectiv, sold inițial creditor/debitor, sold final creditor/debitor etc.". Nu contează dacă furnizorul e din România, din UE sau din afara UE — structura de identificare e aceeași, cu adresa și codul de identificare fiscală completate conform datelor reale ale furnizorului străin (care poate să nu aibă un format de CUI românesc).

### Unde apar tranzacțiile cu ei

Facturile primite de la orice furnizor, inclusiv cele extracomunitare, se raportează în subsecțiunea **Purchase Invoices (Facturi de achiziție)** din SourceDocuments — care conține „informații despre facturile de cumpărare, precum numărul de intrări/facturi, total debit, total credit, informații despre furnizor, data facturii, termen de plată, liniile din factură, indicatorul privind autofacturarea, codul de taxă etc." (OPANAF 1783/2021, Anexa 1).

### Diferența care contează: importul vs. achiziția intracomunitară

Pentru un furnizor din UE, tranzacția e de regulă o **achiziție intracomunitară de bunuri** — cu regim de TVA specific (taxare inversă, autolichidare), declarată și în D390.

Pentru un furnizor din afara UE, tranzacția e de regulă un **import de bunuri** — TVA-ul se datorează la momentul vămuirii, conform declarației vamale de import, nu se autolichidează pe factura furnizorului ca la achizițiile intracomunitare. Diferența de regim trebuie reflectată corect în **Tax Table (Tabelă taxe)**, unde contribuabilul selectează codurile de taxă TVA din nomenclatorul aplicabil, asociate operațiunilor incluse în fișierul SAF-T (OPANAF 1783/2021, Anexa 1) — un import codificat greșit ca achiziție intracomunitară (sau invers) produce o eroare de fond în raportare, chiar dacă furnizorul e corect identificat în MasterFiles.

### O achiziție dintr-un stat non-UE poate schimba și perioada fiscală de TVA

Dacă firma folosește trimestrul calendaristic ca perioadă fiscală de TVA, e important de reținut că regula de schimbare a perioadei fiscale de la trimestru la lună se declanșează la efectuarea unei **achiziții intracomunitare** de bunuri taxabile în România (Codul fiscal art.322 alin.(7)) — o achiziție de import dintr-un stat non-UE nu declanșează, prin ea însăși, această schimbare, pentru că nu e o achiziție intracomunitară în sensul Codului fiscal. Confuzia dintre cele două tipuri de achiziție, la nivelul departamentului financiar, poate duce fie la o schimbare nejustificată de perioadă fiscală, fie la omisiunea uneia necesare.

### Practic, pentru facturile de la furnizori extracomunitari

1. Înregistrează furnizorul în MasterFiles > Suppliers cu datele lui reale de identificare (denumire, adresă, cod fiscal străin dacă există).
2. Raportează fiecare factură de achiziție de la acest furnizor în SourceDocuments > Purchase Invoices, cu codul de taxă corect (import, nu taxare inversă intracomunitară).
3. Verifică dacă documentul-sursă e o declarație vamală de import, nu o factură intracomunitară — asta determină codul de taxă corect din Tax Table.
4. Nu confunda declanșarea schimbării de perioadă fiscală TVA (specifică achizițiilor intracomunitare, Codul fiscal art.322) cu simpla existență a unui furnizor din afara UE.
