RAPORT — LOTUL 2 din cele patru lucrări: **R191** | 16.09.2026 | `5492f0da` → `4d938efd`

## 0. CERINȚE

**1. Tăria constatării `D406_ASSETS_VS_CONT_28X`** — registrul de imobilizări ↔ conturile 28xx.

| | |
|---|---|
| **ce e** | `EURISTICA` (semnalează) sau `CERTA` (cere confirmare scrisă înainte de depunere). Împărțirea pe tării e explicit a ta, pe tip — `core/supervizor.py` o așteaptă ca **date** |
| **ce blochează dacă rămâne nedată** | **nimic nu se blochează**, și ăsta e chiar designul: un tip fără tărie **se vede și nu produce niciun efect**. Ce rămâne nedeschis e **stratul de efect** pe constatarea asta — adică dacă o nepotrivire între registru și evidență cere confirmare înainte de a depune SAF-T. Și ține **R115** deschisă |
| **detaliile care ajută decizia** | **Propunerea mea: `CERTA`**, fiindcă ambele explicații legitime pe care criteriul tău cere să le caut sunt **închise în cod** (ciornă pe cont → gri; registru ilizibil → gri), iar ce rămâne e o nepotrivire aritmetică între ce se declară și ce e în evidență — chiar definiția pe care ai dat-o CERTEI. **Rezerva mea, și e reală:** contul 28xx e ținut la nivel de **cont**, nu de activ (nota lunară scrie `6811 = 28xx` fără id-ul mijlocului fix), deci constatarea spune **că** și **cu cât**, nu **care** activ. O CERTĂ care cere confirmare fără să poată numi subiectul e mai greu de închis decât una care semnalează. **Cifra care face alegerea concretă:** azi ar produce **2 roșii** pe portofoliu (t003 cont 2808, t013 cont 2813) |
| **a câta tură se cere** | **prima** pentru tipul ăsta. *Pe R115 ca restanță e a doua oară — prima dată, 01.09, ai dat tăriile pentru tipurile de atunci; o tărie nu se moștenește la un tip care n-a existat. De-aia `reluări` a urcat la 1* |

**2. Ce face reevaluarea când amortizarea pe care ar elimina-o depășește ce s-a înregistrat (R192).**

| | |
|---|---|
| **ce e** | **(a)** ruta refuză, numind luna a cărei notă de amortizare lipsește · **(b)** acceptă și semnalează, lăsând soldul `28xx` să treacă pe minus până la regularizare · **(c)** altceva |
| **ce blochează dacă rămâne nedată** | **R192** rămâne deschisă. Confruntarea există deja (lotul ăsta), deci divergența nu mai e invizibilă — dar ruta se poartă în continuare ca înainte |
| **detaliile care ajută decizia** | schimbă ce ajunge la contabil, deci nu o iau eu (§2.3 pct.2). **Cifra care o face concretă:** pe `tenant_003` soldul lui `2813` e **0,00** iar registrul declară **927,96** — deci varianta (a) ar refuza **orice** reevaluare pe firma aia până la punerea la zi a notelor. **O variantă am respins-o fără să întreb:** ca aplicația să genereze singură nota lipsă — ar fi contabilitate făcută în locul omului |
| **a câta tură se cere** | **prima** |

## 1. CE AM PRESUPUS

1. **Că R191 se îngustează** la obiectul numit în restanță, nu la instrumentul #5 întreg din
   `INSTRUMENTE_ROADMAP.md` (care e despre **ecrane** și Playwright). Am semnalat-o în confirmarea de
   la începutul turei, și am scris deosebirea **în roadmap**, ca să nu fie citit ca având #5 făcut.
2. **Că perechea REPORTEAZĂ, nu blochează.** `PLAN_LUCRU` spune deja că supervizorul nu e a doua
   poartă; am aplicat regula, nu am decis-o.
3. **Că identitatea potrivită e cea CUMULATIVĂ** (amortizare cumulată vs. sold), nu cheltuiala
   anului. Presupunerea e a mea; motivul e scris: cumulativul prinde și eliminarea de la reevaluare,
   care e un **debit** și n-ar apărea într-o comparație de cheltuieli.

## 2. CE AM FĂCUT ÎN PLUS / MAI PUȚIN

### ÎN PLUS

