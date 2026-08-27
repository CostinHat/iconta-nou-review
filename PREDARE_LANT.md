Citeste CLAUDE.md §2.2 (structura raportului) si §2.3 (lant, siguranta, limba - pct.11 poarta verde vizuala) + ARHITECT.md "FORMA COMENZII" (7 puncte), apoi acest PREDARE_LANT.md, inainte de a incepe.

# PREDARE LANȚ — ziua în care „nimeni nu întreabă dacă merge" a devenit o clasă cu trei etaje (27.08.2026)

## ANTET — cât de veche e predarea asta

- **ultima rescriere**: **2026-08-27**, *rescriere COMPLETĂ, nu petic*
- **pe commit**: `03a5245`
- **actualizată** *(nu rescrisă)*: **2026-08-27**, după tura R77–R79. Trei restanțe închise, zero deschise. Secțiunile atinse: „CE S-A ÎNCHIS", „CE BLOCHEAZĂ", plus una nouă la coadă. Restul rămâne valabil — de aceea e petic, nu rescriere.
- **de ce acum**: **și pragul, și conținutul.** Contorul arăta **11** commituri de la ultima
  rescriere (`cf945fc`), peste pragul de 10 — deci avertismentul a sunat. Dar s-ar fi rescris
  oricum: **două restanțe închise, două deschise, opt gărzi noi, două decizii aplicate, patru
  cifre invalidate.** *O predare se rescrie când nu mai descrie lumea; contorul doar reamintește.*
- **cine o rescrie și când**: **se rescrie ÎNAINTE de fiecare oprire.**
- **gardat**: `scripts/githooks/pre-commit` avertizează peste 10 commituri;
  `core/test_predare_proaspata.py` nu lasă avertismentul să dispară tăcut. Avertizează, nu blochează.

---

## STAREA LA PREDARE

Poartă verde la `03a5245`: **3382 teste** ✓ · 10 skip · 14 xfail · ruff OK · verificator
**TOTAL 0** · site 200 · four-way `HEAD = origin/main = backup/lant-2026-08-27 = 03a5245`, proces
viu pornit **după** commit. *(Se reverifică rulând poarta, nu se crede pe cuvânt.)*

Neurmărite: cele șapte `LOT_*_VERIFICARI.md`, `corectii_lot_1.md`, artefacte vizuale în
`frontend_test/`. Zero modificări necomise.

**Cifrele nu se scriu aici** — `scripts/raport_b.py`. Fotografia de la `03a5245`: locuri de
verificare **197 scrise / 0 goale (100%)**; restanțe deschise **45** (E1: **23**).

---

## PRIMUL LUCRU DE ȘTIUT: DOUĂ SCHIMBĂRI PE MAȘINĂ, FĂCUTE DE MINE

Nu de cod — **de mediu**. Cine continuă trebuie să știe că nu sunt ale lui Costin:

1. **O linie nouă în `crontab`**, la 15 minute: `core.sonda_web`. Am pus-o eu, fiindcă propria
   gardă din R74 respinge un prag pentru un job care nu există nicăieri. Backup înainte:
   `/home/costin/crontab_inainte_sonda.bak`. **Confirmată de Costin** — dar rămâne scrisă aici ca
   fiind a mea: *„o schimbare pe mașină, făcută de tine, e altceva decât una în repo."*
2. **O alertă pe email**, trimisă de mine la **12:42** din greșeală, în timpul probei sondei —
   subiect *„nu pot spune dacă a fost deploy"*. E de ignorat.

**Cele două firme `PROBA PORTAL SRL` au fost scoase** de Costin la 13:42 și 13:44, prin ecran.
Portofoliul are acum **17** firme. Urmele R62 — patru rânduri din `urme_portal` plus confirmarea
din `schimbari_email` — **au supraviețuit**, în `firme_scoase.urme_pastrate`, cu conținut cu tot.
Cele două conturi de client au fost **dezactivate**, nu șterse.

