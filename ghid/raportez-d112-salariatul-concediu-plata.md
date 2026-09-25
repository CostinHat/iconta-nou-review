---
title: "Cum raportez în D112 salariatul cu concediu fără plată"
description: "Temeiul legal al concediului fără plată și cum afectează el, structural, câmpurile din declarația 112 privind zilele lucrate."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum raportez în D112 salariatul cu concediu fără plată

Concediul fără plată e un drept al salariatului pentru rezolvarea unor situații personale, nu o sancțiune sau o absență nejustificată — dar din perspectiva declarației 112, zilele de concediu fără plată se tratează diferit de zilele efectiv lucrate, cu efect direct asupra bazei de calcul a unor facilități fiscale.

## Temeiul legal

::: ghid-temei
„Pentru rezolvarea unor situaţii personale salariaţii au dreptul la concedii fără plata."
— Legea 53/2003 (Codul muncii), art. 148 alin. (1)

„Durata concediului fără plata se stabileşte prin contractul colectiv de muncă aplicabil sau prin regulamentul intern."
— Legea 53/2003 (Codul muncii), art. 148 alin. (2)
(sursă: anaf_surse/legea_53_2003_codul_muncii.txt:1790-1794)
:::

Structura oficială a formularului 112 tratează explicit zilele fără plată ca zile care reduc baza favorabilă de calcul, alături de zilele nemotivate — spre deosebire de zilele efectiv lucrate sau de cele de concediu medical, care intră normal în formula de calcul a facilității pe venitul din salarii:

> „B2_5P=((4050-300)/NZL*(zile lucrate+zile CM)) - zilele fara plata si zilele nemotivate se supra-taxeaza"
> — structura tehnică D112 (sursă: anaf_surse/d112_struct_anaf.txt:124-125)

Practic: formula oficială a facilității include explicit zilele lucrate și zilele de concediu medical, dar exclude zilele fără plată și cele nemotivate — acestea două se „supra-taxează", adică nu beneficiază de aceeași proporționare favorabilă.

## Ce se greșește în practică

- Se tratează zilele de concediu fără plată la fel ca zilele efectiv lucrate la calculul bazei facilității fiscale, deși structura oficială a formularului le exclude explicit din acea formulă.
- Se confundă concediul fără plată cu absența nemotivată — sunt tratate similar din perspectiva formulei de mai sus (ambele ies din baza favorabilă), dar au regim juridic complet diferit: concediul fără plată e un drept solicitat de salariat, absența nemotivată e o abatere disciplinară.
- Se presupune că durata concediului fără plată e limitată de lege la un număr fix de zile — Codul muncii lasă durata la latitudinea contractului colectiv de muncă sau a regulamentului intern, fără un plafon legal general.

## Ce face iConta.eu

Cercetarea de fond pentru acest ghid a vizat motorul de calcul al indemnizației de concediu medical (`core/salarizare.py`, calculatorul CM, temei OUG 158/2005) — un motor complet separat de generatorul D112 general al salariilor. Nu s-a verificat, în acest context, dacă și cum motorul de salarizare din iConta.eu (`core/d112.py`, `core/salarizare.py`) implementează formula de mai sus pentru zilele fără plată; acest subiect ține de funcționalitatea generală de calcul al salariului și al declarației 112, nu de calculatorul de concediu medical care a stat la baza acestei cercetări.

[iConta.eu](/)