| ce | de ce |
|---|---|
| **măsurătoarea de deschidere**, înainte de orice cod | ca perechea să nu se nască „ca precauție". A găsit **trei conturi divergente** din patru măsurate |
| **`motiv_gri`**, câmp nou pe constatare | cele două griuri trebuie deosebite din **date**. Altfel singura cale ar fi fost un cuvânt căutat în mesaj — gardă pe text |
| **`INSTRUMENTE_ROADMAP.md`**, #5 marcat explicit **NEÎNCEPUT** | fără rândul ăla, cineva ar fi citit roadmapul ca având #5 făcut. *Două lucruri cu același nume nu sunt același lucru* |
| **R115, redeschisă** cu `reluări` urcat | garda a cerut-o; nu e o formalitate — ține vizibil că o decizie e din nou în așteptare |

### MAI PUȚIN

| ce | de ce |
|---|---|
| **tăria nu e atribuită** | e a ta, pe tip. Am scris propunerea **și rezerva**, ca răspunsul să ia o tură, nu două |
| **R192 nu s-a închis** | jumătatea întâi (confruntarea) e făcută; jumătatea a doua e o decizie de produs — §0 pct. 2 |
| **perechea nu spune CARE activ divergă** | contul 28xx e ținut la nivel de cont. Limita e declarată în gardă, în registru și în propunerea de tărie |
| **nicio temă nouă** | regula de la 0Z |

## 3. CE AM ACTUALIZAT

| registru | ce s-a scris |
|---|---|
| **`CONFORMITATE.md`** | **R191 → REZOLVATĂ** (`fcd13ac9`), cu tabelul celor trei conturi divergente și limita declarată · **R115 → REDESCHISĂ**, `reluări` 0→1, prima închidere păstrată scrisă · **R192** — rând nou: confruntarea există, ce rămâne e decizia, cu variantele numite |
| **`GARZI.md`** | garda nouă, cu tabelul a ce păzește **și** a ce nu; plus inventarul regenerat (591 → 592) |
| **`TESTE.md`** | două intrări: garda, și producătorul adăugat în cele trei locuri de stub |
| **`ISTORIC.md`** | ce se schimbă pentru un contabil, în cuvintele lui |
| **`INSTRUMENTE_ROADMAP.md`** | #5 rămâne **NEÎNCEPUT**, cu deosebirea de obiect scrisă |
| **`PREDARE_LANT.md`** | antetul pe `fcd13ac9`; la 0Z, lucrarea 2 marcată ÎNCHISĂ; blocul de clichete regenerat |
| **`DECIZII.md`** | **nimic de actualizat** — lotul n-a produs nicio decizie de-a mea care să răstoarne una scrisă; cele două alegeri reale (tăria, comportamentul rutei) sunt **ale tale** și sunt la §0. *Ce am ales eu — identitatea cumulativă, `motiv_gri`, forma învelișului — sunt alegeri de implementare, scrise în cod și în GARZI, nu decizii de direcție (regula 1)* |
| **`PLAN_LUCRU.md` · `PLAN_INVESTIGATII.md` · `PLAN_ARHITECTURA.md`** | **nimic de actualizat** — nicio regulă, fază sau interdicție atinsă |
| **`METODA_VERIFICARE.md`** | **nimic de actualizat** — §22 și §23 s-au *aplicat*. *Dar dacă vrei, aici ar avea loc lecția lotului: o mutație care nu se aplică arată exact ca un test care nu păzește* |
| **`DESIGN_SYSTEM.md`** | **nimic de actualizat** — niciun ecran atins |
| **`MODEL_AUDIT_TENANT.md` · `ISTORIC_TENANTI.md`** | **nimic de actualizat** — niciun tabel nou, nicio fațetă redefinită |
| **`anaf_surse/INDEX.json` · `PROVENIENTA.json`** | **nimic de actualizat** — niciun act nou în corpus |

## 4. ÎNȚELEGEREA

Lucrarea 2 din cele patru: construiesc confruntarea pe care R191 o cere — *amortizare declarată
contra amortizare înregistrată* —, îngustată la obiectul ăla, nu la instrumentul #5 întreg.

**Ce a ieșit diferit de înțelegerea de la început, și se scrie:** credeam că închid R191 **și** R192
în același lot, fiindcă R192 trimite la R191. Măsurând, s-a văzut că R192 cere o **decizie de
produs** peste confruntare, nu doar confruntarea. Ordinea pe care o scrisesem eu ieri în R192 —
*„întâi se poate confrunta, apoi se decide"* — s-a dovedit exactă, iar lotul s-a oprit unde spunea ea.

