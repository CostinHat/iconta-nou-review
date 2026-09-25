---
title: La ce curs valutar se calculează TVA în D301?
description: În D301 baza în lei se calculează la ultimul curs BNR sau la cursul băncii de decontare, valabil la data exigibilității taxei (Codul fiscal art. 290 alin. (2); instrucțiunile OPANAF 592/2016). Data exigibilității diferă după tipul operațiunii.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# La ce curs valutar se calculează TVA în D301?

Cursul se ia de la data exigibilității taxei pentru fiecare operațiune declarată. Nu contează data plății și nici data depunerii D301. Particularitatea D301 este că exigibilitatea diferă după tipul achiziției.

### Regula de curs

Codul fiscal art. 290 alin. (2): pentru operațiunile în valută, altele decât importul, se aplică „ultimul curs de schimb comunicat de Banca Națională a României sau ultimul curs de schimb publicat de Banca Centrală Europeană ori cursul de schimb utilizat de banca prin care se efectuează decontările, valabil la data la care intervine exigibilitatea taxei”. Cursul băncii comerciale se poate folosi doar dacă contractul prevede asta.

Instrucțiunile D301 (OPANAF 592/2016, anexa 2, secțiunea „Date privind obligația de plată”) cer completarea coloanei 4 „Curs de schimb” cu „ultimul curs de schimb comunicat de Banca Națională a României sau cursul de schimb utilizat de banca prin care se efectuează decontările, din data la care intervine exigibilitatea taxei pentru operațiunile declarate”. Baza de impozitare este coloana 2 (valoarea în valută) înmulțită cu coloana 4. TVA este baza înmulțită cu cota.

Instrucțiunile nu menționează cursul BCE, deși Codul fiscal îl permite. Varianta fără dubii în D301 rămâne cursul BNR.

### Data exigibilității, pe tip de operațiune

**Achiziții intracomunitare de bunuri** (art. 284 alin. (2)): exigibilitatea intervine la data emiterii facturii de către furnizor. Dacă factura nu e emisă până atunci, intervine pe **15 a lunii următoare** celei în care a avut loc faptul generator.

**Servicii cumpărate din UE sau din afara UE, cu taxare inversă**: exigibilitatea intervine la data faptului generator (art. 282 alin. (1)), adică la data prestării (art. 281 alin. (1)). La serviciile continue, de exemplu abonamente sau chirii, se ia fiecare dată de plată prevăzută în contract. În lipsa unei astfel de prevederi, se ia data emiterii facturii (art. 281 alin. (8)).

### Exemplu

O firmă neînregistrată în scopuri de TVA, care depune D301:

- Primește în martie marfă din Germania, iar furnizorul emite factura pe 2 aprilie. Factura e emisă înainte de 15 aprilie, deci exigibilitatea e **2 aprilie**. Se folosește cursul BNR valabil pentru 2 aprilie.
- Primește în martie marfă din Italia, fără factură până pe 15 aprilie. Exigibilitatea e **15 aprilie**, cu cursul BNR valabil în acea zi.
- Plătește un abonament software din Irlanda, cu scadența de plată pe 10 aprilie. Exigibilitatea e **10 aprilie**.

Pentru o factură de 2.000 euro cu cursul BNR valabil de 5,0800 lei/euro:

- baza: 2.000 × 5,0800 = 10.160 lei;
- TVA 21%: 2.133,60 lei.

Dacă plătești furnizorul la alt curs, diferența e diferență de curs valutar. Nu modifică baza din D301.

### Pași pentru contabil

1. Pentru fiecare document, stabilește tipul operațiunii și data exigibilității.
2. Ia cursul valabil la acea dată, nu cursul din ziua introducerii în contabilitate.
3. Completează coloana 4 cu același curs pe care l-ai folosit în evidență.
4. Dacă ai folosit un curs greșit, corectează prin D301 rectificativă.

### De reținut

- Cursul pentru D301 este cel valabil la data exigibilității taxei (Codul fiscal art. 290 alin. (2)).
- La achizițiile intracomunitare de bunuri, exigibilitatea e data facturii sau 15 a lunii următoare (art. 284 alin. (2)).
- Instrucțiunile D301 cer cursul BNR sau cursul băncii de decontare (OPANAF 592/2016).
