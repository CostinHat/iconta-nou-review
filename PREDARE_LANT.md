Citeste CLAUDE.md §2.2 (structura raportului) si §2.3 (lant, siguranta, limba - pct.11 poarta verde vizuala) + ARHITECT.md "FORMA COMENZII" (7 puncte), apoi acest PREDARE_LANT.md, inainte de a incepe.

# PREDARE LANȚ — R58 aplicat, trei restanțe închise, loturile 1–5 scrise (26.08.2026)

## ANTET — cât de veche e predarea asta

- **ultima rescriere**: **2026-08-26**, *rescriere COMPLETĂ, nu petic*
- **pe commit**: `7e07265`
- **de ce completă și nu incrementală**: versiunea de dinainte fusese peticită de cinci ori într-o
  zi și ajunsese să se contrazică singură — titlul spunea „loturile 1 și 2", o secțiune spunea
  „192 de locuri, **0 scrise**", alta „loturile 1–5 sunt SCRISE", iar R55 apărea cu **cifra
  greșită** pe care o corectasem deja de două ture. *Un document care se contrazice nu e „parțial
  vechi": cine îl citește nu poate ști care rând mai e adevărat.* De aici înainte se **rescrie**,
  nu se peticește.
- **cine o rescrie și când**: **se rescrie ÎNAINTE de fiecare oprire.** Regula stă aici fiindcă a
  fost încălcată de patru ori: 22.08 (trei afirmații false), 24→25.08 (**38 de commituri** în
  urmă), 26.08 dimineața (avertismentul a sunat pe **trei rapoarte la rând** și a fost raportat de
  fiecare dată fără să fie executat), 26.08 seara (a cerut-o Costin explicit, a doua oară).
  **Lecția e despre avertismente, nu despre hook:** un avertisment care se raportează corect și nu
  se execută e o linie de raport, nu o gardă.
- **gardat**: `scripts/githooks/pre-commit` **avertizează** când `HEAD` e cu mai mult de **10**
  commituri mai nou decât ultimul care a atins fișierul ăsta, iar `core/test_predare_proaspata.py`
  nu lasă avertismentul să dispară tăcut. **Avertizează, nu blochează** — un blocaj pe fiecare
  commit ar face din predare un impozit pe reparațiile mici.

## STAREA LA PREDARE

Poartă verde: **3267 teste** ✓ · 10 skip · 14 xfail · ruff OK · verificator **TOTAL 0** · site 200 ·
four-way `HEAD = origin/main = backup/lant-2026-08-26 = 7e07265`, proces viu pornit **după** commit.
*(Cifra de teste se reverifică rulând poarta, nu se crede pe cuvânt.)* Rămân artefacte
**neurmărite** în `frontend_test/` din rulările vizuale, plus `LOT_*_VERIFICARI.md`; nu sunt
modificări.

**Unde suntem**: **E1, faza 1.** **Cifrele nu se scriu aici** — se derivă cu `scripts/raport_b.py`,
sursa secțiunii 6 a fiecărui raport. *(Ce urmează e o fotografie de la `7e07265`, ca să nu porniți
orb; se re-derivă, nu se crede.)* Interdicții: MĂSURATE 21 · PARȚIAL 16 · NEMĂSURABILE 1 ·
NEÎNCEPUTE 38. Restanțe deschise **36** (E1: **13**), rezolvate **24**.

**Pasul curent, și e al lui Costin, nu al meu:** `TRASEE_VERIFICARI.md` — **150 din 192 de locuri
scrise, 42 goale**. Se citesc în **7 loturi de câte 30** (`scan_trasee.py --loturi N`).
**Loturile 1–5 sunt scrise. Lotul 6 e dat** (`~/iconta_nou/LOT_6_VERIFICARI.md`, 30 de pași).
**Rămâne lotul 7 — ultimul, 12 pași.** **Nu se regenerează fișierul** — regenerarea șterge ce s-a
scris.

