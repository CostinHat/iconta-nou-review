---
title: Cum se raportează în D205 dividendele distribuite după o majorare de capital?
description: O majorare de capital social nu schimbă mecanica D205 — regula rămâne aceeași: impozitul se calculează pe dividendul distribuit/plătit prin contul 457, la cota curentă de participare a fiecărui asociat, fără reguli fiscale separate legate de majorarea de capital.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se raportează în D205 dividendele distribuite după o majorare de capital?

O majorare de capital social poate schimba structura de proprietate a unei firme — cote noi de participare, poate chiar asociați noi — și e firesc să vă întrebați dacă asta afectează în vreun fel raportarea în D205 a dividendelor distribuite ulterior. Răspunsul scurt: nu există o regulă fiscală separată pentru acest caz — se aplică regula generală D205, cu cotele de participare actuale.

## Temeiul legal

::: ghid-temei
„Cap. V «Date informative privind impozitul pe veniturile din dividende» se completează de către plătitorii de venituri din dividende, pentru fiecare persoană fizică beneficiară." (OPANAF 179/2022, Secțiunea V dividende, l.381-397)

„2. unicitate (tip_venit1+cifR) pt. tip_venit1#25" (structura D205, OPANAF 102/2025, „Validari suplimentare")
:::

## Ce se schimbă efectiv, și ce nu

D205 nu are nicio regulă specifică legată de majorarea capitalului social — declarația raportează, pentru fiecare beneficiar persoană fizică, dividendul distribuit, dividendul plătit, baza de calcul și impozitul reținut, calculate din mișcările contabile ale distribuirii de dividende. Dacă structura de capital sau cotele de participare se schimbă în cursul anului (de exemplu în urma unei majorări de capital cu asociați noi sau cote redistribuite), regula generală rămâne: repartizarea dividendului pe fiecare beneficiar se face proporțional cu **cota de participare curentă**, cea aplicabilă la momentul distribuirii/generării declarației — nu cu cote istorice, calculate separat pe fiecare tranșă de timp în care structura de capital a fost diferită.

Dacă majorarea de capital a adus un asociat nou, acel asociat va apărea ca beneficiar distinct în D205 doar dacă a primit efectiv dividende plătite din contul care alimentează declarația, cu propriile date de identificare (CNP validat, nume).

## Ce se greșește în practică

- Se caută un tratament fiscal special pentru dividendele distribuite „după majorare de capital" — nu există un asemenea regim separat, aplicabil doar acestui caz.
- Se încearcă recalcularea manuală a dividendului pe cote istorice, per tranșă de timp în care structura de capital a fost diferită, deși regula aplicată e cota curentă.
- Se omite actualizarea cotelor de participare ale asociaților în sistem înainte de generarea D205, ceea ce duce la repartizarea greșită a dividendului între beneficiari.
- Se confundă majorarea de capital social (operațiune juridică, la Registrul Comerțului) cu distribuirea de dividende (operațiune fiscal-contabilă) — cele două sunt evenimente independente.

## Ce face iConta.eu

Pentru fiecare asociat cu cotă de participare mai mare decât zero, aplicația calculează dividendul plătit și cel distribuit proporțional cu cota lui de participare curentă din tabelul de asociați ai firmei — aceeași regulă indiferent dacă acea cotă a rezultat dintr-o structură de capital neschimbată sau dintr-o majorare recentă. Nu există în cod nicio ramură separată pentru „majorare de capital" — regulile D205 (cota de impozit, contul de evidență 457, validarea rezidenței și a datelor de identificare) se aplică identic, indiferent de evenimentele juridice petrecute la nivelul capitalului social. Dacă structura de capital s-a schimbat, verificați doar că tabelul de asociați reflectă cotele actuale înainte de generarea declarației.

[iConta.eu](/)
