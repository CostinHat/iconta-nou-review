# METODA DE VERIFICARE

Scrisă 20.08.2026, după ce discuția „ce e, de fapt, verificarea vizuală" a arătat că metoda exista doar
ca practică, nu ca text. Până atunci trăia împrăștiată: cele trei acte într-un docstring de gardă,
calibrarea instrumentelor în memoria de sesiune, restul în cap. **Ce nu e scris nu se poate contrazice.**

Documentul ăsta e METODA. Regulile de proces (lanțul, poarta, raportul de 11 secțiuni) rămân în
CLAUDE.md; aici e doar cum se verifică ceva și cum se construiește un instrument care măsoară.

---

## 1. Cele TREI ACTE, separate deliberat

Verificarea vizuală de până acum le prăbușea într-unul singur: mă uitam la ecran și, în același timp,
jucam comparator cu o așteptare nescrisă. Așa se ajunge să raportezi „curat" pe un ecran față de care nu
ai, de fapt, nicio așteptare cu care să compari.

| act | ce face | unde trăiește (exemplu viu) |
|---|---|---|
| **observația** | constată fapte, **fără verdict**: „în caseta X e cifra Z" | `frontend_test/vizual/scan_casete.py` → artefact JSON |
| **așteptarea** | ce TREBUIE să fie acolo, scrisă **ÎNAINTE** de observație | `frontend_test/vizual/harta_casete.py` |
| **comparația** | **altă instanță** confruntă ce a văzut unul cu ce știe altul că trebuie să fie | `core/test_harta_casete.py` |

Formularea lui Costin, care a fixat regula: *„privitul în casetă îți spune că acolo este cifra Z. Altă
instanță compară ce a văzut unul, cu ce știe altul că trebuie să fie."*

**De ce contează ordinea:** o așteptare scrisă DUPĂ observație nu e o așteptare, e o descriere. Se
potrivește întotdeauna.

## 2. Cele PATRU SURSE ale unui ecran

O casetă nu se verifică dintr-o singură direcție. Fiecare are patru surse independente, iar dezacordul
dintre oricare două e constatarea:

1. **codul de randare** — ce ar trebui să fie acolo
2. **sursa de date** — ce valoare ajunge acolo
3. **regula-lege** — ce ar trebui să fie valoarea
4. **randarea** — ce apare efectiv

Un scan care se uită doar la (4) confirmă că aplicația e consecventă cu ea însăși, nu că are dreptate.

## 3. PRECONDIȚIA: harta casetelor

Nu se verifică un ecran fără hartă. Harta conține: **anatomii** (formele de rând), **structura**
(casetele, cu sursa și condiția de apariție, citibile mecanic), **felurile** (nomenclator ÎNCHIS — un fel
nou produs de backend fără intrare în hartă = ROȘU, nu omisiune tăcută), **temeiul**, **constrângerile**
între casete și **limitele** declarate.

Constrângerile poartă DOUĂ câmpuri, fiindcă unul singur minte: `marcaj` (cine decide) și `stare` (ce face
azi: verifică / datorie / neexercitat / așteaptă decizie).

## 4. TEMEI LEGAL nu e REGULĂ DE PRODUS

Cele două **se revizuiesc diferit**. Un temei legal se schimbă când se schimbă legea, și nu decizi tu
nimic. O regulă de produs se schimbă când decizi tu, iar „mai e bună?" e o întrebare legitimă oricând.

Amestecate, o regulă de produs devine imposibil de repus în discuție — nimeni nu contestă un articol de
lege — iar o prevedere legală devine negociabilă, ceea ce e mai rău. Instanța care a produs regula:
indicatorul de patru ochi; etichetat temei legal în loc de control intern, nimeni n-ar fi întrebat dacă
„posibil" înseamnă >=2 validatori.

**Al treilea fel** — regulă derivată dintr-un act care adaugă o alegere proprie — nu cere un al treilea
câmp: e cazul în care AMÂNDOUĂ sunt pline. Termenul care se mută în ziua lucrătoare următoare e lege;
alegerea de a afișa firma ca restanțieră de a doua zi e produs. `regula_produs` spune CE ADAUGĂ peste act,
nu reformulează actul.

Fiecare regulă de produs poartă **decizia și data**. Funcția spune ce face; decizia spune de ce și când.
Fără dată, peste șase luni nu se știe dacă regula a fost gândită sau a apărut din inerție.
`NEDOCUMENTATA` e un răspuns valid — tăcerea nu.

Gardat: `core/test_harta_temei.py`.

## 5. Cum se construiește un INSTRUMENT DE MĂSURĂ

**Regula de intrare:** nu repara fragmente dintr-o clasă nemăsurată. Când nu se știe cât de mare e clasa,
măsurarea trece înaintea reparării unei bucăți din ea — altfel alegi ce repari după ce ți-a picat sub
ochi, nu după cât cântărește.

Șase pași, în ordinea asta:

1. **Nu produce lista întâi.** Un scan pe cod găsește mii. Taxonomia descoperită după 4.000 de rânduri e
   descoperită prea târziu.
2. **Calibrare în MAI MULTE DIRECȚII, nu una.** O singură țintă lasă instrumentul să treacă pe gol în
   celelalte. La scanul de constante: `25` trebuie să cadă în „nesursat", `4050` în „sursat", `40` (cod
   județ) în „nomenclator", `cote_tva` 21/11 în „temei în proză" — și **fiecare direcție a picat efectiv
   o dată** în construcție.
   **Și contra-direcția.** O clasă care „sursează" poate ȘTERGE datorie: la clasa E, regula largă ar fi
   mutat 100 din 126 în „sursat în proză". Deci fiecare clasă nouă primește și aserțiuni că anume cazuri
   RĂMÂN în țintă, nu doar că anume cazuri ies din ea.
3. **Privește un eșantion de ~30 înainte de orice total.** Acolo apare taxonomia reală.
4. **Verifică LA SURSĂ primele N de pe lista de ardere și publică rata de fals-pozitiv.** Eșantionul
   de la 3 privește clasa în agregat; el NU prinde un caz al cărui temei se vede doar deschizând
   fișierul (`COTA_STANDARD = 21` nu se deosebește de nimic într-un rând de scan). Ce l-a prins a fost
   Regula de Aur aplicată propriei măsurători, la prima intrare pe care urma s-o „repari".
   **Un total fără rată de eroare măsurată e o afirmație, nu o măsurătoare** — la scanul de constante
   rata era 28 din 126, adică un sfert din lista de ardere.
