Citeste CLAUDE.md §2.2 (structura raportului) si §2.3 (lant, siguranta, limba) inainte de a incepe.

## ★★ PREDARE — 07.08.2026 — CITEȘTE ASTA ÎNTÂI (supersedează secțiunea C-4 de mai jos, care e istoric)

**Ritual pornire:** `ssh iconta 'cd ~/iconta_nou && pwd; hostname; git log -1'`. Apoi citește CLAUDE.md §2.2/§2.3.

**⚠ STARE — ATENȚIE: main NU e publicat.**
- HEAD (local) = **`9b3e88f`**. Backup remote OK: `backup/lant-2026-08-07` = `9b3e88f` (identic).
- **origin/main = `2fc777d` — în urmă cu 45 commituri.** HEAD ≠ origin/main. Munca există în 2 din 3 locuri
  (server + backup), NU pe origin/main. Vezi „REGULA PUSH" mai jos ÎNAINTE de a împinge (Costin a cerut să NU
  se împingă până nu decide).
- Tree curat, poartă verde (verificator TOTAL 0, 1524 passed).

**CE S-A LIVRAT (cele 45 de commituri `origin/main..HEAD`, tematic):**
- **Corpus legislativ (azi 07.08)** — 575bd5e/68feed5/9b3e88f + B1 tichet/plafon (7e53ac7/ebae623):
  temeiurile COTE legate la fișiere locale din `anaf_surse/`, ridicate REDARE→MO **verbatim, act cu act**.
  COTE MO 4→24, REDARE 9. Manifest **`anaf_surse/INDEX.json`** (regenerabil: `anaf_surse/gen_index.py`) +
  3 gărzi **`core/test_corpus_surse.py`**: G1 (MO ⟹ sursă locală existentă), G2 (formă `consolidat_la_zi` nu
  poate sursa o valoare cu succesor — prinde CF consolidat la zi), G3 (`cote_volatile_fara_mo`, prag 18 luni,
  warning la generare — semnalează DOAR valoarea curentă non-MO volatilă/recentă). OUG 8/2026 + OUG 89/2025
  aduse local și legate (6 valori). **D112 byte-identic `ea0520b0c8b2eb0c`** pe tot (doar temeiuri, zero valori).
- **Model episod CM (azi 07.08)** — da990a8/7785a55: indemnizația pe **EPISOD**, nu pe certificat (OUG 158/2005
  art.17), migrare `core/migrare_cm_episod.py` (12/12 scheme, backup `pre_cm_episod_20260807`), recalcul
  retroactiv, refuz pe perioadă confirmată, `data_episod_initial`. Gard `core/test_cm_episod.py`. art.XI
  L141/2025 = forma pre-141 (75% uniform pe certificatul inițial). NEFĂCUT: sugestia AUTO de legare episoade
  adiacente (decizie, nu defect).
- **Ieri (06.08):** campanie reparație închisă + **PLAN_B rescris** (b02b837); blocuri B3 (proprietarul cabinetului
  depune fără blocaj), A6 (D394 linia scutită L→LS), D1a (skip vizibil la import); C-5 conformitate cap.6
  (G1–G12 markeri); **G10 Faza 0 coexistență + Faza 1 PILOT pe `flux_concediu`** (b1dcc0d).

**E1–E12 (PLAN_B.md) — propunere DATĂ și APROBATĂ, dar NEEXECUTATĂ:**
- Parcurgere cap-coadă a aplicației ca un contabil real (NU scanare de sursă). PLAN_B.md = documentul
  (E1–E12 + firme F1–F8 + „cum se citește un eșec").
- **Aprobat:** firma **F2** (micro + salariați + TVA trimestrial); parcurgere **E1→E11** o tură; **HTTP acum**
  (FastAPI, `main.py`; pornești `uvicorn` + conduci ca client HTTP — NU există browser headless pe server);
  **headless a doua tură** (instalezi playwright+chromium doar dacă rămâne suspiciune pur-vizuală / pentru E12).
- **NEÎNCEPUT:** `E1E12_GASITE.md` **nu există încă** — se creează la prima parcurgere. **Nu repari pe loc**: doar
  consemnezi (stări: DEFECT | SUSPICIUNE | INFIRMAT-OK | DESCHIS-cunoscut); reparațiile cu aprobarea lui Costin.
- Defect = divergență pe FLUX REAL, cu repro (declarație datorată lipsă / declarație greșită tăcută & depozabilă /
  blocaj tăcut sau prost plasat / izolare tenant spartă / te obligă să ghicești). NU zgomot: A5, F8-produs,
  AUTO-legare CM (deschise cunoscute).

**CE E DESCHIS și DE CE:**
- **Octombrie 2025 `tichet_masa_plafon` = GOL MOTIVAT.** Lipsește Ordinul MF tichet sem.II 2025; `data_out`
  explicit 30 sep pe Ordinul 484/2025 oprește propagarea tacită a lui 40,18. `cota(..., 2025-10-...)` ridică
  „gol in registru". Se închide când vine ordinul.
- **Acte P2 (istorice, pentru recalculări retroactive) — REDARE, surse neaduse:** OG 16/2022 (dividend 8%@2023),
  Legea 296/2020 (plafon TVA 4,5M@2021), OUG 115/2023 (avans 5.000 + facilitate 300@2025), Legea 70/2015
  (sold casă 50.000).
- **Snapshot CF 2016/2017 — LIPSĂ.** `cod_fiscal_227_consolidat` e LA ZI → nu conține formele istorice, deci
  tva_standard 19%@2017, plafon_mijloc_fix 2.500@2015, impozit_dividend 5%@2016 rămân REDARE. Nevoie de
  snapshot-uri CF la 2016 și 2017 (nu consolidatul curent). Garda G2 blochează abuzul (formă la zi pe valoare veche).
- **`tva_redusa_5` 11%@2025 = DECIZIE de produs (nu act lipsă).** Legea 141 pct.43 abrogă cota de 5% (art.291
  alin.3); unde ajung fostele operațiuni (cărți, acces cultural, locuințe sociale) — 11% vs 21% — nu e confirmat
  verbatim, diferă probabil pe operațiune. Legea 141 e locală; de citit pct.43 + lista operațiunilor și de decis.
  E singura valoare pe care garda G3 o mai semnalează.
- **A5 amortizare — DESCHIS.** `calc_asset` e liniar (pe luni) chiar dacă metoda zice degresiv/accelerat.
  Campanie proprie „amortizare MF metode" amânată (nu se rezolvă pe jumătate — o metodă incompletă ar da deducere
  fiscală eronată). E8/D406 se parcurge cu asta în minte.
