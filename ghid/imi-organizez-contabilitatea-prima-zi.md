---
title: "Cum îmi organizez contabilitatea de la prima zi de firmă"
description: "Ce obligații contabile de bază există chiar din prima zi de activitate a unei firme, conform Legii contabilității nr. 82/1991."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum îmi organizez contabilitatea de la prima zi de firmă

Contabilitatea unei firme nu începe „când apar primele facturi" — obligația de a organiza și conduce contabilitatea, de a documenta fiecare operațiune și de a ține registrele contabile obligatorii există din prima zi de existență legală a firmei, indiferent de volumul de activitate.

## Temeiul legal

::: ghid-temei
„Persoanele prevăzute la art. 1 alin. (1)-(4) au obligația să conducă contabilitatea în partidă dublă și să întocmească situații financiare anuale, potrivit reglementărilor contabile aplicabile."
— Legea nr. 82/1991 a contabilității, art. 5 alin. (1) (sursă: anaf_surse/legea_82_1991_consolidat.txt)

„(1) Orice operațiune economico-financiară efectuată se consemnează în momentul efectuării ei într-un document care stă la baza înregistrărilor în contabilitate, dobândind astfel calitatea de document justificativ. (2) Documentele justificative care stau la baza înregistrărilor în contabilitate angajează răspunderea persoanelor care le-au întocmit, vizat și aprobat, precum și a celor care le-au înregistrat în contabilitate, după caz."
— Legea nr. 82/1991 a contabilității, art. 6 (sursă: anaf_surse/legea_82_1991_consolidat.txt)
:::

Din aceste articole rezultă structura de bază pe care orice firmă nou-înființată trebuie s-o pună la punct din prima zi:

- **Contabilitate în partidă dublă**, condusă potrivit reglementărilor contabile aplicabile (pentru majoritatea SRL-urilor, OMFP 1802/2014) — nu contabilitate simplificată, disponibilă doar pentru anumite categorii de entități fără scop patrimonial.
- **Document justificativ pentru fiecare operațiune**, consemnat „în momentul efectuării ei" — o cheltuială sau un venit nu pot fi înregistrate în contabilitate fără actul care le susține (factură, chitanță, contract, dispoziție de plată etc.), iar cine întocmește sau înregistrează un astfel de document răspunde pentru el.
- **Registrele de contabilitate obligatorii** — Registrul-jurnal, Registrul-inventar și Cartea mare (art. 20 din aceeași lege), plus balanța de verificare lunară (art. 22), care confirmă corectitudinea înregistrărilor.

## Ce se greșește în practică

- Se amână organizarea contabilității până la prima factură emisă sau primită, considerând că „nu e nimic de contabilizat" în perioada de dinaintea acesteia — obligația de a conduce contabilitatea curge din prima zi de existență a firmei, nu de la prima tranzacție.
- Se înregistrează cheltuieli sau încasări fără documentul justificativ corespunzător, „pe cuvânt" sau pe baza unui extras de cont fără document-suport — orice înregistrare contabilă trebuie să aibă la bază documentul justificativ, conform art. 6.
- Se aleg din start un plan de conturi și o structură de evidență ad-hoc, fără să se raporteze la reglementările contabile aplicabile (OMFP 1802/2014 pentru majoritatea firmelor) — ceea ce complică ulterior corelarea cu situațiile financiare anuale și cu declarațiile fiscale.

## Ce face iConta.eu

iConta.eu oferă evidența contabilă generală de la înființarea profilului firmei în aplicație: configurarea datelor de identificare și a vectorului fiscal (`core/firma_profil_api.py`, `core/vector_fiscal_api.py`), plan de conturi conform reglementărilor aplicabile, și înregistrarea notelor contabile pe bază de documente justificative introduse de utilizator. Aplicația nu automatizează și nu poate înlocui decizia inițială de organizare (alegerea regimului de impozitare, structura de conturi analitice specifică activității, politicile contabile proprii) — acestea rămân decizii ale contabilului sau ale asociatului, pe care aplicația le reflectă ulterior în evidență.

[iConta.eu](/)
