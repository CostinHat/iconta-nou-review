---
title: "Cum se tratează veniturile din management consulting"
description: "Regula specială din Codul fiscal pentru serviciile de management sau consultanță plătite unui nerezident: impozitarea nu depinde de locul prestării serviciului, ci de reședința plătitorului."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se tratează veniturile din management consulting

Serviciile de management sau consultanță plătite de o firmă românească unui furnizor nerezident sunt impozabile în România — cu reținere la sursă — indiferent de locul unde consultantul prestează efectiv serviciul, chiar dacă activitatea se desfășoară integral în afara României. Este o excepție notabilă față de regula generală, care leagă impozitarea serviciilor de locul prestării lor efective.

## Temeiul legal

::: ghid-temei
„Sunt considerate ca fiind obținute din România, indiferent dacă sunt primite în România sau în străinătate, în special următoarele venituri: [...] k) veniturile din servicii prestate în România, exclusiv transportul internațional și prestările de servicii accesorii acestui transport; [...] l) venituri din prestarea de servicii de management sau de consultanță din orice domeniu, dacă aceste venituri sunt obținute de la un rezident sau dacă veniturile respective sunt cheltuieli ale unui sediu permanent în România;"
— Legea nr. 227/2015 (Codul fiscal), art. 12 lit. k), l) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Diferența dintre cele două litere este exact esența problemei:

- **Regula generală** (lit. k) leagă impozabilitatea în România de **locul prestării serviciului** — dacă serviciul e prestat în afara României, venitul nu e, în principiu, impozabil în România.
- **Excepția de la lit. l)**, aplicabilă specific serviciilor de management sau consultanță „din orice domeniu", schimbă criteriul: impozabilitatea depinde de **reședința plătitorului** — dacă plătitorul este un rezident român (sau o cheltuială a unui sediu permanent din România), venitul e impozabil în România, indiferent unde a fost prestat efectiv serviciul.
- Cota de impozit cu reținere la sursă aplicabilă acestor venituri este, în regula generală, de 16% asupra venitului brut (art. 224 alin. (4) lit. d)), redusă la 10% dacă beneficiarul e persoană fizică rezidentă într-un stat UE sau într-un stat cu care România are încheiată o convenție de evitare a dublei impuneri (art. 224 alin. (4) lit. c^1)) — sau la cota din convenția de evitare a dublei impuneri, dacă e mai favorabilă și sunt îndeplinite condițiile de aplicare a acesteia.
- Impozitul se calculează, reține, declară și plătește de către **plătitorul de venit** (firma românească), până la data de 25 a lunii următoare celei în care s-a plătit venitul (art. 224 alin. (1), (5)).

## Ce se greșește în practică

- Se presupune că serviciile de consultanță prestate integral în străinătate de un furnizor nerezident nu sunt impozabile în România, prin analogie cu regula generală a serviciilor (lit. k) — dar art. 12 lit. l) schimbă exact acest criteriu pentru management/consultanță.
- Se omite reținerea la sursă a impozitului la plata facturii către consultantul nerezident, considerând că obligația fiscală revine exclusiv acestuia, în statul lui de rezidență.
- Se aplică automat cota redusă de 10% sau cota din convenția de evitare a dublei impuneri, fără a verifica întâi dacă furnizorul prezintă certificatul de rezidență fiscală cerut pentru aplicarea acestor cote favorabile.

## Ce face iConta.eu

La data acestui ghid, iConta.eu poate genera declarația D207 (declarație informativă privind impozitul reținut la sursă pe beneficiari nerezidenți), prin modulul `core/d207.py`, pe baza datelor introduse manual de contabil pentru fiecare beneficiar nerezident. Aplicația nu clasifică automat un serviciu ca fiind „de management sau consultanță" în sensul art. 12 lit. l) și nu calculează ea însăși cota de impozit aplicabilă (16%, 10% sau cota din convenția de evitare a dublei impuneri) — încadrarea juridică a serviciului și cota corectă de reținere rămân o determinare făcută de contabil, pe baza contractului și a documentelor de rezidență fiscală prezentate de furnizor.

[iConta.eu](/)
