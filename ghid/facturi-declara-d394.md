---
title: "Ce facturi nu se declară în D394?"
description: "Categoriile de operațiuni și de documente excluse din declarația 394, cu temeiul legal și modul în care iConta.eu le filtrează automat."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce facturi nu se declară în D394?

D394 nu e o oglindă a tuturor documentelor emise sau primite de firmă: ea raportează exclusiv operațiunile taxabile pe teritoriul național. Cea mai importantă excludere, dar nu singura, este cea a achizițiilor intracomunitare. Mai jos sunt toate categoriile confirmate din text de lege, împreună cu ce anume filtrează automat aplicația.

## Temeiul legal

::: ghid-temei
„Nu se înscriu achiziţiile intracomunitare de bunuri şi servicii pentru care există obligativitatea înscrierii în declaraţia 390."
— OPANAF 2194/2025, Anexa 2 pct.1 lit.b) (sursă: anaf_surse/opanaf_2194_2025_d394.txt:741-742)
:::

- **Achizițiile intracomunitare** — nu intră în D394 dacă trebuie declarate în D390 (VIES). Atenție la nuanță: regula privește direcția de **achiziție**, nu și livrarea — livrările intracomunitare (mărfuri/servicii vândute către un partener UE) rămân în D394, ca operațiune de tip L, reclasificată LS la cotă 0.
- **Facturile pentru operațiuni fără loc de impozitare în România** — D394 raportează doar operațiunile al căror loc de livrare/prestare e în România, conform art.275/278 din Codul fiscal.
- **Proformele și avizele de însoțire** — nu sunt facturi în sensul legii și nu generează obligație de declarare.

## Ce se greșește în practică

- Se presupune, generic, că „operațiunile intracomunitare" nu intră în D394 — dar afirmația e corectă doar pentru achiziții. O livrare intracomunitară de bunuri sau servicii intră în D394, la fel ca exporturile.
- Se declară o factură anulată sau stornată cu bază și TVA, pentru că cineva confundă „factura există în evidență" cu „operațiunea trebuie declarată".
- Se lasă în calculul D394 proforme sau avize introduse din greșeală în sistemul de facturare, în loc să fie excluse ca documente fără valoare fiscală.

## Ce face iConta.eu

Generatorul D394 (`core/d394.py`, cu accesul la date în `core/repo_d394.py`) exclude automat din calcul: achizițiile de la parteneri UE și non-UE (direcția „primită" e sărită explicit, cu comentariul din cod „ACHIZIȚIILE INTRACOMUNITARE NU INTRĂ ÎN D394 — se declară în D390"), documentele de tip proformă/aviz (filtrate după tipul de document) și, din 17.09.2026, facturile cu status anulat, stornat sau ciornă — aliniat cu aceeași regulă folosită la decontul D300. Înainte de acest ultim fix, o factură anulată sau stornată putea intra în D394 cu bază și TVA, deși D300 o excludea deja; corecția a unificat cele două surse.

Depunerea efectivă a declarației rămâne manuală, prin portalul SPV — iConta nu transmite fișierul automat la ANAF, ci doar îl generează și îl validează local.

[iConta.eu](/)
