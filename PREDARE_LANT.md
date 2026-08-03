# PREDARE LANT — limita de 6 clustere/rulare atinsa (03.08.2026, lant #2 continuare)

Predare pentru o sesiune NOUA cu context GOL (§2.3 pct.6). Oprire = limita de 6 clustere/rulare (§2.3 pct.5).

## HEAD si stare
- **HEAD:** `c4922e1` · tree curat · **ahead 41 fata de origin/main, NEPUSHAT**.
- **Poarta (toate VERZI):** `venv/bin/pytest` = 1296 passed / 2 skipped / **21 xfailed**; `verificator` TOTAL 0.
- **Push:** decizia EXCLUSIVA a lui Costin. NU impinge.
- **Unde:** `ssh iconta`, `~/iconta_nou`. pytest/verificator/DUK = `venv/bin/...`. Editari pe server prin scripturi
  python scp-uite (Edit local NU atinge serverul). Full-suite ~100s (timeout 200000+).

## Sold lant (ACEASTA rulare - 6 clustere)
`SOLD: 6 clustere INCHISE / 1 datorie INCHISA (GRI reverse charge) / 0 xfail noi / start af675e3 -> c4922e1`
1. **taxare inversa | d300** (2c7c2ed) — REPARAT: `R12_` lipsea din allow-list-ul manual -> rd.12 (auto-taxare
   art.331) era silentios aruncata. Adaugat. GRI reverse-charge D300/D394 INCHIS (reconfirmat la sursa art.331 +
   structuri). Proba DUK. SOLD datorii 22->21.
2. **pro-rata deducere | d300** (8bf066a) — VERIFICAT corect (art.300: R31_2 ajustare Rd.33, net R28xpro_rata) +
   gap de acoperire inchis (test pro_rata<100 + DUK).
3. **rotunjire aritmetica | d300** (647c396) — verificat aritmetic (ROUND_HALF_UP, deja in gardul de identitate) +
   proba d300-specifica.
4. **ajustari | d300** (d26d289) — REPARAT: `R29_/R30_/R35_/R36_` lipseau din allow-list -> ajustari/regularizari
   (restituiri straini, regularizari taxa dedusa, sold reportat, diferente inspectie) silentios aruncate. Adaugate
   (R29/R30 -> R32, R35/R36 -> R37). Proba DUK.
5. **tipuri operatiune 1-5 | d301** (fc36c84) — VERIFICAT maparea tip->sectiune (OPANAF 592/2016: 1=S1 bunuri, 2=S2
   mijloace transport, 3=S3 accize, 4=S4 servicii, 5=S4.1) + gard tipuri 1/2/3 + proba DUK toate 5.
6. **rollup S4.1->S4 | d301** (c4922e1) — VERIFICAT complet (S4.1 subset din S4, TVA nedublat, checksum, proba DUK;
   test_d301_rollup.py dedicat).

**Pattern recurent gasit in D300** (util pt clusterele viitoare): allow-list-uri manual incomplete -> randuri
DECLARATE de contabil silentios aruncate. Gasite si reparate: R12 (taxare inversa), R29/R30/R35/R36 (ajustari).
Cand verifici un rand manual D300, testeaza intai daca `calcul_d300(prof, per, [], {"RXX_2": val})` chiar il seteaza.

## Clusterul URMATOR (mecanic)
`venv/bin/python3 -c "from core import agenda; print(agenda.urmator_cluster())"` -> **`('baza = val x curs','d301')`,
46 ramase, 0 blocate.**
- Scop: in D301 baza impozabila = valoare_valuta x curs (achizitii intracom in valuta). Vezi `calc_baza` +
  `Operatiune` in core/d301.py. Verifica: cursul folosit (BNR la data faptului generator / data facturii?),
  rotunjirea bazei (_r0), moneda (EUR default). Temei: CF art.290 (cursul de schimb pt baza in valuta) + OPANAF
  592/2016. Proba pe date reale + DUK (fixtura/PROF in test_d301_rollup.py).

## Datorii/blocaje deschise (21 xfail; relevante D300/D301)
1. **9% deductibil auto | d300** (`test_datorie_d300_9pct_deductibil_auto`) - validatorul DUK instalat respinge R75.
2. **MF metode degresiva/accelerata** (`test_datorie_mf_metode_amortizare`) - subsistem mijloace fixe.
3. Restul: `git grep "@pytest.mark.xfail" core/test_datorie.py`.
(GRI reverse charge D300/D394 a fost INCHIS in aceasta rulare.)

## Registre atinse (rulare)
- `core/d300.py` (R12 + R29/R30/R35/R36 in allow-list; fara alte schimbari de calcul), `core/test_d300.py`,
  `core/test_d301_rollup.py`, `core/test_datorie.py`. DECIZII/GARZI/TESTE: 6 intrari + √; contor 1294->1319;
  secventa 52->46.

## Cum continui (sesiune noua)
1. Citeste CLAUDE.md §2.2 + §2.3. Ruleaza `agenda.urmator_cluster()` -> `baza = val x curs | d301`.
2. Verifica temeiul la sursa (CF art.290 curs valutar + OPANAF 592/2016; /tmp/cf.txt sau anaf_surse/).
3. Increment testat, commit local, gard + registru la inchidere. Proba DUK.
4. Limita: max 6 clustere/rulare (contorul se reseteaza la sesiune noua).
5. Sterge PREDARE_LANT.md dupa ce ai reluat lantul.
