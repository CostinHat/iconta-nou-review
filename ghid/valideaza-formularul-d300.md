---
title: De ce nu se validează formularul D300?
description: D300 este respins când încalcă una dintre regulile de tip „ERR” din structura XML publicată de ANAF pentru decontul aplicabil din august 2025. Cele mai frecvente sunt datele de identificare, combinația dintre tipul decontului și lună, formulele dintre rânduri, oglinda taxării inverse și cererea de rambursare sub 5.000 lei.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# De ce nu se validează formularul D300?

Decontul de TVA, aprobat prin OPANAF 174/2026, este verificat automat pe baza structurii XML publicate de ANAF (versiunea D300_A10.0.0, aplicabilă din 01.08.2025). Structura are două niveluri de mesaje. Un **ERR** blochează depunerea. Un **ATT** este doar o atenționare și nu oprește decontul. Dacă D300 „nu trece”, cauza este aproape întotdeauna una dintre regulile ERR de mai jos.

### 1. Datele de identificare

Mesajele ERR apar dacă:

- CUI-ul este invalid sau inexistent;
- lipsesc denumirea, adresa, numele, prenumele sau funcția declarantului;
- câmpurile banca sau cont sunt necompletate ori conțin caracterele „,” sau „#”;
- codul CAEN lipsește sau nu este în lista de valori (se acceptă și valori din CAEN rev. 2);
- CUI-ul succesorului, dacă este completat, este invalid.

### 2. Tipul decontului nu se potrivește cu luna

Câmpul tip_decont acceptă valorile L, T, S sau A:

- pentru **T** (trimestrial), luna trebuie să fie 02, 03, 05, 06, 08, 09, 11 sau 12;
- pentru **S** (semestrial), luna trebuie să fie 06 sau 12;
- pentru **A** (anual), luna trebuie să fie 12.

Plătitorii trimestriali au o situație specială când fac achiziții intracomunitare în lunile 02, 05, 08 sau 11. Pentru aceste luni se depune decont trimestrial, cu valorile cumulate (01+02, 04+05 etc.). Decontul următor, pentru luna 03, 06, 09 sau 12, se depune ca decont lunar.

### 3. Formulele dintre rânduri

Totalurile trebuie să rezulte din formulele din structură. Orice abatere produce „ERR : calcul”. Exemple:

- R33_2 = MAX(R32_2 − R17_2, 0) și R34_2 = MAX(R17_2 − R32_2, 0): taxa de plată și suma negativă a perioadei;
- R37_2 = R34_2 + R35_2 + R36_2, respectiv R40_2 = R33_2 + R38_2 + R39_2;
- R41_2 = MAX(R37_2 − R40_2, 0) și R42_2 = MAX(R40_2 − R37_2, 0): soldurile finale.

Un rând „din care” nu poate depăși rândul său principal. De exemplu, rd. 17.1 nu poate fi mai mare decât rd. 17.

**Soldurile din decontul anterior.** R35_2 este soldul de plată neachitat din perioada precedentă. R38_2 este suma negativă reportată din perioada precedentă, pentru care nu s-a cerut rambursare. Cele două nu pot fi completate simultan: dacă unul este mai mare decât zero, celălalt trebuie să fie zero.

### 4. Oglinda taxării inverse

Pentru achizițiile intracomunitare și pentru operațiunile cu taxare inversă, TVA-ul se colectează și se deduce în același decont. Validarea cere ca rândul de deducere să fie egal cu rândul de colectare, atât la bază, cât și la TVA. Regulile V_7–V_26 compară, de exemplu, R18 cu R5 și R25 cu R12. Diferențele apar când o factură este introdusă doar pe o parte.

### 5. Metoda simplificată bifată greșit

Dacă este bifată „metoda simplificată pentru operațiuni interne” (bifa_interne = 1), rândurile de operațiuni intracomunitare și taxare inversă enumerate în regula V_1 trebuie să fie goale. Altfel apare un ERR explicit.

### 6. Rambursare sub 5.000 lei

Dacă suma negativă de TVA de la sfârșitul perioadei este sub 5.000 lei, câmpul solicit_ramb trebuie să fie N. Cererea de rambursare (D) sub acest prag este respinsă.

### 7. Numărul de evidență și suma de control

Numărul de evidență a plății (23 de caractere, cu sumă de control) și câmpul totalPlata_A se generează automat. Dacă XML-ul este editat manual, aceste valori pot deveni greșite și decontul este respins.

### Ce nu blochează

Mesajele ATT verifică dacă TVA-ul declarat pe un rând se încadrează în cota respectivă ±1%. De exemplu, la cota de 21%, TVA-ul trebuie să fie între 20% și 22% din bază. Nu blochează depunerea, dar merită verificate.

### De reținut

- Citește codul erorii: ERR blochează, ATT doar avertizează.
- Verifică întâi identificarea (CUI, bancă, cont, CAEN) și combinația dintre tipul decontului și lună.
- Totalurile se calculează după formule, nu se completează manual.
- Rândurile de colectare și de deducere pentru taxarea inversă trebuie să fie egale.
- Nu cere rambursare pentru o sumă negativă sub 5.000 lei.
