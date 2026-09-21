# Așteptări F2 — profil + etapele 1-2 — scris ÎNAINTE de a rula

**Profil (din plan Sesiunea B):** SRL, **TVA trimestrial**, **impozit pe profit 16%**. Testează UNIC față de F1:
D300 **trimestrial**, D100 (profit), **amortizare + mijloace fixe**, **registru de casă**. **Fără salariați**
(planul nu listează D112). Cabinet A (același cabinet ca F1: contabil.b@sesiuneab.test).

- **CUI:** RO403000015 (cifra de control verificată).
- **Denumire:** F2 Profit Amortizare SRL.
- **Vector fiscal:** profit 16%, plătitor TVA **trimestrial**, fără IC, fără salariați.
- **Set declarații așteptat:** D300 (trimestrial), D100 (obligații trimestriale profit), D101 (profit anual),
  D394, D406. (NU D112 — fără salariați; NU D100-micro — e profit, nu micro.)

## Etapa 1 — sold inițial (echilibrat), cu mijloc fix
| cont | debit | credit | ce |
|---|---|---|---|
| 2131 | 12.000 | | Echipamente (utilaj) |
| 2813 | | 2.200 | Amortizare cumulată utilaj (11 luni × 200, Feb–Dec 2025) |
| 5121 | 5.000 | | Bancă |
| 1012 | | 200 | Capital |
| 117 | | 14.600 | Rezultat reportat |
| **Σ** | **17.000** | **17.000** | ECHILIBRAT |

**Mijloc fix (1):** utilaj, cod MF-001, valoare 12.000, **valoare reziduală (salvage) = 0**, cont 2131/amortizare
2813, DNF 60 luni (5 ani), metoda liniară, PIF 2025-01-15. **Amortizabil = valoare − rezidual = 12.000;
amortizare lunară = 12.000/60 = 200 lei** (verificat la etapa 6). NOTĂ: câmpul „rezidual" din import = valoarea
reziduală finală (salvage, standard CF art.28: amortizabil = cost − reziduală), NU „valoare rămasă de amortizat".

## Invarianți etapa 1-2 (DB tenant F2)
| ce | valoare |
|---|---|
| Σdebit = Σcredit sold | **17.000 = 17.000** |
| mijloace_fixe | **1** (MF-001, valoare 12.000, dnf 60, liniar) |
| vector fiscal | (profit, TVA trimestrial, fără IC, fără salariați) |
| salariați | **0** |

**Temei:** amortizare liniară OMFP 1802/2014 + CF art.28 (amortizare fiscală); profit 16% CF Titlul II art.17;
TVA trimestrial CF art.322 alin.(2). Valorile așteptate se confirmă cu generatoarele (nu din memorie).

**Capcană (regula bazei nule):** F2 NU e F7 — are activitate reală; orice declarație cu bază 0 e eroare.
**Capcană (mijloace fixe):** amortizarea la etapa 6 NU mai e N/A (ca la F1) — trebuie să producă nota 6811=2813 200.
