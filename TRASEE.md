# TRASEE — ce parcurge fiecare lucru prin aplicație

Al patrulea document. Celelalte trei spun **cum trebuie construit**, **ce se măsoară** și **când**. Ăsta spune **ce se întâmplă cu un document, de la intrare până la ieșire** — și e ce lipsea când s-a verificat E1.

Consecința lipsei, măsurată: s-a verificat că D301 iese și se validează, dar nu că traseul până la el e complet. Coada „De depus" conținea trei declarații care n-au trecut prin validator. N-a ieșit din nicio măsurătoare — a ieșit fiindcă cineva a apăsat un buton.

---

## Cum se folosește

**Un traseu se parcurge, nu se citește.** Verificarea unui artefact înseamnă parcurgerea traseului lui, pas cu pas, pe date reale, cu ce trebuie să fie adevărat după fiecare pas.

**Un artefact care iese corect la capătul unui traseu nesparcurs nu e verificat.** E doar produs.

**Ce e scris aici din conversație e marcat `[știut]`. Ce trebuie completat din cod e marcat `[de completat]`.** Nu se inventează pași plauzibili — e chiar greșeala care a produs 13 ghiduri greșite din 40.

---

## Ce poartă un traseu

| element | ce conține |
|---|---|
| **precondiții** | ce trebuie să existe în firmă ca traseul să poată fi parcurs |
| **pașii** | în ordine, fiecare cu ce declanșează trecerea la următorul |
| **ce se verifică după fiecare pas** | nu că pasul a mers — ce trebuie să fie adevărat după el |
| **stările** | în ce stare e obiectul după fiecare pas |
| **cine** | ce rol poate face fiecare pas |
| **traseele negative** | ce se întâmplă când ceva lipsește sau e respins |
| **ce nu are voie** | tranzițiile interzise |

---

# I. DECLARAȚIA

## Traseul principal

```
1. DATELE EXISTĂ ÎN EVIDENȚĂ
      ↓
2. GENERARE
      ↓
3. VALIDARE cu instrumentul oficial
      ↓
4. INTRARE ÎN COADĂ
      ↓
5. APROBARE  (patru ochi, dacă politica e activă și posibilă)
      ↓
6. CONFIRMARE DEPUNERE  (cu index de la autoritate)
      ↓
7. DEPUSĂ
```

### Ce se verifică după fiecare pas

**După 1 — datele:** `[știut]` operațiunile care trebuie să intre în declarație sunt în evidență, nu doar în documente. Cazul care a produs regula: TVA colectată pe facturi în stare `de_preluat`, excluse tăcut din D300.

**După 2 — generarea:** `[știut]` fiecare operațiune din evidență care ar trebui să apară, apare. Absența unei operațiuni nu e vizibilă în structura declarației — D300 cu 18 din 19 e perfect coerent.

**După 3 — validarea:** `[știut]` verdictul se păstrează, cu data și cu ce a spus validatorul. **Un verdict care nu se păstrează nu s-a produs.**

**După 4 — coada:** `[știut]` o declarație intră în coadă **numai cu verdict de validare**. Coada înseamnă „gata de depus", nu „generată".

**După 5 — aprobarea:** `[știut]` cine a aprobat se consemnează. Dacă patru ochi e activ și posibil, cel care aprobă nu e cel care a pregătit.

**După 6 — confirmarea:** `[de completat]` ce se schimbă efectiv — starea, indexul, momentul, autorul.

**După 7 — depusă:** `[de completat]` ce se poate și ce nu se mai poate face cu ea.

### Traseele negative

`[de completat]` — validatorul respinge · autoritatea respinge · datele se schimbă după generare · declarația se retrage · rectificativa.

**Cel puțin astea trebuie să existe ca trasee, nu ca erori.** O respingere nu e un eșec al aplicației; e o stare a documentului.

### Ce nu are voie

`[știut]` O declarație în coadă fără verdict de validare.
`[știut]` O declarație marcată depusă fără să fi trecut prin validare.
`[de completat]` Restul.

---

# II. FACTURA EMISĂ

