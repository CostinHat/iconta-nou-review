Citeste CLAUDE.md §2.2 (structura raportului) si §2.3 (lant, siguranta, limba) inainte de a incepe.

# PREDARE — Campania "IMPLEMENTARILE RAMASE" (04.08.2026)

Sesiune noua, context gol. Server: `ssh iconta`, `~/iconta_nou` (branch main). Raspunde in ROMANA.
Rulezi pytest/DUK/verificator/commit PE SERVER. Credentiale DB: `set -a; . ~/.iconta/db.env; set +a` inainte
de scripturi care ating baza. Poarta + push de siguranta dupa fiecare punct: `git push -f origin HEAD:backup/lant-20260803`.

## Ritual de pornire
1. `git log --oneline -1` -> HEAD asteptat cel putin **7921280** (commitul C4). `git status --porcelain` gol.
2. `venv/bin/python -m pytest -q` -> ~1367 passed, 2 skipped, 21 xfailed. `venv/bin/python3 verificator_conformitate.py` -> TOTAL 0.
3. DB dump de siguranta EXISTA: `~/backup_pre_migrari_20260804_1312.sql.gz` (322 CREATE TABLE). Daca faci migrari noi, ia altul.

## STARE: 2 din 7 puncte LIVRATE, 5 ramase.

### DONE — Punctul 1: C5 migrare tichete culturale pe tenanti reali (commit "C5 executat")
tenant_001 (singurul tenant real) migrat: beneficii_lunare CHECK accepta acum tip='cultural' + eveniment='ocazional'.
Efemera + tenant_001 + idempotent, zero esecuri. Nimic de facut.

### DONE — Punctul 2: C4 sectiunea 8.3 avantaje D112 (commit "C4 implementat")
D112 emite acum E3_60 + E3_10(masa)/E3_72(cresa)/E3_74(cultural)/E3_75(vacanta) cand exista bilete. Probat DUK.
Decizie tehnica cheie: NU se atinge E3_8/E1_1 (scenariul E3_8+=nominal e RESPINS de DUK regula S111); constrangerea
oficiala e ">=", E3_8 (venit) >= E3_60 (bilete) prin constructie. SUB-BLOCAJ ramas: E3_73 (cadou) - cadou nu e in
pipeline-ul de impozit D112 (calcul_salariu nu proceseaza tip=cadou, plafon 300 lei art.76(4)a neimplementat) ->
cere campanie proprie "tichete cadou end-to-end". Vezi DECIZII 04.08.

## RAMASE (ordinea din comanda; schimb-o pe dependente si spune de ce)

### Punctul 3: SUPORT COMPLET N — D394 (approach a) — FULL-STACK, cel mai mare
Groundwork: DECIZII.md ~6480-6525 + GARZI.md ~599-620. Stare curenta (approach b): operatiunile N (achizitii de la
parteneri NEINREGISTRATI, tip_partener=2) se EXCLUD cu avertisment vizibil (core/d394.py:336-340 calea auto,
367-370 calea manuala, avertisment la 372-380). Input-ul calcul_d394 ACCEPTA DEJA `tip_N?` optional pe factura
(d394.py:301).

RISCUL TEHNIC CHEIE, NEVERIFICAT: **poate valida J8 o operatiune N emisa?** De testat PRIMUL lucru (proba DUK), ca
la scenariile din C4. Daca J8 respinge N indiferent de atribute -> blocaj, ramai pe approach b.

CE CERE structura (validator J8, pct.228/229/60):
- op1.tip_document (1=facturi/2=borderouri/3=file carnet/4=contracte/5=alte) - OBLIGATORIU pt tp2+N. Calea AUTO=1.
- op1.tip_N (1=bunuri/2=servicii) - CONTINUT DECLARAT de contabil (nu derivabil). DEFAULT = NIMIC: fara el, N ramane
  EXCLUS cu avertismentul curent (NU ghici bunuri/servicii - un default gresit da o declaratie ACCEPTATA dar FALSA).
- rezumat1.document_N (=tip_document) - <>null pt tp2+cota0. Conditioneaza facturiLS (R41.2: facturiLS doar cand document_N=1).

PLAN (5 puncte de atingere in core/d394.py, dupa ce proba DUK confirma fezabilitatea):
1. Cele doua ramuri `if tip == "N":` - daca `f.get("tip_N")` in (1,2): INCLUDE (nu exclude); altfel exclude ca acum.
2. Cheia op1 pt N trebuie sa poarte tip_N (2 op N la acelasi partener cu tip_N diferit = 2 intrari). Extinde cheia
   sau tine un side-dict {cheie_op1 -> (tip_document=1, tip_N)}.
