---
title: "Cum caut o factură în SPV după număr?"
description: "Ce presupune, tehnic, căutarea unei facturi electronice în Spațiul Privat Virtual și ce oferă, la acest moment, conectorul SPV al iConta.eu."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum caut o factură în SPV după număr?

Spațiul Privat Virtual (SPV) e interfața ANAF prin care contribuabilul accesează mesajele și documentele electronice, inclusiv facturile din sistemul e-Factura. Căutarea unei facturi anume, după numărul ei, ține de modul în care sistemul ANAF (sau aplicația conectată la el) indexează și filtrează documentele descărcate, nu de o regulă fiscală separată.

## Temeiul legal

::: ghid-temei
„k) specificaţiile naţionale de utilizare a facturii electronice - RO_CIUS - specificaţii tehnice de utilizare a elementelor de bază ale facturii electronice aşa cum sunt prevăzute în standardul european SR EN 16931-1, aplicabile la nivel naţional"
— OUG 120/2021, art. 2 alin. (1) lit. k) (sursă: anaf_surse/oug_120_2021.txt)
:::

Ce contează, structural, pentru identificarea unei facturi electronice:

- Fiecare factură electronică transmisă prin RO e-Factura are un identificator propriu (`cbc:ID`, numărul facturii, conform structurii UBL 2.1) și un identificator de încărcare atribuit de sistemul ANAF la momentul upload-ului — cele două numere nu sunt neapărat identice, ceea ce complică o căutare „după număr" dacă nu se știe care dintre ele se caută.
- Regulile operaționale RO_CIUS definesc structura documentului, dar nu impun un mecanism unic, standard, de căutare a facturilor pe SPV — modul de căutare depinde de interfața ANAF folosită sau de aplicația terță conectată prin API la sistemul e-Factura.
- Pentru facturile primite, identificarea corectă a furnizorului și a numărului facturii se face din elementele structurate ale XML-ului (numărul, data, CUI furnizor/client), nu dintr-un rezumat generat manual.

## Ce se greșește în practică

- Se caută o factură doar după numărul intern dat de furnizor, ignorând că sistemul ANAF poate indexa documentele și după identificatorul de încărcare, diferit de numărul facturii.
- Se presupune că orice factură emisă e vizibilă imediat în SPV — între emitere, validare și afișare pot trece intervale de timp, în funcție de procesarea sistemului ANAF.
- Se caută manual în interfața SPV, factură cu factură, fără să se folosească funcțiile de filtrare disponibile (perioadă, CUI partener), ceea ce devine nepractic pentru un volum mare de facturi.

## Ce face iConta.eu

iConta.eu are un conector propriu la sistemul e-Factura al ANAF (autorizare OAuth, apoi upload/descărcare/interogare stare prin API-ul oficial), prin care preia automat facturile primite și le importă în evidența firmei (extrăgând numărul, data, scadența, părțile și sumele direct din XML). La acest moment, aplicația **nu are o funcție dedicată de căutare** a unei facturi individuale, după număr, direct în interfața SPV — facturile importate sunt disponibile în evidența internă a firmei din iConta.eu, unde pot fi identificate din datele deja extrase, dar o căutare directă „în SPV" prin aplicație nu există încă.

[iConta.eu](/)