```
1. CREARE
      ↓
2. STARE  ──  emisa / de_preluat  [știut: două căi de creare, două stări]
      ↓
3. CONTABILIZARE  [știut: nu se face automat; propunerea de conturi lipsește]
      ↓
4. INTRĂ ÎN: D300 · D394 · e-Factura · jurnalul de vânzări
```

**Ce se verifică:** `[știut]` o factură emisă apare în toate ieșirile care o cuprind. Cazul: `de_preluat` era exclus din D300 și inclus în export.

`[știut]` Cele două căi de creare — `creeaza_factura` (7 apelanți, pune `emisa`) și `emite_factura` (6 apelanți, pune `de_preluat`) — produc două populații în aceeași firmă, iar starea nu se mai schimbă niciodată.

**Ce nu are voie:** `[știut]` o factură fără cod fiscal de partener — nu intră în D394 și nu se corelează în VIES.

---

# III. STATUL DE PLATĂ ȘI FLUTURAȘUL

```
1. PONTAJ
      ↓
2. CALCUL  (contribuții, deduceri, facilități, concedii medicale)
      ↓
3. EMITERE STAT  [știut: înghețat cu amprentă, exemplar numerotat]
      ↓
4. FLUTURAȘ  [știut: randare peste rândul statului, nu al doilea calcul]
      ↓
5. PREDARE  [de completat: se marchează?]
      ↓
6. D112
```

**Ce se verifică:** `[știut]` fluturașul și D112 spun același lucru despre aceeași lună. Cazul: fluturașul acorda 920 lei tichete pe care statul nu-i dădea.

`[știut]` Podeaua part-time e aceeași în stat și în declarație.

**Precondiții:** `[știut]` pontajul trebuie să existe — fără el, tichetele se blochează, iar calculul stă pe zile presupuse.

---

# IV. CONCEDIUL MEDICAL

```
1. CERTIFICAT INTRODUS  (cod indemnizație, perioadă, inițial / în continuare)
      ↓
2. VERIFICARE ÎNAINTE DE PLATĂ  [știut: obligație legală de a respinge certificatele greșite]
      ↓
3. CALCUL  (media pe 6 luni, procentul pe episod, diminuarea)
      ↓
4. INTRĂ ÎN STAT DE PLATĂ
      ↓
5. D112
```

**Ce se verifică:** `[știut]` media pe 6 luni se calculează din sursă, nu dintr-un tabel intermediar. Cazul: media depindea de ce ecrane deschisese cineva.

`[știut]` Procentul se determină pe episod, nu pe certificat. Diminuarea se aplică o dată pe episod.

---

# V. NOTA CONTABILĂ

```
1. DOCUMENT (factură, extras, stat)
      ↓
2. PROPUNERE DE CONTURI  [știut: NU EXISTĂ]
      ↓
3. CONFIRMARE DE CĂTRE OM  [știut: ecranul există, ruta există]
      ↓
4. NOTĂ SALVATĂ
      ↓
5. INTRĂ ÎN: registrul-jurnal · cartea mare · balanță · D406
```

**Starea măsurată:** `[știut]` 9.981 din 10.023 de facturi n-au notă. Cele 42 cu notă au fost create manual, prin ecran.

**Ce se verifică:** `[știut]` nota poartă documentul justificativ — felul, numărul, data. Fără el, registrul-jurnal nu e conform, iar lanțul P14 e rupt.

---

# VI. TRASEE DE COMPLETAT DIN COD

`[de completat]` — nu le scriu din presupunere:

importul de e-Factura · extrasul bancar și potrivirea · NIR și recepția · casa și registrul de casă · inventarierea · închiderea de lună · închiderea de an și situațiile financiare · trecerea de regim fiscal · preluarea unei firme.

Pentru fiecare, aceeași structură: precondiții, pași, ce se verifică după fiecare, stări, cine, trasee negative, ce nu are voie.

---

# VII. CE MAI TREBUIE PENTRU TESTARE, ÎN AFARĂ DE TRASEE

Ce n-am spus până acum și lipsește la fel de mult.

## 1. Stările și tranzițiile legale

Pentru fiecare obiect — declarație, factură, stat, notă, perioadă — lista completă a stărilor și ce trecere e permisă din fiecare.