5. **Confruntă instrumentul cu cine mai are o opinie despre aceleași obiecte.** Verificatorul ținea
   `cote_tva.py` pe `_TVA_EXCLUSE` („aici cotele sunt așteptate"), scanul îl raporta nesursat — două
   măsurători ale aceluiași lucru, niciodată comparate. Testată retroactiv, confruntarea ar fi dat 9
   semnale din prima zi, **fără să deschizi vreun fișier**. Întreabă mereu ce registru de excepții,
   listă de excluderi, hartă sau xfail vorbește deja despre obiectele tale: un dezacord între două
   măsurători e cel mai ieftin semnal că una dintre ele are o clasă nedistinsă.
6. **Zgomotul exclus se NUMĂRĂ, nu se aruncă tăcut** — altfel filtrul devine el însuși o afirmație
   neverificată.

7. **Recalibrează după FIECARE atingere a instrumentului, nu o dată la început.** O calibrare făcută
   pe versiunea 1 nu spune nimic despre versiunea 3. Orice filtru adăugat ca să scoată zgomot poate
   scoate și datorie, iar momentul în care se adaugă e exact momentul în care nimeni nu se mai uită la
   cazurile cunoscute.

**O listă de scutiri prea largă orbește exact ca un tipar mort — și e mai greu de văzut, fiindcă arată ca
precizie.** (§8 din raportul I1, 22.08.2026.) Un tipar mort se vede: nu potrivește nimic, iar cifra iese
zero. O scutire prea largă potrivește, apoi scoate — și cifra rămâne plauzibilă.

Instanța: prima formă a sub-instrumentului C din `core/scan_garzi.py` scutea orice modul care folosea
`tokenize` sau `ast.parse`, ca dovadă că „știe să scoată proza". Amândouă sunt scutiri false —
tokenizarea *colectează* string-urile, iar `ast.parse` lasă docstringurile ca noduri `Constant` — și
scutirea a înghițit exact cazul canonic pe care instrumentul fusese construit să-l prindă
(`test_schema_coloane`).

**Deci: scutirile se numără separat de zgomot, iar fiecare scutire primește proba că un caz cunoscut NU
scapă prin ea.** Fără proba aia, o scutire e o afirmație despre cod, adăugată tocmai în momentul în care
atenția era pe altceva.

**Și întreabă-te unde trăiește lucrul căutat, nu unde stă fișierul de test.** Domeniul greșit e cea mai
ieftină formă de orbire: `test_datorie.py:144` afirma „nimic nu scrie în `state_plata`" și căuta doar în
`core/`, în timp ce `main.py` scria.

### Formele de orbire prin construcție, cu instanțele lor

| formă | instanță |
|---|---|
| măsori proxy-ul, nu lucrul | inventarul 31.07 a numărat TESTE care asertează o constantă — orb la cele care trăiesc doar în producție |
| cheia pe rolul sintactic greșit | v1 al scanului a căutat aritmetică+comparații; `_ZIUA.get(tip, 25)` e un *default*, deci invizibil |
| clasifici ramura, nu obiectul | v2 a clasat `Decimal("4050")` ca nesursată deși avea `Temei` pe același rând |
| domeniul de căutare prea îngust | `test_datorie.py:144`; și scanul ăsta, până a fost măsurată rădăcina |
| **câmp gardat ca PREZENȚĂ, necontrolat ca ADEVĂR** | corpusul avea **177 de amprente** `.sha256` și **niciun test care să le compare cu fișierele**. Prezența era gardată, adevărul nu — iar un câmp completat pe care nimic nu-l verifică arată identic cu unul verificat. Clasa, nemăsurată încă, e restanța R7 |
| **act INCOMPLET în corpus** | OMFP 2634/2015 era în corpus cu **o anexă din trei**. Nomenclatorul din copia veche sare de la 14-4-4 la 14-4-13, deci „registrul de casă" nu se găsea — și absența arăta exact ca un act care nu prevede lucrul căutat |
| **formă INIȚIALĂ citită ca formă la zi** | copia din corpus a Reglementărilor contabile (OMFP 1802/2014) e forma inițială 2014. Am citit de acolo criteriile de mărime — 350.000 EUR / 700.000 EUR — și le-am scris în registru. La zi sunt **2.250.000 lei / 4.500.000 lei**, modificate de ORDIN 4.164/2024. Actul era complet, corect și în vigoare; **forma** era veche |
| scutire prea largă, adăugată ca precizie | scutirea `tokenize`/`ast.parse` din `core/scan_garzi.py` (sub-instrumentul C): pusă ca să scoată falsele pozitive, a scos chiar cazul canonic. Arată ca precizie, se poartă ca orbire |
| temei prezent, dar în PROZĂ | `cote_tva.py` citează art. 291 în antet și per categorie — scanul cerea obiect `Temei`, deci îl raporta nesursat. ÎNCHISĂ 21.08: clasa E, ancorată pe valoare (proza trebuie să conțină și citarea, și valoarea). 126 → 98 |
| **filtru ÎNVECHIT — nu produce zgomot, produce TĂCERE** | `scripts/trasee_tabele.json` fusese generat **înainte** ca tabela `artefacte_produse` să existe, deci filtrul care trebuia să scoată numele inventate tăia o tabelă **reală**. Consecința s-a propagat tăcut: **patru trasee** păreau că nu scriu nimic, **trei** rămâneau clasificate PARȚIAL — *„produce și nu se păstrează”* — o zi întreagă după ce persistența fusese construită. **Distincția față de celelalte forme din tabel:** un filtru prea larg produce **zgomot**, care se vede și se numără; unul învechit produce **absență**, iar absența arată exact ca un rezultat corect. Un instrument care se lărgește greșit se aude; unul care se îngustează greșit tace. **Consecința de metodă:** orice fișier generat pe care se sprijină un filtru poartă întrebarea *„mai vechi decât ce filtrează?”* — vechimea lui se compară cu lumea pe care o descrie, nu se presupune. |
| **POZIȚIA de afișare nemodelată — criteriul e bun, îi lipsește LOCUL** | gardul de diacritice pe JS scana patru poziții (`eticheta:`, `.innerHTML`, `nav.*`, noduri-text). Etichetele formularelor de operațiuni stau în alte două — al doilea argument **pozițional** al unui constructor de câmp, și al doilea element al perechii de opțiune. **125** de șiruri afișate au trăit ASCII sub un clichet de **0**. Distinctiv față de „domeniu prea îngust": aici domeniul era corect pentru formele cunoscute; formele **noi** de scriere n-au fost adăugate. Iar defectul fusese **numit în scris** de lotul 13, și garda a rămas verde peste text — *o descriere nu e o gardă* (R168) |
| **domeniul rămas în urma PROPRIEI politici** | `scan_citate` culege obiecte `Temei` din `core/common`. Decizia 73 cere ca temeiul să stea în **modulul regulii**, nu în rută — deci *cu cât repo-ul urmează mai bine regula, cu atât gardul vede mai puțin*. Măsurat la lărgire: citări văzute **36 → 60**, verbatim **12 → 26**; `TEMEI_291_5`, scris exact după politică, nu era verificat de nimeni. **Consecința de metodă:** când o regulă de scriere se schimbă, se întreabă care instrument o măsura pe cea veche (R169) |
| **filtru de TEXT într-un ENUMERATOR = plafon tăcut** | proba celor 32 de formulare culegea butoanele vizibile și arunca `t.length > 46`. Registrul are **34**; exact două titluri trec de 46 de caractere. Cifra „32 din 32" a intrat în trei registre. *Nu erau „fără defect", erau nedeschise, purtând numele unora probate.* Reparat pe structură (`data-op`), nu pe un prag mai mare — un prag mai mare e același defect, amânat (R170) |


### Două forme de mascare, adăugate 26.08.2026

**`or <implicit>` pe o intrare de la om nu e o gardă, e o MASCĂ.** `str(corp.get("cont_x") or "707")`
citește ca „dacă lipsește, pune 707". Face și altceva: lasă **orice** valoare adevărată să treacă
neatinsă, inclusiv `"   "`. Diferența nu se vede la citire, fiindcă ochiul completează „deci e
validat". Instanța: 19 situri, iar consecința era invizibilă în trei straturi deodată — `NOT NULL`
nu oprește spațiile, un `CHECK (cont <> '')` nu le-ar fi oprit, și nici verificarea de echilibru
nu le vedea, fiindcă `if cont` e adevărat pe un șir de spații. **Regula: pe o valoare venită din
afară, normalizarea și validarea sunt două operațiuni, iar `or` nu e niciuna.**

**Un PLAFON SUPERIOR scris ca măsurătoare.** `scan_trasee` atribuia unei rute reuniunea tabelelor
scrise **oriunde** în modulele pe care ruta le atinge. În text arăta identic cu SQL-ul măsurat pe
rută: `scrie solduri_initiale (DELETE/INSERT)`. Măsurat: **108 din 192** de pași purtau doar
atribuiri moștenite. Instanța care a scos-o la iveală n-a fost un instrument, ci **omul care scria
verificările**: patru rute de `/incarca` cu docstring *„nu salvează"* apăreau ca scriind în tabele
de date. **Regula: o supra-aproximare are voie să existe, dar trebuie să se NUMEASCĂ** — altfel cine
o citește scrie o aserțiune pe ea. Forma: `poate atinge, prin modul (PLAFON, nemăsurat pe rută)`.

### O mutație care probează o CALIBRARE trebuie să lovească exact linia care face distincția (26.08.2026)

**Cerut de Costin**, după instanța din aceeași zi. O mutație e proba că un test poate deveni roșu.
Dar un test poate deveni roșu **din alt motiv decât cel probat** — și atunci proba confirmă
altceva decât crede cine a scris-o.

**Instanța.** Gardul `test_rol_pe_efect` are o calibrare: *sonda de credențiale nu prinde o simplă
citire*. Am mutat sonda ca să întoarcă `True` mai des, aștept­ându-mă ca acea calibrare să pice. A
picat **testul principal** (multe rute deodată fără rol), iar calibrarea a rămas **verde** —
fiindcă distincția citire/scriere se face pe **altă linie**, o poartă `INSERT|UPDATE|DELETE` care
se scurtcircuitează înainte de linia mutată. Mutația era reală, roșul era real, și totuși nu
proba nimic despre ce voiam să probez.

**Regula:** *o mutație care probează o calibrare trebuie să lovească **linia care face distincția**,
nu o linie din aceeași funcție.* Verificarea e ieftină și e mecanică: **se cere ca mutația să facă
roșu TESTUL ANUME**, nu suita. Dacă pică alt test, mutația e greșit țintită — nu gardul e slab.

**Cum se scrie**, ca să nu depindă de memorie: bucla de mutații ține, lângă fiecare mutație,
**numele testului așteptat**, și cade dacă a picat altul. Fără asta, „trei mutații, trei roșii" e o
propoziție adevărată despre altceva.

*Aceeași familie cu interdicția 76 — calibrarea pozitivă nu dovedește că instrumentul nu ratează —
dar un pas mai jos: aici nici proba calibrării nu dovedește ce pare.*

### O gardă care încodează o decizie NUMEȘTE AXA pe care păzește (26.08.2026)

**Cerut de Costin, cu motivul lui:** *„R42 spunea că nota nu primește rol fiindcă nu e artefact
predat. R55 pune rol fiindcă schimbă starea. O gardă care încodează o decizie trebuie să numească
axa pe care păzește — altfel a doua decizie pe altă axă o face să pară contrazisă."*

**Instanța, din aceeași zi.** `test_nota_contabila_NU_cere_admin_firma` încoda R42 (25.08): *nota
nu e artefact predat, deci nu primește rol*. Când R55 (26.08) a pus rol pe validare — pe criteriul
*ce schimbă ce datorează firma* — garda a picat. **Și a avut dreptate să pice:** o decizie nouă
atinsese ceva ce o decizie veche păzea. Ce lipsea era ca garda să spună **pentru ce** păzea, ca
diferența dintre „te contrazic” și „vorbim despre altceva” să fie citibilă fără să reciteșt
ambele decizii.

**Ce cere regula, practic:**

1. **Numele testului și mesajul de eșec spun axa**, nu doar concluzia. Nu *„nota nu cere rol”*, ci
   *„nota nu cere rol PE CRITERIUL «artefact predat»”*.
2. **Excepțiile pe altă axă se enumeră**, fiecare cu decizia care o justifică — nu se topesc în
   condiția testului.
3. **Lista de excepții e bidirecțională**: o intrare care și-a pierdut motivul (ruta a dispărut,
   rolul s-a scos) trebuie să PICE, altfel lista devine amintire.

**De ce contează mai mult decât pare:** `METODA` §25 spune deja că *între două reguli scrise care
se contrazic câștigă cea păzită, și o face tăcut*. Regula asta e cealaltă jumătate — **cum faci ca
tăcerea aia să nu se producă**: o gardă care își numește axa nu poate anula o decizie de pe altă
axă fără ca cineva să vadă.

### Aducerea unui act e ea însăși o verificare

**Un act incomplet în corpus nu se deosebește de un act care nu spune ce cauți.** Amândouă produc
același rezultat la căutare: zero potriviri. Diferența — că într-un caz regula nu există, iar în
celălalt pagina lipsește — nu se vede din interiorul căutării. La fel, **o formă inițială nu se
deosebește de o formă la zi decât dacă o întrebi**: valorile citite din ea sunt reale, doar că ale
altui an.

**Deci la aducere, două lucruri obligatorii:**

1. **Un act cu anexe se aduce ÎNTREG, sau se scrie ce lipsește.** Nu „am adus ordinul" — ordinul și
   anexele lui sunt documente separate pe portal, iar regula căutată stă aproape întotdeauna în anexă.
2. **Se scrie CE FORMĂ e** — inițială, la o dată, sau consolidată la zi — și se confruntă cu
   `TIP_FORMA` din `anaf_surse/gen_index.py`, care deja poartă răspunsul pentru fișierele legate de
   cote. Două instrumente care vorbesc despre același fișier și nu se confruntă e chiar tiparul de la
   pasul 5 de mai sus.

**Ce urmează din asta, ca restanță scrisă:** câte alte acte din corpus sunt parțiale sau sunt forme
vechi citite ca fiind la zi. Se ține în `CONFORMITATE.md`, la RESTANȚE (R1 și R4), cu condiția de
deblocare scrisă — nu aici.


**Și o amprentă care nu se poate reproduce nu răspunde la întrebarea pentru care a fost pusă.**
Descărcat de două ori, același act de pe portal dă **doi octeți diferiți**: pagina poartă URL-uri de
CSS/JS versionate. S-a văzut la prima verificare de după commit — `legea_82_1991_consolidat.html`
apărea modificat cu 1629 de linii, iar **textul extras era identic**. O amprentă pe pagină răspunde la
*„e acesta fișierul pe care l-am stocat?"*; interdicția 52 întreabă altceva — *„s-a schimbat TEXTUL
după aducere?"* — și pentru ea amprenta trebuie luată pe textul extras. De-aceea fiecare act adus
primește acum **două**: `<nume>.html.sha256` și `<nume>.txt.sha256`.

**Fiecare gard nou primește o aserțiune anti-vacuu:** un gard care nu găsește nimic TRECE. Un gard cu
domeniul greșit e mai rău decât niciun gard — raportează verde despre o lume pe care n-o vede.

## 6. CLICHET, nu xfail

Un `xfail` **înregistrează** o datorie; nu o **împiedică**. Inventarul de pe 31.07 a fost xfail și clasa a
produs a cincea apariție opt zile mai târziu. Un xfail e o notiță; un clichet e o poartă.

**Per fișier, nu global** — global, o reparație într-un modul plătește pentru o încălcare nouă în altul, și
totalul stă pe loc arătând verde. Baseline-ul se COBOARĂ pe măsură ce se arde, niciodată nu se ridică, iar
un fișier nou pornește de la 0.

RED-proof se face din **copie de siguranță**, niciodată `git checkout` — ăla șterge lucrul necomis.

## 7. Dezacordul DOC contra COD nu spune cine greșește

Spune că afirmația n-a fost niciodată verificată la sursă. Clasa a apărut de cinci ori în 20.08, în
direcții OPUSE: la `d112_reconciliere` docstring-ul era stătut dar avea dreptate (arbitrul DUK i-a dat
dreptate, nu codului mai nou); la `common.pastila_firma` docstring-ul avea dreptate și codul nu fusese
scris niciodată să-l respecte.

Deci nici „codul e mai nou, deci corect", nici „docstring-ul e intenția, deci corect" nu sunt reguli.
**Tranșarea vine din AFARĂ**: arbitru (validator/XSD/spec), lege, sau un argument semantic explicit. Iar
după tranșare afirmația se **leagă** printr-un test; docstring-ul nu se înmoaie ca să se potrivească
codului.

## 8. VERDE e o AFIRMAȚIE

„Am verificat și e în regulă" — nu „n-am ce contrazice". Griul spune că afirmația nu se poate face, iar o
afirmație parțial imposibilă nu devine adevărată prin partea care s-a putut face.

Gri și verde sunt pe **axe diferite**: verde/galben/roșu măsoară GRAVITATEA, gri măsoară CUNOAȘTEREA. Un
`max` peste amândouă e o eroare de categorie. O problemă CONFIRMATĂ bate o necunoaștere; o absență
confirmată de problemă NU o rezolvă.

Clasa a apărut de trei ori în două zile — F3/F7 pe tabele goale, raportul meu de audit pe t001, și
semaforul pe care îl vede clientul. Gardat: `core/test_pastila_gri.py`.

## 9. CE NU ACOPERĂ metoda

- Comparatorul citește artefactul UNEI SINGURE firme. Punctul orb e **firma, nu ecranul**: un scan vede
  doar stările pe care le produc datele firmei pe care rulează.
- Gardul temeiurilor verifică doar că citarea **aterizează** pe un document existent — nu că documentul
  spune ce pretinzi. Aia cere arbitrul.
- Așezarea în pagină nu e prinsă de niciun verificator. Reorganizarea unui ecran cere confirmare.

## 10. DISCIPLINA EXECUȚIEI — greșeli proprii, scrise ca să nu se repete

Secțiunile 1–9 spun cum se verifică. Asta spune ce am greșit executând, în ciuda lor. Fiecare rând
are instanța care l-a produs; fără instanță ar fi un principiu, iar principiile nu se pot verifica.

**10.1 Nu descrie un mecanism după NUMELE lui. Deschide-l.**
Două instanțe în aceeași tură (21.08.2026):
- am scris în registrul de excepții că D390 are „poartă: lună închisă" — sună a completitudine. Citit
  la sursă, `d390_are_operatiuni` face `prima_urm > azi -> None`: e luna **calendaristică**, nu
  evidența închisă. O firmă care n-a introdus încă facturile de iulie primește în august „nu se
  datorează pe iulie".
- am scris că `d300_reconciliere` „dublează maparea lui d300 și trebuie reparată prin import din sursa
  unică". Antetul modulului spune exact pe dos: duplicarea e **deliberată**, iar
  `test_non_tautologie_*` o apără — a doua cale n-are voie să împartă cod cu prima, altfel gardul de
  conținut devine tautologic. „Reparația" ar fi șters gardul.

E aceeași orbire ca „măsori proxy-ul, nu lucrul", mutată în scris: numele unui mecanism e un proxy
pentru corpul lui. **Un semnal spune UNDE să te uiți, nu CE să repari.** Instrumentul avea dreptate
că e ceva acolo; eu am greșit ce anume, fiindcă n-am deschis fișierul.

**10.2 Înainte de a adăuga o intrare într-un registru, citește CONSUMATORUL lui.**
Am înregistrat semnalele R6 ca `casete` în harta ecranului. Gardul a picat corect: „casete cu
condiție necunoscută (ar fi sărite tăcut)". Casetele sunt SECȚIUNI, iar comparatorul le caută după
titlu în DOM; semnalele sunt un tip de RÂND în două casete existente. O intrare într-un registru e o
promisiune făcută codului care îl citește — dacă nu știi cine îl citește, nu știi ce promiți.

**10.3 Scrie FIȘIERUL, nu scriptul care scrie fișierul.**
Trei defecte de escaping într-o singură tură, toate din același tipar: text românesc („…") și `\n`
puse în literali Python care generau alt cod. Un ghilimet drept de închidere a rupt de două ori
fișierul generat, iar `\n` dintr-un șir ne-raw a rupt al treilea. Regula: **textul trăiește în
fișiere**; scripturile doar le citesc și le aplică. Timpul pierdut pe escaping e timp în care nu
verifici nimic.

**10.4 Captura care se PRIVEȘTE se ia din codul care RULEAZĂ.**
Prima captură a semnalelor R6 arăta textul de dinaintea schimbării, fiindcă serviciul rula încă
commitul anterior. Captura probează versiunea pornită, nu fișierul de pe disc. Dacă repornirea nu e
în puterea ta, capturează DUPĂ publicare și privește atunci — și spune în raport care versiune ai
privit.

**10.5 Ce a mers, și de ce se păstrează.**
Defectul care a contat cel mai mult în tura asta — semnalul care repeta integral motivul randat
imediat deasupra lui, același paragraf de patru rânduri de două ori — n-a fost găsit de niciun test,
de niciun contor și de nicio măsurătoare. A fost găsit **privind captura**. Numărătoarea spunea „4
rânduri `.cf-semnal`, axe 0 violări": tot verde, și tot greșit. Privitul rămâne singurul instrument
care găsește dublarea, aglomerarea și tonul.

### 10.6 — Un gard „nu face X" trebuie să provoace întâi starea în care X ar fi tentant

`test_verificarea_nu_scrie_nimic` număra rândurile înainte și după, pe o lună **fără nicio
contradicție**. O verificare care ar fi emis singură corecții ar fi trecut senin: n-avea ce corecta.
Gardul măsura corect, într-o lume în care întrebarea nu se punea.

Regula: un test de forma „funcția asta NU face X" e vid dacă nu construiește întâi condiția în care X
ar fi rezultatul natural. Numărătoarea înainte/după nu e suficientă — trebuie ca între ele să existe
motivul pentru care cineva ar scrie.

Aceeași formă, altă față: `test_emiterea_persista` chema `emite` **o singură dată**, deci nimic nu
asertea idempotența, și mutația care o scotea trecea verde. Un gard pe o proprietate care se vede
doar la a doua apăsare trebuie să apese de două ori.

**Cum se prinde:** RED-proof. Amândouă au ieșit doar fiindcă am mutat implementarea și am văzut că
gardul rămâne verde. Nicio citire a testului nu le-ar fi arătat.

### 10.7 — Mutația din test trebuie DOVEDITĂ, nu presupusă

Un ajutor de test muta salariul cu `UPDATE salariu_istoric SET salariu_brut = salariu_brut + 1000`.
Tenantul are istoricul **gol** (salariul vine din bridge-ul `salariati.salariu_brut`), deci UPDATE-ul
prindea ZERO rânduri. Două teste „probau" că documentul emis rezistă la schimbarea datelor de sub el
— într-o lume în care nimeni nu schimbase nimic. Au trecut, și n-au verificat.

Regula: după ce muți starea într-un test, **asertează că mutația s-a văzut** înainte de a asertea
concluzia. O linie: `assert dupa != inainte, "mutația nu a schimbat nimic"`. Fără ea, un test de
rezistență e o tautologie costisitoare.

### 10.8 — REGULA DE AUR se aplică și la botez

Am definit `_schema_sau_404(tenant_id, ctx)` fără să caut întâi numele. Exista deja
`_schema_sau_404(ctx, tenant_id)` în același fișier; definiția mea a suprascris-o tăcut și a rupt
**47 de rute** cu argumentele inversate. Python nu spune nimic la redefinire.

„Verifici la sursă înainte de a afirma «absent»" nu e doar despre funcționalități — e și despre
simboluri. Un `grep -n "def <nume>"` înainte de a scrie `def` costă o secundă. Aici a costat o rundă
întreagă de suită plus un diagnostic pe o urmă de eroare care arăta ca un bug în rute străine.

### 10.9 — Cheia de idempotență prea largă sare peste munca reală

Scripturile de patch pornesc cu `if <cheie> in text: return "deja scris, sar"`. **Cheia trebuie să fie
unică pentru ce SCRIE funcția aceea**, nu o frază care poate ajunge acolo pe altă cale.

**De trei ori într-o singură zi (22.08.2026), aceeași greșeală, cu efecte diferite:**

1. Cheia `## Restanțele` — secțiunea exista deja (scrisă de Costin), deci funcția a returnat imediat și
   **n-a mai aplicat lărgirea excepției în două locuri**. Am raportat lărgirea „în patru locuri"; erau
   două. **O afirmație falsă într-un raport, produsă de un `return` prea devreme.**
2. Cheia `cele trei praguri` — fraza fusese tocmai introdusă de textul excepției, în aceeași rulare,
   deci secțiunea pragurilor n-a mai fost scrisă.
3. Cheia `de_preluat` — cuvântul apărea deja în tabelul pragurilor, adăugat cu câteva minute înainte,
   deci instanța din secțiunea 17 n-a mai fost adăugată.

**Regula:** cheia se pune pe **titlul sau fraza pe care funcția o scrie ea însăși**, cât mai lungă și
cât mai specifică. Iar dacă o funcție face **mai multe** schimbări, ori are o cheie per schimbare, ori
se sparge în funcții.

**A patra instanță (22.08.2026), și cea mai subtilă:** cheia `"CONFIRMAT de Costin"` era **subșir** al
textului pe care funcția urma să-l înlocuiască — `"DE CONFIRMAT de Costin"`. Nu venea din alt patch și
nu fusese introdusă de o rulare anterioară: era **chiar în ținta înlocuirii**. Deci regula se
strânge: **cheia se alege din textul NOU, nu din cel vechi, și se verifică să nu fie subșir al
niciunuia dintre ele.**

**Și consecința care contează cel mai mult:** un patch care „sare" nu eșuează — **raportează succes**.
De aceea greșeala se vede abia la verificarea de după, dacă se face. Verificarea de după nu e opțională.

### 10.10 — Un comentariu în cod nu e o declarație de perimetru

Formularea, din 22.08.2026: **un comentariu în cod nu e o declarație de perimetru — nu-l citește
nimeni care se uită unde suntem, n-are stare, și nu se aprinde când devine neadevărat.**

**Instanța:** ruta `/tenants/{id}/jurnal-marja` își declară singură, în comentariu, *„raport regim
marjă — fără UI încă, păstrat deliberat"*. Perimetrul declarat există însă doar pentru două firme
(t006, t001); t007 și t008, purtătoarele regimurilor de marjă, n-au niciunul. Deci absența ecranului
era **uitată în registru și declarată lângă cod** — două lucruri diferite.

**Unde se declară, deci:** în registrul de perimetru al firmei, sau ca restanță cu felul de blocaj
potrivit. Comentariul rămâne util pentru cine citește codul; nu ține locul niciuneia.

### 10.11 — Un `tenant_id` în rută nu e ornament

**Formularea:** *un `tenant_id` într-o rută nu e ornament — un 200 confirmă că tenantul există.*

**Instanța, 22.08.2026:** ruta nouă `GET /tenants/{tenant_id}/concedii/coduri` întorcea **200 pe
tenantul altui cabinet**. Raționamentul care a produs-o era plauzibil și de asta e periculos:
*„codurile de concediu nu depind de firmă, deci `tenant_id` e decorativ aici"*. Nu e: chiar dacă
răspunsul nu conține nicio dată a firmei, **codul de stare e el însuși o informație** — spune că
tenantul există și că nu ești refuzat. Interdicțiile 24 și 25.

Prinsă de `test_izolare_structurala`, care încearcă toate cele 255 de perechi (rută × metodă) cu un
token din alt cabinet. **Regula practică:** dacă ruta are `{tenant_id}` în cale, prima ei linie e
verificarea accesului — indiferent ce întoarce.

### 10.12 — Proza care descrie codul poate fi falsă de la naștere, nu doar îmbătrânită

Registrele au deja o clasă pentru **doc-stătut**: textul a fost adevărat, codul s-a schimbat sub el,
iar gărzile anti-stale îl prind comparând datele. **Asta e altceva:** o frază care descrie codul poate
fi **greșită din clipa în care a fost scrisă** — și atunci nicio gardă de vechime n-o atinge, fiindcă
nu s-a învechit nimic.

**Instanța (22.08.2026):** `core/export_saga.py:157` afirma că *„WinMentor cere `status='emisa'`"*.
F187-fix scosese acel filtru din WinMentor **înainte** ca fraza să fie scrisă. Nimeni n-a fost indus
în eroare până acum fiindcă niciun apelant nu folosea parametrul — dar fraza ar fi îndrumat exact pe
dos primul om care ar fi citit-o ca să afle regula.

**Ce se poate verifica mecanic și ce nu:** o afirmație despre **propriile** valori implicite se poate
confrunta cu semnătura (proxy scris, 1 instanță găsită). O afirmație despre **alt modul** nu are proxy
— se verifică doar citind ambele. De aceea regula e: *o frază care descrie comportamentul altui modul
poartă referința la locul din care a fost citită*, cum poartă `Temei` un citat.

**Testul practic, când scrii proză despre cod:** dacă fraza ar fi fost falsă în ziua în care ai
scris-o, ce ar fi prins-o? Dacă răspunsul e „nimic", fraza are nevoie de o referință, nu de mai multă
grijă.

### 10.13 — Un total care poartă numele unei componente e o afirmație falsă, chiar dacă cifra e corectă

Gărzile de conținut verifică **cifre**: reconcilierea pe a doua cale, egalitățile stricte, plafoanele.
Niciuna nu se uită la **eticheta** de lângă cifră. Iar o etichetă e o afirmație: „Deducere personala:
1.513,75" spune că deducerea personală e 1.513,75. Când numărul e de fapt un total din trei deduceri
distincte în lege, afirmația e falsă — și niciun gard n-o vede, fiindcă suma e corectă.

**Instanța (22.08.2026):** fluturașul tipărea `deducere['total']` sub eticheta „Deducere personala".
Calculul avea deducerea desfăcută corect în `baza`/`tineri`/`copii`; API-ul a colapsat-o la `total`;
hârtia a dat totalului numele uneia dintre componente. Fiecare strat era apărat de garda lui, și
niciunul nu apăra numele. 3 din 5 cazuri obișnuite, 2 din 24 de salariați reali.

**Regula, generalizată:** *agregarea nu e neutră.* Când un total împrumută numele unei componente,
încetează să fie o rotunjire a adevărului și devine o afirmație greșită. Locurile de căutat sunt cele
în care legea distinge și codul adună: deduceri, scutiri, cote, plafoane.

**Testul practic:** citește eticheta cu voce tare ca pe o propoziție, apoi întreabă dacă e adevărată
pentru cifra de lângă ea. „Deducere personala 1.513,75" — e adevărat? Nu. Nicio gardă de cifre nu pune
întrebarea asta, fiindcă nu e o întrebare despre cifră.

### 10.14 — Un graf cheiat pe nume simplu afirmă despre dependențe ceea ce nu poate ști

Un instrument care răspunde la *„ce depinde de ce"* e mai periculos decât unul care răspunde la
*„câte sunt"*: cifra greșită se vede, legătura greșită nu. `core/graf_temei` indexează funcțiile
într-un dicționar plat, cheiat pe **numele simplu**, peste tot `core/*.py`, incluzând definițiile
imbricate — deci două funcții cu același nume din fișiere diferite sunt **una singură**, iar cea care
supraviețuiește e decisă de **ordinea alfabetică a fișierelor**.

**Instanța (22.08.2026):** un helper imbricat numit `_suma`, adăugat într-un fișier care sortează
târziu, a preluat apelanții celorlalte cinci `_suma` din `core/`. Clusterele de TVA au apărut brusc ca
depinzând de salariul minim. Măsurat după aceea: **118 din 1.411 nume** sunt definite în mai multe
fișiere, iar printre ele sunt chiar `genereaza` (53 de fișiere), `pull` (52) și `build_xml` (49).

**Ce contează, dincolo de instanță:** greșeala are **două semne**, și doar unul e zgomotos. Un nume
preluat ADAUGĂ dependențe false — numărul crește, ratchet-ul cade, cineva se uită. Același mecanism
ȘTERGE dependențe reale când numele tău e preluat de altcineva — și atunci instrumentul raportează
liniște despre o lume pe care n-o mai vede. **Un gard care poate greși în ambele direcții și e
observabil doar într-una e, practic, negardat.**

**Testul practic, când construiești un instrument care leagă lucruri:** întreabă ce se întâmplă dacă
două lucruri diferite primesc aceeași cheie. Dacă răspunsul e „unul îl înlocuiește pe celălalt", cheia
e prea scurtă — și adaugă întrebarea a doua: *pe care direcție a greșelii se aprinde ceva?*

**Corolar, pentru cifrele deja scrise:** o cifră măsurată cu un instrument despre care afli ulterior
că era conflat nu devine falsă, dar devine **necreditabilă** — se re-măsoară, nu se moștenește.
`STALE_BAZA_BASELINE = 14` e într-o astfel de poziție.

### 10.15 — Un instrument se calibrează pe modul în care POATE greși, nu pe cazul fericit

Ziua de 23.08.2026 a dat patru instanțe ale aceleiași greșeli, la patru instrumente diferite, toate
scrise de mine, toate în câteva ore:

| instrument | forma de suprafață pe care s-a legat | ce ar fi trebuit |
|---|---|---|
| `graf_temei` | cheie pe **numele simplu** al funcției | `(fișier, nume)` |
| `vigoare_punct` | marcajul se termină la primul `)` · un singur tipar de numerotare | fereastră feliată · ambele tipare |
| `scan_instrumente` (calibrarea) | **cuvântul** „calibrare" în docstring | aserțiune care pinează un literal |
| `scan_instrumente` (legătura) | **numele fișierului** `test_<modul>.py` · pomenirea modulului | importul, și numele aduse de el |

**Ce au în comun:** fiecare avea calibrare, și fiecare trecea. `graf_temei` are patru afirmații
pozitive și una negativă **din prima zi** — toate cinci trec la fel de bine pe graful conflat ca pe cel
reparat, fiindcă toate privesc o zonă unde numele erau unice. Calibrarea exista; **nu atingea modul în
care instrumentul putea greși.**

**Regula:** *„a fost calibrat" nu e o întrebare binară.* Se întreabă **pe ce**, și dacă printre cazuri
se află **modul de eșec propriu construcției lui**:

- un instrument care **cheie** ceva → se calibrează pe o **coliziune de chei**;
- unul care **citește marcaje** → pe **două marcaje lipite**, și pe unul cu paranteze în adresă;
- unul care **decide după un cuvânt** → pe un text unde cuvântul apare **fără** lucrul, și pe unul unde
  lucrul apare **fără** cuvânt;
- unul care **numără o clasă** → pe un membru al clasei pe care nu trebuie să-l găsească (**calibrare
  negativă**). Măsurat pe 23.08: **doar 4 din 12** instrumente cu gărzi o au.

**Testul practic:** înainte de a folosi un instrument, scrie în două rânduri **cum ar arăta un caz pe
care construcția lui îl ratează prin natura ei**. Dacă nu poți, nu-l cunoști încă. Dacă poți, ăla e
primul test.

**Corolar, verificat de patru ori într-o zi:** greșelile astea au fost prinse **toate** de un caz
cunoscut, și **niciuna** de recitire. Recitirea confirmă ce credeai deja; cazul cunoscut nu.

### 10.16 — O stare afirmată ca ACTUALĂ se recitește imediat înainte de a fi scrisă

**Regula.** **Orice stare afirmată ca ACTUALĂ se recitește imediat înainte de a fi scrisă în raport,
nu la începutul turei.** O stare citită la minutul 3 al unei ture de 30 și raportată la minutul 30 e
o **amintire**, nu o măsurătoare — și se scrie cu ora citirii. Corolarul: nicio propoziție de forma
„e exact cum ai lăsat-o" fără o recitire între ea și trimiterea raportului. **Sunt doi actori pe baza
asta, nu unul.**

**Instanța, 27.08.2026, ora 19:27:** am raportat `nume_ales` ca **NULL** — la **11 minute** după ce
fusese scris. Citirea era adevărată când am făcut-o și falsă când am scris-o, iar între cele două
apăsase Costin un buton. Nimic din raport nu spunea la ce oră fusese citit, deci nimic nu-l putea
pune la îndoială.

**De ce nu e o neatenție, ci o clasă.** Baza nu e a mea. Orice stare care se poate schimba prin ecran
— portofoliul, alegerile consemnate, perioadele confirmate — are **doi** actori, iar al doilea nu-mi
spune când apasă. O măsurătoare pe cod poate îmbătrâni numai dacă schimb eu codul; una pe **date**
îmbătrânește singură.

**Testul practic, înainte de a trimite raportul:** pentru fiecare propoziție care spune *este*, nu
*a fost*, întreabă când a fost citită. Dacă răspunsul nu e „acum", ori se recitește, ori se scrie ora
și devine o afirmație despre trecut. Ora e mai ieftină decât recitirea și e întotdeauna disponibilă.


### 10.16b — A doua instanță, și mecanismul care a ieșit din ea (28.08.2026)

Regula din §10.16 s-a scris pe 28.08.2026, dimineața. **În aceeași zi, la douăzeci de minute după ce
am comis-o**, am scris în `PREDARE_LANT.md`: *„**0 din 18** firme au `nume_anaf`."* Recitit pe date:
**1 din 18** — iar denumirea chiar diferea de cea de la ANAF. Concluzia rămânea adevărată din
întâmplare (caseta nu apare), dar din **alt motiv**: alegerea fusese deja făcută.

**Ce face instanța asta mai utilă decât reparația ei:** cifra fusese **deja invalidată o dată**.
Tabelul „cifre invalidate" din **aceeași predare** scria că *„0 din 17"* fusese invalidată în ziua
precedentă în favoarea lui *„1 din 18"*. Am purtat-o mai departe **din memorie**, peste propriul meu
tabel, la douăzeci de minute după ce scrisesem regula care o interzice.

**Concluzia, și e despre metodă, nu despre atenție:** *o regulă scrisă nu ține fără control mecanic.*
E chiar §14, aplicată unei reguli din §10.

### Mecanismul, construit (28.08.2026, decizia lui Costin: „da, se construiește")

**Cifrele despre DATE din predare sunt un bloc GENERAT.** `scripts/scan_predare_cifre.py`
interoghează baza și produce tabelele — portofoliu, cabinete, divergențe, instantanee ANAF, urme de
scoatere, scheme, contor, orfani, duplicate. `core/test_predare_cifre.py` compară blocul din document
cu interogarea **de la rulare**, caracter cu caracter, și pică dacă diferă. Același tipar ca Partea
XII din `TRASEE.md` și ca inventarul din `GARZI.md`.

**Trei lucruri pe care garda le face, și merită numite separat:**
1. **doc↔cod** — o cifră care nu mai descrie baza pică poarta;
2. **nicio cifră culeasă nu rămâne nescrisă** — dacă instrumentul măsoară ceva ce nu ajunge în tabel,
   blocul ar fi identic cu el însuși și ar **tăcea** despre ea; a doua direcție se verifică separat;
3. **blocul nu poartă ora măsurătorii** — ar fi fost firesc s-o poarte, și ar fi fost greșit:
   comparația ar fi picat la **fiecare** rulare, iar cineva ar fi scos garda ca să poată comite.

**CE RĂMÂNE AFIRMAȚIE DATATĂ, deliberat** *(regula, nu doar practica de azi)*:
- **cifrele de PROCES** — „a câta tură", „câte commituri în urmă", „a doua respingere a porții". Nu
  se pot interoga de nicăieri; se scriu cu **ora citirii**, nu ca fapte atemporale.
- **judecățile** — „ce nu e adevărat despre starea asta" e proză, și rămâne proză.
- **cifrele despre COD** — rute, gărzi, teste — au deja instrumentele lor, fiecare cu garda ei; nu se
  dublează aici (regula sursei unice).

**CE NU FACE, declarat:** nu interzice o cifră de date în **proza** predării. Narațiunea are voie să
spună „cele patru firme"; ce nu mai are voie e ca **tabelul** să fie scris din memorie. Un gard care
ar interzice orice cifră din proză ar fi zgomot pe fiecare frază.

**LIMITA OPERAȚIONALĂ, măsurată la construcție și scrisă aici fiindcă e reală:** blocul e derivat din
date **vii**, nu din cod. Codul nu se mișcă singur în timpul porții; datele da. Deci:
- dacă portofoliul se schimbă între generarea blocului și sfârșitul porții (**~12,5 minute**), garda
  pică — **și pe drept**: documentul chiar nu mai descrie baza. Remediul e regenerarea, nu o
  toleranță. Operațional: blocul se regenerează **ultimul**, imediat înainte de commit.
- **predarea nu se mai poate scrie fără acces la bază.** În fluxul de azi asta e întotdeauna
  adevărat — se lucrează pe server, cu `db.env` încărcat, iar suita cere oricum baza. **Scenariul în
  care nu e:** un incident în care baza e jos. Atunci nu se poate nici rula poarta, deci nu se poate
  comite nimic — dar merită știut că handover-ul e blocat **exact când e mai necesar**. Dacă apare, se
  scrie predarea fără bloc și se declară de ce; garda va cere blocul înapoi la prima rulare verde.


## §30 — UN BLOCAJ DECLARAT PE UN SINGUR ARTICOL NU E BLOCAJ PÂNĂ NU I-AU FOST CITITE NORMELE DE APLICARE

*(30.08.2026, urcat de Costin ca **a doua instanță în două zile**. Nu e o observație despre neatenție:
amândouă citirile au fost corecte pe textul citit. Ce lipsea era **al doilea nivel al actului**.)*

### Cele două instanțe, cu ce a fost citit și ce nu

**1. „Corpusul nu poate sursa pragurile de mărime."** Citit: pct. 9 din OMFP 1802/2014, găsit
**trunchiat** exact la criteriile numerice (*„…se grupează în trei categorii, astfel: microentități;
entități mici; entități mijlocii și mari. **…**"*). Concluzia: actul e parțial, R3 nu se poate
construi. **Necitit:** același fișier conține actul **de două ori** — un cuprins cu elidări și corpul
complet, cu toate cele trei criterii, per literă, și cu actul modificator.

**2. „Registrul de evidență fiscală nu se poate construi, s-ar inventa un model."** Citit: art. 19 și
art. 68 din Codul fiscal; art. 68 alin. (9) trimite modelul la un ordin care nu era în corpus.
Concluzia: blocaj. **Necitit:** **normele** art. 19 — HG 1/2016, pct. 8 — care specifică **integral**
conținutul registrului pentru impozitul pe profit. Erau **două** registre, nu unul, iar numai al
doilea avea nevoie de ordin.

### De ce e o clasă, și nu de două ori aceeași greșeală

Un act fiscal românesc trăiește pe **cel puțin două niveluri**: legea/ordinul spune **că** se
datorează ceva, iar normele de aplicare spun **ce anume conține**. Ambele instanțe de mai sus au
declarat imposibilitatea de la primul nivel — și în amândouă răspunsul stătea la al doilea.

*Forma e înșelătoare tocmai fiindcă citirea de la primul nivel e corectă.* Un blocaj declarat astfel
nu arată ca o eroare: arată ca prudență. Iar consecința e mai rea decât o cifră greșită — o cifră
greșită se corectează la următoarea măsurătoare, dar **un blocaj declarat oprește munca**, și nimeni
nu remăsoară un lucru despre care s-a scris că nu se poate face.

### Ce cere, practic

**Înainte de a scrie că ceva nu se poate construi din lipsă de temei**, se citesc, în ordine:

1. **articolul** — spune că se datorează, și cine datorează;
2. **normele lui de aplicare** — HG-ul pentru Codul fiscal, ordinul pentru reglementările contabile.
   *Aici stă, de regulă, conținutul;*
3. **actele la care trimit ele** — dacă norma zice „prin ordin al ministrului", ordinul se caută. Iar
   dacă e numit printr-o **trimitere**, nu printr-un număr, se caută **după titlu**
   (`scripts/portal_legislativ.py cauta-titlu`) — nu se ghicește numărul. *Un act adus pe baza unui
   număr ghicit e mai rău decât unul lipsă.*

**Și încă una, din prima instanță:** când un act din corpus apare **trunchiat**, se caută a doua
apariție în același fișier înainte de a-l declara parțial. Portalul livrează adesea un cuprins cu
elidări **și** corpul complet, în aceeași pagină.

### Ce NU cere

Nu cere citirea întregului act înainte de orice afirmație — ar fi un impozit pe fiecare pas. Cere
**cele trei niveluri, și numai atunci când concluzia e „nu se poate"**. O afirmație despre ce *există*
se poate face de la primul nivel; una despre ce *lipsește* nu.

## §29 — O CALIBRARE POZITIVĂ ANCORATĂ PE INSTANȚELE CARE URMEAZĂ SĂ FIE REPARATE SE AUTODISTRUGE

*(30.08.2026, măsurat la prima reparație din lista 5. Nu e o ipoteză: instrumentul a picat efectiv,
la prima atingere a codului pe care el însuși o ceruse.)*

`scripts/scan_r97_livrat_tacut.py` măsoară clasa *„ruta livrează, ecranul tace"*. Calibrarea lui
pozitivă cerea ca **cele șase instanțe fondatoare** — `nr_curent`, `total_debit`, `total_credit`,
`deducere_tineri`, `deducere_copii`, `cas_suprataxa` — **să fie GĂSITE ca tăcute**, cu `assert`. Adică
ancora care dovedea că instrumentul vede clasa erau **chiar defectele pe care le scosese ca să fie
reparate**.

**Ce s-a întâmplat:** prima reparație — randarea celor trei coloane ale registrului-jurnal — a făcut
`assert`-ul să cadă. Instrumentul a devenit inutilizabil **exact în tura în care începea munca pe
care el o ordonase**, și nu pe un defect al lui: pe un succes.

### De ce e o clasă, nu un accident

Tiparul se naște de fiecare dată la fel, și pare corect când îl scrii: *„instrumentul trebuie să
dovedească că vede clasa; am două instanțe cunoscute; le pun în calibrare."* Instanțele cunoscute
sunt însă, prin construcție, **exact cele care vor dispărea** — un instrument de măsurat o datorie e
făcut ca datoria să scadă. Cu cât e mai bun, cu atât mai repede își taie propria ancoră.

Are aceeași formă cu **§14 (doc↔cod)** și cu **§25**: o afirmație scrisă o dată, adevărată atunci,
care nu are niciun mecanism prin care să afle că s-a schimbat lumea de sub ea. Diferența e că aici
mecanismul **există și e un `assert`** — deci nu îmbătrânește tăcut, cade zgomotos. Asta e partea
bună; partea rea e că cade **peste reparație**, iar cine îl vede roșu are toate motivele să creadă
că a stricat ceva.

### Regula

**Ce trebuie să rămână adevărat nu e că aplicația ARE defectul, ci că DETECTORUL îl vede.** Deci
calibrarea se ancorează pe un **caz construit**, care nu se schimbă când se schimbă aplicația:

1. clasificarea se scoate din bucla vie într-o funcție **pură**, ca să poată fi chemată pe date
   inventate — cât timp stă înăuntrul buclei, singura calibrare posibilă e pe starea aplicației;
2. cazul sintetic acoperă **fiecare coș** al clasificării, în amândouă direcțiile (§22): ce trebuie
   găsit **și** ce n-are voie să apară;
3. **instanțele fondatoare rămân, dar ca RAPORT, nu ca aserțiune** — instrumentul tipărește, pentru
   fiecare, dacă mai e tăcută sau a fost reparată. Așa reparația **se vede** în ieșirea
   instrumentului, în loc să dispară odată cu aserțiunea care o interzicea.

Punctul 3 nu e cosmetic: fără el, mutarea calibrării pe sintetic ar șterge singura urmă că cele șase
au existat vreodată.

### Corolarul, mai larg decât un instrument

Orice clichet, prag sau aserțiune care numește **instanțe** în loc de **proprietăți** are aceeași
soartă. Un clichet pe un NUMĂR e sănătos — scade, și e bine. O aserțiune pe o LISTĂ DE NUME e o
promisiune că numele alea vor rămâne defecte.

## §28 — O ÎNLOCUIRE DE TEXT ÎNTR-UN INSTRUMENT DE GENERARE AFIRMĂ CĂ A GĂSIT POTRIVIREA

*(28.08.2026, a treia recurență — regula se scrie abia acum, și asta e chiar partea de reținut.)*

`str.replace` **nu se plânge** când nu potrivește nimic: întoarce textul neatins. Un script care
peticește un document și nu verifică tipărește *„OK"* peste o modificare **care nu s-a produs**, iar
documentul rămâne în forma **veche** — care de acum arată curentă. Aceeași formă are `re.sub`, și
orice generator care rescrie un bloc între marcaje fără să verifice că marcajele mai există.

**REGULA:** orice înlocuire de text într-un instrument care **scrie un document** trebuie să afirme
că potrivirea s-a găsit — și **de câte ori** s-a găsit. Nu „a mers", ci *„s-a potrivit exact o dată"*.
Unealta care o face e `scripts/inlocuieste.py`; păzită de `core/test_inlocuire_afirmata.py`.

**Cele patru feluri de ratare, toate tăcute:**

| ratarea | ce se întâmplă fără aserțiune |
|---|---|
| ancora **nu se potrivește** (documentul s-a schimbat sub script) | scriptul zice OK, documentul rămâne vechi |
| ancora e **ambiguă** | se schimbă **toate** aparițiile, nu cea vizată |
| `vechi == nou` | trece verde și nu face nimic |
| **marcajul de bloc lipsește** (generator) | blocul generat nu-și găsește locul, documentul rămâne pe generația veche |

**INSTANȚA, cu prețul ei.** Tabelul de restanțe din `PREDARE_LANT.md` a driftat de **trei ture
consecutive**: șablonul local rămăsese în urma peticului aplicat direct pe server, iar înlocuirile
următoare n-au mai potrivit nimic. De fiecare dată predarea a ieșit cu rânduri vechi despre restanțe
închise — adică **exact minciuna pe care predarea e construită s-o prevină**. Primele două ori am
corectat rândul; a treia oară am pus aserțiunea, iar ea a prins-o pe loc.

**De ce nu s-a pus un clichet pe „instrumente care înlocuiesc fără să verifice":** **măsurat, în repo
nu există niciunul.** Pe fișierele urmărite de git (fără `venv/`), șase funcții cheamă
`.replace`/`.sub` și scriu un fișier în același loc — și toate șase sunt **formatări de șir sau
transformări de conținut** (`core/duk.py` taie un mesaj de eroare, `main.py` construiește răspunsuri,
`portal_legislativ` curăță HTML, `versioneaza_assets` face `re.sub` **cu raportare de erori**).
Niciuna nu peticește un document pe o ancoră. Clasa trăiește în scripturile de patch **de fiecare
tură**, care nu sunt urmărite de git. *Un clichet peste un domeniu gol ar fi chiar tiparul pe care
metoda asta îl combate: un verde care nu poate deveni roșu.*

**Corolarul, mai larg decât înlocuirea:** o operație care poate eșua **întorcând un rezultat
plauzibil** are nevoie de o afirmație despre efectul ei, nu despre rularea ei. *Un `replace` fără
aserțiune nu e o modificare, e o speranță.*

---

## §27 — VERIFICAREA VIZUALĂ SE FACE PE **REGULI**, NU PE ASEMĂNARE CU O CAPTURĂ

**DECIZIA DE ARHITECTURĂ (Costin, 03.09.2026), verbatim:**

> *„Un baseline vizual e o probă care îmbătrânește prin construcție — se strică la orice schimbare
> legitimă, iar atunci se regenerează ca să treacă și devine formalitate. Ce se păstrează sunt
> regulile, care nu îmbătrânesc: contrast minim, nicio revărsare la 393 px, elementele principale
> vizibile fără derulare. Alea au prins lucruri reale; capturile n-au prins nimic."*

**CE S-A SCOS, cu totul:** `frontend_test/vizual/baseline_scan.py`, directorul `baseline/` cu cele
15 capturi de referință, rapoartele lui, și artefactele comparației (`b1_*`, `b2_*`, `cur_*`).
Împreună cu ele au ieșit din arbore **217** capturi neurmărite, adunate în săptămâni.

**DE CE E O DECIZIE, nu o curățenie.** Comparația pixel cu pixel are un mod de eșec care o
golește de sens **fără să se strice nimic**: orice schimbare legitimă de ecran o face roșie, iar
singurul răspuns practic e să regenerezi referința. După a doua regenerare, gardul nu mai
răspunde la întrebarea *„s-a stricat ceva?"*, ci la *„am regenerat de curând?"*. **Un gard care se
repară prin ștergerea propriei referințe nu e un gard.** *Contrastul aceleiași clase: gărzile de
regulă de mai jos au prins, în trei săptămâni, lucruri reale — contrast 3,82 pe o pastilă nouă,
revărsare la 393 px pe bara de sus, ținte de atingere sub 24 px. Comparația de capturi n-a prins
niciuna dintre ele, fiindcă toate au apărut **odată cu** captura de referință.*

**CE SE PĂSTREAZĂ — regulile, fiecare cu unealta ei.** Nu îmbătrânesc: nu descriu o stare, descriu
o constrângere.

| regula | unde se verifică |
|---|---|
| contrast minim, etichete, landmarks (WCAG AA) | `frontend_test/vizual/axe_scan.py` + `axe.min.js` vandorizat |
| **nicio revărsare orizontală la 393 px**, ținte de atingere ≥24 px, ce dispare pe touch | `frontend_test/vizual/mobil_scan.py` |
| **elementele principale vizibile fără derulare**; comportamentul la apăsare; text lung fără rupere | `frontend_test/vizual/interactiune_scan.py`, cuplat mecanic de `core/test_acoperire_vizuala.py` |

**Gardat**: `core/test_infra_vizuala.py` cere **uneltele de regulă** — și, în direcția opusă, cere ca
`baseline_scan.py` și `baseline/` **să nu reapară**. *Fără a doua aserțiune, cineva ar putea reface
mecanismul peste o lună fiindcă „lipsește ceva din infra vizuală", iar motivul pentru care a fost
scos nu trăiește în cod, ci aici.*

---

**CE RĂMÂNE ADEVĂRAT DESPRE CAPTURI: cele care nu se pot reface.**

O captură care **dovedește că un lucru s-a întâmplat o dată**, pe o stare care **nu mai există**
(firma ștearsă, cabinetul dus, divergența nereproductibilă fără tot montajul) **nu e regenerabilă** —
e singura urmă. Aia **intră în repo, selectiv**, și se **numește în `CONFORMITATE.md`, la restanța pe
care o probează**. Altfel e un fișier binar fără proprietar, iar peste o lună nimeni nu mai știe ce
arată.

**TESTUL, într-o întrebare:** *pot să o refac rulând un instrument?* Dacă **da**, nu intră — și de
azi nici nu se mai ține pe disc. Dacă **nu**, e probă și intră, cu trimitere la restanță.

**GARDAT**, fiindcă „suspectă" nu se autoverifică (`core/test_capturi_numite.py`): fiecare `.png`
**comis** sub `frontend_test/` trebuie să aibă numele scris în `CONFORMITATE.md`. Se citește din
**index**, nu de pe disc — o captură abia pusă în stage e prinsă la commitul care o aduce.

**LIMITA, declarată:** distincția rămâne o **judecată**, nu un criteriu mecanic. Ce o ține onestă e
obligația de a lega captura de o restanță.

**Excepția pinată** — opt capturi de pe 20.08, dinainte ca regula să existe — **nu are voie să
crească**. A le numi retroactiv ar însemna să scriu, zile mai târziu, ce probează fiecare: exact
repovestirea refuzată la `GARZI.md`.

**ȘI GARDA CARE FACE DIN §27 O REGULĂ, nu o intenție** *(Costin, 03.09.2026, verbatim)*: *„Adaugă la
curățenie: o gardă care refuză introducerea de fișiere imagine ca probă vizuală. Fără ea, §27 rescris
rămâne o intenție și capturile revin la prima tură de interfață. Capturile pentru diagnostic, în
timpul unei ture, rămân permise — dar nu se salvează și nu devin bază de comparație."*

`core/test_fara_probe_imagine.py` — două interdicții și o graniță:

| ce | verdict |
|---|---|
| capturi făcute **în timpul** turei, ca să te uiți la ele | **permis** — așa se găsesc defecte apăsând |
| aceleași capturi **salvate în repo** | **refuzat** — mulțimea imaginilor din index e pinată |
| cod care compară două imagini | **refuzat** — pe **import**, structural, nu pe numele funcției |

*Granița nu e „ce e o probă", care e o judecată, ci **„intră în index?"**, care e mecanic.* Clichetul
merge în **amândouă** direcțiile: una nouă pică, dar și una **dispărută** pică, cerând să fie scoasă
din listă.

<!-- CAI-SCOASE:START (căi pe care metoda le NUMEȘTE, dar care NU mai există; gardul le cere ABSENTE) -->
- `frontend_test/vizual/baseline_scan.py` — scos 03.09.2026 prin decizia din §27
<!-- CAI-SCOASE:STOP -->

*Blocul de mai sus există fiindcă `core/test_metoda_vie.py` cere ca fiecare cale numită de metodă să
existe pe disc — pe drept, altfel metoda ar descrie instrumente dispărute. Dar o metodă trebuie să
poată numi și ce a **scos**, altfel n-ar putea scrie niciodată de ce. Blocul e o declarație
structurală, nu o excepție tăcută: gardul cere pentru căile din el **exact opusul** — să nu existe.
Dacă `baseline_scan.py` reapare, blocul devine roșu.*

## 11. O POZIȚIE se atribuie după CE PRODUCE modulul, nu după cum se numește

**Regula.** Când clasifici un artefact — *există / nu există*, *predare / construcție*, *ore / zile* —
deschizi modulul și confrunți **ce produce** cu **ce cere norma**. Numele funcției, existența rutei și
numărătoarea de obiecte dintr-un domeniu vecin **nu sunt dovezi de acoperire**.

**De ce e regulă și nu observație: e o rată, nu o instanță.** Măsurat pe 23.08.2026, la verificarea
triajului: **6 artefacte clasificate greșit din 16 atinse** — 4 din 12 la pragul 3, 2 din 4 la poziția
2. Toate din același gest.

**Greșeala merge în AMBELE direcții, și de asta nu se prinde cu o singură bănuială:**

| direcția | instanța (23.08.2026) | ce a costat |
|---|---|---|
| numele **creditează** un motor inexistent | `carte_mare` în `core/motor.py` — înveliș de o linie peste `agrega_conturi`, care întoarce rulaje totale. Norma cere defalcarea rulajului debitor pe conturi corespondente. Ce există e balanța de rulaje | o construcție necesară, amânată ca „predare" |
| lipsa numelui **ascunde** ce există | `registru_inventar` în `core/rip_api.py` are producător, rută în `main.py` și ecran — și era trecut „fără producător". La fel `jurnal-marja` | o construcție pornită degeaba |
| o numărătoare **dintr-alt domeniu** ținută drept acoperire | *„valorile există: 57 de obiecte `Temei`"* — cele 57 sunt în `core/common.py` și `core/salarizare.py`; **cele nouă module de declarație au zero** | o listă întreagă ordonată pe un cost fals |

**Cum se aplică, mecanic:**

1. **Numește ce produce funcția**, în termenii normei — nu în termenii ei proprii. *„Întoarce
   `{cont: {debit, credit, sold}}`"* nu e un răspuns; *„întoarce rulaje totale, fără conturi
   corespondente"* e.
2. **Verifică domeniul numărătorii.** O cifră adevărată despre modulul A nu spune nimic despre modulul
   B. Întrebarea de control: *pe ce fișiere s-a numărat?*
3. **Caută în ambele direcții.** După ce ai confirmat că ceva lipsește, caută-l și sub alte nume: un
   artefact poate exista pentru **alt regim** (partidă simplă vs dublă) și să pară absent.
4. **Zero consumatori nu înseamnă zero producători, și invers.** Sunt două măsurători, nu una.

**Ce NU acoperă regula:** nu spune că o clasificare făcută corect e și completă. Spune doar că una
făcută pe nume nu e o clasificare — e o presupunere cu aspect de măsurătoare. Vezi `CONFORMITATE.md`,
secțiunea TRIAJ, cele două corectări din 23.08.

## 12. O MĂSURĂTOARE NOUĂ se confruntă cu ce spune deja registrul despre același obiect

**Regula.** Înainte de a scrie o cifră, caută în registru ce s-a mai spus despre **același obiect** și
pune cele două afirmații una lângă alta. Dacă nu se confruntă, registrul poate ține ani întregi două
propoziții contradictorii despre același lucru, fiecare adevărată în contextul ei.

**Instanța care a produs regula (23.08.2026).** În `CONFORMITATE.md` stăteau, la **900 de rânduri** una
de alta: *„valorile există: 57 de obiecte `Temei`"* (justificarea pentru care lista 5 era „predare, ore")
și *„structurile de declarație au **zero** legături structurate"* (interdicția 60). Amândouă măsurate,
amândouă adevărate, **niciodată confruntate** — iar din prima s-a ordonat o listă întreagă de muncă.

**A doua instanță, în aceeași zi, și e a corectării înseși.** Corectarea a fost măsurată cu
`grep 'Temei('` și a scris *„cele nouă module au ZERO"*. Fals: `d101` construiește două prin **aliasul
`_Tm(`**, pe care grep-ul nu-l vede. Re-măsurat cu AST, rezolvând aliasurile: 57 în `core/`, din care 2
în cele nouă module. **Concluzia a rezistat; instrumentul, nu.** De unde a treia formă a regulii de la
§11: *nici măcar corectarea unei măsurători pe nume nu se face pe nume.*

**Cum se aplică, mecanic:**

1. **Caută obiectul, nu formularea** — „ce mai spune registrul despre modulele de declarație?", nu „ce
   mai spune despre `Temei`".
2. **Pune cifrele una lângă alta în text**, chiar dacă se confirmă. O confruntare care nu se vede n-a
   avut loc.
3. **Când se contrazic, întâi verifică domeniile** — de obicei nu una e falsă, ci măsoară altceva.
4. **Instrumentul se numește lângă cifră.** „57" nu spune nimic; „57, AST, constructori sub orice
   alias, `core/` fără teste" se poate contesta.

## 13. Un NOMENCLATOR se completează din NORMĂ, nu din ce produce aplicația

**Regula.** Când construiești un nomenclator care are o sursă oficială, îl completezi **din act**, cu
toate intrările pe care actul le numește — inclusiv pe cele pe care aplicația nu le produce azi. Ce
lipsește din mapare **nu se șterge din nomenclator**. Diferența dintre *ce numește norma* și *ce
produce aplicația* e o **măsurătoare**, nu o lipsă de îngrijire.

**Instanța care a produs regula (23.08.2026).** Maparea `inregistrari.sursa` → jurnal de origine, în
D406. Norma (OMFP 2634/2015, Anexa 1 pct. 52) numește cinci feluri de jurnal auxiliar; aplicația
produce patru. Al cincilea — *„operațiuni privind decontările cu furnizorii"* — a rămas în nomenclator
**fără mapare**, cu asta scris lângă el. Dacă l-aș fi șters fiindcă „nu-l produce nimeni", nomenclatorul
ar fi arătat complet, iar întrebarea *„ce fel de jurnal nu ținem?"* n-ar mai fi avut unde să se pună.

**Ce se câștigă, concret:**

1. **Absența devine numărabilă.** „4 din 5 feluri au mapare" e o cifră; „nomenclatorul e complet" e o
   impresie.
2. **Nomenclatorul nu se rescrie** când aplicația crește. Ziua în care apare o sursă de furnizori,
   intrarea e deja acolo, cu temeiul ei.
3. **Se vede în ce direcție e datoria.** Un nomenclator mai bogat decât maparea = funcționalitate
   lipsă. O mapare mai bogată decât nomenclatorul = **ceva ce inventăm** — iar aia e o afirmație către
   autoritate, nu o scăpare.

**Cum se aplică, mecanic:**

- Nomenclatorul se ancorează pe **textul actului**, verbatim, gardat prin căutare **literală în
  corpus** — o reformulare îl face roșu (vezi `core/test_d406_jurnal_origine.py`).
- **Ca CLASĂ, din 25.08.2026:** `core/nomenclatoare.py` (registrul ancorelor) + `core/
  test_nomenclator_pe_norma.py`. Până atunci regula asta trăia gardată **pe un singur fișier**, iar
  peste ea trecea un gard de clasă care cerea opusul — vezi §25.
- Maparea stă **separat**, și e decizie de produs; fiecare abatere de la lista normei se scrie ca
  abatere, cu motivul (la D406: `CASA`/`BANCA` sunt două identificatoare pentru un singur fel al
  normei; `AMORTIZARE` intră la *„alte operațiuni"*).
- Intrarea fără mapare **rămâne**, cu o notă de o linie: *nimic nu o produce azi*.

**Ce NU acoperă regula:** nu spune că nomenclatorul e corect — spune doar că diferența față de mapare e
vizibilă. Un act citit greșit produce un nomenclator greșit, complet și verificabil literal. Pentru
asta e §12: confruntarea cu ce spune deja registrul.

## 14. O REGULĂ SCRISĂ ȘI NEPĂZITĂ se citește ca respectată

**Regula.** O regulă de proces care are mecanism scris, dar niciun gard, **nu produce efect** — și, mai
rău, **consumă atenția care ar fi găsit-o**: cine o citește în plan o bifează ca existentă. Deci: orice
regulă de proces cu mecanism scris ori primește un gard, ori primește o **declarație scrisă** că nu e
gardabilă și cum se verifică altfel.

**Instanța nu e un caz, e o populație întreagă, măsurată la 100%** (23.08.2026). *Reaprinderea* e
scrisă în `PLAN_LUCRU.md` cu mecanism explicit — la fiecare tură se verifică ce restanțe au blocajul
dispărut, iar contorul de reluări crește. Măsurat: **`reluări` = 0 pe toate cele 25 de restanțe**, de la
prima până la ultima. **Regula n-a funcționat niciodată de când există.** Nu una dintre restanțe a fost
ratată — **niciuna n-a fost vreodată reluată.**

Iar consecința nu era teoretică: trei condiții se îndepliniseră fără să fie observate, dintre care una
(**R8**) se declanșase de două ori **în aceeași zi, prin commituri proprii**. Când reaprinderea s-a
făcut anume, prima restanță încercată (**R10**) s-a închis în **două minute** — nu era grea, era
neîncercată.

**De ce se promovează pe o singură instanță**, contra disciplinei de la §11 (*o instanță nu e o rată*):
fiindcă **instanța ESTE rata**. Populația măsurată e întreaga aplicare a regulii, de la nașterea ei, iar
rata de eșec e **100%**. O clasă cu o singură populație măsurată, în care populația e totul, nu e o
anecdotă.

**Cum se aplică, mecanic:**

1. **Fiecare regulă de proces cu mecanism scris primește un gard sau o declarație.** Declarația e
   acceptabilă — *„rapoartele nu trăiesc pe disc, deci enumerarea restanțelor nu se poate garda"* e un
   răspuns bun. Tăcerea nu e.
2. **Contorul e primul lucru de privit.** Un contor care n-a crescut niciodată nu spune „n-a fost
   nevoie"; spune „nimeni nu l-a atins".
3. **Se măsoară acoperirea gardului, nu doar existența lui.** Garda de reaprindere închide clasa în
   care declanșatorul e mecanic: măsurat, **1 din 18** condiții deschise are forma aceea. Un gard care
   acoperă 6% dintr-o clasă e un început, nu o rezolvare — și se scrie ca atare.
4. **Pârghia e adesea în FORMA regulii, nu în gard.** O condiție de deblocare scrisă *„la primul commit
   care atinge `X`"* se poate cabla; una scrisă *„se închide când inventarul există"* nu. Cine scrie
   condiția alege dacă ea va putea fi păzită.

**Ce NU acoperă:** nu spune că o regulă gardată e și respectată în spirit — gardul apără forma. Și nu
transformă o regulă negardabilă într-una proastă: unele nu se pot garda, iar declarația e răspunsul
corect (vezi §11 și `CONFORMITATE.md`, R10).

## 15. FIXTURA CARE NU ACOPERĂ CAZUL — o mutație care trece degeaba

**Regula.** O mutație se probează pe date care conțin **tranziția**, nu doar **starea**. Dacă fixtura e
uniformă pe dimensiunea pe care mutația o strică, mutația trece — iar gardul pare RED-probat fără să
fie.

**E o formă distinctă de orbire**, a treia, și n-avea nume până azi:

| forma | ce se strică | cum se vede |
|---|---|---|
| **tipar mort** | detectorul nu poate deveni roșu niciodată (regex imposibil, marcaj invizibil) | mutația trece, **și nicio dată n-ar ajuta** |
| **verde pe zero rânduri** | gardul rulează pe o mulțime goală | mutația trece, **fiindcă nu se compară nimic** |
| **fixtura care nu acoperă cazul** | gardul e corect, datele de probă sunt **prea uniforme** | mutația trece, **iar datele potrivite ar fi prins-o** |

**Instanța (23.08.2026).** `core/fisa_cont.py` calculează soldul cu sensul lui (`D`/`C`). Mutația
*„`sens_sold` devine `"D"` fix"* **a trecut** — fiindcă în fixtură toate rândurile aveau sold
**debitor**. Gardul era corect; datele nu conțineau **trecerea** D→C. Adăugat un caz în care soldul
trece prin zero, plus unul de sold zero: abia atunci mutația a picat. **Propria mutație a găsit gaura
propriei gărzi** — nu o citire, nu o recenzie.

**Cum se aplică, mecanic:**

1. **Numește dimensiunea pe care o strică mutația** — sens, semn, ordine, prezență, unitate.
2. **Întreabă dacă fixtura variază pe ea.** Dacă toate rândurile au aceeași valoare pe acea
   dimensiune, mutația e nefolositoare **înainte** de a o rula.
3. **Probează pe tranziție**, nu pe capete: soldul care trece prin zero, luna care schimbă cota, actul
   care se modifică între două citiri, lista care ajunge goală după ce a fost plină.
4. **O mutație care trece nu e o veste bună.** E fie gard slab, fie fixtură uniformă — și trebuie spus
   care dintre ele, altfel a doua se citește ca prima.

**Ce NU acoperă:** nu spune că o fixtură care variază e și suficientă. Acoperirea rămâne o judecată;
regula închide doar cazul în care mutația **nu putea** să prindă nimic.

## 16. VERIFICAREA SE FACE UNDE E NEVOIE, nu unde e ușor de făcut

**Regula.** Când verifici ceva, întreabă **unde trăiește lucrul căutat** — nu unde e cel mai comod să
te uiți. O verificare făcută în locul ușor produce un răspuns adevărat despre locul acela și fals
despre întrebare.

**E o singură clasă, nu trei** — formulare unificată la cererea lui Costin, 23.08.2026, după ce a treia
instanță a apărut în aceeași zi. Toate au aceeași formă: **s-a măsurat ce era la îndemână**.

| instanța | unde era ușor | unde era nevoie | ce a costat |
|---|---|---|---|
| **R10**, „grea" de 40 de commituri | să presupui că e grea | **s-o încerci o dată** | s-a închis în două minute; 40 de commituri de amânare |
| **condițiile de deblocare** — 1 din 18 cablabilă | să scrii proză | **să ceri forma** când se scrie condiția | 12 din 15 se puteau scrie cablabil; reaprinderea a rămas nepăzită |
| **lista de locuri la o schimbare de valoare fiscală** | să te iei după ce **pică** | **să faci lista din COD** | *(clasa e reală, dar instanța nu s-a produs aici: în depozit n-a existat nicio campanie de actualizare a cotei — verificat, niciun commit n-a atins mai mult de șase module)* |
| **măsurătoarea mea din 23.08** | să numeri argumentele **numite** (ușor de citit din AST) | **legarea reală a parametrului**, inclusiv pozițional | am ridicat R26 la **prag 1** pe o cifră de 23 de căi vii; cea reală e **zero** |
| **verificarea reparației R26**, o oră mai târziu | să rulezi `core/`, unde stau majoritatea testelor | **suita întreagă** — testele din rădăcină nu sunt în `core/` | am declarat suita verde; poarta a găsit **35 de roșii** în `test_*.py` din rădăcină |

**A patra e cea care contează cel mai mult**, fiindcă e a mea și fiindcă a produs o **decizie**: am
escaladat un prag pe o măsurătoare care întreba ce era ușor de întrebat. „Are apelul un `keyword` cu
numele ăsta?" e o întrebare despre **sintaxă**; „ajunge valoarea la parametru?" e întrebarea despre
**lume**. Prima se scrie în trei rânduri de AST, a doua cere să potrivești pozițiile.

**Cum se aplică, mecanic:**

1. **Numește lucrul căutat, apoi locul lui.** *„Ajunge defaultul să lucreze?"* trăiește în **legarea
   argumentelor**, nu în lista de `keywords`. *„E grea restanța?"* trăiește în **încercare**, nu în
   vechime.
2. **Dacă răspunsul e ușor de obținut, bănuiește-l.** Nu e o regulă de suspiciune generală: e
   observația că metoda comodă și metoda corectă coincid rar.
3. **La o schimbare de valoare fiscală, lista de locuri se face din COD, nu din teste.** Un loc fără
   test nu e un loc care nu există — iar reciproc: **un test poate ENCODA defaultul**. Măsurat la
   scoaterea celor 25 de literale: **11 teste picau pe default**, adică îl testau.
4. **Când corectezi o măsurătoare, corectează și ce s-a decis pe ea.** O cifră greșită care a mișcat
   un prag nu se corectează singură — pragul se mișcă înapoi, scris.

**Ce NU acoperă:** nu spune cum se găsește locul potrivit — asta rămâne judecată, și e chiar §12
(confruntarea cu registrul) plus §11 (ce produce, nu cum se numește). Spune doar că **ușurința
măsurătorii nu e o dovadă că e cea potrivită**.

## §17 — O CLASĂ GOLITĂ SE GOLEȘTE PE TOATE LIMBAJELE ÎN CARE POATE EXISTA

**Instanța, 24.08.2026.** R26 a scos **25** de valori implicite de cotă TVA din Python, măsurate prin
AST pe `core/` + `main.py`, și a încheiat cu *«zero căi vii ajung la vreun default»*. Adevărat —
**despre Python**. Aceeași valoare implicită trăia în `firme.js`, scrisă de **trei** ori, iar aceea era
cea care rula: ecranul completează `cota_tva: l.cota_tva || 21` **înainte** ca serverul s-o vadă, deci
refuzul pe care serverul tocmai îl învățase nu se putea declanșa niciodată din ecranul acela.

**Regula.** Când se declară golită o clasă de defect, se numesc **limbajele și straturile** în care
clasa poate exista, nu doar cel în care s-a măsurat. Dacă măsurătoarea a acoperit unul singur,
concluzia se scrie cu domeniul în ea — *«zero în Python»*, nu *«zero»*.

**Și consecința pe gărzi.** Un gard cu domeniul pe un singur limbaj — `DEFAULT_FISCAL_TACIT` citește
Python — **raportează verde despre limbajul pe care nu-l vede**. E aceeași formă cu *gardul care nu se
verifică pe sine*: nu minte despre ce măsoară, minte prin **tăcerea** despre ce nu măsoară. Un gard nou
își declară domeniul **în text**, iar dacă domeniul e mai îngust decât clasa, o restanță ține diferența.

**Ce nu spune regula:** că orice gard trebuie să citească toate limbajele. Costul e real. Spune doar că
**diferența dintre clasă și domeniu se scrie**, ca să nu fie citită drept zero.

## §20 — O VERIFICARE CARE NU POATE FI LEGATĂ POATE FI SIMPTOMUL UNEI ABSENȚE

**Formă nouă, dată de Costin 24.08.2026, alături de §19.** Un modul nelegat nu e automat o omisiune.
Poate fi un **producător fără livrare**: codul există, artefactul pe care îl servește **nu se produce
încă**. Atunci „leagă-l" nu are unde.

**Testul care le deosebește, și e mecanic:** *există o suprafață de livrare pentru artefactul lui?* Dacă
da — ecran, rută, export — modulul e nelegat **din omisiune**, și se leagă. Dacă nu, e nelegat **prin
construcție**, iar condiția lui de deblocare nu e un apel, ci **apariția artefactului**.

**Instanța măsurată: `core/fisa_cont.py`.** Produce *Fișa de cont pentru operațiuni diverse* (cod
14-6-22), care înlocuiește **Cartea mare** (14-1-3) — un registru obligatoriu care lipsea complet.
Zero consumatori: **nicio rută, niciun ecran**. Iar `ISTORIC.md` 23.08.2026 (3) o spunea deja, cu o zi
înainte de măsurătoare: *„nu există încă ecran sau rută. Artefactul are producător, nu livrare."*
**Deci nu e o omisiune — e lista 5 din verdictul fazei 1**, iar condiția de deblocare e livrarea.

**Contra-exemplul, din același set de patru:** `salarii_contare.control_coerenta` are artefact (D112 se
produce și se depune) și **suprafață** (control fiscal, închiderea lunii). Ăla e nelegat din omisiune,
e prag 1, și legarea lui scoate 29 de divergențe (**R34**).

**Consecința pentru clichet:** o intrare din registrul modulelor nelegate trebuie să poarte **care din
două** e — altfel „4 module nelegate" amestecă o datorie de livrare cu o verificare care nu rulează.

---

## §23 — O GARDĂ ASERTEAZĂ PE STRUCTURĂ, NU PE TEXT

**Regula, dată de Costin 24.08.2026.** Nu *„cheia apare undeva în răspuns"*, ci *„câmpul are valoarea
asta"*. Un răspuns JSON se **parsează** și se verifică pe câmpuri; un XML, pe elemente; o randare, pe
arbore; codul, pe **AST**. **Unde nu se poate asertă pe structură, se declară de ce, lângă gardă** —
nu se strecoară un `in` pe șir ca și cum ar fi echivalent.

**De ce.** Un `"cheie" in text` nu păzește lucrul, păzește **proza de lângă lucru**. Nu poate deosebi
*„e implementat"* de *„e descris"*. Iar cea mai rea formă e cea auto-referențială: gardul citește
**documentația lucrului pe care îl păzește**, deci trece verde exact pentru că altcineva a scris
despre lucru — sau pentru că l-a scris el însuși.

### Instanțele — trei într-o singură zi, toate ale mele

Toate din reparația Registrului-jurnal (24.08), toate prinse de RED-proof, niciuna de poartă:

| # | forma | ce s-a întâmplat |
|---|---|---|
| 1 | `'"nr_curent":' in ruta` | șirul era în **docstringul rutei, scris de mine** — gardul trecea verde fără ca ruta să producă cheia |
| 2 | curățarea de docstring cu `re.sub` lacom | ștergea și **SQL-ul din același f-string**, iar gardul acuza fals că numerotarea dispăruse |
| 3 | `'note_fara_document' in ruta` | aceeași ca 1, pe altă coloană — **auto-referențială** |

A doua e cea instructivă: încercarea de a repara o gardă textuală **tot cu text** a produs un
instrument care greșea în **ambele direcții** — deci fără plafon, nici superior, nici inferior (§22).
Ieșirea nu era o curățare mai bună, ci **schimbarea sursei de adevăr**: `ast.parse` + cheile din
nodurile `Dict`. Un docstring nu e un `ast.Dict`, iar un comentariu nu ajunge deloc în AST — deci
distincția *construit* vs *descris* devine imposibil de ratat, nu doar improbabil.

### Două clase, nu două cifre pentru același lucru

Interdicția **18** spunea **13**. Măsurătoarea de azi spune **369**. Nu se contrazic — **măsoară
lucruri diferite**, iar confuzia dintre ele e chiar felul în care o clasă rămâne nemăsurată ani.

| | ce număra | cifra | domeniu |
|---|---|---|---|
| **îngustă** | gărzi care își iau dovada din **documentația codului** | **13** | ad-hoc, faza 4, 22.08, 369 de fișiere |
| **largă** | **orice aserțiune care poate trece dintr-un motiv străin** | **369** | declarat, reproductibil, 24.08, 397 de fișiere |

Cea îngustă e o **specie**; cea largă e **genul**. Un docstring nu e singurul motiv străin din care
poate trece o aserțiune — mai sunt HTML-ul de lângă randare, și reprezentarea unei structuri. **Clasa
largă n-a fost măsurată până azi**, iar cifra îngustă, folosită singură, dădea impresia că problema e
mică și aproape închisă.

Cifra îngustă are și un defect propriu: **nu se poate recalcula**. N-a lăsat niciun instrument în
urmă, iar între timp fișierele-gardă au crescut de la 369 la 397. *O cifră care nu se poate recalcula
nu e o măsurătoare, e o amintire.*

### Cele trei sub-categorii se numără separat

Fiindcă nu sunt același defect și nu se repară la fel:

1. **sursa** (113) — se caută un șir în **codul păzit**. Nu deosebește *„e implementat"* de
   *„e descris"*. Reparația: `ast.parse` + noduri.
2. **randare** (6) — se caută în **HTML**. Un `<div>` dintr-un comentariu trece la fel de bine ca
   unul randat. Reparația: arbore de randare.
3. **reprezentare** (250) — `"x" in str(d)`, `in json.dumps(d)`, `in resp.text`. **Cea mai
   insidioasă**: *arată ca apartenență la o cheie și e sub-șir pe reprezentare.* `"total" in str(d)`
   trece și când `d = {"subtotal_vechi": 1}`. E și **cea mai mare dintre cele trei** — dacă ar fi
   topită în total, n-ar exista nicio pârghie s-o ataci pe ea. Reparația: câmp și valoare.

Și o a patra formă, care **nu** e în clasă dar merită numită: **`in` pe un container**. Acolo `in`
*chiar e* apartenență — dar e sigur doar cât timp dreapta rămâne container. `"nr_curent" in chei` se
transformă tăcut în sub-șir dacă `chei` devine vreodată un `str`, **și arată identic**. Forma care nu
poate degrada e operatorul de mulțime: **`chei >= {"nr_curent"}` crapă pe un șir**, în loc să treacă.

**369 e PLAFON INFERIOR.** Din 1339 de forme găsite, **899 (67%) rămân `nedeterminat`** — nu s-a
putut rezolva ce stă în dreapta. Nu se raportează ca trecute: absența unei verificări nu e o
verificare. Cifra se scrie cu semnul ei (§22).

### Clasele nu sunt disjuncte

O aserțiune pe text e permisivă în **două direcții simultan**: trece **pe proză** și trece **pe listă
goală**. Nu sunt două defecte care coexistă întâmplător — e aceeași slăbiciune văzută din două părți:
*aserțiunea nu-și verifică propria premisă.* Nu întreabă nici **unde** a găsit potrivirea, nici
**dacă a avut ce compara**.

**Măsurat 24.08.2026: 221 din 1339** de aserțiuni (**17%**) trăiesc într-un context care dispare pe
iterabil gol — `all(… for x in L)` sau corpul unui `for x in L:`.

**Unde stau contează mai mult decât cifra.** Doar **18** sunt în clasa clasificată (369); **202 sunt
în `nedeterminat`**. Rata e **5% în clasă** față de **22% în nedeterminat**. Deci cele 899 de
aserțiuni nerezolvate nu sunt un rest neutru pe care îl declari și mergi mai departe — sunt **locul
unde se adună cele mai slabe**, iar „nu știu ce e în dreapta" e corelat cu „nu compară nimic".

**Cele două goluri sunt același gol.** Într-un `all("x" in l for l in lista)`, dreapta lui `in` e
variabila de buclă, pe care clasificatorul o dă `nedeterminat` — deci tocmai formele vacue ieșeau din
clasă *înainte* de a putea fi numărate. Prima măsurătoare a raportat **18** exact din motivul ăsta,
și a fost prinsă de **propria calibrare pozitivă**: cerea ca un `all(...)` peste o listă filtrată să
fie recunoscut, și nu era. Un instrument construit ca să numere o slăbiciune a picat în ea.
*Calibrarea a valorat cât măsurătoarea.*

Rămâne **plafon inferior**: o listă golită de un `parametrize`, de un filtru care nu potrivește nimic
sau de o fixtură care întoarce `[]` nu se vede structural.

**Regula care rezultă, pentru orice măsurătoare viitoare pe interdicțiile 18, 19 și §23:** *nu
presupune disjuncția.* Adunarea cifrelor supraestimează; tratarea lor ca alternative exclusive ascunde
exact instanțele cele mai slabe — cele care cad în **amândouă**, și care trec din două motive
independente, deci rezistă la două reparații diferite.

### Proprietatea, nu procentul

**O aserțiune pe text trece pe date goale — cu o singură excepție: cele care caută un mesaj de
eroare, adică ceva ce apare doar când ceva merge prost. Restul caută ceva ce apare oricum.**

Nu e o observație despre un eșantion, e o proprietate a **formei**. `"X" in ceva` întreabă *există X
undeva*, nu *s-a întâmplat ce trebuia*. Când X e prezent și în starea „nu s-a întâmplat nimic" — un
nume de funcție, o clasă CSS, o cheie, un fragment de cod — aserțiunea **nu discriminează** între
cele două lumi pe care testul ar trebui să le separe. Un mesaj de eroare e altceva: **nu poate fi
produs de starea normală**, deci găsirea lui chiar spune ceva.

De aici iese și legătura cu §22 și cu suprapunerea 18/19: aserțiunea pe text nu-și verifică nici
**premisa** (a avut ce compara?), nici **locul** potrivirii (unde a găsit-o?), nici **discriminarea**
(ar fi trecut și fără ca lucrul testat să se întâmple?). Trei întrebări, același gol.

**Măsurat, cu direcția erorii scrisă** (`core/scan_garzi_pe_text.fel_ancorei`): **1222**
aserțiuni — clichetul viu — ancorează pe ceva ce apare oricum; restul, sub o zecime, pe un semn
de rău. Clasificatorul **supraevaluează deliberat** semnul de rău — prinde și SQL, de pildă
`'NOT NULL fara default'` — deci **partea de semn-de-rău e plafon SUPERIOR** și **1222 plafon
INFERIOR**. Excepția e mai mică decât pare, nu mai mare. *Celelalte două cifre nu se mai scriu
aici: totalul și semnul-de-rău n-au clichet și au îmbătrânit deja o dată, tăcut (1341/119 →
1342/120, măsurat 31.08). Se recalculează: `core/scan_garzi_pe_text.pe_fel()`.*

### Ce cere, practic

1. **Sursa de adevăr a unei gărzi e structura**: `json.loads` + câmp și valoare · parsare XML +
   element · arbore de randare · `ast.parse` + noduri. Nu textul din care s-a construit.
2. **Compromisul textual se îngustează și se declară.** Dacă o aserțiune chiar trebuie să cadă pe
   text (SQL, de pildă, e șir chiar și în AST), atunci **AST-ul localizează** constanta și abia
   înăuntrul ei se caută — iar motivul se scrie lângă gardă.
3. **Clichet, nu campanie.** Cele 50 nu se repară azi, dar numărul lor **nu poate crește**:
   `core/test_garzi_pe_text.py` cu calibrare în ambele direcții. O gardă nouă pe șir e o **regresie**,
   nu un compromis.

Legat de [[§22]] (ambele direcții de eșec) și de interdicția **18**, căreia îi dă instrumentul viu.

---

## §22 — UN INSTRUMENT CARE GREȘEȘTE ÎN AMBELE DIRECȚII N-ARE NICI PLAFON SUPERIOR, NICI INFERIOR

**Regula, dată de Costin 24.08.2026.** Interdicția **76** cere calibrare pe propriul mod de eșec.
Regula asta spune ce se întâmplă când modurile de eșec sunt **două, opuse**: *un instrument care poate
și să rateze ce există, și să revendice ce nu există, **nu produce nici măcar o margine**. Cifra lui
nu se poate folosi până nu e calibrat pe amândouă direcțiile.*

**De ce contează.** Un instrument care doar **ratează** dă un **plafon inferior** — „cel puțin atâtea".
Unul care doar **inventează** dă un **plafon superior** — „cel mult atâtea". Amândouă sunt folosibile
la triaj, cu semnul scris. **Unul care face amândouă nu dă nimic**: cifra lui poate fi și prea mare,
și prea mică, în același timp, iar cele două erori nu se anulează — se ascund una pe alta.

### Instanța, măsurată pe 24.08.2026

Același instrument — „ce acte citate de ghiduri lipsesc din corpus" — în trei forme, în aceeași zi:

| formă | cum potrivea | ce a raportat |
|---|---|---|
| **v1** | numele fișierului | **40 de acte lipsă** |
| **v2** | tip+număr+an oriunde în conținut, toleranță 60 de caractere | **20 „recuperate" — toate FALSE** |
| **v3** | titlul propriu al actului, în antet | **0 recuperări peste v1** |

**v2 „a găsit" HG 479/2003 în Codul de procedură fiscală**, care doar o **menționează**. Și Legea
1/2020 în Legea 141/2025. Și OG 6/2026 în Codul fiscal. *O mențiune nu e posesie* — aceeași distincție
ca proza-care-numește-un-modul față de apelul lui (§19), dar pe direcția opusă: **nu ratează ce e
prezent, ci revendică ce n-are.**

**Dacă aș fi raportat cifra lui v2 fără calibrare, 20 de acte ar fi fost declarate „în corpus" și
nimeni nu le-ar mai fi adus.** Costul unui fals „prezent" e mai mare decât al unui fals „lipsă": al
doilea trimite pe cineva să caute degeaba; primul închide căutarea definitiv.

### Ce cere, practic

1. **Numește amândouă direcțiile de eșec înainte de prima măsurătoare**, nu doar una. Antetul lui
   `scan_module_nelegate` are cinci moduri de eșec, dar toate pe direcția „nu vede" — niciunul pe
   „revendică greșit". Aia a fost o listă pe jumătate.
2. **Calibrează pe câte un caz din fiecare direcție**, construit: un membru pe care instrumentul
   **trebuie** să-l găsească, și unul pe care **nu trebuie**.
3. **Până atunci, cifra se scrie cu semnul ei** — „plafon inferior" sau „plafon superior" — sau nu se
   scrie deloc. „40 de acte lipsă" fără să spui în ce direcție greșește instrumentul nu e o măsurătoare.

Legat de [[§21]] (a declara corect fără a confrunta) și de interdicția **19** (verde pe zero rânduri):
toate trei sunt forme ale aceleiași întrebări — *ce anume nu poate vedea instrumentul, și în ce parte
te împinge asta*.

---

## §21 — A DECLARA CEVA CORECT FĂRĂ SĂ-L FI CONFRUNTAT E CALIBRARE DOAR POZITIVĂ

**Regula, dată de Costin 24.08.2026.** Interdicția **76** cere ca un instrument să fie calibrat pe
**propriul mod de eșec**, nu doar pe cazul fericit. Regula asta o mută pe o suprafață nouă: nu
instrumentul, ci **măsurătoarea**. *O măsurătoare care declară ceva corect fiindcă «pare corect», fără
să-l fi confruntat cu sursa, e o măsurătoare cu calibrare doar pozitivă* — și se citește la fel ca una
făcută.

**Testul, și e mecanic:** pentru fiecare lucru declarat corect, se poate numi **cu ce a fost
confruntat**? Dacă răspunsul e „cu nimic, dar arăta bine", declarația nu e rezultat, e impresie.

**Instanța, măsurată — și e a unui gard propriu.** `core/test_valori_fiscale_js.py` a fost construit ca
să confrunte cotele scrise în ecrane cu registrul, și **făcea exact asta, corect**, pe cele 6 situri
din tabelul lui. Ce nu spunea nimeni cu voce tare e că tabelul e **scris de om**: gardul verde însemna
*„cele 6 pe care le știu coincid"*, dar se citea ca *„cotele din ecrane coincid"*. La măsurătoarea din
24.08 au ieșit **10** situri reale — **4 nu fuseseră niciodată confruntate**, printre ele fratele de pe
linia următoare a unui rând care era deja în tabel. Valorile lor s-au dovedit corecte; **dar asta s-a
aflat abia la confruntare, nu înainte.** Diferența dintre „e corect" și „am verificat că e corect" e
fix diferența dintre noroc și măsurătoare.

**De ce nu se prinde singură:** un tabel scris de om nu-și declară golurile. Gardul care stă pe el
raportează despre **domeniul lui**, nu despre lume — iar cine îl citește presupune lumea. Aceeași formă
cu §17 (o clasă golită pe un singur limbaj) și cu interdicția 19 (verde pe zero rânduri), pe încă o
față: **verde pe un domeniu mai mic decât cel presupus.**

**Ce cere, practic:** orice cifră care spune „N corecte" poartă și **numitorul**, și **cum a fost
stabilit**. „8 din 8 conturi din ecrane sunt în planul tuturor celor 17 firme" e o măsurătoare. „Cele 4
par corecte" nu e.

---

## §19 — UN MODUL DE VERIFICARE NELEGAT E O GARDĂ CARE NU PĂZEȘTE

**Regula, cerută de Costin 24.08.2026.** Un modul care verifică ceva și pe care **nu-l cheamă nimeni**
nu e cod mort inofensiv: e o **verificare pe care toată lumea o crede făcută**. Iar de la ce se vede,
arată identic cu unul viu.

**De ce nu se aprinde nimic.** Un modul mort care **pică** ar fi fost găsit demult. Unul mort care
**trece** e invizibil, fiindcă **testele lui îl țin verde** — verdele lor e chiar alibiul. Aceeași
formă cu „regula scrisă și nepăzită se citește ca respectată" (§14), mutată un nivel mai jos: aici
regula e păzită, dar paznicul nu e chemat.

**Cum se măsoară: prin AST, nu prin grep — și diferența ESTE rezultatul.** Un `grep <nume_modul>` dă
zeci de potriviri, majoritatea **comentarii**. Proza care numește un modul nu-l apelează. Instrument:
`core/scan_module_nelegate.py`, cu cele cinci moduri de eșec scrise în antet înaintea primei
măsurători (interdicția 76). Gard: `core/test_module_nelegate.py`, clichet pe **NUME**, nu pe număr.

### Cele trei instanțe măsurate

1. **`core/echilibru_perioada.py`** — verificare de echilibru + orfani, **zero importatori de
   producție**, ȘI există o funcție legată cu nume apropiat: `main.py:4634` calculează „echilibru" prin
   `verificatoare.verifica_balanta` (balanța se construiește la `main.py:4597`).
   **CORECTAT 25.08.2026 — „logica paralelă" era o afirmație despre NUME, nu despre comportament, și
   e falsificată.** Rulate amândouă pe aceleași date, **modurile de eșec sunt disjuncte**:
   `echilibru_perioada` prinde linia cu o parte lipsă și orfanii, pe care cealaltă îi ratează tăcut;
   `verifica_balanta` prinde soldurile inițiale dezechilibrate, pe care prima nu le citește deloc.
   Deci nu sunt două implementări ale aceleiași verificări, iar a alege una **șterge** o verificare.
   Cifrele, calibrarea și ce nu vede măsurătoarea: `CONFORMITATE.md`, R33.
   **Lecția care rămâne pentru METODA, și e mai mare decât instanța: două funcții care poartă același
   cuvânt — „echilibru", „balanță" — nu se declară duplicate până nu li se dă ACELAȘI caz și nu se
   compară VERDICTELE.** Afirmația veche a supraviețuit patru registre și 37 de commituri fiindcă
   nimeni nu le rulase pe amândouă; o măsurătoare de zece minute a răsturnat-o. E aceeași clasă cu
   **R16** (proza care descrie codul poate fi falsă de la naștere), aplicată la proza pe care am
   scris-o eu.
2. **`core/salarii_contare.py`** — `control_coerenta`, verificare încrucișată **notă contabilă vs
   declarație**, zero importatori. `core/salarizare.py:296` **o numește** — *„incrucisat
   nota-vs-declaratie"* — dar într-un **COMENTARIU**. Un scan pe text ar fi raportat modulul ca legat.
3. **`rip_api.fisa_d212` ↔ `d212_engine.PLAFOANE_VENIT_2026`** — instanța cea mai ascuțită, și e la
   nivel de **FUNCȚIE**, nu de modul: modulul era legat, dar plafoanele 2026 — **verificate la sursă pe
   03.08.2026**, Legea 239/2025 art. XII pct. 19, CASS 72 sm în loc de 60 — nu erau chemate de nimeni,
   fiindcă `fisa_d212` refuza orice an ≠ 2025 și folosea constanta anului trecut. Efect pe o instalare
   din august 2026: **butonul «Fișa D212» nu putea produce decât fișa anului trecut, pentru orice PFA.**
   Reparată 24.08.2026 (prag 1).

### Ce spune contra-instanța, și de ce se scrie aici

**`control_incrucisat` a fost PRESUPUS nelegat** în aceeași zi. Măsurat: **6 importatori de producție**
și data nașterii **15.07.2026**. Verificarea încrucișată rulează în producție din iulie. *O presupunere
despre o legătură lipsă nu e o măsurătoare* — de aceea modulul stă acum în **calibrarea negativă** a
gardului: dacă sonda ar începe să-l raporteze, ea e ruptă, nu codul.

### Limita, declarată

Măsurătoarea e la nivel de **MODUL**. Instanța 3 — cea cu efect real la un om — e la nivel de
**FUNCȚIE**, și a fost găsită **de mână**, nu de sondă. Un modul importat pentru o funcție, cu alte
trei moarte, trece neatins. **Clasa nu e închisă**, iar cifra „4 module" e un plafon inferior.

---

## §18 — LA O SCHIMBARE DE VALOARE FISCALĂ, JS-UL SE CAUTĂ EXPLICIT

**Observația lui Costin, 24.08.2026:** *«JS-ul nu e atins de campaniile fiscale fiindcă nu e căutat
acolo. Nu decurge din nimic.»* Are trei instanțe măsurate în două zile, toate în JS, toate defecte
**din prima zi**, nu regresii: cota implicită din ecranul de NIR (R29), anul înghețat în cererea D212
(R31), și cotele scrise ca etichetă lângă valori venite de la server.

**Cauza, numită exact:** campaniile fiscale au pornit de fiecare dată dintr-un instrument care citește
**Python** — AST pe `core/`, scanul de constante, verificatorul. Niciunul nu deschide un `.js`. Nu
pentru că cineva a decis așa, ci pentru că **domeniul n-a fost niciodată pus în discuție** (`§17`).

**Regula ar fi fost: „la fiecare schimbare de valoare fiscală, se caută explicit și în JS".** N-a
rămas regulă, fiindcă o regulă care depinde de memorie se rupe exact când e nevoie de ea. A devenit
**gard**: `core/test_valori_fiscale_js.py` confruntă fiecare cotă scrisă literal într-un ecran cu
`COTE`, la data de azi. Când o cotă se schimbă în registru, testul devine **roșu și numește fișierul
de ecran** rămas în urmă. Căutarea nu se mai ține minte — se întâmplă singură.

**Ce rămâne de ținut minte, fiindcă gardul nu poate:** tabelul lui e **scris de om**, alimentat din
`core/scan_valori_afisate.py`. O valoare fiscală nouă apărută într-un ecran nu intră singură. De-aia
scanul rămâne, lângă gard: unul măsoară, celălalt păzește.

---

## §24 — O PROBĂ CARE CONFIRMĂ IPOTEZA FIINDCĂ JUMĂTATE DIN REPARAȚIE NU RULEAZĂ

**Cerută de Costin, 25.08.2026, ca formă proprie.** Nu e „verde pe zero" (interdicția 19) și
nu e „gardă care își ia dovada din proză" (interdicția 18). E a treia:

> **Proba rulează pe un sistem în care doar o parte din reparație e activă. Partea inactivă
> produce exact starea pe care proba o aștepta. Verdele nu vine din reparație — vine din
> absența ei.**

**Ce o face periculoasă e chiar potrivirea.** Un rezultat care contrazice așteptarea se
investighează. Unul care o confirmă, nu. Aici confirmarea e produsă de defect, deci semnalul
care ar fi cerut o a doua privire lipsește prin construcție.

### Instanța, cu mecanismul ei

R41 partea a II-a: ecranul cozii nu mai trebuia să numească „De depus" o listă în care intră
și ce nu e gata. Reparația avea două jumătăți — **serverul** (`lista_coada` întoarce
`gata_de_depus`) și **ecranul** (două liste, după acel câmp).

Proba a dat **16/16**. Dar:

- **JS-ul se servește de pe disc** → era cel nou;
- **`core/coada_api.py` rulează în serviciu**, care nu se repornise → era cel vechi;
- deci `gata_de_depus` **lipsea din răspuns**, `c.gata_de_depus` era `undefined`, **tot** ce
  era în coadă cădea în „nevalidat";
- iar așteptarea de atunci era exact *„De depus (0)"*, fiindcă niciuna nu era validată.

**Proba a confirmat ipoteza pentru că serverul o contrazicea.** Rulată după repornire, pe o
coadă cu stare **mixtă** (una gata, una nu), a dat 12/12 — și abia atunci a dovedit ceva:
listele chiar se separă, butoanele chiar diferă pe rând.

### Unde apare, generalizat

Oriunde **o parte a sistemului se încarcă altfel decât alta**:

| ce se încarcă la fiecare cerere | ce se încarcă o dată, la pornire |
|---|---|
| fișiere statice (JS, CSS, șabloane) | codul Python al serviciului |
| conținutul unui fișier de date citit la rulare | modulele importate |
| rândurile din bază | schema, migrările aplicate |
| variabile de mediu citite la apel (`cfg`) | cele citite la import |

**Riscul e maxim când reparația trece granița** — jumătate într-un strat care se reîncarcă,
jumătate în unul care nu.

### Ce se face

1. **Proba comportamentală se rulează DUPĂ ce partea care nu se reîncarcă a fost repornită.**
   La noi: după commit, fiindcă `post-commit` repornește serviciul. Înainte de asta, proba
   spune despre un sistem hibrid care nu va exista niciodată în producție.
2. **Se verifică four-way că procesul viu are codul probei** — ora de pornire ulterioară
   commitului. Verificarea aia exista deja pentru publicare; se aplică și probelor.
3. **Așteptarea nu se fixează pe o cifră care coincide cu starea de defect.** Dacă „0" e și
   rezultatul corect, și rezultatul defectului, aserțiunea nu discriminează. La R41 s-a
   reparat derivând așteptarea din starea reală a cozii, nu fixând-o.
4. **Proba se rulează pe o stare MIXTĂ**, nu pe una uniformă. O coadă în care totul e
   nevalidat nu poate arăta că cele două liste se separă — arată doar că una e goală.

### Ce nu rezolvă

Nu ajută la o reparație care e **întreagă** într-un singur strat și greșită. Aia se prinde cu
mutație (§22), nu cu repornire. §24 e despre **granița dintre straturi**, nu despre corectitudine.

---

## §25 — CÂND DOUĂ REGULI SCRISE SE CONTRAZIC, CÂȘTIGĂ CEA PĂZITĂ — ȘI O FACE TĂCUT

**Regula.** O regulă scrisă și nepăzită nu e doar „mai slabă" decât una păzită (§14). În prezența
unei reguli păzite **care spune contrariul**, ea e *inoperantă* — iar contradicția nu se semnalează
nicăieri, fiindcă amândouă sunt verzi: una fiindcă nimic n-o verifică, cealaltă fiindcă exact ea e
verificată. Deci: **înainte de a scrie o regulă, se caută regula pe care o contrazice.** Și înainte
de a cere o decizie, se caută răspunsul în ce e deja scris.

**Instanța 1 — nomenclatoarele (25.08.2026).** METODA §13, scrisă pe 23.08: *„un nomenclator se
completează din NORMĂ"*, ancorat pe textul actului. `core/test_nomenclatoare_ancorate.py`, scris pe
04.08: *„fiecare nomenclator e ancorat pe VALIDATORUL INSTALAT, **nu pe un document**"* — cu asertare
care **pică** dacă ancora nu atinge validatorul. Aceeași chestiune, două reguli scrise, în sens opus.
A câștigat cea din 04.08, fără ca cineva să aleagă: era singura cu gardă de clasă. §13 avea gardă doar
pentru D406, deci a rămas adevărată pe un singur fișier și inertă pe restul.

Consecința nu e teoretică: `d301.VALUTE` are douăzeci de valute fiindcă atâtea acceptă DUKIntegrator,
în timp ce OPANAF 592/2016 **nu închide lista** — spune *„de exemplu: USD, euro…"*. O operațiune
făcută legal într-o altă valută nu se poate depune, iar până azi asta nu era scris nicăieri ca
dezacord: era scris ca *ancorare corectă*.

**Instanța 2 — restanța care nu citește planul (25.08.2026, Costin).** *„Dacă o ceri de cinci ture
deși răspunsul e în plan, problema nu e condiția restanței — e că restanța nu citește planul."*
Aceeași formă: răspunsul exista scris (PLAN_ARHITECTURA, Partea 0, Pasul 4 — ierarhia surselor, cu
validatorul declarat explicit *constrângere, nu normă*), iar restanța a cerut decizia de cinci ori.
Nu lipsea decizia. Lipsea citirea.

**Cum se aplică, mecanic:**

- O restanță **DESCHISĂ** deblocată de **DECIZIE** poartă un câmp `- **planul**:` cu una din două:
  locul din plan care răspunde (și atunci restanța se închide, nu se cere), sau **NEACOPERIT** cu ce
  anume s-a citit. Gardat de `test_restanta_care_cere_decizie_a_citit_planul` (clichet, coboară).
- O regulă nouă în METODA/CLAUDE.md se caută întâi în celelalte: dacă există una care o contrazice,
  **contradicția se rezolvă în aceeași tură**, nu se lasă amândouă scrise.
- Perechea de gărzi rămâne perechea: sursa (normă) și constrângerea (validator) se probează *separat*,
  iar diferența dintre ele se consemnează. Un singur gard, oricare, reașază tăcut ierarhia.

**Ce NU acoperă regula.** Nu detectează contradicția automat — nu există instrument care să compare
sensul a două paragrafe de proză. Acoperă doar cazul în care una dintre reguli are gardă: atunci gardă
contra text e o confruntare pe care o poate face un om în cinci minute, dacă știe s-o caute. Iar asta
e tot ce cere §25: **să se caute.**

### Motivul dintr-un clichet se VERIFICĂ, nu se presupune (26.08.2026)

Un clichet cere ca fiecare intrare tolerată să poarte **de ce**. Regula tace despre partea grea:
motivul e o afirmație despre cod, deci poate fi **falsă**, exact ca orice altă proză (R16).

Instanța, din aceeași zi: eram gata să scriu, pentru jumătate din intrările clichetului R54,
motivul *„modul pur, fără conn/schema în domeniu"*. Sunase plauzibil fiindcă **una** dintre ele
chiar era așa. Citite la sursă, șapte nu erau: `conn` și `schema` erau în domeniu, expresia era
în `try` care prinde `ValueError`, iar singurul lucru care le ținea nelegate era **forma
patch-ului meu**. S-au legat toate șapte.

**Un motiv de clichet scris din analogie transformă „n-am făcut" în „nu se poate" — și atunci
clichetul nu mai e o datorie, e o justificare.** Testul, ieftin: pentru fiecare intrare, deschide
funcția și verifică exact propoziția pe care vrei s-o scrii.

### Ghilimelele românești rup șirul Python (26.08.2026, a patra oară în aceeași zi)

Un ghilimel de închidere ASCII pus după unul de deschidere românesc încheie **șirul Python**, nu
citatul: `„ceva"` într-un literal cu ghilimele duble e o eroare de sintaxă la linia următoare.
S-a întâmplat de patru ori într-o singură tură, iar mesajul pe care îl dă interpretorul arată
spre caracterul greșit — de obicei o linie-două mai jos.

**Și „reparația" automată e mai periculoasă decât greșeala:** un înlocuitor care transformă orice
`"` de după `„` în ghilimel de închidere nu știe unde se termină literalul Python, deci strică
și șirurile corecte. Instanța: a stricat trei literale valide într-un fișier pe care încerca să-l
repare. **Se scrie corect de la început** — perechea tipografică, în tot textul românesc — sau
textul stă într-un fișier separat, nu într-un literal.

## §26 — O CIFRĂ DESPRE „FIRME REALE" DECLARĂ POPULAȚIA PE CARE S-A CALCULAT, SAU NU SE SCRIE

**Regula.** O măsurătoare care spune ceva despre *firmele reale*, *utilizatorii reali* sau *datele de
producție* scrie, lângă cifră, **pe cine s-a calculat** — și cum se poate reface acea mulțime. Fără
asta, cifra e adevărată despre o populație pe care nimeni n-o poate numi, iar cine o recitește peste
o săptămână o va citi despre alta.

**Instanța, 27–28.08.2026.** Clichetul `_DIVERGENTE_CUNOSCUTE = 4` din `core/test_nume_firma_unic.py`
măsura *„firme la care denumirea din portofoliu diferă de cea fiscală"*. Interogarea lui era
`SELECT id, nume, schema_name FROM public.tenants` — **fără niciun filtru**. Măsurat pe populația
declarată: **toate cele patru divergențe sunt la cabinetul de test 4163**, creat deliberat pe
09.08.2026 (`DECIZII.md`) ca mediu izolat, cu firme adăugate manual și profil fiscal scris de un
semănător din afara repo-ului. **Pe cele 14 firme reale: 0.** Deci clichetul nu măsura aplicația, ci
**semănătorul** — și l-ar fi ținut pe 4 la infinit, cu aerul unei datorii tehnice.

**De ce nu e o greșeală de interogare.** Instrumentul era corect; ce lipsea era **declarația**. Baza
nu avea — și, prin decizia lui Costin din 28.08, nu primește — nicio coloană care să spună „cabinet de
test"; populația se declară **lângă clichet**, ca listă explicită de cabinete excluse, cu motivul și
cu decizia care le-a creat. Iar excluderea își cere propriul anti-vacuu: garda verifică faptul că
cabinetul exclus **încă poartă numele sub care a fost exclus**, altfel un `id` reciclat ar scoate
tăcut din măsurătoare un cabinet real.

**Ce cere, practic:**

1. **numește mulțimea** — „14 firme, cabinetul 1968" e o populație; „firmele din bază" nu e;
2. **numește ce ai scos și de ce**, cu trimitere la decizia care a creat excepția;
3. **verifică excluderea**, nu doar aplic-o: un identificator se poate recicla;
4. **anti-vacuu pe rest** — dacă populația declarată se golește, cifra devine 0 și arată ca o
   reparație. Se asertează că mai are membri.

**Corolarul, și e mai larg decât R81:** orice măsurătoare viitoare *„pe firme reale"* lovește aceeași
lipsă. Cifra care nu-și declară populația nu se corectează — **nu se scrie.**