## 5. RĂSPUNS LA COMANDĂ

**1.** *„Citește, în ordinea asta: CLAUDE.md · PREDARE_LANT.md (0Z) · PLAN_LUCRU.md · ARHITECT.md."*
→ **FĂCUT** la începutul turei; nu s-a recitit pentru lotul ăsta, fiindcă nimic din ele nu s-a
schimbat între loturi (verificat: cele patru fișiere nu apar în `git diff cfdd00ae..HEAD` decât
`PREDARE_LANT.md`, pe care l-am scris eu).

**2.** *„Citește starea celor patru lucrări din 0Z."* → **FĂCUT**; pentru lotul ăsta am **re-derivat**
starea lui R191 din cod, nu din registru: măsurătoarea de deschidere e primul act al lotului.

**3.** *„Confirmă-mi în două rânduri… Dacă ceva contrazice, spune înainte."* → **FĂCUT** la începutul
turei. Contradicția pe care o semnalasem atunci — R191 trimite la instrumentul #5 din backlogul A3,
declarat NEÎNCEPUT — s-a rezolvat exact cum am spus: am îngustat la obiectul numit, iar deosebirea e
scrisă acum **în roadmap**, nu doar în raport.

**4.** *„Execută cele patru lucrări din 0Z, în ordinea scrisă acolo: R59 → R191 → cele 8 rute → cele
8 citări DUK."* → **PARȚIAL: 2 din 4 închise**, în ordine. Urmează **cele 8 rute cu clichet**.
**Nicio temă de investigație nouă n-a fost deschisă.**

**5.** *„Loturi cu publicare și raport… ZIP, calea exactă, SHA-256 și duratele măsurate."* →
**FĂCUT** (mai jos).

**6.** *„Continuă lot după lot, fără să întrebi între loturi."* → **ÎN CURS.** Cele două cerințe de
la §0 **nu opresc lanțul**: nimic nu se blochează fără ele. Trec la **lotul 3 — cele 8 rute**.

## 6. UNDE SUNTEM

*Derivat cu `scripts/raport_b.py`, după commit.*

- **etapa**: E1 — SETUL COMPLET · **locuri de verificare**: 221 scrise / 0 goale (100%)
- **interdicții, din 78**: MĂSURATE 24 · PARȚIAL 16 · NEMĂSURABILE 5 · NEÎNCEPUTE 33
- **restanțe DESCHISE: 55** (din care ale etapei E1: **25**) — R191 a ieșit, **R115 a reintrat**
- **restanțe REZOLVATE**: +1 → R191 · **R115 a ieșit din rezolvate**
- **decizii care blochează**: **niciuna** *(cele două de la §0 nu blochează: fără ele, comportamentul
  de azi rămâne cel de azi)*
- **antetul, actualizat la**: 2026-09-16

## 7. POARTA

| | |
|---|---|
| **teste** | **6225 passed · 0 failed** · 7 skipped · 11 xfailed — 2111,41 s (35:11). COLLECTED confirmat prin rulare |
| **verificator** | `TOTAL: 0 candidate` (207 scanat = 206 + 0 GRI + 0 ROȘU + 1 EXCLUS; rute 421 = 382 + 7 GRI + 0 ROȘU + 32 EXCLUS) |
| **four-way** | **ÎNCHIS.** `HEAD = origin/main = backup/lant-2026-09-16 = 4d938efd`; `toate_poarta_head.py` → *2 din 2 procese*. `public/main` pe același commit. Zero sentinele de eșec |
| **tree** | `git status --porcelain` → **gol** · **site** `iconta.eu` → **200** |
| **poartă verde vizuală** | **N/A — niciun ecran atins** (perechea de reconciliere, supervizorul, registre). Declarat explicit |

**Trei rulări complete de poartă (~1 h 45 min) + una țintită pe registre (5:18).** O singură
respingere de poartă completă, pe blocul generat din `GARZI.md` (591 → 592) — regenerat, nu scris cu
mâna. Rulările țintite pe registre au prins de **două ori** aceeași greșeală de-a mea: câmpurile unei
restanțe se citesc **până la capătul rândului**, iar o paranteză lămuritoare pusă acolo face garda să
citească `DESCHISĂ** *` sau să crape la `int()`. Lămurirea stă acum pe rând propriu, iar cele două
instanțe sunt scrise **în registru, lângă câmpuri**, ca să nu existe a treia.
