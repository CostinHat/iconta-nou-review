


## 14.09.2026 — **planul de întărire P0…P7 se închide formal**

Pentru un contabil: nimic. Nicio linie de cod de producție n-a fost atinsă azi — e o zi de
consemnare, nu de lucru.

**Ce s-a scris.** Cei opt pași P0…P7 sunt marcați `CLOSED_ACCEPTED`, fiecare cu commitul lui final,
într-un tabel la capătul lui `PLAN_HARDENING.md`. Lângă el stau două lucruri care fac diferența
între o închidere și o declarație: **poarta care a lăsat-o să treacă**, copiată din ieșirea
hook-ului (5840 de teste, ruff OK, verificator `TOTAL: 0`, arbore curat), și **cele șase restanțe
care rămân deschise**, fiecare cu cifra ei și cu motivul pentru care nu blochează.

*O închidere care n-ar numi ce rămâne ar fi o cifră flatantă — exact clasa pe care planul o
păzește de opt pași.* Niciuna dintre cele șase n-are lucrare pornită, și niciuna nu contrazice
criteriul pasului ei: `_raspuns` e serializarea mutată la P5 · `D3`=1 e stratul HTTP însuși ·
cele 7 rute GRI sunt clichet, iar GRI nu e verde · cele 6 căi C5 au verdict scris · R178 și R183
sunt proprietăți ale configurației, măsurate, nu regresii.

**Ce rămâne în vigoare:** gărzile. Criteriile celor opt pași nu sunt propoziții dintr-un raport, ci
probe care rulează la fiecare commit.

## 13.09.2026, partea a cincea — **P7 · valul use-case: 385 de corpuri de rută, și faza se ÎNCHIDE**

Pentru un contabil, a cincea oară azi: nu s-a schimbat nimic. Aceleași ecrane, aceleași declarații,
aceleași refuzuri — cuvânt cu cuvânt, și asta nu mai e o promisiune, e o confruntare.

### Ce s-a schimbat, sub capotă

**Cele 385 de corpuri de rută au plecat din `main.py`** în **27 de module `core/uc_*.py`**, împreună
cu **58 de helperi** și **12 nume de modul** pe care le cereau. `main.py`: **11714 → 6546** de linii.
Fiecare rută a rămas la locul ei, cu decoratorul, semnătura și docstringul — FastAPI validează pe
semnătură, deci contractul de intrare e literal același —, iar corpul a devenit o delegare.

Cifra care a ținut faza deschisă două valuri, **`RUTE_CARE_DESCHID_SINGURE_TRANZACTIA`**, a mers
**385 → 73 → 17 → 5 → 0**. Cu ea, **toate cele patru criterii canonice ale lui P7 sunt satisfăcute**,
și faza se închide.

### Ce a făcut posibilă mutarea: un vocabular de refuz

`HTTPException` nu poate trăi în use-case — al doilea criteriu canonic o interzice. Dar decizia care
produce refuzul se ia **înăuntrul tranzacției**, adică exact în codul care pleacă. S-a scris deci
`core/erori.py`: clase care numesc **condiția** (*inexistent*, *fără drept*, *conflict*, *date
invalide*…), iar traducerea condiție → cod HTTP e **o singură hartă**, în stratul HTTP.

**Ce face traducerea sigură e o măsurătoare, nu o speranță:** `HTTPException` **nu e prinsă
nicăieri** — zero `except HTTPException` în tot repo-ul —, deci înlocuirea ei nu poate schimba niciun
flux de control. La fel s-a măsurat că niciun obiect de răspuns nu se construiește înăuntrul unei
tranzacții.

### Ce NU a trecut granița

Obiectele de protocol. Un `Response`/`FileResponse` se construiește tot în înveliș, din valorile pe
care use-case-ul le întoarce (**15 rute**); un `UploadFile` se citește în înveliș și se pasează ca
`bytes` + nume (**12 rute**); gărzile de ritm care se uită la IP-ul cererii rămân deasupra, pe primul
rând (**2 rute**). *Un use-case care vorbește HTTP n-ar fi un use-case.*

Și un al treilea fel de graniță, care n-a fost evident: `_TENANT_TEMPLATE` și `_STATIC_DIR` nu sunt
constante — se **aleg la pornire**, în stratul HTTP. Mutate ca valori, use-case-ul ar fi rămas cu
`None` iar scriitorul cu copia lui: o legătură ruptă pe tăcute, care s-ar fi văzut abia în producție.
S-au mutat invers, și așa e și corect ca strat: **HTTP-ul configurează, use-case-ul consumă.**

### Dovada că nu s-a schimbat contractul

`core/test_p7_uc.py` ia `main.py` **de la commitul dinainte de val** (`git show 43fd2197:main.py`) și
confruntă, **funcție cu funcție**, mulțimile de perechi `(cod HTTP, mesaj)` pe care le ridică —
mesajul comparat ca **arbore**, nu ca text, fiindcă dedentarea schimbă sursa fără să schimbe
valoarea. Trece cu **o singură abatere declarată**, cu motivul scris în fișier: un input-guard
telegrafic (`"suma invalida"`) care a intrat în domeniul regulii G5 odată cu mutarea și și-a primit
constrângerea în mesaj.

*Fișierul acela era citat de două ori în cod înainte să existe — `core/erori.py` și `main.py` îl
numeau ca dovadă a parității. Trimiterea la ceva inexistent se semnalează; aici s-a semnalat
construind lucrul citat.*

