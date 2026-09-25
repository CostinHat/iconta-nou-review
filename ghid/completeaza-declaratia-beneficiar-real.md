---
title: "Cum se completează declarația de beneficiar real"
description: "Ce este beneficiarul real al unei firme, cine îl definește legal și de ce declarația privind identificarea lui ține de o lege distinctă de Codul fiscal."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se completează declarația de beneficiar real

Orice societate înregistrată la registrul comerțului trebuie să declare cine sunt „beneficiarii reali" — persoanele fizice care, în cele din urmă, dețin sau controlează firma, chiar dacă nu apar direct ca asociați. Definiția și obligația de declarare nu vin din Codul fiscal sau din Codul de procedură fiscală, ci dintr-o lege dedicată prevenirii spălării banilor, la care actele fiscale doar fac trimitere.

## Temeiul legal

```
::: ghid-temei
„În rubrica «Modalitatea de exercitare a controlului» se menționează modalitatea prin care se exercită controlul în ultimă instanţă asupra fiduciei sau a construcţiei juridice similare, potrivit art. 4 alin.(2) lit.b) din Legea nr.129/2019 pentru prevenirea şi combaterea spălării banilor şi finanţării terorismului, precum şi pentru modificarea şi completarea unor acte normative, cu modificările și completările ulterioare."
— OPANAF nr. 2175/2025, instrucțiuni de completare a formularului D169N (Anexa nr. 6 — declarație privind neconcordanțele dintre informațiile privind beneficiarii reali ai fiduciilor), cu referință la Legea nr. 129/2019, art. 4 alin. (2) lit. b) (sursă: anaf_surse/opanaf_2175_2025_d169n.txt)
:::
```

Ce se poate confirma din sursele fiscale disponibile — și, la fel de important, ce nu se poate:

- **Documentul ANAF disponibil în corpus (D169N) privește un caz îngust**: raportarea neconcordanțelor despre beneficiarul real al unei **fiducii** (sau al unei construcții juridice similare fiduciei), nu declararea beneficiarului real al unui SRL sau al altei societăți obișnuite înregistrate la registrul comerțului. Chiar și în acest caz îngust, textul face doar trimitere la Legea nr. 129/2019, art. 4 alin. (2) lit. b) — nu reproduce el însuși definiția beneficiarului real.
- **Definiția generală a beneficiarului real**, aplicabilă societăților obișnuite (SRL, SA etc.), se află la art. 4 din Legea nr. 129/2019 privind prevenirea și combaterea spălării banilor — act care, la data acestui ghid, nu se regăsește integral în corpusul de surse (anaf_surse) folosit pentru redactare. Nu redăm, așadar, un citat verbatim al acelei definiții generale, ca să nu inventăm un text pe care nu-l putem confirma la sursă.
- Legea nr. 31/1990 (societăților) menționează la rândul ei existența unui **registru al beneficiarilor reali**, ținut de Oficiul Național al Registrului Comerțului, dar textul disponibil în corpus nu detaliază procedura de completare pentru o societate obișnuită.

**Important, cu onestitate:** termenele exacte de depunere (la constituire și, ulterior, anual sau la fiecare modificare a structurii de acționariat/asociați), formatul declarației și sancțiunile aplicabile pentru o societate obișnuită sunt reglementate integral de Legea nr. 129/2019 și de normele ONRC — texte care nu se regăsesc, la data acestui ghid, în sursele fiscale (anaf_surse) pe care se bazează acest material. Pentru pașii concreți de completare recomandăm verificarea directă pe portalul ONRC (recom.ro/onrc.ro), unde procedura este actualizată curent.

## Ce se greșește în practică

- Se crede că declarația de beneficiar real este o obligație fiscală administrată de ANAF, deși ea este administrată de Oficiul Registrului Comerțului, în temeiul Legii nr. 129/2019.
- Se confundă „beneficiarul real" cu administratorul sau cu asociatul majoritar înscris în actul constitutiv — definiția legală vizează persoana fizică ce exercită controlul efectiv, care poate fi alta decât cea aparentă din structura formală.
- Se presupune că declarația se depune o singură dată, la înființare, și se omite actualizarea ei atunci când structura de control se schimbă.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu are o funcționalitate dedicată** identificării sau depunerii declarației de beneficiar real a unui SRL sau a altei societăți obișnuite — căutarea în cod (`core/`) nu a găsit niciun modul care să gestioneze acest proces pentru societăți. Există, distinct, `core/d169.py` și `core/d169n.py`, module care generează declarații privind beneficiarul real, dar exclusiv pentru un caz juridic îngust — fiducia (contract de fiducie sau construcție juridică similară), în temeiul aceleiași Legi nr. 129/2019 — nu pentru beneficiarul real al unei societăți comerciale obișnuite, care rămâne neacoperit de aplicație. (O altă potrivire de nume din cod, `test_d300_taxare_inversa_beneficiar.py`, privește un concept diferit, „beneficiarul" taxării inverse la TVA în D300, fără legătură cu beneficiarul real din legislația anti-spălare de bani.) Aplicația oferă evidența contabilă generală a firmei; obligația de declarare a beneficiarului real către ONRC rămâne, la acest moment, în sarcina administratorului sau a consultantului juridic.

[iConta.eu](/)