Iar `firma_profil.patron_nume` rămâne **goală pe toate cele 17 firme, iar 8 au salariați**.
Neschimbat față de ieri: prima adeverință cerută pe oricare din cele opt **se oprește**. Oprirea e
corectă; cine continuă trebuie s-o știe **înainte** să dea de ea.

---

## FORMA ZILEI: „CEVA FUNCȚIONEAZĂ SAU NU, ȘI NIMENI NU ÎNTREABĂ" — TREI ETAJE

Aceeași formă, găsită de trei ori în două zile, la trei niveluri diferite:

| etaj | instanța | starea |
|---|---|---|
| **ruta** | `POST /public/confirma-email` — scrisă, gardată, verde, **nechemată** | R70, gard construit |
| **jobul** | `spv-poll/receive/refresh` — programate, verzi în `list-timers`, **nepornite ~31 de zile** | R74 **ÎNCHISĂ** |
| **procesul** | `iconta-nou` — a căzut și a revenit în 3s, **nimeni n-a aflat** | R75, sondă construită |

**Gărzile verificau ce face lucrul DACĂ rulează. Niciuna nu întreba DACĂ rulează.**

---

## A DOUA FORMĂ: UN CONTOR CARE NU URCĂ FACE O GARDĂ IMPOSIBIL DE APRINS

Costin a întrebat de două ori *„de ce nu ajunge răspunsul la restanță?"*. Măsurat: din restanțele
DESCHISE deblocate de DECIZIE, **19 aveau `reluări: 0`** — **R9 de 133 de commituri**, R18 de 122,
R26 de 90. Câmpul exista. Garda lui exista (sare la ≥3). **Dar contorul nu urca niciodată, deci
garda n-a putut să se aprindă nici măcar o dată.**

Și partea mai rea: clasa era **deja găsită și scrisă** în registru — *„regula era scrisă și
nepăzită, deci se citea ca respectată"* — și lăsată ca **disciplină**. A rămas 0 pe 69 din 76.
`core/test_reluari_decizie.py` o mută pe gardă.

**A doua jumătate, care NU se poate garda:** denumirea n-a ajuns la restanță fiindcă **n-a fost
niciodată o restanță** — a trăit doar în §0 al rapoartelor. *O cerință fără restanță n-are contor,
n-are condiție de deblocare, și nu supraviețuiește turei.*

---

## A TREIA: UN INSTRUMENT CARE GREȘEȘTE ÎN AMÂNDOUĂ DIRECȚIILE N-ARE NICIUN PLAFON

Cititorul de șiruri JS din `test_aritmetica_in_prezentare` **nu știa de `${…}`**. La un template
imbricat era **defazat**: ce era text trecea drept cod și invers. **Deci clichetul „2" nu era o
măsurătoare, era o coincidență de sincronizare** — a ținut până când un ecran nou a schimbat
parcursul. N-a găsit-o niciun instrument: **a găsit-o poarta**.

Reparat de două ori, și a doua oară contează mai mult: **prima reparație albea și interiorul
interpolării**, adică exact codul. A prins-o **calibrarea scrisă în aceeași tură**. Fără ea, o
orbire ar fi fost înlocuită cu alta și raportată ca reparație.

---

## CE S-A ÎNCHIS ȘI CE S-A DESCHIS

**Închise azi:** **R72** (o firmă adăugată din greșeală se poate scoate; una cu evidență, nu) ·
**R50** (ștergerea de cabinet curăță toate cele 13 tabele) · **R74** (cele trei joburi SPV) ·
**R71 obs. 2** — închisă **abia acum**, fiindcă reparația din 26.08 **nu funcționa**.

**Deschise azi:** **R75** (procesul web n-avea deadman) · **R76** (70% din cererile care se declară
Googlebot sunt scanere) · **R77** (divergența de denumire se arată, dar alegerea nu se cere) ·
**R78** (butonul de scoatere stă sub 26 de carduri) · **R79** (ștergerea își produce propriul
orfan, la 78 ms după ce a terminat).

