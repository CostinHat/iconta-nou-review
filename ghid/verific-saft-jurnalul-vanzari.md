---
title: "Cum verific SAF-T cu jurnalul de vânzări"
description: "Ce cere legea de la fișierul standard de control fiscal privind concordanța cu evidența contabilă și cum se verifică efectiv legătura cu jurnalul de vânzări."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum verific SAF-T cu jurnalul de vânzări

Declarația D406 (SAF-T) trebuie să reflecte fidel evidența contabilă a firmei — inclusiv veniturile din vânzări, așa cum apar în jurnalul de vânzări. Diferențele dintre cele două nu sunt doar riscuri estetice: pot semnala facturi pierdute, duplicate sau mapate greșit la generarea declarației.

## Temeiul legal

::: ghid-temei
„ART. 59^1 Obligația de depunere a fișierului standard de control fiscal
(1) Contribuabilul/Plătitorul are obligația de a depune la organul fiscal central o declarație cuprinzând informații din evidența contabilă și fiscală, denumită în continuare fișierul standard de control fiscal.

(2) În scopul efectuării inspecției fiscale, organul de inspecție fiscală procedează la: [...] b) verificarea concordanței dintre datele din declarațiile fiscale cu cele din evidența contabilă și fiscală a contribuabilului/plătitorului, inclusiv din fișierul standard de control fiscal."
— Legea nr. 207/2015 (Codul de procedură fiscală), art. 59^1 alin. (1) și art. 113 alin. (2) lit. b) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Principiul e simplu: SAF-T nu e o declarație independentă de evidența contabilă, ci o **reflectare** a ei. De aceea legea prevede explicit, printre atribuțiile organului fiscal, verificarea concordanței dintre declarațiile fiscale (inclusiv D406) și evidența contabilă din care provin. Practic, pentru firmă asta înseamnă:

- Totalurile din secțiunea de facturi de vânzare a SAF-T trebuie să corespundă cu ce apare în jurnalul de vânzări al firmei, pentru aceeași perioadă.
- O diferență (factură lipsă din SAF-T, factură dublată, sumă mapată pe alt cont) e exact genul de discrepanță pe care organul fiscal o poate identifica la o verificare, iar responsabilitatea corectării ei revine contribuabilului.
- Verificarea nu se limitează la totalul general — se face, de regulă, cont cu cont și document cu document, pentru a localiza exact unde apare prima diferență.

## Ce se greșește în practică

- Se verifică doar totalul general al TVA colectate din SAF-T față de jurnalul de vânzări, fără verificare document cu document — o eroare de mapare pe o factură poate rămâne ascunsă dacă alte erori o compensează valoric.
- Se presupune că, odată generat, SAF-T e automat corect, fără o verificare independentă față de sursa contabilă — declarația reflectă exact ce a fost mapat la generare, inclusiv eventualele erori de mapare.
- Se ignoră reconcilierea pentru lunile fără mișcări sau cu volum redus, considerându-se că „nu au ce să difere" — tocmai lunile cu puține tranzacții pot ascunde o eroare de tip „factură lipsă" mai ușor de observat altfel.

## Ce face iConta.eu

Verificat în cod: modulul `core/d406_reconciliere.py` implementează o a doua cale de verificare pentru D406 — construiește independent o balanță de rulaje per cont, direct din înregistrările contabile, și o compară cu totalurile per cont din SAF-T-ul deja emis, blocând declarația (nu o corectează tăcut) dacă apare o divergență. Acest gard acoperă secțiunea de note contabile (`GeneralLedgerEntries`), cu dubla partidă verificată. **Limita declarată explicit în cod**: gardul „NU acoperă sub-secțiunile SalesInvoices/PurchaseInvoices/Payments/Assets/MovementOfGoods" — reconcilierea linie cu antet pentru facturi există doar **parțial**. Verificarea completă a concordanței dintre secțiunea de facturi de vânzare din SAF-T și jurnalul de vânzări rămâne, în acest moment, o zonă de acoperire parțială, care merită atenție suplimentară din partea contabilului.

[iConta.eu](/)
