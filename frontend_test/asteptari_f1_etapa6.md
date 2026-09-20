# Așteptări F1 — ETAPA 6 (Sfârșit de lună) — scris ÎNAINTE de a rula

**Context F1 (comerț micro, TVA lunar):** operațiunile de sfârșit de lună relevante:
- amortizare mijloace fixe — **N/A** (F1 nu are mijloace fixe).
- descărcare gestiune CMP — **deja făcută** per-factură la D1 (F172).
- **închiderea lunii facturi** (`#fac-inchide`, `facturi/perioada/confirma`) — acțiunea testabilă: blochează
  editarea facturilor pe septembrie, evidența devine "completă" (semaforul se poate sprijini pe ea).
  Precondiție: fără blocaj (e-facturi primite nevalidate) — D2 e validat, deci `poate_confirma=True`.

## Invarianți verificabili în DB după etapa 6 (tenant_049)
| ce | valoare așteptată |
|---|---|
| stare închidere sept. 2026 | **confirmat=True** (luna închisă) |
| redeschidere disponibilă | da (`#fac-redeschide` apare; simetric) |

**Temei:** N/A fiscal — pas de flux (închiderea lunii, R55/cap.23). Închiderea e opțională; o testăm ca acțiune
de sfârșit de lună. Nu schimbă cifre — doar blochează editarea și marchează evidența completă.

**OBS:** pentru F1 etapa 6 e subțire (fără amortizare, CMP deja descărcat). Închiderea lunii e singura
acțiune de stare. Regularizarea TVA (4427/4426→4423) e calculată de D300, nu o notă separată în acest flux.