**Închise în tura de seară, toate trei deschise în aceeași zi:** **R79** (auditul nu mai lasă
referințe moarte) · **R78** (butonul e pe rândul fiecărei firme din listă) · **R77** (două butoane,
niciunul implicit, amândouă scriu). *Deci din cele cinci deschise azi rămân două: R75 și R76.*

**Aplicate fără restanță proprie:** denumirea unică per cabinet (creare **și** redenumire) ·
instantaneul ANAF al denumirii · plasa pentru refuzurile înghițite.

---

## CE BLOCHEAZĂ, ÎN ORDINE

1. **R67 cere `postgres`.** Neschimbat: `iconta_user` n-are CREATEROLE.
2. **Cele 19 restanțe cu `reluări: 0`** stau într-o fotografie. Nu le-am urcat contorul: aș inventa
   cifre pe care nu le pot recalcula.
3. **Divergența de denumire nu se poate vedea pe nicio firmă reală.** **0 din 17** au `nume_anaf` —
   instantaneul se captează doar de la o precompletare ANAF încolo. Calea R77 e construită, gardată
   și probată (server pe date reale, ecran pe răspuns fabricat), dar **veriga de capăt lipsește**:
   o firmă nouă, cu CUI ales de Costin, care să treacă prin ANAF și să producă divergența singură.
   Costin a oferit-o în tura asta; e cea mai ieftină verificare rămasă deschisă.
4. **`ISTORIC.md` n-a primit încă rândul celor două firme scoase din portofoliu.** Datorie declarată
   de mine, „la închiderea zilei", și încă neplătită.

---

## REGULI EXERCITATE AZI

- **Măsoară întâi, construiește după** — R72 a început cu inventarul, nu cu ruta. Din inventar au
  ieșit trei lucruri pe care nimeni nu le căuta: 10 tabele fără cheie străină, `gdpr_sterge` care
  ar fi eșuat la mijloc, și 9 scheme fără firmă.
- **Calibrează pe instanțe reale înainte de a publica cifra** — „25 de scrieri mute" a devenit
  **16** după ce le-am citit una câte una.
- **O cale distructivă se exercită înainte de a fi publicată** — calea GDPR **veche** a fost
  rulată într-un `SAVEPOINT` și a eșuat, ca să se vadă că defectul nu era o deducție.
- **RED-proof pe sursa reală, nu pe șabloane** — `main.py` mutat în memorie, patru mutații, patru
  roșii, fișierul de pe disc neatins.
- **Un plafon declarat mută costul, nu-l scoate** — eticheta *„PLAFON, nemăsurat pe rută"* e
  onestă, dar Costin tot a trebuit s-o ceară și eu tot a trebuit s-o măsor.
- **Registrele nu se umplu ca să pară pline** — `ISTORIC.md`, `DECIZII.md`, `METODA` au rămas
  neatinse de zece ori azi, cu motivul scris de fiecare dată.

---

## CIFRE INVALIDATE — se păstrează, nu se șterg

*O cifră ai cărei termeni nu se mai pot reconstitui se **INVALIDEAZĂ**, nu se corectează.*

| cifra | unde apărea | de ce e INVALIDATĂ |
|---|---|---|
| **131** (valori fiscale în afara registrului) | predarea din 22.08 | termeni recalculați pe domeniu lărgit de trei ori. Clichetul viu: `core/test_constante_nesursate.py` |
| **„25 de trasee"** | comenzile din 24 și 25.08 | nu exista instrument. Cifra care se poate reface e **36** (T36 adăugat azi) |
| **„129 de rute schimbă date fără rol"** | predarea din 26.08 dimineață | raza nu se mai poate reconstitui |
| **17** (coloane citite și scrise de nimic) | instrument din 26.08 seara | INVALIDATĂ înainte de publicare |
| **13 / 6** (rute de citire fără apelant) | raportul din 26.08 seara | ancoră greșită; real, prin citire: **5** |
| **„4 din 5 rute nedeclarate"** | R70, 26.08 | **2**, nu 4. Trei aveau deja marcajul — iar registrul îl **citase** pe unul, în același fișier |
| **12** (tabele cu `tenant_id`) | R50, 25.08 | **13** din 26.08: `schimbari_email`, creată de reparația R62 |
| **25** (scrieri care refuză fără motiv) | prima măsurătoare, 27.08 | **16** după calibrare: nouă foloseau `insertAdjacentHTML` |
| **623** (404-uri primite de Googlebot) | raportul meu din 27.08 | **11**. Restul sunt scanere care se dau drept el — 70,3%, verificat prin rDNS cu confirmare |
| **„2" (aritmetică pe nume neutre)** | clichet din 24.08 | cifra e tot 2, dar **termenii** erau greșiți: cititorul era defazat. Acum e o măsurătoare |

