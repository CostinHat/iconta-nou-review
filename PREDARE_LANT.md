# PREDARE LANT — oprire la limita de 6 clustere/rulare (03.08.2026)

Predare scrisa pentru o sesiune NOUA cu context GOL (§2.3 pct.6). Contine tot ce trebuie ca sa continui
lantul de clustere fara sa fi citit sesiunea anterioara.

## HEAD si stare
- **HEAD:** `ec23dc3` · tree curat (`git status --porcelain` gol) · **ahead 32 fata de origin/main, NEPUSHAT**.
- **Poarta la oprire (toate VERZI):** `venv/bin/pytest` = 1275 passed / 2 skipped / **23 xfailed**;
  `verificator_conformitate.py` TOTAL 0; tree curat. Oprire la stare sanatoasa.
- **Push:** decizia EXCLUSIVA a lui Costin. NU impinge. Commite local si continua.
- **Unde se lucreaza:** pe server, `ssh iconta`, `~/iconta_nou`. pytest/verificator/DUK = `venv/bin/...`.
  NU pe copia locala. Editarile pe server se fac cu scripturi python scp-uite (Edit local nu atinge serverul).

## Sold lant (aceasta rulare)
`SOLD LANT: 5 clustere INCHISE + 1 gap verificat-neinchis / +2 xfail datorii noi / start 2d3919c -> curent ec23dc3`
- **Inchise (√ 03.08):**
  1. `baze contributii (CAS/CASS/imp/CAM) | d112` (c3d74a7) — cotele 25/10/10/2.25% rutate period-aware prin
     `cota()` (CF art.138/156/78/220^3), eliminate literalele hardcodate. Value-preserving.
  2. `rotunjire aritmetica (A91b) | d112` (3b4cffe) — REPARAT: minimul part-time (prag_zile, cas_min_pt,
     cass_min_pt) rotunjea BANCAR in B4_*P declarat (prag_zile=1226 -> CAS 306 in loc de 307); rutat prin `_d112int`.
  3. `sect_II tip_venit (impozit retinut) | d205` (a6a770d) — REPARAT: impozit dividende hardcodat 10%, gresit pt
     2026; rutat period-aware 16% (Legea 141/2025, CF art.97). Proba DB reala + DUK. Structura = OPANAF 102/2025.
  4. `rotunjire | d205` (83cfe0f) — verificat aritmetic (deja corect `_i` ROUND_HALF_UP); gardat cross-generator.
  5. `cote TVA -> randuri | d300` (b234d81) — REPARATIE MARE: achizitii deductibile 11% erau la R74 (=19% legacy,
     respins DUK) -> R23 (Rd.25); 9% erau la R76 (taxare inversa, pierdut din totalul R27) -> scos din auto +
     avertisment manual. Livrari 21/11/9 -> R9/R10/R11 verificate + proba DUK reala.
- **xfail datorii NOI (2), ambele din d300:**
  - `test_datorie_d300_9pct_deductibil_auto` — 9% deductibil auto (validatorul instalat respinge R75 din v12).
  - `test_datorie_d300_exigibilitate_tva_la_incasare` — vezi mai jos (clusterul urmator).

## Clusterul URMATOR (mecanic) — CERE DECIZIE DE PRODUS
Ruleaza `venv/bin/python3 -c "from core import agenda; print(agenda.urmator_cluster())"`.
Intoarce: **`('exigibilitate / TVA la incasare', 'd300')`, 53 ramase, 0 blocate.**

**ATENTIE — nu e o aliniere, e un GAP de fond (documentat in DECIZII.md 03.08 + xfail):** D300 IGNORA complet
regimul TVA la incasare (CF art.282). `d300.pull` filtreaza facturile DOAR dupa `data_emitere` si nu citeste
`firma_profil.tva_la_incasare`. Pentru o firma pe acest regim, exigibilitatea TVA colectate e la INCASARE (cap 90
zile de la emitere), iar TVA deductibila la PLATA achizitiei (art.282 alin.3-6). Acum D300 declara pe toate
facturile emise/primite in perioada -> exigibilitate gresita pentru aceste firme.
- **Fezabil:** datele exista — `firma_profil.tva_la_incasare` (bool) + `facturi.platita_la` (timestamp) + `data_scadenta`.
- **De ce neinchis:** e FEATURE care schimba substantial sumele declarate, cu reguli de temei de verificat verbatim
  (art.282 alin.3-6, capul de 90 zile, tratamentul deductibilei). §2.3 pct.2 = decizie de produs (domeniu: doar
  firmele pe regim; abordare: filtrare la pull dupa platita_la vs. rand dedicat de exigibilitate). **Cere greenlight
  Costin pe temei + domeniu inainte de implementare. Nu se face pe jumatate.**

## Blocaje / datorii deschise relevante (cu motiv)
1. **exigibilitate TVA la incasare | d300** — gapul de mai sus (xfail test_datorie_d300_exigibilitate_tva_la_incasare).
   DECIZIE DE PRODUS.
2. **9% deductibil auto | d300** (xfail test_datorie_d300_9pct_deductibil_auto) — structura v12 pune 9% deductibil
   la Rd.25.1/R75, dar validatorul DUK INSTALAT respinge R75 ("nu trebuie sa exista aici"). Momentan 9% deductibil e
   scos din auto + avertisment de declarare manuala. Se deblocheaza cand validatorul instalat accepta R75 (sau se
   identifica randul deductibil 9% corect la sursa).
3. **MF metode degresiva/accelerata** (xfail test_datorie_mf_metode_amortizare) — subsistemul mijloace fixe/D406
   calculeaza doar amortizare liniara; d101 nu e afectat (ia amortizarea fiscala ca input).
4. **Alte xfail preexistente** (23 total): art.XI CM procente pre-141, sub-randuri C2 cod 05, verificatorul netestat
   pe clasificare, D394 scutit-catre-CUI, etc. — vezi `git grep "@pytest.mark.xfail" core/test_datorie.py`.

## Registre atinse in aceasta rulare
- **core/d112.py** (cote period-aware + minim part-time aritmetic), **core/d205.py** (dividend period-aware + OPANAF
  102/2025), **core/d300.py** (mapare achizitii deductibile 11%->R23, 9% manual + avertisment).
- **DECIZII.md, GARZI.md, TESTE.md** — cate o intrare per cluster; contor teste 1284 -> 1300; secventa 59 -> 53.
- **anaf_surse/** — neatins (sursele existau: cod_fiscal, d205_struct, d300_struct).

## Cum continui (sesiune noua)
1. Citeste CLAUDE.md §2.2 (structura raportului) + §2.3 (regim de lant).
2. Ruleaza `agenda.urmator_cluster()` -> `exigibilitate / TVA la incasare | d300`.
3. **NU porni implementarea direct** — e decizie de produs (vezi mai sus). Prezinta-i lui Costin constatarea +
   optiunile de domeniu/abordare si cere greenlight pe temei (art.282 verbatim la sursa). Daca vrea sa continui cu
   ALT cluster, sari-l: urmatoarele din secventa sunt in TESTE.md (`## Secventa de verificare`).
4. Verifica temeiurile la sursa (anaf_surse/ intai; daca lipseste, cauta la sursa oficiala si SALVEAZA).
5. Increments testate, commit local per increment, gard + registru la inchidere. Contorul de 6 clustere se reseteaza.
6. Sterge acest fisier (PREDARE_LANT.md) dupa ce ai reluat lantul.
