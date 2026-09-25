---
title: "Cum verific D406 cu D394?"
description: "De ce D406 (SAF-T) și D394 sunt declarații cu scop diferit, ce le leagă structural și de ce iConta.eu nu are un modul dedicat care le compară automat."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum verific D406 cu D394?

D406 (SAF-T) și D394 provin, în bună măsură, din aceleași documente — facturile firmei — dar nu raportează același lucru. D406 e o evidență contabilă completă, cerută în scopuri de audit fiscal computerizat; D394 e o declarație informativă de TVA, limitată la operațiunile taxabile pe teritoriul național. A le „verifica una cu cealaltă" înseamnă, de fapt, a înțelege unde se suprapun și unde nu.

## Temeiul legal

::: ghid-temei
„Fişierul standard de control fiscal (SAF-T) se transmite de către contribuabili/plătitori prin intermediul Declaraţiei informative privind fişierul standard de control fiscal, denumită în continuare Declaraţia informativă D406."
— OPANAF 1783/2021, art.2 (sursă: anaf_surse/opanaf_1783_2021_saft_d406.txt:23-26)
:::

- D406 raportează date extrase din evidența contabilă și fiscală a firmei (SAF-T — standard internațional OECD), pentru testarea substanțială a controalelor și datelor de către organele fiscale — o evidență de ansamblu, nu doar TVA.
- D394, în schimb, raportează strict operațiunile taxabile efectuate pe teritoriul național de persoanele înregistrate în scopuri de TVA, cu excluderile deja cunoscute (achiziții intracomunitare, importuri, exporturi din categoria achizițiilor cu taxare inversă).
- Nu există în sursele disponibile un text normativ care să ceară explicit corelarea/compararea celor două declarații — fiecare are propriile reguli de completare și propriul termen de depunere, independente una de alta.

## Ce se greșește în practică

- Se așteaptă ca totalurile din D406 (secțiunile de facturi de vânzare/cumpărare) să coincidă exact cu cele din D394, ignorând că D406 include operațiuni pe care D394 le exclude (importuri, achiziții intracomunitare) și invers, poate exclude operațiuni manuale pe care D394 le include.
- Se tratează o eventuală neconcordanță între D406 și D394 ca eroare automată, fără a verifica întâi dacă diferența vine dintr-o categorie de operațiuni cu tratament declarativ diferit.
- Se presupune că o reconciliere internă din aplicație acoperă automat și comparația între cele două declarații, deși fiecare are propriul ei mecanism de verificare, separat.

## Ce face iConta.eu

Fiecare declarație are propriul „gard de conținut" — o a doua cale de calcul, independentă, care recalculează valorile din datele brute și oprește generarea la divergență: `core/d394_reconciliere.py` pentru D394 și `core/d406_reconciliere.py` pentru D406 (aceasta din urmă verifică dubla partidă a notelor contabile, Σdebit = Σcredit, față de o balanță de rulaje calculată separat). **Nu există însă un modul care compară D406 cu D394 între ele** — fiecare declarație e verificată doar față de propriile date sursă, nu una față de cealaltă.

Un detaliu de fond, relevant pentru firmele trimestriale: până la o reparație recentă din cod, fereastra de date a D406 pentru o firmă cu perioadă fiscală trimestrială acoperea o singură lună din trei, în timp ce D300 și D394 pe același trimestru le conțineau pe toate — inconsecvență acum corectată, astfel încât fereastra D406 urmează aceeași perioadă fiscală de TVA ca D300/D394. Chiar și așa, nicio funcție din aplicație nu pune cele două declarații una lângă alta pentru comparație — dacă vrei să verifici coerența lor, rămâne un pas manual.

[iConta.eu](/)
