---
title: Raportarea operațiunilor scutite de TVA în SAF-T
description: SAF-T (D406) nu exclude operațiunile scutite de TVA din raportare — acestea rămân în fișier, cu indicarea distinctă a tipului de scutire, potrivit obligației legale de la art. 59^1 din Codul de procedură fiscală.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se raportează operațiunile scutite de TVA în SAF-T?

O greșeală frecventă e să crezi că, fiindcă o operațiune nu generează TVA de plată, poate fi omisă din SAF-T. Fals — fișierul standard de control fiscal raportează toate operațiunile din evidența contabilă și fiscală, inclusiv cele scutite, doar cu tratamentul lor fiscal marcat distinct.

### Baza legală a obligației SAF-T

Obligația de transmitere a fișierului standard de control fiscal (SAF-T) e reglementată prin art. 59^1 din Codul de procedură fiscală (Legea nr. 207/2015), iar structura tehnică și termenele sunt stabilite prin OPANAF nr. 1783/2021 privind natura informațiilor pe care contribuabilul/plătitorul trebuie să le declare prin SAF-T, modelul de raportare, procedura și condițiile de transmitere. Anexa nr. 5 a acestui ordin (structura tehnică a fișierului) a fost modificată prin OPANAF nr. 407/2025.

### De ce operațiunile scutite rămân în fișier

SAF-T reflectă integral evidența contabilă și fiscală a firmei, nu doar operațiunile taxabile — scopul lui e să permită organelor fiscale accesul la datele complete din contabilitate, pentru confruntarea declarațiilor depuse (D300, D390, D394) cu realitatea din evidențe. Omiterea operațiunilor scutite ar face fișierul incomplet și ar genera automat discrepanțe la confruntarea cu jurnalele de vânzări/cumpărări.

Practic, fiecare linie de factură raportată în SAF-T poartă informația despre regimul de TVA aplicat — taxabilă la cota standard/redusă, scutită cu drept de deducere (de exemplu exportul, conform art. 294 din Codul fiscal) sau scutită fără drept de deducere (de exemplu serviciile medicale, conform art. 292 din Codul fiscal) — nu se raportează un total agregat fără distincție.

### Cele două categorii de scutiri și diferența lor

- **Scutiri fără drept de deducere** (art. 292 din Codul fiscal) — operațiuni de interes general (servicii medicale, educaționale, financiar-bancare, de asigurare) pentru care furnizorul nu colectează TVA, dar nici nu-și poate deduce TVA-ul aferent achizițiilor legate de acele operațiuni.
- **Scutiri cu drept de deducere** (art. 294 din Codul fiscal) — în principal exportul de bunuri și operațiunile asimilate, pentru care furnizorul nu colectează TVA, dar își păstrează dreptul de deducere a TVA-ului aferent achizițiilor.

Distincția contează pentru SAF-T pentru că afectează, indirect, și calculul pro-rata de deducere raportat prin fișier, dacă firma desfășoară ambele tipuri de operațiuni (taxabile și scutite fără drept de deducere).

### Practic

1. Verifică, în programul de contabilitate/facturare, că fiecare factură emisă pentru o operațiune scutită are marcat corect codul de TVA aplicabil (scutit cu sau fără drept de deducere), nu doar "0% TVA" generic.
2. Nu exclude facturile scutite din exportul de date pentru SAF-T — trebuie incluse, cu indicatorul corect de regim fiscal.
3. Dacă firma are atât operațiuni taxabile, cât și scutite fără drept de deducere, verifică separat cum se reflectă pro-rata de deducere în secțiunile relevante ale fișierului, pentru consecvență cu decontul de TVA (D300) depus pentru aceeași perioadă.
4. Structura tehnică exactă (câmpuri, coduri, format XML) se verifică direct în ultima versiune a Anexei nr. 5 la OPANAF nr. 1783/2021, așa cum a fost modificată prin OPANAF nr. 407/2025 — schema se actualizează periodic, deci verifică versiunea aplicabilă perioadei raportate.
