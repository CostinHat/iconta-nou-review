Citeste CLAUDE.md §2.2 (structura raportului) si §2.3 (lant, siguranta, limba - pct.11 poarta verde vizuala) + ARHITECT.md "FORMA COMENZII" (7 puncte), apoi acest PREDARE_LANT.md, inainte de a incepe.

# PREDARE LANȚ — patru decizii aplicate, loturile 1 și 2 scrise (26.08.2026)

## ANTET — cât de veche e predarea asta

- **ultima rescriere**: **2026-08-26**, *a patra din ziua asta*
- **pe commit**: `3c774dc`
- **cine o rescrie și când**: **se rescrie ÎNAINTE de fiecare oprire, nu la câteva zile.** Regula e
  scrisă aici fiindcă a fost încălcată de trei ori. Prima dată (22.08) versiunea veche conținea trei
  afirmații false. A doua oară (24→25.08) a rămas **38 de commituri** în urmă. A treia oară e **azi**:
  avertismentul hook-ului a sunat pe **trei rapoarte la rând** (12, apoi 15 commituri) și a fost
  raportat de fiecare dată, dar rescrierea s-a amânat până a cerut-o Costin explicit.
  *Un PREDARE_LANȚ care instruiește sesiunea nouă să-l citească primul și e vechi de 15 commituri e
  mai rău decât unul absent: cine îl citește n-are cum să știe care rând mai e adevărat.*
  **Lecția e despre avertismente, nu despre hook:** un avertisment care se raportează corect și nu se
  execută e o linie de raport, nu o gardă.
- **gardat**: `scripts/githooks/pre-commit` **avertizează** când `HEAD` e cu mai mult de **10**
  commituri mai nou decât ultimul care a atins fișierul ăsta, iar `core/test_predare_proaspata.py` nu
  lasă avertismentul să dispară tăcut. **Avertizează, nu blochează** — un blocaj pe fiecare commit ar
  face din predare un impozit pe reparațiile mici.

## STAREA LA PREDARE

Poartă verde: pytest (suita întreagă, prin hook) · ruff OK · verificator **TOTAL 0** · site 200 ·
four-way HEAD = `origin/main` = ramura de backup = procesul viu. *(Cifra de teste se reverifică
rulând poarta, nu se crede pe cuvânt.)* Rămân artefacte **neurmărite** în `frontend_test/` din
rulările vizuale; nu sunt modificări.

**Unde suntem**: **E1, faza 1**. *(La `d0bd859` — cifrele de mai jos se re-derivă, nu se cred.)* **Cifrele nu se scriu aici** — se derivă cu `scripts/raport_b.py`,
sursa secțiunii 6 a fiecărui raport. La `4926e15`: interdicții MĂSURATE 21 · PARȚIAL 16 ·
NEMĂSURABILE 1 · NEÎNCEPUTE 38; restanțe deschise **32** (E1: **9**).

**Pasul curent, și e al lui Costin, nu al meu:** `TRASEE_VERIFICARI.md` — **192 de locuri goale**,
câte unul per pas care schimbă ceva. Fiecare poartă acum și rândul `*ce face: …*`. Se citesc în
**7 loturi de câte 30** (`scan_trasee.py --loturi N`). **Nu se regenerează fișierul** — regenerarea
șterge ce s-a scris.

## CE S-A CONSTRUIT ÎN ZIUA ASTA (28 de commituri)

Ziua a avut trei jumătăți; astea sunt cele care contează pentru cine continuă.

- **Inventarul traseelor** — `scripts/scan_trasee.py` + `core/test_trasee.py`: **35 de trasee**, **403
  rute**, **orfane 0**, clasificare **MECANIC 30 · MANUAL 5** (PARȚIAL a ajuns la **0** azi), plus
  modul `--loturi` și scheletul `--verificari`. **Partea XII din `TRASEE.md` e GENERATĂ** (`--md`), iar
  garda compară blocul cu ce produce instrumentul: **blocul nu se editează cu mâna**.
- **R41, R44, R45, R49, R51, R42, R52 — închise.** R30 măsurată și acceptată. Detaliile fiecăreia sunt
  în `CONFORMITATE.md`, cu `măsurat la` și `pe commit`.
