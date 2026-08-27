Citeste CLAUDE.md §2.2 (structura raportului) si §2.3 (lant, siguranta, limba - pct.11 poarta verde vizuala) + ARHITECT.md "FORMA COMENZII" (7 puncte), apoi acest PREDARE_LANT.md, inainte de a incepe.

# PREDARE LANȚ — ziua în care cinci restanțe deschise dimineața au fost și închise, iar trei dintre ele s-au exercitat pe viu (27.08.2026)

## ANTET — cât de veche e predarea asta

- **ultima rescriere**: **2026-08-27**, seara. *Rescriere COMPLETĂ, nu petic.*
- **pe commit**: `110f346` — starea pe care o descrie.
- **rescrierea de dinainte**: `03a5245`, aceeași zi, dimineața. Între ele au încăput **6 commituri**,
  trei restanțe închise și **trei deschise** (R80, R81 sunt noi).
- **de ce acum, deși pragul NU sunase**: `PREDARE_LANT.md` era atins ultima dată în `04e6f38`, deci
  la **2 commituri** în urmă, sub pragul de 10 — avertismentul din `pre-commit` **nu** a apărut azi.
  Costin a cerut rescrierea pe alt motiv, iar el ține: *„o sesiune nouă o citește prima și ar porni
  din stare veche."* Conținutul îmbătrânise, nu contorul. *(Cifra „12 commituri în urmă" din comandă
  nu se confirmă în repo — se scrie aici ca să nu fie recitită mâine ca fapt.)*
- **cine o rescrie și când**: **se rescrie ÎNAINTE de fiecare oprire.**
- **gardat**: `scripts/githooks/pre-commit` avertizează peste 10 commituri;
  `core/test_predare_proaspata.py` nu lasă avertismentul să dispară tăcut. Avertizează, nu blochează.

---

## STAREA LA PREDARE

Poartă verde la `110f346`: **3395 teste** ✓ · 10 skip · 14 xfail · ruff OK · verificator
**TOTAL 0** · site 200 · four-way `HEAD = origin/main = backup/lant-2026-08-27 = 110f346`, proces
pornit **19:38:52**, după commitul de la **19:27:29**. *(Se reverifică rulând poarta, nu se crede
pe cuvânt.)*

Zero modificări necomise. Neurmărite: **234** de fișiere — cele șapte `LOT_*_VERIFICARI.md`,
`corectii_lot_1.md`, și artefacte vizuale în `frontend_test/` (capturi `.png`, `.csv` de probă).

**Cifrele nu se scriu aici** — `scripts/raport_b.py`. Fotografia de la `110f346`: locuri de
verificare **203 scrise / 0 goale (100%)**; restanțe deschise **47** (E1: **25**); interdicții din
76: MĂSURATE 21 · PARȚIAL 16 · NEMĂSURABILE 1 · NEÎNCEPUTE 38.

---

## PRIMUL LUCRU DE ȘTIUT: TREI SCHIMBĂRI PE MAȘINĂ ȘI ÎN DATE, FĂCUTE ÎN AFARA REPO-ULUI

Cine continuă trebuie să știe că nu sunt în git:

1. **O linie nouă în `crontab`**, la 15 minute: `core.sonda_web`. Pusă de **mine**, fiindcă propria
   gardă din R74 respinge un prag pentru un job care nu există nicăieri. Backup înainte:
   `/home/costin/crontab_inainte_sonda.bak`. **Confirmată de Costin** — dar rămâne scrisă aici ca
   fiind a mea: *„o schimbare pe mașină, făcută de tine, e altceva decât una în repo."*
2. **O alertă pe email**, trimisă de mine la **12:42** din greșeală, în timpul probei sondei —
   subiect *„nu pot spune dacă a fost deploy"*. E de ignorat.
3. **Portofoliul s-a schimbat de trei ori azi, prin ecran, de către Costin** (vezi mai jos).

---

## CE S-A ÎNTÂMPLAT ÎN DATE, ȘI E MAI IMPORTANT DECÂT CE S-A SCRIS ÎN COD

**Trei firme scoase, prin ecran, nu prin `psql`** — `public.firme_scoase` are 3 rânduri:

| # | firma | CUI | când |
|---|---|---|---|
| 7 | PROBA PORTAL SRL | 14399840 | 13:42:13 |
| 8 | PROBA PORTAL SRL | 2816464 | 13:44:40 |
| 9 | **BORG DESIGN SRL** | 14837428 | **19:25:04** |

