# ISTORIC OPERAȚIUNI PE TENANȚI

Index pe firmă al muncii de investigare/reparare/verificare. **Un rând per (tură × tenant).** Cronologic
descrescător (cel mai nou sus). **Sursa de adevăr rămâne `git log`** (mesajele de commit, imuabile); acesta e
doar indexul pe firmă, ca să nu depinzi de `git log --grep`. Regula: **fiecare tură ADAUGĂ un rând, nu rescrie**
(spre deosebire de `PREDARE_LANT.md`, care e snapshot-ul de predare și se rescrie).

Coloane: **Data** · **Ce s-a atins** (temele turei) · **Commit(uri)** · **Rămas** (ce a lăsat deschis tura).
Metoda de lucru per tenant = [`MODEL_AUDIT_TENANT.md`](MODEL_AUDIT_TENANT.md).

---

## tenant_006 — Achizitii IC Neplatitor SRL (CUI 95451848 · schema tenant_006 · cabinet Prisma 1968 · N1, neplătitor micro cu achiziții intracomunitare)

| Data | Ce s-a atins | Commit(uri) | Rămas |
|------|--------------|-------------|-------|
| 2026-08-18 | **Re-test complet cu audit_tenant.py** (F2/F6/F7): scos ce scapase - D301 mesaj 'nr_doc gol' (nume intern), a11y app-wide (etichete lipsa fa-stocuri/registratura/banca/rapoarte, contrast fa-control/etransport/centrecost, mobil tinte<24px) | (audit, necomis-fix) | campanie colectii date valide+invalide: F5 mesaj D301 + a11y P3 + colectii invalide |
| 2026-08-18 | **Mobil touch-target AA 2.5.8** pe 5 ecrane → 0 ținte <24px (.fir-veriga 19→24, .ajutor-btn 20→24, bug flex-shrink `#pc-cauta` 40→20px reparat) + **import motiv VIZIBIL** (nu title-only) pe 4 straturi, probat live salariați | `dc1ee22`, `e4fee31` | provocare **individuală** straturi import: firme (CUI ANAF), vector_fiscal, solduri_parteneri, plan_conturi; mobil pe casă/bancă, facturi, produse |
| 2026-08-18 | **axe landmarks app-wide → 0** (fix structural navigator.js: `<header>` banner + role=dialog + role=status) + **D406 conturi 731-738** verificat la sursă = excludere corectă din norma A (sunt în planul ONG) | `0392b3b`, `6be6a53` | — |
| 2026-08-18 | **D390↔d301** rezolvat pe corectitudine + **auto-derivare d301→D390 cod A/S** (decizia Costin) + rafinări tip 3/4 verificate la sursă + confirmare "nu e serviciu" per-furnizor + a11y contrast grila D301 | `8ceed16`, `0a47512`, `bce45bc`, `cba1856`, `abea0b6`, `a8c2f1e`, `4349d4b`, `816cf65` | — |
| 2026-08-18 | **D100 micro pe fapt de venituri** (semafor, restanță falsă stinsă) + a11y contrast Control fiscal + import blockages verificate + **field-level error marking** (contur roșu pe câmpul cu eroare, app-wide) | `b196943`, `2d9bc00`, `9638da3`, `c55308f` | — |
| 2026-08-18 | **D710** formular manual pornit pe tenant_006 (declarația 1/6 din campania de formulare _DOAR_API — detalii la secțiunea Global) | `e8d8cdc`, `885afe9` | — |
| 2026-08-17 | **Semafor: existenta_firma_an** numără achizițiile IC + casă/bancă (coerență) + cluster a11y contrast (WCAG AA) | `288f886`, `50c3ebf`, `128f239` | fronturi a11y/D390/field-marking (închise ulterior mai sus) |

---

## Global — funcționalități care nu sunt per-firmă (probate pe firme demo)

Muncă de produs care atinge TOATE firmele; se probează pe o firmă demo, dar nu e „a tenantului". Ținută aici ca
să nu se piardă între rândurile per-firmă.

| Data | Ce | Commit(uri) | Probat pe |
|------|-----|-------------|-----------|
| 2026-08-18 | **Campania 6 formulare manuale `_DOAR_API`** (D710, D311, D307, D107, D177, D207) — scoase din `_DOAR_API`, formular UI + gardă formular-gol + DUK valid + Playwright (axe/mobil). **ÎNCHISĂ.** | `e8d8cdc`, `238deb0`, `ad74bcd`, `bca0cc8`, `06cbeb1`, `89c3a26` | ALFA MICRO (8396); D710 pe tenant_006 |

---

## Alți tenanți (probe/scanuri, sesiuni anterioare — din `git log` complet, nu în fereastra de mai sus)

- **tenant_003 — Comert Micro TVA SRL**: firma de referință pentru uneltele vizuale (`nav_ecrane.ECRANE`: import mijloace fixe, vector fiscal, plan conturi, stat plată, declarații) + D100 pe venituri 0 corectat. Scanurile a11y/mobil de mai sus (dc1ee22, 0392b3b) rulează pe ecranele acestei firme (componente tenant-agnostice).
- **tenant_002 / t004 / t005**: probe cap-coadă în sesiuni anterioare (walk-uri Playwright în `frontend_test/`). Detalii în `git log` — de migrat aici la prima atingere nouă.

> Notă: acest fișier a fost creat pe 2026-08-18 și populat retroactiv din `git log` recent (turele documentate în `PREDARE_LANT.md`). Istoricul complet dinainte trăiește în `git log`; nu a fost reconstituit integral — se completează pe măsură ce fiecare tenant e atins din nou.