- **R42, criteriul complet.** Costin: *„tot ce iese către o autoritate sau către un om, plus tot ce
  închide sau redeschide o perioadă"*, iar la cele patru întrebări rămase: nota contabilă **nu** e
  artefact predat (primește P15, nu rol) · completarea manuală e parte din declarație **după**
  generare · trecerea de regim cere `admin_firma` pe criteriul nou *„ce schimbă ce datorează firma"* ·
  pornirea/oprirea unui canal cere `admin_firma`.
- **R33, jumătatea de prag 1.** Semnalul notă-vs-D112 apare **la propunere** și **semnalează**, nu
  blochează, cu **ambele cifre**. Legând-o s-a descoperit că modulul era nelegat **în întregime**:
  salariile nu deveneau niciodată notă contabilă.
- **C6 — ierarhia surselor.** Norma câștigă; validatorul e **constrângere**, nu sursă.
  `core/nomenclatoare.py` + `core/test_nomenclator_pe_norma.py`. **Tensiunea P8 ↔ interdicția 16 din
  predarea anterioară e REZOLVATĂ** — răspunsul era deja scris în `PLAN_ARHITECTURA`, Partea 0,
  Pasul 4, și nimeni nu-l citise.
- **METODA §25** — *când două reguli scrise se contrazic, câștigă cea păzită, și o face tăcut.*
- **`SABLON_RAPORT.md`** — ordinea 0–7, cerințele numerotate la final, și ce se așteaptă înapoi de la
  Costin (părțile A și B).

## CIFRE INVALIDATE — nu se corectează, se RE-MĂSOARĂ

*O cifră ai cărei termeni nu se mai pot reconstitui se **invalidează**, nu se corectează.*

| cifra | unde apărea | de ce e invalidată |
|---|---|---|
| **131** (valori fiscale în afara registrului) | predarea din 22.08 | termenii recalculați pe domeniu lărgit de trei ori. Clichetul viu e în `core/test_constante_nesursate.py` |
| **„25 de trasee"** | comenzile din 24–25.08 | nu exista instrument care să le numere. Cifra care se poate reface e **35** |
| **„25 de rute predau un document, 17 fără rol"** (R52) | măsurătoarea din 25.08 dimineață | gardul care o păzește, cu aceleași marcaje dar citind doar **corpul rutei**, găsește **18** și **8**. Diferența e **raza**, nu progresul. Clichetul stă pe **8** — cifra pe care instrumentul o poate recalcula. Restul până la 17 **nu e păzit** |
| `STALE_BAZA_BASELINE = 14` | `core/test_agenda.py` | măsurată pe graful conflat |

## FRONTURI DESCHISE, în ordine

1. **`TRASEE_VERIFICARI.md` — îl completează Costin.** 192 de locuri, **0 scrise**. Până se scriu,
   inventarul de trasee e o **hartă a codului**, nu o listă de verificare. E cel mai mare lucru rămas,
   și **nu e muncă de-a mea**. **Cadența, fixată 25.08: un lot pe tură** — eu dau lotul
   (`scan_trasee.py --loturi N`), el scrie verificările în fișier, apoi trec la următorul.
   **Loturile 1–4 sunt SCRISE** (120 de locuri completate, **72 rămase**). **Lotul 5 e dat**,
   în forma nouă. **Din 26.08 lotul poartă și GARDA fiecărui pas** (`garda X · rol:… · drept:…`),
   nu doar efectul — cerut de Costin, fiindcă altfel cine scrie verificarea trebuie s-o caute în
   alt fișier. Loturile 1 și 2 au fost date fără ea. **Rândul `*ce face:*` distinge** ce e măsurat pe rută (`scrie …`)
   de ce e moștenit de la modul (`poate atinge, prin modul (PLAFON, nemăsurat pe rută)`) — **R53**.
   **Lotul 1 a primit formularea veche**, iar Costin a cerut lista celor afectate: **20 din 30** stăteau
   pe o etichetă care s-a schimbat integral, **10** nu, **0** mixte. Lista e în raportul turei.
