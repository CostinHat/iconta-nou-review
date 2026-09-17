# Raport de audit independent — iConta.eu

Data: 17.09.2026 · Commit auditat: `d8034c54` (main, verificat `git ls-remote` = același hash) · Arhiva: SHA-256 verificat, `MANIFEST.sha256` integral OK, `zip == pachet/`.

Auditor: Claude (sesiune Cowork), fără acces la serverul iConta, fără DUKIntegrator, fără baza de test a echipei. Mediul exact e în `audit_artefacte/mediu_audit.txt`.

**Convenție de certitudine** (a solicitării): **certă** = am rulat și am văzut; **probabilă** = am citit codul, n-am rulat; **ipoteză** = deducție.

**Răspunsul la întrebarea de fond: DA.** Aplicația produce cifre valide-ca-formă și greșite-ca-sumă pe cel puțin patru drumuri distincte (A1–A4), fiecare trecând validatorul, a doua cale de reconciliere și controlul încrucișat — fiindcă toate citesc aceeași sursă cu aceeași greșeală.

---

## 0. Prima constatare: cifrele pachetului nu se reproduc de la zero

**ce e** · „Cum rulezi poarta de la zero" nu produce o bază pe care suita să dea `6247 passed`. Pachetul nu conține nici baza de test, nici procedura de a o construi; `bootstrap_public.sql` + cele 56 de `core/migrare_*.py` + 11 fișiere `*_ddl.sql` din rădăcină + `migrare_tokene_hash.py` nu sunt orchestrate nicăieri, iar 84 din 536 fișiere de probă cer `tenant_001…020` cu conținut pe care nimic din depozit nu-l generează.

**cum se reproduce** · exact pașii din `01_COMMIT/CUM_RULEZI_POARTA.md` §2–§4 pe o mașină curată, cu o bază goală + `infra/bootstrap_public.sql`. Rezultat măsurat (log în `audit_artefacte/pytest.log`):

```
ruff: All checks passed
pytest: 5748 passed, 189 failed, 178 errors, 158 skipped, 9 xfailed — 1713 s (0:28:33)
verificator_conformitate.py: FileNotFoundError '/root/iconta_nou/static/js/ecrane'
```

Cauzele celor 367 de căderi, numărate din tracebacks: 152 × `PoolError: connection pool exhausted` (v. C3), 38 × `public.firma_sursa_versiune does not exist`, 25 × `public.spv_token`, 22 × `FileNotFoundError '/home/costin/iconta_nou/core'`, 8 × `'/root/iconta_nou/static/js/ecrane'`, 8 × `assert 'gri' == 'valid'` (probele care cer DUK **pică**, nu se sar — contrar afirmației din §1 al ghidului), 4 × `OS TZ nu e Europe/Bucharest` (ghidul nu spune că `TZ` e obligatoriu), restul tabele/coloane din migrări nerulate.

**alte defecte ale pachetului, toate certe:**
- `verificator_conformitate.py:29` și `scripts/scan_mutatie_garzi.py:27` au calea `~/iconta_nou` / `/home/costin/iconta_nou` scrisă în cod; 26 de apariții `home/costin` în `core/test_*.py` + `scripts/`. Poarta completă nu poate fi verde decât pe mașina lui Costin.
- `venv/` e versionat în depozitul public (4.688 fișiere, 146 MB, `pyvenv.cfg` → `/home/costin/iconta_nou/venv`). Nu e în `.gitignore`.
- `03_PROBAT/INVENTAR.txt` și `04_NEVERIFICAT/NEVERIFICAT.txt` conțin o linie de log (`INFO iconta [R118] /static servit din …`) topită în mijlocul textului: importul modulelor `core` scrie în stdout la import.
- `05_FISCAL/INVENTAR_A.md` are 12 chei; `core/common.py COTE` are 20 (`tva_redusa*`, `impozit_dividend`, `plafon_tva_incasare`, `plafon_intrastat`, `impozit_micro`, `impozit_profit` lipsesc). Date divergente: `tichet_masa_plafon` intrare `2026-01-01` (inventar) vs `2025-11-01` (cod); `plafon_mijloc_fix` `2026-01-01` vs `2026-02-25`. Un auditor care citește pachetul vede altă stare decât codul.
- Solicitarea spune „88 de rute care scriu fără probă"; pachetul spune 77 (în suită) + 3 (nicăieri). Nu există numitor (câte rute scriu în total) nici în solicitare, nici în `INVENTAR.txt`.
- Tichetul de masă 45 lei: Legea 201/2025 art. II(2) îl acoperă explicit până la 30.09.2026; în `COTE` valoarea n-are `data_out`. Peste 13 zile aplicația va aplica 45 fără temei confirmat, fără avertisment.

**certitudine** · certă.

---

## A. Cifre valide-dar-false în declarații (ordonate după gravitate)

### A1. Facturile în valută intră în D300 / D394 / D390 / D406 cu sumele în valută, nu în lei — și nota contabilă la fel, deci a doua cale și controlul încrucișat sunt verzi

**ce e** · `facturi.total_lei / tva_lei / curs_bnr` există și se scriu la emitere (`facturi_api.py:734-739`), dar niciun generator nu le citește: D300 (`repo_d300.py:79-101`, `d300.py:131-144` — `cantitate × pret_unitar`), D394 (`repo_d394.py:22-38`), D390 (`repo_d390.py:22-27`), D406 (`repo_d406.py:54-68`). Contarea automată (`contare_facturi.py:350-375`) scrie 4427 tot din linii, în valută. `creeaza_factura` (ruta `POST /facturi`, cea a facturilor primite) nici măcar nu calculează `total_lei`. Singurul loc unde cursul se aplică e D301 (`d301.py:76-90`).