**Portofoliul are acum 18 firme.** Urmele R62 — patru rânduri din `urme_portal` plus confirmarea
din `schimbari_email` — au supraviețuit, cu conținut cu tot, în `firme_scoase.urme_pastrate`.
Conturile de client rămase fără firmă au fost **dezactivate**, nu șterse.

### R79 s-a verificat pe viu, nu doar în teste

Primele două ștergeri (13:42, 13:44) au lăsat fiecare **câte un orfan**: rândul de audit al cererii
`DELETE` se scria la ~78 ms **după** ce firma dispărea, cu `tenant_id`-ul ei mort. 67 → 69.

A treia ștergere (**19:25:04**, după reparație) a scris:

```
id 1272066 · user 1968 · tenant_id = NULL · 'DELETE /tenants/33395' · {'status': 200}
```

**`tenant_id` e NULL, iar totalul orfanilor a rămas 69.** Legea era liniară — fiecare scoatere
lăsa exact unul. Acum nu mai lasă. *Asta e verificarea care contează; testul doar o ține.*

### R77 s-a exercitat de un om, pe o firmă reală

Costin a adăugat **`Antibiotice Iasi`** (CUI `1973096`) la **19:12:00**. Precompletarea ANAF a
capturat `nume_anaf = 'ANTIBIOTICE SA'` — **prima firmă din sistem cu instantaneu ANAF**. Caseta cu
două butoane a apărut, iar la **19:16:24** el a apăsat **„Păstrez denumirea mea"**:

```
tenants:   nume_ales='aplicatie' · nume_ales_la=19:16:24 · nume_ales_de=1968
audit_log: 'nume_ales' {'nume':'Antibiotice Iasi','alege':'aplicatie','nume_anaf':'ANTIBIOTICE SA'}
```

**Ramura care „nu face nimic" a scris.** Exact ce cerea restanța: *„a păstra pe a ta = a nu face
nimic" nu e o alegere.* Astăzi nu mai e — e un act cu autor și dată.

**Deci divergența de denumire nu mai e o construcție neprobată pe date reale.** Nota din predarea
de dimineață — *„0 din 17 firme au `nume_anaf`, divergența nu se poate vedea nicăieri"* — **nu mai
e adevărată.** Azi: 18 firme, **1** cu `nume_anaf`, **1** cu alegere consemnată.

---

## CE S-A ÎNCHIS ȘI CE S-A DESCHIS, ÎN ORDINEA ZILEI

**Închise:** **R72** (o firmă adăugată din greșeală se poate scoate; una cu evidență, nu) ·
**R50** (ștergerea de cabinet curăță toate cele 13 tabele) · **R74** (cele trei joburi SPV) ·
**R71 obs. 2** (reparația din 26.08 nu funcționa) · **R79** · **R78** · **R77**.

**Deschise și rămase deschise:** **R75** (procesul web n-avea deadman — sonda e construită, dar
restanța rămâne: prinde repornirea, nu durata) · **R76** (70% din cererile care se declară Googlebot
sunt scanere) · **R80** · **R81**.

**Cele trei deschise dimineața și închise seara:** R77, R78, R79. *Din cele cinci deschise azi, două
rămân.*

**Aplicate fără restanță proprie:** denumirea unică per cabinet (creare **și** redenumire) ·
instantaneul ANAF al denumirii · plasa pentru refuzurile înghițite · validarea CUI pe redenumire.

---

## CE BLOCHEAZĂ, ÎN ORDINE

1. **R81 — o firmă are denumirea în DOUĂ locuri, iar pe 4 din 18 ele diferă.** `tenants.nume` e
   portofoliul (lista, bara de sus); `firma_profil.nume` e **fiscala** — pleacă în D100, D101, D205,
   D301, D390, D394, D406 și pe bilanț. Ecranul le arată acum distinct și spune care pleacă pe
   hârtie; **regula de împăcare e nescrisă.** Decizia lui Costin: (a) una singură, a doua derivată ·
   (b) divergența devine alegere, ca la ANAF · (c) rămân două, cu clichet.
2. **R80 — gardul „rută fără apelant" e mut pe 51 din 411 rute.** Varianta (c) aplicată: măsurat și
   clichetat. Verdele gardului poartă acum numitorul — *„acoperire reală: 360 din 411 (88%)"*.
   Rămâne deschisă fiindcă orbirea nu s-a reparat, doar s-a numit.
3. **`PUT /tenants/{tenant_id}` avea zero apelanți** până seara, când i-am dat câmpul din „Date
   firmă". Acum are unul. **Dar cazul rămâne instanța lui R80**: gardul construit exact pentru clasa
   asta n-a văzut-o, fiindcă singura ei ancoră literală e `tenants`, care apare de 235 de ori în JS.