### Ce a ieșit la iveală mutând, și e clasa zilei

**Întreaga mașinărie de gărzi doc↔cod era ancorată pe presupunerea că logica aplicației stă în
`main.py`.** Mutând-o, ~40 de gărzi au devenit deodată oarbe sau roșii — nu fiindcă s-ar fi stricat
codul, ci fiindcă se uitau unde nu mai e nimic. Fiecare a fost re-ancorată prin accesorul comun
(`core/scan_sql_efectiv.py`), fără să-și piardă semantica.

**Patru lucruri s-au pierdut tăcut, și fiecare a fost prins de alt instrument:** două gărzi
anti-spam (`_rate_limit_*`) lăsate pe dinafară de mutator · comentariile de pe linia decoratorului,
printre care cinci marcaje `[api_intern_v1]` pe care un instrument le citește ca declarație · și un
RE-EXPORT (`main.pastila_firma`) scos de curățenia automată de importuri, care a lăsat șase firme cu
`control_fiscal` în eroare. Toate patru erau lucruri pe care codul le spunea, iar valul le-a rescris
din ceva care nu le conținea. Fiecare și-a primit garda.

**Iar două scanere aveau `main.py` ca punct orb DECLARAT** (`scan_data_curenta`, `scan_constante`):
valul le-a închis gaura, iar clichetele lor au urcat — nu fiindcă s-a scris cod nou, ci fiindcă
**instrumentul vede mai mult**. Fiecare urcare e scrisă cu lista exactă a cazurilor nou-expuse, și
fiecare caz se regăsește, la aceeași formă, în `git show HEAD:main.py`.


## 13.09.2026, partea a patra — **P7 · valul D4: 215 instrucțiuni mutate, și faza tot nu se închide**

Pentru un contabil, a patra oară azi: nu s-a schimbat nimic. Aceleași ecrane, aceleași declarații,
aceleași cifre. Ce s-a schimbat e unde stă SQL-ul — și ce știm despre cât mai avem de făcut.

### Ce s-a schimbat, sub capotă

Cele **37 de module mixte** — cele care făceau două straturi deodată, de la `core/d223.py` cu o
instrucțiune la `core/control_incrucisat.py` cu 45 și `main.py` cu 38 în helperii de modul — și-au
dat cele **215 instrucțiuni SQL** la **37 de `core/repo_*.py`**. `D4` **37 → 0**.

Mutarea a fost făcută de un instrument, `scripts/p7_d4_separa.py`, nu cu mâna. Motivul e o
măsurătoare, nu o preferință: 215 poziții în 13 forme diferite de loc, iar modul de eșec al unei
mutări manuale — parametri schimbați de ordine, un `fetchone` devenit `fetchall`, un `%s` pierdut —
**nu se vede la citire**. Instrumentul mută expresii, nu text; ce nu poate rezolva mecanic
raportează și lasă neatins. **Rest: 0 din 215.**

**Dovada că s-a mutat, nu s-a rescris:** amprenta SQL a întregului cod de producție — **1050
instrucțiuni distincte, 1307 în total** — e identică înainte și după.

### Partea care merită citită: cifra care arăta bine

După val: `D1`=0, `D2`=0, `D4`=0, **`P7_ACTION_REQUIRED`=0**. Citită singură, cifra spune că faza s-a
terminat. **Nu s-a.** Textul canonic cere patru straturi, iar despre use-case spune că *deține
tranzacția (P4) și orchestrează*. Măsurat: **385 din 421 de rute își deschid singure tranzacția**,
doar **7** deleagă către un modul `USE_CASE`, iar use-case-uri declarate sunt **4**.

*Un `ACTION_REQUIRED=0` care nu acoperă un criteriu canonic nu e o stare, e o lipsă de detector.* Am
închis golul cu un instrument și o gardă, nu cu o propoziție în predare: `scripts/p7_criterii.py`
măsoară toate patru criteriile, iar `core/test_p7_criterii.py` ține clichetul celor 385 **și
interzice planului să declare P7 închisă peste el**.

### Ce a mai scos valul, și toate trei sunt aceeași clasă

1. **O justificare ancorată prin vecinătate nu se mută cu codul.** Trei `ON CONFLICT DO UPDATE` au
   trecut în depozit, iar `# upsert-ok:` a rămas în modulul vechi. Prins de `test_upsert_motivat` la
   prima rulare — de instrument, nu de mine.
2. **Instrumentul traseelor a tăcut din nou**, a doua oară în două valuri: 12 adnotări deodată.
   Reparat cu **perechea nominală** modul ↔ `repo_<același nume>`.
3. **Citările în plan s-au mutat iar** — 8 ancore. De data asta reparate cu un instrument,
   `scripts/reancoreaza_plan.py`, care a greșit el însuși de două ori înainte să meargă: cerea
   unicitatea fragmentului pe tot planul, și lua reperul din fișierul deja editat.

### Cifre

`D4` **37 → 0** · `P7_RAW_ITEMS` **38 → 1** · `P7_ACTION_REQUIRED` **37 → 0** · straturi declarate
**167** (96 `FISCAL_ENGINE` · 65 `REPOSITORY` · 4 `USE_CASE` · 2 `HTTP`). Criteriul rămas:
**385/421**. Poarta: **5795 verzi / 0 roșii** · 12 sărite · 14 xfail ·
verificator **TOTAL 0**.

**P7 RĂMÂNE DESCHISĂ.** *Zero pe toate detectoarele nu e zero pe fază.*
