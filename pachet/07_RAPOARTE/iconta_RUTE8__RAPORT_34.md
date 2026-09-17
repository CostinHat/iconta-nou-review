RAPORT — LUCRĂRILE 3 și 4 din cele patru | 16.09.2026 | `4d938efd` → `45503d84`

## 0. CERINȚE

**Niciuna nouă.** Cele două din raportul lotului 2 **rămân deschise**, și le repet fiindcă șablonul
cere numerotarea, nu fiindcă s-ar fi schimbat ceva:

**1. Tăria constatării `D406_ASSETS_VS_CONT_28X`** — `EURISTICA` sau `CERTA`. Propun `CERTA`, cu
rezerva scrisă (contul 28xx e ținut la nivel de cont, nu de activ, deci constatarea nu poate numi
CARE activ divergă). **Nu blochează nimic** — un tip fără tărie se vede și n-are efect. Ține **R115**
deschisă. *A doua tură de când e cerută.*

**2. Ce face reevaluarea când eliminarea depășește ce s-a înregistrat (R192)** — (a) refuză, numind
luna lipsă · (b) acceptă și semnalează · (c) altceva. Pe `tenant_003` soldul lui `2813` e 0,00 iar
registrul declară 927,96, deci (a) ar refuza *orice* reevaluare acolo. *A doua tură.*

## 1. CE AM PRESUPUS

1. **Că lucrarea 3 se poate tăia în două loturi** (patru rute care împart o lume + patru care cer
   fiecare alta). Comanda spunea „loturi", fără să fixeze numărul.
2. **Că „până în cifra declarației" înseamnă rulajul contului**, nu XML-ul generat. Motivul: rulajul
   e chiar sursa din care se ridică `GeneralLedgerEntries`, iar structura XML are gărzile ei.
3. **Că o citare corectă căreia îi lipsește doar marca de formular se repară, nu se șterge** —
   convenția exista deja în antetul gărzii (`DUK regula A91b (D112)`).

## 2. CE AM FĂCUT ÎN PLUS / MAI PUȚIN

### ÎN PLUS

| ce | de ce |
|---|---|
| **pasul intermediar** în fiecare probă (înainte de validare, rulajul e **zero**) | fără el, o rută care ar scrie direct `validata` ar trece la fel de verde, iar poarta patru-ochi ar dispărea fără să spună nimeni nimic |
| **ambele direcții** pe fiecare rută unde există refuz, cu **urma** verificată | un refuz care lasă totuși o notă e jumătate de refuz |
| **al doilea pas al metodei** la lucrarea 4: dovedirea mutației în fișier | *„DUK nu verifică regula" și „mutația n-a intrat" arată IDENTIC* |
| **calibrarea inversă** cu `R40` / `R49.1` | ca un `valid` să însemne ceva |
| **restaurarea secvenței** în fixtură | altfel proba ar fi înroșit poarta altcuiva a doua zi |
| **două clichete rescrise ca CRITERII** | un clichet la zero nu mai păzește nimic |
| **DECIZII 53 și 54** | ambele reguli de metodă meritau scrise o dată, nu lăsate ca precedente |

### MAI PUȚIN

| ce | de ce |
|---|---|
| **structura XML a D406 nu se probează aici** | are gărzile ei (`test_d406*.py`); aici se probează că efectul rutei **ajunge** acolo |
| **corectitudinea CMP pe metode nu se probează aici** | `test_stocuri_*.py` |
| **cele trei reguli D402 nu s-au reconfruntat cu norma** (OMFP 2727/2015) | s-au confruntat cu **documentul de structură ANAF** din corpus, verbatim. Dacă norma spune altceva decât documentul, nu se vede de aici — limită declarată |
| **nicio temă nouă** | regula de la 0Z, acum în vigoare |

## 3. CE AM ACTUALIZAT

**`GARZI.md`** — două secțiuni: cele opt rute (cu tabelul cifrelor și cu ce păzește pasul
intermediar) și cele opt citări (cu ce a răspuns validatorul la fiecare mutație, calibrarea inversă,
și anti-vacuul care a fost necesar). · **`TESTE.md`** — două intrări, cu clichetele și cu corectura pe
`PLAFON_IN_SUITA`. · **`DECIZII.md`** — **53** (un clichet la zero se rescrie ca criteriu) și **54**
(o citare de validator se lămurește prin rulare, iar mutația se dovedește întâi). · **`ISTORIC.md`** —
ce s-a schimbat azi în total, pentru un contabil. · **`PREDARE_LANT.md`** — antet, 0Z (lucrările 3 și
4 ÎNCHISE), și starea: cele patru sunt terminate.

