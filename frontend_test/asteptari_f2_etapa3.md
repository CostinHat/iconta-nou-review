# Așteptări F2 — ETAPA 3 (documente primare) — scris ÎNAINTE de a rula

**Context:** F2 = SRL profit 16%, TVA trimestrial, FĂRĂ stoc (are mijloc fix, nu marfă). Perioada: sept 2026 (T3).

### D1 — Factură EMISĂ (serviciu, fără descărcare de gestiune)
Vinde serviciu 5.000 + 21% TVA 1.050 = **6.050**. Serviciu (fără articol) → NU apare poarta „pleacă marfa".
Note: **4111 = 6.050** / **704 (sau 707) = 5.000** + **4427 = 1.050** (TVA colectată T3).

### D2 — Registru de casă (F2 UNIC) — 2 operațiuni
- Ridicare de la bancă 1.000: **5311 = 581** (numerar intră în casă).
- Plată furnizor din casă 500: **401 = 5311** (numerar iese).

## Invarianți DB după etapa 3 (tenant_050)
| ce | valoare |
|---|---|
| facturi emise | **1** (serviciu 6.050, TVA 1.050) |
| TVA colectată (4427) T3 | **1.050** |
| operațiuni casă | **2** (ridicare 1.000 + plată 500) |
| sold casă 5311 | **500** (1.000 intrat − 500 ieșit) |

**Temei:** TVA colectată CF art.291 (21%); registru de casă Legea 70/2015 (plafoane numerar). Cotă serviciu
determinată de AI (potriveste_cota) — se confirmă la rulare, nu din memorie.
**Capcană:** F2 NU are stoc — emiterea serviciului NU trebuie să declanșeze descărcarea de gestiune (F172).
