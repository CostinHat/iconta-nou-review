---
title: "Unde găsesc recipisa pentru D212?"
description: "Ce reprezintă, din punct de vedere legal, confirmarea de depunere a Declarației unice (D212) transmise electronic și unde se regăsește aceasta."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Unde găsesc recipisa pentru D212?

„Recipisa" pentru o declarație depusă electronic nu este un document separat pe care contribuabilul îl solicită, ci **mesajul electronic de confirmare** generat automat de sistemul ANAF în momentul înregistrării și validării declarației pe portal. Acesta se regăsește în contul de Spațiul Privat Virtual (SPV) al contribuabilului, la declarația respectivă.

## Temeiul legal

::: ghid-temei
„(3) Data depunerii declarației fiscale este data înregistrării acesteia la organul fiscal sau data depunerii la poștă, după caz. în situația în care declarația fiscală se depune prin mijloace electronice de transmitere la distanță, data depunerii declarației este data înregistrării acesteia pe pagina de internet a organului fiscal, astfel cum rezultă din mesajul electronic de confirmare transmis ca urmare a primirii declarației."
— Legea nr. 207/2015 (Codul de procedură fiscală), art. 103 alin. (3) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Ce înseamnă practic:

- Legea numește expres acest document „mesaj electronic de confirmare transmis ca urmare a primirii declarației" — el joacă rolul recipisei clasice, eliberate altădată la depunerea pe hârtie la ghișeu.
- Data înscrisă în acest mesaj este data legală a depunerii declarației, relevantă pentru calculul respectării termenului legal (art. 122 alin. (3) pentru D212) și, implicit, pentru eventuale penalități de întârziere.
- Mesajul se generează automat de sistemul de tranzacționare al ANAF și rămâne asociat declarației respective în contul SPV al contribuabilului — de acolo poate fi descărcat sau consultat ulterior, inclusiv ca probă în caz de litigiu privind data depunerii.

## Ce se greșește în practică

- Se caută recipisa ca document separat, solicitat expres de la ANAF, deși ea este generată automat și disponibilă direct în contul SPV, atașată declarației transmise.
- Se șterge sau nu se salvează local mesajul electronic de confirmare, considerându-se că rămâne oricând disponibil în SPV — accesul ulterior poate fi mai greoi, motiv pentru care se recomandă păstrarea unei copii locale imediat după depunere.
- Se confundă confirmarea de încărcare a fișierului (simpla primire) cu mesajul de validare — abia acesta din urmă, care atestă validarea conținutului, are valoarea de recipisă cu efecte juridice depline (vezi art. 103 alin. (4)).

## Ce face iConta.eu

La data acestui ghid, iConta.eu generează fișierul XML al Declarației unice (D212) (`core/d212.py`), dar nu depune declarația în SPV și, prin urmare, nu primește și nu stochează mesajul electronic de confirmare (recipisa) emis de ANAF. Acesta rămâne disponibil exclusiv în contul de Spațiul Privat Virtual al contribuabilului, în urma depunerii efective a declarației pe portalul ANAF.

[iConta.eu](/)
