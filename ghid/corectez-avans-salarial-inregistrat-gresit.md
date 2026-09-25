---
title: "Cum corectez un avans salarial înregistrat greșit?"
description: "Regulile contabile pentru corectarea unei erori de înregistrare a unui avans salarial (chenzinal), în funcție de perioada la care se referă eroarea."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum corectez un avans salarial înregistrat greșit?

Avansul chenzinal (plata parțială a salariului la mijlocul lunii) e un document contabil obișnuit, dar o sumă greșită — introdusă manual sau preluată greșit din pontaj — trebuie corectată după regulile generale de corectare a erorilor contabile, nu prin simpla suprascriere a înregistrării inițiale.

## Temeiul legal

::: ghid-temei
„(1) Erorile constatate în contabilitate se pot referi fie la exercițiul financiar curent, fie la exercițiile financiare precedente. (2) Corectarea erorilor se efectuează la data constatării lor. [...] Înregistrarea stornării unei operațiuni contabile aferente exercițiului financiar curent se efectuează fie prin corectarea cu semnul minus a operațiunii inițiale (stornare în roșu), fie prin înregistrarea inversă a acesteia (stornare în negru), în funcție de politica contabilă și programele informatice utilizate."
— OMFP nr. 1802/2014, pct. 65 și pct. 69 (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

- O eroare se corectează **la data la care e constatată**, nu retroactiv, prin modificarea silențioasă a înregistrării vechi (pct. 65 alin. (2)).
- Corectarea unei erori din **exercițiul financiar curent** se face pe seama contului de profit și pierdere (pct. 67 alin. (1)).
- Corectarea unei erori **semnificative din exerciții financiare anterioare** (deci dintr-un an deja închis) se face pe seama rezultatului reportat, contul 1174 „Rezultatul reportat provenit din corectarea erorilor contabile" (pct. 67 alin. (2)).
- Tehnic, stornarea unei operațiuni din anul curent se face fie „în roșu" (aceeași înregistrare, cu semn minus), fie „în negru" (înregistrare inversă), în funcție de politica contabilă a firmei (pct. 69).
- Documentul care stă la baza avansului chenzinal e statul de salarii: „Plățile făcute în cursul lunii, cum sunt: avansul chenzinal, lichidările, indemnizațiile de concediu etc. se includ în statele de salarii" (OMFP 2634/2015, anexa 2, cod 14-5-1).

## Ce se greșește în practică

- Se modifică direct suma din nota contabilă existentă, în loc să se facă o stornare urmată de înregistrarea corectă — practică ce rupe trasabilitatea și îngreunează un eventual control.
- Se corectează o eroare din luna precedentă direct pe cheltuieli, fără să se verifice dacă exercițiul financiar anterior era deja închis — caz în care corectarea trebuie să treacă prin rezultatul reportat (1174), nu prin contul de profit și pierdere curent.
- Nu se documentează motivul corecției — deși legea cere ca „erorile constatate" să fie identificate și tratate ca atare, nu doar suprascrise.
- Se ignoră impactul asupra statului de plată deja transmis către salariat sau asupra reținerilor (impozit, contribuții) calculate pe baza sumei greșite.

## Ce face iConta.eu

Pentru corectarea notelor contabile în general — inclusiv, la nevoie, pentru un avans salarial înregistrat greșit — iConta.eu folosește un **mecanism intern de stornare**, prezent generalizat în motoarele de contare ale aplicației (facturi, bancă, decont TVA, SAF-T etc.), care respectă principiul din OMFP 1802/2014: corectarea se face printr-o operațiune de stornare, nu prin suprascrierea directă a înregistrării inițiale. Nu există însă, la acest moment, o funcție special dedicată exclusiv „corectării avansului salarial" — statul de plată și salarizarea au module proprii (`plata_salarii.py`, `salarii_contare.py`), dar corecția unei sume greșite urmează logica generală de stornare + re-înregistrare, aplicată manual de utilizator.

[iConta.eu](/)
