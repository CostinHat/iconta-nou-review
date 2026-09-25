---
title: "D205 și declarația unică pentru persoanele fizice"
description: "Impozitul pe dividende reținut la sursă este final, ceea ce înseamnă că un asociat persoană fizică nu mai raportează separat acest venit prin Declarația unică."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# D205 și declarația unică pentru persoanele fizice

Dacă ai primit dividende ca persoană fizică și firma ți-a reținut deja impozitul, nu mai ai, de regulă, nimic de trecut în Declarația unică pentru acest venit — caracterul „final" al impozitului pe dividende rezolvă situația la sursă.

## Temeiul legal

::: ghid-temei
„Veniturile sub formă de dividende, inclusiv câştigul obţinut ca urmare a deţinerii de titluri de participare definite de legislaţia în materie la organisme de plasament colectiv, se impozitează cu o cotă de 16% din suma acestora, impozitul fiind final. Obligaţia calculării şi reţinerii impozitului pe veniturile sub formă de dividende revine persoanelor juridice, odată cu plata dividendelor [...]"
— Legea nr. 227/2015 (Codul fiscal), art. 97 alin. (7) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Consecința directă a caracterului „final" al impozitului:

- **Firma** este cea care calculează, reține și virează impozitul, iar tot firma raportează nominal, pe fiecare beneficiar, prin **Declarația informativă D205** — un document informativ depus de plătitor, nu de beneficiar.
- Fiind impozit final, asociatul persoană fizică **nu recalculează și nu redeclară** acest venit prin Declarația unică privind impozitul pe venit și contribuțiile sociale — spre deosebire de alte categorii de venituri (de exemplu, cele din activități independente), unde contribuabilul însuși are obligații declarative anuale.
- D205 servește ANAF ca instrument de evidență și verificare încrucișată — confirmă că impozitul reținut de firmă a fost corect calculat și virat, nu generează o obligație suplimentară de declarare pentru persoana fizică beneficiară.

## Ce se greșește în practică

- Se raportează, din prudență, veniturile din dividende și în Declarația unică a asociatului, deși impozitul final reținut la sursă nu impune această declarare suplimentară — dublează, inutil, informația deja transmisă de firmă prin D205.
- Se presupune că lipsa unei obligații de declarare pentru asociat înseamnă și lipsa oricărei obligații fiscale legate de dividende — de fapt obligația există, dar este a firmei plătitoare, prin reținere la sursă și prin D205.
- Se confundă D205 (declarație informativă a plătitorului) cu o declarație pe care ar trebui să o depună personal asociatul — D205 se depune de firmă, nu de persoana fizică beneficiară.

## Ce face iConta.eu

Pentru firmă, iConta.eu generează Declarația D205 direct din evidența plăților de dividende (`core/d205.py`), pe fiecare asociat, cu impozitul calculat conform cotei aplicabile la data distribuirii. Aplicația **nu se ocupă de Declarația unică a persoanei fizice** — aceasta este o declarație separată, a contribuabilului individual, în afara sferei de evidență contabilă a firmei pe care o administrează iConta.eu.

[iConta.eu](/)
