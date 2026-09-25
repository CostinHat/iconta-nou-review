---
title: "D301 rectificativă: cum corectez declarația specială"
description: "Cum se corectează decontul special de TVA (D301) când a fost depus cu erori, și de ce nu se folosește declarația 710."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# D301 rectificativă: cum corectez declarația specială

Decontul special de taxă pe valoarea adăugată (D301) se depune pentru anumite achiziții intracomunitare — de exemplu mijloace de transport noi — de către persoane care, în mod obișnuit, nu sunt plătitoare de TVA. Dacă acest decont a fost completat greșit, corecția lui se face **prin decontul special însuși**, redepus, nu prin altă declarație.

## Temeiul legal

::: ghid-temei
„Declarația depusă inițial se rectifică prin depunerea unei noi declarații, pe același format, bifând căsuța corespunzătoare de pe formular. În situația în care persoana impozabilă depune declarația după anularea rezervei verificării ulterioare, în condițiile art. 105 alin. (6) din Legea nr. 207/2015 privind Codul de procedură fiscală [...] se bifează, în căsuța corespunzătoare, temeiul legal pentru depunerea declarației."
— OPANAF 592/2016 (instrucțiuni de completare a decontului special de TVA, formularul 301) (sursă: anaf_surse/opanaf_592_2016_d301.txt)
:::

- Rectificativa D301 e, la fel ca la D101, un formular „refăcut" — se redepune același tip de declarație, cu bifa de rectificare activată, nu un formular separat.
- Dacă în aceeași lună apar mai multe achiziții intracomunitare de mijloace de transport, se pot depune mai multe deconturi separate pentru aceeași perioadă „fără a bifa căsuța «Declarație rectificativă»" — nu orice a doua depunere e automat o corecție.
- Se aplică aceeași regulă generală privind rezerva verificării ulterioare ca la celelalte declarații de impunere: corecția rămâne posibilă și după anularea rezervei doar în situațiile enumerate expres la CPF art. 105 alin. (6).

## Ce se greșește în practică

- Se caută în ecranul „declarație rectificativă" generic al aplicației un formular D301 rectificativ separat — D301 nu funcționează ca D100/710; corecția se face redepunând D301, cu bifa activată.
- Se bifează „rectificativă" și pentru un al doilea decont din aceeași lună care declară pur și simplu o altă achiziție, nu o corecție a celei dintâi.
- Se confundă mecanismul D301 cu cel al formularului 710, pentru că amândouă corectează o „declarație depusă anterior" — dar au temei legal, formular și cod de obligație complet diferite.

## Ce face iConta.eu

Declarația 301 are, în iConta.eu, propriul mecanism de rectificare — un marcaj propriu pe formularul D301, independent de D710. Formularul 710 din iConta.eu **nu poate** corecta un decont special de TVA: motorul care generează D710 acceptă, prin construcție, doar codurile de obligație aferente impozitului pe veniturile microîntreprinderilor (121) și impozitului pe profit (103), declarate prin D100 — TVA-ul din D301 nu face parte din această listă și nu apare nicăieri în procesarea D710. Așadar, o rectificativă D301 nu ține de funcționalitatea D710, ci de ecranul propriu al declarației 301.

[iConta.eu](/)