- **G10 verdict VIZUAL — DESCHIS.** G10 (mesaj lângă câmpul-cauză) e doar Faza 1, DOAR pe `flux_concediu` (câmp
  `#cm-cnp-ingrijit`, coduri 09/91/92/17). Pe celelalte fluxuri NU e implementat. Că mesajul chiar *apare lângă
  câmp* (nu doar există în DOM) e neverificabil fără browser → rămâne pentru tura headless / E11.

**REGULA PUSH (constatare 07.08 — clasă de defect, nu doar pas uitat):**
- Regula (CLAUDE.md §2.3 pct.8, decizia c răsturnată 05.08): munca în TREI locuri — server + backup + origin/main;
  push pe main sub poartă verde, FĂRĂ aprobare, fast-forward; raportul confirmă HEAD = origin/main = backup.
- **NU e cablată:** `core.hooksPath = scripts/githooks`; `pre-commit` rulează DOAR poarta verde (pytest +
  verificator), NU împinge. Fără `post-commit`/`pre-push`. Push-ul pe main e pas MANUAL.
- **Ce a ieșit din verificare:** s-a împins doar în backup; push-ul pe origin/main a fost sărit repetat (45
  commituri), iar verificarea three-way de la finalul raportului (care l-ar fi prins) a fost și ea sărită.
  Push-ul NU eșuează: `2fc777d` e ancestor curat, `behind=0` → `git push origin main` = fast-forward curat.
- **De făcut (cu decizia lui Costin):** (a) `git push origin main` (fast-forward, NU forța) ca să aducă origin/main
  la HEAD; dacă origin/main a avansat sub tine (commit al lui Costin) → `pull --rebase` ÎNTÂI. (b) Fix de clasă:
  `post-commit`/wrapper care împinge pe main sub poartă verde, SAU gard care refuză raportul „încheiat" cât timp
  HEAD ≠ origin/main. Costin a cerut să NU se împingă până nu decide.

**INFRASTRUCTURĂ (neschimbată — secțiunea C-4 de mai jos rămâne validă pentru detalii de seed/generare):**
- Poartă verde: commit pe server rulează pre-commit (suită ~4min + verificator); **rulează commit-ul în background**.
  Backup: `git push -f origin HEAD:backup/lant-<data>` (remote-only). DB live: `set -a && . ~/.iconta/db.env &&
  set +a`; `venv/bin/python`. tenant_001 există.
- Scripturi cu paranteze/ghilimele → fișier local + scp (heredoc prin ssh double-quote se strică; backtick în
  `ssh "..."` golește mesajul de commit — trimite prin stdin single-quoted). Editează cod pe server cu patch-uri
  python (io.read + `.replace` cu count==1 + io.write).

---



## ★★ PREDARE — C-4 TRANȘA 2 (coerență + TVA) — 06.08.2026 — CITEȘTE ASTA ÎNTÂI

**STARE:** HEAD = origin/main = backup/lant-20260805 = **559bce3**. Tree curat. Poartă verde (verificator TOTAL 0).
Ritual pornire: `ssh iconta 'cd ~/iconta_nou && pwd; hostname; git log -1'`; apoi `python -m core.agenda` / `agenda_drift`.

**TRANȘA 1 (salarizare S4) ÎNCHISĂ** cu DUK verde complet (12 luni × 12 salariați FĂRĂ EROARE). 6 neconformități
fiscale găsite de seed-ul S4, TOATE reparate cu gard + RED/GREEN + vânătoare de clasă:
1. brut/bază declarate pe salariul contractual stale (01c075a) · 2. bază minimă part-time = sm−facilitate → sm integral
(2786954) · 3. filtrare salariați fără data_angajare, 4 situri (2786954) · 4. cod 15 D_23="RM" · 5. cod 07 carantină
absentă din angajatorC2 · 6. cod 10 D_13 aviz (toate 4661fa5). GARZI: divergență part-time lege-vs-DUK (7982dfd).
Seed reproductibil: `date_test/seed/transa1_salarizare_s4.py` (559bce3).

**CE URMEAZĂ — TRANȘA 2 (coerență + TVA):**
- Cele 6–7 tranzacții R3 (**T-1…T-7**, `date_test/C4_date.md` secțiunea C) cu **sume EXACTE identice pe ambele laturi**
  (emitent + primitor: CUI/sumă/dată identice → D394 vânzări↔cumpărări + control_incrucisat se verifică din date).
  T-7 (P1→S4) deja are S4 din tranșa 1. TVA 21% (cotă 2026).
