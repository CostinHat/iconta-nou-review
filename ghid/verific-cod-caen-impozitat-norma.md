---
title: "Cum verific dacă un cod CAEN poate fi impozitat la normă de venit?"
description: "Codul fiscal nu ține o listă fixă de coduri CAEN eligibile pentru normă de venit — nomenclatorul se stabilește anual, iar verificarea se face la direcția regională a finanțelor publice."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum verific dacă un cod CAEN poate fi impozitat la normă de venit?

Normă de venit înseamnă că statul stabilește dinainte o sumă fixă de impozitat pentru activitatea respectivă, indiferent de venitul real obținut. Nu orice activitate poate fi impozitată așa — Codul fiscal lasă stabilirea listei de activități eligibile, pe coduri CAEN, în sarcina Ministerului Finanțelor, iar nivelul normei, în sarcina direcțiilor regionale.

## Temeiul legal

::: ghid-temei
„Ministerul Finanțelor Publice elaborează nomenclatorul activităților pentru care venitul net se poate determina pe baza normelor anuale de venit, care se aprobă prin ordin al ministrului finanțelor publice, în conformitate cu activitățile din Clasificarea activităților din economia națională - CAEN, aprobată prin ordin al președintelui Institutului Național de Statistică. Direcțiile generale regionale ale finanțelor publice, respectiv a municipiului București au următoarele obligații: a) stabilirea nivelului normelor de venit; b) publicarea acestora, anual, în cursul trimestrului IV al anului anterior celui în care urmează a se aplica, precum și a coeficienților de corecție stabiliți prin consultarea consiliilor județene/Consiliului General al Municipiului București, după caz."
— Codul fiscal (Legea 227/2015), art. 69 alin. (2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Din text rezultă un mecanism în doi pași, nu o listă unică valabilă pe toată țara:

- **Nomenclatorul activităților** eligibile pentru normă de venit se aprobă prin ordin al ministrului finanțelor, pe coduri CAEN — deci prima verificare e dacă activitatea PFA-ului apare deloc în acest nomenclator.
- **Nivelul concret al normei** (suma în lei) se stabilește separat, de fiecare direcție generală regională a finanțelor publice, și se publică anual, în trimestrul IV al anului anterior celui de aplicare — ceea ce înseamnă că aceeași activitate poate avea o normă diferită de la un județ la altul.

## Ce se greșește în practică

- Se caută codul CAEN direct în Codul fiscal, care nu conține nicio listă de coduri — nomenclatorul e un act separat, emis prin ordin al ministrului finanțelor.
- Se presupune că norma valabilă în alt județ se aplică și la sediul propriu — nivelul normei se stabilește pe direcție regională, nu unitar la nivel național.
- Se verifică nomenclatorul o singură dată, la înființarea PFA-ului, și nu se mai reface verificarea anual, deși nomenclatorul și nivelurile normelor se pot schimba de la un an la altul.

## Ce face iConta.eu

iConta.eu **nu are încărcat nomenclatorul de coduri CAEN eligibile pentru normă de venit** și nu determină automat dacă o activitate poate fi impozitată astfel. Această verificare rămâne, la data acestui ghid, în sarcina contabilului sau a antreprenorului, consultând ordinul ministrului finanțelor și nivelurile publicate de direcția regională competentă.

Odată ce s-a stabilit că activitatea e la normă de venit, aplicația oferă un **Registru de evidență fiscală pentru persoane fizice**, care aplică mecanic regula din OMFP 3254/2017, art. 1 alin. (2): la normă de venit se completează doar partea de venituri, iar dacă se introduce o valoare la cheltuieli deductibile, înscrierea e respinsă.

[iConta.eu](/)
