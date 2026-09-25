---
title: "Am omis comisioanele bancare din evidență"
description: "De ce corectarea unei omisiuni de contabilizare a comisioanelor bancare depinde de momentul în care e descoperită eroarea, potrivit regulilor de corectare a erorilor contabile din Codul fiscal."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Am omis comisioanele bancare din evidență

O eroare frecventă la firmele care importă manual extrasele bancare este omiterea liniilor de comision (administrare cont, mentenanță card, taxe de transfer) din evidența contabilă. Corectarea nu se face la fel indiferent de moment — Codul fiscal tratează diferit o eroare descoperită în cursul aceluiași an și una descoperită după ce exercițiul financiar respectiv s-a închis.

## Temeiul legal

::: ghid-temei
„(3) Pentru determinarea rezultatului fiscal, erorile înregistrate în contabilitate se corectează astfel: a) erorile care se corectează potrivit reglementărilor contabile pe seama rezultatului reportat, prin ajustarea rezultatului fiscal al anului la care se referă acestea și depunerea unei declarații rectificative în condițiile prevăzute de Codul de procedură fiscală; b) erorile care se corectează potrivit reglementărilor contabile pe seama contului de profit și pierdere sunt luate în calcul pentru determinarea rezultatului fiscal în anul în care se efectuează corectarea acestora."
— Legea nr. 227/2015 (Codul fiscal), art. 19 alin. (3) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Regula împarte corectarea în două căi, în funcție de tratamentul contabil aplicabil:

- Dacă, potrivit reglementărilor contabile, eroarea se corectează **pe seama rezultatului reportat** (de regulă erori semnificative din exerciții anterioare deja închise), rezultatul fiscal al anului la care se referă comisioanele omise se ajustează retroactiv, iar firma trebuie să depună o **declarație rectificativă**.
- Dacă eroarea se corectează **pe seama contului de profit și pierdere curent** (de regulă erori nesemnificative sau descoperite în cursul aceluiași exercițiu), cheltuiala cu comisioanele omise se recunoaște direct în anul în care se face corectarea, fără rectificarea declarațiilor din anii anteriori.
- Alegerea între cele două tratamente nu e discreționară — ea depinde de pragul de semnificație stabilit de politicile contabile ale firmei și de exercițiul la care se referă eroarea, nu de comoditatea corectării.

## Ce se greșește în practică

- Se corectează orice omisiune direct în luna curentă, prin cont de profit și pierdere, chiar și atunci când eroarea privește un exercițiu financiar deja închis și ar trebui tratată pe seama rezultatului reportat, cu declarație rectificativă.
- Se depune declarație rectificativă pentru erori nesemnificative din luna curentă, deși regula permite corectarea directă, mai simplă, prin contul de profit și pierdere al perioadei.
- Se omite reconcilierea soldului contului de disponibilități bancare din contabilitate cu extrasul de cont real, ceea ce face ca omisiunea comisioanelor să treacă neobservată luni la rând.

## Ce face iConta.eu

La data acestui ghid, iConta.eu recunoaște automat tranzacțiile de tip comision din extrasul bancar importat și le contează implicit pe contul 627 (`core/banca.py`, cheia „comision": „taxa adm", „speze", „serviciu bancar"), reducând riscul de omisiune la importurile viitoare. Aplicația **nu corectează retroactiv** și nu depune automat declarații rectificative pentru comisioane omise în exerciții financiare anterioare — decizia privind tratamentul corectării (pe rezultatul reportat sau pe rezultatul curent) rămâne a contabilului.

[iConta.eu](/)
