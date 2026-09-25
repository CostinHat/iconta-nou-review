---
title: "Înregistrarea noilor asociați străini la ONRC"
description: "Regula legală pentru intrarea unui nou asociat — inclusiv străin — într-un SRL prin cesiune de părți sociale și înscrierea ei la registrul comerțului."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Înregistrarea noilor asociați străini la ONRC

Un nou asociat, cetățean străin sau persoană juridică străină, intră de regulă într-un SRL existent prin cesiune de părți sociale — fie de la un asociat existent, fie printr-o majorare de capital cu aport nou. Legea nu face distincție de cetățenie sau naționalitate pentru procedura de transmitere: regulile de mai jos se aplică oricărui asociat nou, indiferent de unde vine.

## Temeiul legal

::: ghid-temei
„Dacă actul constitutiv nu prevede altfel, transmiterea către persoane din afara societății este permisă numai dacă a fost aprobată de asociați reprezentând cel puțin trei pătrimi din capitalul social."
— Legea 31/1990, art. 202 alin. (2) (sursă: anaf_surse/legea_31_1990_societatile.txt)
:::

- **Aprobarea prealabilă**: intrarea unui asociat nou (deci și a unuia străin) prin cesiune de părți sociale către o persoană din afara societății cere, dacă actul constitutiv nu prevede altă majoritate, votul asociaților reprezentând cel puțin 3/4 din capitalul social.
- **Înscrierea, obligatorie pentru efect**: „Transmiterea părților sociale trebuie înscrisă în registrul comerțului și în registrul de asociați al societății" — art. 203 alin. (1).
- **Momentul opozabilității față de terți**: „Transmiterea are efect față de terți numai din momentul înscrierii ei în registrul comerțului" — art. 203 alin. (2). Până la înscriere, noul asociat nu e opozabil terților, chiar dacă între părți contractul de cesiune e deja semnat.
- Pentru un asociat persoană fizică străină sau persoană juridică străină, datele de identificare cerute în actul constitutiv/actul modificator urmează aceleași reguli generale de identificare din art. 7 lit. a) (nume, act de identitate/pașaport, respectiv firma și naționalitatea pentru persoana juridică).

## Ce se greșește în practică

- Se consideră cesiunea de părți sociale valabilă și opozabilă terților din momentul semnării contractului între cedent și cesionar, ignorând că efectul față de terți curge abia de la înscrierea la registrul comerțului.
- Se omite aprobarea prealabilă a celorlalți asociați (majoritatea de 3/4 din capitalul social), atunci când actul constitutiv nu prevede o regulă diferită.
- Se presupune că pentru un asociat străin există o procedură ONRC separată, cu cerințe suplimentare de cetățenie — legea nu prevede o astfel de distincție la nivelul art. 202-203, mecanismul fiind identic pentru orice cesionar, rezident sau nerezident.

## Ce face iConta.eu

Din verificarea codului, iConta.eu **nu are o funcționalitate pentru cesiunea de părți sociale sau pentru înregistrarea la ONRC a unui asociat nou**, fie el român sau străin. Singurul modul învecinat, F007 (`core/asociati_import_api.py`), importă o listă de asociați (nume, CNP/CUI, cotă) dintr-un fișier .xlsx/.csv, exclusiv la migrarea unei firme deja existente în aplicație — nu depune și nu generează nimic către registrul comerțului, iar validarea CNP din import acoperă doar formatul românesc de 13 cifre, fără o logică dedicată identificării asociaților străini. Cesiunea de părți sociale și depunerea la ONRC rămân, la acest moment, în afara iConta.eu.

[iConta.eu](/)