4. **R67 cere `postgres`.** Neschimbat: `iconta_user` n-are CREATEROLE.
5. **Cele 19 restanțe cu `reluări: 0`** stau într-o fotografie. Nu le-am urcat contorul: aș inventa
   cifre pe care nu le pot recalcula.

---

## INSTRUMENTE NOI, ȘI CE MĂSOARĂ FIECARE

| instrument | ce numără | clichet |
|---|---|---|
| `core/test_tenant_stergere.py` | calea de ștergere + orfanii de audit | orfani **69** |
| `core/test_joburi_supravegheate.py` | joburile citite din SISTEM, nu dintr-o copie | interpretoare lipsă **0** |
| `core/test_esec_trimitere_email.py` | un `except` care prinde o trimitere cheamă `esec_secundar` | fără baseline |
| `core/test_sonda_web.py` | sonda e în `RITMURI`, cere pagina, compară ora de pornire | — |
| `core/test_refuz_tacut.py` | scrieri care refuză fără să arate motivul | **16** scrieri · **70** citiri |
| `core/test_nume_firma_unic.py` | unicitatea denumirii + **cele două denumiri** (R81) | duplicate **0** · divergențe **4** |
| `core/test_nume_anaf.py` | alegerea are amândouă ramurile, amândouă scriu | — |
| `core/test_ancore_rute.py` + `scripts/scan_ancore_rute.py` | rute despre care R70 nu poate afirma nimic | **51 din 411** |
| `core/test_reluari_decizie.py` | o restanță DECIZIE nu trece 5 commituri cu `reluări: 0` | fotografie **19** |
| `frontend_test/vizual/axe_firme.py` | axe-core pe ecranele de firme (nu sunt în `nav_ecrane`) | 0 violări |

---

## REGULI EXERCITATE AZI, CU INSTANȚA FIECARE

- **Măsoară întâi, construiește după.** De trei ori măsurătoarea a schimbat construcția, nu doar a
  confirmat-o: (1) `ON DELETE SET NULL` ar fi făcut ștergerea de firmă **imposibilă** pe 10 din 13
  tabele; (2) „13 rute care ating denumirea" erau **5**, iar cifra 13 era numărul tabelelor; (3)
  ecranul „Date firmă" **avea deja** un câmp de denumire, care scrie altundeva.
- **Numele unei variante nu spune ce face varianta.** Vezi (1) de mai sus.
- **„Nu rearanjează nimic" poate fi adevărat despre pixeli și fals despre structură.** Un `<button>`
  nu poate conține alt `<button>`; prima implementare a butonului „Scoate" a transformat rândul în
  `<div>` — și **36 de fișiere** selectează `button.firme-rand`, între ele `w_auth.deschide_firma`.
- **O sondă care citește `inner_text("body")` citește și ecranele de dedesubt.** A raportat că toate
  cele 13 firme au evidență. Fals în ambele direcții — deci fără plafon (METODA §22).
- **Verdele fals are un miros: lipsa unui numitor.** „0 PUT-uri trimise" era verde fiindcă validarea
  oprea salvarea înainte de orice cerere. Sonda cere acum explicit ca salvarea **să plece**.
- **RED-proof pe sursa reală, nu pe șabloane** — `main.py` și `tenant_provisioning.py` mutate în
  memorie, patru mutații, patru roșii, fișierele de pe disc neatinse. Refăcut după refactor.
- **O gardă asertează pe structură.** Clichetul de ancore pe text s-a aprins pe **fișierul meu nou**
  și m-a trimis înapoi să scriu trei aserțiuni ca noduri de AST, nu ca șiruri.

---

## CIFRE INVALIDATE — se păstrează, nu se șterg

*O cifră ai cărei termeni nu se mai pot reconstitui se **INVALIDEAZĂ**, nu se corectează.*

