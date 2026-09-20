# Așteptări F1 — SESIUNEA B (scris ÎNAINTE de a rula aplicația pe date)

**Regula (TESTE.md):** cifrele așteptate se îngheață AICI, din temeiurile verificate în Sesiunea A,
înainte de a rula aplicația. Altfel copiezi output-ul și testezi că 1 = 1.

**F1** (TESTE.md tabelul firmelor): SRL · TVA **lunar** · impozit **micro 1%** · comerț cu stoc,
3 salariați, descărcare de gestiune. Cabinetul A. An fiscal **2026**.

## Identitate (date de test, cifre de control VERIFICATE)
- Cabinet: „Cabinet Test Sesiunea B SRL" (creat prin înregistrare — contabil prima dată).
- Firmă F1: „F1 Comerț Stoc SRL", **CUI RO401002001** (cifra de control validă, algoritm oficial).
- 3 salariați (CNP-uri cu cifra de control validă): `1900301400108`, `2850702400152`, `1921103400201`.

---

## Etapa 2 — Configurare firmă (vector fiscal) — AȘTEPTĂRI

`tip_firma = SRL` · `regim_tva = lunar` · `platitor_tva = DA` · `impozit = micro 1%` · `an_fiscal = 2026`.

**Vectorul fiscal (setul de declarații pe care regimul TREBUIE să-l producă), din temeiuri:**
| Declarație | Se depune? | Periodicitate | Temei |
|---|---|---|---|
| **D300** (decont TVA) | DA | **lunară** | CF art.322 (plătitor TVA cu perioadă lunară) |
| **D394** (informativă TVA național) | DA | lunară (cu D300) | OPANAF 77/2022 |
| **D112** (contribuții salarii) | DA | lunară (3 salariați) | CF Titlul V; OUG 158/2005 |
| **D100** (obligații de plată — **impozit micro 1%**) | DA | **trimestrială** | CF Titlul II (impozit pe veniturile microîntreprinderilor); OPANAF |
| **D406** (SAF-T) | DA | lunară | OPANAF 1783/2021 (odată intrat în obligație) |
| **D101** (impozit pe **profit** anual) | **NU** | — | micro NU depune D101 (e pentru profit — F2); decizie Costin 20.09 |
| **D390** (recapitulativă IC) | NU | — | fără operațiuni IC (comerț stoc intern) |

### DISCREPANȚĂ DE PROFIL — REZOLVATĂ (decizie Costin 20.09)
Rândul F1 din `TESTE.md` lista „D101" — **eroare de redactare**. F1 e **micro 1%**: depune **D100**
(impozit pe veniturile microîntreprinderilor, trimestrial), **NU D101** (impozit pe profit, doar plătitorii
de profit — F2). Setul CONFIRMAT F1 = **D300 · D394 · D112 · D100 · D406**. TESTE.md corectat.

**Invariant etapa 2:** regimul ales produce EXACT setul de mai sus (nici o declarație în plus, nici una
lipsă). Capcană (TESTE.md): regim schimbat retroactiv care rescrie tăcut trecutul.

---

## Etapa 1 — Migrare / preluare — AȘTEPTĂRI

Firmă NOUĂ (nu preluare de la alt program): preluarea = soldurile inițiale + plan de conturi + parteneri
+ stoc inițial + salariați, la **01.01.2026**.

**Invariant (TESTE.md):** `Σ debit = Σ credit` pe soldul preluat; nr. rânduri importate = nr. din fișier
− duplicate raportate explicit. **Capcană:** import „reușit" cu 0 rânduri; dedup care înghite tot.

**Sold inițial de deschidere (echilibrat, exemplu minim pentru comerț cu stoc):**
| Cont | Denumire | Debit | Credit |
|---|---|---|---|
| 1012 | Capital subscris vărsat | | 200,00 |
| 371 | Mărfuri (stoc inițial) | 5.000,00 | |
| 5121 | Conturi la bănci | 10.000,00 | |
| 401 | Furnizori | | 3.000,00 |
| 4111 | Clienți | 2.000,00 | |
| 117 | Rezultat reportat | | 13.800,00 |
| **Σ** | | **17.000,00** | **17.000,00** |
→ **Σdebit = Σcredit = 17.000,00** (invariantul etapei 1).

**Plan de conturi:** standard OMFP 1802/2014 (se încarcă la crearea firmei). **Parteneri:** ≥1 client
(CUI valid) + ≥1 furnizor (CUI valid). **Stoc inițial:** ≥1 articol în 371 cu `valoare` = soldul 371.
**Salariați:** 3 contracte active de la 01.01.2026 (salariu brut ≥ salariul minim 2026 — valoarea exactă
se citește din registrul de cote Sesiunea A la etapa 4, nu se îngheață aici).
**Mijloace fixe:** F1 nu are (mijloacele fixe = profilul F2).

---

## Etapele 3–11 (declarații, cifre pe an) — SE ÎNGHEAȚĂ pe măsură ce se proiectează setul de tranzacții
Cifrele pe an (D300 lunar, D394, D112, D100, D406) depind de setul de facturi/mișcări de stoc/salarii care
se introduce la etapele 3–4. Se adaugă AICI, tot înainte de a rula fiecare etapă, din temeiuri (Sesiunea A).
Regula bazei nule (TESTE.md): orice declarație cu bază 0 e EROARE până la proba contrară.
