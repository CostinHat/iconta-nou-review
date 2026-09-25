---
title: "Cum justific cheltuielile plătite cu cardul firmei?"
description: "Ce documente stau la baza înregistrării în contabilitate a cheltuielilor achitate cu cardul firmei, potrivit Legii contabilității nr. 82/1991."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum justific cheltuielile plătite cu cardul firmei?

Plata cu cardul nu se justifică singură — extrasul de cont arată doar că banii au ieșit din firmă, nu și ce s-a cumpărat sau de ce. Fără documentul care descrie operațiunea propriu-zisă, cheltuiala rămâne nejustificată contabil, indiferent cât de clar e istoricul din aplicația băncii.

## Temeiul legal

::: ghid-temei
„(1) Orice operațiune economico-financiară efectuată se consemnează în momentul efectuării ei într-un document care stă la baza înregistrărilor în contabilitate, dobândind astfel calitatea de document justificativ. (2) Documentele justificative care stau la baza înregistrărilor în contabilitate angajează răspunderea persoanelor care le-au întocmit, vizat și aprobat, precum și a celor care le-au înregistrat în contabilitate, după caz."
— Legea contabilității nr. 82/1991, art. 6 (sursă: anaf_surse/legea_82_1991_consolidat.txt)
:::

Aplicat concret la plățile cu cardul firmei:

- Extrasul de cont bancar sau extrasul de card **nu este, prin el însuși, document justificativ** pentru natura cheltuielii — el confirmă doar mișcarea de bani, nu conținutul economic al operațiunii.
- Documentul justificativ propriu-zis este **bonul fiscal sau factura** emisă de comerciant la momentul plății; fără el, cheltuiala nu poate fi înregistrată corect pe categoria economică reală (combustibil, protocol, materiale etc.), iar deductibilitatea ei devine discutabilă.
- Când plata cu cardul e făcută de un angajat, în interesul firmei, suma se poate reflecta prin contul de avansuri de trezorerie, cu decontare ulterioară pe bază de documente justificative — nu doar prin corespondența cu extrasul de card al firmei.

## Ce se greșește în practică

- Se înregistrează cheltuiala direct din extrasul de cont, fără bonul fiscal sau factura aferentă, mizând pe descrierea tranzacției oferită de bancă — aceasta nu are valoare de document justificativ contabil.
- Se pierd bonurile fiscale pentru plăți mărunte (parcare, combustibil, papetărie), considerându-le neimportante, deși fiecare achiziție plătită cu cardul firmei are nevoie de propriul document justificativ.
- Se confundă justificarea cheltuielii (ce s-a cumpărat, pentru ce scop economic) cu simpla trasabilitate a plății (cine, cât, când) — extrasul de cont acoperă doar a doua parte.

## Ce face iConta.eu

La data acestui ghid, iConta.eu oferă evidența plăților bancare și a documentelor de cheltuială introduse de utilizator, inclusiv reconcilierea extrasului de cont cu facturile/bonurile fiscale asociate (`core/banca.py`, `core/banca_parser.py`), dar **nu poate genera** documentul justificativ lipsă — dacă bonul fiscal sau factura nu a fost păstrată și introdusă, aplicația nu poate justifica singură, din extrasul de card, natura economică a cheltuielii. Colectarea documentului justificativ pentru fiecare plată rămâne responsabilitatea firmei.

[iConta.eu](/)