2. **R33 și R54 — ÎNCHISE pe partea care blochează (26.08.2026).** `echilibru_perioada` e legat lângă
   `verifica_balanta`, tautologia e scoasă, iar cele două se arată ca **un singur** „Echilibru".
   Contul din corpul cererii **se refuză** dacă nu e în planul firmei (`core/cont_valid.py`, legat în
   **19** din 27 de citiri; 8 rămân în clichet, fiecare cu motivul **citit la sursă**).
   **Nicio decizie nu mai blochează.** Deschise fără să blocheze: **R53** (inventarul supra-atribuie
   scrieri), **R55** (șapte rute scriu evidență contabilă, șase fără rol, una cu — o regulă care nu
   există), **R56** (trei rute cu credențiale externe, fără rol). Din cele patru module nelegate mai e
   **unul**: `compensare`.
3. **Cele 129 de rute care schimbă date fără verificare de rol.** Criteriul lui Costin e aplicat pe
   clasele numite (28 de rute în patru aplicări). Restul se triază pe **același** criteriu, iar cifra
   trebuie să devină clichet — azi nu e.
4. **Pragul 3 din triaj** — amânat de zece ture, cea mai mare datorie: îngustarea Registrului-inventar
   la partidă dublă, registrul de evidență fiscală pe partidă simplă (`rip_api` + `d212_engine`), apoi
   deductibilitatea per operațiune.
5. **R50** — ștergerea unui cabinet nu curăță tabelele partajate. Două firme-fantomă, 44 de rânduri de
   audit rămase pe un tenant care nu mai există.
6. **R5, R6** (încrederea în corpus) — deschise de peste 95 de commituri, și blochează tot 1a.
7. **R8, R9** — deschise de peste 90 de commituri fiecare.
8. **Cele 91 de rute ne-documentare** — declarate ca atare în inventar, dar nimeni n-a verificat că
   declarația e adevărată pentru fiecare.

## CE TREBUIE ȘTIUT DESPRE DATE, ÎNAINTE DE ORICE MĂSURĂTOARE

Măsurat 25.08, pe toate cele 17 firme:

- **evidența e concentrată în două firme** — `tenant_013` are rânduri în 26 de tabele, `tenant_003` în
  14; patru firme au **exact două**;
- **41 de facturi · 34 de note · 24 de salariați · 2 state de plată · 55 de declarații depuse ·
  0 pontaje · 0 operațiuni de partidă simplă · 0 NIR-uri**;
- **12 conturi în 7 cabinete**, din care **un singur `angajat`** — fără nicio firmă atribuită și fără
  niciun drept fin. **Patru-ochi nu se poate exercita azi pe nicio firmă**, deci nu se inventează
  scenarii de test pe cabinete care nu există;
- **`public.spv_token` = 0** și **`reges_chei` = 0** — e-Factura, e-Transport și REGES se opresc la
  pasul „token", nu la marginea ANAF;
- **mediul de test e-Factura EXISTĂ și e cel implicit**; ce lipsește e certificatul.

## CE SĂ NU FACI

- **Nu porni de la un nume primit în comandă fără să-l cauți la sursă.** În ultimele ture, comenzi
  succesive au numit `estimare_impozit`, `_recalc()`, „ecranul POS", „cele 12 constante", „3750 în
  JS", „25 de trasee", „jurnalul de vânzări" — **majoritatea nu existau**. Caută **eticheta pe care o
  vede omul**, nu doar identificatorul.
- **Nu ghici numele unei tabele.** Lista reală se regenerează din bază: `scan_trasee.py --tabele`.
- **Nu te încrede într-un fișier generat fără să-i verifici vechimea.** `scripts/trasee_tabele.json`
  era mai vechi decât tabela `artefacte_produse`, deci filtrul tăia o tabelă **reală**. Trei trasee au
  rămas clasificate PARȚIAL — *„produce și nu se păstrează"* — o zi întreagă după ce persistența
  fusese construită. **Un filtru învechit nu produce zgomot, produce TĂCERE.**
- **Nu lega o rută de un modul după un nume, fără să verifici că numele nu e umbrit local.** Două
  forme ale aceleiași greșeli: `from core import stocuri_api as _s` **în corp** (ruta de NIR primea
  `salarizare`), și `with conn.cursor() as _c` peste `from core import casa_api as _c` (o rută primea
  `casa_api` și trei tabele în care nu scrie). **O atribuire falsă e mai rea decât o absență** — trece
  verde. La reparație au ieșit **două** atribuiri false, nu una.
- **Nu căuta un șir într-un f-string ca și cum ar fi text.** `f"INSERT INTO {schema}.x"` nu conține
  `{schema}` — `FormattedValue` nu e text. Un detector construit așa vede **zero** și pare verde.