**Fără ea, o stare greșită nu se poate recunoaște.** Cazul: `de_preluat` însemna două lucruri opuse în două module, iar nimic n-o contrazicea.

**Și tranzițiile interzise, explicit:** ce nu se poate întoarce. O perioadă închisă. O declarație depusă. Un document emis.

## 2. Rolurile — cine poate face fiecare pas

Ce poate un asistent, ce poate un administrator de cabinet, ce poate superadmin.

**Contează pentru testare:** verificarea cu un cont care poate tot nu testează restricția. Patru ochi verificat cu superadmin nu verifică patru ochi.

## 3. Precondițiile — ce date trebuie să existe

Pentru fiecare traseu: ce trebuie să aibă firma ca traseul să poată fi parcurs.

**Cazul măsurat:** firmele de test au 3–19 note și 3.000 de facturi. Verdictul familiei A din faza 1 a fost dat pe o evidență cu 0,4% acoperire. Nu era greșit — era pe altceva decât credeam.

**Iar de aici decurge:** care firmă poate exercita care traseu. Azi nu se știe.

## 4. Traseele negative

Ce se întâmplă când merge prost — respingere, lipsă, întrerupere, timeout.

**Sunt cele care nu se testează niciodată**, fiindcă nu se produc singure. Iar când se produc, se produc la un client.

## 5. Ce trebuie să fie adevărat DUPĂ fiecare pas

Nu că pasul a mers — ce s-a schimbat în urma lui, verificabil.

**Diferența:** „butonul a funcționat, coada a trecut de la 3 la 2" e o observație. „Declarația are stare depusă, cu autor și moment, iar verdictul de validare e păstrat" e o verificare.

## 6. Ce nu se testează niciodată, și de ce

Traseele care ating exteriorul real: depunerea la autoritate, transmiterea e-Facturii, plata.

**Se declară ca netestabile**, cu ce se poate testa în locul lor — până unde merge traseul intern, și unde se oprește.

Altfel rămân în aer: nici verificate, nici declarate.

---

# VIII. DE UNDE SE COMPLETEAZĂ

**Pașii** — din cod: ce rută cheamă ce, ce stare pune fiecare.

**Ce se verifică după** — din `PLAN_ARHITECTURA`, Partea IV, plus din ce s-a măsurat.

**Stările** — din schemă și din nomenclatoare.

**Rolurile** — din verificările de drepturi.

**Precondițiile** — din ce eșuează când lipsesc datele.

**Traseele negative** — din ce tratează codul azi, plus ce ar trebui să trateze.

**Ce nu are voie** — din interdicțiile din plan, aplicate la traseu.

Un traseu completat din presupunere e mai rău decât unul lipsă: se verifică ceva care nu există, iar verificarea trece.


---

# IX. COMPLETAT DIN COD — 24.08.2026, pe commit `6d3a414`

Ce urmează **nu e scris din presupunere**: fiecare bloc e extras din sursă și poartă cifra lui. Ce n-a
putut fi extras rămâne marcat, și e enumerat în Partea X ca decizie.

## A. ROLURILE — complet din cod

Măsurat pe **400 de rute HTTP**, din care **378 poartă o gardă** în semnătură:

| gardă | rute | ce înseamnă |
|---|---|---|
| `cere_cabinet` | **242** | orice utilizator autentificat al unui cabinet — fără distincție de rol |
| `cere_context` | 55 | context de cabinet/firmă |
| `cere_rol` | **57** | `admin_firma` **30** · `admin_firma`+`angajat` **19** · `superadmin` **8** |
| `cere_client` | 19 | portalul clientului |
| `cere_api_key` | 5 | integrări |

**Drepturile fine nu sunt roluri.** `poate_pregati` · `poate_valida` · `poate_depune` sunt **coloane
booleene pe `public.users`**, verificate **în corpul rutei** prin `_are_permisiune`, nu în gardă.

**Ce trebuie știut la testare, și e în cod:** `_are_permisiune` întoarce `True` **necondiționat pentru
`superadmin`**, înaintea oricărei citiri din bază. *Patru-ochi verificat cu superadmin nu verifică
patru-ochi* — nu e o precauție, e o ramură scrisă.

