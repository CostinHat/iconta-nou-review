---
title: "Cum verific D390 cu jurnalul de vânzări?"
description: "Ce sursă folosește de fapt controlul automat al D390 — facturile intracomunitare și notele lor validate, nu un jurnal de vânzări separat."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum verific D390 cu jurnalul de vânzări?

Dacă te aștepți ca aplicația să compare D390 cu un „jurnal de vânzări" ca document distinct, e util să știi cum funcționează de fapt controlul: nu citește un jurnal separat, ci lucrează direct cu facturile intracomunitare din perioadă.

## Temeiul legal

::: ghid-temei
„art. 325 Cod fiscal (Legea 227/2015)" — declarația recapitulativă (D390): obligație, conținut (livrări intracomunitare scutite, achiziții intracomunitare taxabile), depunere lunară; „OMFP 1802/2014" — temeiul pentru evidența contabilă (nota validată vs. ciornă).
:::

## Ce se greșește în practică

- Se caută în aplicație un raport separat numit „jurnal de vânzări" ca sursă a comparației — controlul D390 nu funcționează așa.
- Se presupune că orice diferență de sumă înseamnă automat o eroare de raportare — nu e cazul; multe diferențe primesc culoarea gri, nu roșu, tocmai pentru că pot avea cauze legitime (decalaj de perioadă, regularizări, rotunjire).

## Ce face iConta.eu

Controlul automat pentru livrările intracomunitare (partea D390 vs. evidență) ia direct facturile intracomunitare emise din perioadă (filtrate după direcție și partenerul din UE) și verifică, pentru fiecare, dacă are o notă contabilă legată de acea factură, cu statusul „validată" — nu ciornă. Sursa e tabelul de facturi și notele legate de ele, nu un „jurnal de vânzări" citit ca document separat.

Rezultatul urmează aceleași reguli ca la controlul general D390 vs. evidență: verde dacă diferența e sub toleranța de rotunjire, roșu doar dacă operațiunea e declarată dar lipsește complet din evidența validată (cu remediu sugerat, confirmat manual), gri pentru orice altă diferență de cifre (motivată de decalaj de exigibilitate, regularizări sau rotunjire) sau dacă evidența arată mai mult decât declaratul.

Onest: dacă aplicația are un ecran sau raport propriu numit „jurnal de vânzări", alimentat din aceleași facturi, poți corela conceptual cifrele — dar mecanismul de control al D390 nu citește acel raport ca sursă separată; sursa reală e perechea factură intracomunitară + notă contabilă validată legată de ea.

[iConta.eu](/)
