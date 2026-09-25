---
title: Ce cod de obligație se folosește în D100 pentru impozitul micro?
description: Impozitul pe veniturile microîntreprinderilor se declară în D100 cu codul de obligație 121, adică poziția 5 din Nomenclatorul obligațiilor de plată la bugetul de stat (anexa nr. 3 la OPANAF 587/2016), și se plătește în contul unic 5503.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Ce cod de obligație se folosește în D100 pentru impozitul micro?

Codul de obligație pentru impozitul micro este **121**. În Nomenclatorul obligațiilor de plată la bugetul de stat (anexa nr. 3 la OPANAF 587/2016), impozitul ocupă poziția 5, „Impozit pe veniturile microîntreprinderilor”, cu temeiul legal „art. 47 și 56 din Legea nr. 227/2015”. În structura XML a D100 publicată de ANAF, aceeași poziție are codul 121, perioadă de raportare trimestrială și contul bugetar 5503.

### Poziție în nomenclator și cod de obligație

Documentele folosesc două numerotări și e bine să nu le confunzi:

- **Poziția 5** este numărul din nomenclatorul aprobat prin ordin.
- **Codul 121** este codul obligației din fișierul XML. Tot codul 121 apare în numărul de evidență a plății și în formularul 710.

Nu confunda codul 121 cu alte coduri din nomenclator care au legătură cu regimul micro:

- **125** (poziția 92): diferența de impozit micro redirecționată în plus, obligație distinctă, întemeiată pe Codul fiscal art. 56 alin. (2^3);
- **127**: impozit micro scutit, pentru cooperativele agricole. Figurează în Nomenclatorul obligațiilor scutite de la plată (anexa nr. 3^1) și se declară în tabelul III din D100;
- **103**: impozitul pe profit. Îl folosești doar dacă firma a ieșit din regimul micro.

### Ce cere validatorul pentru codul 121

Specificația structurii D100/710 impune pentru codul 121:

- câmpul de cotă, obligatoriu, cu valoarea 1. Regula este „daca cod_oblig=121 atunci cota = 1”, iar la celelalte coduri câmpul rămâne gol. Valoarea corespunde cotei de 1% din Codul fiscal art. 51 alin. (1), în forma dată de OUG 89/2025;
- relația dintre sume: suma de plată este egală cu suma datorată minus deducerile și reducerile admise, iar suma de restituit este 0;
- perioada trimestrială. La dizolvarea cu sau fără lichidare poate fi raportată orice lună, nu doar 3, 6, 9 sau 12.

### Numărul de evidență a plății

Numărul de evidență a plății are 23 de caractere, compuse astfel:

- pozițiile 1–2: „10”;
- pozițiile 3–5: codul obligației, adică 121;
- pozițiile 6–7: „01”;
- pozițiile 8–11: luna și anul de la sfârșitul perioadei de raportare;
- pozițiile 12–17: scadența, în format ZZLLAA;
- pozițiile 18–21: zerouri;
- ultimele două cifre: suma de control.

Exemplu pentru trimestrul IV 2026, cu scadența la 25 ianuarie 2027: începutul numărului este 10 121 01 1226 250127. Verifică de fiecare dată ca pozițiile 3–5 să conțină 121, nu codul altei obligații.

### Contul bugetar

Nomenclatorul din structura ANAF cere înlocuirea vechiului cont 20470101 cu **5503**. Tabelul I din D100 se numește chiar „Impozite și taxe care se plătesc în contul unic”. Potrivit OPANAF 587/2016, anexa nr. 4, pct. 3.1, tabelul acoperă și poziția 5.

### Pași pentru contabil

1. Verifică în vectorul fiscal al firmei că impozitul micro figurează ca obligație trimestrială.
2. În D100 selectează poziția 5. Programul generează codul 121 și cere cota.
3. Construiește ordinul de plată în contul unic, cu numărul de evidență care conține codul 121.
4. La o corecție prin formularul 710, folosește tot codul 121 și completează din nou cota.

### De reținut

- Impozitul micro are codul 121 în D100 și în 710, adică poziția 5 din nomenclator.
- 125 și 127 sunt obligații diferite, nu variante ale impozitului curent.
- Cota se completează obligatoriu cu 1, și numai pentru codul 121.
- Plata se face în contul unic, cu numărul de evidență care conține codul 121.
