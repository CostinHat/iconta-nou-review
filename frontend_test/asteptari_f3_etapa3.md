# Așteptări F3 — ETAPA 3 (operațiuni intracomunitare) — scris ÎNAINTE de a rula

**Context.** F3 = SRL, **neplătitor TVA + înregistrat art.317**, **micro 1%** (2026), operațiuni IC, 0 salariați.
tenant_051, Cabinet A. Perioada: sept 2026. Etapele 1-2 gata (vector corect; sold Σ=5.000). Regula bazei
nule: achiziții IC reale, nu bază 0.

## Operațiunile etapei 3 (2 achiziții IC, furnizor UE)
| # | tip | descriere | valută | val | curs | bază (lei) | cotă | TVA (lei) | furnizor |
|---|---|---|---|---|---|---|---|---|---|
| A | **1** (bunuri IC) | Marfă din DE | EUR | 1.000 | 5,0000 | **5.000** | 21% | **1.050** | DE (cod TVA UE) |
| B | **5** (servicii IC) | Serviciu UE | EUR | 500 | 5,0000 | **2.500** | 21% | **525** | DE (cod TVA UE) |

- **Cotă:** 21% standard 2026 (period-aware, CF art.291 alin.(1); alin.(8) leagă cota AIC de cota internă).
  Exigibilitate AIC: CF art.284 alin.(2) — a 15-a zi a lunii următoare faptului, sau data facturii.
- **Bază = val × curs, rotunjită la leu; TVA = round(bază × cotă/100), STOCAT** (d301 îl citește, nu-l recalc).

## D301 (decont special) — din operațiunile D301
| ce | valoare |
|---|---|
| operațiuni | **2** (tip 1 + tip 5) |
| bază totală | **7.500** (5.000 + 2.500) |
| TVA total datorat | **1.575** (1.050 + 525) |

## D390 (recapitulativ VIES) — derivat automat din operațiunile D301
| op | cod D390 | bază |
|---|---|---|
| A (tip 1 bunuri) | **A** (achiziții IC bunuri) | 5.000 |
| B (tip 5 servicii) | **S** (achiziții servicii IC) | 2.500 |

## Contabilizare — taxare inversă, CONȘTIENTĂ DE PLĂTITOR (reparat, DECIZII 65)
F3 e **neplătitor art.317** → TVA pe IC e **DATORATĂ dar NEDEDUCTIBILĂ** (CF art.297: deducerea cere
art.316) → intră în **COSTUL achiziției** (contul principalului + 446), **NU 4426=4427**:
| op | cont bază | linii notă (așteptat) |
|---|---|---|
| A (bunuri, cont 371) | 371 | **371 = 401 · 5.000** + **371 = 446 · 1.050** (TVA în costul mărfii) |
| B (serviciu, cont 628) | 628 | **628 = 401 · 2.500** + **628 = 446 · 525** (TVA în costul serviciului) |

*Un plătitor ar avea `4426 = 4427` (deductibil); F3 NU — asta e miezul reparației. Contra-verificare:
la un plătitor, aceeași operațiune trebuie să dea `4426=4427`.*

## Set declarații așteptat (etapa 3, step 8) — DUK-valid
- **D301** (achiziții IC + servicii UE) — din operațiunile D301.
- **D390** (recapitulativ) — cod A (5.000) + cod S (2.500).
- **D100** (micro 1%) — pe VENITURI; F3 n-are venituri în perioadă → impozit micro pe bază proprie
  (achizițiile IC NU sunt venit, nu intră în baza micro, CF art.51/53). Se confirmă cifra la rulare.
- **D406** (SAF-T) — include operațiunile.
- NU D300 (neplătitor); NU D112 (0 salariați); NU D394 (pentru plătitori).

## Capcane / limite declarate
- **Dublă raportare D390:** `d301-operatiuni` alimentează D301+D390; `achizitie-ic` alimentează
  D390 din factură. Folosite ÎMPREUNĂ → D390 dublu (d390.py:415 semnalează, nu blochează). Pentru
  neplătitor nicio cale unică nu dă și D301 și nota corectă → **restanță de flux** (DECIZII 65), nu
  se rezolvă aici; proba trebuie să aleagă o singură cale și s-o declare.
- **Temei:** micro 1% CF art.51; art.317 (înregistrare IC); taxare inversă CF art.307/331; D301 art.324;
  D390 art.325; nedeductibilitate CF art.297. Cifrele din generatoare + DUK, confirmate la rulare.
