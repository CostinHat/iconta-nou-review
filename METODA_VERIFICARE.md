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

**Și consecința care contează cel mai mult:** un patch care „sare" nu eșuează — **raportează succes**.
De aceea greșeala se vede abia la verificarea de după, dacă se face. Verificarea de după nu e opțională.

