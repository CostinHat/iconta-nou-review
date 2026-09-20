# Așteptări F1 — ETAPA 5 (Contabilizare / validare jurnal) — scris ÎNAINTE de a rula

**Context:** după etapele 3-4, F1 (tenant_049) are **6 note CIORNĂ** în jurnal:
- `facturi`: 2 (D1 emisă 4111/707+4427; D2 primită 371/4426/401)
- `stocuri`: 1 (descărcare gestiune D1: 601=302 500)
- `banca`: 2 (încasare 5121=4111 1210; plată 401=5121 1210)
- `salarii`: 1 (statul de plată: 641=421, 421=4315/4316/444, 646=436)

**Etapa 5 = contabilizare = validarea ciornelor → `validata`** (patru-ochi, rol admin_firma; `jurnal/{id}/valideaza`).
O ciornă NU e evidență — fișele de cont, balanța și declarațiile se fac din note VALIDATE (regula repetată în UI:
„Fișa se face din notele VALIDATE — o ciornă nu e evidență").

**Ce NU schimbă validarea:** cifrele. Doar statusul ciornă→validata. Balanța rămâne echilibrată.

## Invarianți verificabili în DB după etapa 5 (tenant_049)
| ce | valoare așteptată |
|---|---|
| note `ciorna` rămase | **0** (toate 6 validate) |
| note `validata` | **6** (banca 2 + facturi 2 + salarii 1 + stocuri 1) |
| balanță echilibrată (Σ debit note = Σ credit note) | **da** (fiecare notă e balansată; suma la fel) |
| solduri parteneri închise de bancă | 4111 sold 0, 401 sold 0 (din etapa 3, acum în evidență validată) |

**Regula cascadei:** fără etapa 5 (contabilizare) dovedită, nu se poate declara „balanță/fișe verzi" la
etapele 6-8. Notele ciornă nu intră în fișe (probat: fișa de cont e goală pe ciorne).

**Temei:** N/A fiscal — pas de flux contabil (validare patru-ochi, R55: validarea transformă ciorna în
evidență). Cifrele vin din etapele 3-4, neschimbate.
