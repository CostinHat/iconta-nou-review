# CLAUDE.md — Reguli permanente de lucru pe proiectul iConta

Acest fișier e citit automat de Claude Code la începutul fiecărei sesiuni în acest
director. Conține regulile de lucru stabilite de Costin de-a lungul mai multor
sesiuni — nu sunt sugestii, sunt obligatorii, indiferent de presiunea de timp.

## Context general

iConta e o platformă de contabilitate SaaS (iconta.eu), solo founder Costin,
stack FastAPI + PostgreSQL (schema-per-tenant, `iconta_v2`) + vanilla JS ES
modules, pe server Hetzner (`costin@iconta-prod`, cod în `~/iconta_nou`,
serviciu `iconta-nou.service`, port 8010). Costin e în Bucureşti, comunică
tors, lucrează în sesiuni maraton, preferă corectitudine peste viteză.

## REGULA DE AUR — verificare la sursă (cea mai importantă)

**Înainte de a declara ceva "absent/inexistent/de construit/lipsă" SAU de a
scrie cod nou SAU de a folosi orice valoare fiscală — verifici la sursă și
ARĂȚI comanda de verificare, nu doar rezultatul.**

Trei surse obligatorii, în funcție de context:
1. **Cod**: `grep -rn` pe TOT `~/iconta_nou/` (nu doar fișierul pe care crezi
   că trebuie modificat) — infrastructura veche (`/opt/iconta`, port 8000)
   poate conține implementări pierdute la refacere; caută și acolo înainte
   de a declara ceva "de construit".
2. **Fiscal/legal**: sursă oficială ANAF/lege, NICIODATĂ din memorie. Pentru
   declarații (D1xx, D3xx, D4xx): validatorul oficial DUK instalat local
   (`~/duk/dist/lib/`, apelat prin `core/duk.py`, funcția
   `valideaza(xml, tip, an=, luna=)`) e judecătorul final — nu presupunerea
   din documentul PDF descărcat, care poate fi incomplet sau despre o altă
   versiune a formularului.
3. **UI/produs**: Design System (`DESIGN_SYSTEM.md`, v2.10+, 16 capitole) +
   `ICONTA_STATUS.md`.

**Niciodată nu se ghicesc valori — nici coduri fiscale, nici CUI/CNP de test,
nici formate XML, nici nume de coloane de bază de date.**

## CICLUL DE NECONFORMITATE (31.07.2026 — guverneaza tot restul)

Ne tinem de plan PANA cand intalnim o neconformitate. Atunci ne oprim si parcurgem, IN ORDINE,
cei patru pasi — nu se sare niciunul, nu se amana:

1. **OPRIRE.** Firul curent se suspenda. NU se noteaza neconformitatea ca datorie pentru mai
   tarziu — se trateaza acum.
2. **GENERALIZARE.** Se identifica CLASA, nu instanta. Se cauta TOATE aparitiile in tot codebase-ul
   INAINTE de a repara vreuna. "Bug la linia X" e formulare gresita; "clasa de bug X, N aparitii"
   e cea corecta.
3. **CORECTARE.** Peste toata aplicatia, nu doar unde a fost gasita.
4. **GARD.** Mecanism care face reaparitia IMPOSIBILA, nu improbabila (hook, ratchet, gard
   structural, test permanent). Fara acest pas, corectia se erodeaza. Abia dupa gard se revine la plan.

DE CE: disciplina singura cedeaza. Dovezi 31.07: poarta "pytest && git commit" ocolita prin subset;
markerii TEMEI fara gard; "or 0" supravietuind fiindca se cautase doar "or 21". Ce a TINUT au fost
MECANISMELE: hook pre-commit, ratchet, gard structural. Consecinta acceptata: ritmul scade — fiecare
neconformitate devine campanie. E pretul corect (cerut explicit de Costin).

## Metoda de investigare pentru bug-uri de validare fiscală (D1xx/D3xx/D4xx)

Lecția cea mai costisitoare din sesiunea de 16.07.2026 (peste 10 ore pe patru
declarații din cauza ghicitului repetat):

1. **Citește ÎNTREG documentul sursă o singură dată, înainte de a scrie orice
   cod.** Nu „citesc o parte, scriu, corectez, mai citesc o bucată" — asta
   e ghiceală mascată în iterații. Dacă documentul are 400+ linii, se citesc
   toate 400, nu primele 180.
2. **Dacă documentul PDF/oficial nu are structura XML exactă (nume atribute,
   obligativitate, valori permise)** — de multe ori documentele „structura_
   DXXX.pdf" descriu doar istoricul de modificări ale unui nomenclator, NU
   schema XML propriu-zisă — treci direct la extragerea din **validatorul
   instalat**: `unzip` pe jar-ul din `~/duk/dist/lib/DXXXValidator.jar`,
   `strings` pe clasele `.class` din **ultima versiune** (`vN` cu N maxim),
   citind TOATE atributele reale (`grep -E "^_[a-zA-Z]"` pe constant pool),
   nu doar primele care par relevante.
3. **Testează IZOLAT, cu date minime construite manual, NU doar pe date
   reale ale unei firme.** Un test pe profil real, incomplet (câmpuri goale)
   poate ocoli condiții ale validatorului fără să-ți dai seama — „valid pe
   un caz" nu înseamnă "structură completă". Construiește un profil minim
   cu toate câmpurile completate și validează acela separat.
4. **Validatorul DUK poate raporta eroarea greșit poziționată.** Dacă apare
   o eroare confuză, aparent fără legătură (ex. "CustomerID lipsă" pe o
   linie care vizual are CustomerID), verifică dacă nu cumva o secțiune
   ANTERIOARĂ în document (Header, MasterFiles) are o problemă reală care
   rupe parsarea — validatorul uneori raportează eroarea pe ultima secțiune
   parsată cu succes, nu pe cauza reală. Construiește un XML minim de la
   zero, secțiune cu secțiune, ca să localizezi exact unde apare prima
   discrepanță structurală.
5. **O singură corecție per rundă, apoi testezi din nou pe validator.** Nu
   se aplică trei ipoteze deodată "ca să fie mai rapid" — asta ascunde care
   fix a rezolvat ce.
6. **Fiecare reparație validă se comite cu mesaj care documentează:** ce
   era greșit, ce spune sursa oficială (citat/paraphrase scurt), ce s-a
   schimbat, dovada (stare=valid pe validator). Fișierul de teste al
   modulului (`core/test_dXXX.py`) apără explicit fiecare regresie găsită.

## Rotunjire fiscală

Contribuțiile/sumele fiscale se rotunjesc **aritmetic** (dacă partea
zecimală ≥ 0.5, se adaugă 1 la partea întreagă), NU bancar (`round()` din
Python folosește half-to-even, care dă rezultate greșite pe `.5` exact).
Orice rotunjire de sumă fiscală trebuie să folosească `Decimal` +
`ROUND_HALF_UP`, nu `round()` simplu — și `round()` Python NU trebuie aplicat
NICIODATĂ înainte de o funcție de rotunjire aritmetică proprie (dublă
rotunjire = rezultat greșit silențios).

## Date de test — CUI/CNP OBLIGATORIU verificate înainte de inserare

**Niciun CUI sau CNP de test nu se inserează în baza de date fără verificare
prealabilă a cifrei de control**, prin algoritmul oficial:

```python
# CUI (persoană juridică RO)
def cui_valid(cui):
    ch = [7,5,3,2,1,7,5,3,2]
    c = str(cui).strip()
    corp, ctrl = c[:-1].rjust(9,'0'), int(c[-1])
    s = sum(int(corp[i])*ch[i] for i in range(9))
    r = (s*10) % 11
    if r == 10: r = 0
    return r == ctrl

# CNP
def cnp_valid(baza12):
    ch = [2,7,9,1,4,6,3,5,8,2,7,9]
    s = sum(int(baza12[i])*ch[i] for i in range(12))
    c = s % 11
    return baza12 + str(1 if c == 10 else c)
```

Un CUI/CNP inventat "din cap" fără verificare a produs ore de investigație
falsă pe 16.07.2026 (validatorul confunda o dată de test greșită cu un bug
de cod real). Dacă ai nevoie de un CUI real pentru test (firmă cunoscută),
caută-l/verifică-l, nu-l inventa.

## Metoda "4 comenzi per temă"

Pentru orice temă de lucru (bug fix, feature mic, refactor local):
**maxim 2 comenzi de citire → 1 comandă de implementare → 1 comandă de
verificare+commit.** Patru comenzi, nu zece. Dacă o temă cere mai mult,
înseamnă că tema e prea mare și trebuie tăiată în bucăți mai mici, nu că
regula nu se aplică.

## Verificare funcțională reală, nu doar sintactică

