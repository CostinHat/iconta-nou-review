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
  ICONTA_STATUS.md). Actualizat DOAR la finalul zilei, nu după fiecare task
- `~/iconta_nou/DECIZII.md` — DE CE am făcut așa. Registru de decizii cu temei,
  alternative respinse și limite. Se ADAUGĂ cronologic, nu se editează istoria.
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
- comite si impinge pe server
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
4. Code comite si impinge pe server. UN PAS NESALVAT PE SERVER NU S-A INTAMPLAT
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

CAND SE APLICA (incadrarea o stabileste executorul la finalul executiei, pe ce s-a intamplat efectiv, nu pe ce
se astepta la inceput):

- Raport COMPLET (titlu + sectiunile 1-10): inchidere de cluster; campanie multi-pas; orice modificare de logica
  fiscala; orice modificare care schimba iesirea catre ANAF.
- Raport SCURT (titlu + sectiunile 1, 2, 5): modificare de registru sau procedura fara efect pe cod executabil;
  interventie de infrastructura; campanie de un singur pas fara neconformitate gasita.
- Fara raport: niciodata. Orice comanda executata produce cel putin raport scurt.
- Incadrarea se declara in titlu, dupa numarul de pasi: "| COMPLET" sau "| SCURT". Daca incadrarea e ambigua,
  se alege COMPLET.
- Incadrarea pe ce s-a intamplat efectiv, nu pe ce se astepta: o campanie pornita ca SCURT care descopera o
  neconformitate devine COMPLET.

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

## 2.3 CONTINUITATE INTRE CLUSTERE (02.08.2026, ceruta de Costin)

Dupa raportul unui cluster inchis, executorul NU se opreste sa intrebe ce urmeaza. Ruleaza
`core.agenda.urmator_cluster()` si porneste campania pentru clusterul indicat, IN ACEEASI TURA.

Se opreste si cere decizie DOAR daca:
- clusterul urmator e BLOCAT si TOATE cele de dupa el sunt blocate;
- campania cere o DECIZIE DE PRODUS (scop, push, migrare pe date reale);
- a aparut o NECONFORMITATE care cere oprire conform ciclului (vezi CICLUL DE NECONFORMITATE);
- CONTEXTUL se apropie de epuizare - atunci se opreste la GRANITA CURATA DE COMMIT, cu predare scrisa.

Push-ul ramane decizie EXCLUSIVA a lui Costin (decizia c, DECIZII.md). Executorul commite LOCAL si continua
cu clusterul urmator, FARA sa astepte push.

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