## B. STĂRILE ȘI TRANZIȚIILE IMPLEMENTATE

**Coada de declarații are singurul tabel explicit de tranziții din aplicație** (`core/coada_api.py`):

| acțiune | din stare | în stare |
|---|---|---|
| `aproba` | `la_senior` | `aprobata` |
| `respinge` | `la_senior` | `respinsa` |
| `depune` | `aprobata` | `depusa` |

Verificat de `poate_tranzitiona`. **`depusa` nu are nicio ieșire** — e terminală prin construcție, nu
prin regulă scrisă.

**Restul stărilor nu au tabel, ci literale împrăștiate.** Măsurat pe `main.py` + `core/`:

- `status = '…'` → `validata` (46) · `ciorna` (7) · `emisa` (6) · `extras` (5) · `de_verificat` (3) ·
  `aprobat` (3) · `contat` (3) · `ignorat` (2) · `descarcata` (2) · `de_preluat` (2) · `nou` ·
  `respinsa` · `raspuns` · `potrivit`
- `stare = '…'` → `la_senior` (3) · `respinsa` (3) · `noua` (3) · `inchisa` · `prezent` ·
  `fara_token` · `nevalidat` · `deja_trimisa` · `erori` · `aprobata` · `depusa` · `investigatie`

**Două vocabulare sunt declarate ca module** — `core/nomenclator_status_factura.py`,
`core/nomenclator_cm.py`. Restul nu. **Nicăieri nu e scris care tranziție e interzisă.**

## C. PRECONDIȚIILE, ÎN FORMĂ NEGATIVĂ

Codul nu declară ce **trebuie** să existe; declară **ce refuză când lipsește**. Aia se extrage:

- **519** `HTTPException` și **35** `ValueError` ridicate în `main.py`;
- **`PerioadaNeconfirmata`** — excepție proprie, definită în `core/perioada.py`, tratată în
  `core/d112.py` și `core/control_incrucisat.py`. E singura precondiție cu **nume propriu**;
- **coduri de eșec cu nume**, din răspunsurile structurate: `INEXISTENT` (11) · `CAMPURI_LIPSA` (3) ·
  `TEXT_GOL` (3) · `STARE_GRESITA` (3) · `AUTH_ESEC` (3) · `LINII_INCOMPLETE` (2) ·
  `CABINET_SUSPENDAT` (2) · `NUME_EXISTA` (2) · `FARA_PROFIL` · `TVA_LIPSA` · `IC_LIPSA` ·
  `DECONT_INVALID` · `REGIM_INVALID` · `REGIM_LA_PARTIDA_SIMPLA` · `TVA_INCEPUT_INVALID`.

**Ce NU se poate extrage:** *care firmă poate exercita care traseu*. Nu e o proprietate a codului, e
una a datelor — și pe **41 de facturi și 34 de note** (măsurat pe toate cele 17 scheme, 24.08.2026)
majoritatea traseelor n-au ce parcurge.

## D. TRASEELE NEGATIVE TRATATE AZI

Din cele cinci cerute în Partea I, **una singură există**: respingerea de către validator
(`respinge`, cu **motiv obligatoriu**). Codurile de refuz ale cozii sunt `PATRU_OCHI`,
`STARE_GRESITA`, `DEJA_IN_COADA`, `INEXISTENT`.

**Nu există:** autoritatea respinge · datele se schimbă după generare · retragerea.
**Există pe jumătate:** rectificativa — `nr_depunere` versionează depunerile și vederea
`declaratii_depuse_curente` alege maximul, dar **nimic nu leagă o rectificativă de cea pe care o
înlocuiește**, și nimic nu spune că e rectificativă.

## E. MARGINEA EXTERIORULUI — cine iese din aplicație

Măsurat pe `core/`, module care ating exteriorul real:

