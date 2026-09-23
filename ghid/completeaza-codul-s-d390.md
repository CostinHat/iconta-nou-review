---
title: "Cum se completează codul S în D390?"
description: Codul S identifică achiziția intracomunitară de servicii, cu o excepție clară pentru prestatorii din afara UE, care nu se declară deloc în D390.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum se completează codul S în D390?

Codul **S** desemnează achiziția intracomunitară de servicii, primită de la un prestator dintr-un alt stat membru. La fel ca P, nu este tipul implicit al aplicației pentru facturile primite — implicitul rămâne A (achiziție de bunuri), deci o achiziție de servicii trebuie declarată explicit.

## Temeiul legal

::: ghid-temei
**OPANAF 705/2020, Anexa 2, Instrucțiuni pct. 1 lit. e)**:
> „[...] e) achiziţii intracomunitare de servicii (S) [...]"

**Coloana „Cod operator intracomunitar" pentru S**:
> „în cazul achiziţiilor intracomunitare de servicii (S) - codul de identificare în scopuri de TVA din alt stat membru atribuit prestatorului sau, după caz, doar codul statului membru în care este stabilit prestatorul serviciilor, în cazul în care prestatorul nu este identificat în scopuri de TVA, dar există indicii suficiente pentru a considera că este o persoană impozabilă."

**Excepție — prestatorul stabilit în afara UE**:
> „Nu vor fi declarate prestările de servicii prevăzute la art. 278 alin. (2) din Codul fiscal, dacă prestatorul serviciului este o persoană impozabilă care nu este stabilită pe teritoriul Comunităţii."
:::

Două particularități pentru S, potrivit textului citat mai sus: (1) dacă prestatorul nu e identificat în scopuri de TVA dar există indicii că e persoană impozabilă, se poate trece doar codul statului membru, fără un cod de TVA propriu-zis; (2) dacă prestatorul e stabilit în afara Uniunii Europene, operațiunea nu e „intracomunitară" și nu se declară deloc în D390 — indiferent de codul TVA pe care l-ar avea.

## Ce se greșește în practică

Cea mai frecventă greșeală este raportarea în D390 a unor achiziții de servicii de la prestatori din afara UE (de exemplu SUA, UK, Elveția) — aceste operațiuni nu intră în sfera declarației recapitulative, indiferent de tratamentul lor de TVA prin taxare inversă. A doua greșeală: nedeclararea achizițiilor de servicii intracomunitare pentru că rămân „ascunse" sub clasificarea implicită de bunuri (A).

## Ce face iConta.eu

Ca și la P, aplicația nu deduce automat tipul S din facturi — orice factură primită intracomunitar e clasificată implicit pe A (bunuri). Pentru o achiziție de servicii, reclasifici operațiunea din panoul D390 (pasul 2) din A în S, sau adaugi o linie manuală de tip S (codul partenerului nu e obligatoriu pentru S, conform normei citate mai sus).

**Limitare curentă de reconfirmat**: la fel ca la codurile L/A/P, pentru facturile create prin ecranul dedicat de achiziție intracomunitară cu axa înregistrată „servicii" la creare, tipul D390 rezultat pare determinat direct de acea axă; reclasificarea ulterioară din panou nu ar mai trebui să fie necesară în acest caz, dar dacă axa a fost înregistrată greșit „bunuri" la creare, corectarea din panoul de clasificare ar putea să nu aibă efect — recomandăm verificarea comportamentului live pentru situația ta concretă.

[iConta.eu](/)
