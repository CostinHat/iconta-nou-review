---
title: "Checklist de conformare e-Factura pentru firme mici"
description: "Ce elemente structurale cere formatul RO_CIUS pentru facturile electronice și ce presupune, practic, conformarea unei firme mici cu sistemul e-Factura."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Checklist de conformare e-Factura pentru firme mici

Sistemul e-Factura nu e doar „trimiterea unui PDF pe SPV" — presupune generarea unei facturi electronice într-un format structurat (UBL 2.1, cu specificațiile naționale RO_CIUS), încărcarea ei prin sistemul RO e-Factura și respectarea unor reguli operaționale specifice.

## Temeiul legal

::: ghid-temei
„k) specificaţiile naţionale de utilizare a facturii electronice - RO_CIUS - specificaţii tehnice de utilizare a elementelor de bază ale facturii electronice aşa cum sunt prevăzute în standardul european SR EN 16931-1, aplicabile la nivel naţional;"
— OUG 120/2021, art. 2 alin. (1) lit. k) (sursă: anaf_surse/oug_120_2021.txt)
:::

Ce presupune, concret, conformarea:

- Factura trebuie generată în formatul electronic structurat impus (UBL 2.1, adaptat prin specificațiile RO_CIUS), nu ca simplu document scanat sau PDF — structura XML trebuie să respecte schema oficială.
- Factura electronică se transmite prin sistemul RO e-Factura, gestionat de ANAF, respectând regulile operaționale naționale specifice (autentificare, format de răspuns, termene de reacție la respingere).
- Elementele obligatorii de bază ale facturii (identificarea părților, datele fiscale, liniile de factură, totalurile) trebuie completate conform structurii RO_CIUS, nu doar conform practicii contabile obișnuite a firmei.

## Ce se greșește în practică

- Se emit facturi „clasice" (PDF, Word) și se presupune că sunt suficiente atât timp cât conțin toate informațiile relevante — dacă firma intră sub obligația e-Factura, doar factura transmisă în format XML structurat, prin sistemul RO e-Factura, are valoare de factură conformă.
- Se ignoră regulile operaționale specifice de transmitere (autentificare, gestionarea răspunsurilor de la sistemul ANAF), presupunând că trimiterea fișierului e suficientă fără confirmarea de la sistem.
- Se completează manual câmpurile facturii fără a respecta strict specificațiile RO_CIUS pentru elementele de bază, ceea ce duce la respingerea facturii de către sistemul ANAF.

## Ce face iConta.eu

iConta.eu generează facturile electronice conform structurii XML UBL 2.1/CIUS-RO și le trimite prin conectorul propriu la sistemul e-Factura al ANAF, folosind fluxul oficial de autorizare OAuth. Aplicația construiește documentul din datele deja existente în evidența facturilor firmei (parteneri, linii de factură, profil fiscal), cu rotunjire fiscală explicită conform regulilor iConta. O limită cunoscută: pentru cumpărător, aplicația reține în prezent doar nume/CUI/adresă liberă, în timp ce CIUS-RO cere orașul ca element separat (BT-52) — până la completarea acestui câmp dedicat în formularul de factură, informația trebuie introdusă corect în câmpul de adresă.

[iConta.eu](/)