**cum se reproduce** (rulat pe instanța vie, tenant nou, profil plătitor TVA lunar):
```
POST /tenants/1/facturi/emite
{"linii":[{"descriere":"Servicii","cantitate":1,"pret_unitar":1000,"cota_tva":21}],
 "tert_nume":"CLIENT RO SRL","tert_cui":"RO1234573","data_emitere":"2026-08-10",
 "moneda":"EUR","curs_manual":5.0,"data_curs_manual":"2026-08-10","tert_tara":"RO"}
→ răspuns: total=1210, tva=210, total_lei=6050, tva_lei=1050,
  contare: 4111=707 1000.00 ; 4111=4427 210.00        ← în EUR, nu 5000/1050
POST /declaratii/d300 {"tenant_id":1,"an":2026,"luna":8}
→ R9_1=1000  R9_2=210  R17_1=1000  R17_2=210  R41_2=210   „Rezultat TVA de plată 210 lei"  avertismente: []
d300_reconciliere.reconciliaza(...) → {"acoperit": True, "divergente": []}
POST /declaratii/d394 (aceeași lună) → op1 baza="1000" tva="210"
```
Artefacte: `audit_artefacte/d300_eur.json`, `d394.json`.

**ce cifră se schimbă** · D300 rd.9 (R9_1/R9_2), rd.17, rd.34/37/41: subdeclarate cu factorul cursului (aici 5×: 1.000/210 în loc de 5.000/1.050 lei). D394 `bazaL/tvaL`, D390 `baza` (cazul tipic IC e chiar în EUR), D406 `SourceDocuments`, rulajul 4427/4426 din carte — toate la fel, deci nicio verificare internă nu se aprinde. DUK trece (raportul TVA/bază e corect).

**certitudine** · certă.

### A2. TVA la încasare: achizițiile și livrările intracomunitare, exportul și storno-ul dispar din D300

**ce e** · Pe calea `tva_la_incasare`, `_pull_incasare` (`d300.py:905-926`, `repo_d300.py:18-31`) întoarce doar `{directie, decontari}` — fără `tert_tara`, `cui`, `axa_ic`, `taxare_inversa`. Orice operațiune cu cotă 0 plătită/încasată cade pe `f_zero_b` / `zero_livr` și blocul de rutare 0% e sărit → nici rd.1, nici rd.5/rd.18, nici rd.14, niciun avertisment. Separat, `if gross <= 0: continue` (`:922`) — o decontare negativă (storno rambursat) nu reduce nimic. Art. 282 alin.(3)/(6) și 297 alin.(2)–(3) nu amână exigibilitatea IC; a doua cale se declară singură „neacoperit" pe tvai (`d300_reconciliere.py:164-170`).

**cum se reproduce** (calcul pur, rulat):
```python
from core import d300; from collections import namedtuple
P=namedtuple("P","an luna")
d300.calcul_d300({"tva_la_incasare":True}, P(2026,8),
                 [{"directie":"primita","decontari":[{"suma":5000,"cota":0}]}])
→ R={}  avertismente=[]  „Rezultat TVA 0 lei."
```
Pe date: profil `tva_la_incasare=true`, factură primită DE 5.000 (linii 0%), notă validată `401 = 5121` în lună → D300 fără rd.5/rd.18, în timp ce D390 declară achiziția.

**ce cifră se schimbă** · rd.5/rd.18 (R5_1/R5_2/R18_1/R18_2) = 0 în loc de bază / 21% (net zero pe plată, dar D390↔D300 rd.5 neconcordante); rd.1 = 0 pentru livrări IC încasate; rd.14 = 0 pentru export; R9_2 supradeclarat cu TVA-ul storno-urilor rambursate.

**certitudine** · certă pentru IC/export (rulat pe funcția pură + citit `_pull_incasare`); probabilă pentru storno (depinde de cum se contează rambursarea).

### A3. D394, D390 și D406 nu filtrează statusul facturii; D390/D406 nici tipul — iar o factură „anulată" primește notă contabilă

**ce e** · D300 exclude `ciorna/descarcata/anulata/stornata` și `tip≠factura` (`nomenclator_status_factura.clauza_sql`). D394 filtrează doar tipul (`repo_d394.py:22-38`, la fel `d394_reconciliere.py:116-131`); D390 (`repo_d390.py:22-27`) și D406 (`repo_d406.py:54-68`) nu filtrează nimic. `FacturaIn.status` (`main.py:1038`) e text liber și trece nevalidat prin `factura_creeaza` → `creeaza_factura`; `_conteaza_la_creare` (`facturi_api.py:295`) contează indiferent de status.

**cum se reproduce** (rulat):
```
POST /tenants/1/facturi
{"numar":"X-9","data_emitere":"2026-08-12","directie":"emisa","status":"anulata",
 "linii":[{"descriere":"Marfa","cantitate":1,"pret_unitar":2000,"cota_tva":21}],
 "tert_nume":"BETA SRL","tert_cui":"RO1234581"}
→ 200, contare: 4111=707 2000.00 ; 4111=4427 420.00     ← notă pentru o factură anulată
D300 08/2026 → R9_1=1000 (neschimbat, corect)
D394 08/2026 → rezumat2 bazaL="3000" tvaL="630"; op1 BETA SRL baza="2000" tva="420"
```
**ce cifră se schimbă** · D394 `bazaL/tvaL` și `op1` +2.000/+420 față de D300 rd.9; D390 `baza` cu proforme/avize (o proformă IC + factura rezultată = dublă numărare); D406 cu ciorne/anulate; 4427 din carte +420. `_orizontal_d300_vs_d394` compară doar rd.12 vs tip C (`control_incrucisat.py:2016-2098`), deci nu vede L↔rd.9.