**Neatinse, cu motivul:** **`CONFORMITATE.md`** — R59 și R191 s-au închis în consemnările lor, cu
hash-urile lor; R115 și R192 sunt deja scrise acolo; lucrările 3 și 4 **n-au deschis nicio restanță
nouă**. · `PLAN_LUCRU` / `PLAN_INVESTIGATII` / `PLAN_ARHITECTURA` — nicio regulă, fază sau interdicție
atinsă. · `METODA_VERIFICARE.md` — **aici ar avea loc DECIZII 54**, dacă vrei: *un `valid` de la un
validator nu înseamnă nimic până nu dovedești că valoarea rea era în fișier*. N-am scris-o singur în
METODA, fiindcă acolo textul e canonic pentru CUM se verifică și merită decizia ta. ·
`DESIGN_SYSTEM.md` — niciun ecran atins. · `INSTRUMENTE_ROADMAP.md` — atins în lotul 2, neatins acum. ·
`MODEL_AUDIT_TENANT.md` / `ISTORIC_TENANTI.md` — niciun tabel nou. · `anaf_surse/*.json` — niciun act
nou în corpus (documentele citite existau deja acolo).

## 4. ÎNȚELEGEREA

Lucrarea 3: cele opt rute primesc probă **în suită**, care merge până în cifra declarației.
Lucrarea 4: cele opt citări se lămuresc **prin rulare**.

**Ce a ieșit diferit:** credeam că lucrarea 4 e o verificare de igienă — schimbă niște etichete.
Măsurând, **trei dintre citări erau afirmații false despre ce face validatorul oficial**. Nu e igienă:
e diferența dintre „ANAF prinde asta" și „noi prindem asta", iar cine ar fi crezut prima ar fi putut
scoate verificarea ca duplicat.

## 5. RĂSPUNS LA COMANDĂ

**1.** *„Citește, în ordinea asta…"* → **FĂCUT** la începutul turei; niciunul din cele patru nu s-a
schimbat între loturi în afară de `PREDARE_LANT.md`, pe care l-am scris eu.

**2.** *„Citește starea celor patru lucrări din 0Z."* → **FĂCUT**; ambele liste au fost **derivate
din cod** la începutul turei, și **re-derivate** la începutul fiecărei lucrări.

**3.** *„Confirmă-mi în două rânduri… Dacă ceva contrazice, spune înainte."* → **FĂCUT**. Cele trei
semnalări de atunci s-au rezolvat toate: decizia R59 era măsura din 16.09 · R191 s-a îngustat, cu
deosebirea scrisă în roadmap · suprapunerea lucrărilor 1 și 3 s-a dovedit mai mică decât credeam
(clichetul fiscal n-a scăzut la lotul 1, fiindcă proba era la nivel de use-case).

**4.** *„Execută cele patru lucrări din 0Z, în ordinea scrisă acolo: R59 → R191 → cele 8 rute → cele
8 citări DUK. După ele nu se deschide nicio temă de investigație nouă."* → **FĂCUT, toate patru, în
ordine.** **Nicio temă de investigație nouă n-a fost deschisă**, iar regula e acum scrisă ca stare în
predare.

**5.** *„Loturi cu publicare și raport la fiecare lot… ZIP, calea exactă, SHA-256 și duratele."* →
**FĂCUT** pentru toate patru (patru loturi, cinci pachete numărând cele două jumătăți ale lucrării 3).

**6.** *„Continuă lot după lot până epuizezi cele patru, fără să întrebi între loturi."* →
**FĂCUT. Cele patru sunt epuizate.** N-am întrebat nimic între loturi; cele două cerințe de la §0
n-au blocat lanțul.

## 6. UNDE SUNTEM

*Derivat cu `scripts/raport_b.py`.*

- **etapa**: E1 — SETUL COMPLET · **restanțe DESCHISE: 55** (E1: 25) · **decizii care blochează: niciuna**
- **antetul, actualizat la**: 2026-09-16
- închise azi: **R59**, **R191** · deschise/redeschise azi: **R192**, **R115**

## 7. POARTA

| | |
|---|---|
| **teste** | **6244 passed · 0 failed** · 7 skipped · 10 xfailed — 2115,01 s (35:15) |
| **verificator** | `TOTAL: 0 candidate` |
| **four-way** | **ÎNCHIS.** `HEAD = origin/main = backup/lant-2026-09-17 = 45503d84`; 2 din 2 procese. `public/main` pe același commit |
| **tree** | gol · **site** `iconta.eu` → **200** |
| **poartă vizuală** | **N/A — niciun ecran atins** în lucrările 3 și 4 (probe de suită, motor fiscal, registre). Declarat explicit |

**Zece porți complete în tura de azi**, ~5 h 50 min. Fiecare respingere a fost reală; două au produs
cod mai bun decât evitarea lor.