- `node --check` / `py_compile` verifică DOAR sintaxa, nu comportamentul de
  runtime. După orice schimbare de backend care afectează o funcție apelată
  din alt fișier, rulează un test funcțional real (curl sau script Python
  care apelează funcția cu date reale) înainte de a declara "gata".
- Orice modificare de SQL cere test funcțional real pe Postgres (rulare
  reală a interogării, nu doar verificare de sintaxă) — string-urile SQL
  corupte sau coloanele inexistente nu sunt prinse de py_compile.
- Un query SQL prins într-un `try/except: pass` care eșuează silențios e un
  bug la fel de grav ca unul care crapă vizibil — de fapt mai grav, pentru
  că ascunde problema. Verifică mereu ce se întâmplă dacă interogarea din
  interiorul unui `try` chiar aruncă excepție.
- **Testele nu presupun gol un interval unde pot ajunge date reale.** Un
  fixture care scrie într-un tabel PARTAJAT (public.*, ex. declaratii_depuse)
  pe o perioadă plauzibilă (2026/luna curentă) intră în coliziune de PK cu
  prima depunere reală pe acel interval — testul „verde azi" pică mâine, fără
  ca cineva să fi schimbat cod. Fixture-urile pe tabele partajate folosesc
  perioade SINTETICE, evident nereale (an 2099) și/sau tenant_id sintetic,
  rulate în ROLLBACK. Lecție prinsă 22.07: prima depunere reală D300 pe
  tenant_002 2026/06 a intrat în coliziune cu un test care insera fabricat pe
  aceeași perioadă.

## Verificare prin mutație — două capcane

Verificarea prin MUTAȚIE (strici în cod ce verifică testul, confirmi că pică, apoi revert) are DOUĂ
capcane, ambele plătite pe 29.07.2026:

1. **`git checkout -- fișier` ȘTERGE lucrul NECOMIS.** Reverteaza la HEAD, nu la starea de dinainte
   de mutație. Dacă implementarea pe care o testezi e încă necomisă, o pierzi (pățit: proratarea din
   salarizare.py). REVERT prin backup de conținut, nu git checkout:
   `cp fișier /tmp/f.bak` → mută → testează → `cp /tmp/f.bak fișier`.
2. **`.pyc` stale otrăvește rulările următoare.** Bytecode-ul din `.py`-ul mutat rămâne în
   `__pycache__` chiar după ce `.py` a revenit (git status curat) → teste care pică fără cauză
   vizibilă (pățit: 2 teste D112 păreau poluate de alt test, ~10 pași pierduți). După orice rundă de
   mutație: `find . -name __pycache__ -type d -exec rm -rf {} +` (sau `PYTHONDONTWRITEBYTECODE=1`).
   Semnal de `.pyc` stale: un `print` de debug care „schimbă” rezultatul.

## Global-first pentru CSS/UI

Înainte de orice schimbare vizuală, verifică dacă elementul țintă e deja
acoperit de o regulă CSS globală — și spune explicit asta înainte de a
propune soluția.

## Reparație reală, nu patch

Când ceva trebuie corectat, elimini problema efectiv — fără cod mort, fără
căi comentate lăsate în urmă, fără dubluri de logică. Dacă găsești o
funcție/logică deja existentă care face ce ai vrut să construiești, o
refolosești/repari pe aia, nu construiești una paralelă.

## Design System

`DESIGN_SYSTEM.md` (canonic, pe server, în git) e sursa unică pentru orice
regulă vizuală. Înainte de orice cod de UI: citește regula relevantă din
DS și citeaz-o. Dacă regula nu există încă în scris — STOP, se stabilește
cu Costin întâi, nu se inventează un pattern generic. Orice regulă nouă de
UI intră simultan în `DESIGN_SYSTEM.md` ȘI în `verificator_conformitate.py`
(gardian automat), nu doar una din ele.

## Ce NU face Costin

- Nu vrea reflecții/scuze repetate de tip "ai dreptate" — direct la treabă.
- Nu vrea presupunerea că sesiunea s-a terminat fără să i se ceară explicit.
- Nu vrea aceeași comandă repetată de două ori (o dată în explicație, o
  dată în blocul de executat) — o comandă, o singură dată, în bloc.
- Nu vrea amânare ("las pe mai târziu", "documentăm limitarea") când a
  cerut explicit să nu se amâne nimic — dacă apare o limitare structurală
  reală care chiar cere o decizie de scop mai mare (schimbare de schemă,
  timp semnificativ), se explică clar și se cere decizia lui, nu se declară
  unilateral "gata pentru azi".

## Fișiere normative pe server (NU se editează local, doar prin SSH)

- `~/iconta_nou/DESIGN_SYSTEM.md` — reguli UI, v2.10+
- `~/iconta_nou/verificator_conformitate.py` — gardian mecanic pentru DS
- `~/iconta_nou/ISTORIC.md` — CE s-a făcut, când, ce commit (include fostul
  ICONTA_STATUS.md). APPEND-ONLY după FIECARE execuție (vezi 2.2.1); regula veche „doar la finalul zilei” ELIMINATĂ 04.08.2026. O execuție ulterioară care răstoarnă una din aceeași zi o SUPERSEDEAZĂ explicit, nu o rescrie
- `~/iconta_nou/DECIZII.md` — DE CE am făcut așa. Registru de decizii cu temei,
  alternative respinse și limite. Se ADAUGĂ cronologic (append-only), nu se editează istoria; o decizie răsturnată primește o intrare de PIVOT care o supersedează EXPLICIT.
  Nu e normativ — norma trăiește unde se aplică și se verifică mecanic
- `~/iconta_nou/ARHITECT.md` — reguli de conduită pentru arhitect (Claude în
  chat). Se citește la începutul fiecărei sesiuni; se predă prin copy-paste cu starea.
- `~/iconta_nou/LANSARE.md` — backlog
- `~/iconta_nou/FUNCTIONALITATI.csv` — registrul canonic al funcționalităților.
  Nicio funcționalitate nu trăiește în afara listei. Stări: LIVE / PLANIFICAT /
  PARTIAL (blocat din exterior, cu carență) / RESPINS / AMANAT — niciuna implicită
- `~/iconta_nou/ARHITECTURA_SPV.md` — decizii și parametri ANAF/SPV verificați la
  sursă (OAuth, blocantul SPVWS2, conectorul)
- `~/iconta_nou/anaf_surse/` — toate documentele oficiale ANAF descărcate
  (structuri XML, scheme SAF-T xlsx, versiuni.xml) — verifică AICI ÎNTÂI
  înainte de a căuta din nou pe internet, poate exista deja sursa.

## Deciziile se scriu, nu rămân în chat
Orice răspuns la un STOP (întrebare de direcție, arhitectură, fiscal, UI) este o
DECIZIE și se scrie în `DECIZII.md` — cu temei, alternativa respinsă și limita.
Motivul: sesiunea de chat se închide, codul rămâne fără explicație. Peste trei luni
nimeni nu mai știe de ce pontajul e informativ sau de ce lipsește pragul +14.
Formatul e în capul lui `DECIZII.md`.
Norma rezultată intră unde se APLICĂ și se VERIFICĂ mecanic (DESIGN_SYSTEM.md +
verificator, docstring de modul). `DECIZII.md` trimite acolo. Două surse de adevăr = drift.

## Reorganizarea unui ecran existent = STOP
Adăugarea unui element la sfârșitul unui rând = implementare, se face fără întrebare.
Rearanjarea a ce era deja acolo (ordine, rupere de rânduri, mutare între zone) =
schimbare de direcție, cere confirmare. Verificatorul prinde clasele greșite, NU
prinde așezarea — de aceea aici disciplina nu e mecanică.

## Infrastructură

- Restart aplicație: `sudo systemctl restart iconta-nou` (NU pkill+nohup,
  deprecat)
- `iconta.service` (fără `-nou`) = build vechi, port 8000, sursă istorică
  de verificat cu grep înainte de a declara ceva "de construit"
- Python venv: `/opt/iconta/venv/bin/python3` (nu Python de sistem)
- DB: schema-per-tenant în `iconta_v2`, `tenant_002` = firmă de test
  (DANTE INTERNATIONAL SA, plătitoare TVA, regim profit)

## Stare la 16.07.2026 (ultima sesiune majoră)

Toate cele 9 declarații fiscale (D100, D101, D112, D205, D300, D301, D390,
D394, **D406/SAF-T**) — confirmate `stare: valid, FARA ERORI` pe validatorul
oficial, atât izolat (profil minim construit manual) cât și pe date reale.

