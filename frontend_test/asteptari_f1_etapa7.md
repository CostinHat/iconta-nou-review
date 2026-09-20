# Așteptări F1 — ETAPA 7 (Verificări interne / Control fiscal) — scris ÎNAINTE de a rula

**Context:** Control fiscal (`#fa-control`, GET /control-fiscal/{id}) = semafor conformare: declarații
datorate/depuse + verificări contabile (reconciliere sursă↔declarație, coerență).

## Așteptat (F1, înainte de generarea/depunerea declarațiilor)
| ce | valoare așteptată |
|---|---|
| stare generală | **roșu** — DAR din declarații nedepuse (28 lipsă), NU din corupție de date |
| declarații datorate / depuse | ~30 / 0 (nimic depus încă — etapele 8-9) |
| reconciliere sursă↔declarație | **verde** (contabilitatea F1 e coerentă cu ce ar declara) |
| contradicții / corupție de date | **niciuna** |

**Interpretare (regula cascadei):** „roșu" aici NU invalidează etapele 3-6 — e semnalul corect că
declarațiile nu s-au depus. Verificarea internă care contează (reconciliere_surse) e **verde**: fluxul
date→jurnal (etapele 3-5) e coerent cu declarațiile care se vor genera la etapa 8.

**Temei:** N/A — pas de verificare (semafor conformare). Nu produce note, nu schimbă cifre.
