---
title: "Cum declar un retur intracomunitar în D390?"
description: "D390 are un cod dedicat de 'retur bunuri' doar pentru regimul stocurilor la dispoziția clientului; pentru o livrare intracomunitară obișnuită returnată, ajustarea se declară în luna în care regularizarea a fost comunicată clientului, nu prin rectificarea perioadei inițiale."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum declar un retur intracomunitar în D390?

Declarația recapitulativă 390 VIES are un mecanism explicit de „retur bunuri", dar el nu se aplică oricărei livrări sau achiziții intracomunitare — ci exclusiv operațiunilor din secțiunea specială privind regimul stocurilor la dispoziția clientului (call-off stock). Pentru o livrare sau achiziție intracomunitară „normală" care e returnată, mecanismul e altul.

## Temeiul legal

::: ghid-temei
„*) Se va completa, după caz, cu una dintre cifrele corespunzătoare situaţiei: 1 - retur bunuri; 2 - înlocuire client."
— OPANAF 705/2020 pentru aprobarea formularului 390 VIES, Anexa nr. 2 (Instrucțiuni de completare), secțiunea III litera B „Modificări ale informațiilor furnizate" (sursă: anaf_surse/opanaf_705_2020_d390.txt)
:::

::: ghid-temei
„Spre exemplificare, modificări ale informaţiilor furnizate pot apărea atunci când persoana impozabilă care ar fi trebuit să achiziţioneze bunurile este înlocuită cu o altă persoană impozabilă sau când bunurile sunt returnate în România în termenul menţionat la art. 270^1 alin. (4) din Codul fiscal, fără ca furnizorul să fi transferat dreptul de a dispune de bunuri către altă persoană impozabilă. Corectarea datelor declarate eronat sau nedeclararea datelor în perioade anterioare nu reprezintă modificări ale informaţiilor furnizate la litera A."
— OPANAF 705/2020, Anexa nr. 2, instrucțiuni la secțiunea III litera B (sursă: anaf_surse/opanaf_705_2020_d390.txt)
:::

Din aceste texte rezultă două situații distincte, tratate diferit în D390:

- **Regimul stocurilor la dispoziția clientului** (art. 270^1 din Codul fiscal — bunuri transferate într-un alt stat membru și puse la dispoziția unui client cunoscut, fără transfer imediat al dreptului de proprietate): dacă bunurile sunt returnate în România înainte de a fi efectiv vândute clientului respectiv, se completează secțiunea III litera B a formularului, cu motivul „1 – retur bunuri".
- **Livrare sau achiziție intracomunitară obișnuită** (secțiunea I/II a declarației, bunuri vândute/cumpărate efectiv, nu doar puse la dispoziție): dacă bunurile sunt returnate ulterior facturării, nu există un cod special de „retur”. Returul este o **ajustare a bazei** (Codul fiscal art. 287) care, potrivit instrucțiunilor D390, „se declară pentru luna calendaristică în care intervine exigibilitatea taxei, conform art. 282 alin. (9) din Codul fiscal, respectiv în luna calendaristică în care regularizarea a fost comunicată clientului” — deci în luna regularizării, nu prin rectificarea perioadei inițiale. Declarația rectificativă se folosește doar pentru date declarate eronat.
- Instrucțiunile precizează explicit că simpla corectare a unor date declarate greșit NU se tratează ca „modificare a informațiilor furnizate" (mecanismul cu cod 1/2), ci ca rectificare obișnuită a declarației.

## Ce se greșește în practică

- Se caută codul „1 – retur bunuri" pentru orice retur intracomunitar, deși el există doar pentru secțiunea specială privind stocurile la dispoziția clientului.
- Se raportează returul unei livrări/achiziții intracomunitare obișnuite prin declarație rectificativă pentru perioada inițială, deși ajustarea se declară în luna calendaristică în care regularizarea a fost comunicată clientului (instrucțiunile D390, Codul fiscal art. 282 alin. (9)).
- Se confundă termenul de 12 luni prevăzut la art. 270^1 alin. (4) din Codul fiscal pentru returul bunurilor din regimul stocurilor la dispoziția clientului cu un termen general aplicabil oricărui retur intracomunitar.
- Se omite emiterea facturii de stornare/credit note aferente returului, deși aceasta este documentul justificativ pe baza căruia se corectează atât evidența TVA internă, cât și declarația 390.

## Ce face iConta.eu

La data acestui ghid, iConta.eu nu are o funcție dedicată pentru regimul special al stocurilor la dispoziția clientului (call-off stock) și nici pentru generarea automată a codului „retur bunuri" din secțiunea III a formularului 390. Aplicația generează declarația D390 pe baza livrărilor/achizițiilor intracomunitare obișnuite introduse, iar corectarea unui retur pentru o operațiune intracomunitară normală se face, în prezent, prin introducerea manuală a stornării și, dacă e cazul, prin redepunerea rectificativă a declarației.

[iConta.eu](/)