D406 reparat pe 16.07.2026 (commit `d68dbfc`), 5 discrepanțe structurale față
de XSD-ul oficial (`/opt/duk/saft/saft.xsd`) + regula semantică din
`d406_schema_anaf.xlsx`: (1) `Transaction` cerea `CustomerID`+`SupplierID`
(lipseau; validatorul raporta greșit lipsa pe `TransactionLine`); (2) fiecare
`TransactionLine` cere AMBELE — partener pe latura de client/furnizor, cod
propriu (`00`+CUI) pe liniile fără partener, niciodată ambele `"0"`; (3)
`pull()` citea facturile pe coloane inexistente (`except: pass` tăcut → 0
facturi); (4) sub-secțiunile goale din `SourceDocuments` se omit, iar
`MovementOfGoods` e gol self-closed; (5) luna fără mișcări → depunere „pe
zero" cu `<GeneralLedgerEntries/>` self-closed, fără a fabrica tranzacții.
`test_d406.py` (11 teste) apără fiecare regresie + validează pe DUK. Vezi
`git log` pentru istoricul complet al tuturor reparațiilor, fiecare cu mesaj
detaliat.

## GARZI.md
Registrul gardurilor: categoriile de eșec ale unui sistem contabil și ce gard acoperă
fiecare, cu starea reală (ACOPERIT / PARȚIAL / LIPSĂ) și limita declarată a fiecărui gard.
Se actualizează în ACELAȘI commit cu gardul livrat — un registru stale dă fals sentiment de
acoperire. Înainte de a construi un gard nou: citește categoria acolo, ca să nu dublezi
unul existent și să nu ratezi limita deja cunoscută.

## DE_FACUT.md nu mai există (27.07.2026)
Șters la cererea lui Costin: „a fost o capcană". 806 linii pe care nimeni nu le citea integral
— iar aproape tot ce s-a reparat pe 27.07 era deja consemnat acolo ca amânat. Registrul exista,
disciplina de a scrie exista; lipsea mecanismul care să-l facă imposibil de uitat.
Ce l-a înlocuit:
- **`core/test_datorie.py`** — datoria verificabilă mecanic, ca `xfail(strict=True)`. Rulează la
  fiecare commit; când se repară, testul PICĂ și anunță. Nu se poate uita.
- **`GARZI.md`** — gardurile pe categorii de eșec, fiecare cu limita declarată.
- **`LANSARE.md`** — ce NU se poate automatiza: decizii, blocaje externe, datorie acceptată.
Regula: verificabil mecanic → test, nu notă. Notă → doar cu decizie și motiv, altfel e amânare
cu altă formă.

## Un singur arbore pe server (29.07.2026)

Se lucrează EXCLUSIV pe server (`~/iconta_nou`, branch `main`) — acolo e singura aplicație, nu
există alta. Serverul are **un singur arbore: `core/`**; nu există `declaratii/` și nu există
`motor/`. Pe 27.07.2026 s-au pierdut ore reparând trei defecte „confirmate" (D101 pe coloane
greșite, arbori paraleli, 946 de teste cu fake-uri) care nu existau pe server — erau într-o
copie locală. Ritualul de început, opririle și regula de redirecționare sunt în „PROCEDURA DE
LUCRU (30.07.2026)" de mai jos (supersedă fostul „LOCUL DE LUCRU (29.07.2026)").

# PROCEDURA DE LUCRU (30.07.2026)

## De ce exista

In 27-30.07.2026 s-au pierdut ore repetat din trei cauze de procedura:
- o sesiune a lucrat pe o copie locala in loc de server; defectele raportate nu existau pe
  productie
- instructiuni detaliate au trait doar in conversatie; la /clear s-au pierdut, desi agenda
  arata corect ce urmeaza
- arhitectul a formulat brief-uri pe presupuneri marcate ca fapte, si a modificat direct cod -
  deci nimeni nu-l putea corecta

## 1. Rolurile

### Code - executa si cauta temeiul
- cauta in legislatie temeiul pentru orice valoare, cota, prag, rotunjire sau structura fiscala
- citeaza TEXTUL actului normativ: act, articol, alineat, litera
- propune ce trebuie schimbat, cu temeiul atasat
- dupa validare: implementeaza, scrie testele cu temeiul citat PE LINIE langa assert, verifica
  prin mutatie, ruleaza proba functionala
- comite LOCAL pe server, apoi la FINALUL rularii impinge pe `backup/lant-<data>` SI pe `main` (decizia c RASTURNATA 05.08.2026: push pe main NU mai cere aprobarea lui Costin; CONDITIE ABSOLUTA = poarta verde, vezi §2.3 pct.8). NU push-per-pas
- raporteaza

Cine executa trebuie sa stie DE CE, altfel aplica orb.

### Arhitect (chat) - valideaza si verifica
- valideaza temeiul gasit de Code: actul e cel corect, textul citat spune ce se afirma, e act
  normativ si nu comentariu de pe site fiscal
- verifica INDEPENDENT fiecare pas, cu propriile comenzi, NU citind raportul lui Code
- da drumul la pasul urmator sau arata exact unde difera
- formuleaza pasii urmatori, marcand explicit ce e verificat si ce e presupunere

ARHITECTUL NU MODIFICA NIMIC. Nici cod, nici fisiere normative, nici baza, nici commit-uri.
Comenzile lui contin exclusiv citire: cat, grep, sed -n, psql -c "SELECT", pytest, curl,
git log, ls, wc.

SEMNAL DE INCALCARE: daca o comanda data de arhitect contine > >> sed -i git add git commit
git push INSERT UPDATE DELETE DROP ALTER rm cp mv - e incalcare de procedura si se refuza.

### Costin - decide lansarea
Decide daca aplicatia poate fi pusa pe piata. Tehnicul e la Code si la arhitect.

## 2. Bucla de lucru

UN PAS = cea mai mica bucata care lasa aplicatia FUNCTIONALA. Nu "un punct din lista": daca
scoaterea unei coloane cere reparate cinci locuri care o citesc, pasul cuprinde toate cinci.

1. Code cauta temeiul in legislatie, citeaza textul, propune schimbarea
2. Arhitectul valideaza temeiul - sau arata unde nu se tine
3. Code implementeaza: cod, teste cu temeiul pe linie, mutatie, proba functionala
4. Code comite LOCAL pe server. UN PAS NECOMIS PE SERVER NU S-A INTAMPLAT. La FINALUL rularii (nu per pas) impinge pe `backup/lant-<data>` SI pe `main` - decizia c (05.08.2026): push pe main NU mai cere aprobare, DAR numai sub poarta verde (§2.3 pct.8). Sursa unica - fara norma paralela de push-per-pas.
5. Code raporteaza. Raportul contine OBLIGATORIU cinci elemente:

   a) PROBA FUNCTIONALA, CU OUTPUT BRUT
      Nu "am verificat, e corect". Comanda rulata si ce a tiparit, cu cifrele.
      Exemplu bun: "calcul_salariu(3497.73, venit_brut_total=4050) -> facilitate 300.00
      (era 0.00)". Exemplu inutil: "facilitatea se calculeaza corect acum".
      Arhitectul nu poate reproduce proba dupa fapt - ruleaza in tranzactie anulata. Deci
      output-ul brut e singura dovada.

   b) MUTATIA, CU OUTPUT
      Ce ai stricat, ce test a picat, mesajul de esec. Un test care trece nu dovedeste nimic
      pana nu se arata ca pica atunci cand trebuie.

   c) TEMEIUL CU TEXTUL CITAT
      Nu doar "OUG 89/2025 art.III". Fragmentul din lege pe care se sprijina schimbarea.
      Arhitectul valideaza ca textul spune ce se afirma - fara text, nu poate.
      Daca pasul nu invoca nicio regula fiscala, se scrie "N/A - schimbare de tooling".

   d) CE N-AI VERIFICAT, EXPLICIT
      Ce ai presupus, ce ai luat din memorie, ce n-ai putut confirma la sursa.
      Cel mai valoros element din raport. Pe 29.07, un brief al arhitectului afirma ca
      "generatorul face deja rollup-ul" - era presupunere, si Code a descoperit ca nu.
      Simetric: cand Code marcheaza ce presupune, arhitectul verifica exact acolo.

   e) CE AI ATINS DIN CE NU ERA IN PLAN
      Daca ai modificat un fisier care nu era in lista de pasi, spune care si de ce.
      Un pas care atinge mai mult decat s-a declarat e un pas care a crescut - vezi §2.1.

   Un raport fara a) si b) nu se valideaza. Arhitectul cere sa fie rulate.
6. Arhitectul verifica independent, cu comenzile lui
7. Validare sau respingere cu motiv -> pasul urmator

Salvarea pe server la fiecare pas face ca spatiul in care lucreaza Code sa devina detaliu.

## 2.2 STRUCTURA RAPORTULUI (02.08.2026, ceruta de Costin)

