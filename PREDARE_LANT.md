# PREDARE LANT — checkpoint dupa feature TVA la incasare (03.08.2026, lant #2)

Predare pentru o sesiune NOUA cu context GOL (§2.3 pct.6). Oprire = checkpoint de calitate dupa un feature mare
(TVA la incasare), NU limita de 6 (lant #2 are inca margine). Munca fiscala pe context lung -> predau pentru
context proaspat la clusterul urmator (taxare inversa cere citit art.331 la sursa + posibil inchis un GRI).

## HEAD si stare
- **HEAD:** `91a5e5f` · tree curat · **ahead 34 fata de origin/main, NEPUSHAT**.
- **Poarta (toate VERZI):** `venv/bin/pytest` = 1282 passed / 2 skipped / **22 xfailed**; `verificator` TOTAL 0.
- **Push:** decizia EXCLUSIVA a lui Costin. NU impinge.
- **Unde:** `ssh iconta`, `~/iconta_nou`. pytest/verificator/DUK = `venv/bin/...`. Editari pe server prin scripturi
  python scp-uite (Edit local NU atinge serverul). Full-suite ~90s (timeout 200000+).

## Sold lant #2 (aceasta rulare)
`SOLD LANT #2: 1 cluster INCHIS (feature mare) / 0 datorii noi / 1 datorie INCHISA / start 2d3919c -> 91a5e5f`
- **Inchis (√ 03.08):** `exigibilitate / TVA la incasare | d300` (91a5e5f) — FEATURE complet, greenlight Costin
  (ambele laturi + proportional). art.282(3)+(8)/297(2-3), OUG 8/2026. Firma pe sistem -> D300 calculeaza
  exigibilitatea din DECONTARI (incasari cont 4111 / plati cont 401, note validate legate de factura, `i.data` in
  perioada), suta marita, proportional pe plati partiale; taxare inversa exclusa (art.282(6)); fara cap 90 zile
  (OUG 8/2026 l-a eliminat - verificat la sursa). Proba DB reala + DUK. **Datorie inchisa** (xfail
  test_datorie_d300_exigibilitate_tva_la_incasare eliminat, SOLD 23->22).
- Cod: `core/d300.py` (`_pull_incasare`, `_aloca_pe_cote`, branch cash-basis in `calcul_d300`); teste in
  `core/test_d300.py` (fixture `conn_tvai`). Motorul pur = `core/tva_incasare.py` (exista de dinainte).

## Clusterul URMATOR (mecanic)
`venv/bin/python3 -c "from core import agenda; print(agenda.urmator_cluster())"` -> **`('taxare inversa','d300')`,
52 ramase, 0 blocate.**

**Scop (deja mapat):** D300 trateaza taxarea inversa (art.331 CF - cereale/deseuri/etc., beneficiarul e obligat la
plata TVA) **MANUAL prin dict-ul `manual`** (rd.12 + sub-randuri 12.1/12.2/12.3 pe cote 21/11/9), NU derivat din
facturi - decizie de design consemnata in docstring-ul `core/d300.py` (liniile 21-22). R12 intra corect in rollup-ul
R17 (colectata). Structura sursa (anaf_surse/d300_struct_anaf.txt, Rd.12): `R12_1 >= R12_1_1+R12_2_1+R12_3_1` si
`R12_2 >= ...` (ERR daca nu). Sub-rand 12.1 = cota 21% (marja 20-22%), 12.2 = 11%, 12.3 = 9%.
- **Verificare (Sesiunea A):** confirma la SURSA PRIMARA (CF art.331 + struct Rd.12) ca reverse-charge domestic e
  auto-taxare beneficiar declarata in rd.12 (manual), cu deducerea simultana pe latura deductibila. Adauga proba:
  un decont cu manual R12 (+sub-randuri) trece DUK + R12 intra in R17. Latura DEDUCTIBILA a reverse-charge (rd.27.x)
  se declara si ea - verifica ca mecanismul manual acopera ambele laturi (auto-taxare = colectata SI deductibila,
  net zero pt deducere integrala).
- **Legatura cu o datorie GRI deschisa:** `test_datorie_d300_reverse_charge_manual_reconfirmat_mo` (xfail, GRI) -
  verdictul "reverse charge = doar manual" sta pe DEDUCTIE din cod + practica, NU pe text MO. Daca reconfirmi la
  sursa primara (art.331 + structura oficiala D300) ca reverse-charge se declara manual in rd.12 si ca D394 tip C
  la cota bunului e cerinta (nu optiune), poti INCHIDE acest GRI (marker in DECIZII.md:
  "d300 reverse charge doar manual reconfirmat la sursa oficiala"). Vezi si limita documentata din
  `test_d300_d394_paritate.py:119` (taxare inversa primita fara linii diverge - cerinta ANAF, nu bug).

## Datorii/blocaje deschise (22 xfail; relevante pt D300)
1. **reverse charge manual reconfirmat MO** (`test_datorie_d300_reverse_charge_manual_reconfirmat_mo`, GRI) - vezi mai sus.
2. **9% deductibil auto** (`test_datorie_d300_9pct_deductibil_auto`) - validatorul DUK instalat respinge R75 (v12);
   9% deductibil ramane manual + avertisment.
3. **MF metode degresiva/accelerata** (`test_datorie_mf_metode_amortizare`) - subsistem mijloace fixe, nu d101.
4. Restul: `git grep "@pytest.mark.xfail" core/test_datorie.py`.

## Registre atinse (rulare)
- `core/d300.py` (feature TVA la incasare), `core/test_d300.py`. DECIZII/GARZI/TESTE: intrare + √ + contor
  1300->1306 + secventa 53->52. `core/tva_incasare.py` NEatins (motor reutilizat).

## Cum continui (sesiune noua)
1. Citeste CLAUDE.md §2.2 + §2.3. Ruleaza `agenda.urmator_cluster()` -> `taxare inversa | d300`.
2. Verifica art.331 CF la sursa (/tmp/cf.txt sau anaf_surse/cod_fiscal_227_2015_consolidat.html; daca /tmp/cf.txt
   lipseste, regenereaza-l: strip HTML din anaf_surse/cod_fiscal...). Struct Rd.12 in anaf_surse/d300_struct_anaf.txt.
3. Increment testat (rosu->verde), commit local, gard + registru la inchidere. Proba DUK pe manual R12.
4. Limita: max 6 clustere/rulare (ai facut 1 in lant #2; contorul se reseteaza la sesiune noua).
5. Sterge PREDARE_LANT.md dupa ce ai reluat lantul.
