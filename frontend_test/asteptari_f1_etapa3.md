# Așteptări F1 — ETAPA 3 (intrare documente primare) — scris ÎNAINTE de a rula

**Context:** F1 = SRL, micro 1%, plătitor TVA lunar, comerț cu stoc (CMP), 3 salariați. Stoc inițial (etapa 1):
Marfa A, 100 buc × 50 = 5.000 (cont 371). Perioada de test: **septembrie 2026** (UI foloseste data curenta).

**Invariant etapa 3 (TESTE.md):** fiecare document → EXACT o intrare în registru; total documente = total listă
= total raport. **Capcană:** parser cu 0 linii tratat ca „lună fără documente"; semn inversat; document dublat la reimport.

## Documentele de introdus (prin interfață)

### D1 — Factură EMISĂ (vânzare cu descărcare de gestiune)
Vinde 10 buc Marfa A × 100 lei = **1.000 bază + 21% TVA 210 = 1.210 total**.
Note contabile așteptate:
- Vânzare: **4111 = 1.210** (client) / **707 = 1.000** (venit) + **4427 = 210** (TVA colectată).
- Descărcare gestiune (CMP 50/buc × 10): **607 = 500** / **371 = 500** (ieșire stoc).
- TVA **colectată** sept.: **210**.

### D2 — Factură PRIMITĂ (achiziție marfă) — prin SPV (calea reală, corectată la măsurare)
Cumpără 20 buc Marfa A × 50 lei = **1.000 bază + 21% TVA 210 = 1.210 total**.
**Cale corectată (20.09):** factura primită vine DOAR prin SPV (nu există intrare manuală, corect RO
e-Factură). Test: se inserează efactura_primite (simulare livrare SPV) + se validează prin UI
(#fac-primite → cont cheltuială 371 → Validează). Notele NIR-GV din varianta inițială coincid cu cele SPV.
Note contabile așteptate:
- **371 = 1.000** (marfă) + **4426 = 210** (TVA deductibilă) / **401 = 1.210** (furnizor).
- TVA **deductibilă** sept.: **210** → ajunge în D300 (verificat: R22_1=1000/R22_2=210).

**FINDING măsurat (NU reparat — decizie Costin):** validarea SPV NU mișcă stocul CANTITATIV (fișe de
magazie/CMP). Cantitatea rămâne 90 buc (din D1), deși contabilul (371) urcă la 5.500. Cele două sunt
DOUĂ documente nereconciliate: SPV = D300 + valoare (371); cantitatea = separat prin NIR/CV-intrare,
care ar dubla nota 371/4426 în jurnal. Nicio cale non-SPV nu alimentează D300 cu deductibila de stoc.

### D3 — Extras bancar (o încasare + o plată)
- Încasare de la client 1.210: **5121 = 1.210 / 4111 = 1.210**.
- Plată către furnizor 1.210: **401 = 1.210 / 5121 = 1.210**.

## Invarianți verificabili în DB după etapa 3 (tenant_049)
| ce | valoare așteptată |
|---|---|
| nr. facturi (emise+primite) | **2** (D1 emisă + D2 primită) |
| TVA colectată (4427) sept. | **210** |
| TVA deductibilă (4426) sept. | **210** |
| D300 TVA de plată sept. (colectată − deductibilă) | **0** (210 − 210) — NU e bază 0 tăcută: sunt operațiuni reale |
| 371 CONTABIL după D1+D2 | **5.500** (5.000 + 1.000 achiziție SPV − 500 descărcare) |
| cantitate Marfa A (fișă magazie) | **90 buc** (100 − 10; SPV NU mișcă cantitatea — vezi FINDING D2) |
| DIVERGENȚĂ 371-contabil vs fișă CV | **1.000** (achiziția SPV pe valoare, nu pe cantitate) — finding |
| fiecare document → o intrare în registru (Σ note = Σ documente) | da (fără dublare la reimport — vezi C5/etapa 3 capcană) |

Notă: micro (impozit 1% pe venit, D100 trimestrial) e SEPARAT de TVA; venitul din D1 (1.000) intră în baza micro
la etapa 8-9, nu aici.