Orice raport de executie respecta aceasta structura, IN ORDINEA DATA. Inlocuieste formatul liber. Cele cinci
elemente din 2/etapa 5 (a-e) RAMAN valabile ca SUBSTANTA - se prezinta asa. Motivul: formatul liber amesteca
informatia (cifra care conteaza langa o nota tehnica; ce n-a fost verificat uneori la (d), alteori topit in
proza). Pe cifre se face aritmetica de validare (COLLECTED = passed + skipped + xfailed, comparat cu runda
anterioara); pe deciziile cerute se stie ce blocheaza. Amandoua merita randuri proprii.

UN SINGUR FORMAT (nu exista raport redus / SCURT; eliminat 08.08.2026, ceruta de Costin). Orice executie, FARA
EXCEPTIE: titlu + TOATE sectiunile 1-11, IN ORDINEA DATA. Nu exista o submultime de sectiuni care se pot sari.

- O sectiune care nu se aplica NU se omite: se scrie EXPLICIT "N/A - <motiv>" (la fel cum §11 cere deja pentru
  registrele neatinse si §6 cere "niciuna"). Absenta unei sectiuni = raport incomplet.
- Fara raport: niciodata. Orice comanda executata produce raportul de 11 sectiuni.
- Titlul NU mai poarta incadrare (nu exista "| COMPLET" / "| SCURT"); se incheie la "| <n> pasi".

TITLU (obligatoriu, prima linie a raportului, inaintea sectiunii 1):
RAPORT <NUME_CAMPANIE> | <data> | <HEAD_intrare> -> <HEAD_iesire> | <n> pasi
Fara titlu, raportul e incomplet.

1. VERDICT - o linie: LIVRAT / LIVRAT PARTIAL / OPRIT, si motivul in maximum o propozitie.

2. CIFRE - brut, fiecare pe rand propriu, nimic altceva pe randurile astea:
   COLLECTED: N
   passed / skipped / xfailed: N / N / N
   verificator TOTAL: N
   HEAD: hash
   ahead: da/nu
   HEAD intrare -> HEAD iesire: hash_intrare -> hash_iesire, cu lista commiturilor pe pas.
   SOLD DATORII: xfail deschise la intrare N / inchise in campanie N / deschise nou N / sold la iesire N. Cifra, nu proza.
   Cifra COLLECTED se CONFIRMA EXPLICIT (rulata), nu se deduce din passed.

3. PROBA - per pas: ce s-a testat, output ROSU inainte, output VERDE dupa, MUTATIA si ce a produs. Output BRUT,
   nu rezumat. Fara probe, pasul nu e livrat. (= substanta 2/etapa 5 a+b.)

4. TEMEI - act, articol, alineat, nivel sursa (MO / REDARE / INTERPRETARE_OFICIALA / PRACTICA). "N/A - tooling"
   unde nu se aplica. (= substanta 2/etapa 5 c.)

5. CE NU AM VERIFICAT - lista EXPLICITA, fiecare limita pe rand propriu, NU topita in proza. Include si ce s-a
   presupus fara sa se citeasca sursa. (= substanta 2/etapa 5 d.)

   **GOL IMPLICIT (20.08.2026, cerut de Costin - regula intarita dupa o incalcare).** §5 nu e o lista de
   observatii; e o lista de IMPOSIBILITATI. Valoarea implicita e "niciuna" (sectiunea NU se omite, se scrie
   explicit). Un item are voie in §5 doar daca poarta UNA din exact trei etichete, scrisa la inceputul randului:

     - **[EXTERN]** - depinde de un raspuns pe care nu-l pot obtine (ANAF, un tert, o cheie, un acces).
     - **[DECIZIE]** - cere o alegere de produs care e a lui Costin, nu de corectitudine. Atunci apare SI la §6.
     - **[NEVERIFICABIL]** - l-am vazut, dar nu se poate verifica din cod (comportament de terti, randare pe
       dispozitiv real, date de productie inaccesibile).

   **Un item care nu incape in niciuna din cele trei NU e o limita, e MUNCA NETERMINATA** - se face inainte de
   raport, nu se raporteaza. Testele astea, in ordine: (a) as putea s-o inchid cu comenzile pe care le am acum?
   (b) e o afirmatie despre REPO (lista incompleta, ramura netestata, tipar nematurat) sau despre LUME? Ce e
   despre repo si e inchidabil = munca. Scrisul lui in §5 nu il descarca - il ascunde.

   **INCALCATA DIN NOU, 21.08.2026 (a treia oara).** Doua rapoarte din aceeasi tura au avut in §5 itemi FARA
   eticheta: "daca portile declarate sunt destul de bune" si "d300_reconciliere duplica maparea - n-am facut-o".
   Amandoi erau MUNCA, nu limite: primul s-a inchis citind doua functii (si a scos la iveala ca poarta D390 e
   calendaristica, nu de completitudine - o afirmatie deja publicata, corectata), al doilea citind un antet de
   modul (si a scos la iveala ca "reparatia" pe care o propuneam ar fi sters un gard de non-tautologie). Motivul
   real n-a fost imposibilitatea, ci ora si scopul. Testul (a) din paragraful de mai sus le-ar fi prins pe
   amandoua: "as putea s-o inchid cu comenzile pe care le am acum?" - da, in cinci minute fiecare.

   **De ce regula asta e intarita:** exista deja ca Regula 12 si ca §5-gol-la-finalizarea-firmei (19.08), si a
   fost incalcata pe 20.08 intr-un raport de METODA (nu de firma) - formularea veche era legata de "firma gata",
   deci n-a declansat. Se aplica la ORICE raport. Doua din cele patru randuri de atunci erau fixabile in cinci
   minute ("lista de module e incompleta", "o ramura a gardului n-a fost executata"); prima a devenit al treilea
   colt al gardului de perimetru, a doua un test sintetic - amandoua in commitul urmator. Asta e forma corecta:
   §5 se GOLESTE reparand, nu explicand.

6. DECIZII CERUTE - NUMEROTAT: ce asteapta raspunsul lui Costin si ce blocheaza fiecare. Se scrie "niciuna" daca
   nu e cazul - sectiunea NU se omite.

7. IN AFARA PLANULUI - ce s-a atins si nu era cerut in comanda. (= substanta 2/etapa 5 e.)

8. GENERALIZARE PE CLASA - pentru fiecare neconformitate corectata: unde s-a cautat acelasi tipar in restul
   aplicatiei (comanda de cautare, verbatim), ce s-a gasit, ce s-a corectat. Locurile verificate SI curate se
   enumera explicit - "cautat in X, Y, Z; tiparul nu apare" e informatie, absenta ei e gol. Daca o neconformitate
   nu a fost generalizata, se scrie de ce.

9. GARDURI ADAUGATE - tabel: gard | fisier:linie | ce face imposibil | mutatia care il probeaza (comanda + iesire
   rosie). Un gard fara mutatie probata nu se trece aici - se trece la sectiunea 5 ca neverificat.

10. EFECT PE PRODUS - ce se schimba vizibil pentru contabil sau in iesirea catre ANAF: ecran, camp, cifra pe
    fluturas, linie in declaratie, comportament nou. Format: "inainte -> dupa". Daca nu se schimba nimic vizibil
    (campanie pur interna), se scrie "niciun efect vizibil" - explicit, nu prin omisiune.

11. CE AM ACTUALIZAT - ULTIMUL PUNCT, OBLIGATORIU. Cele patru registre (GARZI.md, DECIZII.md, TESTE.md, ISTORIC.md),
    fiecare cu ce s-a scris in el la aceasta executie, SAU "nimic de actualizat in X, pentru ca <motiv>" - explicit,
    niciodata prin omisiune. Un registru neatins fara motiv scris = raport incomplet.
    PLUS (predare, 09.08.2026, ceruta de Costin): sectiunea 11 listeaza INTOTDEAUNA si PREDARE_LANT.md (al
    cincilea pas de publicare, §2.3 pct.10), cu una din DOUA valori: "rescris (tura N)" - si atunci se arata
    diff-ul; SAU "nemodificat - starea din tura N ramane valida" - si atunci se spune de ce niciun front
    deschis nu s-a miscat. Absenta lui din sectiunea 11 = raport incomplet.
    PLUS (decizia c, 05.08.2026): se confirma EXPLICIT ca HEAD local, origin/main si backup sunt pe ACELASI commit,
    numind commit-ul (ex. "HEAD = origin/main = backup/lant-<data> = <hash>"). Daca NU sunt pe acelasi commit, se
    spune DE CE (poarta rosie -> nepins pe main; tree murdar; origin/main avansat sub tine; etc.).
    PLUS (four-way, 09.08.2026): se confirma SI ca PROCESUL VIU ruleaza commitul - RUNNING = HEAD (`versiune.stare()`,
    divergent=False), cu start-time-ul procesului DUPA data commitului. Confirmarea completa e FOUR-WAY, numind
    commit-ul: "HEAD = origin/main = backup/lant-<data> = RUNNING = <hash>". Daca procesul NU ruleaza commitul, se
    spune DE CE (restart neefectuat -> stop point comportament vizibil / decizie de produs; poarta rosie). Vezi §2.3 pct.10.
    PLUS (CONFORMITATE.md, 22.08.2026, ceruta de Costin): **CONFORMITATE.md intra in §11, ca oricare alt registru** -
    registrul confruntarii codului cu PLAN_ARHITECTURA.md, o sectiune per interdictie, cu stare / cifra+lista /
    calibrare / ce nu vede masuratoarea / unde ajunge efectul. MOTIVUL, scris de Costin: *"Cifrele confruntarii nu au
    voie sa existe doar in raport. Raportul se citeste o data; registrul ramane."* Deci: **un raport de confruntare
    care nu-l actualizeaza e INCOMPLET, indiferent ce contine in rest** - o cifra masurata care traieste numai in
    conversatie se pierde si munca se reface de la zero. Regula fisierului: *"«Investigata» nu e o stare. Un camp gol
    nu e permis"* - daca nu se poate masura, se scrie NEMASURABILA CU MOTIVUL. Cele patru stari: MASURATA / PARTIAL
    (cifra e un plafon inferior, si se SPUNE) / NEMASURABILA / NEINCEPUTA. Gardat de `core/test_conformitate.py`:
    o interdictie noua in plan fara sectiune, un camp obligatoriu gol sau o stare inventata opresc poarta.

