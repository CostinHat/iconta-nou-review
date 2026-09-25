---
title: "Cum blochez o plată suspectă la bancă"
description: "De ce blocarea unei plăți suspecte ține de banca/instituția de plată, iar organizarea controlului intern care previne o astfel de eroare este, prin lege, responsabilitatea administratorului firmei."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum blochez o plată suspectă la bancă

Când un ordin de plată e trimis din greșeală sau ca urmare a unei fraude (de exemplu, o factură falsă cu un IBAN modificat), procedura tehnică de blocare sau revocare a plății ține de relația contractuală cu banca sau instituția de plată, nu de legislația fiscală — Codul fiscal și Codul de procedură fiscală nu reglementează revocarea ordinelor de plată. Ce reglementează legea contabilității este altceva, dar la fel de relevant: cine răspunde pentru organizarea sistemului de control intern care ar trebui să prevină, în primul rând, ca o astfel de plată să ajungă la bancă.

## Temeiul legal

::: ghid-temei
„Articolul 10 (1) Răspunderea pentru organizarea și conducerea contabilității la persoanele prevăzute la art. 1 alin. (1)-(4) revine administratorului, ordonatorului de credite sau altei persoane care are obligația gestionării entității respective."
— Legea contabilității nr. 82/1991, art. 10 alin. (1) (sursă: anaf_surse/legea_82_1991_consolidat.txt)
:::

Ce înseamnă asta în practică:

- **Blocarea efectivă** a unei plăți deja trimise (dacă mai e posibilă) se solicită direct băncii/instituției de plată, prin canalele ei de urgență — legislația fiscală nu are niciun rol în această etapă.
- **Prevenția** ține însă de organizarea internă a firmei: verificarea IBAN-ului de plată contra celui din contractul/factura originală, principiul „patru ochi" la aprobarea plăților mari și separarea persoanei care introduce plata de cea care o aprobă sunt măsuri de control intern, iar administratorul este, prin lege, responsabil pentru ele.
- Odată ce banii au plecat efectiv, recuperarea lor (dacă frauda s-a consumat) ține de proceduri civile/penale, nu de o „anulare" fiscală sau contabilă a operațiunii.

## Ce se greșește în practică

- Se așteaptă ca sistemul contabil sau aplicația de facturare să „prindă" automat o plată suspectă, deși niciun program de contabilitate nu are acces la fluxul bancar în timp real, pentru a o bloca înainte de decontare.
- Se anulează contabil plata (storno) imediat ce se suspectează frauda, fără confirmarea băncii că suma a fost efectiv recuperată — creând o discrepanță între evidența contabilă și extrasul bancar real.
- Se omite raportarea internă a incidentului către administrator, deși răspunderea pentru organizarea controlului care ar fi putut preveni eroarea îi revine direct, potrivit legii contabilității.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu are nicio conexiune live cu banca** și nu poate iniția, opri sau bloca o plată. Aplicația importă și clasifică automat operațiunile din extrasul de cont (`core/banca.py`, `core/banca_parser.py`), inclusiv recunoașterea automată a comisioanelor bancare, dar acest lucru se întâmplă întotdeauna **după** ce plata a fost deja procesată de bancă. Verificarea unei plăți înainte de a fi trimisă rămâne integral responsabilitatea persoanei care o aprobă.

[iConta.eu](/)
