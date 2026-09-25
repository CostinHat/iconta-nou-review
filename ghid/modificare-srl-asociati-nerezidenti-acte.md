---
title: "Modificare SRL cu asociați nerezidenți: acte specifice"
description: "Ce date de identificare cere legea societăților pentru un asociat persoană fizică străină la o modificare a actului constitutiv, și de ce e o procedură de registrul comerțului, nu una contabilă."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Modificare SRL cu asociați nerezidenți: acte specifice

O modificare a actului constitutiv (intrare de asociat nou, cesiune de părți sociale, schimbare de administrator) urmează aceeași procedură la registrul comerțului indiferent de cetățenia asociatului — dar când asociatul e o persoană fizică străină, legea cere explicit ca actul să conțină și **echivalentul CNP-ului**, potrivit legislației lui naționale, alături de actul de identitate/pașaport.

## Temeiul legal

::: ghid-temei
„Datele de identificare [...] includ: a) pentru persoanele fizice: numele, prenumele, codul numeric personal și, dacă este cazul, echivalentul acestuia, potrivit legislației naționale aplicabile, locul și data nașterii, domiciliul/reședința și cetățenia, actul de identitate/pașaportul, seria, numărul, emitentul, data eliberării, perioada de valabilitate."
— Legea 31/1990 (a societăților), art. 8^1 (sursă: anaf_surse/legea_31_1990_societatile.txt)
:::

Pentru un asociat persoană fizică nerezidentă, aceasta înseamnă concret:

- Actul constitutiv modificat trebuie să conțină, în locul CNP-ului românesc, **echivalentul lui potrivit legislației naționale a asociatului** — nu se lasă câmpul necompletat și nu se inventează un CNP.
- Rămân obligatorii toate celelalte date: locul și data nașterii, domiciliul/reședința, cetățenia și datele complete ale actului de identitate sau pașaportului (serie, număr, emitent, data eliberării, valabilitate).
- Pentru asociați persoane juridice străine, art. 8^1 cere în schimb firma, sediul, naționalitatea, numărul de înregistrare din registrul comerțului propriu și, unde există, identificatorul unic la nivel european.
- Actele emise în străinătate (act de identitate, hotărâri, procuri) trec, de regulă, prin cerințele uzuale de recunoaștere pentru documente străine (traducere autorizată, apostilă sau supralegalizare, după caz) — regulile exacte țin de practica registrului comerțului și de convențiile internaționale aplicabile țării de proveniență, subiect pe care nu l-am verificat în corpusul de acte fiscale disponibil pentru acest ghid.

## Ce se greșește în practică

- Se completează actul constitutiv cu un CNP fictiv sau se lasă câmpul gol pentru asociatul străin, în loc să se treacă echivalentul lui legal din țara de origine.
- Se tratează identic persoana fizică și persoana juridică străină, deși setul de date cerut de art. 8^1 e diferit pentru fiecare (date personale vs. date de identificare a societății).
- Se presupune că modificarea cu asociat nerezident are o procedură fiscală separată la ANAF — de fapt, modificarea propriu-zisă e o procedură de registrul comerțului (ONRC); implicațiile fiscale (de exemplu impozitarea dividendelor plătite unui asociat nerezident) sunt un subiect distinct, ulterior înregistrării.

## Ce face iConta.eu

Subiectul acestui ghid — actele și datele de identificare cerute la o modificare a actului constitutiv cu asociat nerezident — este o **procedură de registrul comerțului**, nu o funcționalitate contabilă sau fiscală. iConta.eu **nu are un modul care să întocmească sau să depună acte de modificare la ONRC** — aplicația lucrează cu evidența contabilă și declarativă a firmei deja înregistrate, nu cu actele constitutive ale acesteia.

Ce are aplicația, legat tangențial de asociați și distribuții către ei, e funcționalitatea **Decontări asociați** (notele de dividende, împrumuturi și regularizări, `core/decontari_asociati.py`), care aplică o cotă unică de impozit pe dividende, fără nicio distincție rezident/nerezident și fără logică de convenție de evitare a dublei impuneri. Fiscalitatea specifică unui asociat nerezident (impozitul reținut la sursă, declarația D207, eventuala aplicare a unei convenții de evitare a dublei impuneri) e un subiect separat, needocumentat în acest modul — de tratat distinct de contabil, nu ca funcție automată a aplicației.

[iConta.eu](/)