| modul | prin ce | ce face |
|---|---|---|
| `efactura_send.py` | `requests` → `spv_conector.apel_anaf` | **TRANSMITE e-Factura la ANAF** |
| `spv_receive.py` / `spv_refresh.py` | prin `spv_conector` | primesc mesaje SPV, rotesc token |
| `anaf_api.py`, `monitor_fiscal.py`, `woocommerce.py` | `requests` | interogări externe |
| `curs_bnr.py`, `intracomunitar.py`, `reges_client.py`, `observare.py` | `urlopen` | idem |
| **`duk.py`** | `subprocess` (Java) | **validatorul oficial DUKIntegrator, local** |
| `amef_import.py`, `agenda*.py`, `versiune.py`, `scan_garzi.py` | `subprocess` | unelte locale |

**Corectură la o afirmație anterioară a mea:** spusesem *„aplicația nu transmite nimic la ANAF,
niciodată"*. **Fals.** `efactura_send` transmite. Ce e adevărat e mai îngust: **calea de depunere a
declarațiilor (`coada_api`) n-are niciun apel extern** — „depunerea" acolo înseamnă *„marchează ca
depusă și păstrează ce s-a depus"*.

**Iar DUKIntegrator nu e o margine netestabilă**: rulează local, prin `subprocess`, fără rețea.

## F. PASUL 3 DIN TRASEUL DECLARAȚIEI — există, dar se aruncă

Corectură la a doua afirmație a mea, și e cea care contează. Spusesem că *„calea cozii nu cheamă
niciodată validarea DUK"*. **Fals.** Validatorul e legat în **două** locuri:

- `POST /declaratii/{tip}/valideaza` — rută de sine stătătoare;
- **`GET /coada/{coada_id}/continut`** — rulează DUKIntegrator **de fiecare dată când cineva deschide
  un element din coadă**, și întoarce `stare`, `erori`, `severitate`, `temei`, `limita`.

Docstringul rutei spune **`Read-only`**, și e exact problema: verdictul oficial se **produce**, se
afișează, și **nu se scrie nicăieri**. Coloana care l-ar ține — `declaratii_coada.coerenta` — e
parametru cu default `None` în `adauga_in_coada`, iar singurul apelant nu-l trimite niciodată. Nici
`aproba`, nici `marcheaza_depusa` nu-l consultă.

**Deci pasul 3 nu lipsește din traseu — lipsește din memoria lui.** Iar regula scrisă la „După 3" în
Partea I — *„Un verdict care nu se păstrează nu s-a produs"* — descrie literal starea de azi.


---

# X. CELE NOUĂ TRASEE DIN PARTEA VI, COMPLETATE DIN COD — 25.08.2026, pe `7cc646e`

**Sunt nouă, nu 25.** Partea VI le enumeră într-o singură frază, iar numărătoarea contează fiindcă
„completează cele 25" ar fi însemnat să inventez șaisprezece.

**Cum s-a extras, ca să se poată discuta ce nu prinde.** Pentru fiecare traseu: rutele din `main.py`
(cale, metodă, gardă), modulele din `core/` pe care le cheamă, tabelele în care scriu, stările pe care
le pun, și numărul de refuzuri explicite. **Ce nu s-a găsit nu s-a scris.**

**Extractorul a greșit de două ori, în aceeași direcție — „lipsește" — și amândouă corectate înainte
de a scrie ceva aici:**
1. raporta *„fără gardă"* pentru rutele păzite cu `cere_cabinet`/`cere_context`, fiindcă nu le citea
   din argumentele funcției. **Toate rutele de mai jos sunt păzite**;
