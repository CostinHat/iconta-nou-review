---
title: "Cum se completează codul A în D390?"
description: Codul A identifică achiziția intracomunitară de bunuri; codul de TVA al furnizorului poate lipsi într-un caz special prevăzut explicit de normă (NOTA 1).
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum se completează codul A în D390?

Codul **A** desemnează achiziția intracomunitară de bunuri primită din alt stat membru. În aplicație este tipul implicit pentru orice factură primită de la un furnizor dintr-un alt stat membru UE.

## Temeiul legal

::: ghid-temei
**OPANAF 705/2020, Anexa 2, Instrucțiuni pct. 1 lit. c)**:
> „[...] c) achiziţii intracomunitare de bunuri, achiziţii intracomunitare asimilate prevăzute la art. 273 alin. (2) lit. a) [...] achiziţii efectuate de beneficiarul livrării ulterioare în cadrul unei operaţiuni triunghiulare (A)."

**Coloana „Cod operator intracomunitar" pentru A**:
> „în cazul achiziţiilor intracomunitare de bunuri [...] (A) efectuate în România - codul de identificare în scopuri de TVA din alt stat membru atribuit furnizorului care efectuează livrarea intracomunitară."

**NOTA 1 (cazul furnizorului fără cod de TVA valid)**:
> „Pentru achiziţii intracomunitare de bunuri taxabile în România, în cazul în care furnizorul nu comunică un cod valabil de TVA, dar bunurile sunt transportate de pe teritoriul unui stat membru al Uniunii Europene, achiziţia se declară în declaraţia recapitulativă astfel: Coloana «Ţara» - codul ţării membre din care s-a efectuat livrarea intracomunitară. Coloana «Cod operator intracomunitar» - nu se va înscrie nimic. Coloana «Denumire/Nume, prenume operator intracomunitar» - se va înscrie denumirea/numele, prenumele furnizorului care a emis factura. Coloana «Tipul operaţiunii» - se va înscrie «A»."
:::

Codul A acoperă și situația beneficiarului livrării ulterioare dintr-un lanț triunghiular (vezi ghidul dedicat operațiunilor triunghiulare). Spre deosebire de L/T/P, codul de operator intracomunitar **nu** este obligatoriu pentru A — NOTA 1 prevede explicit cazul în care rămâne necompletat, dacă furnizorul nu a comunicat un cod valabil de TVA.

## Ce se greșește în practică

Greșeala tipică este să se creadă că lipsa codului de TVA al furnizorului exclude achiziția din D390 — nu este așa; achiziția rămâne declarabilă cu tipul A, doar coloana „Cod operator" rămâne goală, cu țara obligatoriu completată.

## Ce face iConta.eu

Orice factură primită de la un furnizor dintr-un alt stat membru e clasificată implicit pe **A**. Pentru liniile adăugate manual, aplicația nu cere codul TVA la tipul A (spre deosebire de L/T/P/R, unde e obligatoriu) — exact cazul NOTA 1.

Aceeași limitare curentă semnalată la codul L se aplică și aici: pentru facturile create prin ecranul dedicat „Achiziție intracomunitară", axa bunuri/servicii înregistrată pe factură la creare pare, conform codului verificat, să determine definitiv tipul D390, iar reclasificarea din panou să nu mai aibă efect pentru acele facturi — fără un mesaj explicit în interfață care să anunțe asta. Recomandăm confirmarea comportamentului live înainte de a te baza pe reclasificarea unei astfel de facturi.

[iConta.eu](/)