---

## TURA R77–R79: CE S-A ÎNVĂȚAT, ÎN TREI RÂNDURI

1. **Numele unei variante nu spune ce face varianta.** Costin a cerut cheia străină cu
   `ON DELETE SET NULL` — și a cerut măsurarea înainte. Măsurarea a arătat că `SET NULL` pe o
   coloană `NOT NULL` **se acceptă la definire** și rupe **la ștergere**, pe **10 din 13** tabele;
   iar pe coloanele nullable nici nu atinge cazul nostru, fiindcă rândul se scrie **după** ce
   părintele a murit — deci ar fi fost **respins**, nu trecut pe `NULL`. *Fără măsurătoarea cerută,
   aș fi livrat o cheie străină care oprea ștergerea de firmă.*
2. **„Nu rearanjează nimic" poate fi adevărat despre pixeli și fals despre structură.** Un
   `<button>` nu poate conține alt `<button>`, deci prima implementare a butonului „Scoate" a
   transformat rândul în `<div>`. Nimic nu se mișca pe ecran — dar **36 de fișiere** selectează
   `button.firme-rand`, între ele `w_auth.deschide_firma`, poarta întregii infrastructuri vizuale.
   Refăcut: rândul rămâne buton, acțiunea se așază **lângă** el. *Constrângerea nu cerea să schimb
   rândul, cerea să nu bag butonul în el.*
3. **O sondă care citește `inner_text("body")` citește și ecranele de dedesubt.** Prima versiune a
   probei de scoatere a raportat că **toate cele 13** firme au evidență. Fals: ecranele anterioare
   rămân în DOM. Trecută pe structură (`#sf-sterge` în ecranul curent), a găsit imediat ambele
   clase. *Greșea în ambele direcții — deci n-avea niciun plafon (METODA §22).*

---

## CE NU E ADEVĂRAT DESPRE STAREA ASTA, ȘI SE SPUNE

- **Verde nu înseamnă exercitat.** 3382 de teste trec, și o reparație raportată ca făcută pe 26.08
  n-a funcționat trei zile — `incarca()` era declarată în alt scop, iar `catch`-ul înghițea
  `ReferenceError`. **Ce a ascuns-o e chiar clasa reparată la R73.**
- **Sonda web prinde REPORNIREA, nu DURATA.** Între două sonde la 15 minute, o cădere de trei
  secunde și una de paisprezece minute arată identic.
- **Baseline-urile nu sunt curate.** Sunt fotografii. Gărzile spun că **nu cresc**, nu că listele
  sunt adevărate.
- **Sursa celor 17 URL-uri 404 din Search Console rămâne NECUNOSCUTĂ.** Sitemap, HTML, ghiduri, JS
  și istoria git — verificate, niciunul. Fereastra în care s-ar putea măsura (iunie–iulie) nu mai
  există în loguri. *Iar absența accesărilor după 17.08 nu dovedește că reparația a oprit ceva:
  ultima e din 30 iulie, cu 16 zile înainte de ea.*
- **`nume_anaf` e gol pe toate cele 19 firme.** Instantaneul se captează de acum încolo, la
  următoarea precompletare — nu retroactiv. Până atunci, divergența nu se poate arăta nicăieri.
