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

Patru pași, în ordinea asta:

1. **Nu produce lista întâi.** Un scan pe cod găsește mii. Taxonomia descoperită după 4.000 de rânduri e
   descoperită prea târziu.
2. **Calibrare în MAI MULTE DIRECȚII, nu una.** O singură țintă lasă instrumentul să treacă pe gol în
   celelalte. La scanul de constante: `25` trebuie să cadă în „nesursat", `4050` în „sursat", `40` (cod
   județ) în „nomenclator" — și **fiecare direcție a picat efectiv o dată** în construcție.
3. **Privește un eșantion de ~30 înainte de orice total.** Acolo apare taxonomia reală.
4. **Zgomotul exclus se NUMĂRĂ, nu se aruncă tăcut** — altfel filtrul devine el însuși o afirmație
   neverificată.

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
| temei prezent, dar în PROZĂ | `cote_tva.py` citează art. 291 în antet și per categorie — scanul cere obiect `Temei`, deci îl raportează nesursat |

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
