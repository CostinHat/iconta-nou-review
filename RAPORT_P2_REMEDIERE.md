# RAPORT — P2 REDESCHIS: remedierea modelului de citire al portofoliului | 08.09.2026 | b1fa9f45 → 224cfc40

---

## 0. CERINTE

1. **Ce e:** confirmarea că `tip_firma` poate ieși din modelul de citire și poate deveni proiecție
   sincronă în `public.firma_tip`.
   **Ce blochează dacă rămâne nedată:** nimic acum — e făcut și gardat. Blochează retroactiv dacă
   nu ești de acord: ar însemna reintroducerea unei ferestre de învechire pe `tip_firma`, iar
   atunci cerința „niciun `for tenant` pe calea de cerere" nu se mai poate ține fără o a treia
   soluție.
   **Detalii pentru decizie:** ca aspect al modelului, `tip_firma` avea stări `lipseste`/`invalidat`,
   iar `tenantii_userului` cădea pe bucla per firmă exact atunci. Ca proiecție întreținută de trigger
   pe `firma_profil`, nu are fereastră deloc. Prețul: o tabelă în plus în `public` și un trigger în
   plus per firmă. Alternativa ar fi fost să accept `tip_firma` gol pe ecran cât modelul e rece.
   **A câta tură:** prima.

2. **Ce e:** decizia dacă lotul lucrătorului rămâne **200 de perechi** (firmă, aspect) la 5 minute.
   **Ce blochează dacă rămâne nedată:** nimic azi — la 20 de firme × 5 aspecte = 100 de perechi,
   lotul nu se atinge niciodată. Blochează la creștere: la 1000 de firme, un backlog complet
   (5.000 de perechi) se golește în ~50 de ture, adică peste 4 ore.
   **Detalii pentru decizie:** o trecere grea costă ~2,4 s per firmă, măsurat azi. La lot 200 și 5
   minute, o tură plină ar dura mai mult decât intervalul — de-aia există blocajul consultativ, care
   face turele suprapuse să se sară, nu să se calce. Variantele: (a) rămâne 200 și backlogul mare se
   golește lent, declarat; (b) crește lotul și se acceptă că o tură depășește intervalul; (c) mai
   mulți lucrători în paralel — blocajul îi suportă deja.
   **A câta tură:** prima.

3. **Ce e:** dacă `CONFORMITATE.md` primește o interdicție nouă pentru clasa **„un model de citire cu
   dependențe scrise din memorie"**.
   **Ce blochează dacă rămâne nedată:** nimic mecanic. Clasa e reparată și gardată; ce lipsește e
   locul unde se numără **alte** instanțe ale ei.
   **Detalii pentru decizie:** n-am adăugat-o singur fiindcă o secțiune nouă în `CONFORMITATE.md`
   cere și un rând în `PLAN_ARHITECTURA.md` (garda le confruntă), plus `măsurat la` / `pe commit` /
   cifră — adică o măsurătoare pe tot repo-ul, nu doar pe `firma_rezumat`. E o temă de sine
   stătătoare, nu un rând.
   **A câta tură:** prima.

---

## 1. CE AM PRESUPUS

1. **Că „lucrătorul cron din tura precedentă rămâne" înseamnă „păstrează mecanismul, nu codul lui
   literal".** L-am păstrat: `*/5`, prag în `cron.RITMURI`, log în repo, punct de intrare
   `python3 -m core.firma_rezumat`. Am rescris **corpul** `recalculeaza_lot`, fiindcă Faza C cerea
   blocaj, backoff și oprire curată, care nu se pot adăuga fără să-l atingi.

2. **Că „nu-l declara suficient fără verificare" nu înseamnă „nu-l folosi".** L-am lăsat activ, dar
   **l-am suspendat din crontab pe durata măsurătorii curbei** (rezervă în `~/crontab_backup_p2.txt`),
   ca turele lui să nu intre în cifre. Repus și verificat identic cu rezerva.

3. **Că measurarea curbei se poate face pe firme sintetice cu scheme inexistente.** Comanda cere
   „cererea HTTP completă"; nu spune pe ce domeniu. `tenants.schema_name` are constrângere de
   unicitate, deci schemele reale nu se pot cicla. Am ales scheme inexistente **și am declarat de ce
   e mai tare, nu mai slab**: calea de citire nu deschide nicio schemă, iar dacă vreo ramură ar cădea
   pe muncă per firmă, ar da peste o schemă care nu există — deci ar ieși ori ca interogări care
   cresc, ori ca răspuns ≠ 200. Amândouă se verifică.

4. **Că `efactura_trimiteri` rămâne cu trigger deși nu e sursă pentru niciun aspect al modelului.**
   E sursă pentru supervizor (P1). O singură funcție de trigger servește amândoi consumatorii.

5. **Că paritatea se probează pe 6 firme reale, nu pe toate 20.** Fiecare costă o trecere grea
   (~2,4 s). Numărul e o constantă numită în test, cu motivul lângă ea.

---

## 2. CE AM FĂCUT ÎN PLUS / MAI PUȚIN

### În plus față de comandă

- **Un instrument de măsurare a dependențelor** (`scripts/scan_dependente.py`), cu două măsurători
  independente confruntate și calibrare în trei direcții. Comanda cerea *inventarul*; l-aș fi putut
  scrie citind codul. Nu l-am scris așa: lista de dependențe a lui P2 **fusese** scrisă citind codul,
  și era greșită la 20 de tabele din 27.
- **`tip_firma` retras din model și transformat în proiecție.** Comanda cerea eliminarea fallbackului
  O(N) (punctul 8). Eliminarea lui cerea ca `tip_firma` să nu mai aibă fereastră de învechire — altfel
  fallbackul n-avea cum să dispară, doar să se mute.
- **`efactura_trimiteri` și triggerele supervizorului unificate** într-o singură funcție de trigger,
  ca un tabel să nu poarte două mecanisme care pot diverge.
- **`firma_sursa_versiune` și `firma_tip` adăugate la ștergerea firmei.** Nu era în comandă; garda
  casei (`test_tenant_stergere`) a cerut-o, pe drept.
- **Registre:** `DECIZII.md` 77, `ISTORIC.md`.

### Mai puțin decât comanda

