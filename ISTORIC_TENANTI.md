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
| 2026-08-19 | **Audit D301 vector<->operatiuni (006)**: mesajul selectorului D301 se bazeaza pe campul platitor_tva (control_fiscal_api); 006 are platitor_tva=True -> D301 blocat, DESI are 3 operatiuni d301_operatiuni. DEFECT: ruta adauga nu verifica statutul -> reparat (refuza platitorii). PROIECTARE: mesajul e corect. DATE: vector 006 platitor_tva=True contradictoriu cu numele+operatiunile. | (vezi commit d301 guard) | DATE: contabilul decide - firma platitoare (sterge 3 op) sau neplatitoare (corecteaza vectorul platitor_tva=False). |
| 2026-08-19 | **Audit căi achiziție IC (D390/D301/D394) + 2 reparații D390**: mapat cum intră facturile de achiziție în afara SPV (rute `achizitie-*`→facturi, ecran D301→d301_operatiuni, manual e-Factura); reparat [Q1a] dublă-sursă (factură+d301 se adună în D390 → avertisment) și [Q2] primită-fără-CUI numită distinct. Gard RED + probă vizuală R14. Q1b (D394 gol pe neplătitor IC) și Q3 (ferestre exigibilitate) = proiectare corectă. Doar cod — date 006 neatinse (seed temporar curățat). | `ade5ab6` | Datorie de date app-wide (necuantificată): câți tenanți reali au dublă-sursă/primită-fără-CUI. |
| 2026-08-19 | **F6 a11y app-wide reparat (perimetru extins 006) + 7 ecrane gardate**: auditul orchestrator pe 006 (tid 4841) a dat F2/F7 VERDE (firmă N1 fără declarații datorate; 5 neclar = necunoscute declarate P2, §5 extern legitim), F6 ROȘU pe 7 ecrane shell. Reparat cu tiparul: fără-etichetă (8 controale date/select/file -> aria-label), contrast (`.buton-sters` #ff3b30->--rosu, `.cap-titlu` #888->#6b6b6b, `.pf-frand-nume span`/`CUL.rosu` --rosu-semafor->--rosu, +2 text-uses), țintă<24px mobil (`.btn-link`+`input[file]` min-height 24). Cele 7 ecrane ÎNREGISTRATE în `nav_ecrane.ECRANE` (scan 13, gard) -> închide 7/21 din datoria hărții. | (F6 app-wide + 7 ecrane) | Latent app-wide: `CUL.galben/gri`-ca-text (contrast, de verificat când se renderizează acele stări); F3/F5 manual pe 006. |
| 2026-08-19 | **F5 nume intern D301 (perimetru 006) reparat + tipar app-wide GARDAT**: mesajele D301 `fără număr document (nr_doc gol)` / `(data_doc gol)` expuneau numele intern al câmpului (Regula 14.4) -> rescrise fără paranteză. Descoperit că tiparul e MASIV app-wide (274 mesaje / 31 generatoare, ex. `categ_venit`, `cif_c`, `nr_contract`). Gardă-ratchet `core/test_mesaje_generare_fara_camp_intern.py` (baseline per-fișier, niciun fișier nu crește; burn-down la 0). | (F5 D301 + gard app-wide) | Tipar app-wide 274 = burn-down F5 DINCOLO de perimetrul 006 (nu datoria firmei; gardat contra creșterii). |
| 2026-08-19 | **DS + mobil (F6) parcurse pe perimetrul import 006 (cerut de Costin)**: citirea DESIGN_SYSTEM a scos vector fail-fast (cap.6 pct.4) -> colectare multi-camp, marcheaza toate campurile lipsa odata; changelog DS v2.56/v2.57 (Regula 6). Trecerea Pixel 5 a scos `scrollable-region-focusable` pe corpul modal partajat `.fereastra-corp` -> `tabindex=0` app-wide. axe-pe-mobil pe firme/vector/plan/parteneri = 0, body 393, tinte >=24 (AA), title-unic 0. §5 perimetru = GOL (DS + F6 incluse). | `b94fcf2`, `6683623` | — |
| 2026-08-19 | **Plan de conturi (Adauga cont) - camp gol MARCAT + obligativitate inainte de buton**: inchide ultima datorie de field-marking din PERIMETRUL plan_conturi (tenant_006) - asterisc `.oblig` (obligativitate inainte de buton) + campul gol marcat (`.camp-invalid`) cu mesaj care numeste ce lipseste (simbol vs denumire); duplicatul marcheaza simbolul. Gard RED (4) + probat live (ambele goale->ambele rosii; doar simbol->doar denumirea; axe 0). §5 pe perimetrul straturilor de import 006 = GOL. | `ebd05c6` | — |
| 2026-08-19 | **Strat import VECTOR FISCAL - camp obligatoriu marcheaza campul vinovat**: provocat pe tenant_001 (firma fara vector) - platitor TVA fara periodicitate decont -> salvare respinsa (nicio scriere), mesaj corect DAR grupul nu era marcat (Regula 14.4 pct.4). Fix: `salveaza()` intoarce `camp` -> ruta `erori_campuri` -> `migrare.js` marcheaza grupul (`.camp-invalid`+aria-invalid). Gard RED (5) + probat live (contur rosu privit, axe 0). Cele 4 straturi import 006 INCHISE. | `73522f5` | — (in perimetru; tiparul in alte formulare = pattern app-wide, nu datoria firmei) |
| 2026-08-18 | **Straturi import solduri_parteneri + vector_fiscal verificate + a11y contrast P3**: solduri_parteneri = mesaj conform by-design (poarta Q5 preview=salvare: per-rand DE CE + Salvare blocata, probat live cu conturi ne-partener); vector_fiscal = obligativitate marcata inainte de buton (asterisc) + fara default tacit (probat live). axe pe preview parteneri a scos 2 contrast `.mig-sold-cont` #347ab8=3.86<4.5 pe #e9edf3 (fix-ul Control fiscal asumase «pe alb», gresit) -> baza #2f6fa6 (P3, toate instantele) + gard. | `2bdac14` | — (vector inchis in 73522f5) |
| 2026-08-18 | **Strat import PLAN DE CONTURI - suprascriere tacuta reparata**: adaugarea manuala facea `ON CONFLICT DO UPDATE` -> simbol duplicat (101) redenumea tacut contul OMFP standard «Capital». Acum refuz 409 in limba contabilului, cont standard neatins (re-cautare «101» = «Capital»). Gard RED + probat live (axe 0, mobil 393). | `a651fec` | — (field-marking inchis in `ebd05c6`) |
| 2026-08-18 | **Strat import FIRME - drop tacut reparat**: intrare fara cifre (typo/antet, «ABC») era eliminata inainte de ANAF fara niciun semn (Regula 4). Acum `separa_cui()` -> banner vizibil «N intrari nu contin un CUI: ...». Gard RED (7) + probat live (banner vizibil, axe 0, mobil 393). | `fd224d2` | - |
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