**certitudine** · certă (D394, contare, acceptarea statusului); certă pe cod pentru D390/D406 (nu am rulat D406).

### A4. `storneaza` nu copiază `tert_tara`, `taxare_inversa`, `categorie_331`, `axa_ic`, `tip_operatiune`, `tert_platitor_tva`, `data_faptului_generator` — storno-ul unei livrări IC nu scade rd.1

**ce e** · `facturi_api.py:785-788` cheamă `creeaza_factura` doar cu `client_id/tert_nume/tert_cui/tert_adresa/moneda/status`; restul cad pe implicite (`tert_tara="RO"`, `taxare_inversa=False`). Storno-ul devine o „livrare RO cu cotă 0" neclasificabilă.

**cum se reproduce** (rulat):
```
POST /tenants/1/facturi/emite {"linii":[{"cantitate":1,"pret_unitar":5000,"cota_tva":0}],
  "tert_nume":"KUNDE GMBH","tert_cui":"DE811569869","data_emitere":"2026-09-01","tert_tara":"DE"}
POST /tenants/1/facturi/3/storno {}
→ facturi: id 3 tert_tara=DE total=5000 ; id 4 tert_tara=RO total=-5000 storno_din_id=3
D300 09/2026 → R1_1=5000, R17_1=5000  (ar trebui 0)
   avertisment: „Livrare cu cotă 0% (bază -5.000 lei) — nu se clasifică automat … R14/R15"  ← îndrumare greșită
D390 09/2026 → <operatie tip="L" tara="DE" baza="0"/>        (cheie pe CUI, copiat → corect 0)
```
La fel pentru factura V (taxare inversă, deșeuri) + storno: în D394 rulat `('V',…):[1,1000,0]` rămâne, storno-ul apare ca `('LS',…):[1,-1000,0]`.

**ce cifră se schimbă** · D300 rd.1 (R1_1) și rd.13 (R13_1) rămân neduse cu baza stornată → D300 ≠ D390 (ANAF vede neconcordanța, dar D300 e cea greșită); D394: LS negativ + V nemodificat.

**certitudine** · certă.

### A5. Partener non-UE: serviciile emise ajung la rd.14 în loc de rd.3; serviciile primite la rd.26 în loc de rd.7 + rd.20