- **Nu asertui pe text într-o gardă nouă.** Clichetul 50 e per fișier, iar **un fișier nou pornește de
  la zero**. Azi au picat 7+3 aserțiuni pe text; toate s-au putut trece pe **seturi**, iar una a cerut
  o schimbare în cod (statusul notei era scris în interiorul SQL-ului, deci nu se putea asertui
  altfel; a devenit parametru).
- **Nu înlocui intrări în `sys.modules` ca să falsifici un modul.** `from core import d112` citește
  **atributul de pe pachet**. O probă construită așa măsoară funcția reală pe o bază inexistentă și dă
  zero, fals. Se folosește `monkeypatch` pe **funcții**.
- **Nu declara o clasă golită pe un singur limbaj** (`METODA` §17).
- **Nu recicla un nume într-un fișier de gărzi.**
- **Nu lărgi un scan ca să scadă un număr.** S-a încercat de două ori.
- **Nu edita scripturi de conversie din shell.** Escapările se rup pe ghilimelele românești, pe `\u` și
  pe `\n`. Azi s-a întâmplat de **trei ori**, iar de două ori a stricat un fișier de teste care a
  trebuit restaurat cu `git checkout`. Se scrie **fișierul** pe stație, se trimite octet cu octet
  (`cat fișier | ssh …`), iar scriptul de patch **rulează pe server** (`METODA` §10.3).
- **Nu rula un RED-proof cu `git checkout`** când arborele are muncă necomisă.
- **Un RED-proof pe un REFUZ scrie.** Verificarea nu e „testul a picat", ci **„testul a picat ȘI n-a
  rămas nimic în urmă"**. Se compară sha256 înainte/după.
- **Nu regenera `TRASEE_VERIFICARI.md`.** E singurul document scris de om.
- **Nu curăța `__pycache__` doar la sfârșit.**
- **Nu citi un `or "<implicit>"` ca pe o validare.** E o mască: transformă `None` și `""` în implicit
  și lasă `"   "` să treacă verbatim. 19 situri, iar consecința era invizibilă în trei straturi deodată.
- **Nu scrie o aserțiune pe un rând `poate atinge, prin modul`.** Acela e un plafon superior, nu o
  măsurătoare pe rută: 108 din 192 de pași îl poartă (R53).
- **Nu scrie un motiv de clichet din analogie.** E o afirmație despre cod, deci poate fi falsă (R16).
  Instanța: eram gata să scriu „modul pur, fără conn/schema" pentru șapte intrări; citite la sursă,
  aveau și `conn`, și `schema`, și erau în `try`. Un motiv presupus transformă „n-am făcut" în „nu se
  poate", iar atunci clichetul nu mai e datorie, e justificare.
- **Nu închide un ghilimel românesc cu `"` ASCII într-un literal Python.** Încheie ȘIRUL, nu citatul,
  iar eroarea apare o linie mai jos. S-a întâmplat de **patru ori** într-o tură. Și **nu „repara"
  automat**: un înlocuitor care nu știe unde se termină literalul strică și șirurile corecte — a
  stricat trei într-un fișier pe care încerca să-l repare.
- **Nu citi „STABIL" din `baseline_scan` ca pe o comparație.** În modul implicit e **self-diff** între
  două capturi din aceeași rulare. Pentru comparație: `--compare`. Instanța e a mea, în raportul de ieri.
- **Nu presupune că un gard care pică te contrazice.** Poate păzi o decizie de pe ALTĂ axă. Instanța:
  `test_nota_contabila_NU_cere_admin_firma` încoda R42 (nota nu e artefact predat); R55 punea rol
  fiindcă schimbă starea. Nu se relaxează — se numește axa. `METODA`, secțiunea din 26.08.
- **Nu măsura o gardă cu un grep pe CALE.** Pe aceeași cale pot exista `GET` și `PUT` cu gărzi
  diferite — iar tu o vei citi pe prima. Instanța: am scris „`woocommerce/config` fără rol" citind
  garda GET-ului, când PUT-ul avea `admin_firma` din 25.08. Se măsoară pe **metodă + cale**.
- **Nu amâna rescrierea predării fiindcă ai raportat-o.** Vezi antetul.