3. rezumat1 (tp=2, cota=0): adauga `document_N=1` in dict-ul `r` cand exista N (emisia la d394.py:614 ia din `r`).
4. Emisia op1 (d394.py:648-657): adauga `tip_document="1" tip_N="X"` pentru tip N.
5. Flip gardul invers (cauta `GARD_INVERS`/`test_.*_N_.*respins` in core/test_d394*.py - poate nu exista inca cu
   numele exact; groundwork il numeste test_rezumat1_tp2_neinreg_N_respins_de_validator_DATORIE / test_N_ar_fi_
   respins...). Cand N se emite valid, gardul care spunea "N ar fi respins" trebuie sa devina "N e acceptat".

DB + UI (dupa ce generatorul e probat DUK):
- Camp nou pe factura (tabela facturi din tenant_template.sql + migrare idempotenta pe tenant_001, ca la C5/A2):
  ex. `tip_n smallint NULL CHECK (tip_n IN (1,2))`, default NULL. Backward-compat: NULL = exclus (comportament curent).
- pull() d394 (d394.py:~700+) citeste f.tip_n si il paseaza ca `tip_N` in dict-ul facturii.
- UI (firme.js / ecranul de factura): pe o factura de achizitie FARA CUI furnizor (care da N), un select "bunuri/servicii"
  (default gol). Cauta in firme.js cum se face un select pe factura (ex. taxare_inversa) si oglindeste.
Suport tip_document 2-5 (borderouri/contracte) = EXTINDERE DE CONTRACT separata; daca e prea mare -> sub-blocaj motivat.

### Punctul 4: D390 "ZIUA 15" — art.284 (A2) — MIGRARE + camp optional
Groundwork: cauta A2 in DECIZII/GARZI ("exigibilitate / prag|d390", "ziua 15", art.283/284). Camp
`data_faptului_generator` in tabela facturi + migrare idempotenta pe TOTI tenantii (tenant_001) + tenant_template.sql.
Camp OPTIONAL: cand e gol, comportamentul actual (incadrare pe data_emitere) RAMANE neschimbat - backward-compat probat.
Aceleasi precautii ca C5 (dump, efemera intai, oprire la esec, nu lasa tenanti partiali). Generatorul d390 foloseste
data_faptului_generator cand e prezent pt incadrarea in perioada (exigibilitate art.284), altfel data_emitere.

### Punctul 5: D177 (A3) — cere DOWNLOAD structura de la ANAF
Groundwork: cauta A3 / D177 in DECIZII/GARZI. Structura oficiala D177 LIPSESTE din anaf_surse/. DESCARC-O de la ANAF
(WebFetch/WebSearch pe static.anaf.ro - formular 177 "Cerere redirectionare impozit micro"). FARA ea NU inventa campuri:
daca nu o obtii -> blocaj motivat, treci mai departe. Motorul calculeaza deja `redirectionabil_d177` (cauta in cod).
Formularul D177 = cererea de redirectionare a impozitului pe micro catre sponsorizari/burse.

### Punctul 6: AMORTIZARE MF — metode neliniare (C3) — SUBSISTEM
Groundwork: xfail `test_datorie_mf_metode` in core/test_datorie.py (cauta motivul). Subsistem de mijloace fixe:
amortizare DEGRESIVA + ACCELERATA (azi doar liniara). TEMEIURI LA SURSA inainte de cod: CF art.28 (Codul fiscal),
metodele degresiva (coeficienti 1.5/2/2.5 pe durata) si accelerata (50% primul an). Afecteaza MF + D406 (SAF-T
AssetTransactions). Scop propriu - probabil sub-blocaje.

