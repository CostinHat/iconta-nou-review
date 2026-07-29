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
  ICONTA_STATUS.md). Actualizat DOAR la finalul zilei, nu după fiecare task
- `~/iconta_nou/DECIZII.md` — DE CE am făcut așa. Registru de decizii cu temei,
  alternative respinse și limite. Se ADAUGĂ cronologic, nu se editează istoria.
  Nu e normativ — norma trăiește unde se aplică și se verifică mecanic
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

## LOCUL DE LUCRU — verificare obligatorie la fiecare sesiune (29.07.2026)

**Se lucrează EXCLUSIV pe server: `costin@178.105.201.56`, `~/iconta_nou`, branch `main`.**
Acolo e singura aplicație. Nu există alta.

**Înainte de PRIMA modificare din fiecare sesiune, verifici și arăți:**

    pwd; hostname; git log --oneline -1
    ./venv/bin/python -m core.agenda

Trebuie să iasă `/home/costin/iconta_nou` și `iconta-prod`. Dacă nu iese așa, **te
oprești** și spui unde ești și cum ai ajuns acolo. Nu modifici nimic până nu se confirmă.

**De ce.** Pe 27.07.2026 s-au pierdut ore reparând cod care nu rulează nicăieri: fuseseră
raportate trei defecte „confirmate" (D101 pe coloane greșite, arbori paraleli `declaratii/`
și `motor/`, 946 de teste cu fake-uri) care nu existau pe server — erau într-o copie locală.
Serverul are **un singur arbore: `core/`**. Nu există `declaratii/` și nu există `motor/`.

**Ritualul de agendă (29.07.2026).** PRIMA ACȚIUNE din fiecare sesiune, înainte de orice altceva:
rulează agenda (`./venv/bin/python -m core.agenda`) și ARATĂ rezultatul. Nu începe să lucrezi la ce ți
se cere până n-ai arătat unde suntem.

DACĂ ți se cere ceva care NU e în agendă: spune-o explicit, cu formula „Asta nu e în agendă. Următorul
pas din agendă e X. Modificăm agenda întâi, sau lăsăm X pentru mai târziu?" Nu refuza — semnalează și
așteaptă decizia.

Motivul: fără asta, planul se erodează fără ca nimeni să observe. S-a întâmplat: pe 27.07 s-a lucrat o zi
întreagă la reparații care erau deja consemnate ca amânate într-un registru pe care nimeni nu-l citea.

REGULA DE REDIRECȚIONARE: dacă apare ceva ce nu știm acum și vrem să schimbăm direcția, MODIFICĂM AGENDA
ÎNTÂI, apoi ne ținem de ea. Agenda (TESTE.md + test_datorie.py) e sursa; ce nu e acolo nu se lucrează. Un
lucru nou se adaugă în TESTE.md sau ca xfail ÎNAINTE de a începe lucrul la el.