**ce e** · Rutarea `strain and not ue` (`d300.py:319-320, 332-333`) ignoră `axa_ic`: orice emisă non-UE → `export_livr` (rd.14 „scutite cu drept"), orice primită non-UE la 0% → `f_zero_b` (rd.26). Structura ANAF (`anaf_surse/d300_struct_anaf.txt:365-371, 444-450`): rd.3 = prestări cu locul în afara RO (UE sau non-UE); rd.7 = achiziții de servicii pentru care beneficiarul RO e obligat la plată (autolichidare, cu rd.20 la deducere). Importurile de bunuri non-UE (rd.21, TVA în vamă) nu sunt modelate.

**cum se reproduce** (rulat): `calcul_d300({}, per, [{"directie":"emisa","tert_tara":"US","axa_ic":"servicii","linii":[(1,1000,0)]}])` → `{'R14_1': 1000}` cu nota „export"; primită US servicii → `{'R26_1': 1000}` + avertisment generic despre IC.

**ce cifră se schimbă** · R14_1 +bază / R3_1 −bază; R26_1 +bază în loc de R7_1/R7_2/R20_1/R20_2 (21% autolichidat — net zero la deducere integrală, diferență de TVA de plată la pro-rata < 100%).

**certitudine** · certă.

### A6. D205: cota de impozit pe dividende după anul declarației, nu după data distribuirii

**ce e** · `d205.py:363`: `_cota205("impozit_dividend", 31.12.an)` pentru tot ce s-a plătit în an. Registrul (`common.py:609`) spune „se aplică după data DISTRIBUIRII"; Legea 141/2025 art. VII(1) lit. c) (în corpus: `legea_141_2025_consolidat.html:484`, `cod_fiscal_227_2015_consolidat.txt:5075`): 16% „veniturilor din dividende distribuite începând cu 1 ianuarie 2026"; alin. (2): interimare 2025 → 10% fără recalculare.

**cum se reproduce** · credit 457 (distribuire) în dec. 2025, debit 457 (plată) în ian. 2026 → D205/2026 aplică 16% (corect 10%). Reconcilierea D205 recalculează cu aceeași cotă → verde.

**ce cifră se schimbă** · `imp` +6% × dividendul plătit (cel mai frecvent caz din practică: dividende 2025 aprobate/plătite la început de 2026).

**certitudine** · certă (cod + textul legii din corpus); n-am rulat pe date.

### A7. Deducerea personală: tranșele de 50 lei sunt decalate cu o treaptă

**ce e** · `salarizare.py:66-68`: `floor((b−sm)/50)`. Art. 77 alin.(4) (corpus `cod_fiscal_227_2015_consolidat.txt:8395-8404`): „sm+1 … sm+50 → 19,50 %", deci treapta corectă e `ceil`.

**cum se reproduce** (rulat, sm 08/2026 = 4.325):
```
brut 4326 (sm+1)   → 865,00 (20,00%)   corect 843,38 (19,50%)
brut 4375 (sm+50)  → 843,38 (19,50%)   corect
brut 4376 (sm+51)  → 843,38 (19,50%)   corect 821,75 (19,00%)
brut 4426 (sm+101) → 821,75 (19,00%)   corect 800,13 (18,50%)
```
Greșit pe 49 din fiecare 50 de valori de brut între sm și sm+2.000.

**ce cifră se schimbă** · D112 impozit (cod 602, E3_14/E3_15) subdeclarat cu 10% × 0,5% × sm ≈ 2,16 lei/salariat/lună. Mic, dar sistematic, valid la DUK și invizibil contabilului.

**certitudine** · certă.

### A8. D100: baza micro = doar creditul 70x; impozitul pe profit pe trimestru izolat, nu cumulat

**ce e** · `repo_d100.py:22-27`: venituri = `cont_credit LIKE '70%'`, cheltuieli = `cont_debit LIKE '6%'`. Art. 53(1) CF: venituri din orice sursă (75x/76x intră), 709 se scade. Profit: art. 41 — calcul cumulat de la începutul anului, plata trimestrială = diferență; codul (`d100.py:335-345`) ia `venituri − cheltuieli` ale trimestrului curent, iar 691 (nedeductibil) e în 6xx. A doua cale (`_thunk_d100`) folosește aceeași `deriva_obligatii` („SURSA UNICA") → verde.

**cum se reproduce** · micro: 766 credit 10.000 și 709 debit 2.000 în trimestru → baza omite 10.000 și include 2.000. Profit: T1 −50.000, T2 +80.000 → cod 103 = 12.800 (corect 16% × 30.000 = 4.800).

**ce cifră se schimbă** · cod 121 ± 1% × (75x/76x impozabile − 709); cod 103 supradeclarat după trimestre cu pierdere și subdeclarat cu 16% × 691.

**certitudine** · certă pe cod și lege; efectul pe date — probabilă.

### A9. D394 la firma cu TVA la încasare: `tvaCol*/tvaDed*/tvaDedAI*` sunt 0, tipul AI nu e emis

**ce e** · `d394.py:720-726` hardcodează câmpurile din `<informatii>` cerute la `sistemTVA=1` (`d394_struct_anaf.txt:1838-1968`); `tip_operatiune` (`:359-369`) nu cunoaște `furnizor_tva_incasare` (nici `repo_d394.select_facturi` nu-l aduce) → achizițiile de la furnizori la încasare ies „A", nu „AI".

**ce cifră se schimbă** · `tvaCol21/tvaDed21` = 0 în loc de sumele pe care D300 le calculează pe decontări; `facturiAI/bazaAI/tvaAI` = 0, `bazaA` umflat. ANAF corelează `informatii` cu D300.

**certitudine** · probabilă (citit; nu am rulat cu profil tvai pe D394).

### A10. Import e-Factura: baza liniei = `InvoicedQuantity × PriceAmount`; `BaseQuantity`, `AllowanceCharge`, `LineExtensionAmount` sunt ignorate; moneda XML intră fără curs

**ce e** · `efactura_import.py:60-66` citește doar `InvoicedQuantity`, `PriceAmount`, `Percent`. Nu există niciun `AllowanceCharge` / `BaseQuantity` / `LineExtensionAmount` în modul (grep = 0). `total/tva` din antet se salvează, dar declarațiile citesc liniile. Controlul „TVA orfan" (`d300.py:351-356`) semnalează doar `antet > linii`, nu invers. Categoria AE (taxare inversă) devine 0% simplu.

**cum se reproduce** · UBL cu linie `10 × 100`, `AllowanceCharge` −200 (`LineExtensionAmount=800`, `TaxAmount=168`) → `factura_linii` 10 × 100 @21 → bază 1.000/TVA 210 în D300/D394; carburant cu `Price/BaseQuantity=1000` → bază × 1.000.

**ce cifră se schimbă** · R22_1/R22_2 (primită) sau R9_1/R9_2 (emisă) supradeclarate cu reducerea/factorul; AE → R26 în loc de rd.12/rd.25.

**certitudine** · certă pe cod; frecvența în date — necunoscută (n-am rulat un UBL).

### A11. Exigibilitatea D300 diferă de D390 pe aceeași factură IC

**ce e** · D300: `COALESCE(data_faptului_generator, data_emitere)` (`d300.py:52`); D390: `LEAST(data_emitere, ziua 15 a lunii următoare faptului)` (`d390.py:524-526`, art. 284(2)). O livrare IC cu fapt generator 20.06 și factură 05.07 → D300 rd.1 în iunie, D390 în iulie. Și art. 282(2) lit. a) (factură emisă înainte de faptul generator → exigibilă la emitere) nu e modelat.

**certitudine** · probabilă (citit ambele expresii; nu am rulat perechea).

### A12. Pro-rata aplicată pe întreg rd.28 ca ajustare negativă

**ce e** · `d300.py:549-553`: `R31_2 = −R28_2 × (100−pr)/100` pe toate achizițiile, deși art. 300(3)–(5) aplică pro-rata doar achizițiilor mixte. Reconcilierea declară rd.33→42 „neacoperit".

**certitudine** · ipoteză (depinde de cum e folosit `pro_rata` de contabil).

---

## B. Izolare între firme și control intern

### B1. Un cabinet aprobă, respinge și marchează „depusă" declarația altui cabinet

**ce e** · `/coada/{id}/aproba|respinge|depune` (`main.py:2867-2893` → `uc_coada.py:155-283` → `coada_api.py:359-535`) nu compară `declaratii_coada.cabinet_id` cu `ctx["firm"]`; singura rută scoped e `GET /coada/{id}/continut` (`repo_declaratii.py:15-19`). `_are_permisiune` verifică flagul propriu al userului, nu apartenența elementului. Gardul `test_izolare_structurala.py:151-160` enumeră doar rutele cu `{tenant_id}` — familia `/coada/{coada_id}` e în afara lui.

**cum se reproduce** (rulat, două cabinete, element în coada lui B cu `cabinet_id=5`):
```
GET  /coada/1/continut   (token cabinet A) → 404 „Element de coadă negăsit (sau alt cabinet)."
POST /coada/1/aproba     (token cabinet A) {"motiv_trecere":"audit"} → {"ok":true,"stare":"aprobata"}
POST /coada/1/depune     (token cabinet A) {"motiv_trecere":"audit"} → {"ok":true,"stare":"depusa","an":2026,"luna":8}
public.declaratii_coada: cabinet_id=5 stare=depusa depus_de_id=4 (userul lui A)
public.declaratii_depuse: tenant_id=2 (firma lui B) an=2026 luna=8 tip=d300 nr_depunere=1
```
**ce cifră se schimbă** · nu o cifră de declarație; istoricul „depuse" al firmei B, controlul D-vs-D (`compara_ce_s_a_depus`) și poarta „D112 depusă → nu șterge salariat" (`salariati_api.py:334-341`) ale lui B se schimbă fără ca B să fi depus nimic; `respinge` scrie `motiv_respingere` și notifică pregătitorul lui B.

**certitudine** · certă.

### B2. Orice angajat își acordă singur `poate_valida` / `poate_depune`

**ce e** · `POST /eu/competente` (`main.py:4493-4498` → `uc_eu.py:94-98` → `asistenti_api.py:332-342`, „fără restricții") e sub `cere_cabinet`, deci și `angajat`, și scrie cele trei flaguri pe propriul rând, ocolind `/asistenti/{uid}/permisiuni` (rezervat admin_firma).

**cum se reproduce** (rulat): angajat creat cu `poate_valida=false` → `POST /eu/competente {"poate_pregati":true,"poate_valida":true,"poate_depune":true}` → `{"ok":true,…}`; `users`: `t t t`. Apoi aprobă orice element din coada cabinetului (patru-ochi îl oprește doar pe al lui).

**certitudine** · certă.

### B3. Un client de portal dezactivează orice cont fără rânduri în `user_tenants`

**ce e** · `DELETE /portal/acces-cont/acces/{user_id}` (`uc_portal.py:76-91`): șterge legătura (scoped), apoi, dacă `count(user_tenants)==0`, `UPDATE users SET activ=false` NEscoped (`repo_utilizatori.py:211-213`). Cabinetul are ramura corectă (`:177-180`); portalul nu.

**cum se reproduce** (rulat): client titular al firmei 1 (cabinet A) → `DELETE /portal/acces-cont/acces/7?tenant_id=1` cu 7 = angajatul cabinetului (fără rânduri în `user_tenants`) → `{"ok":true}`; `users.activ=false`; login angajat → „email sau parolă greșite". Userul 5 (admin cabinet B) a supraviețuit doar fiindcă avea un rând în `user_tenants`. Victime: angajați fără firme atribuite, admini ale căror firme au fost scoase, superadmin.

**certitudine** · certă.

### B4. `POST /coada` nu verifică `poate_pregati`

**unde** · `uc_coada.py:26-110` — niciun `_are_permisiune(ctx,"poate_pregati")`; flagul apare doar la setare. **certitudine** · certă pe cod (nu am rulat: coada cere DUK).

### B5. `SET search_path` e de sesiune, nu `SET LOCAL` — latent sub PgBouncer

**unde** · `db.py:13, 113` afirmă `SET LOCAL`/„PgBouncer-safe"; `db.py:130` execută `SET`. Azi, cu conexiune directă și `RESET` în `finally`, e inofensiv. Dacă se comută `DATABASE_URL` pe PgBouncer în transaction mode (calea „ZERO cod" din docstringul `:7-8`), după `commit` conexiunea server poate migra la alt client cu `search_path` al firmei A. **certitudine** · ipoteză (condiționată de infrastructură).

---

## C. Ce rămâne pe jumătate scris

### C1. Numerotarea facturilor: două cereri concurente → același număr

**ce e** · `numerotare()` citește `urmator_numar_factura` fără `FOR UPDATE` (`facturi_api.py:510-518`), `emite_factura` scrie `numar+1` (`:641-667`); `facturi` n-are unic pe (serie, numar) (`tenant_template.sql:1450-1451`). Apelanți: emitere manuală, `vanzare_ic`, cron `facturi_recurente` (07:00), `woocommerce` (07:30), API public.

**cum se reproduce** (rulat): 12 × `POST /tenants/1/facturi/emite` simultan (`xargs -P 12`) → 5 × 200, 7 × 422; `SELECT numar, count(*) … HAVING count(*)>1` → **numar 6 × 3**. Trei facturi cu același număr, `urmator_numar_factura` = 7.

**ce cifră se schimbă** · D394 `nrFacturi`/plaja de serie; e-Factura: al doilea upload cu număr existent e respins de ANAF; jurnalul de vânzări cu numere dublate (art. 319 CF: numerotare secvențială unică).

**certitudine** · certă.

### C2. Import în masă de firme: răspunsul spune „creat", baza nu conține nimic

**ce e** · `uc_migrare.py:66-99`: bucla `provision_tenant` într-o singură tranzacție; `except Exception` continuă după o eroare psycopg2 (tranzacție abortată), firmele următoare pică cu „current transaction is aborted", iar la ieșirea din `with` `commit()` pe tranzacție abortată = ROLLBACK tăcut. `MigrareFirma.denumire` e nelimitat, `tenants.nume` e `varchar(255)`.

**cum se reproduce** (rulat): `POST /migrare/importa` cu 4 firme, a 3-a cu denumire de 300 de caractere →
```
creat: [{'cui':'2000007','tenant_id':3}, {'cui':'2000015','tenant_id':4}]
erori: ['value too long for type character varying(255)', 'current transaction is aborted…']
public.tenants: doar firma existentă; pg_namespace: fără tenant_003/004
```
**certitudine** · certă. Aceeași clasă: `uc_tenants.py:5496-5507` (`tenant_creeaza`), `uc_auth.py:128` (`register`) — probabilă.

### C3. `get_conn(schema)` pierde definitiv conexiunea din pool când conexiunea moare

**ce e** · `db.py:137-145`: în `finally`, `RESET search_path` pe conexiune moartă ridică → `except: conn.rollback()` ridică din nou din `finally` → `p.putconn(conn)` nu se mai execută; conexiunea rămâne în `_used` pentru totdeauna. Cu `schema=None` calea e sănătoasă.

**cum se reproduce** (rulat, pool real, `pg_terminate_backend` din altă conexiune în timpul blocului):
```
in block, used: 1 → exceptie InterfaceError → after block, used: 1 (conexiune pierdută)
după încă 3 → used: 4 of maxconn 10
```
Cu `ICONTA_POOL_MAX=10` în producție: 10 evenimente (restart PostgreSQL, failover, RST) → `PoolError("connection pool exhausted")` pe toate rutele, până la restart manual; procesul web n-are deadman (R75). Suita mea a produs 152 astfel de erori pe o bază incompletă.

**certitudine** · certă.

### C4. e-Factura / e-Transport: răspuns ANAF pierdut → retrimitere permisă → același XML de două ori în SPV

**unde** · `efactura_trimitere.py:95-100` (insert `pregatit` + commit înainte de upload), `:105-123` (`except Exception` → `eroare_upload`, inclusiv timeout 60 s, `efactura_send.py:350`), `repo_efactura.py:107-111` (`viu` = incarcat/in_prelucrare/ok, deci `pregatit`/`eroare_upload` permit alt upload), indexul unic parțial (`tenant_template.sql:2455-2457`) exclude ambele stări. Identic `etransport_send.py:143-185`. ANAF nu e idempotent (admis în docstring `:71-72`). **certitudine** · probabilă (fără ANAF nu se poate rula).

### C5. Import extras bancar neidempotent

**unde** · `uc_tenants.py:4837-4853` → `reconciliere_api.py:57-101`: insert fără cheie de dedup (`extras_linii` doar PK). Dublu-click / răspuns pierdut după commit → toate liniile de două ori → notele pe 5121 dublate. **certitudine** · probabilă.

### C6. Minore

- `facturi_recurente.py:120` `SET search_path TO {schema}` fără `public`, fără `RESET`; `:126-128` `platitor_tva` cade tăcut pe `True` la eșec. Proces cron separat → fără scurgere, dar o factură recurentă a unei firme neplătitoare poate primi TVA. probabilă.
- `woocommerce.py:65` același tipar `SET search_path` prin f-string.
- `uc_portal.py:439-448` (`portal_bon`): rândul e comis, apoi pozele pe disc → eșec disc = bon fără imagini. probabilă.
- R183 (`apel_anaf` ține tranzacția peste HTTP): **nu se mai confirmă** — `spv_conector.py:479-516` închide conexiunea înainte de apel; o scanare AST n-a găsit niciun apel `requests/duk/email` în interiorul vreunui `with get_conn`. Restanța poate fi închisă ca „reparată".

---

## D. Instrumentele mint (clichetele)

Cele patru cifre din `deriva_cifrele.py` **se reproduc** (`0 / 77 / 3 / 0`, rulat). Dar trei din patru reproduc ceva gol:

### D1. `PLAFON_SUBSET_FISCAL = 0` e fals: atribuirea vede un singur nivel de apel, iar rutele care scriu prin două nivele cad în `fara_tabele`, care nu intră în criteriu

**unde** · `scan_scrieri_declaratii.py:87-111` (`_sql_cu_un_nivel`), `:150-155` (`fara_tabele`, 17 azi, asertat doar `< 40` în `test_rute_probate.py:129`).

**cum se reproduce** (rulat):
```python
from scripts import scan_scrieri_declaratii as D
D.scrise_de_ruta('wc_sinc')            → (set(), 'main.py')
D.scrise_de_ruta('stocuri_descarcare') → (set(), 'core/uc_tenants.py')
```
`wc_sinc` → `woocommerce.sincronizeaza:108` → `facturi_api.emite_factura` → **facturi, factura_linii** (D300/D394/D390/D406). `stocuri_descarcare` → `stocuri_api.descarca_luna:133` → `_noteaza:21-27` → **inregistrari, inregistrari_linii** (D100/D101/D300/D406). Amândouă sunt în lista celor 77 neprobate.

### D2. Tabele citite de generatoare, absente din lista scanerului — D112 e cel mai lovit

`citite_de_generatoare()` (rulat) vede 14 tabele, numai din SQL-ul din `core/dNNN.py` + `repo_dNNN.py`. Lipsesc: **beneficii_lunare** (`d112.py:723-727` → baza CASS/impozit tichete), **pontaj** (`d112.py:819` → tichete de masă), **salariu_istoric** (`d112.py:804` → brut = tot; SQL `FROM %s`, `salariu_istoric.py:29`, orbire declarată), **d300_manual** (`d300.py:1058` → R41/R42), **mijloace_fixe / reevaluari / miscari_stoc** (D406 Assets/Stocks se generează în `uc_tenants.py:5062,5092`, iar `d406_active.py`/`d406_stocuri.py` nu potrivesc `^d\d{3}[a-z]?\.py$`, `:128`). Scriitorii lor neprobați: `salariat_beneficiu_lunar`, `tenant_pontaj_set`, `mijloace_import_salveaza`, `cv_transfer`, `articole_import_salveaza` — toate în cei 77. Subsetul fiscal recalculat cu tabelele astea: **8 rute, nu 0**.

### D3. „Numită" înseamnă subșir oriunde, inclusiv în comentarii

`scan_rute_fara_proba.py:97` `nume in t` — fără graniță de cuvânt, fără excluderea comentariilor. `jurnal_editeaza`/`jurnal_sterge` (scriu `inregistrari`) sunt „probate" de comentariul `test_ancore_rute.py:32-33`; `nota_avans` e subșir al lui `av.nota_avans_platit` (funcție pură); `produse/{id}` e numită de docstringul testului de calibrare al scanerului. 20 de rute care scriu sunt numite în suită **numai** așa.

### D4. Mutație: o rută nouă care dublează `facturi.total`, numită într-un comentariu, trece toate trei clichetele

Pe o copie a arborelui: (a) rută → `woocommerce.sincronizeaza` fără probă → IN_SUITA 78 (pică), NICAIERI 4 (pică), **SUBSET_FISCAL 0 (trece)**; (b) rută cu `UPDATE facturi SET total=total*2`, numele într-un comentariu dintr-un `test_zz_*.py` → **toate trei trec**. certă.

### D5. `PLAFON_NICAIERI = 3` e artefact

`_fisiere_de_proba(doar_suita=False)` (`scan_rute_fara_proba.py:52-66`) ia **toate** `.py` din `core/`, deci modulul care definește ruta o „numește". Cele 3 sunt exact rutele cu corpul încă în `main.py`. Fără modulele de implementare: **54**.

### D6. `PLAFON_NECORELATE = 0` reproduce vid fără DUK

`scan_coduri_validator.confrunta()` (`:136-143`) pune citarea în `fara_validator` când nu există jar; `deriva_cifrele.py:64` raportează `acum=0 OK`. Rulat aici: `citari 246 · fara validator instalat: 246 · NECORELATE 0`. Anti-vacuumul există doar în `test_coduri_validator.py:70`, nu în instrumentul de audit.

### D7. Garda de atribuire păzește alt instrument decât cel din clichet

`test_atribuire_scrieri.py` testează `scan_functionalitati.scrie_unitatea`; clichetul folosește `scan_scrieri_declaratii.scrise_de_ruta` (`test_rute_probate.py:119-120`), care n-are probă pe direcția „tăcere". Cele două diverg exact pe rutele din D1.

### D8. `scan_mutatie_garzi.py` și `scan_instrumente.py` nu măsoară mutații

`scan_mutatie_garzi.py:59-104` numără teste după convenția de nume (`_prinde_/_detecteaza_`), nu execută nimic; `RAD` = `/home/costin/iconta_nou` → aici „0 fișiere din 0", exit 0. `scan_instrumente.py:52-77` nu vede `from scripts import …` → raportează 0 teste pentru exact cele trei scanere ale clichetelor.

### D9. `NEVERIFICAT.txt` §D omite cele trei scanere ale clichetelor

`deriva_neverificatul.py:129-131` caută `"Unde e oarbă"` (case-sensitive); scanerele scriu `UNDE E OARBĂ`. Lista celor 67 nu-i conține.

### D10. Zgomot în regexuri

`DO UPDATE SET` → tabel fals `set` (`scrise_de_ruta('tenant_pontaj_set')` = `{'set','pontaj'}`); `EXTRACT(YEAR FROM data_pif)` → tabel `data_pif`; tiparul de cale (`:81`) nu potrivește `"/tenants/%d/…" % tid`, stilul dominant al probelor.

**certitudine** pentru D1–D10 · certă.

---

## E. Valori fiscale (05_FISCAL)

Verificate și găsite conforme cu sursele din `anaf_surse/`: TVA 21/11 (Legea 141/2025 art. 291), CAS 25 / CASS 10 / impozit 10 / CAM 2,25, dividend 16% din 2026 (dar v. A6), salariu minim 4.050 → 4.325 de la 01.07.2026 (HG 146/2026), facilitate 300 (S1 2026) / 200 (S2 2026) + plafoane 4.300/4.600 (OUG 89/2025 art. III), plafon TVAI 5.000.000 (OUG 8/2026), micro 1% unic, sărbătorile 2026, deducerea tinerilor 15%, CASS pe CM doar 01/07/10.

Constatări:
- **Plafon micro 100.000 EUR** (art. 52(1)): nicio verificare; D100 rămâne pe cod 121 cât timp `regim_fiscal='micro'`. certă (absență).
- **Tichet 45 lei** expiră 30.09.2026 fără `data_out` (v. §0).
- **CAM pe indemnizația CM suportată de angajator** nu se calculează (`d112.py:545, 614-617, 684`); art. 220^5 exceptează doar partea FNUASS. cod 480 subdeclarat cu 2,25% × cm_ang. probabilă.
- `salarizare.cam` (`:285`) include facilitatea de 300/200 pe care D112 o scade → statul de plată/436 ≠ cod 480 cu 6,75/4,5 lei per salariat la minim; declarația e cea corectă, dar `verifica_d112` e roșu permanent pe firmele cu salariați la minim. certă pe cod.
- Nota contabilă a facturii primite folosește `MAX(cota_tva)` pe toată factura (`contare_facturi.py:372-375`): factură mixtă 21/11 → 4426 supraevaluat; D300 corectă, controlul încrucișat roșu — risc de „corectare" a declarației după carte. probabilă.
- JS/HTML: cote hardcodate doar ca sugestii UI (`firme.js:2660` select NIR limitat la [21, 11], fără 0%). Nu produc cifre.

---

## F. Am căutat și n-am găsit

- Rute `/tenants/{tenant_id}/…` fără poartă de apartenență: scaner AST peste `main.py` + `core/uc_*.py` + `core/*_api.py` — toate cele 276 de handlere deleagă în `uc_*`, fiecare cu una din porțile `schema_tenant`/`_schema_sau_404`/`_tenant_client`/… Derivare de schemă din `tenant_id` fără proprietate: doar în provisioning, gardată.
- Interpolare de input utilizator în SQL: toate interpolările sunt `schema` (validată), liste de coloane constante, `%d` pe int, sau whitelist.
- Cache-uri fără cheie de tenant cu date de tenant: `scan_stare_proces` (13 itemi) — doar curs BNR global, sărbători, ajutor. `supervizor_cache`/`firma_rezumat` sunt în DB, cheiate pe tenant.
- Path traversal în fișiere (bonuri, recipise SPV, raportări): nume generate + `int(id)`.
- Cross-cabinet pe `/asistenti/{uid}/*`, `/raportari/{rid}`, `/notificari/{nid}`, `/cabinet/api-chei/{kid}`, API public, OAuth SPV, portal (`_tenant_client`): gardate corect.
- Ștergere tenant: 13 tabele `public` + `DROP SCHEMA` într-o tranzacție, fișierele după commit.
- E-mail înainte de commit: nu (notificări după bloc).
- Joburi cu retry pe scrieri neidempotente: `spv_receive` (`ON CONFLICT`), `spv_poll`, `woocommerce` (`deja_importata`) — curate.
- `conn.commit()` în helperi (7 locuri): fiecare e singura scriere a apelantului.
- Dublă numărare facturi ↔ `inregistrari` în D300 pe calea normală: nu există (D300 citește doar `facturi`).
- Rotunjire: `ROUND_HALF_UP` peste tot pe sume; nu e problemă.
- Maparea cotă → rând D300 pentru cotele interne (21→R9/R22, 11→R10/R23, 9→R11): corectă; `_oglinda_r12_r25` corectă.
- `stornata`/`anulata` pe originale: niciun cod nu le setează → fără dublă scădere prin status.
- Valori expirate la 17.09.2026 în `COTE`: niciuna.
- Formule D112 CAS/CASS/impozit pe salariu și CM (25/10, split angajator/FNUASS): conforme cu sursele din repo.
- Triggere/funcții SQL care scriu în tabele de declarație: doar 2 triggere de refuz (`tenant_template.sql:2153-2191`).
- `execute_values/execute_batch/sql.SQL/copy_*` către tabele de declarație: 0.
- Rute GET care scriu în tabele de declarație: 0 (două false pozitive).
- Rute din cei 77 exercitate în suită prin cale `%d` nevăzută de scaner: 2, nefiscale.

## G. N-am ajuns la

- **DUKIntegrator** — nu e în pachet. Comportamentul validatorului pe rânduri negative (storno > vânzări, R9_1 < 0), și pe orice din A1–A12, e neverificat cu arbitrul. F6/D6 rămân neprobate pe server.
- D406 în profunzime (doar filtrele SQL și valuta), D301 (doar conversia), `d112_reconciliere` / `control_incrucisat.verifica_d112`, `d390_reconciliere` complet, `inchidere_luna`, `audit_preluare`, `gdpr_*`, `uc_admin`, motorul `salarizare`/`stat_plata_emis`.
- `core/uc_tenants.py` (5.573 linii): porțile verificate mecanic, ~15 funcții citite rând cu rând; restul nu.
- Pragul de 10.000 lei pentru persoane fizice în D394 (nicio constantă `10000` în `d394.py`; OPANAF 3769/2015 neconfruntat).
- `/facturi-primite/{id}/valideaza` — dacă poate seta `taxare_inversa`/`tert_tara` pe importurile e-Factura (ar atenua A10).
- Fluxul `d301_operatiuni` → D390 la o firmă cu și facturi IC (posibilă dublă sursă).
- Frontendul (dacă UI-ul retrimite automat la timeout — ar agrava C4/C5); cele 35 de probe de lanț din `frontend_test/` nu le-am rulat (cer instanța echipei).
- A9, A11, C4, C5, C6, E-CAM: citite, nerulate.
- Suita pe o bază completă: fără dump, cifra `6247 passed` nu se poate confirma de aici.

---

## H. Comenzi de reproducere (mediul din `audit_artefacte/mediu_audit.txt`)

```
# pachet
sha256sum iconta_AUDIT_2026-09-17.zip ; (cd pachet && sha256sum -c MANIFEST.sha256)
git clone https://github.com/CostinHat/iconta-nou-review.git && git checkout d8034c54
# poarta (§0)
export ICONTA_MEDIU=test DATABASE_URL=postgresql://iconta_test_user:…/iconta_test TZ=Europe/Bucharest
./venv/bin/python -m ruff check core/ scripts/ main.py ; ./venv/bin/python -m pytest -q ; ./venv/bin/python verificator_conformitate.py
# clichete (D)
./venv/bin/python audit/deriva_cifrele.py ; ./venv/bin/python scripts/scan_coduri_validator.py
./venv/bin/python -c "from scripts import scan_scrieri_declaratii as D; print(D.scrise_de_ruta('wc_sinc'), D.scrise_de_ruta('stocuri_descarcare'), sorted(D.citite_de_generatoare()))"
# lab viu (A1, A3, A4, B1–B3, C1, C2): bootstrap_public.sql + for m in core/migrare_*.py: python -m core.$m ; *_ddl.sql ; migrare_tokene_hash.py
uvicorn main:app --port 8099   # apoi cererile HTTP din fiecare constatare, în ordinea scrisă
# pool (C3), deducere (A7), rutare D300 (A2, A5): scripturile Python inline din constatări
```
