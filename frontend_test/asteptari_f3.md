# Așteptări F3 — profil + etapele 1-2 — scris ÎNAINTE de a rula

**Profil (plan Sesiunea B, cotă corectată la 2026):** SRL, **neplătitor TVA + înregistrat art.317**, **micro 1%**
(NU 3% — OUG 89/2025 a abrogat cota 3% de la 01.01.2026; decizie Costin 21.09). **Fără salariați.** Cabinet A.
Testează UNIC: **D301** (decont special TVA — achiziții IC + servicii UE, la neplătitor art.317), **D390**
(recapitulativ VIES), **taxare inversă**.

- **CUI:** RO404000013 (cifra de control verificată).
- **Denumire:** F3 Intracomunitar SRL.
- **Vector fiscal:** regim=micro (1%), platitor_tva=**nu** (neplătitor), operatiuni_ic=**da**, inreg_art317=**da**.
- **Set declarații așteptat:** **D301** (achiziții IC + servicii UE), **D390** (recapitulativ), **D100** (micro 1%),
  **D406** (SAF-T). NU D300 (neplătitor de TVA); NU D112 (0 salariați); NU D394 (D394 e pentru plătitori de TVA).

## Etapa 1 — sold inițial (echilibrat, simplu — F3 nu are stoc/mijloace fixe)
| cont | debit | credit | ce |
|---|---|---|---|
| 5121 | 5.000 | | Bancă |
| 1012 | | 200 | Capital |
| 117 | | 4.800 | Rezultat reportat |
| **Σ** | **5.000** | **5.000** | ECHILIBRAT |

## Invarianți etapa 1-2 (DB tenant F3)
| ce | valoare |
|---|---|
| Σdebit = Σcredit sold | **5.000 = 5.000** |
| vector fiscal | (micro, platitor_tva=false, operatiuni_ic=true, art.317=true) |
| salariați | **0** |

**Temei:** micro 1% CF art.51 alin.(1) (OUG 89/2025, unic 2026); art.317 CF art.317 (înregistrare pentru IC);
taxare inversă IC CF art.331/307; D301 CF art.324; D390 recapitulativ CF art.325. Cifrele din generatoare + DUK.

**Capcană:** F3 e neplătitor DAR are obligații de TVA prin IC (D301/D390) — „neplătitor" nu înseamnă „fără TVA".
Regula bazei nule: achizițiile IC reale, nu bază 0.