2. raporta *„nu scrie nimic"* pentru module care scriu cu tabelă **necalificată** (`UPDATE
   firma_profil`, fără prefix de schemă — conexiunea e deja poziționată). A produs o absență falsă pe
   `firma_profil_api`, prinsă prin citire directă.

*Ambele sunt exact clasa pe care documentul ăsta o interzice: o verificare care trece pentru că
n-a văzut, nu pentru că nu era.*

---

## 1. IMPORTUL DE e-FACTURA — 5 rute

`POST /tenants/{id}/import-efactura` · `GET|POST /tenants/{id}/facturi-primite[/{id}/valideaza|respinge|xml]`
Gardă: `cere_context`. Module: `efactura_import` (citire/calcul), `spv_receive` (scrie
`efactura_primite`), `efactura_send` (scrie `efactura_trimiteri`).

**Scrie în:** `efactura_primite`, `facturi`. **Stări:** `validata`, `respinsa` — plus, pe trimitere:
`fara_token`, `nevalidat`, `deja_trimisa`. **Refuzuri:** 13.

**Singurul traseu care atinge exteriorul real în ambele sensuri:** `spv_receive` primește,
`efactura_send` transmite prin `spv_conector.apel_anaf`. `[de decis]` unde se oprește traseul intern
testabil — vezi Partea VII.3.

## 2. EXTRASUL BANCAR ȘI POTRIVIREA — 9 rute

`POST .../banca/parse-extras` · `GET .../banca/reconciliere` · `POST .../reconciliere/import` ·
`POST .../reconciliere/{linie}/contabilizeaza|ignora|repotriveste` · `POST .../rip/import-banca`.
Gardă: `cere_cabinet`. Module: `banca_parser` (pur), `reconciliere_api`, `rip_api`.

**Scrie în:** `extras_linii` (INSERT + UPDATE), și — prin `reconciliere_api` — **`inregistrari` +
`inregistrari_linii`**. **Stări:** `nou`, `ignorat`, `contat`. **Refuzuri:** 13.

**E una dintre cele patru căi care produc note contabile** (`sursa='banca'`, 6 note măsurate). Aici
lanțul document→notă **există** și e automat pe potrivire, spre deosebire de facturi.

## 3. NIR ȘI RECEPȚIA — 2 rute

`GET|POST /tenants/{id}/stocuri/nir`. Gardă: `cere_cabinet`. Modul: `stocuri_api`.

**Scrie în:** `nir`, `nir_linii`, `inregistrari`, `inregistrari_linii`. **Stare pusă: `validata`.**
**Refuzuri:** 3.

**Notabil, și de confruntat cu R36:** NIR-ul creează nota direct **validată**, sărind peste ciornă.
Toate celelalte căi de creare de notă pun `ciorna`. Nu spun că e greșit — spun că e **o excepție
netratată nicăieri**, iar dacă modelul ales la R36 e „AI propune, omul validează", NIR-ul îl încalcă
deja.

## 4. CASA ȘI REGISTRUL DE CASĂ — 15 rute

`POST|DELETE /tenants/{id}/casa/operatiuni` · `GET .../casa/registru` · fluxul de bonuri
(`/portal/bon`, `/tenants/{id}/bonuri/{id}/aproba|stinge`, imagini) · `POST .../nota-tva-incasare`.
Gardă: `cere_cabinet`. Module: `casa_api`, `tva_incasare` (pur), `ai_client`, `rip_api`.

**Scrie în:** `casa_operatiuni`, `bonuri`, `inregistrari`, `inregistrari_linii`, `facturi`; **și
ȘTERGE** din `casa_operatiuni` și `inregistrari`. **Stări:** `extras`, `de_verificat`, `aprobat`.
**Refuzuri:** 29 — cele mai multe din toate cele nouă.

**Singurul traseu care ȘTERGE înregistrări contabile.** `[de decis]` dacă ștergerea unei note e o
tranziție permisă — vezi Partea VII.1: azi nu e scrisă nicăieri ca interzisă, deci e permisă tăcut.

## 5. INVENTARIEREA — 4 rute

`POST /tenants/{id}/nota-inventariere` · `POST .../nota-obiect-inventar` · `POST .../stocuri/inventar` ·
`GET .../rip/inventar/{an}`. Gardă: `cere_cabinet`. Module: `inventariere` (pur), `stocuri_cv_api`,
`obiecte_inventar` (pur), `d406_active` (pur).

**Scrie în:** `inregistrari`, `inregistrari_linii`, `mijloace_fixe`, și prin `stocuri_cv_api`
**`miscari_stoc`** (5 INSERT) + `articole`. **Stări:** niciuna proprie. **Refuzuri:** 6.

**Trei din patru module sunt de citire.** Inventarierea **calculează** mult și **persistă** doar prin
`stocuri_cv_api`. `[de completat]` dacă rezultatul inventarierii (listele, diferențele) se păstrează
ca artefact — n-am găsit tabelă proprie.

## 6. ÎNCHIDEREA LUNII — 5 rute

`GET .../facturi/perioada` · `POST .../facturi/perioada/confirma|redeschide` ·
`POST|DELETE .../perioade-blocate`. **Gardă: `rol:admin_firma` pe 4 din 5** — singurul traseu din
cele nouă cu gardă de rol pe aproape tot.

**Scrie în:** `perioade_blocate`. Module: `inchidere_luna` (pur), `perioada` (un UPDATE dinamic).
**Refuzuri:** 3.

**Are deja ce lipsește altora:** `PerioadaNeconfirmata` e singura precondiție cu nume propriu din
aplicație, iar `redeschide` există — deci închiderea **e reversibilă prin rută**. `[de decis]` dacă
trebuie să rămână (Partea VII.1 o numește printre cele ireversibile).

## 7. ÎNCHIDEREA ANULUI ȘI SITUAȚIILE FINANCIARE — 4 rute

`POST /tenants/{id}/s1003-valideaza` · `GET .../s1003-xml` · aceleași pentru `s1005`.
Gardă: `cere_cabinet`. Modul: `bilant_api`.

**Scrie în: NIMIC.** Verificat în ambele forme, după corectarea extractorului. **Refuzuri:** 8.

**Aceeași clasă cu verdictul de validare de la R41:** situațiile financiare anuale se **produc** —
XML validat — și **nu se păstrează nicăieri**. Nu intră nici în coadă (nu există `POST /coada` pentru
s1003/s1005), nici în `declaratii_depuse`. Deci artefactul care încheie exercițiul financiar nu are
memorie. **De deschis ca restanță proprie** — nu o scriu aici ca decizie, e o constatare.

## 8. TRECEREA DE REGIM FISCAL — 4 rute

`POST /tenants/{id}/firma-profil/regim-tva` · `GET|POST /tenants/{id}/vector` (POST cu
`rol:admin_firma`) · `GET /migrare/vector`. Module: `firma_profil_api`.

**Scrie în:** `firma_profil` — **4 UPDATE-uri**, plus unul inline în rută
(`UPDATE firma_profil SET platitor_tva = %s`). **Refuzuri:** 2 — cele mai puține din cele nouă.

**Traseul cu cea mai mare consecință fiscală și cele mai puține refuzuri.** O trecere micro↔profit
sau plătitor↔neplătitor schimbă ce declarații se datorează, pe ce perioade, cu ce cote. `[de
completat din cod]` n-am găsit **nicio** verificare de coerență la schimbare: nici că perioada
afectată e deschisă, nici că declarațiile deja depuse pe regimul vechi rămân explicabile.

## 9. PRELUAREA UNEI FIRME — 16 rute

`POST /migrare/incarca|fisier|importa` (importa cu `rol:admin_firma`) · `GET /migrare/{solduri,
plan-conturi, parteneri, salariati, mijloace-fixe, asociati, straturi, status}` ·
`GET /control-fiscal/{id}/audit-preluare`. Module: `migrare_api` (scrie `migrare_status`),
`audit_preluare` (pur).

**Scrie în:** `migrare_status`, plus UPDATE-uri dinamice. **Refuzuri:** 7.

**Cel mai multe rute din cele nouă, și cel mai mult de citire:** paisprezece din șaisprezece sunt
`GET` de previzualizare. `audit_preluare` **nu scrie nimic** — auditul de preluare e un calcul care
se afișează. `[de completat]` dacă verdictul lui se păstrează; după tiparul de la R41 și de la punctul
7, presupunerea implicită ar fi că nu, dar **nu o scriu ca fapt fără s-o măsor**.

---

## Ce NU conțin cele nouă, și e aceeași lipsă la toate

Fiecare traseu de mai sus are **pașii, stările, cine și refuzurile** — extrase. Le lipsesc, la toate,
exact cele două lucruri pe care codul nu le poate da:

- **ce trebuie să fie adevărat după fiecare pas** — codul spune ce s-a schimbat, nu ce *trebuia* să
  se schimbe (Partea VII.5);
- **traseele negative care ar trebui să existe** — se vede doar ce se tratează azi (Partea VII.4).

Amândouă sunt decizii, și sunt scrise ca atare. Un traseu completat fără ele e o hartă a codului, nu
o listă de verificare — util, dar nu suficient.
