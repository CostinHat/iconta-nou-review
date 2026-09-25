---
title: "Calendar fiscal 2026: termene legate de amortizarea mijloacelor fixe"
description: "Cum se leagă amortizarea fiscală a mijloacelor fixe de termenele de declarare a impozitului pe profit, potrivit Codului fiscal."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Calendar fiscal 2026: termene legate de amortizarea mijloacelor fixe

Amortizarea fiscală nu are propriul ei termen de „depunere" — nu există o declarație separată pentru amortizare. Ea intră, ca element de calcul, în termenele generale de declarare a impozitului pe profit, trimestrial sau anual, în funcție de sistemul ales de firmă.

## Temeiul legal

::: ghid-temei
„(1) Calculul, declararea și plata impozitului pe profit, cu excepțiile prevăzute de prezentul articol, se efectuează trimestrial, până la data de 25 inclusiv a primei luni următoare încheierii trimestrelor I-III. Definitivarea și plata impozitului pe profit aferent anului fiscal respectiv se efectuează până la termenul de depunere a declarației privind impozitul pe profit prevăzut la art. 42."
— Legea nr. 227/2015 (Codul fiscal), art. 41 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Consecințele practice pentru calculul care include amortizarea fiscală:

- Firmele care aplică sistemul **trimestrial** trebuie să reflecte cheltuiala cu amortizarea fiscală lunară, cumulată, în fiecare din cele trei calcule intermediare (trimestrele I-III, până pe 25 ale lunii următoare), iar definitivarea anuală se face la termenul declarației de impozit pe profit (art. 42).
- Amortizarea fiscală se calculează **lunar**, potrivit art. 28, indiferent dacă firma raportează trimestrial sau anual — diferența dintre cele două sisteme privește doar frecvența declarării impozitului pe profit, nu ritmul de calcul al amortizării.
- Pentru investițiile puse în funcțiune în cursul unui trimestru, amortizarea începe abia din **luna următoare** punerii în funcțiune — un detaliu care schimbă suma dedusă în trimestrul respectiv.

## Ce se greșește în practică

- Se calculează amortizarea „pe an întreg" abia la închiderea exercițiului financiar, în loc să fie reflectată lunar/trimestrial în calculul provizoriu al impozitului pe profit, ceea ce distorsionează plățile intermediare.
- Se pune în funcțiune un mijloc fix la sfârșitul unei luni și se începe amortizarea din aceeași lună, în loc de luna următoare, așa cum cere regula generală.
- Se confundă termenul de declarare a impozitului pe profit (care include, indirect, amortizarea) cu un termen separat pentru „raportarea" amortizării — un asemenea termen distinct nu există în lege.

## Ce face iConta.eu

La data acestui ghid, iConta.eu calculează amortizarea lunară a mijloacelor fixe, cu regula punerii în funcțiune din luna următoare (`core/d406_active.py`), și generează declarațiile de impozit pe profit trimestriale (D100) și anuale (D101) pe baza datelor introduse (`core/d101.py`). Aplicația nu are o funcționalitate separată de „calendar al amortizării" — termenele relevante sunt exclusiv cele generale de declarare a impozitului pe profit, urmărite prin scadențarul fiscal al aplicației.

[iConta.eu](/)
