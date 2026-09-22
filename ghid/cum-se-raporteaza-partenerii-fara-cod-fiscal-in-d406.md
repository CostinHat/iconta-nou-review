---
title: Cum se raportează partenerii fără cod fiscal în D406?
description: Un partener persoană fizică fără CNP declarat se raportează cu tipul de cod "04", urmat de un identificator derivat determinist din numele partenerului — placeholder-ul prevăzut explicit de normă pentru acest caz.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se raportează partenerii fără cod fiscal în D406?

Nu toți clienții unei firme au un cod fiscal sau un CNP declarat pe factură — este cazul frecvent al persoanelor fizice care cumpără fără să-și comunice CNP-ul. SAF-T nu permite pur și simplu omiterea identificării acestor parteneri, dar nici nu cere un cod fiscal inventat.

## Temeiul legal

::: ghid-temei
**Notă onestă privind temeiul**: formatul codului `04` pentru parteneri fără cod fiscal (persoane fizice fără CNP declarat pe factură), precum și distincția `00`+CUI / `03`+CNP, nu au fost găsite ca citate verbatim în actele normative citite integral pentru acest dosar (OPANAF 1783/2021, OPANAF 407/2025). Aceste formate provin din schema tehnică oficială ANAF (foaia "5. Structures" a fișierului `d406_schema_anaf.xlsx`, regula sintactică S.I.26 pct. 1.4 pentru CNP), verificate direct în codul aplicației — nu dintr-un text de lege redat ca atare în sursele parcurse aici. Detaliile tehnice sunt descrise mai jos, în secțiunea explicativă.
:::

## Cele patru tipuri de cod de identificare

Nomenclatorul oficial S.C.1 folosește patru tipuri de prefix pentru identificatorul unui partener, în funcție de ce informație fiscală există despre el:

- `00` + CUI — pentru un operator economic român, plătitor sau neplătitor de TVA;
- `03` + CNP — pentru o persoană fizică al cărei CNP este cunoscut și valid (validat prin checksum);
- `01`/`02` + țară + cod — pentru parteneri străini, din UE, respectiv din afara UE;
- `04` + cod derivat din nume — pentru o persoană fizică fără CNP declarat pe factură.

Cazul `04` este placeholder-ul prevăzut explicit de normă pentru situația în care operatorul economic nu are altă opțiune decât să asocieze un cod unic clientului, pe baza numelui acestuia.

::: ghid-exemplu
Un client persoană fizică plătește cash, fără să comunice CNP-ul, iar pe factură apare doar numele "Popescu Ion Andrei". Codul de identificare generat pentru SAF-T va fi `04` urmat de un cod derivat determinist din acest nume (maximum 33 de caractere alfanumerice) — nu un cod fiscal fictiv și nu valoarea `"0"`.
:::

## Ce se greșește în practică

- Se raportează un partener fără CNP cu codul `00` sau `"0"`, ceea ce e interzis explicit de regula sintactică ANAF.
- Se confundă un CNP valid cu un CUI și se folosește prefixul `00` în loc de `03`.
- Se emite factura fără cod fiscal ȘI fără nume complet al partenerului — caz în care nu există niciun element pe baza căruia să se genereze un identificator valid.
- Se presupune că adresa completă a partenerului iese corect în SAF-T — câmpul de stradă (`StreetName`) al clientului/furnizorului este în prezent placeholder în aplicație, nu adresa reală din nomenclator.

## Ce face iConta.eu

Identificarea partenerilor fără cod fiscal este automată, prin funcția `_partener_id_saft`: dacă partenerul nu are CUI sau CNP declarat, dar are nume, se generează un cod de tip `04` derivat determinist din nume (maximum 33 de caractere alfanumerice), conform prevederii exprese a normei pentru acest caz. Dacă un partener nu are nici cod fiscal, nici nume, funcția nu produce un identificator implicit, ci întoarce `None` și raportează situația, pentru ca datele lipsă să fie completate înainte de generare — aplicația nu cade tacit pe un cod interzis de regula sintactică ANAF.

[iConta.eu](/)