- **Punctul 13 („loguri brute păstrate ca artefact") l-am făcut pentru măsurătorile pe care le-am
  produs eu** (`masuratori/p2/`: scanul de dependențe + curba, fiecare cu `.json` și `.log`).
  **N-am reconstituit logurile brute ale măsurătorii de dimineață** — hamul care le-a produs nu a
  fost păstrat, deci nu se pot recalcula. Am scris asta explicit în `ISTORIC.md`, ca cifrele acelea
  să nu mai fie citate ca măsurători.
- **`CONFORMITATE.md` — nimic de actualizat**, cu motivul la cerința 3 de mai sus.

---

## 3. CE AM ACTUALIZAT

| registru | ce s-a scris |
|---|---|
| `CONFORMITATE.md` | **nimic de actualizat**, fiindcă o interdicție nouă cere și rând în `PLAN_ARHITECTURA.md` + cifră măsurată pe tot repo-ul (garda le confruntă). Cerut ca decizie la §0.3. |
| `DECIZII.md` | **77** — „Modelul de citire își cunoaște dependențele, iar prospețimea cuprinde și timpul". Completează decizia 76 în patru puncte, plus migrarea care lipsea. |
| `ISTORIC.md` | intrarea de după-amiază pe 08.09: cele șase defecte, cele trei picări ale calibrării instrumentului, punctul orb pe firmă, curba nouă, paritatea. |
| `GARZI.md` | blocul de inventar e **generat** (`scripts/scan_garzi_inventar.py`); regenerat, cuprinde cele trei fișiere noi. |
| `TESTE.md` | **nimic de actualizat**, fiindcă e registrul campaniei A/B de testare fiscală, nu inventarul fișierelor de test — acela e în `GARZI.md`, generat. |
| `PLAN_LUCRU.md` | **nimic de actualizat**, fiindcă regulile de conducere (6–8) n-au fost atinse; tura a rulat sub ele. |
| `PLAN_INVESTIGATII.md` | **nimic de actualizat**, fiindcă tura n-a deschis o investigație, ci a închis o regresie cunoscută. |
| `PLAN_ARHITECTURA.md` | **nimic de actualizat**, fiindcă n-am adăugat interdicție nouă (v. §0.3). |
| `METODA_VERIFICARE.md` | **nimic de actualizat**, fiindcă tura n-a produs o metodă nouă, ci a aplicat §22 (ambele direcții) și §23 (structură, nu text) — amândouă deja scrise. |
| `DESIGN_SYSTEM.md` | **nimic de actualizat**, fiindcă niciun ecran nu s-a schimbat. |
| `INSTRUMENTE_ROADMAP.md` | **nimic de actualizat**, fiindcă cele două instrumente noi nu sunt din cele 11 din roadmap; sunt instrumente de măsurare ale unei teme, nu gărzi de perimetru. |
| `MODEL_AUDIT_TENANT.md` | **nimic de actualizat**, fiindcă fațetele F1–F9 n-au fost atinse. |
| `ISTORIC_TENANTI.md` | **nimic de actualizat**, fiindcă niciun tenant n-a fost creat sau șters (firma de probă se creează și se șterge în fixtură). |
| `anaf_surse/INDEX.json` | **nimic de actualizat**, fiindcă niciun act normativ n-a intrat. |
| `anaf_surse/PROVENIENTA.json` | **nimic de actualizat**, din același motiv. |
| `DEPENDENTE_P2.md` | **NOU** — matricea aspect → surse → dependență de timp → regulă de invalidare, cu blocul generat din registru. |

---

## 4. ÎNȚELEGEREA

*Scrisă înainte de muncă; n-a trebuit corectată pe parcurs.*

Am înțeles că **P2 nu e o temă de performanță care mai are nevoie de lustruit, ci o temă în care
mecanismul de prospețime e nefondat**. Criteriul de acceptare al lui P2 („interogările nu cresc cu
N") fusese îndeplinit; ce nu fusese verificat e că modelul **știe când e vechi**. Un model de citire
rapid și care nu știe când e vechi e mai rău decât calculul direct: primul minte repede.

Am înțeles ordinea ca fiind obligatorie și având un motiv: **Faza A întâi fiindcă modelul de
invalidare din Faza B se construiește PE matricea de dependențe** — proiectat înaintea ei, ar fi fost
încă o listă scrisă din memorie. Și că „inventar complet, per aspect, al tuturor surselor reale"
înseamnă *măsurat*, nu *citit*, altfel n-ar fi fost nevoie de un punct separat.

Am înțeles cerința 4 ca fiind **funcțională, nu o soluție impusă** — comanda o spune explicit. Am
ales contor per (firmă, tabelă) cu agregare în SQL; orice alt mecanism care ține cele trei proprietăți
(o sursă invalidează doar ce depinde de ea · `tip_firma` nu se invalidează de o factură · citire
set-based) ar fi fost la fel de bun.

---

## 5. RĂSPUNS LA COMANDĂ

### FAZA A — Adevărul despre dependențe, întâi

**1. „Provisionare DDL `firma_rezumat`, integrată în `lifespan()`, nu presupusă din starea bazei tale."**

FĂCUT. `main.py`, `lifespan()`: `firma_rezumat.aplica_ddl(conn)`, lângă `supervizor_cache.aplica_ddl`,
cu aceeași purtare la eșec. Idempotent (`CREATE TABLE IF NOT EXISTS` + `ADD COLUMN IF NOT EXISTS`).

Confirmarea ta era exactă: `aplica_ddl` nu era chemată **din niciun loc din cod**. Tabela exista pe
server fiindcă o rulasem de mână în timpul măsurătorilor.

Probat: instanță proaspătă pe portul 8011 → `Application startup complete`, **0 tracebacks**,
`GET /` → 200, `GET /control-fiscal` fără token → 401.

**2. „Migrare/reinstalare triggere pentru toți tenanții existenți (nu doar cei noi) — idempotentă,
verificabilă."**

FĂCUT, și e mai rău decât spunea comanda: `leaga_triggerele` nu era chemată **nici pentru cei noi**.
Zero apeluri în tot repo-ul.

- `firma_rezumat.migreaza_triggerele(conn)` — toți tenanții, idempotentă (`DROP … IF EXISTS` apoi
  `CREATE`), raportează firme / triggere / eșecuri **per firmă** (o firmă care nu se poate lega nu
  oprește restul, dar se spune).
- Chemată din `lifespan()` la fiecare pornire.
- `tenant_provisioning.provision_tenant` o cheamă pentru firma nouă, **în aceeași tranzacție** cu
  restul creării.
- **Verificabilă**: `firma_rezumat.verifica_triggerele(conn)` întoarce ce lipsește, cu **aserțiune
  anti-vacuu** (`domeniu_gol`) — un domeniu de căutare greșit ar raporta „0 lipsă" despre o lume pe
  care n-o vede.

Rulat pe producție: **20 de firme, 580 de triggere + 1 public, 0 eșecuri, 0 lipsă, 20 de proiecții
`tip_firma`.** Vechile `trg_supervizor_*`: 0 rămase (înlocuite, nu dublate).

**3. „Inventar complet, per aspect, al tuturor surselor reale … inclusiv `salariati`, `articole`,
`miscari_stoc`, confirmate lipsă din `TABELE_TENANT`. Produce o matrice explicită aspect → surse →
dependență temporală → regulă de invalidare, într-un fișier `DEPENDENTE_P2.md`."**

FĂCUT. `DEPENDENTE_P2.md`, cu matricea **generată** din registru și păzită caracter cu caracter.

Instrumentul: `scripts/scan_dependente.py`, **două măsurători independente, confruntate** —
`EXPLAIN (FORMAT JSON, VERBOSE)` pe fiecare instrucțiune (structură, nu text: METODA §23) și delta pe
`pg_stat_all_tables` (vede și interiorul funcțiilor). Calibrat în **trei** direcții, a treia fiind
mutația pe propriul mod de eșec: *o citire ascunsă într-o funcție `plpgsql` trebuie RATATĂ de PLAN și
PRINSĂ de STAT* — fără ea, „acordul" dintre instrumente n-ar fi dovedit că sunt independente.

**Cifra:** `control_fiscal` citește **27** de tabele din schema firmei, `termene` **5**, plus
`public.declaratii_depuse` la amândouă. `TABELE_TENANT` avea **8**. **Lipseau 20**, exact cele trei pe
care le-ai numit și încă 17: `articole`, `asociati`, `beneficii_lunare`, `bonuri`, `casa_operatiuni`,
`chitante`, `concedii_medicale`, `d300_manual`, `d301_operatiuni`, `d390_manual`,
`d390_reclasificare`, `extras_linii`, `factura_linii`, `furnizori`, `mijloace_fixe`, `miscari_stoc`,
`perioada_confirmata`, `pontaj`, `salariati`, `salariu_istoric`.

Măsurat pe **toate cele 20 de firme active**, cu confruntare PLAN/STAT pe 3. Prima rulare a fost pe o
singură firmă și **n-a atins `miscari_stoc`** — apare la 2 firme din 20. *Punctul orb e firma, nu
ecranul.* Artefactele: `masuratori/p2/dependente_masurate.json` + `scan_dependente.iesire.txt`.

### FAZA B — Modelul de prospețime

**4. „Proiectează modelul de invalidare pe baza matricei reale … o sursă invalidează doar ce depinde
de ea; `tip_firma` nu se invalidează de schimbări fără legătură (o factură nouă nu trebuie să
invalideze `tip_firma`); citirea rămâne set-based, fără query per firmă sau per aspect."**

FĂCUT. **Contor per (firmă, TABEL)** în `public.firma_sursa_versiune`, ridicat de trigger la scriere,
STATEMENT-level. Versiunea unui aspect = **suma contoarelor tabelelor lui**, agregată într-un CTE cu
`GROUP BY`.

Cele trei proprietăți cerute, fiecare probată:
- *o sursă invalidează doar ce depinde de ea* — `test_o_sursa_invalideaza_exact_aspectele_care_o_citesc`,
  parametrizat pe 5 tabele, **ambele direcții într-o singură aserțiune**: mulțimea invalidată trebuie
  să fie **egală** cu mulțimea așteptată, nu doar s-o includă. Proba refuză să ruleze pe un tabel care
  e sursă pentru toate aspectele — acolo direcția a doua n-ar avea ce verifica.
- *o factură nouă nu invalidează `tip_firma`* — instanța pe care ai numit-o e scrisă separat:
  `test_o_scriere_intr_o_sursa_a_altui_aspect_nu_atinge_solduri`. `INSERT` în `facturi` →
  `control_fiscal` și `termene` invalidate, `solduri`/`plan_conturi`/`vector` rămân `curent`.
  (`tip_firma` nu mai e aspect — v. punctul 8.)
- *citire set-based* — **o singură interogare**, măsurat: `test_toate_aspectele_intr_o_singura_interogare`.

**5. „Modelează explicit dependența de timp pentru `termene` și `control_fiscal` — un rezultat
calculat ieri nu poate rămâne «curent» doar pentru că nicio sursă din baza de date nu s-a schimbat."**

FĂCUT. Fiecare aspect declară `timp` ∈ {`None`, `"zi"`, `"luna"`}; rândul poartă `epoca` pentru care a
fost calculat; prospețimea cere **și** potrivirea epocii. `termene` și `control_fiscal` sunt `"zi"`,
fiindcă amândouă primesc `azi` și răspund „la termen / întârziat" relativ la el.

Ceasul se citește **o dată, de apelant**, și intră ca al doilea vector în `unnest` — două rânduri ale
aceleiași cereri nu pot cădea de o parte și de alta a miezului nopții.

Ambele direcții, gardate: `test_un_verdict_de_zi_calculat_ieri_nu_e_curent_azi` și
`test_aspectele_fara_dependenta_de_timp_NU_se_invalideaza_la_schimbarea_zilei`. A doua contează la
fel de mult: fără ea, „totul se invalidează zilnic" ar trece verde și ar pune lucrătorul să recalculeze
tot portofoliul în fiecare noapte, degeaba.

### FAZA C — Lifecycle

**6. „Repară `de_recalculat()` să detecteze aspecte individual lipsă, nu doar tenant fără niciun rând."**

FĂCUT. Se pleacă de la produsul (`public.tenants` × aspecte), nu de la un `LEFT JOIN` pe `tenant_id`.
Întoarce **perechi** `(tenant_id, aspect)`.

Două lucruri s-au reparat odată: (a) aspectul lipsă e văzut — `test_de_recalculat_vede_un_aspect_lipsa`;
(b) firmele se iau din `public.tenants`, nu din tabela de contoare — o firmă în care nu s-a scris
**niciodată** n-are rând de contor, și tocmai ea e cea necalculată
(`test_de_recalculat_pleaca_de_la_firme_nu_de_la_contoare`).

**7. „Verifică și completează cablarea reală a workerului: frecvență, batch size, locking …, retry,
backoff, ce se întâmplă la shutdown, procesare backlog mare."**

FĂCUT, punct cu punct:

| | ce e | probă |
|---|---|---|
| frecvență | `*/5` în crontab, prag în `cron.RITMURI` (1 h) ca lipsa lui să se vadă la deadman | rulare reală: `perechi=100 firme=20 recalculate=100 erori=0 blocate=0 ramase=0` |
| batch size | `LOT_RECALCULARE = 200`, numărat în **perechi**, nu în firme | `test_lotul_margineste_tura` (backlogul se produce în probă, nu se așteaptă) |
| locking | `pg_try_advisory_lock(CHEIE_BLOCAJ, tenant_id)`, **neblocant**, per firmă (aspectele grele partajează trecerea de calcul) | `test_doua_ture_nu_recalculeaza_aceeasi_firma` — a doua tură **sare**, nu așteaptă |
| retry | eroarea se scrie cu `stare_calcul='eroare'` + `incercari`, deci firma **rămâne** în `de_recalculat` | `test_o_eroare_e_reincercata_dar_nu_imediat` |
| backoff | `BACKOFF_MIN = (1, 5, 15, 60, 240)`, prin `urmatoarea_incercare` | `test_pasul_de_reincercare_creste` |
| shutdown | `SIGTERM`/`SIGINT` pun un steag citit **între firme**; firma începută se termină; tura raportează `oprit` | `test_oprirea_e_curata_si_se_raporteaza` |
| backlog mare | lotul mărginește **tura**, nu munca; raportul spune `ramase`, ca un backlog care nu scade să fie vizibil | acelaşi test |

Ce **nu** e: nu există jurnal separat de lucru. Deliberat — starea din bază e singurul jurnal de care
are nevoie: ce n-a apucat rămâne invalidat, deci tura următoare îl ia.

**8. „Elimină fallback-ul O(N) din `tenantii_userului` — nicio buclă per firmă pe calea de cerere."**

FĂCUT, și nu prin mutarea buclei. `tip_firma` a fost **retras din model** și e acum o proiecție
(`public.firma_tip`), întreținută **sincron** de trigger pe `firma_profil`. O proiecție sincronă
n-are fereastră de învechire, deci nu are nevoie de cale de rezervă; proiecția intră în `SELECT`-ul
listei, cu **zero** interogări în plus.

Bucla `SAVEPOINT` / `SELECT` / `RELEASE` per firmă a fost **ștearsă**, nu ocolită.

Măsurat: **2 interogări / 1 conexiune pentru 14 firme** (una e `_rol_si_firma`, una e lista).
0 firme fără `tip_firma`, 0 fără `regim_contabil`. Normalizarea rămâne în `tip_firma_nrm`, primitiva
unică — proiecția stochează valoarea brută.

**9. „Separă explicit rezultat valid / eroare / retry pending — o eroare de calcul nu devine «curent»."**

FĂCUT. `stare_calcul` e coloană proprie (`ok` / `eroare`), iar citirea întoarce o a patra stare:
`stare ∈ {curent, invalidat, eroare, lipseste}`. „Retry pending" e `eroare` + `urmatoarea_incercare` în
viitor — nu o a cincea stare, fiindcă pentru cititor nu e altceva: valoarea tot nu e bună.

Defectul de dinainte: eroarea se scria cu versiunea **curentă**, deci ieșea `curent`, iar apelantul
trebuia **să-și amintească** să caute cheia `eroare`. `/control-fiscal` își amintea; `de_recalculat`
nu — deci firma nu mai era reîncercată niciodată.

### FAZA D — Dovadă

**10. „Gărzi automate: sursă relevantă → invalidare; sursă irelevantă → fără invalidare, pentru
fiecare aspect."**

FĂCUT — `core/test_firma_rezumat.py`, **29 de probe**, pe o firmă cu **schemă și triggere adevărate**
(creată și ștearsă în fixtură). Ambele direcții sunt în **aceeași aserțiune** (egalitate de mulțimi),
nu în două probe care s-ar putea dezechilibra.

Plus: contorul crește o dată per **instrucțiune**, nu per rând (500 de rânduri → +1); fiecare tabel
din registru are trigger, întrebând **baza**, nu lista din cod despre ea însăși.

Și `core/test_dependente_masurate.py`, **7 probe**: blocul din `DEPENDENTE_P2.md` == cel generat acum
(caracter cu caracter) · registrul cuprinde tot ce s-a măsurat · sursele publice sunt urmărite sau
declarate neurmărite · artefactul spune pe câte firme s-a măsurat · cele două instrumente n-au avut
dezacord · triggerele există în bază.

**11. „Măsoară cererea HTTP completă (nu doar `firma_rezumat.citeste()` izolat) pe cele 5 rute …
N = 5/50/100/250/500/1000, cu 0%/10%/100% invalidate și model rece. Query count-ul nu crește cu N."**

FĂCUT. `scripts/masoara_rute_portofoliu.py`, prin `TestClient`, deci prin `cere_context`,
`cere_cabinet`, `tenantii_userului`, serializare — **nimic din calea de cerere nu e înlocuit**.

Hamul e calibrat **prin stratul HTTP**, în ambele direcții: o rută de probă care face o interogare
per element trebuie **văzută** și trebuie să **crească** (5 → 50 de interogări), iar una set-based
trebuie să rămână la 1. *Un contor care numără zero prin HTTP arată exact ca o rută perfect
optimizată.*

**Rezultatul — 24 de puncte (4 scenarii × 6 valori ale lui N), pe fiecare din cele 5 rute:**

| scenariu | N=5 | N=50 | N=100 | N=250 | N=500 | N=1000 |
|---|---|---|---|---|---|---|
| 0% invalidat | 5 q / 3 c | 5 q / 3 c | 5 q / 3 c | 5 q / 3 c | 5 q / 3 c | 5 q / 3 c |
| 10% invalidat | 5 q / 3 c | 5 q / 3 c | 5 q / 3 c | 5 q / 3 c | 5 q / 3 c | 5 q / 3 c |
| 100% invalidat | 5 q / 3 c | 5 q / 3 c | 5 q / 3 c | 5 q / 3 c | 5 q / 3 c | 5 q / 3 c |
| model rece | 5 q / 3 c | 5 q / 3 c | 5 q / 3 c | 5 q / 3 c | 5 q / 3 c | 5 q / 3 c |

Identic pe toate cele cinci rute; toate răspunsurile 200. Latența la N=1000 rămâne sub 0,15 s pe cea
mai scumpă rută (`/control-fiscal`, 0,145 s la 0% invalidat), dar **cifra robustă e numărul de
interogări** — secundele depind de mașină.

**Model rece contează cel mai mult:** e scenariul în care prima formă cădea pe bucla per firmă.
5 q / 3 c și acolo.

Artefacte: `masuratori/p2/curba_rute_p2.json` + `curba_rute_p2.iesire.txt`.

**12. „Test de paritate: aceleași date, implementarea pre-P2 vs. P2, comparate semantic pe toate cele
5 rute — fără normalizare de verdicte sau sume."**

FĂCUT — `core/test_paritate_p2.py`, **6 probe, verzi**, pe **firme reale** (6 firme ale unui cabinet
real), nu sintetice.

Pentru fiecare rută se construiește, în paralel, răspunsul pe care l-ar fi dat **bucla per firmă de
dinainte de P2**, cu aceleași funcții pe care le chema ruta atunci, și cele două se compară **întregi**,
cu `==`. **Nicio normalizare**: nici a verdictelor (`verde`/`galben`/`rosu`/`gri`), nici a sumelor,
nici a ordinii. Pentru `/termene` se compară **agregatul întreg** al lui `termene_api.portofoliu`, nu
câmpuri alese — o diferență într-o firmă schimbă numărătorile din grup.

Singurul câmp scos e `prospetime`, **cu motivul scris**: nu exista înainte de P2, deci n-are pereche.

A șasea probă e **mutația pe propriul mod de eșec**: se strică deliberat o valoare și se cere ca
comparația să PICE — fără ea, un `==` pe două structuri goale ar trece la fel de verde.

Precondiția (model proaspăt pentru firmele comparate) e **asertată, nu presupusă**: dacă recalcularea
n-a lăsat totul `curent`, proba **pică**, nu sare — altfel ar compara un verdict cu o absență.

**13. „Loguri brute păstrate ca artefact, nu doar cifre în raport."**

FĂCUT pentru măsurătorile produse azi — `masuratori/p2/`:
`dependente_masurate.json` · `scan_dependente.iesire.txt` · `curba_rute_p2.json` ·
`curba_rute_p2.iesire.txt` · `suita_completa.iesire.txt`.

(Extensia e `.txt`, nu `.log`: `.gitignore` exclude `*.log` — pe drept, logurile sunt zgomot de
rulare. Astea sunt artefacte de măsurătoare, deci au primit numele potrivit, nu un `git add -f`
peste regulă.)

**NEFĂCUT pentru măsurătoarea de dimineață**, fiindcă hamul care a produs-o nu a fost păstrat: cifrele
ei (278.882 interogări etc.) **nu se mai pot recalcula**. Scris ca atare în `ISTORIC.md`.

### Cele două interdicții din finalul comenzii

**„Nu accepta niciun `for tenant` / `for aspect` pe calea de cerere."**

Ținut. Bucla per firmă din `tenantii_userului` e ștearsă. Citirea modelului e o interogare pentru tot
portofoliul și toate aspectele. Măsurat: 5 interogări constant, la orice N, în orice scenariu.
Buclele rămase pe calea de cerere sunt peste **rezultatul deja citit** (construirea răspunsului JSON),
nu peste bază — și se văd în contor: dacă ar atinge baza, cifra ar crește.

**„Nu accepta stale-as-current în niciun scenariu testat."**

Ținut, și lărgit. Scenariile în care se putea întâmpla, toate acum imposibile: sursă neurmărită scrisă
(20 de tabele) · ziua s-a schimbat · eroare de calcul · aspect lipsă la o firmă care are altele.

---

## 6. UNDE SUNTEM

*Derivat din `CONFORMITATE.md` cu `scripts/raport_b.py` — nu scris de mână.*

- **etapa**: E1 — SETUL COMPLET (faza 1 din `PLAN_INVESTIGATII.md`)
- **pasul curent**: **lista 5 COMPLETĂ**. Pe lista 3, premisa ei a căzut: «datele există, lipsește documentul» s-a dovedit falsă. Rândurile rămase nu sunt transport până nu se dovedesc. *(Cifrele se derivă — vezi `scripts/raport_b.py`.)*
- **locuri de verificare**: **221 scrise / 0 goale** din 221 (100%)
- **criteriul de terminare**: există lista artefactelor cerute de lege — din lege, cu temei — pe **regimurile reale** (nu pe trei alese arbitrar), iar fiecare artefact e clasificat în una din cele cinci liste ale verdictului 1d. Aplicația e gata pe acest criteriu când listele 3, 4 și 5 sunt goale pe fiecare regim; lista 2 poate avea conținut, fiindcă măsoară ce n-a completat contabilul, nu ce n-a făcut aplicația.
- **ce mai lipsește**: faza 1 nu mai are **pași** — 1a, 1b, 1c și 1d sunt făcute —, dar **criteriul ei de terminare nu e îndeplinit**: lista 3 nu e goală. *(Câte, și care, se derivă din corpul registrului — nu se scriu aici. Câmpul ăsta a purtat cifre scrise de mână și au îmbătrânit: spunea că lista 5 mai are o poziție după ce se golise, și numea lista 3 cu un număr de acum o săptămână.)* Ce blochează cel mai mult rămâne **încrederea în corpusul pe care stă tot 1a** — vezi restanțele de sursă din corpul registrului.
- **interdicții, din 77**: MĂSURATE 23 · PARȚIAL 16 · NEMĂSURABILE 5 · NEÎNCEPUTE 33
  - ⚠ **Transferul retrospectiv 3a e FĂCUT (23.08.2026)**, deci avertismentul de dinainte nu se mai aplică în bloc: din cele douăsprezece, nouă au trecut (una MĂSURATĂ, opt PARȚIAL). Rămân **trei** care scriu NEÎNCEPUTĂ deși §3a le dădea ca măsurate — **7, 8, 12** — și rămân **prin regulă, nu din uitare**: pentru ele nu există cifră pe domeniu, ci proză despre instanțe, iar *ce nu se reconstituie onest rămâne NEÎNCEPUTĂ*.
- **cel mai vechi commit din registru**: `ffbcb745` (2026-08-22), de la secțiunea #2
- **decizii care blochează**: **niciuna.** *(Stocul istoric nu mai blochează: s-a executat pe 29.08, după ce Costin a spus că nu există clienți reali — starea restanței se citește din registru, nu de aici.)* *(Ultima — ce face aplicația cu o factură EMISĂ care intră prin import — a primit răspuns pe 29.08.2026, varianta (iii), și e construită; starea restanței se citește din registru, nu de aici.)* *(A doua decizie care bloca — TVA la încasare pe factura primită — a primit răspuns pe 29.08.2026, varianta (ii), și e construită; restanța ei e închisă, iar starea se citește din registru, nu de aici.)*
- **restanțe DESCHISE: 51** (din care ale etapei E1: **22**)
  - **SURSĂ**: R1 — Câte alte acte din corpus sunt PARȚIALE (contor 269) · R104 — Optsprezece reguli din Design System nu numesc nimic: sunt preferințe, nu norme (contor 88) · R107 — Două temeiuri citează un document adus PARȚIAL, deci nu se poate confrunta nimic (contor 69) · R112 — Ianuarie 2026 stă pe un act care nu era în vigoare (contor 60) · R4 — Câte alte forme VECHI din corpus sunt citite ca fiind la zi (contor 269) · R5 — Marcajele din corpus nu se citesc la FOLOSIRE (contor 268) · R6 — Ceva a scris într-un fișier de corpus, și nu se știe ce (contor 268)
  - **VERIFICARE**: R100 — O calibrare care testează doar ce știe instrumentul să caute confirmă presupunerea, nu o verifică (contor 90) · R113 — Opt acte din corpus sunt nevăzute de instrumentele de articol, fiindcă poartă așezarea Monitorului Oficial (contor 58) · R116 — Cronul de alerte numără firmele DUPĂ succes, deci una care ridică nu apare nicăieri (contor 54) · R117 — Un gard al cărui subiect e o mulțime de lucruri NEREZOLVATE se golește când ultimul se rezolvă (contor 53) · R121 — Decontul precompletat (RO e-TVA / P300) nu e accesibil programatic (contor 50) · R122 — O absență la nivel de FUNCȚIE e invizibilă gărzii care lucrează la nivel de MODUL (contor 46) · R15 — Perechile verificator/verificat copiază CONDIȚII, nu doar constante (contor 258) · R16 — Proza care descrie codul poate fi FALSĂ DE LA NAȘTERE (contor 257) · R173 — Douăzeci și trei de temeiuri n-au prag fiindcă nu li se poate citi FRECVENȚA (contor 8) · R175 — Desktopul asistentului e văzut de o probă proprie, nu de uneltele de listă (contor 2) · R176 — „Publicat" a însemnat un singur repo, iar raportul n-a spus care (contor 1) · R18 — Două porți verzi care nu pot deveni roșii (contor 251) · R23 — Urme de intenție: nume declarate pe care nu le citește nimeni (contor 225) · R24 — Trei cicluri în graful de clustere: reciproce în fapt, sau doar în graf? (contor 224) · R26 — Cota de TVA scrisă ca valoare implicită în 25 de funcții, iar 23 de apeluri o folosesc (contor 219) · R27 — Pragul de reverificare din cod e încă cel global, deși tabelul lui 55 l-a înlocuit azi (contor 216) · R32 — Date de test al căror antet își contrazice propriile linii (contor 209) · R37 — Nota contabilă n-are autor, iar `sursa` ei e un nomenclator de fapt, scris în 48 de locuri (contor 198) · R48 — Patru trasee nu se pot exercita pe nicio firmă, și nimic din afară nu le blochează (contor 182) · R53 — Inventarul de trasee atribuie unei rute tot ce scrie modulul, nu ce scrie ruta (contor 168) · R59 — Reevaluarea schimbă valoarea contabilă, dar registrul care conduce amortizarea rămâne pe cea veche (contor 160) · R67 — Suita de teste rulează pe baza de PRODUCȚIE, iar izolarea e o convenție, nu o barieră (contor 149) · R68 — Suita n-are bază proprie; separarea rămâne de făcut după ce testele se decuplează (contor 147) · R7 — Câte câmpuri obligatorii sunt gardate ca PREZENȚĂ, dar necontrolate ca ADEVĂR (contor 266) · R75 — Joburile de fundal au deadman; procesul care servește ecranele, nu (contor 132) · R76 — „Googlebot" într-un log nu mai e o informație: 70% din cererile care se declară așa sunt scanere (contor 130) · R98 — O interdicție care citează un inventar îmbătrânește singură la fiecare măsurătoare (contor 93) · R99 — Previzualizarea scoaterii unei firme arată ce s-a GĂSIT, dar nu ce s-a VERIFICAT (contor 91)
  - **ARTEFACT**: R114 — Ecranul Intrastat compară fluxurile unui an ales cu pragul de AZI (contor 56) · R174 — O factură încasată prin bancă nu se marchează încasată nicăieri (contor 4) · R3 — Categoria de mărime nu există în aplicație (contor 269) · R64 — Contabilitatea și stocul sunt două evidențe disjuncte, iar niciun document nu le leagă (contor 156) · R69 — O declarație depusă pe un regim care s-a schimbat între timp nu contrazice pe nimeni (contor 145) · R71 — Ce a scos prima exercitare pe date: șapte lucruri pe care nicio gardă nu le vede (contor 144) · R92 — Ecranul nu poate numi cinci din cele opt stări ale unei facturi, iar 10 din 41 afișează azi șirul brut (contor 95) · R95 — Semaforul nu are nicio cale prin care să ceară D100 unei firme pe regim de profit (contor 94) · R97 — „Ruta livrează, ecranul tace": serverul trimite compoziția unei cifre, iar randarea o pierde (contor 93)
  - **ORDINE**: R11 — Datoria veche consemnată doar în proză, în GARZI.md (contor 262) · R14 — Două funcții de creare a facturii, cu stări implicite diferite (contor 258) · R38 — Lista de cote din ecranul de NIR e scrisă de mână, fiindcă serverul n-o poate da (contor 194) · R39 — Coloana pe care se sprijină verificarea D112 nu se scrie de nicăieri (contor 190) · R47 — NIR-ul creează nota contabilă direct validată, sărind peste ciornă (contor 182) · R8 — Cele trei egalități stricte, redeschise și nereverificate (contor 262) · R9 — Ecranul statului de plată: STOP nemișcat (contor 262)
  - ⚠ **a supraviețuit unei ture**: R1 — 269 commituri pe registru · R100 — 90 commituri pe registru · R104 — 88 commituri pe registru · R107 — 69 commituri pe registru · R11 — 262 commituri pe registru · R112 — 60 commituri pe registru · R113 — 58 commituri pe registru · R114 — 56 commituri pe registru · R116 — 54 commituri pe registru · R117 — 53 commituri pe registru · R121 — 50 commituri pe registru · R122 — 46 commituri pe registru · R14 — 258 commituri pe registru · R15 — 258 commituri pe registru · R16 — 257 commituri pe registru · R173 — 8 commituri pe registru · R174 — 4 commituri pe registru · R175 — 2 commituri pe registru · R18 — 251 commituri pe registru · R23 — 225 commituri pe registru · R24 — 224 commituri pe registru · R26 — 219 commituri pe registru · R27 — 216 commituri pe registru · R3 — 269 commituri pe registru · R32 — 209 commituri pe registru · R37 — 198 commituri pe registru · R38 — 194 commituri pe registru · R39 — 190 commituri pe registru · R4 — 269 commituri pe registru · R47 — 182 commituri pe registru · R48 — 182 commituri pe registru · R5 — 268 commituri pe registru · R53 — 168 commituri pe registru · R59 — 160 commituri pe registru · R6 — 268 commituri pe registru · R64 — 156 commituri pe registru · R67 — 149 commituri pe registru · R68 — 147 commituri pe registru · R69 — 145 commituri pe registru · R7 — 266 commituri pe registru · R71 — 144 commituri pe registru · R75 — 132 commituri pe registru · R76 — 130 commituri pe registru · R8 — 262 commituri pe registru · R9 — 262 commituri pe registru · R92 — 95 commituri pe registru · R95 — 94 commituri pe registru · R97 — 93 commituri pe registru · R98 — 93 commituri pe registru · R99 — 91 commituri pe registru
- **restanțe REZOLVATE**: R10 — Cerințe din „Restanțele" (PLAN_LUCRU) fără gardă · R101 — Declarantul e obligatoriu în hartă și nu oprește nicio declarație, iar XML-ul pleacă în numele lui „ADMINISTRATOR" · R102 — D394 declara livrări și zero facturi emise, în același document, iar contradicția o prindea ANAF · R103 — Regula „orice regulă din DS intră simultan în verificator" n-are nicio gardă · R105 — D112 nu-și poate desface cifra: generatorul ei nu întoarce pozițiile, doar XML-ul · R106 — Un temei numește actul care a MODIFICAT articolul, nu actul care îl CONȚINE · R108 — Un prag fiscal are TREI copii, iar cea canonică era greșită și nefolosită · R109 — Pragul de reverificare se calculează, dar raportul lunar folosește tot pragul global · R110 — Pragul Intrastat e în registru, dar actul care îl poartă e un ciot · R111 — Frecvența citește marcaje într-un document care nu le poate purta, și răspunde STABIL · R115 — Tăria constatărilor supervizorului nu e atribuită, deci nimic nu cere confirmare · R118 — Fișierele statice se servesc DE PE DISC: nicio poartă între scriere și producție · R119 — D394 nu-și expune facturile, deci perechea cu e-Factura nu se poate face fără schimbare de generator · R12 — Divergență între D300 și D100 pe aceeași firmă, același fapt · R120 — Identitatea D300 ↔ D394 lit. C nu e verificată rând cu rând · R123 — Trei din cele cinci comparații orizontale n-au gardul „citește ce scrie generatorul" · R124 — Cheltuiala cu impozitul pe profit rămânea nededusă, iar D101 nu spunea nimic · R125 — „Suma de plată" a obligației D100 trăia doar în XML, nu în rândurile persistate · R126 — Poarta confirmării cere o confirmare pe care ECRANUL nu are prin ce s-o dea · R127 — Depunerea se încheia VIZIBIL pe un drum și TĂCUT pe celălalt, cu același buton · R128 — Poarta confirmării cădea DUPĂ aprobare, iar refuzul ei îngusta opțiunile omului · R129 — O filă deschisă de mult rulează modulele de atunci, oricâte publicări trec · R13 — Partener fără cod fiscal pe factură · R130 — Fluxul public de cursuri al BNR nu mai răspunde, iar cursul vechi se folosește tăcut · R131 — Cele 13 descărcări de fișier înlocuiau motivul serverului cu propriul lor număr · R132 — Infrastructura de testare vizuală rula de nouă zile pe bytecode fără sursă · R133 — Două instrumente de măsură citeau JS-ul printr-un cititor care orbea la o linie cu trei ghilimele · R134 — Toate porțile lui `PUT /tenants/{id}` refuzau cu `500`, deci mesajele lor n-au ajuns niciodată la un om · R135 — O denumire de firmă fără nicio literă trecea, și pleca pe `den` în D394 · R136 — Ecranul «Date firmă» trimitea redenumirea ÎNAINTEA a ceea ce putea fi refuzat · R137 — Sonda de ecran număra rânduri, deci era oarbă exact la felul de scriere pe care îl face un ecran de date · R138 — Un `@` nu e o adresă de email: patru rute creau un cont sau trimiteau un email pe orice șir care conținea unul · R139 — Refuzul de pe linia facturii spunea CARE câmp, nu CE e greșit — iar cuvântul pe care îl folosea era fals · R140 — Registrul de încasări și plăți refuza în limba programatorului, și nimeni nu-l putea deschide ca să vadă · R141 — Unsprezece restanțe erau scrise în AFARA blocului pe care îl citește garda, deci nu le-a verificat nimeni · R142 — Pe ecranul de emitere, o cotă de TVA NECUNOSCUTĂ se afișa ca zero, iar «Total» ieșea egal cu «Bază» · R143 — Ecranul de emitere avea două violări de accesibilitate, dintre care una critică, și nimic nu le vedea · R144 — «Aur de investiții» cădea cu `500` pe o puritate care nu e număr, deci refuzul lui n-a existat niciodată · R145 — «Chirii / comodat / refacturări» nu putea reuși NICIODATĂ din ecran: formularul trimitea alt câmp decât cere ruta · R146 — Fix acolo unde verificarea devenea imposibilă, se renunța la ea: o operațiune fără dată trecea · R147 — Șase refuzuri care vorbeau limba programatorului, dintre care unul în patru locuri · R148 — Aceeași achiziție intracomunitară era așezată în declarație pe exigibilitate și i se valida cota pe data facturii · R149 — Două rute validau cota pe o dată pe care legea nu o numește niciodată · R150 — Un cabinet inexistent răspundea „n-a făcut nimic", iar trei rute înlocuiau tăcut o valoare imposibilă cu una convenabilă · R151 — Excepția din art. 291 alin. (5) nu e modelată: aplicația nu poate ști dacă factura sau avansul au precedat livrarea · R152 — Magazinul online se declara „conectat" la o adresă cu care nu vorbise nimeni · R153 — Registratura scria un document într-un an pe care tot ea îl refuză la citire · R154 — „N-am putut trimite" despre un șir care nu era o adresă de email · R155 — „Încearcă o poză mai clară" despre un fișier care nu era o poză · R156 — Ecranul pachetelor acoperea refuzul precis al serverului · R157 — Răspunsul gol la o sesizare: ecranul nu făcea nimic și nu spunea nimic · R158 — Ecranul de recomandare spunea una, bara de sus alta · R159 — „Ciornă salvată." după o salvare care fusese refuzată · R160 — Gardul acoperirii vizuale cerea 16 ecrane din 18, și nimic n-o spunea · R161 — Butonul de casă rămânea stins, iar motivul trăia într-un `title` pe care atingerea nu-l vede · R162 — «Nota a fost creată ca ciornă» se scria și se ștergea în aceeași clipă · R163 — Nota contabilă cădea cu `500` pe un cont PLAUZIBIL, și numai pe unul plauzibil · R164 — Un CNP valid, deja folosit, întorcea `500` în loc de refuz · R165 — SAF-T-ul unei firme TRIMESTRIALE raporta o singură lună din trei · R166 — Validarea D406 din aplicație era INACCESIBILĂ: orice apel ieșea `gri` · R167 — Refuzul spunea că firma depune TRIMESTRIAL și nu spunea pe ce se sprijină · R168 — Gardul de diacritice era verde, la clichet 0, peste un defect pe care lotul 13 îl scrisese · R169 — Scannerul de citări măsura o lume care se micșora cu fiecare temei pus unde trebuie · R17 — Graful de dependențe e cheiat pe NUME SIMPLU, plat peste tot `core/` · R170 — „32 de formulare probate" era spus despre un registru de 34 · R171 — Cele 24 de citări scoase la iveală de R169 n-au nici articol localizabil, nici prag de reverificare · R172 — «Date firmă» cerea periodicitatea TVA fără să spună după ce se alege · R19 — `graf_clustere` tratează utilitarele partajate ca proprietate · R2 — Vigoarea PE PUNCT, nu doar pe articol · R20 — Opt artefacte de UN OCTET în corpus, cu nume de declarație · R21 — Forma de înregistrare în contabilitate nu există nicăieri, iar de ea atârnă Cartea mare · R22 — Jurnalul de origine al unei înregistrări e o constantă, și pleacă așa la ANAF · R25 — Module fiscale care NU citează legea, deci rămân în afara domeniului scanului · R28 — Ce trebuie să arate ecranul de angajare, dacă arată ceva · R29 — Cota de TVA ca valoare implicită în ECRAN, care anulează refuzul învățat de server · R30 — Avertismentul de prăpastie al salariului minim, plecat odată cu estimarea · R31 — Anul e scris în cerere, deci ecranul nu poate ajunge la anul curent · R33 — Module de verificare care n-au fost NICIODATĂ legate · R34 — Nota contabilă de salarii contrazice D112-ul depus, pe 10 din 40 de perechi · R35 — Verdict VERDE pe o lună cu factură necontabilizată, cunoscută în chiar payload-ul verdictului · R36 — Cum ajung faptele economice în contabilitate nu e o alegere DECLARATĂ nicăieri · R40 — Nicio declarație depusă prin aplicație, deci lanțul de apărare nu e exercitat niciodată · R41 — Verdictul oficial de validare se produce, se afișează și se aruncă · R42 — 144 de rute care schimbă date nu verifică niciun rol, iar 24 din 24 dintre ele fac contabilitate · R43 — Confirmarea de plată marchează o factură încasată fără să fi intrat un leu, și caută prin toate firmele · R44 — Un element din coadă e legat de o firmă care nu există · R45 — Patru artefacte se produc, se descarcă, și nu rămân nicăieri · R46 — Trecerea de regim fiscal are cea mai mare consecință și cele mai puține verificări · R49 — Avertismentul de prăpastie al salariului minim, desprins din R30 · R50 — Ștergerea unui cabinet nu curăță tabelele partajate, iar datele lui rămân în ele · R51 — Data încetării contractului nu ajungea în bază, iar ruta răspundea 200 · R52 — Un document care ajunge la un om poate pleca pe un GET, iar acolo nu se verifică niciun rol · R54 — Contul contabil venit din corpul cererii nu e confruntat cu planul de conturi · R55 — Aceeași clasă de operațiune contabilă, roluri diferite, fără motiv scris · R56 — Trei rute manipulează credențiale ale unor sisteme externe, fără rol · R57 — Calea de API emite facturi fără poarta de gestiune pe care o are ecranul · R58 — Închiderea perioadei nu verifică nimic, iar redeschiderea nu lasă urmă · R60 — Instrumentul care hrănește verificările atribuia rutei modulul importat de altcineva · R61 — Raportul Z tastat de om nu are verificare de duplicat, iar nota lui intră direct ca evidență · R62 — Clientul își schimbă adresa de autentificare fără confirmare, iar cabinetul nu află nici asta, nici cine a primit acces · R63 — Aceeași persoană are două adrese în aplicație, iar nimic nu le confruntă · R65 — `patron_email` are precedență la trimiterea pachetului și nicio cale de scriere · R66 — `patron_nume` intră în adeverințe și contracte, și nu-l scrie nimic · R70 — O rută poate fi scrisă, gardată și verde, fără ca nimic s-o cheme · R72 — O firmă adăugată din greșeală nu se poate scoate · R73 — Patru trimiteri de email sunt înghițite tăcut, iar trei dintre ele sunt singura cale de intrare · R74 — Trei joburi de fundal sunt oprite de o lună, iar deadman-ul nu se uită la ele · R77 — Divergența de denumire se ARATĂ, dar alegerea nu se CERE · R78 — Actul cel mai distructiv al aplicației stă sub 26 de carduri, iar cine îl caută nu-l găsește · R79 — Ștergerea unei firme își produce propriul orfan, la 78 de milisecunde după ce a terminat · R80 — Pentru 51 din 411 rute, gardul „rută fără apelant" nu poate afirma nimic · R81 — Denumirea unei firme stă în două locuri, iar redenumirea atinge unul singur · R82 — Cele patru acte cu cel mai mare efect asupra unei firme se termină în tăcere · R83 — O firmă dezactivată nu se poate reactiva: poarta de acces o consideră inexistentă · R84 — Trecutul unei firme scoase din portofoliu nu se mai poate citi: 13 rute de raport răspund 404 · R85 — `d112.pull` întoarce un salariat cu CAS, CASS și impozit, dar fără CAM · R86 — Nota de salarii nu înregistrează deloc biletele de valoare, iar salariile brute intră cu altă cifră decât cea declarată · R87 — O factură EMISĂ nu produce nota contabilă; contabilizarea e un act separat, care se poate uita · R88 — O factură PRIMITĂ validată creează cheltuiala, dar nu și nota contabilă · R89 — Stocul de facturi rămase în afara evidenței n-are nici listă revizuită, nici decizie: reconcilierea istorică · R90 — O notă legată de o factură nu se poate dezlega, iar refuzul ștergerii numește o ieșire care nu există · R91 — O factură EMISĂ care intră prin import nu produce nota, iar absența e DECLARATĂ, nu decisă · R93 — Aceeași lipsă e poartă în trei module de declarație și simplu avertisment în al patrulea, iar ANAF respinge XML-ul · R94 — Două mecanisme răspund diferit la „ce datorează firma asta", iar generatorul nu ascultă de niciunul · R96 — Cele trei registre obligatorii citesc trei populații diferite de note, în aceeași lună și pe aceeași firmă
- **antetul, actualizat la**: 2026-09-08

---

## 7. POARTA

**Teste:** `4225 passed, 11 skipped, 14 xfailed` — **0 roșii**, în 26 min 14 s. Rulate de poarta
`pre-commit`, pe suita ÎNTREAGĂ, fără subset.

**Verificator:** `verificator_conformitate.py` → **TOTAL: 0 candidate** (12,28 s).

**`ruff`** (F821/F822/F823, nume nedefinite): `All checks passed!`

**Four-way ÎNCHIS:**

| | |
|---|---|
| `HEAD` | `224cfc40` |
| `origin/main` | `224cfc40` |
| `public/main` | `224cfc40` |
| `backup/lant-2026-09-08` | `224cfc40` |
| procesul viu | pornit **14:45:50**, commitul e din **14:19:03** — pornirea e ULTERIOARĂ commitului |

**Arborele de lucru:** curat (`git status --short` gol).

**Site:** `https://iconta.eu/` → **200**.

**Ce a mai probat poarta, dincolo de cifre.** Patru gărzi ale casei au respins prima formă a muncii
ăsteia, și toate patru aveau dreptate: tabelele noi lipseau din ștergerea firmei · două valori de
cadență stăteau într-un modul pe care `scan_constante` îl vede ca fiscal (mutate lângă `RITMURI`) ·
o aserțiune pe șir în loc de structură (rescrisă) · un import mort. Plus cinci blocuri generate,
regenerate. *Niciuna n-a fost ocolită.*

---

## Anexă — operațiuni care au durat peste 1 minut

*Cerut explicit. Fiecare pas măsurat, nu doar poarta agregată. Sub 1 minut, deci în afara listei:
migrarea triggerelor (0,35 s), curba celor 5 rute (33,66 s), inventarul pe o singură firmă (24,27 s),
paritatea (2,85 s), cele trei suite P2 (3,49 s), `ruff` (sub 10 s).*

| operațiune | durată exactă | de ce a durat |
|---|---|---|
| `scan_dependente`, sweep pe 20 de firme — rularea 1 | **67,34 s** | `control_fiscal` face ~5.000 de instrucțiuni per firmă; fiecare formă distinctă primește un `EXPLAIN` |
| `scan_dependente`, rularea 2 (artefact mutat în `masuratori/p2/`) | **71,35 s** | idem |
| `scan_dependente`, rularea 3 (după reparația `ASPECTE_USOARE`) | **79,02 s** | idem; a treia rulare a fost necesară fiindcă garda a refuzat o măsurătoare goală |
| suita întreagă, rularea de verificare de dinaintea commitului | **1631,04 s** (27 min 11 s) | rularea care a găsit cele 9 gărzi ale casei respinse |
| suita celor 9 gărzi reparate, prima trecere | **158,76 s** | `test_trasee` interoghează baza pentru fiecare traseu |
| suita celor 9 gărzi reparate, a doua trecere (după injectarea blocurilor) | **158,40 s** | idem |
| suita întreagă, în poarta `pre-commit` a commitului | **1574,52 s** (26 min 14 s) | poarta cere suita completă, fără subset |

*Sub 1 minut, deci în afara listei, dar măsurate: `verificator_conformitate.py` **12,28 s** · curba
celor 5 rute **33,66 s** · inventarul pe o singură firmă **24,27 s** · migrarea triggerelor pe 20 de
firme **0,35 s** · paritatea **2,85 s** · cele trei suite P2 **3,49 s** · `ruff` sub 10 s.*
