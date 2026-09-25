---
title: "Control pe tranzacții intracomunitare: cum îl anticipez"
description: "Declarația recapitulativă (D390) e principala sursă de comparare automată pentru tranzacțiile intracomunitare — orice neconcordanță între ce declari tu și ce declară partenerul devine vizibilă la nivel european prin VIES."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Control pe tranzacții intracomunitare: cum îl anticipez

Tranzacțiile intracomunitare sunt printre cele mai expuse la verificări încrucișate, pentru că datele nu rămân doar la ANAF — declarația recapitulativă a fiecărei firme e comparată automat, la nivel european, cu declarațiile partenerilor din alte state membre. O firmă care vrea să anticipeze un control trebuie să pornească de la ce anume trebuie să apară corect în această declarație.

## Temeiul legal

::: ghid-temei
„Orice persoană impozabilă înregistrată în scopuri de TVA conform art. 316 sau 317 trebuie să întocmească și să depună la organele fiscale competente o declarație recapitulativă în care menționează: a) livrările intracomunitare scutite de taxă în condițiile prevăzute la art. 294 alin. (2) lit. a) și d), pentru care exigibilitatea taxei a luat naștere în luna calendaristică respectivă."
— Legea nr. 227/2015 (Codul fiscal), art. 325 alin. (1) și lit. a) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce anticipează, în practică, riscul unui control pe tranzacții intracomunitare:

- Declarația recapitulativă (**D390**) trebuie să reflecte exact livrările intracomunitare scutite, achizițiile intracomunitare și operațiunile din lanțuri triunghiulare — orice discrepanță între ce declari tu ca livrare intracomunitară și ce declară partenerul din alt stat membru ca achiziție corespunzătoare devine vizibilă prin sistemul VIES, folosit de autoritățile fiscale din toate statele membre pentru verificări încrucișate.
- Codul de identificare TVA al partenerului trebuie **verificat și valid** la data operațiunii — o livrare scutită ca intracomunitară către un cod de TVA invalid sau inexistent în VIES la momentul respectiv riscă recalificarea operațiunii ca livrare internă, cu TVA colectată suplimentar.
- Verificarea generală de conformitate fiscală se face prin procedura de inspecție fiscală, reglementată de Codul de procedură fiscală, iar pentru orice neconcordanță constatată, organul fiscal are obligația de a formula o cerere scrisă de informații, potrivit art. 58 din același act — deci o primă etapă, înainte de o inspecție propriu-zisă, e adesea o solicitare de clarificări legată tocmai de discrepanțe în D390.

## Ce se greșește în practică

- Se declară o livrare intracomunitară ca scutită fără verificarea prealabilă a codului de TVA al partenerului în VIES, la data operațiunii, ceea ce creează un risc direct de recalificare a operațiunii.
- Se depune D390 cu întârziere sau incomplet, ceea ce generează automat o neconcordanță vizibilă la nivel european, chiar dacă tranzacțiile de bază sunt corecte.
- Se ignoră corelarea dintre D390 și decontul de TVA (D300) — sumele raportate ca livrări/achiziții intracomunitare trebuie să corespundă între cele două declarații, iar o diferență necorelată atrage atenția organului fiscal.

## Ce face iConta.eu

iConta.eu generează D390 pe baza operațiunilor intracomunitare înregistrate în aplicație (livrări, achiziții, servicii), corelate cu facturile emise/primite din evidența firmei. Aplicația nu verifică automat, la momentul emiterii facturii, validitatea codului de TVA al partenerului în VIES și nu semnalează proactiv riscul unei neconcordanțe la nivel european — verificarea partenerilor și corelarea D390 cu D300 rămân un control pe care contabilul îl face separat.

[iConta.eu](/)
