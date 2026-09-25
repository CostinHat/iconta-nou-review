---
title: "Un telefon mobil este mijloc fix sau obiect de inventar?"
description: "Pragul legal care decide dacă un telefon mobil (sau orice alt bun) se înregistrează ca mijloc fix amortizabil sau ca obiect de inventar, conform Codului fiscal."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Un telefon mobil este mijloc fix sau obiect de inventar?

Nu contează ce fel de bun e — telefon, laptop, mobilier — ci **valoarea lui de intrare** și **durata normală de utilizare**. Legea fixează un prag: sub el, bunul e obiect de inventar (trece direct pe cheltuială); peste el, e mijloc fix amortizabil.

## Temeiul legal

::: ghid-temei
„Mijlocul fix amortizabil este orice imobilizare corporală care îndeplinește cumulativ următoarele condiții: a) este deținut și utilizat în producția, livrarea de bunuri sau în prestarea de servicii, pentru a fi închiriat terților sau în scopuri administrative; b) la data intrării în patrimoniul contribuabilului, are o valoare fiscală egală sau mai mare decât suma de 5.000 lei; această limită se actualizată anual, în funcție de indicele de inflație, prin hotărâre a Guvernului; c) are o durată normală de utilizare mai mare de un an."
— Legea 227/2015 (Codul fiscal), art. 28 alin. (2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Cele trei condiții sunt **cumulative** — trebuie îndeplinite toate deodată pentru ca bunul să fie mijloc fix:

- **Destinație de utilizare** economică (administrativă, de producție, de închiriere) — un telefon mobil folosit de un angajat pentru activitatea firmei se încadrează aici fără discuție.
- **Valoare la intrare ≥ 5.000 lei** — prag introdus prin OUG 8/2026 (art. 6 pct. 7) și aplicabil pentru întreg anul fiscal 2026, adică inclusiv achizițiilor din 01.01–24.02.2026 (OUG 8/2026 art. 10 alin. (2): „Prevederile art. 6 pct. 1-14 se aplică începând cu anul fiscal 2026"). Pragul de 2.500 lei rămâne relevant doar pentru bunurile intrate până la 31.12.2025. Un telefon cumpărat sub acest prag **nu** e mijloc fix, indiferent de durata lui reală de folosire.
- **Durată normală de utilizare > 1 an** — dacă bunul e destinat unei utilizări scurte, sub un an, nu e mijloc fix nici dacă valoarea depășește pragul.

Dacă oricare din cele trei condiții lipsește — de regulă, la telefoane, condiția de valoare — bunul se înregistrează ca **obiect de inventar**: costul lui trece integral pe cheltuială la darea în folosință, nu se amortizează în timp.

Notă de tranziție: mijloacele fixe aflate deja în evidență la 31.12.2025, cu valoare fiscală între 2.500 și 5.000 lei (sub pragul vechi, dar sub noul prag din 2026), **nu se reclasifică** retroactiv — continuă să fie amortizate pe durata rămasă (CF art. 45 alin. (21^3)).

## Ce se greșește în practică

- Se folosește vechiul prag de 2.500 lei pentru achiziții din 2026, ignorând majorarea la 5.000 lei aplicabilă pentru tot anul fiscal 2026 (inclusiv pentru achizițiile din 01.01–24.02.2026).
- Se reclasifică retroactiv mijloacele fixe existente la 31.12.2025 cu valoare între 2.500 și 5.000 lei — legea spune explicit că acestea NU se reclasifică, ci continuă amortizarea pe durata rămasă.
- Se aplică pragul valoric fără verificarea celorlalte două condiții (destinație economică și durată > 1 an) — toate trei trebuie îndeplinite simultan.

## Ce face iConta.eu

Aplicația are un motor dedicat exact acestei clasificări, `core/obiecte_inventar.py`, care citește pragul legal curent dintr-un registru de cote istoricizat (nu un număr fix scris în cod) — motiv pentru care aplică automat 5.000 lei pentru achiziții din 2026 și valoarea anterioară pentru date mai vechi. Funcția `e_obiect_inventar(valoare, la_data, durata_sub_1_an)` decide încadrarea exact pe criteriile de mai sus (sub prag sau durată sub un an → obiect de inventar), iar motorul generează automat notele contabile corespunzătoare: la achiziție (303 + 4426 = 401), la darea în folosință (603 = 303, cu evidență extracontabilă în contul 8035 până la scoaterea din uz) și la scoaterea din uz. Pentru bunurile care depășesc pragul și devin mijloace fixe, aplicația are un motor separat de amortizare (`core/d406_active.py`), care aplică metoda și durata alese conform regulilor de amortizare fiscală.

[iConta.eu](/)
