---
title: "PFA la normă de venit plătește CAS?"
description: "CAS e obligatorie doar dacă norma de venit (cumulată cu alte venituri din activități independente și drepturi de autor) atinge 12 salarii minime brute pe țară — sub acest prag, e opțională."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# PFA la normă de venit plătește CAS?

Nu automat — CAS depinde de un prag valoric, nu de forma de stabilire a venitului. Un PFA la normă de venit datorează CAS exact în aceleași condiții ca unul la sistem real: dacă venitul cumulat din activități independente atinge nivelul de 12 salarii minime brute pe țară.

## Temeiul legal

::: ghid-temei
„Persoanele fizice care în anul fiscal pentru care se depune Declarația unică [...] au realizat venituri din activitățile prevăzute la art. 137 alin. (1) lit. b) și b^1), din una sau mai multe surse și/sau categorii de venituri, a căror valoare anuală cumulată este cel puțin egală cu 12 salarii minime brute pe țară, datorează contribuția de asigurări sociale la o bază de calcul stabilită potrivit alin. (2)."
— Codul fiscal (Legea 227/2015), art. 148 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce contează pentru un PFA la normă de venit:

- Pentru încadrarea în pragul de 12 salarii minime brute, norma de venit ajustată intră în cumul alături de venitul net din alte activități independente și drepturile de proprietate intelectuală (art. 148 alin. (3)) — nu se raportează izolat, activitate cu activitate.
- Dacă venitul cumulat atinge sau depășește 12 salarii minime brute, CAS devine obligatorie, cu bază de calcul aleasă de contribuabil între 12 și 24 de salarii minime brute, în funcție de treaptă (art. 148 alin. (2)).
- Sub acest prag, CAS nu e obligatorie, dar contribuabilul poate opta pentru plata ei, la un venit ales de minimum 12 salarii minime brute (art. 148 alin. (4)) — util pentru vechimea în sistemul public de pensii.
- Excepția de la art. 150: persoanele asigurate în sisteme proprii de asigurări sociale sau pensionarii nu datorează CAS pentru aceste venituri, indiferent de nivelul lor.

## Ce se greșește în practică

- Se presupune că norma de venit, fiind o valoare fixă mai mică decât veniturile reale, scapă automat de CAS — dacă norma (eventual ajustată) atinge 12 salarii minime brute, obligația există exact ca la sistem real.
- Se calculează pragul doar pe norma unei singure activități, ignorând cumulul cu alte surse de activități independente sau drepturi de proprietate intelectuală ale aceluiași contribuabil.
- Se confundă excepția pentru pensionari și asigurați în sisteme proprii (art. 150) cu o scutire generală pentru normă de venit — excepția ține de statutul contribuabilului, nu de modul de stabilire a venitului.

## Ce face iConta.eu

Motorul `core/d212_engine.py` (funcția `calculeaza_cas`) aplică corect pragul de 12 salarii minime brute și plafonarea pe trepte (12-24 sm), cu reperul de salariu minim citit din registrul de cote pentru anul de venit. Calculul automat, prin `fisa_d212` (`core/rip_api.py`), pornește însă de la venitul net rezultat din Registrul-jurnal de încasări și plăți — deci acoperă sistemul real, nu norma de venit.

Pentru un PFA la normă de venit, aplicația nu calculează automat dacă norma (ajustată) atinge pragul de 12 salarii minime brute și nu cumulează automat norma cu alte venituri din activități independente ale aceleiași persoane — verificarea rămâne manuală.

[iConta.eu](/)
