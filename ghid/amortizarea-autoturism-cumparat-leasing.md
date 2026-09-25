---
title: "Amortizarea unui autoturism cumpărat în leasing"
description: "Cum se amortizează un autoturism achiziționat prin leasing financiar și plafonul legal de 1.500 lei/lună pentru deductibilitatea fiscală a amortizării."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Amortizarea unui autoturism cumpărat în leasing

Într-un contract de leasing financiar, autoturismul se înregistrează în contabilitatea utilizatorului (locatarului) ca imobilizare corporală și se amortizează de acesta — nu de firma de leasing. Deductibilitatea fiscală a amortizării unui autoturism de persoane e însă plafonată legal, indiferent dacă a fost cumpărat cash sau prin leasing.

## Temeiul legal

::: ghid-temei
„214. - (1) Înregistrarea în contabilitate a amortizării bunului ce face obiectul contractului se efectuează în cazul leasingului financiar de către locatar/utilizator, iar în cazul leasingului operațional, de către locator/finanțator. (2) În cazul leasingului financiar, achizițiile de către locatar de bunuri imobile și mobile sunt tratate ca investiții în imobilizări, fiind supuse amortizării pe o bază consecventă cu politica normală de amortizare pentru bunuri similare ale locatarului."
— OMFP 1802/2014, pct. 214 (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)

„[...] pentru mijloacele de transport de persoane care au cel mult 9 scaune de pasageri, incluzând și scaunul șoferului, din categoria M1 [...] cheltuielile cu amortizarea sunt deductibile, pentru fiecare, în limita a 1.500 lei/lună."
— Codul fiscal (Legea 227/2015), art. 28 alin. (14) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce rezultă din cele două texte:

- **Contabil**, autoturismul intră în evidența locatarului la valoarea capitalului finanțat (cont 2133, potrivit motorului de leasing folosit de iConta.eu — vezi mai jos), iar amortizarea se calculează după politica firmei, ca la orice mijloc fix propriu.
- **Fiscal**, indiferent de modul de achiziție (leasing sau cumpărare directă), amortizarea unui autoturism de persoane (categoria M1, cel mult 9 locuri) e deductibilă doar **până la 1.500 lei/lună, per autoturism** — partea care depășește acest plafon e cheltuială nedeductibilă la calculul impozitului pe profit.
- Separat de amortizare, cheltuielile de funcționare (combustibil, întreținere, reparații) sunt deductibile doar 50%, dacă autoturismul nu e folosit exclusiv în scopul activității economice (CF art. 25 alin. (3) lit. l), iar TVA-ul aferent achiziției, chiriei/leasingului și cheltuielilor de funcționare e deductibil tot 50%, cu aceeași condiție (CF art. 298).

## Ce se greșește în practică

- Se aplică plafonul de 1.500 lei/lună la valoarea totală a ratelor de leasing (capital + dobândă), nu la amortizarea contabilă a bunului — cele două sunt fluxuri diferite, iar plafonul vizează strict cheltuiala cu amortizarea.
- Se presupune că leasingul „scapă" de plafon pentru că nu există o achiziție clasică — plafonul de 1.500 lei/lună se aplică oricărui autoturism M1 amortizat, indiferent de forma de finanțare.
- Se uită plafonul separat de 50% pentru TVA și cheltuielile de funcționare, tratând autoturismul ca fiind integral deductibil doar pentru că amortizarea a fost calculată corect.

## Ce face iConta.eu

La data acestui ghid, iConta.eu are un motor dedicat leasingului financiar și operațional (`core/leasing.py`), care generează notele contabile pentru primirea bunului, ratele de leasing și valoarea reziduală, potrivit OMFP 1802/2014 pct. 212-217 — inclusiv separarea capitalului de dobândă și evidența extracontabilă a dobânzii (contul 8051). Aplicația **nu calculează însă automat** plafonul fiscal de 1.500 lei/lună pentru amortizarea autoturismelor M1, nici plafonul de 50% pentru cheltuielile de funcționare și TVA — verificarea acestor limite, la calculul impozitului pe profit, rămâne în sarcina contabilului.

[iConta.eu](/)