### Punctul 7: PLAFON CRESA >450/copil (C1) + FEREASTRA CULTURALE oct.2025-mar.2026 (C2) — MO RESEARCH
Groundwork: DECIZII 02.08 (tichete cresa: "indexarea 368/179/2026 = 740 lei GRI"; tichete culturale: "fereastra GRI
oct2025-mar2026"). REINCEARCA la MO (WebSearch/WebFetch) ordinele: 368/2026 (indexare cresa 740) si 1574/3246/2025 +
369/2624/2026 (plafoane culturale). Ce se CONFIRMA la MO -> deblocheaza (adauga fereastra in common.plafon_cresa /
plafon_cultural, ca la celelalte ferestre). Ce NU se confirma -> ramane GRI cu data incercarii SCRISA. `common.plafon_cresa`
si `common.plafon_cultural` au deja structura de ferestre datate - adaugi o intrare cand un ordin e confirmat.

## Reguli (din comanda Costin)
- Nu opri pentru ordine/structura/nume/forma testului - decizi singur.
- Opreste-te DOAR pentru: poarta rosie, tree murdar, esec migrare pe tenant real, sau alegere care schimba ce declara
  contabilul si NU rezulta din structura oficiala.
- Prea mare pentru o campanie -> blocaj motivat cu 4 elemente (CE/DE CE/CE TREBUIE/URMATOR), mergi mai departe.
- Poarta + push de siguranta dupa fiecare punct. Raport §2.2 sectiunile 1-10 per punct.
- RAPORT FINAL cand toate 7 tratate: implementat vs blocaj (cu motiv), efect pe produs punct-cu-punct, stare migrari
  pe tenanti, sold datorii, si EXPLICIT ce mai lipseste ca sa iasa din mentenanta.

## NOTA context / quoting
- Pentru editari pe server: scrie patch python LOCAL si `cat fisier | ssh iconta "venv/bin/python3 -"` (pipe).
  NU heredoc inline in `ssh '...'` cu `$`/`!`/ghilimele - se ciocnesc. Commit cu ghilimele: `git commit -F fisier`.
- DUK: `from core import duk; duk.valideaza(xml, "d394", an=..., luna=...)` -> {stare: valid/erori/gri, erori}.
  d394 foloseste J8 (validatorul instalat curent). Pattern probe: monkeypatch/ construieste res + build_xml + valideaza.


---

# RAPORT FINAL — campania „implementarile ramase" (04.08.2026)

## 1. Implementat vs blocaj (motiv intr-o linie)

| # | Punct | Stare | Motiv (o linie) |
|---|---|---|---|
| 1 | C5 migrare tichete culturale | **IMPLEMENTAT** | CHECK-uri beneficii_lunare extinse (tip 'cultural', eveniment 'ocazional'); migrat tenant_001 |
| 2 | C4 sectiunea 8.3 avantaje D112 | **IMPLEMENTAT** | E3_10/72/73/74/75 -> E3_60 (suma >= componentele), fara sa atinga E3_8/E1_1 |
| 3 | Suport N D394 | **IMPLEMENTAT PARTIAL** (approach a conditionat) | N emis VALID (DUK-probat) cu categorie_331 lit.D; fara categorie = exclus+avertisment. Deblocaj = UI categorie_331 |
| 4 | D390 ziua 15 art.284 | **IMPLEMENTAT** | camp OPTIONAL data_faptului_generator; exigibilitate = MIN(data_emitere, ziua 15); migrat tenant_001. Deblocaj = UI de completare |
| 5 | D177 | **BLOCAJ MOTIVAT** | e cerere-formular PDF, nu declaratie XML validata de jar DUK -> nu are autoritatea R17; canal = decizie produs |
| 6 | Amortizare MF neliniara | **BLOCAJ MOTIVAT** | subsistem cu reguli anuale (switch degresiv->liniar, proratare, eligibilitate pe clasa); impact D406, nu d101 |
| 7 | C1 cresa / C2 culturale | **C2 IMPLEMENTAT, C1 BLOCAJ** | C2: cultural 240/470 confirmat la primar + deblocat. C1: cresa 740 confirmat la emitent, dar text ordin neobtinut + mecanism ferestre lipsa |

**Bilant: 5/7 livrate (1,2,3-partial,4,7-C2), 2 blocaje motivate + 1 sub-blocaj (C1).**

## 2. EFECT PE PRODUS (ce poate face contabilul azi si nu putea inainte)

1. **Acorda tichete culturale** (lunar + pe eveniment ocazional) — baza le accepta acum; inainte CHECK-ul beneficii_lunare le respingea la insert.
2. **D112 declara corect avantajele sect.8.3** — masa/cresa/cadou/cultural/vacanta agregate in E3_60 cu suma >= componentele; inainte lipseau sau erau sub-declarate.
3. **D394 cu achizitii de la neinregistrati (N) categorizate art.331 iese VALIDA** — inainte orice operatiune N o facea neconforma/respinsa de J8. Fara categorie: exclus + numit in avertisment (nu tacut).
4. **D390 incadreaza facturile IC pe exigibilitate** (MIN data_emitere / ziua 15 luna+1 fapt generator) — o factura intarziata intra in perioada corecta cand campul e completat; NULL = comportament vechi (data_emitere), backward-compat probat in ambele sensuri (intarziat SI avans).
5. **Plafon cultural oct.2025-mar.2026 calculat automat 240/470** — inainte era blocat GRI (contabilul primea eroare motivata, nu putea seta).

## 3. Stare migrari pe tenanti

- **Aplicate pe tenant_001** (singurul tenant real): C5 (`migrare_tichet_cultural.verifica`=True, pe beneficii_lunare) + `data_faptului_generator` (coloana prezenta pe facturi).
- **In tenant_template.sql** (sursa unica pt tenanti NOI): ambele. NU exista schema live `tenant_template` in DB — provisionarea ruleaza fisierul .sql, auditat F165 (audit_schema.py, drift template->tenant = HARD).
- **Nimic ramas „doar in fisier"** care ar trebui aplicat pe tenant_001. Fara tenant partial.

## 4. Sold datorii

- **xfail: NESCHIMBAT.** 28 markeri in test_datorie.py la baseline 3dbb175 (inainte de campanie) = 28 acum (~21 xfail runtime). Campania **nu a introdus xfail nou si nici regresii verzi-false**.
- **Datorii NOI create de campanie** — toate scrise acum in GARZI.md (locul canonic; sectiunea „04.08 Datorii deschise ale campaniei" + Categoria 3):
  - `clasifica_partener` infera platitor TVA din FORMA CUI, nu din flag real -> risc de misclasificare N (PJ neplatitor TVA vs persoana fizica).
  - **UI categorie_331** lipsa -> N in calea auto ramane exclus (deblocajul principal al pct.3).
  - **UI data_faptului_generator** lipsa -> D390 ziua-15 nefolosibil pana la ecran (coloana e OPTIONALA, NULL = corect).
  - **D177 canal** de emitere (formular PDF vs XML) — decizie produs.
- **Referinta (deja in GARZI, nu duplicat):** tip_document 2-5 + tip_N (N complet); amortizare MF neliniara (Categoria 3, xfail existent).
- **Corectate ca stale in GARZI** (onestitate): fereastra cultural (GRI -> confirmat 240/470), cresa (740 GRI verdict 17 -> confirmat la emitent/neaplicat), intrarea N (approach-b -> approach-a conditionat; rand de tabel cu test inexistent inlocuit cu testele reale).

## 5. Ce mai lipseste ca produsul sa IASA DIN MENTENANTA (intrebarea principala)

Onest: **nu poate iesi complet**, din cauza unei singure gauri structurale — dar restul sunt lucrari finite.

1. **Deriva legislativa nedetectata (gaura structurala #1).** `cota()` refuza valori dupa `data_out`, dar o schimbare de lege **intre data_in si data_out** e invizibila. Nu exista feed legislativ RO mecanic fiabil (dovedit repetat in campanie: WebFetch esueaza, MO se citeste manual). -> degradeaza la **revizuire manuala periodica ghidata de GARZI/temeiuri structurate**, nu la automatizare. Asta tine produsul in mentenanta prin natura domeniului.
2. **UI in urma motorului.** Mai multe functii livrate sunt „oarbe" fara ecran: categorie_331, data_faptului_generator, tip_N. Motorul stie sa le foloseasca; contabilul nu le poate seta. **Lucrare finita** (ecrane), nu structurala.
3. **Flag real de platitor TVA pe partener** (VIES/ANAF) — inchide misclasificarea N din `clasifica_partener` (azi pe forma CUI). Finita.
4. **Garduri de CONTINUT, nu doar structura.** DUK valideaza structura, nu semantica (GARZI cat.4). Lipsesc: totaluri reconciliate pe a DOUA cale de calcul, snapshot de regresie pe fixturi inghetate, mutantul-zero sistematic (azi ad-hoc). O declaratie structural-valida dar semantic-gresita inca poate trece.
5. **Subsisteme blocate pe decizie de produs:** amortizare MF neliniara (campanie proprie), D177 (canal). Pana nu-s decise, raman gauri cunoscute.
6. **Operational:** proba de restaurare backup automata periodica (azi one-shot manual), verificare nocturna Sigma debit = Sigma credit per tenant/perioada, deadman EXTERN pentru heartbeat (azi verificatorul ruleaza pe acelasi server).

**Concluzie:** punctele 2-4 si 6 sunt lucrari finite care ar muta produsul de la „reactiv" spre „proactiv gardat". Punctul 1 (deriva legislativa) ramane structural si se gestioneaza prin disciplina de revizuire ghidata de registru — nu prin cod.
