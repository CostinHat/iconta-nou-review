RAPORT — LOTUL 1 din cele patru lucrări: **R59** | 16.09.2026 | `cfdd00ae` → `5492f0da`

## 0. CERINȚE

**nimic.** Lotul n-a produs nicio cerință către tine.

*Lucrarea 1 avea `cine deblochează: DECIZIE`, iar condiția ei cerea alegerea între (a), (b) și (c).
N-am cerut-o din nou, și spun de ce: criteriul pe care l-ai lărgit pe 16.09 — „coloana din registru
urcă **și** `AcquisitionAndProductionCostsEnd` o declară" — **este** varianta (a), scrisă ca cifră. Am
tratat măsura ca pe decizie. Am semnalat citirea asta înainte de a începe, în confirmarea de două
rânduri, și n-am primit contra.*

*R192 (deschisă azi) și R191 (lucrarea 2) nu sunt cerințe: sunt muncă, și e chiar lotul următor.*

## 1. CE AM PRESUPUS

Trei lucruri, toate declarate înainte de a începe:

1. **Că lărgirea criteriului R59 înseamnă varianta (a)** — v. §0. Presupunerea e a mea; textul tău
   n-o spune în cuvintele astea.
2. **Că R191 se îngustează la obiectul numit în restanță** („amortizare declarată contra amortizare
   înregistrată"), nu la instrumentul #5 întreg din `INSTRUMENTE_ROADMAP.md`. Nu s-a exercitat încă —
   e lotul 2.
3. **Că momentul efectului e validarea notei, nu crearea ciornei.** Textul variantei (a) o spune
   („la validarea notei"), dar proba pe care o scrisesem ieri aștepta efectul **imediat după rută**.
   Am schimbat proba, nu regula — și am adăugat aserțiunea pe starea intermediară, ca schimbarea să
   nu treacă drept relaxare.

**Ce NU am presupus, și e important:** n-am presupus că e destul să urc coloana. Am măsurat ce se
întâmplă cu amortizarea dacă o urc fără etape — v. §2.

## 2. CE AM FĂCUT ÎN PLUS / MAI PUȚIN

### ÎN PLUS

| ce | de ce, în plus față de comandă |
|---|---|
| **etapele de amortizare** (reevaluarea taie durata) | criteriul cerea două cifre. Urcând doar coloana, motorul ar fi recalculat cumulata pe valoarea **nouă** de la **PIF-ul original** — o cifră pe care evidența n-a înregistrat-o niciodată. *Reparația ar fi mutat divergența de pe o coloană pe alta, exact acolo unde criteriul n-ar mai fi văzut-o.* Nu e zel: fără etape, reparația introducea un defect nou |
| **`AppreciationForPeriod` și costul de DESCHIDERE** în anul reevaluării | `cost_begin` = `cost_end` într-un an în care valoarea s-a schimbat e o afirmație falsă despre soldul de deschidere |
| **refuzul pe durată epuizată**, cu clasă proprie de eroare | altfel aplicația ar fi ales tăcut o durată „rezonabilă" — interdicția din `CLAUDE.md` §3 |
| **întrebarea pusă validatorului ANAF** | un câmp constant a devenit variabil; „structura rămâne validă" nu se mai putea presupune |
| **R192, consemnată** | a ieșit construind R59. Fluxul din `PLAN_LUCRU` cere consemnarea ca **prim** gest |
| **`ISTORIC_TENANTI.md`**, clasificarea tabelului nou pe ambele firme | cerut de gardul de perimetru; clasificarea se **derivă** din cea a lui `mijloace_fixe` |

### MAI PUȚIN

| ce | de ce |
|---|---|
| **clichetul `PLAFON_SUBSET_FISCAL` n-a scăzut: 8 → 8** | proba mea exercită **use-case-ul** și lanțul pe schemă efemeră, **nu ruta HTTP**. Ruta `reevaluare-imobilizare` rămâne pe lista lotului 3, întreagă. *Aș fi putut coborî clichetul lărgind definiția lui „numită" — exact ce interzice fișierul în care stă* |
| **prezentarea SAF-T a ELIMINĂRII cumulatei** între `BookValueBegin` și `BookValueEnd`, în anul reevaluării | cere o regulă ANAF pe care n-am confruntat-o la sursă. DUK acceptă forma emisă, dar acceptarea validatorului nu e o regulă citită. Consemnat, nu presupus |
| **nicio temă nouă** | regula de la 0Z |

## 3. CE AM ACTUALIZAT

| registru | ce s-a scris |
|---|---|
| **`CONFORMITATE.md`** | **R59 → REZOLVATĂ** pe `d937eef6`, cu ambele cifre din criteriu, tabelul celor două momente, arbitrul și garda. **`măsurat la` NU s-a re-datat** — rămâne pe 26.08 / `abc0bc2`: nu se re-datează o măsurătoare pe care n-am refăcut-o. **R192 — secțiune nouă**, cu cele opt câmpuri |
| **`DECIZII.md`** | intrarea **52**: patru decizii, fiecare cu alternativa respinsă (momentul · obiect vs. coloană · etape vs. bază urcată · apreciere declarată), plus limita pe durata epuizată |
| **`GARZI.md`** | `core/test_reevaluare_registru.py`, cu **ce păzește dincolo de cele două cifre** și cu ce **nu** păzește. Plus blocul de inventar, **regenerat** din instrument |
| **`TESTE.md`** | trei intrări: garda, migrarea, proba DUK pe apreciere nenulă |
| **`ISTORIC.md`** | ce se schimbă pentru un contabil, în cuvintele lui |
| **`ISTORIC_TENANTI.md`** | `reevaluari` clasificat pe **amândouă** firmele: pe t006 *în afara perimetrului* (regimul nu poartă imobilizări), pe t001 *poate primi date*. Cu motivul derivării scris |
| **`TRASEE.md` · `TRASEE_VERIFICARI.md`** | blocul generat, **regenerat**; adnotarea rutei **re-ancorată de la instrument**, iar cele trei verificări scrise sub ea — care stăteau pe constatarea din 26.08 — **rescrise**. Măsurătoarea veche se **păstrează** scrisă |
| **`PREDARE_LANT.md`** | antetul pe `d937eef6`; la **0Z**, lucrarea 1 marcată ÎNCHISĂ; blocul de clichete, regenerat |
| **`PLAN_LUCRU.md`** | **nimic de actualizat** — lotul n-a schimbat nicio regulă de conducere a lucrului |
| **`PLAN_INVESTIGATII.md`** | **nimic de actualizat** — nu s-a atins nicio fază a investigației |
| **`PLAN_ARHITECTURA.md`** | **nimic de actualizat** — nicio interdicție nouă; R59 rămâne NEACOPERITĂ de plan, exact cum scria |
| **`METODA_VERIFICARE.md`** | **nimic de actualizat** — §22 și §23 s-au *aplicat*, nu s-au schimbat |
| **`DESIGN_SYSTEM.md`** | **nimic de actualizat** — niciun ecran atins |
| **`INSTRUMENTE_ROADMAP.md`** | **nimic de actualizat** — instrumentul #5 se atinge în lotul 2, nu acum |
| **`MODEL_AUDIT_TENANT.md`** | **nimic de actualizat** — fațetele F1..F9 n-au fost redefinite |
| **`anaf_surse/INDEX.json` · `PROVENIENTA.json`** | **nimic de actualizat** — n-a intrat niciun act nou în corpus |

## 4. ÎNȚELEGEREA

*Scrisă înainte de muncă. Ce a ieșit diferit se spune mai jos, nu se rescrie.*

Am înțeles că: citesc cele patru documente **întâi**, confirm în două rânduri, apoi execut **cele
patru lucrări de la 0Z în ordinea scrisă acolo**, în loturi, fiecare lot publicat și raportat, cu
pachet ZIP la închidere — și că nu mă opresc să întreb între loturi.

**Ce a ieșit diferit de înțelegerea de la început, și se scrie:** credeam că R59 e o reparație de o
coloană. Măsurând, s-a dovedit că o coloană urcată fără etapă de amortizare **produce** o divergență
nouă. Lucrarea a fost mai mare decât o citeam la început — nu fiindcă am lărgit-o, ci fiindcă
îngustă ar fi fost falsă.

## 5. RĂSPUNS LA COMANDĂ

**1.** *„Citește, în ordinea asta: CLAUDE.md (procedura) · PREDARE_LANT.md (punctul 0Z) ·
PLAN_LUCRU.md (regulile în vigoare) · ARHITECT.md. Nu începe nimic până n-ai citit tot."*
→ **FĂCUT**, în ordinea dată, înainte de orice altceva. `CLAUDE.md` 919 rânduri (§2.2 raportul de 11,
§2.3 lanțul și publicarea în 5 pași + four-way, mecanica porții) · `PREDARE_LANT.md` 1.164 (0Z, cele
patru lucrări) · `PLAN_LUCRU.md` 817 (cele nouă reguli, cele trei praguri, regulile 4–8 ale porții) ·
`ARHITECT.md` 65 (FORMA COMENZII).

**2.** *„Apoi citește starea celor patru lucrări din 0Z: R59 și R191 în CONFORMITATE.md · cele 8 rute
cu clichet și cele 8 citări DUK în GARZI.md."*
→ **FĂCUT**, și cele două liste le-am **derivat din cod**, nu citit din registru:
`scan_scrieri_declaratii.subsetul()` → cele 8 rute; `scan_coduri_validator.confrunta()` → cele 8
citări (`d301_operatiuni_api.py:209` R24.1 · `d402.py` 196 R14, 261 R34, 290 R39, 305+307 R43,
312 R50 · `test_d402.py:51` R14). *Un perimetru citat din predare e o amintire.*

**3.** *„Confirmă-mi în două rânduri: commitul pe care ești, starea porții, și că ai citit cele patru
documente. Dacă ceva din ele contrazice ce urmează, spune înainte de a începe."*
→ **FĂCUT**, înainte de prima linie de cod: `cfdd00ae`, poartă verde la intrare, cele patru citite.
Am semnalat **trei** lucruri: (a) R59 poartă `DECIZIE`, iar citirea mea e că măsura din 16.09 *este*
varianta (a) — și am spus că merg pe ea; (b) R191 trimite la instrumentul #5 din backlogul A3,
declarat NEÎNCEPUT în `PLAN_LUCRU` — comanda de la 0Z îl deschide, iar eu îl îngustez la obiectul
numit; (c) lucrarea 1 și lucrarea 3 se suprapun pe ruta `reevaluare-imobilizare`.
*Punctul (c) s-a dovedit mai mic decât credeam: clichetul fiscal NU a scăzut — v. §2 MAI PUȚIN.*

**4.** *„Execută cele patru lucrări din 0Z, în ordinea scrisă acolo: R59 → R191 → cele 8 rute → cele 8
citări DUK. După ele nu se deschide nicio temă de investigație nouă."*
→ **PARȚIAL — lucrarea 1 din 4 e închisă**, în ordinea scrisă. R191, cele 8 rute și cele 8 citări
DUK **nu sunt începute**; urmează, în ordine. **Nicio temă de investigație nouă n-a fost deschisă.**

**5.** *„Loturi cu publicare și raport la fiecare lot. La închiderea fiecărui lot: ZIP cu tot ce s-a
schimbat, calea exactă, SHA-256 și duratele măsurate în raport."*
→ **FĂCUT** pentru lotul 1. Publicat în două commituri (reparația, apoi consemnarea cu hash-ul real —
tiparul deja folosit în repo). Calea, SHA-256 și cele **șapte** durate de poartă: §7 și
`MASURATORI_R59.txt` din pachet.

**6.** *„Continuă lot după lot până epuizezi cele patru, fără să întrebi între loturi."*
→ **ÎN CURS.** Nu întreb nimic (§0 scrie „nimic"); trec la **lotul 2 — R191**.

## 6. UNDE SUNTEM

*Derivat cu `scripts/raport_b.py`, rulat DUPĂ ce commitul a intrat. Nu scris de mână.*

- **etapa**: E1 — SETUL COMPLET (faza 1 din `PLAN_INVESTIGATII.md`)
- **pasul curent**: **lista 5 COMPLETĂ**. Pe lista 3, premisa ei a căzut: «datele există, lipsește
  documentul» s-a dovedit falsă.
- **locuri de verificare**: **221 scrise / 0 goale** din 221 (100%)
- **interdicții, din 78**: MĂSURATE 24 · PARȚIAL 16 · NEMĂSURABILE 5 · NEÎNCEPUTE 33
- **cel mai vechi commit din registru**: `ffbcb745` (2026-08-22), de la secțiunea #2
- **decizii care blochează**: **niciuna**
- **restanțe DESCHISE: 55** (din care ale etapei E1: **26**) — R59 a ieșit, R192 a intrat
- **restanțe REZOLVATE**: +1 → **R59**
- **antetul, actualizat la**: 2026-09-16

*Proza antetului, recitită la raportul ăsta: «ce mai lipsește» spune că faza 1 n-are pași, dar
criteriul ei nu e îndeplinit fiindcă lista 3 nu e goală — încă adevărat pe `5492f0da`.*

## 7. POARTA

| | |
|---|---|
| **teste** | **6213 passed · 0 failed** · 7 skipped · 11 xfailed — 2101,01 s (35:01). COLLECTED **confirmat prin rulare**, nu dedus |
| **verificator** | `TOTAL: 0 candidate` (scanat 207 = ACCEPTAT 206 + GRI 0 + ROȘU 0 + EXCLUS 1; rute 421 = ACCEPTAT 382 + GRI 7 + ROȘU 0 + EXCLUS 32, clichet GRI 7) |
| **four-way** | **ÎNCHIS.** `HEAD = origin/main = origin/backup/lant-2026-09-16 = 5492f0da0348affa19b460ea83e7dbb482abc7fd`, iar `toate_poarta_head.py` (SHA complet) → exit 0: *„TOATE procesele de producție poartă HEAD: 2 din 2"*, pornite 16:03:11 EEST, **după** commit. Niciuna dintre cele trei sentinele de eșec nu există. `public/main` publicat pe același commit |
| **tree** | `git status --porcelain` → **gol** |
| **site** | `https://iconta.eu/` → **200** |
| **poartă verde vizuală** | **N/A — niciun ecran atins** în tura asta (schimbările sunt în motorul de amortizare, depozite, use-case și registre). Declarat explicit, nu prin omisiune |

**Cele șapte rulări de poartă, cu durata fiecăreia**, sunt în `MASURATORI_R59.txt` §7. Pe scurt:
patru respinse (13 roșii · perimetrul firmei · fotografia buclelor · fișier normativ necitit), una
întreruptă de mine la ~1 minut fiindcă mesajul de commit conținea o afirmație devenită falsă, două
verzi. **Cost total ~3 h 30 min de poartă. Nicio rulare preventivă** — regula 8 din `PLAN_LUCRU`.

**Când poarta a respins, a avut dreptate de fiecare dată.** Două dintre respingeri au produs cod mai
bun decât evitarea lor: refuzul are acum clasă proprie de eroare (în loc de un cuvânt căutat într-un
mesaj), iar fragmentul de SQL a încetat să fie o funcție într-un modul de depozit.