- Documentele care produc rândurile **D300/D394/D390/D301** pentru **M1/M2/P1/P2/N1/S1/S2/S3** (S3 = agricultor forfetar,
  interacțiune D394 „achiziție de la agricultor" = exceptia numită; N1 = D301 achiziție IC de neplătitor).
- Cele **14 valori la limită** din catalogul C-4 secțiunea B care țin de TVA (L1 prag micro 100k, L2 perioadă TVA, L3
  prag scutire 395k, L4 TVA la încasare 4,5M→5M la 01.03, L10 achiziție IC 10k, L12 semne contrare storno/retur/ajustare),
  fiecare cu **3 cazuri (exact/−1/+1)** — DAR (lecție tranșa 1): cazul **prag−1 e uneori DATE DEFECTE (C-5)**, nu C-4
  (app-ul blochează, ex. salariu sub minim). Verifică per prag dacă −1 e date corecte sau input defect.

**METODOLOGIA (identică cu tranșa 1):** orice divergență = **bug până la proba contrarie** → **vânătoare de clasă**
(TOȚI consumatorii, nu doar situl unde a apărut — bug-urile #1 și #3 aveau 2–4 situri) → **temei la sursă** (verbatim,
din `anaf_surse/`) → **gard + mutație + RED/GREEN** → **DUK**. NU raporta între bug-uri; UN SINGUR raport la închiderea
tranșei, cu §2.2 pe fiecare neconformitate.

**INFRASTRUCTURĂ (dovedită în tranșa 1):**
- Provizionare: `core.tenant_provisioning.provision_tenant(conn, nume, cui, firm_id, user_id, tpl)`;
  `tpl=open("tenant_template.sql").read()`; cabinet+admin via `core.auth_api.inregistreaza_cabinet`. Setează
  `firma_profil.caen` după provizionare (D394 îl cere).
- Conexiune: `core.db.get_conn(schema="tenant_NNN")` (setează search_path). Încarcă `~/.iconta/db.env` în os.environ ÎNTÂI
  (vezi `_incarca_db_env` din seed-ul tranșei 1).
- Generare declarații — **atenție la semnătură** (verifică `inspect.signature`): `d300.pull(conn, schema, Perioada(an,luna))`
  și d394/d390/d301 folosesc **Perioada** (din `core.common`); `d112.genereaza(conn, schema, an, luna)` folosește an/luna.
  Toate întorc `(xml, avertismente)`. Rute HTTP: `POST /declaratii/{tip}` și `/declaratii/{tip}/valideaza` → `declaratii_api.genereaza`.
- DUK: `core.duk.valideaza(xml, tip, an=, luna=) -> {"stare": "valid"|"erori"|"gri"}`. **Atenție:** „atenționare" (A:) ≠
  „eroare" (E:); atenționările NU blochează depunerea, dar `stare` devine „erori". Clasifică pe liniile `E:` vs `A:`
  (pattern `/tmp/clasific.py` din tranșa 1). „gri" = nevalidat (java/validator lipsă), NU verde.
- CUI-uri fictive (verificate ANAF v9 05.08, lot 95–96M) în `date_test/C2_firme.md`; **re-verifică la seed**. Firme:
  M1=95138914, M2=RO95141537, P1=RO95275466, P2=RO95363126, N1=95451848, S1=RO95687300, S2=RO95775518, S3=95873249,
  NR1=RO95904434, T1=96385785, T2=RO96516171, S4=RO96653616. Cabinet Prisma=RO96756476 (tenant_001 existent).
- Poartă verde: commit pe server rulează pre-commit hook (suita ~4min + verificator). **Rulează commit-ul în background**
  (background=true). Push `origin main` + `origin HEAD:backup/lant-20260805` fără aprobare (§2.3 pct.8).
- **Scripturi cu paranteze/ghilimele → fișier local + pipe** (`cat local | ssh iconta 'cat > /tmp/x.py && python3 /tmp/x.py'`);
  heredoc-urile prin ssh double-quote se STRICĂ. Editează codul pe server cu patch-uri python (io.read + .replace + io.write).

**LECȚII (tranșa 1):** (a) regula 3 cazuri — prag−1 poate fi C-5, nu C-4. (b) DUK poate fi în urma legii (part-time) →
urmează legea + GARZI (ca D101-scadență). (c) DB live are tenant_001 (S4); gărzile care scanează tenanți (cnp_ingrijit)
sunt ACTIVE acum — nu le sparge. (d) TVA cota 21% e period-aware (`common.cota("tva_standard", data)`); NU hardcoda.

**DE CE M-AM OPRIT:** §2.3 pct.6 (buget de context epuizat) la granită curată (tranșa 1 închisă, tree curat, 559bce3),
cu această predare. Registrele la zi. Tranșa 2 începe de la seed-ul de firme + tranzacțiile R3.

---


# PREDARE — Campania EXTINDEREA ACOPERIRII (05.08.2026)

## ★★ PREDARE CAMPANIA DE TESTARE 05.08.2026 — CITESTE ASTA INTAI (predarea ★ de mai jos = sesiunea de cod, istoric)

**UNDE S-A AJUNS:**
- **PASUL 1 (stergerea datelor de test) INCHIS.** DB de la zero: 0 scheme tenant, 0 randuri tenants/accounting_firms.
  Cont unic id=1 (costin.hateganu@gmail.com) promovat **superadmin** cu accounting_firm_id=NULL (acces platforma,
  observational). Backup: /home/costin/backups_db/iconta_pre_curatare_20260805_204420.dump. App HTTP 200, provisionare
  din template functionala (46 tabele), funnel inregistrare cabinet DESCHIS. Gardul test_toti_tenantii_au_cnp_ingrijit
  trecut la SKIP pe mediu gol - **trebuie sa REDEVINA activ dupa popularea firmelor (C-3), verifica**.
- **C-1 (matricea obligatiilor) LIVRAT + VALIDAT** de Costin cu 3 completari (regimuri speciale TVA art.311-315;
  e-Factura/e-Transport; D392 abrogat + D207 in vigoare). Salvat: **date_test/C1_matrice_obligatii.md**.

**CELE 8 CONFIRMARI RAMASE (la sursa, INAINTE de C-2 - firmele se deriva din matrice, NU se presupun):**
1. Cota micro 1% vs 3%: prag 60.000 EUR + lista activitatilor la 3% -> CF art.51 (forma 2026, anaf_surse/cod_fiscal).
2. Lista CAEN excluse de la micro 2026 (consultanta/management >20% etc.) -> CF art.47 + OUG modificatoare.
3. Data intrarii pragului TVA 395.000 lei + stabilitate pe 2026 -> Legea 141/2025 + norma.
4. Data tranzitiei TVA la incasare 4.5M->5M ianuarie 2026 -> CF art.282 + Legea 141/2025.
5. Salariul minim brut 2026 -> HG salariu minim (MO).
6. Calendarul SAF-T firme mici (01.01.2025 + amanari) -> OPANAF 1783/2021 + acte amanare.
7. D392 re-verificat ca nu a fost reintrodus (confirmat abrogat aici) -> legislatie.
8. Periodicitatea D112 trimestrial - care micro/mici pot opta -> CF Titlu V + OPANAF.
=> C-2 se incepe ABIA DUPA ce cele 8 sunt confirmate la sursa.

**PROCEDURA PE CATEGORII (obligatorie): o SINGURA categorie, apoi STOP; Costin valideaza/modifica; abia atunci se
salveaza ca set valid; urmatoarea categorie abia dupa confirmarea celei anterioare. NU anticipa, NU doua odata, NU
incepe urmatoarea in timp ce astepti.**
- **C-1 MATRICEA** (din legislatie, NU din cod) — LIVRAT+VALIDAT.
- **C-2 FIRMELE** — setul minim care acopera toate celulele matricei validate. Numarul IESE din matrice, nu se fixeaza
  dinainte. CUI-uri fictive: cifra de control OK DAR sa NU apartina firmelor reale (verifica inainte de a le fixa -
  altfel ANAF v9 intoarce date terte). Idem CNP-uri (salariati/copii/pacienti): fictive, valide ca structura,
  neapartinand persoanelor reale. Daca nu poti garanta pt un identificator, SPUNE - nu-l inventa.
- **C-3 CABINETELE/ASISTENTII/CLIENTII** — cine administreaza firmele, roluri+drepturi distincte: patron cabinet,
  asistent cu poate_valida, asistent fara, asistent cu firme atribuite partial, client de portal. Fiecare rol = cont cu
  email+parola CUNOSCUTE (pt verificarea vizuala de la etapa 2). Gardul test_toti_tenantii_au_cnp_ingrijit revine activ.
- **C-4 DATE CORECTE** — documentele care produc EFECTIV randurile cerute de declaratiile fiecarei firme (nu generice:
  daca D394 are rand achizitii de la neplatitori -> factura de la neplatitor; D300 taxare inversa -> operatiune de
  taxare inversa). Valori la LIMITA: praguri CA, plafon CM, salariu minim, luni partiale (angajare la mijloc, CM peste
  luni), operatiuni cu semn contrar (storno, retur, ajustare TVA).
- **C-5 DATE DEFECTE** — acoperire ABSOLUT COMPLETA, fara exceptie: toate ridicarile de exceptie backend, toate
  returnarile de eroare din rute, toate validarile de formular UI, TOATE campurile obligatorii cu asterisc pe toate
  ecranele (sweep-ul 24.07 neterminat - se reia integral), toate starile de blocare (rol insuficient, perioada inchisa,
  date lipsa). Inventar prin SCANARE SISTEMATICA a codului, nu din memorie. Fiecare caz: mesajul explicativ care trebuie
  sa apara (Design System cap.6: explicit, cu lux de amanunte, CE e gresit + CE trebuie facut; niciodata telegrafic,
  niciodata "a aparut o eroare"; nicio oprire fara mesaj). Cale neacoperibila -> declarata explicit cu motivul (omiterea
  tacuta = esec). Cea mai mare categorie - daca nu incape intr-o livrare, se imparte pe module si se anunta in cate
  bucati vine INAINTE de prima.

**REGULILE R1-R4 (se aplica TUTUROR categoriilor):**
- **R1 VOLUM REALIST**, nu simbolic. Zeci-sute documente/an per firma activa (exerseaza paginare/reconciliere/perf).
  Volumul per firma se PROPUNE si se justifica; Costin il valideaza.
- **R2 REPRODUCTIBILITATE.** Datele = fisiere VERSIONATE in git, din care popularea se reface identic dupa stergere. NU
  inserturi ad-hoc. Al doilea rulaj comparabil cu primul.
- **R3 COERENTA INTRE FIRME.** Firma A factura catre firma B (ambele in set) -> sume/CUI/date IDENTICE. Altfel controlul
  incrucisat si D394 produc divergente din DATE, nu din cod.
- **R4 CALEA DE INTRARE.** Fiecare tip de document: marcheaza cum intra - prin ECRAN (se testeaza calea) sau prin SEED
  (nu). Fiecare cale distincta (e-Factura, upload manual, OCR bon, import banca, tastare directa) exersata prin ecran
  cel putin o data; volumul poate intra prin seed.

**PERIOADA acoperita:** an fiscal 2026 complet + ianuarie 2027 (anuale + tranzitia de an). Legislatia = cea in vigoare
pe fiecare perioada (parametrii 2026 difera de 2025 - Legea 141/2025, OUG 156/2024). NU presupune cote constante pe an.

---


## ★ PREDARE FINALA 05.08.2026 (inchidere sesiune) — CITESTE ASTA INTAI (restul de mai jos = istoric tura cu tura)

**STARE:** HEAD = origin/main = origin/backup/lant-20260805 = **a979715**. Tree curat. Suita **1445 passed / 2 skipped /
21 xfailed** (COLLECTED 1468). verificator TOTAL **0**. Ritual de pornire (prima actiune): `pwd; hostname; git log -1`;
`python -m core.agenda`; `python -m core.agenda_drift`. Push sub poarta verde pe backup SI main, fara aprobare (§2.3 pct.8).

**CE S-A INTAMPLAT:** sesiunea a pornit pe 1c-CM (concedii medicale). Verificarea rotunjirii la sursa a scos ca premisa
retetei era gresita + o NECONFORMITATE FISCALA ACTIVA -> deviere justificata pe descoperiri, apoi pe cererile lui Costin.
Livrate (fiecare cu proba RED/GREEN/DUK + gard + poarta verde + push):
1. **D112 CM baza salariala CAS/CASS/CAM = castig REALIZAT** (proratat pe zile lucrate), nu brut intreg (ced5e23).
   CF art.139(1) "realizat". Supra-declarare ~952 lei/angajat-luna eliminata.
2. **Poarta cale2 D112 pe valorile EMISE** (post-generare), nu pre-emisie (27adccf). Doar D112 avea blind-spot-ul.
3. **Impozit CM neimpozabil** (08/09/15/17/91/92, CF art.62 lit.c) exclus din baza impozitului, SIMETRIC (+CAS/CASS
   aferent), in taxe_cm + d112.bimp (0abb9cc). Coduri 14/18 = impozabile (DECIZII.md).
4. **Poarta pe ARTEFACT** (res==parse(emis)) pe 6/7 declaratii (cb752e8): totalPlata_A parsat din XML == res.
   d406 = exceptie lossy. 2b (rotunjire) NU e prins de asta (per-rand, treaba DUK).
5. **Feature CNP persoana ingrijita** D_8 (09/91/92) / D_8a (17): schema+migrare (1/1 tenant) + validare cifra control +
   emisie + UI (Design System) + block pe CNP lipsa + E2E cod 09 DUK VALID (d878762).
6. **Campania C (5 clase oarbe)** (94fe7d0..a979715): C5 (AST anti-except + mutant-zero), C2 (fluturas<->D112 via
   artefact contabil + D101 preexistent; D100/D205 tautologii numite), C3 (snapshot+hash regenerare-diff + orfani;
   Sigma debit=Sigma credit tautologic pe schema), C4 (coada REDARE + procedura scrisa), C1 (limita scrisa). Stare
   completa: TESTE.md capitolul "Metode de verificare" sectiunea 7.

**RAMAN (follow-up scopat; nimic blocat definitiv, toate actionabile):**
- **1c-CM reconciliere propriu-zisa** - deblocata de poarta pe valori emise (pct.2 de sus), NEimplementata. cale2 poate
  acum recalcula independent CAS/CASS emise pt CM si le confrunta; CM ramane sarit (cm_ids) in reconciliaza pana atunci.
- **2b rotunjire** - B4_8 = Sigma(round componenta) vs oficial ROUND(B4_7*25%); pe granita 1-2 lei, DUK-invalid. Aliniere
  single-round in emisie = DECIZIE DE PRODUS (schimba iesirea ANAF). GARZI 05.08 tura 4.
- **C1 migrare enforce** - facturi cheie unica naturala (dupa DEDUP) + money columns SET NOT NULL (dupa audit NULL);
  riscant pe date existente -> pas dedup/backfill INTAI. TESTE sectiunea 7.
- **C3 wiring** - job nocturn echilibru_perioada_db per tenant + tabel snapshot pt amprenta la depunere.
- **C5 mutant-zero** - extins la d100/d101/d300/d394/d406 (marker de continut per generator).
- **d406 poarta pe artefact** - partida dubla necablata (fixturi de test cu GL dezechilibrat de curatat); DUK accepta GL
  dezechilibrat = constatare.
- **P2/P3/P4 din campania ORIGINALA** (NEATINSE - sesiunea a deviat pe CM): P2 D101 impozabil (ajustari computed vs §8
  manual), P3 amortizare MF neliniara (xfail test_datorie_mf_metode_amortizare), P4 D394 tip_document 2-5. Detalii in
  sectiunile PUNCTUL 2/3/4 din predarea originala mai jos.

**DECIZII CERUTE (produs, Costin):**
1. **GDPR CNP tert minor** - cnp_ingrijit = prelucrare date tert minor sensibile. F199-F205 = drepturi persoana vizata,
   NU ROPA (art.30, LIPSESTE). Nicio baza documentata. Cere temei art.6/9 + informare art.14 + ROPA. Feature livrat (D112
   il cere fiscal); POLITICA GDPR ramane de decis. GARZI tura 11.
2. **2b rotunjire** (single-round) - schimba iesirea ANAF cu 1-2 lei pe granita.

**REGISTRE la zi:** GARZI (garduri + INVENTAR + turele 3-15), DECIZII (14/18), TESTE (Inventar A + capitolul metode
sectiunile 6-7), ISTORIC (turele 3-15). SURSA UNICA respectata.

---



## PREDARE 05.08.2026 (tura 12) - Campania C in curs: C5 partial livrat, C1/C2/C3/C4 + C5-mutant-zero raman

STARE: HEAD dupa acest commit. Poarta verde. Spec-ul celor 5 clase = TESTE.md capitolul "Metode de verificare -
clasele oarbe" (metoda concreta + cost + tautologie + ordine efect x cost per clasa).

LIVRAT in campania C:
- C5 (mascare/zero) PARTIAL: gard AST anti-except-masca (core/test_gard_masca_zero.py) - vezi GARZI tura 12.
- C2 (intre documente) perechea FLUTURAS<->D112 LIVRAT: tautologia identificata (ambele=calcul_salariu),
  a doua cale = artefact D112-XML vs ledger (control_incrucisat.compara_d112 extins+gardat+mutatie) - GARZI tura 13.
  C2-rest (tura 14): balanta<->D101 DEJA COMPLET (d101_reconciliere mutatie-probat); D100<->D112 + Sum(D112)<->D205 = TAUTOLOGII numite (sarite). C3 echilibru perioada LIVRAT (tura 14). C4 scris in TESTE. RAMAN: C1 intrare, C3 job+snapshot, C5 mutant-zero. + migrare cnp_ingrijit inchisa (gard).

RAMAN (in ordinea argumentata efect x cost din TESTE.md), fiecare cu: modul + gard AST non-tautologie + MUTATIE:
- C5 rest: mutant-zero sistematic (generator fortat -> [] => suita/verificator rosu). Diagnostic; verifica ce NU
  prinde nimic cand un generator intoarce gol (poarta pe artefact NU-l prinde: res gol == emis gol).
- C2 (intre documente) - CEA MAI VALOROASA (Costin), precondictia LIVRATA (poarta pe artefact + valorile emise):
  perechile cu cai INDEPENDENTE - fluturas(stat_plata)<->D112 INTAI (divergenta dovedita azi la baza CM); apoi
  Sum(D112 lunar)<->D205; balanta<->D101 deja partial (d101_reconciliere din clase 6/7); D100<->D112 = pass-through
  (tautologie pura, NU merita pana se fac independente). NOTA existenta: control_incrucisat.py deja face D112/D300 vs
  contabilitate (citind XML-ul emis) - de EXTINS / gardat, nu de re-inventat.
- C3 (in timp): snapshot+hash la depunere + regenerare-diff + job nocturn Sdebit=Scredit per perioada/tenant + orfani.
  state_plata snapshot deja DECIS (GARZI INVENTAR A).
- C1a (intrare): invarianti DB (NOT NULL pe coloane de bani + cheie naturala unica anti-import-dublat).
- C1b (intrare<->document sursa): Sum(linii importate)==total document; doar unde sursa e digitala (extras bancar).
- C4 (interpretare sursa): a doua lectura oarba / extindere DUK; continuu per cluster, nu proiect separat.

DE CE M-AM OPRIT (§2.3 pct.6): buget de context epuizat dupa o sesiune foarte lunga (A/B baza CM + poarta valori emise
+ impozit CM neimpozabil + poarta pe artefact 6/7 + feature CNP D_8/D_8a + C5 anti-except). Oprire la granita curata de
commit, nu start de C2 (modul+fixtura per pereche) riscand stare partiala. Registrele la zi.


## PREDARE 05.08.2026 (tura 6) — dupa A+B; urmeaza C (5 clase oarbe)

STARE: HEAD = origin/main = origin/backup/lant-20260805 = **27adccf**. Tree curat. 1424 passed / 2 skipped / 21 xfailed,
verificator 0.

INCHIS in aceasta sesiune (tura 3-6), peste starea de campanie:
- 1c-CM NU s-a implementat ca reconciliere; in schimb verificarea lui a scos DOUA neconformitati, reparate:
- **A (ced5e23): D112 CM baza salariala pe brut INTREG -> proratat pe zile lucrate** (CF art.139(1) "castig REALIZAT",
  structura D112 B4_7=B2_5+B3_7). Neconformitate fiscala activa (supra-declarare ~952 lei/angajat-luna CAS + CASS + CAM).
  Gard test_d112_cm_baza_salariala_realizata_nu_brut_intreg; DUK valid. (GARZI 05.08 tura 4/5.)
- **B (27adccf): poarta cale2 D112 re-arhitectata pe valorile EMISE** (post-generare XML), nu pre-emisie. DOAR D112
  afectat (restul 6 = res==emis). Gard test_d112_poarta_reconciliaza_valorile_emise_nu_pre_emisia. (GARZI 05.08 tura 6.)
- **2b DESCHIS (datorie):** rotunjire Sigma(round) vs round(total) [structura: B4_8=ROUND(B4_7*25%)]. Pe fixturi
  non-granita coincid; pe granita B4_8 emis poate diferi de DUK cu 1-2 lei. GARZI 05.08 tura 4.
- **1c-CM DEBLOCAT** de B (poarta vede acum emisul): reconcilierea CM propriu-zisa se poate implementa; ramane sarit
  (cm_ids) pana atunci.

URMEAZA: **C — cele 5 clase de eroare fara nicio metoda de verificare.** Spec COMPLET (metoda concreta, cost, tautologie,
ordine efect x cost, perechile C2) e in **TESTE.md capitolul "Metode de verificare — clasele oarbe"**. Ordinea argumentata
(de implementat, fiecare cu: metoda concreta ce-compara-cu-ce + non-tautologie probata pe AST ca la reconciliere + mutatie
obligatorie + limita scrisa din start; daca o clasa nu se poate acoperi non-tautologic -> numita, nu fortata):
  1. C5 mutant-zero + gard anti-`except: return 0/pass` pe caile de bani (cost mic, demasca restul, zero tautologie).
     ATENTIE scop: tinteste DOAR functiile de bani (calcul_*/build_xml/pull), altfel fals-pozitive pe except-urile
     legitime (tabele optionale etc.).
  2. C2 reconciliere INTRE documente pe perechile cu cai INDEPENDENTE - fluturas(stat_plata)<->D112 INTAI (are deja
     divergenta dovedita azi; B a livrat precondictia = valorile emise). Apoi Sum(D112 lunar)<->D205; balanta<->D101
     deja partial. NU pe D100<->D112 (pass-through=tautologie pura pana se fac independente).
  3. C3 snapshot+hash la depunere + regenerare-diff + job nocturn Sdebit=Scredit (snapshot state_plata deja DECIS, GARZI A).
  4. C1a invarianti DB pe intrare (NOT NULL bani + cheie unica). 5. C1b intrare<->document sursa. 6. C4 a doua lectura/DUK.
Perechile C2 verificate in cod (TESTE.md): fluturas<->D112 NECONTROLAT (azi divergenta), D100<->D112 NECONTROLAT
(pass-through), D205<->D112 NECONTROLAT, balanta<->D101 PARTIAL, SAF-T<->balanta NECONTROLAT, D300<->jurnale PARTIAL.

DE CE M-AM OPRIT AICI (§2.3 pct.6): buget de context dupa A+B (doua fix-uri fiscale cu proba completa). C e o suita de
5 clase, fiecare un modul+gard+mutatie - mai mult decat un context. Oprire la granita curata de commit (27adccf), nu
start de C riscand stare partiala. Registrele (GARZI/DECIZII n/a/TESTE/ISTORIC) la zi prin tura 6.

---

## Stare la predare
- HEAD = origin/main = origin/backup/lant-20260805 = **ef9ba55** (sau commitul acestei predari, dupa push). Tree curat. Suita 1422 passed, verificator 0.
- NOU: GARZI.md are sectiunea **INVENTAR DESCHISE NON-CAMPANIE** (index canonic al tuturor deschiselor din afara celor 4 puncte;
  A actabil azi / B blocat extern / C decizie luata / D cere decizie produs). La revenire NU se recolecteaza - se citeste de acolo.
- Livrate in aceasta sesiune (peste 1a=4ad6f72): 1b TICHETE DE MASA (63b0865, CAS reconciliat/CASS afara),
  1c-PT PART-TIME suprataxare (133811e, CAS+CASS pe baza ridicata la max(brut, sm-facilitate)). Acoperire est ~40-55%.
- Ritual de pornire: agenda_drift curat, agenda arata campania GARDUL DE CONTINUT inchisa (6/6).
- REGULA NOUA de push (decizia c rasturnata 05.08, CLAUDE.md §2.3 pct.8): dupa fiecare executie, sub POARTA VERDE
  (pytest COLLECTED + verificator 0 + tree curat), push pe backup SI main FARA aprobare. Raportul §2.2 sect.11
  confirma HEAD=origin/main=backup pe acelasi commit.

## Campania: 4 puncte, in ordinea data de Costin (NU se schimba fara sa-i spui de ce)
Tiparul uniform (ca la cele 6 garduri de continut): recalcul INDEPENDENT (SQL+formula proprii), non-tautologie
probata pe AST (+ lant TRANZITIV la D112), mutatie obligatorie, HARD-BLOCK la divergenta care numeste ambele valori,
limita de acoperire DECLARATA. Orice valoare fiscala se verifica la sursa (common.cota / act) INAINTE de cod, cu comanda aratata.

### PUNCTUL 1 - D112 cazuri complexe (facilitati/CM/part-time/tichete). Se iau pe rand, ordinea prevalentei; dupa fiecare, cat a crescut acoperirea.
- **1a FACILITATE la minim, toata luna, full-time - LIVRAT (4ad6f72).** baza_contrib=sm-facilitate (S1 fac=300,
  S2 fac=200, verificat common.cota), CAS+CASS. Detectare stabilitate `_stabil_la_minim` (fara schimbare salariu in luna).
  Facilitatea PRORATATA (schimbare in luna) ramane sarita numit. Acoperire ~20-35% -> ~30-45% (est, nemasurat).
  ROTUNJIRE: generatorul tine cas la 2 zec (937.50); D112 EMITE intreg via _d112int (half-up->938); calea 2 confrunta
  valoarea EMISA: `got=_q(g[cas])`, nu int() trunchiere. (core/d112_reconciliere.py)
- **1b TICHETE DE MASA - LIVRAT (63b0865).** angajat peste minim cu tichete de masa: CAS reconciliat (tichetele nu ating baza CAS), CASS NUMIT-AFARA (CASS emis = salarial + cass_tichete, d112.py:239; recalc = tautologie + pontaj). Combo minim+tichete sarit. [istoric analiza:] Analiza facuta: tichetele de masa NU ating baza CAS (salarizare.py: b_imp=b+exces_vac,
  tichetele nu sunt in `b`) -> CAS = baza_contrib x cota_cas E RECONCILIABIL pentru angajatii cu tichete de masa.
  CASS insa creste cu cass_tichete (=nominal tichete x cota_cass) -> CASS pentru ei ramane de acoperit separat.
  Deci 1b poate reconcilia CAS pentru angajatii cu tichete de masa (fara alte beneficii), CASS ramane numit-afara.
  CAVEAT: tichetele cer pontaj CONFIRMAT (d112.pull ridica PerioadaNeconfirmata daca tichet_masa_valoare>0 si pontaj
  neconfirmat) -> fixtura de test trebuie sa confirme pontajul (mecanismul core.perioada.e_confirmat / tabela de
  confirmari - de gasit numele corect, NU e perioade_confirmate). Tichetele de VACANTA au excesul peste plafon anual
  (6 sm) care INTRA in baza (b_imp) -> pe alea CAS se schimba; acopera intai doar tichet de MASA (exces_vacanta=0).
- **1c PART-TIME - LIVRAT (133811e).** suprataxare CF art.146 alin.(5^6): D112 emite CAS/CASS pe baza ridicata
  la max(brut, sm-facilitate). Sub prag -> cas_min_pt/cass_min_pt (dif pe angajator B4_8D/B4_6D); peste prag -> pe brut.
  calea 2 recalculeaza prag=sm-facilitate INDEPENDENT (registru), full month fara CM -> fara proratare/pontaj. Confrunta EMISUL.
- **1c CM - BLOCAT pe DECIZIE DE PRODUS (tura 3, 05.08). PREMISA RETETEI DE MAI JOS E GRESITA - vezi GARZI 05.08 "DESCOPERIRE 1c-CM".**
    Verificat empiric pe generator: poarta cale2 primeste valorile PRE-emisie din pull (salary-only pe brut_lucrat
    proratat, g[cas]=1047.62), NU valoarea EMISA la ANAF (B4_8=4323=salary pe brut intreg + cm_cas). g[cas] NU e emisul
    -> a-l reconcilia = falsa incredere. In plus candidat bug: baza salariala CM difera intre fluturas (proratat) si
    declaratie (brut intreg). Decizie ceruta: (1) baza proratat vs brut intreg; (2) re-arhitectura poarta pe valori emise.
    URMATORUL actionabil fara decizie = Punctul 2. Reteta istorica de mai jos: cotele si rotunjirea (half-even per-cert) raman corecte.
- **[ISTORIC RETETA - premisa g[cas]=emis GRESITA] 1c CM - Sub-caz MARE (scopat 05.08).**
  Motivul opririi acestei sesiuni: buget de context + risc de DIVERGENTA FALSA din rotunjire (vezi mai jos), nu
  dificultate necunoscuta. Toata analiza de mai jos e verificata la sursa; sesiunea noua porneste direct pe cod.

  COTELE (taxe_cm, salarizare.py:562-597, verificat): CAS 25% UNIFORM pe TOATE codurile (CF art.139(1)(o)+140);
  CASS 10% DOAR cod in {01,07,10} (_CM_COD_CU_CASS, art.155(1)i / OUG 34/2024 art.17(2)); impozit 10%. NU importa/apela
  taxe_cm din cale2 (numele e in lista interzisa a test_non_tautologie) - aplica cotele DIRECT din common.cota.

  EMISUL unui angajat cu CM (d112.py, ramura `if cms and zile_cm>0`, ~l.190-210):
    cm_cas  = SUMA per certificat de _d112int((brut_ang+brut_fnuass) x cota_cas)    # 25% pe fiecare cert
    cm_cass = SUMA per certificat de _d112int((brut_ang+brut_fnuass) x cota_cass)   # DOAR cod in {01,07,10}
    cas = _d112int(bazac x cota_cas) + cm_cas ;  cass = _d112int(bazac x cota_cass) + cm_cass
  unde bazac = baza SALARIALA pe zile LUCRATE (nu pe brut intreg): brut_lucrat = brut x (nzl - zile_cm)/nzl,
  bazac = brut_lucrat - facilitate (facilitate 0 daca peste minim). zile_cm = SUMA(zile_ang+zile_fnuass) pe certificate.

  CE TREBUIE IN CALE2 (core/d112_reconciliere.py):
    - relaxeaza skip-ul cm_ids (azi l.~166 sare orice angajat cu CM) DOAR pentru cazul simplu: angajat peste minim,
      full-time, ne-scutit, fara tichete/alte beneficii, CM cod in {01,07,10} (ca sa fie si CASS reconciliabil).
    - capabilitate NOUA: nzl = zile lucratoare holiday-aware. Importa `core.scadente` (NU e in lista interzisa;
      interzise sunt doar salarizare/d112/salariu_istoric) - foloseste zile_lucratoare_luna(an,luna). Verifica pe AST
      ca lantul tranzitiv al scadente NU atinge salarizare/d112 (altfel gaseste alt drum).
    - citeste certificatele: SELECT cod, zile_ang, zile_fnuass, brut_ang, brut_fnuass FROM concedii_medicale
      WHERE salariat_id, an, luna (SQL propriu). exp_cas = _d112int(bazac x cota_cas) + SUMA _d112int((ba+bf) x cota_cas);
      la fel cass (doar cod cu CASS). Confrunta g[cas]/g[cass].

  CAVEAT CRITIC (de ce e MARE): rotunjirea. Generatorul aduna _d112int PER CERTIFICAT apoi sumeaza, si _d112int(bazac x cota)
  SEPARAT. Cale2 TREBUIE sa replice EXACT aceeasi ordine: round(salariu) + SUMA(round(cert_i)), NU round(salariu + total_cm).
  Un round(Σ) in loc de Σ(round) -> DIVERGENTA FALSA de 1-2 lei -> hard-block gresit. Testeaza cu 2 certificate ca sa
  prinzi ordinea. La fel, brut_lucrat proratat: verifica ca formula (nzl-zile_cm)/nzl coincide cu d112.pull:468 (brut_lucrat).

  LIMITA declarata: baza indemnizatiei (brut_ang/brut_fnuass) = INPUT PARTAJAT (§8) - ambele cai o citesc din
  concedii_medicale, o baza gresita acolo nu se prinde. media6 (_cm_media6) e doar pentru afisarea D17/D18, NU pentru
  contributii - cale2 nu are nevoie de ea. Coduri fara CASS (08/09/05 etc.) + defalcarea C2 = xfail-uri separate
  (test_datorie_cm05_subrows, test_datorie_cm_art_xi) - NU le atinge 1c-CM simplu. Verifica OUG 158/2005 la sursa DOAR
  daca extinzi dincolo de aplicarea cotei (procente/plafoane de indemnizatie) - pentru reconcilierea cotei nu e nevoie.

  FIXTURA: rand concedii_medicale (salariat_id, an, luna, cod='01', zile_ang, zile_fnuass, brut_ang, brut_fnuass) pe un
  salariat peste minim. Proba: g[cas] = round(bazac x 25%) + round((ba+bf) x 25%); mutatie pe brut_ang -> pica.

### PUNCTUL 2 - D101 profitul IMPOZABIL (ajustari fiscale). Anual, miza mare.
Azi calea 2 (core/d101_reconciliere.py) acopera doar profitul CONTABIL (P1/P2/P4/P5 din clasele 7/6). Ajustarile
(P6 deduceri, P7, P8 nedeductibile, P10 pierderi reportate) sunt in d101 INTRARI MANUALE ale contabilului (default 0,
d101.py:104-106 + genereaza) -> §8, calea 2 NU le poate recalcula din nimic (nu exista sursa in date). VERIFICA la
sursa (CF art.25 cheltuieli deductibile/nedeductibile, art.26 provizioane/rezerve) CE ajustari CALCULEAZA generatorul
din date (nu manual) - DOAR alea intra in calea 2. Ex. deja calculat de generator: rezerva legala deductibila
(d101.pull ia capital/rezerva_existenta/chelt_impozit din 1012/1061/691 - vezi d101.pull) -> P al rezervei se poate
reconcilia independent din aceleasi conturi. Daca restul ajustarilor raman manuale, SCRIE ca profitul impozabil
ramane pe golden+§8 si calea 2 acopera doar ajustarile COMPUTATE (rezerva legala etc.), nu "D101 impozabil acoperit".

### PUNCTUL 3 - amortizare MF neliniara (degresiva+accelerata). Subsistem propriu.
Temeiuri deja culese: CF art.28 alin.5-8 (eligibilitate pe clasa, coeficienti degresiv 1.5/2/2.5 dupa durata,
accelerata 50% an 1). xfail deja deschis: **test_datorie_mf_metode_amortizare** (ancora). Atinge MF (core/mijloace_fixe
sau d406_active.py) + D101 (amortizare fiscala P11) + D406 AssetTransactions. REGULI ANUALE (schema pe ani,
switch-to-liniar la degresiva cand rata liniara pe durata ramasa depaseste degresiva, prorata an partial). O amortizare
gresita = deducere fiscala eronata in D101 -> nu pe jumatate. Daca prea mare pt un punct: SUB-BLOCAJ motivat (4 elemente
CE/DE CE/CE TREBUIE/URMATOR) si mergi mai departe. VERIFICA art.28 la sursa inainte de cod.

### PUNCTUL 4 - tip_document 2-5 in D394 (borderouri/file carnet/contracte/alte). Ultimul - extindere de contract.
Azi calea auto D394 emite mereu tip_document=1 (facturi), CORECT pt ce se introduce azi. Devine necesar DOAR cand
exista o cale care creeaza operatiuni pe borderou/contract. VERIFICA daca exista o asemenea cale (grep pe
tip_document / borderou / operatiuni manuale d394). Daca NU exista -> spune-o si trateaz-o ca EXTINDERE AMANATA cu
trigger scris in GARZI (ex. "cand apare UI de operatiuni pe borderou"), NU ca datorie deschisa.

### NU e in campanie
Agricultorul forfetar - blocat pe absenta ghidajului ANAF, nu se poate debloca prin munca, ramane exceptie numita.

## Reguli de oprire (Costin)
Oprire DOAR pentru: poarta rosie, tree murdar, esec migrare pe tenant real, sau alegere care schimba ce declara
contabilul si NU rezulta din structura oficiala. Prea mare pt un punct -> sub-blocaj motivat, mergi mai departe.
Raport §2.2 per punct/sub-caz. RAPORT FINAL la sfarsit: acoperire per declaratie inainte/dupa, cifre unde exista,
"nemasurat" unde nu.

## De ce m-am oprit aici (sesiunea 05.08 tura 2)
Oprire §2.3 pct.6 (buget de context) dupa 1b + 1c-PT livrate, la granita curata de commit (133811e). Urmatorul (1c-CM)
e un sub-caz mare (media6 + cod-dependent CASS + fixtura certificat + §8 baza partajata) - a-l incepe risca tree murdar la
mijloc. Registrele (GARZI/DECIZII/TESTE/ISTORIC) la zi pentru 1b si 1c-PT. Firul in TESTE.md arata urmatorul = 1c-CM.
NU e oprire 'ca sa dirijeze Costin' - ordinea o da agenda; e strict buget de context. Analiza CM de mai sus (Punctul 1)
e suficienta ca sesiunea noua sa porneasca direct pe cod.

## [ISTORIC] De ce m-am oprit la 1a (tura 1)
Granita curata de commit (1a livrat+pins). Restul campaniei (1b/1c + P2/P3/P4, mai ales amortizarea neliniara)
e mai mult decat un context; §2.3 pct.6 - oprire la granita curata cu predare, nu start de sub-caz riscand tree murdar.
Registrele (GARZI/DECIZII/TESTE/ISTORIC) sunt la zi pentru 1a. Firul in TESTE.md "In lucru acum" arata urmatorul = 1b.