| cifra | unde apărea | de ce e INVALIDATĂ |
|---|---|---|
| **131** (valori fiscale în afara registrului) | predarea din 22.08 | termeni recalculați pe domeniu lărgit de trei ori. Clichetul viu: `core/test_constante_nesursate.py` |
| **„25 de trasee"** | comenzile din 24 și 25.08 | nu exista instrument. Cifra care se poate reface e **36** |
| **„129 de rute schimbă date fără rol"** | predarea din 26.08 dimineață | raza nu se mai poate reconstitui |
| **17** (coloane citite și scrise de nimic) | instrument din 26.08 seara | INVALIDATĂ înainte de publicare |
| **13 / 6** (rute de citire fără apelant) | raportul din 26.08 seara | ancoră greșită; real, prin citire: **5** |
| **„4 din 5 rute nedeclarate"** | R70, 26.08 | **2**, nu 4 |
| **12** (tabele cu `tenant_id`) | R50, 25.08 | **13** din 26.08 |
| **25** (scrieri care refuză fără motiv) | prima măsurătoare, 27.08 | **16** după calibrare |
| **623** (404-uri primite de Googlebot) | raportul din 27.08 | **11**; restul sunt scanere — 70,3%, prin rDNS cu confirmare |
| **„2" (aritmetică pe nume neutre)** | clichet din 24.08 | cifra e tot 2, dar **termenii** erau greșiți |
| **8** (coloane `tenant_id NOT NULL`) | 27.08, R79, în mesajul commitului `0963d7f` | **10**. Numărată pe drum, fără instrument — *deci nu era o măsurătoare, era o amintire* |
| **„1 din 411" (rute oarbe la detector)** | prima măsurătoare a orbirii, 27.08 | **51**. `_static()` întoarce un **șir**, iar `"\n".join(șir)` îl sparge în caractere |
| **„toate cele 13 firme au evidență"** | prima sondă de scoatere, 27.08 | clasificator pe text, care citea ecranele rămase în DOM |
| **„0 din 17 firme au `nume_anaf`"** | predarea din 27.08 dimineața | **1 din 18** din 19:12 — Costin a adăugat firma |

---

## CE NU E ADEVĂRAT DESPRE STAREA ASTA, ȘI SE SPUNE

- **Verde nu înseamnă exercitat.** 3395 de teste trec, și o reparație raportată ca făcută pe 26.08
  n-a funcționat trei zile — `incarca()` era declarată în alt scop, iar `catch`-ul înghițea
  `ReferenceError`. **Ce a ascuns-o e chiar clasa reparată la R73.**
- **Sonda web prinde REPORNIREA, nu DURATA.** Între două sonde la 15 minute, o cădere de trei
  secunde și una de paisprezece minute arată identic. R75 rămâne deschisă tocmai de-aia.
- **Baseline-urile nu sunt curate.** Sunt fotografii. Gărzile spun că **nu cresc**, nu că listele
  sunt adevărate.
- **Butonul „Scoate" nu e gardat de nimic mecanic.** Proba Playwright e o **probă, nu o gardă**:
  dacă ajunge iar sub pliu, îl găsește Costin, nu un test.
- **Cei 67 de orfani dinainte rămân.** Decizia lui Costin, cu motivul: ștergerea lor ar șterge
  singura urmă că firmele alea au existat. **Cifra 69 nu e o măsură a sănătății, e o constantă
  istorică** — informația e **creșterea**, nu totalul.
- **Sursa celor 17 URL-uri 404 din Search Console rămâne NECUNOSCUTĂ.** Sitemap, HTML, ghiduri, JS
  și istoria git — verificate, niciunul. Fereastra în care s-ar putea măsura (iunie–iulie) nu mai
  există în loguri. *Iar absența accesărilor după 17.08 nu dovedește că reparația a oprit ceva:
  ultima e din 30 iulie, cu 16 zile înainte de ea.*
- **Mesajul commitului `110f346` e TRUNCHIAT la jumătate.** Un ghilimel din text a închis argumentul
  `ssh`, heredoc-ul a rămas nedelimitat, iar git a primit un mesaj scurtat **fără să eșueze**. Din
  ~2200 de caractere au ajuns 1090. E împins, iar `--force` pe main e interzis: **rămâne așa**.
  Substanța e în `CONFORMITATE.md`, `GARZI.md`, `TESTE.md`. *De acum mesajul de commit se trimite
  prin fișier, ca patch-urile, iar ultima linie se verifică după fiecare commit.*
- **Ce n-a fost măsurat, și se știe:** dacă vreo declarație **deja depusă** poartă o denumire
  diferită de cea din portofoliu de azi. E o măsurătoare separată, pe `declaratii_depuse`.

---

## DACĂ CONTINUI DE AICI

1. **Citește `CONFORMITATE.md` pentru R80 și R81** — amândouă așteaptă o decizie a lui Costin, și
   amândouă au variantele scrise cu ce câștigă și ce pierde fiecare.
2. **Nu porni nicio construcție fără măsurătoare.** Azi, de trei ori din trei, măsurătoarea a
   schimbat ce trebuia construit.
3. **`scripts/raport_b.py` derivă secțiunea „Unde suntem".** Nu se scrie de mână.
4. **Poarta durează ~11 minute** (3395 de teste). Comite prin `nohup … &` și așteaptă separat —
   o sesiune `ssh` întreruptă la mijloc lasă fișierele *staged* și niciun commit.