**Forma lotului, fixată 26.08:** fiecare pas poartă **garda** (`garda X · rol:… · fără rol`) și
rândul `*ce face: …*`, care distinge ce e măsurat pe rută (`scrie …`) de ce e moștenit de la modul
(`poate atinge, prin modul (PLAFON, nemăsurat pe rută)` — **R53**). Loturile 1 și 2 au fost date
fără gardă; lotul 1 a primit și formularea veche a efectului (**20 din 30** de pași stăteau pe o
etichetă schimbată integral, 10 nu, 0 mixte — lista e în raportul turei).

## CE S-A ÎNTÂMPLAT ÎN ZIUA ASTA — ce contează pentru cine continuă

**Șase ture, ~34 de commituri.** Detaliul fiecărei restanțe e în `CONFORMITATE.md`, cu `măsurat la`
și `pe commit`; aici stă doar ce schimbă felul în care lucrezi mâine.

- **R33 — ÎNCHISĂ, varianta b′′.** `echilibru_perioada` e legat **lângă** `verifica_balanta`,
  `BALANTA_INEGALA` a ieșit fiindcă era **tautologică** (probat: 0 din 2000 de seturi aleatorii o
  puteau aprinde), iar ecranul arată **un singur rând „Echilibru"** cu ce a găsit fiecare.
  *Premisa comenzii inițiale („logică paralelă") era falsă — de-aia s-a măsurat înainte de a alege.*
- **R54 — ÎNCHISĂ. Contul din corpul cererii SE REFUZĂ**, nu se semnalează. `core/cont_valid.py`,
  legat în **19** din 27 de citiri; **8 rămân în clichet**, fiecare cu motivul **citit la sursă**.
  Refuzul numește contul ȘI unde se creează: *„Contul 7O7 nu există în planul firmei (câmpul
  «cont_venit»). Îl adaugi din Plan de conturi (Import date › Plan de conturi)."*
- **Poarta de coadă s-a MUTAT la intrare.** „Coadă = gata de depus" e ce spune ecranul
  contabilului; ce e generat-și-nevalidat apare separat. Escape: `motiv_trecere`.
- **R55, R56, R57 — REZOLVATE** (marcate pe `19db8b0`, în `abc0bc2`). Roluri pe efect, nu pe nume:
  `plan-conturi`, `jurnal/{id}/valideaza`, `amortizare`, `bonuri/{id}/aproba`, `horeca/raport-z`,
  `reges-config`, `reges-poll`. Pe calea de API, factura cu linie de stoc **se refuză** fără
  `marfa_pleaca_cu_factura`.
- **R58 — poarta de închidere VERIFICĂ, redeschiderea LASĂ URMĂ.** `POST /perioade-blocate` refuză
  **422** pe ciorne sau pe blocajul existent din `inchidere_luna`. Tabelă nouă
  **`perioade_inchideri`**, append-only, cu constrângerea de motiv **în BAZĂ**. Migrare **17/17**
  scheme + oglindă în `tenant_template.sql`. **Rămâne deschisă** doar pentru ce a amânat Costin:
  echilibrul și orfanii ca posibile condiții.
- **R59 — CONSEMNATĂ, nu decisă.** Reevaluarea de imobilizare **nu atinge `mijloace_fixe`**: scrie
  o notă ciornă, iar `POST /amortizare` calculează din registrul rămas pe valoarea veche. Prag 2
  **măsurat**: 0 note de reevaluare pe toate cele 17 scheme.
- **Gard nou pe EFECT:** `core/test_rol_pe_efect.py` — rolul se cere după **ce face** ruta, nu după
  cum se numește. Mulțimea se derivă din AST, aserțiunea e pe **mulțime** (nu pe cardinal), cheia e
  **metodă + cale**. Cele **șase moduri de eșec** ale gardului sunt scrise în antetul lui, înaintea
  primei măsurători.
- **Baseline-urile vizuale NU se urmăresc în git** (decizia lui Costin). `baseline_scan` spune
  explicit când lipsește o referință — **absența nu se mai citește ca „STABIL"**.
- **`METODA_VERIFICARE.md` a primit trei secțiuni**: o gardă care încodează o decizie **numește axa**
  pe care păzește · o mutație care probează o calibrare trebuie să lovească **linia care face
  distincția** · un filtru învechit **nu produce zgomot, produce tăcere**.

## CIFRE INVALIDATE — nu se corectează, se RE-MĂSOARĂ

*O cifră ai cărei termeni nu se mai pot reconstitui se **invalidează**, nu se corectează.*

| cifra | unde apărea | de ce e invalidată |
|---|---|---|
| **131** (valori fiscale în afara registrului) | predarea din 22.08 | termenii recalculați pe domeniu lărgit de trei ori. Clichetul viu e în `core/test_constante_nesursate.py` |
| **„25 de trasee"** | comenzile din 24–25.08 | nu exista instrument care să le numere. Cifra care se poate reface e **35** |
| **„25 de rute predau un document, 17 fără rol"** (R52) | 25.08 dimineață | gardul citește doar **corpul rutei** și găsește **18** și **8**. Diferența e **raza**, nu progresul. Clichetul stă pe **8** |
| **„129 de rute schimbă date fără rol"** | predarea din 26.08 dimineață | raza nu se mai poate reconstitui. Re-măsurat pe **metodă + cale** la `7e07265`: **236 de rute ne-GET, din care 145 fără nicio verificare de rol**. **145 > 129 nu e regres** — e alt domeniu |
| **„R55: șapte rute"** | comanda și predarea din 26.08 | proxy pe **numele grupului**. Real: **40** de rute în clasă, din care **36 scriu `ciorna`** (deci criteriul nu li se aplică) și **3 scriu `validata` direct** |
| `STALE_BAZA_BASELINE = 14` | `core/test_agenda.py` | măsurată pe graful conflat |

## FRONTURI DESCHISE, în ordine

1. **`TRASEE_VERIFICARI.md` — îl completează Costin.** 42 de locuri rămase, **un lot pe tură**.
   Eu dau lotul, el scrie verificările, trec la următorul. **Lotul 7 e ultimul.** Până se scriu
   toate, inventarul de trasee e o **hartă a codului**, nu o listă de verificare.
2. **Trei cerințe pe masa lui Costin, din raportul de la `7e07265`:** (1) R59 — reevaluarea
   actualizează registrul, sau aplicația **spune** divergența? (2) `firma-profil/date` primește
   `admin_firma`? Scrie câmpurile pe care se sprijină **nouă declarații** și n-are rol — punct orb
   al gardului mecanic, fiindcă scrie în `firma_profil`, nu `validata`. (3) Se construiește
   verificarea „suma mișcărilor de articol dintr-o lună se regăsește în descărcarea lunii"?
3. **Cele 145 de rute ne-GET fără rol.** Criteriul lui Costin — *ce schimbă ce datorează firma* —
   e aplicat pe clasele numite. Restul se triază pe **același** criteriu, iar cifra trebuie să
   devină **clichet** — azi nu e.
4. **Poarta de închidere n-are clichet.** Are o probă funcțională pe schemă efemeră, nu un test
   care asertează că refuză. Scris în R58 și în `TESTE.md`, cu ce ar trebui cablat.
5. **Pragul 3 din triaj** — amânat de zece ture, cea mai mare datorie: îngustarea
   Registrului-inventar la partidă dublă, registrul de evidență fiscală pe partidă simplă
   (`rip_api` + `d212_engine`), apoi deductibilitatea per operațiune.
6. **R50** — ștergerea unui cabinet nu curăță tabelele partajate. Două firme-fantomă, 44 de rânduri
   de audit pe un tenant care nu mai există.
7. **R5, R6** (încrederea în corpus) — deschise de peste 108 commituri, și blochează tot 1a.
   **R8, R9** — peste 102 fiecare.
8. **Cele 91 de rute ne-documentare** — declarate ca atare în inventar, dar nimeni n-a verificat că
   declarația e adevărată pentru fiecare.
9. **`core/compensare.py`** — singurul modul rămas nelegat din cele patru, pinat cu motivul.

## CE TREBUIE ȘTIUT DESPRE DATE, ÎNAINTE DE ORICE MĂSURĂTOARE

Măsurat 25–26.08, pe toate cele 17 firme:

- **evidența e concentrată în două firme** — `tenant_013` are rânduri în 26 de tabele, `tenant_003`
  în 14; patru firme au **exact două**;
- **41 de facturi · 34 de note · 24 de salariați · 2 state de plată · 55 de declarații depuse ·
  3 mijloace fixe active · 0 note de reevaluare · 0 pontaje · 0 operațiuni de partidă simplă ·
  0 NIR-uri**;
- **12 conturi în 7 cabinete**, din care **un singur `angajat`** — fără nicio firmă atribuită.
  **Patru-ochi nu se poate exercita azi pe nicio firmă**, deci nu se inventează scenarii de test pe
  cabinete care nu există;
- **`public.api_chei` = 0** — nicio cheie de API n-a fost creată vreodată. Orice schimbare pe calea
  de integrare e prag 2 azi;
- **`public.spv_token` = 0** și **`reges_chei` = 0** — e-Factura, e-Transport și REGES se opresc la
  pasul „token", nu la marginea ANAF;
- **mediul de test e-Factura EXISTĂ și e cel implicit**; ce lipsește e certificatul.

**Punctul orb e FIRMA, nu ecranul:** un scan vede doar stările pe care le produc datele firmei pe
care rulează.

## CUM SE RULEAZĂ CEVA CARE ARE NEVOIE DE BAZĂ

Shell-ul neinteractiv **nu** are `DB_*` în mediu. Nu căuta credențiale — folosește exact
mecanismul testelor: `conftest.py` sursează `~/.iconta/db.env` la import.

```python
import sys; sys.path.insert(0, "/home/costin/iconta_nou")
import conftest            # sursează db.env, ca la pytest
from core import db
```

Pentru un script din `scripts/`: `runpy.run_path("scripts/x.py", run_name="__main__")` după
`import conftest`, cu `sys.argv` pus manual.

## CE SĂ NU FACI

- **Nu porni de la un nume primit în comandă fără să-l cauți la sursă.** Comenzi succesive au numit
  `estimare_impozit`, `_recalc()`, „ecranul POS", „cele 12 constante", „3750 în JS", „25 de
  trasee", „jurnalul de vânzări" — **majoritatea nu existau**. Caută **eticheta pe care o vede
  omul**, nu doar identificatorul.
- **Nu măsura pe un PROXY.** Trei erori într-o singură zi, toate ale mele: **numele funcției**
  (R33 — „a doua implementare" era falsă), **numele grupului** (R55 — „7 rute" erau 40), **calea
  fără metodă** (R56 — am citit garda `GET`-ului și am scris-o în dreptul `PUT`-ului). Se măsoară
  pe **metodă + cale**, pe **efect**, pe **conținut**.
- **Nu ghici numele unei tabele.** Lista reală se regenerează din bază: `scan_trasee.py --tabele`.
- **Nu te încrede într-un fișier generat fără să-i verifici vechimea.** `trasee_tabele.json` era
  mai vechi decât `artefacte_produse`, deci filtrul tăia o tabelă **reală**, iar trei trasee au
  rămas clasificate greșit o zi întreagă. **Un filtru învechit nu produce zgomot, produce TĂCERE.**
  *(Garda scrisă pentru asta mi-a prins azi propria tabelă nouă, `perioade_inchideri`.)*
- **Un tabel nou cere trei locuri, nu unul**: DDL-ul (sursă unică în `core/migrare_*.py`), oglinda
  în `tenant_template.sql`, **și clasificarea în perimetrul firmelor** din `ISTORIC_TENANTI.md` —
  un tabel gol e ambiguu, iar garda de perimetru refuză ambiguitatea. Plus regenerarea filtrului.
- **Antetul nu poartă stări care se pot confrunta cu un câmp.** Am scris „R55, R56, R57 sunt
  REZOLVATE" în antetul lui `CONFORMITATE.md` și a picat
  `test_deciziile_numite_in_antet_sunt_DESCHISE`. Starea se citește din câmpul `stare`. *Dacă o
  propoziție se poate confrunta cu o cifră, nu e a antetului — e a derivatorului.*
- **Un refuz care ajunge la om e o AFIRMAȚIE**, deci poartă `fel` din nomenclator (`core/afirmatii.py`),
  nu proză într-un dicționar. Un refuz de închidere e `neconformitate` — cu `unde` și `regula`.
  `afirmatie()` ridică dacă lipsește un câmp, deci proba se face **și la runtime**, nu doar pe AST.
- **Nu lega o rută de un modul după un nume, fără să verifici că numele nu e umbrit local.**
  `from core import stocuri_api as _s` **în corp**, și `with conn.cursor() as _c` peste
  `from core import casa_api as _c`. **O atribuire falsă e mai rea decât o absență** — trece verde.
- **Nu căuta un șir într-un f-string ca și cum ar fi text.** `f"INSERT INTO {schema}.x"` nu conține
  `{schema}` — `FormattedValue` nu e text. Un detector construit așa vede **zero** și pare verde.
- **Nu asertui pe text într-o gardă nouă.** Clichetul 50 e per fișier, iar **un fișier nou pornește
  de la zero**. Se trece pe **seturi**, pe **structură**, pe **noduri de AST** — iar dacă nu se
  poate, motivul se scrie lângă gardă.
- **Nu înlocui intrări în `sys.modules` ca să falsifici un modul.** `from core import d112` citește
  **atributul de pe pachet**. Se folosește `monkeypatch` pe **funcții**.
- **Nu ținti o mutație pe orice linie din funcția pe care o probezi.** Poate pica alt test, din alt
  motiv, iar atunci proba confirmă altceva. Instanța: poarta `INSERT|UPDATE|DELETE` se
  scurtcircuita înaintea liniei mutate. **Bucla de mutații ține numele testului AȘTEPTAT.**
- **Nu presupune că un gard care pică te contrazice.** Poate păzi o decizie de pe **altă axă**.
  Instanța: `test_nota_contabila_NU_cere_admin_firma` încoda R42 (nota nu e artefact predat); R55
  punea rol fiindcă schimbă starea. **Nu se relaxează — se numește axa.**
- **Nu edita scripturi de conversie din shell.** Escapările se rup pe ghilimelele românești, pe
  `\u` și pe `\n`. Se scrie **fișierul** pe stație, se trimite octet cu octet (`cat fișier | ssh …`),
  iar scriptul de patch **rulează pe server** (`METODA` §10.3).
- **Nu închide un ghilimel românesc cu `"` ASCII într-un literal Python.** Încheie ȘIRUL, nu
  citatul, iar eroarea apare o linie mai jos. S-a întâmplat de **patru ori** într-o tură. Și
  **nu „repara" automat**: un înlocuitor care nu știe unde se termină literalul strică și șirurile
  corecte — a stricat trei într-un fișier pe care încerca să-l repare.
- **Nu rula un RED-proof cu `git checkout`** când arborele are muncă necomisă. **Un RED-proof pe un
  REFUZ scrie**: verificarea nu e „testul a picat", ci **„a picat ȘI n-a rămas nimic în urmă"** —
  se compară sha256 înainte/după.
- **Nu regenera `TRASEE_VERIFICARI.md`.** E singurul document scris de om.
- **Nu curăța `__pycache__` doar la sfârșit.**
- **Nu citi un `or "<implicit>"` ca pe o validare.** E o mască: transformă `None` și `""` în
  implicit și lasă `"   "` să treacă verbatim. 19 situri.
- **Nu scrie o aserțiune pe un rând `poate atinge, prin modul`.** Acela e un plafon superior, nu o
  măsurătoare pe rută: 108 din 192 de pași îl poartă (R53).
- **Nu scrie un motiv de clichet din analogie.** E o afirmație despre cod, deci poate fi falsă
  (R16). Un motiv presupus transformă „n-am făcut" în „nu se poate", iar atunci clichetul nu mai e
  datorie, e justificare.
- **Nu citi „STABIL" din `baseline_scan` ca pe o comparație.** În modul implicit e **self-diff**
  între două capturi din aceeași rulare. Pentru comparație: `--compare`.
- **Nu lărgi un scan ca să scadă un număr.** S-a încercat de două ori.
- **Nu recicla un nume într-un fișier de gărzi.** **Nu declara o clasă golită pe un singur limbaj**
  (`METODA` §17).
- **Nu amâna rescrierea predării fiindcă ai raportat-o.** Vezi antetul.