## 2.2.1 ACTUALIZAREA REGISTRELOR DUPA FIECARE EXECUTIE (04.08.2026, ceruta de Costin)

DUPA FIECARE EXECUTIE (punct / cluster / task livrat), FARA sa ceara cineva, se actualizeaza TOT ce s-a schimbat:

- **GARZI.md** - datorii noi, riscuri noi, sub-blocaje descoperite. O datorie descoperita si NEconsemnata in ACEEASI
  rulare = INCALCARE (nu "o scriu data viitoare").
- **DECIZII.md** - decizia + temeiul + proba, APPEND-ONLY. O decizie anterioara rasturnata NU se editeaza: se scrie
  o intrare de PIVOT care o supersedeaza EXPLICIT (numeste intrarea veche, spune ce era intermediar si ce e final).
- **TESTE.md** - bifa punctului/clusterului (Inventar A) + gardurile noi + proba. (Garduri anti-stale test_agenda:
  bifa DUPA ce codul intra in git HEAD; redenumirea unui test citat cere re-ancorarea bifei + "bump: <motiv>".)
- **ISTORIC.md** - intrarea narativa a executiei. ACUM APPEND-ONLY, ca DECIZII (regula veche "doar la finalul zilei,
  cand cere Costin" ELIMINATA 04.08.2026). O executie ulterioara care rastoarna una din aceeasi zi o SUPERSEDEAZA
  explicit - nu se sterge, nu se rescrie (ex. 04.08: approach-b -> approach-a conditionat; nomenclator N gresit -> reparat).

Raportul 2.2 se incheie OBLIGATORIU cu sectiunea 11 "CE AM ACTUALIZAT": cele patru fisiere, fiecare cu ce s-a scris,
SAU "nimic de actualizat in X, pentru ca ...". Niciodata tacut.

LIMITA CUNOSCUTA (audit 07.08.2026): actualizarea celor patru registre NU are gard mecanic. Un gard care ar avertiza
pe orice commit in `core/` fara atingerea unui registru ar produce zgomot pe reparatii mici - deci ramane JUDECATA,
nu mecanism. La fel, formatul raportului (§2.2), CICLUL DE NECONFORMITATE si WIP-pe-rosu (pct.9) sunt reguli
comportamentale, neguardabile mecanic in acest mediu. Contrast: publicarea pe origin/main + backup (pct.8) era la fel
de neguardata, dar e STARE REMOTE verificabila -> a fost cablata (post-commit). Push-ul e mecanism; registrele raman
disciplina, asumat.

REGULA SURSEI UNICE peste toate: informatia sta intr-un singur loc CANONIC (datoria in GARZI, decizia in DECIZII,
bifa/gardul in TESTE, naratiunea in ISTORIC, functionalitatea in FUNCTIONALITATI.csv), celelalte TRIMIT acolo, nu
duplica textul.

## 2.2.1b CUM SE CITESTE SECTIUNEA `REGISTRE` A UNEI COMENZI (28.08.2026, ceruta de Costin)

Regula, verbatim, asa cum a dat-o:

> **REGISTRE listeaza minimul obligatoriu; o scriere comandata explicit intr-un bloc cu litera e
> autorizata prin faptul ca e comandata. Daca o scriere dintr-un bloc NU e dorita, REGISTRE o
> interzice pe nume.**

**De unde vine.** Pe 27.08.2026 am ridicat o contradictie: un bloc cu litera cerea o scriere pe care
sectiunea `REGISTRE` a aceleiasi comenzi n-o listase. Raspunsul lui a fost regula de mai sus, plus
partea a doua, la fel de importanta: *„Ai ridicat-o corect — **continua sa ridici**, dar cazul
general e rezolvat."* Deci **ridicarea contradictiei ramane obligatorie**; ce se schimba e
**rezolutia implicita**: blocul cu litera castiga, nu `REGISTRE`.

**Consecinta practica.** O scriere ceruta intr-un bloc si nelistata in `REGISTRE` **se face**, si se
declara in raport la §2 („in plus"). O scriere pe care `REGISTRE` o interzice pe nume — tipic
`DECIZII.md: NIMIC` — **nu se face**, oricat ar parea de fireasca.

**Conventia a stat doua zile numai in `PREDARE_LANT.md`.** O conventie care traieste doar in predare
moare cu ea; de-aia locul ei e aici, unde `CLAUDE.md` e canonic pentru PROCES.

**Si o completare la lista de registre din §2.2.1 (28.08.2026):** `GARZI.md` e **linie obligatorie**
in orice sectiune `REGISTRE` si in §3 al raportului — atins sau nu, cu motivul scris cand nu e atins.
Motivul e masurat: registrul a stat **sase zile** fara nicio intrare, timp in care au intrat 80 de
garzi, iar un registru cu sase zile in urma se citeste ca **complet**. Partea derivabila e acum
generata si pazita (`scripts/scan_garzi_inventar.py` + `core/test_garzi_inventar.py`); partea
narativa ramane disciplina, si de-aia intra in lista obligatorie.

## 2.2.2 FORMA COMENZII PRIMITE - oglinda ARHITECT.md (08.08.2026, ceruta de Costin)

Comenzile compuse de arhitect vin in forma cu 7 puncte definita in ARHITECT.md ("FORMA COMENZII"). Textul canonic
sta ACOLO (REGULA SURSEI UNICE); aici doar OBLIGATIILE executorului fata de trei dintre puncte:

- **CE CER INAPOI (pct.4).** Executorul onoreaza ce cere comanda: analiza / propunere / executie, IMPLICIT
  propunere. Daca comanda cere propunere sau analiza, NU se executa - se propune si se asteapta. Continuarea
  automata a lantului (§2.3) se aplica CAMPANIILOR DE EXECUTIE; "ce cer inapoi" decide daca o comanda e executie
  sau propunere. Nu schimba §2.3: cand comanda e executie, lantul curge ca in §2.3.
- **PUNCTE DE OPRIRE (pct.5).** Punctele de oprire declarate in comanda se ADAUGA la criteriile de oprire din
  §2.3 pct.2/5 (decizie de produs, neconformitate, blocaj) - nu le inlocuiesc. Executorul se opreste la ele si
  raporteaza. Nu pot suprascrie "NU SE OPRESTE" din §2.3 pct.3 (push, migrare, GRI).
- **TEMEIURI (pct.6).** Faptele numite in comanda sunt harta de cautare, nu temei: se verifica la sursa INAINTE
  de folosire (intareste §3 "nu pe memorie"; un candidat numit in comanda se confirma la sursa, altfel intra la
  raportul §2.2 sect.5 "ce nu am verificat").

## 2.3 CONTINUITATE INTRE CLUSTERE (02.08.2026, ceruta de Costin)

Dupa raportul unui cluster inchis, executorul NU se opreste sa intrebe ce urmeaza. Ruleaza
`core.agenda.urmator_cluster()` si porneste campania pentru clusterul indicat, IN ACEEASI TURA.

Se opreste si cere decizie DOAR daca:
- clusterul urmator e BLOCAT si TOATE cele de dupa el sunt blocate;
- campania cere o DECIZIE DE PRODUS (scop, migrare pe date reale);
- a aparut o NECONFORMITATE care cere oprire conform ciclului (vezi CICLUL DE NECONFORMITATE);
- CONTEXTUL se apropie de epuizare - atunci se opreste la GRANITA CURATA DE COMMIT, cu predare scrisa.

Push-ul pe main NU mai cere aprobarea lui Costin (decizia c RASTURNATA 05.08.2026; conditia de poarta verde in §2.3 pct.8).
Executorul commite LOCAL si continua cu clusterul urmator FARA sa se opreasca; impinge pe backup SI pe main la FINALUL rularii.

### REGIM DE LUCRU IN LANT NESUPRAVEGHEAT (02.08.2026, ceruta de Costin)

1. **SOLD CUMULAT.** Fiecare raport de campanie din lant se deschide cu:
   `SOLD LANT: <n> clustere inchise / <n> blocaje deschise / <n> xfail noi / HEAD start -> HEAD curent`.
   Lantul nu ascunde datoria acumulata.

2. **OPRIRE PENTRU DECIZIE DE PRODUS:** se opreste cand alegerea schimba CE AJUNGE LA CONTABIL sau CE SE
   PUBLICA. Structura, nume, forma testului = autonom, fara intrebare.

3. **NU SE OPRESTE** pentru: push (comite local si continua; impinge pe backup SI main la finalul rularii, sub poarta verde - §2.3 pct.8, decizia c 05.08); migrare pe tenanti reali (o lasa in sarcina
   deployment-ului si o consemneaza); fereastra GRI sau orice verdict GRI (blocheaza si merge mai departe).

4. **OPRIRE OBLIGATORIE SI DEFINITIVA A LANTULUI** daca: pytest iese cu exit-code nenul, verificator TOTAL > 0,
   sau `git status --porcelain` nu e gol la finalul unei campanii. NU incerca sa repari ca sa continui -
   opreste-te cu tree-ul in starea in care e si scrie ce s-a intamplat.

5. **LANT FARA LIMITA DE CLUSTERE** (limita introdusa 02.08.2026, ELIMINATA 03.08.2026). Limita de 6 clustere
   /rulare a fost introdusa 02.08 ca prudenta la PRIMA rulare nesupravegheata; se ELIMINA 03.08, dupa 15 clustere
   inchise cu poarta verde si zero regresii - nu mai e justificata. Executorul continua lantul cluster dupa
   cluster, in aceeasi tura, pana la UNUL din criteriile de oprire ramase:
   - clusterul urmator e BLOCAT si TOATE cele de dupa el sunt blocate;
   - campania cere o DECIZIE DE PRODUS (scop, migrare pe date reale, schimbare de schema) - vezi pct.2;
   - a aparut o NECONFORMITATE care cere oprire conform ciclului (CICLUL DE NECONFORMITATE);
   - POARTA ROSIE sau TREE MURDAR (pct.4 - oprire definitiva, cu WIP salvat pct.9);
   - CONTEXTUL se apropie EFECTIV de epuizare (pct.6 - oprire la granita curata de commit, cu predare scrisa).
   Oprirea "ca sa decida Costin ordinea" NU e criteriu: ordinea o da agenda (core.agenda.urmator_cluster()).

6. **PREDARE LA OPRIRE:** HEAD, sold lant, ce cluster urmeaza, ce blocaje s-au deschis si de ce.
   Predarea la oprire pentru EPUIZARE DE CONTEXT trebuie sa fie suficienta pentru o sesiune NOUA, cu
   context GOL, care nu a citit nimic din lantul anterior. Contine: HEAD; sold lant; clusterul urmator din
   agenda (`core.agenda.urmator_cluster()`); blocajele deschise CU MOTIVUL fiecaruia; ce registre au fost
   atinse. Se SCRIE PE DISC (fisier de predare), nu doar in chat. Dupa ce ai scris predarea, OPRESTE-TE -
   nu incerca sa continui pe context compactat. PREDAREA TRIMITE EXPLICIT LA REGULI: prima linie a oricarui PREDARE_LANT.md este "Citeste CLAUDE.md §2.2 (structura raportului) si §2.3 (lant, siguranta, limba), si ARHITECT.md "FORMA COMENZII" (forma comenzii primite - 7 puncte), inainte de a incepe." O sesiune noua care reia din predare citeste regulile INAINTE de primul cluster, nu dupa.

7. **RAPORTUL IN LANT.** Fiecare cluster inchis primeste raportul lui conform §2.2, TOATE sectiunile 1-11, inclusiv
   8 (generalizare pe clasa), 9 (garduri adaugate) si 10 (efect pe produs). Sinteza pe rulare NU inlocuieste
   rapoartele per cluster - se adauga peste ele.
   Un cluster fara sectiunea 9 completata NU se declara inchis: daca nu s-a adaugat niciun gard, sectiunea 9
   spune explicit de ce reaparitia e deja imposibila.

8. **SIGURANTA + PUSH PE MAIN (decizia c RASTURNATA 05.08.2026).** Inainte de a raporta o rulare incheiata,
   executorul verifica faptul ca munca exista in TREI locuri: pe server (commit local), pe remote pe ramura de
   siguranta `backup/lant-<data>`, SI pe `origin/main`. Push-ul pe backup SI pe main NU cere aprobare - absenta lui
   e o defectiune.
   CONDITIE ABSOLUTA pentru push pe main: POARTA VERDE - pytest cu COLLECTED confirmat (rulat, nu dedus) + verificator
   TOTAL 0 + `git status --porcelain` gol. Poarta ROSIE sau TREE MURDAR -> NU se impinge pe main; se raporteaza si se
   OPRESTE (WIP salvat pct.9). FARA EXCEPTII, fara "repar dupa push". Pe main se impinge cu fast-forward; daca
   origin/main a avansat sub tine (commit al lui Costin), `pull --rebase` INAINTE (vezi memoria main partajat), nu se
   forteaza NICIODATA.
   **MECANISM (gard, nu intentie) — `scripts/githooks/post-commit` (cablat 07.08.2026, backup adaugat aceeasi zi).**
   Publicarea in AMBELE locuri remote nu mai depinde de memoria executorului: dupa fiecare commit pe `main` (deci dupa
   ce pre-commit a trecut poarta verde), post-commit face `fetch` + verifica fast-forward + `git push` pe `origin/main`
   SI pe `backup/lant-<data>` (creeaza ramura zilei daca nu exista), NICIODATA `--force`. Daca o tinta a avansat sub
   tine / nu e fast-forward, se opreste pe acea tinta si cere rezolvare manuala (`pull --rebase` pentru main, fara sa
   forteze). Daca vreo publicare nu reuseste, ESUEAZA VIZIBIL: banner + sentinela (`.git/PUSH_MAIN_ESUAT`,
   `.git/PUSH_BACKUP_ESUAT`). Confirmarea din raport inseamna ACUM three-way COMPLET: HEAD = origin/main = backup pe
   acelasi commit SI ambele sentinele absente - daca vreuna exista, munca NU e integral publicata si raportul NU e
   incheiat.
   Daca munca exista intr-un singur loc, executorul o spune EXPLICIT in raport, la PRIMA linie, nu la final. Raportul
   se incheie cu `BACKUP: <ramura> — <n> commituri` si confirma HEAD = origin/main = backup pe acelasi commit (§2.2 sect.11).

9. **WIP LA OPRIRE PE ROSU** (inchide gapul pct.4 <-> pct.8). La oprirea obligatorie pe tree murdar sau poarta
   rosie (pct.4), INAINTE de a scrie raportul, executorul pune munca la adapost FARA sa o repare: `git stash create`
   + push pe `refs/heads/wip/<data>-<ora>`, sau commit pe o ramura `wip/` separata. Tree-ul de lucru RAMANE in
   starea in care e - nu se curata, nu se repara, nu se comite pe main/backup. Scop: starea defecta e cea mai
   valoroasa pentru diagnostic SI cea mai expusa la pierdere (pct.8 cere commit+tree curat, deci n-ar acoperi-o).
   Raportul declara `WIP SALVAT: <ramura>` sau motivul exact pentru care nu s-a putut.

10. **PUBLICAREA COMPLETA = CINCI PASI, AUTOMATA DUPA POARTA VERDE (09.08.2026, ceruta de Costin).**
   Publicarea NU se opreste la disc. Dupa ORICE executie care a trecut poarta verde (pytest cu COLLECTED confirmat +
   verificator TOTAL 0 + `git status --porcelain` gol), executorul face TOTI cei cinci pasi de publicare FARA sa fie
   ceruti in comanda - absenta lor e o defectiune, nu o optiune a celui care compune comanda:
   1. **commit** local pe server (declanseaza pre-commit = poarta verde);
   2. **push** pe `origin/main` SI `backup/lant-<data>` (cablat, post-commit hook - pct.8);
   3. **deploy** = codul comis ajunge pe checkout-ul care serveste productia. Serviciul `iconta-nou` ruleaza din
      `/home/costin/iconta_nou` (WorkingDirectory al unitatii systemd), ACELASI checkout pe care se comite -> deploy-ul
      e HEAD-ul de pe disc = commitul; NU exista checkout de prod separat de sincronizat. Daca arhitectura se schimba
      (checkout separat), deploy = `git pull --ff-only` pe acel checkout INAINTE de restart;
   4. **restart** = `sudo systemctl restart iconta-nou` (NU `iconta`, buildul vechi, esueaza tacit), ca procesul VIU
      sa incarce codul comis. Fara restart, procesul ruleaza in continuare commitul stampilat la pornirea lui
      (core/versiune.py) - exact divergenta pe care detectorul running==HEAD o semnala fara ca nimeni s-o repare.
      CABLAT (post-commit, ca pasul 2 de push): restartul e NECONDITIONAT de tipul commitului - dupa ORICE
      publicare din lant procesul viu preia HEAD, fara exceptii, fara liste de tipuri. Conditionarea pe tip
      (docs vs runtime, decisa de executor) a produs divergenta RUNNING!=HEAD (11.08.2026: RUNNING pe commitul
      de cod, HEAD avansat de un commit de DOCS) si e ELIMINATA din mecanism; gardata de
      core/test_publicare_restart_neconditionat.py (cade daca reapare orice inspectie de continut in hook).
   5. **predare** = actualizeaza PREDARE_LANT.md. E fisierul de care depinde sesiunea urmatoare (constatare
      tura 17: DECIZII/GARZI/TESTE/ISTORIC s-au actualizat, dar PREDARE a lipsit din lista - exact ce conteaza
      pentru continuitate era singurul optional). Se SUPRASCRIE, nu se adauga: e fisier de STARE CURENTA, nu
      jurnal (jurnalul e ISTORIC.md). Contine, IN ACEASTA ORDINE: (a) four-way de la ultima executie (SHA +
      ora); (b) fronturile deschise, cu blocajul fiecaruia; (c) ce e in lucru acum; (d) ce urmeaza. Daca
      executia NU a schimbat niciun front deschis, fisierul RAMANE NEATINS - dar raportul (§2.2 sect.11) o
      spune EXPLICIT.
   **Publicarea nu e completa pana cand procesul viu nu ruleaza codul comis, confirmat FOUR-WAY:** HEAD (disc) =
   origin/main = backup/lant-<data> = **RUNNING** (commitul procesului viu; `versiune.stare()`: running==head,
   divergent=False), cu **start-time-ul procesului DUPA data commitului** (systemd ExecMainStartTimestamp > data
   commit - se CITESTE, nu se presupune). Aceasta EXTINDE three-way din pct.8: confirmarea din raport (§2.2 sect.11)
   devine four-way.
   **STOP POINT (mutat INAINTE de commit):** restartul fiind acum automat la publicare (post-commit,
   neconditionat), decizia de produs se ia INAINTE de a comite. Daca schimbarea are comportament VIZIBIL care,
   cu utilizatori activi, cere fereastra sau anunt, se RAPORTEAZA si se asteapta INAINTE de commit-ul care o
   publica - nu dupa. Odata comis pe poarta verde, serviciul preia HEAD neconditionat (nu se mai alege "restart
   sau nu" per commit). Pe poarta ROSIE sau tree murdar (pct.4) NU se comite deloc: nici deploy, nici restart.
   **DE CE executor, nu hook:** pasii 1-2 sunt stare remote fara risc vizibil -> s-au putut cabla in post-commit
   (pct.8). Restartul are stop point uman (comportament vizibil; utilizatori activi -> eventual fereastra = decizie de
   produs) -> NU se cableaza orb in post-commit (ar reporni prod la fiecare commit, peste utilizatori activi); ramane
   pas de EXECUTOR, obligatoriu, cu raportare inainte. Coerent cu decizia iulie "detector vizibil, NU auto-restart"
   (DECIZII 08.08): auto-restartul ORB ramane interzis; devine obligatoriu restartul CONSTIENT al executorului dupa
   poarta verde.

11. **POARTA VERDE VIZUALA (17.08.2026, ceruta de Costin).** Daca tura a ATINS vreun ecran (reparat,
   construit, probat orice ajunge pe un ecran), poarta verde NU e completa pana cand cele TREI unelte
   vizuale (frontend_test/vizual: `axe_scan` / `mobil_scan` / `interactiune_scan`) nu au fost rulate pe
   ecranele atinse in tura respectiva, iar rezultatele lor (CU CIFRE) nu sunt in raport la §3 (PROBA).
   E obligatie de EXECUTOR — cer app viu + browser + auth, deci NU se cableaza in pre-commit (ca
   restartul, pct.10). O tura care NU a atins niciun ecran e SCUTITA, dar o DECLARA explicit in raport
   ("niciun ecran atins -> uneltele vizuale N/A"), niciodata prin omisiune. Extinde Regula 14 din
   MEMORY.md (axe + profil telefon la orice ecran atins) si inventarul din TESTE.md
   ("Infrastructura de testare vizuala"). Gardata structural de core/test_infra_vizuala.py
   (cele trei unelte + axe.min.js + baseline-urile nu pot disparea tacut — Regula 6).

## 2.1 De unde vin pasii

Pasii unui fir traiesc in TESTE.md, la "In lucru acum". NU in conversatie.

Format obligatoriu:

- fir: <numele lucrului, cu contextul>
- ultim: <ce s-a terminat> (<hash commit>)
- urmator: <pasul urmator>. <STARE>
- pasi:
  1. <fisier, functie, ce se schimba concret>
  2. <...>

STARE = NEINCEPUT | IN LUCRU | BLOCAT: <motiv>

CINE SI CAND:
- Arhitectul formuleaza pasii INAINTE de a incepe firul. Concret: nu "repara D300", ci
  "d300.py:264 - cota vine ca fractie din registru, D394 o cere ca procent intreg".
- Code ii scrie in TESTE.md ca PRIMA actiune a firului, inainte de orice modificare de cod.

CAND LISTA SE DOVEDESTE GRESITA PE DRUM:
Code rescrie lista in TESTE.md si raporteaza, INAINTE sa execute ce a descoperit.
Nu se executa o lista mai mare decat cea scrisa. Daca pasul creste, lista creste intai.

CAND UN PAS E PREA MARE PENTRU O SESIUNE:
Se sparge, cu commit intre bucati. Fiecare bucata lasa aplicatia functionala. In TESTE.md
bucatile apar ca pasi SEPARATI, fiecare cu starea lui (ex: 2b-scrieri, 2b-coloana), nu ca
subpuncte.

CE NU E UN PAS:
- "verifica daca e in regula" - fara criteriu de terminare
- "repara zona X" - nu spune ce anume
- ceva ce nu se poate comite singur fara sa lase codul rupt

## 3. Ce inseamna "temei"

TEMEIUL E ACTUL NORMATIV, CU TEXTUL CITAT. Act, articol, alineat, litera.

Ierarhia surselor:
1. Monitorul Oficial - norma. Legi, ordonante, hotarari, ordine. Majoritatea valorilor fiscale
   NU vin de la ANAF, ci de la Parlament sau Guvern.
2. ANAF - procedura: formulare, structuri XML, validator, instructiuni de completare. Publica
   TARZIU: legea intra in vigoare la 1 ianuarie, instructiunile apar in februarie.
3. Comentarii, presa fiscala, ghiduri neoficiale - pot arata UNDE sa cauti. NU sunt temei,
   niciodata.

Cand ghidul ANAF difera de lege, LEGEA CASTIGA.

UNDE NU EXISTA TEMEI LEGAL, NU SE CONSTRUIESTE. Nu se inventeaza, nu se interpreteaza liber,
nu se completeaza cu "ce pare rezonabil". Daca legea nu transeaza, se consemneaza ca
xfail(strict=True) in core/test_datorie.py cu motivul "temei neverificat: <ce anume>".

Un test scris pe presupunere e mai periculos decat absenta lui: da siguranta falsa, iar cand
cineva il vede rosu repara CODUL ca sa se potriveasca cu presupunerea.

INTERPRETAREA, cand e inevitabila: daca doua acte se combina si niciunul nu transeaza
combinatia, se marcheaza in cod ca INTERPRETARE CU TEMEI, nu ca text explicit - cu argumentul,
alternativa respinsa, si nota "de reconfirmat daca apare o norma care transeaza".

## 3.1 Formatul de citare a temeiului (citabil mecanic)

Fiecare loc care aplică o regulă fiscală citează sursa într-un format CONSTANT — ca la o
schimbare legislativă să găsești cu grep exact locurile afectate. Fără format constant,
căutarea e incompletă, deci mai periculoasă decât lipsa completă: pare că ai găsit tot.

**Temei normativ (act).**

    <TIP> <nr>/<an> [art.<art> | pct.<pct>] [alin.(<alin>)] [lit.<lit>]

- TIP ∈ { Legea, OUG, OG, HG, OMF, OMFP, OPANAF, CF (Cod fiscal), CPF (Cod procedură fiscală) }.
- `<nr>/<an>` obligatoriu pentru Legea/OUG/OG/HG/OMF/OMFP/OPANAF. `CF` și `CPF` sunt coduri, NU
  au nr/an → se trece direct la `art.`.
- `art` = arabic sau roman (`art.146`, `art.III`, `art.LXVI`). Normele contabile (OMFP) se
  citează pe puncte: `pct.<n>`, cu interval permis (`pct.111-116`).
- `alin.(<n>)` permite caret pentru exponent: `alin.(5^6)`. `art.`/`pct.`, `alin.`, `lit.` sunt
  toate OPȚIONALE — actul + nr/an singur e citare validă.

Exemple: `OUG 89/2025 art.III alin.(4) lit.b` · `CF art.146 alin.(5^6)` · `OMFP 1802/2014 pct.111-116` · `OPANAF 592/2016`

**Referință de validator / structură (NU e normă).**

Regulile validatorului DUK și limitele din XSD-urile ANAF nu sunt acte normative (tier 2–3, vezi
§3), dar cer același grep la o schimbare de versiune ANAF — deci au convenția lor:

    DUK regula <cod>              (ex: DUK regula A91b, DUK regula R28)
    XSD <element> maxLength <n>   (ex: XSD StreetName maxLength 70, XSD Name maxLength 256)

O regulă de validator NU se scrie ca temei normativ (ar fi fals — vezi lecția D301: `totalPlata_A`
e checksum de structură ANAF, nu regulă fiscală).

## 4. Ce verifica arhitectul la validare

Toate cinci, nu patru din cinci:
1. commit-ul e pe origin/main - verificat cu git log, nu din raport
2. suita e verde - rulata de arhitect
3. verificatorul de conformitate: TOTAL 0
4. aplicatia porneste si site-ul raspunde 200
5. PROBA FUNCTIONALA A RULAT, CU OUTPUT VIZIBIL

Punctul 5 e cel mai important si cel mai usor de sarit. Pe 29.07, reparatia facilitatii a
trecut toate testele, dar d112.pull reconstruia dict-ul fara campul nou, deci declaratia iesea
gresita. A prins-o proba pe schema efemera, nu suita.

FORMA PROBEI: schema efemera din tenant_template, datele care exercita exact cazul reparat,
generarea completa pana la declaratie, verificarea cifrei, ROLLBACK. Fara output vizibil,
pasul nu e inchis.

CE NU POATE VERIFICA ARHITECTUL DIN AFARA

Doua lucruri nu se pot reproduce dupa fapt:
- proba functionala - ruleaza pe schema efemera in tranzactie anulata; nu lasa urma
- mutatia - se face in timpul lucrului

Pentru astea, arhitectul se sprijina pe output-ul brut din raport (§2 etapa 5, a si b). Un
raport care le descrie in loc sa le arate nu e dovada. Cifrele concrete sunt verificabile prin
coerenta: daca raportul spune "facilitate 142.86" si cifra se leaga cu calculul din lege
(300 x 11/21), nu poate fi inventata.

Al treilea lucru pe care arhitectul il face SEPARAT, nici din comanda nici din raport: citeste
articolul din lege si compara cu ce face codul. Aia e responsabilitatea lui si nu se
externalizeaza.

## Mecanica portii (lectii 30.07.2026, platite)

Poarta e ce se ruleaza, nu ce se spune - iar doua capcane au lasat rezultate false:

- **Un commit contine exact ce poti NUMI. Se pune la index pe NUME, niciodata `git add -A` / `git add .`**
  (21.08.2026). `git add -A core/ frontend_test/ static/` a maturat in 5cc3c5e 234 de artefacte necomise -
  190 de capturi PNG de proba, scripturi de lucru, CSV-uri - peste care mesajul de commit nu putea spune
  nimic. Nu se repara rescriind istoria (era deja pe origin/main si pe backup, iar `--force` e interzis):
  se repara INAINTE, cu `git rm --cached`, si raman pe disc netrackate. GARD: `scripts/githooks/commit-msg`
  respinge un commit cu peste 8 fisiere NOI daca mesajul nu poarta `# multe-fisiere-ok: <motiv>`.

- **Exit-code-ul REAL al lui pytest, nu al ultimei comenzi din pipe.** `pytest -q | tail -1 && git
  commit` verifica iesirea lui `tail` (mereu 0), nu a lui pytest - a lasat un commit ROSU sa treaca
  (234f9ae, 30.07). Corect: `pytest -q > log 2>&1; PY=$?; tail -1 log; [ $PY -eq 0 ] && git commit`.
- **Garda anti-stale citeste data ultimului COMMIT (`git log --format=%at`), nu working tree-ul.**
  Rulata INAINTE de commit vede versiunea veche si da verde fals; abia dupa commit devine rosie.
  Ordinea pentru orice garda care citeste starea din git: commit INTAI, apoi poarta.

## 5. Predarea lucrului intre sesiuni

Pasii se scriu la INCEPUTUL firului (vezi 2.1), nu la inchidere.
La inchiderea sesiunii se actualizeaza doar: ultim, urmator, STARE - plus lista rescrisa, daca
s-a schimbat pe drum.

RITUALUL DE INCEPUT al fiecarei sesiuni, prima actiune, inainte de orice altceva:

  pwd; hostname; git log --oneline -1
  git rev-parse --is-inside-work-tree
  ./venv/bin/python -m core.agenda

Trebuie sa iasa /home/costin/iconta_nou, iconta-prod, si arbore git valid. Daca nu - OPRIRE
IMEDIATA, cu raport. Nu se lucreaza pe alta copie.

La PORNIREA unei CAMPANII (nu la fiecare sesiune), pe langa ritualul de mai sus, se ruleaza detectorul de drift
dus-intors al bifelor - DACA se aplica un declansator din GARZI cat.9 (campanie care atinge clustere deja bifate,
sau o bifa mai veche de pragul de acolo). Declansatorii, pragul si motivarea traiesc in GARZI cat.9 - nu se copiaza aici.

  ./venv/bin/python -m core.agenda_drift

Motivul pentru care e legat de pornirea campaniei, nu de un cron: un cron produce output pe care nu-l citeste nimeni
(sau devine zgomot in mail dupa a treia luna), si daca gaseste drift nu e nimeni cu context sa decida. La pornirea
campaniei exista si contextul, si decidentul.

- NEDECLANSAT (niciun cluster bifat atins, nicio bifa peste prag): se scrie EXPLICIT in raport
  "agenda_drift: nedeclansat, pentru ca ..." - ca la sectiunea 11 (CE AM ACTUALIZAT), niciodata tacut.
- CURAT: o linie in raport ("agenda_drift: curat, N functii verificate"), campania continua.
- DRIFT GASIT: NU se porneste campania peste el. Se raporteaza INTAI; decizia (reverificarea la sursa a bifelor
  afectate) e a lui Costin. O bifa cu drift dus-intors poate insemna ca verificarea la sursa (√) nu mai tine.

## 6. Oprirea obligatorie

Sesiunea SE OPRESTE si raporteaza daca:
- structura presupusa in brief nu se regaseste in cod: fisier inexistent, functie cu alta
  semnatura, tabel fara coloana asteptata, ancora de patch care nu se potriveste
- temeiul cautat nu se gaseste sau nu transeaza
- o poarta de validare pica
- se apropie limita de context inainte de terminarea pasului

NU SE INVENTEAZA, NU SE ADAPTEAZA, NU SE CONSTRUIESTE PE PRESUPUNERE.

Cand o sesiune se opreste pentru limita de context: comite ce e complet si functional, scrie
predarea in TESTE.md, raporteaza.

## 7. Regula de redirectionare

AGENDA SE MODIFICA INTAI, APOI SE EXECUTA.

Ce se lucreaza intra in TESTE.md la "In lucru acum" INAINTE de a incepe - FIRUL SI PASII LUI,
nu doar titlul firului. Ce nu e acolo, nu se lucreaza.

Daca se cere ceva din afara agendei, sesiunea semnaleaza: "Asta nu e in agenda. Urmatorul pas
din agenda e X. Modificam agenda intai, sau lasam X pentru mai tarziu?" Nu refuza - intreaba.

Pe 27.07 s-a lucrat o zi intreaga la reparatii care erau deja consemnate ca amanate intr-un
registru pe care nimeni nu-l citea.

## 8. Ce nu e responsabilitatea noastra

DATELE INTRODUSE DE CONTABIL. Corectitudinea lor e raspunderea lui profesionala.

A noastra e:
- sa le ducem NEALTERATE de la introducere pana la declaratie
- sa aplicam corect legea peste ele

Bug-ul din 29.07 era exact in prima categorie: contabilul scrisese 4050 lei in contract, iar
aplicatia trimitea 3497 la calcul. Aia e imputabila noua.
