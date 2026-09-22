---
title: Cum se calculează TVA de recuperat în D300?
description: TVA de recuperat e suma negativă cumulată (rd.43/45) rezultată când taxa dedusă depășește taxa colectată; legea dă opțiunea de rambursare prin bifarea casetei sau reportul în luna următoare, dar iConta generează azi doar deconturi cu reportul — nu poate bifa cererea de rambursare.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se calculează TVA de recuperat în D300?

Când TVA-ul dedus într-o lună depășește TVA-ul colectat, rezultă o sumă negativă — colocvial „TVA de recuperat”. Legea dă contribuabilului două opțiuni pentru acest sold: să ceară rambursarea sau să-l reporteze în decontul lunii următoare. Este esențial de știut că decontul generat de iConta susține azi doar reportul.

## Temeiul legal

::: ghid-temei
„(1) În situația în care taxa aferentă achizițiilor efectuate de o persoană impozabilă
înregistrată în scopuri de TVA [...] este deductibilă într-o perioadă fiscală, este mai mare
decât taxa colectată pentru operațiuni taxabile, rezultă un excedent în perioada de
raportare, denumit în continuare sumă negativă a taxei.”
— art.303 alin.(1) Cod fiscal

„(7) Persoanele impozabile, înregistrate conform art. 316, pot solicita rambursarea soldului
sumei negative a taxei din perioada fiscală de raportare, prin bifarea casetei
corespunzătoare din decontul de taxă din perioada fiscală de raportare, decontul fiind și
cerere de rambursare, sau pot reporta soldul sumei negative în decontul perioadei fiscale
următoare. Dacă persoana impozabilă solicită rambursarea soldului sumei negative, acesta nu
se reportează în perioada fiscală următoare. Nu poate fi solicitată rambursarea soldului
sumei negative a taxei din perioada fiscală de raportare, mai mic de 5.000 lei inclusiv,
acesta fiind reportat obligatoriu în decontul perioadei fiscale următoare.”
— art.303 alin.(7) Cod fiscal

Decizie de admitere RIL nr. 6/2026 (MO nr.443/26.05.2026): „Dreptul persoanei impozabile de a
reporta soldul sumei negative a TVA în decontul de TVA aferent perioadelor fiscale ulterioare
nu este prescriptibil.”
:::

## Cum rezultă suma de recuperat

Suma negativă pe perioada curentă (rd.36) apare atunci când total taxă dedusă (rd.35) depășește total taxă colectată (rd.19). Cumulată cu soldul negativ reportat din luna precedentă (rd.41) și eventuale diferențe stabilite de organele de inspecție fiscală (rd.42), rezultă suma negativă cumulată (rd.43). Diferența dintre aceasta și TVA de plată cumulat (rd.40) dă soldul final la sfârșitul perioadei (rd.45) — acesta e soldul „de recuperat”.

Legea permite, pentru acest sold, două căi: bifarea casetei de pe formular pentru a cere rambursarea (decontul devine el însuși cerere de rambursare), sau reportul necondiționat spre luna următoare. Singura restricție e pentru solduri mici — sub 5.000 lei, reportul e obligatoriu, rambursarea nu poate fi cerută.

## Ce se greșește în practică

- Se așteaptă ca bifarea casetei „Solicitați rambursarea” să fie o opțiune disponibilă în aplicație — nu este, indiferent de mărimea soldului.
- Se confundă suma negativă a perioadei curente (rd.36) cu soldul cumulat de recuperat (rd.45) — sunt valori diferite dacă există și un sold reportat din luna precedentă.
- Se cere rambursare pentru un sold sub 5.000 lei, deși legea impune raportarea obligatorie.
- Se uită să se transfere manual soldul negativ (rd.45) în rândul de report al lunii următoare (rd.41), pentru că nu se preia automat.

## Ce face iConta.eu

Important de știut: `build_xml` scrie mereu, necondiționat, caseta „Solicitați rambursarea soldului sumei negative de TVA?” pe „Nu” — nu există niciun parametru, câmp de profil sau rând manual prin care contabilul să poată bifa „Da”. Practic, orice firmă care generează D300 cu iConta primește întotdeauna un decont cu soldul negativ reportat spre luna următoare, niciodată cu cererea de rambursare bifată, indiferent de mărimea soldului sau de intenția contabilului. Dacă firma dorește efectiv rambursarea, decontul trebuie corectat manual înainte de depunere (sau depus prin alt mijloc) pentru a bifa caseta corespunzătoare — aplicația nu susține azi acest flux. Restul lanțului de calcul (rd.36–rd.45) e generat automat, cu excepția soldului reportat din luna precedentă (rd.41), care e un câmp manual introdus de contabil la fiecare depunere.

[iConta.eu](/)
