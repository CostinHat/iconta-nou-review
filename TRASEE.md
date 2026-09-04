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
   AICI SE TERMINĂ TRASEUL FACTURII.
```

> **CORECTAT 25.08.2026 (Costin: „e o mixtură, nu un traseu unic").** Pasul 4 scria
> *„INTRĂ ÎN: D300 · D394 · e-Factura · jurnalul de vânzări"*. Nu e un pas: e punctul în
> care traseul facturii se termină și încep **alte** trasee, fiecare cu producătorul,
> perioada și refuzurile lui. Măsurat, factura are **20 de consumatori**, nu patru — iar
> *„jurnalul de vânzări"* **nu există**: singura apariție a expresiei în tot codul e un
> placeholder de formular (`static/js/ecrane/validat.js:205`). Lista completă și ce se
> pierde dacă rămâne scris ca traseu unic: **Partea XI.5a**.

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
   AICI SE TERMINĂ TRASEUL NOTEI. Registrul-jurnal E TRASEUL ĂSTA, nu o ieșire a lui.
```

> **CORECTAT 25.08.2026 (Costin: „e o mixtură, nu un traseu unic").** Pasul 5 scria
> *„INTRĂ ÎN: registrul-jurnal · cartea mare · balanță · D406"*. Măsurat, nota are **21 de
> consumatori**, nu patru. Și cele patru nu sunt de același fel: **cartea mare și balanța
> nu sunt trasee, sunt vederi** — `fisa_cont` și `documente_api` le calculează la cerere din
> aceleași `inregistrari_linii` și **nu persistă nimic**; registrul-jurnal e traseul însuși;
> singurul care e cu adevărat traseu propriu e **D406**, fiindcă are XSD, validator, coadă
> și depunere. Lista completă: **Partea XI.5b**.

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

---

# XI. INVENTARUL COMPLET, CELE TREI DECIZII, ȘI CELE DOUĂ MIXTURI — 25.08.2026, pe `3cb6c44`

Partea X a completat cele nouă trasee din Partea VI. Partea asta face trei lucruri pe
care Partea X nu le putea face: **numără traseele**, **răspunde la cele trei decizii din
Partea VII** cu măsurători, și **desface cele două trasee care s-au dovedit mixturi**.

## 0. De ce inventarul e un INSTRUMENT, nu o listă

Până azi, „câte trasee sunt" era o **amintire**. Comanda a numit **25**; Partea X a numit
**nouă**; niciuna dintre cifre nu se putea recalcula, fiindcă nu exista nimic care să
enumere traseele altfel decât citindu-le din proză. *O cifră care nu se poate recalcula nu
e o măsurătoare.*

Deci inventarul trăiește acum în **`scripts/scan_trasee.py`**, iar **`core/test_trasee.py`**
nu-l lasă să îmbătrânească. Instrumentul:

- ține **inventarul declarat** — 35 de trasee, fiecare cu tiparele lui de rută și tabelele lui;
- verifică **acoperirea**: fiecare dintre cele **400 de rute** din `main.py` intră **fie**
  într-un traseu, **fie** într-una din suprafețele declarate ne-documentare (91 de rute:
  autentificare, cabinet, GDPR, suport, administrarea furnizorului). **Orfane: 0.** O rută
  nouă care nu intră nicăieri **pică testul**;
- extrage per traseu, din cod: rutele cu gardă și rol, modulele, tabelele scrise, stările, refuzurile;
- clasifică traseul **din trei fapte măsurate**, nu din impresie;
- cu `--db`, spune **care firmă îl poate exercita azi**.

**Ce nu vede, scris ca să nu se creadă altceva.** Nu vede *ce trebuie să fie adevărat după
un pas* — aia e decizie (Partea VII.5). Nu vede traseele negative care *ar trebui* să
existe, doar pe cele tratate. Iar clasa `MECANIC` spune că traseul **se poate scrie** din
cod, nu că **e corect**.

**Instrumentul a greșit de trei ori până să dea cifrele de mai jos, toate în aceeași
direcție — „lipsește" sau „e altceva" — și toate prinse prin citire directă:**

1. raporta *„fără gardă"* pentru rutele păzite prin argument (`Depends(cere_cabinet)`);
2. raporta *„nu verifică rolul"* pentru rute care îl verifică **în corp** sau printr-un
   **ajutor** (`_cer_admin_cabinet`) — prins citind `/asistenti/{uid}/permisiuni`, care
   arăta nepăzită și nu e;
3. **atribuia ruta de NIR modulului `salarizare`.** Multe rute își importă modulul **în
   corp** (`from core import stocuri_api as _s`), iar `_s` e refolosit în zeci de locuri
   pentru module diferite. Fără harta locală de aliasuri, instrumentul lega ruta de ultimul
   `_s` de la nivel de fișier. **E mai rău decât o absență: e o atribuire falsă**, iar o
   atribuire falsă trece verde.

Toate trei au acum test propriu în `core/test_trasee.py`, plus **calibrare în ambele
direcții** (METODA §22): instrumentul trebuie să **vadă** o rută orfană inventată **și** să
**nu inventeze** una acolo unde nu e.

---

## 1. CÂTE SUNT — și de ce nu 25

**Sunt 35.** Cifra nu e o alegere: e numărul de trasee necesare ca cele 400 de rute să fie
acoperite **fără orfane și fără dublare**, la granularitatea „un document, de la intrare la
ieșire". Comanda a numit 25; Partea X a numit 9. **Nu era greșită niciuna** — se refereau
la altceva: cele 9 erau enumerarea din Partea VI, cele 25 erau o estimare. Cifra care se
poate reface e 35, iar dacă granularitatea trebuie schimbată, se schimbă în `TRASEE` din
instrument și se recalculează totul.

### Cele trei clase, cu criteriul mecanic

| clasă | criteriul, calculat | ce înseamnă practic |
|---|---|---|
| **MANUAL** | traseul cheamă un modul-**margine** — artefactul firmei ajunge la un terț care acționează pe baza lui | traseul intern se scrie din cod, dar **unde se oprește** e decizie (Partea VII.6) |
| **PARȚIAL** | traseul **nu scrie în nicio tabelă** | se produce ceva ce **nu se păstrează nicăieri** — aceeași clasă cu verdictul de la R41 |
| **MECANIC** | restul | pașii, stările, cine și refuzurile se citesc integral din cod |

**Rezultat: MECANIC 27 · PARȚIAL 3 · MANUAL 5.**

**Marginea nu e „modulul cheamă rețeaua".** `requests` nu deosebește o trimitere de o
citire, iar dacă se ia închiderea tranzitivă peste toate modulele de rețea, `observare`
(email) trage după el jumătate din aplicație și clasa nu mai deosebește nimic. Deci lista
de margini e **enumerată, cu motivul lângă fiecare**, iar `NEMARGINI` spune de ce
celelalte module de rețea **nu** sunt margini: `observare` (pleacă o copie, nu artefactul),
`anaf_api` / `curs_bnr` / `intracomunitar` / `monitor_fiscal` (citiri), și **`duk`**, care
rulează local prin `subprocess`, fără rețea.

### Tabelul

| id | clasă | rute | mutante | fără rol | firme | traseu |
|---|---|---|---|---|---|---|
| T01 | MECANIC | 15 | 8 | 1 | 7 | Declarația — generare, validare, coadă, aprobare, depunere |
| T02 | MECANIC | 19 | 13 | 11 | 12 | Factura emisă — creare, contabilizare, ieșiri |
| T03 | MECANIC | 6 | 3 | 0 | 2 | Statul de plată și fluturașul |
| T04 | MECANIC | 5 | 3 | 1 | 4 | Concediul medical |
| T05 | MECANIC | 28 | 24 | **24** | 17 | Nota contabilă — de la document la registrul-jurnal |
| T06 | **MANUAL** | 7 | 4 | 4 | **0** | Importul de e-Factura și transmiterea prin SPV |
| T07 | MECANIC | 7 | 5 | 5 | 2 | Extrasul bancar și potrivirea |
| T08 | MECANIC | 2 | 1 | 1 | **0** | NIR și recepția |
| T09 | MECANIC | 3 | 2 | 2 | 2 | Casa și registrul de casă |
| T10 | MECANIC | 5 | 1 | 1 | ? | Inventarierea |
| T11 | MECANIC | 6 | 4 | 0 | 1 | Închiderea lunii |
| T12 | **PARȚIAL** | 4 | 2 | 2 | ? | Închiderea anului și situațiile financiare |
| T13 | MECANIC | 8 | 4 | 3 | 17 | Trecerea de regim fiscal |
| T14 | MECANIC | 32 | 20 | 10 | 5 | Preluarea unei firme |
| T15 | **MANUAL** | 16 | 11 | 7 | 8 | Salariatul — angajare, contract, adeverință, REGES |
| T16 | MECANIC | 4 | 2 | 1 | **0** | Pontajul |
| T17 | **PARȚIAL** | 2 | 0 | 0 | ? | Plata salariilor — fișierul către bancă |
| T18 | **MANUAL** | 6 | 3 | 2 | 1 | Chitanța și încasarea |
| T19 | MECANIC | 2 | 1 | 1 | **0** | Scadențarul și notificările de scadență |
| T20 | MECANIC | 12 | 7 | 7 | 2 | Mișcarea de stoc — intrare, ieșire, transfer, reclasificare |
| T21 | MECANIC | 9 | 7 | 7 | 1 | Rețeta și producția |
| T22 | MECANIC | 3 | 2 | 2 | 2 | Mijlocul fix și amortizarea |
| T23 | MECANIC | 9 | 5 | 5 | 2 | Bonul de la client — portalul și decontul |
| T24 | MECANIC | 2 | 2 | 2 | ? | Bonul fiscal și raportul Z (AMEF, horeca) |
| T25 | **MANUAL** | 3 | 2 | 2 | ? | Comanda din magazinul online (WooCommerce) |
| T26 | MECANIC | 2 | 1 | 1 | 1 | Registratura |
| T27 | **MANUAL** | 3 | 2 | 2 | **0** | e-Transport |
| T28 | MECANIC | 10 | 5 | 5 | 2 | Operațiunile intracomunitare, VIES și Intrastat |
| T29 | MECANIC | 11 | 10 | 10 | ? | Regimurile speciale de TVA — marjă, aur, agricultori, taxare inversă |
| T30 | MECANIC | 2 | 2 | 2 | ? | Operațiunile în valută |
| T31 | MECANIC | 6 | 4 | 4 | 3 | Completările manuale la o declarație (D300, D301) |
| T32 | MECANIC | 7 | 5 | 5 | **0** | Registrul de încasări și plăți (partida simplă) |
| T33 | **PARȚIAL** | 3 | 0 | 0 | ? | Exportul contabil (SAGA, WinMentor) |
| T34 | MECANIC | 14 | 5 | 5 | 1 | Rapoartele comerciale, centrele de cost, rapoartele salvate |
| T35 | MECANIC | 36 | 15 | 8 | 1 | Pachetul lunar către client și solicitările lui |

**`?` nu înseamnă zero.** Înseamnă că traseul **n-are tabelă proprie**, deci întrebarea
„care firmă îl poate exercita" nu se poate răspunde din date. *Un necunoscut nu se
rotunjește la „știu că nu"* — interdicția 32. Opt trasee sunt în situația asta: T10, T12,
T17, T24, T25, T29, T30, T33. **Patru dintre ele sunt și PARȚIAL sau MANUAL** (T12, T17,
T25, T33) — aceeași cauză: nu persistă nimic. Celelalte patru scriu, dar **în tabelele
altor trasee**: regimurile speciale și valuta produc note contabile, inventarierea și
raportul Z la fel.

---

## 2. DECIZIA 1 — ROLURILE, citite din verificările de drepturi

*Comanda: „cele trei roluri sunt de acord. Dar nu inventa scenarii de test pe cabinete care
nu există. Pentru fiecare pas din trasee: ce rol îl poate face, citit din verificările de
drepturi. Unde codul nu verifică nimic, spune — e mai important decât o matrice corectă."*

### Cele patru forme în care codul verifică un drept

Nu una, patru — iar trei dintre ele nu se văd în semnătura rutei. Cifrele de mai jos sunt
**rute clasificate după PRIMA formă găsită** (o rută poate avea două; se numără o dată):

| formă | unde stă | rute din 400 |
|---|---|---|
| `cere_rol("admin_firma", …)` | în semnătură | **57** |
| comparație pe `ctx["rol"]` sau `_are_permisiune` | în corpul rutei | **21** |
| ajutor care ridică 403 (`_cer_admin_cabinet`) | apel în corp | **18** |
| `cere_client` / `cere_api_key` | în semnătură | 24 |
| **nimic** | — | **280** |

Formele 2 și 3 sunt cele care au produs prima măsurătoare greșită: o rută pazită prin
`_cer_admin_cabinet` arăta nepăzită. `_are_permisiune` apare pe **6** rute — cele trei
tranziții ale cozii (`poate_valida`, `poate_depune`) și cele trei de stat de plată
(`poate_valida`).

### Unde codul NU verifică nimic — cifra care contează

Din **229 de rute care schimbă ceva** (POST/PUT/PATCH/DELETE):

- **48** cer un rol prin gardă;
- **13** îl verifică în corp;
- **9** printr-un ajutor;
- **6** sunt portal de client sau cheie de API;
- **144 cer doar să fii un utilizator autentificat al cabinetului. Niciun rol.**
- restul de **9** sunt public prin construcție (login, activare, resetare de parolă).

**`cere_cabinet` nu e un rol.** Verifică exact două lucruri: că nu ești `client`, și că
cabinetul nu e suspendat. **Un `angajat` și un `admin_firma` sunt același actor pe 144 de
rute care scriu.**

**Unde doare cel mai tare, per traseu:**

- **T05, nota contabilă — 24 din 24 de rute care scriu nu verifică niciun rol.** Toate cele
  optsprezece rute `nota-*`, plus crearea, editarea, ștergerea și validarea din jurnal.
  *Orice utilizator al cabinetului poate crea, valida și șterge o înregistrare contabilă.*
- **T02, factura — 11 din 13.** Crearea și ștergerea cer `admin_firma`/`angajat`; emiterea,
  stornarea, transformarea, numerotarea și trimiterea la SPV nu cer nimic.
- **T29, regimurile speciale de TVA — 10 din 10.**
- **T20/T21, stocul și producția — 7 din 7.**

**Excepțiile, și ele spun ceva:** singurele trei trasee cu rol pe tot ce scrie sunt
**T11 închiderea lunii** (`admin_firma` pe toate cele 4 rute care scriu), **T16 pontajul** (`admin_firma` pe
confirmare) și **T03 statul de plată** (`poate_valida` pe emitere, corecție și motiv).
Adică: *perioada, prezența și statul sunt păzite; contabilitatea nu.*

### Superadmin trece peste tot

`cere_rol` lasă `superadmin` să treacă **înainte de orice verificare**, iar
`_are_permisiune` întoarce `True` **necondiționat** pentru el, înaintea oricărei citiri din
bază. *Patru-ochi verificat cu superadmin nu verifică patru-ochi.* Nu e o precauție — e o
ramură scrisă (`main.py:5743`).

### Ce roluri există AZI, măsurat — și de ce nu se pot inventa scenarii

**12 conturi, în 7 cabinete:**

| rol | conturi | `poate_pregati/valida/depune` |
|---|---|---|
| `superadmin` | 2 | (trec oricum) |
| `admin_firma` | 7 | toți: da/da/da |
| `angajat` | **1** | **nu/nu/nu** |
| `client` | 2 | — |

**Singurul `angajat` din instalare** — `asistent@prisma-cont.test`, cabinetul 1968 — **n-are
nicio firmă atribuită** (nu apare în `public.user_tenants`) și **n-are niciun drept fin**.

**Consecința, și e cifra care contează:** *pe nicio firmă din cele 17 nu se poate exercita
azi un traseu care cere doi oameni.* Patru-ochi are nevoie de **doi validatori activi** în
același cabinet (`coada_api.patru_ochi_posibil`); cabinetul 1968 are **unul**. Restul
cabinetelor au **un singur utilizator**. Nu e o lipsă de scenariu de test — e o lipsă de
actori, și se vede în date: **cele trei elemente din coadă sunt create toate de același
utilizator (1968), iar cel depus a fost și aprobat, și depus, de el.**

---

## 3. DECIZIA 2 — CE NU SE TESTEAZĂ NICIODATĂ, și ce ține locul

*Comanda: „declară-le ca netestabile, cu ce se testează în locul lor: până unde merge
traseul intern și unde se oprește. La e-Factura, dacă există mediu de test, folosește-l."*

**Cinci trasee ating exteriorul. Nu opt, nu două** — cinci, calculate:

### T06 — e-Factura. **Mediul de test EXISTĂ, și e deja implicit.**

`efactura_send.fctel_base(mode)` construiește `https://api.anaf.ro/{prod|test}/FCTEL/rest`,
iar `upload_ubl`, `stare_mesaj`, `descarca`, `lista_mesaje` și `trimite` au toate
**`mediu="test"` ca valoare implicită**. Deci răspunsul la „dacă există mediu de test,
folosește-l" e: **există, și e folosit**.

**Ce blochează totuși testarea live, măsurat:** `public.spv_token` are **0 rânduri** și
`public.spv_cui_acoperit` are **0**. Fără un token OAuth obținut cu certificat calificat,
nici mediul de test nu răspunde. **Deci limita nu e „ANAF-ul e în afara noastră", ci „nu
avem certificat".** Sunt lucruri diferite: primul e permanent, al doilea se rezolvă.

- **Traseul intern testabil se oprește la:** XML-ul UBL generat și validat structural, plus
  rândul din `efactura_trimiteri` cu una din stările `fara_token`, `nevalidat`,
  `deja_trimisa`. Astea se pot proba integral fără rețea.
- **Se declară NETESTAT:** răspunsul ANAF, indexul de încărcare, starea mesajului, descărcarea.
- **Ce se schimbă când apare certificatul:** traseul devine testabil până la capăt **pe
  mediul de test**, fără nicio modificare de cod.

### T27 — e-Transport. **Poarta pe test e deja SCRISĂ în cod.**

`etransport_send` nu are client propriu: trece prin `spv_conector`, cu același token.
Docstringul lui declară deja regula — *„POARTA PRE-TRIMITERE = validare pe TEST
(mediu=test); nu se trimite pe prod nevalidat"* — și numește onest ce nu e dovedit:
formatul exact al răspunsului `upload`/`stareMesaj` e din tiparul ANAF, **nu văzut live**,
deci parsarea e defensivă.

- **Traseul intern se oprește la:** XML-ul UIT generat + garda de timp (declarare cu maximum
  3 zile înainte de mișcare, valabilitate 5 zile național / 15 intracomunitar) + rândul din
  `etransport_trimiteri`.
- **Se declară NETESTAT:** UIT-ul întors de ANAF și starea lui.

### T15 — REGES. Contractul de muncă pleacă la registrul de evidență a muncii.

`reges_client` trimite salariatul prin `urlopen`. `public.reges_chei` = **0 rânduri**,
`reges_mesaje` = **0**. Aceeași structură ca la e-Factura: cheia lipsește, nu calea.

- **Traseul intern se oprește la:** rândul din `reges_mesaje` cu starea lui de trimitere.
- **Se declară NETESTAT:** confirmarea registrului.

### T18 — plata. **Nu e margine. E o absență.**

`GET /public/plata/{ref}` întoarce o pagină al cărei text spune, literal, *„Integrarea cu
procesatorul de plăți urmează. Apăsați pentru a simula plata."* Nu există procesator.

**Și e o rută care merită privită separat:** `POST /public/plata/{ref}/confirma` e
**neautentificată**, **parcurge toate schemele de firme** și marchează factura încasată pe
prima care se potrivește. `ref` e secret și pagina e `noindex`, dar traseul rămâne: *o
cerere fără niciun token schimbă starea unei facturi într-o firmă.*

- **Nu se declară netestabil.** Se declară **neimplementat**, iar ruta de confirmare e o
  restanță proprie.

### T25 — WooCommerce. Margine reală, dar către un terț al clientului, nu către stat.

`woocommerce` citește prin `requests.get` și scrie înapoi în `facturi`. Nicio firmă din cele
17 n-are configurație de magazin.

- **Traseul intern se oprește la:** configurația salvată în `firma_profil` și rezultatul
  sincronizării.
- **Se declară NETESTAT:** răspunsul magazinului.

### Corectură la o afirmație a mea, păstrată fiindcă e utilă

În Partea IX scrisesem că **DUKIntegrator nu e margine**. Rămâne adevărat, și instrumentul
o pune acum în cod: `duk` e în `NEMARGINI`, cu motivul — rulează local prin `subprocess`,
fără rețea. **Validatorul oficial e testabil integral.** Singurul lucru care lipsea era
memoria verdictului, și aia s-a construit la R41.

---

## 4. DECIZIA 3 — PRECONDIȚIILE, pe firmele care există

*Comanda: „pe firmele existente, nu inventa firme noi. Pentru fiecare traseu: care firmă îl
poate exercita azi, și ce lipsește ca să poată fi parcurs. Dacă niciun traseu nu se poate
parcurge pe nicio firmă, aia e cifra care contează."*

Măsurat pe **toate cele 17 firme**, pe **47 de tabele** fiecare, plus tabelele partajate din
`public` care poartă `tenant_id`.

### Cifra care contează

**Din 35 de trasee: 21 au cel puțin o firmă care le poate exercita · 6 nu au niciuna · 8 nu
se pot ști din date** (n-au tabelă proprie).

**Cele șase pe care nicio firmă nu le poate exercita azi:**

| traseu | ce lipsește, exact |
|---|---|
| **T06 e-Factura** | `efactura_primite` = 0 și `efactura_trimiteri` = 0 pe toate cele 17. Plus `spv_token` = 0 |
| **T08 NIR** | `nir` = 0 și `nir_linii` = 0 pe toate cele 17 |
| **T16 Pontajul** | `pontaj` = **0 pe toate cele 17** |
| **T19 Scadențarul** | `notificari_scadenta` = 0 pe toate cele 17 |
| **T27 e-Transport** | `etransport_trimiteri` = 0 pe toate cele 17 |
| **T32 Registrul de încasări și plăți** | `rip_operatiuni` = **0 pe toate cele 17** |

**Două dintre ele contrazic ceva scris.** `pontaj` = 0 peste tot, iar Partea III spune
*„pontajul trebuie să existe — fără el, tichetele se blochează, iar calculul stă pe zile
presupuse"*: deci **cele două state de plată emise — singura firmă care are, `tenant_003` — au fost
calculate fără pontaj**. Iar `rip_operatiuni` = 0 peste tot înseamnă că **partida simplă n-a fost exercitată
niciodată**, deși motorul ei există (`rip_api` + `d212_engine`) — exact datoria numită la
pragul 3 în predare.

### Unde stau datele, pe firme

**Evidența e concentrată în două firme.** `tenant_013` (ALFA MICRO) are rânduri în **26** de
tabele; `tenant_003` (Comert Micro TVA) în **14**. Restul de 15 firme au între **2 și 11**
tabele nevide, iar patru dintre ele (`tenant_006`, `008`, `011`, `012`) au **exact două**:
planul de conturi și profilul.

| ce | total pe toate cele 17 |
|---|---|
| facturi | **41** |
| note contabile (`inregistrari`) | **34** |
| salariați | **24** |
| state de plată emise | **2**, pe o singură firmă |
| declarații depuse | **55**, pe 6 firme |
| elemente în coadă | **3**, toate în cabinetul 1968 |
| pontaje | **0** |
| operațiuni de partidă simplă | **0** |
| NIR-uri | **0** |

### Trei lucruri ieșite din măsurătoare, care nu erau căutate

1. **Un element din coadă aparține unei firme care nu există.** `declaratii_coada.id=2020`
   are `tenant_id = 13245`; în `public.tenants` nu există rândul, iar schema `tenant_13245`
   nu există. Conținutul lui e un D300 al firmei *„Firma Grea Audit SRL"* — care e
   `tenant_017`, id **14769**. Deci o declarație stă în coadă legată de o firmă ștearsă sau
   niciodată creată, și nimic n-o semnalează.
2. **Niciunul dintre cele 3 elemente din coadă n-are verdict păstrat** (`verdict` = `NULL`
   pe toate trei), inclusiv D301-ul deja **depus**. Consecvent cu ce s-a scris la R41: poarta
   e nouă, elementele sunt vechi.
3. **Prima formă a măsurătorii a raportat zece tabele ca „absente pe toate cele 17 firme".
   Nouă dintre cele zece existau.** Trei trăiesc în `public`, partajate, cu `tenant_id`
   (`declaratii_depuse`, `declaratii_coada`, `migrare_status`) — și tocmai de-aia traseul
   declarației arăta „nicio firmă" pe o instalare cu **55 de declarații depuse**. Șase
   există **sub alt nume**: `facturi_linii` e `factura_linii`; `stat_plata` e `state_plata`;
   `perioada` e `perioada_confirmata`; `parteneri` sunt `clienti` + `furnizori`; `scadentar`
   e `notificari_scadenta`; `contracte` e `contracte_sabloane`. Una singură chiar nu există:
   `cote_tva` **nu e tabelă** — verificat, niciun `FROM cote_tva` în `core/`.
   O absență falsă de nouă ori, dintr-un singur motiv: **nume ghicite, necăutate la sursă.**
   De aceea `scripts/trasee_tabele.json` se **regenerează din bază** (`--tabele`), nu se
   scrie de mână.

---

## 5. CELE DOUĂ MIXTURI, DESFĂCUTE

*Comanda: „corectează cele două trasee din TRASEE care s-au dovedit mixturi: factura →
declarație și nota → registru. Erau scrise de mine ca trasee unice și nu sunt."*

Corect, și măsurătoarea arată **de ce**: în amândouă, pasul final scrie *„INTRĂ ÎN: A · B ·
C · D"* — ca și cum ar fi un pas. Nu e un pas. **E punctul în care un traseu se termină și
încep altele**, fiecare cu producătorul lui, perioada lui, refuzurile lui și verdictul lui.

### 5a. Factura NU intră în patru ieșiri. Intră în douăzeci de consumatori.

Partea II scria: *„4. INTRĂ ÎN: D300 · D394 · e-Factura · jurnalul de vânzări"*.

Măsurat — modulele din `core/` care **citesc** `facturi`:

`clienti_api` · `control_fiscal_api` · `control_incrucisat` · `d100` · `d300` ·
`d300_reconciliere` · `d390` · `d390_reconciliere` · `d394` · `d394_reconciliere` ·
`d406` · `efactura_send` · `export_saga` · `facturi_api` · `notificari_scadenta` ·
`plati` · `rapoarte_comerciale_api` · `reconciliere_api` · `scadentar` · `woocommerce`

**Douăzeci, nu patru.** Iar lista veche greșea în ambele direcții:

- **lipseau**: D100, D390, D406, exportul SAGA, reconcilierea bancară, scadențarul,
  controlul încrucișat și fișa de client;
- **„jurnalul de vânzări" nu există.** Căutat la sursă: singura apariție a expresiei în tot
  frontendul e un **placeholder de formular** (`static/js/ecrane/validat.js:205`,
  *„ex: TVA necorelată cu jurnalul de vânzări"*). Nu există modul care să-l producă, nu
  există rută, nu există tabelă. `/tenants/{}/jurnal` e **jurnalul de note contabile**, alt
  lucru; `/tenants/{}/jurnal-marja` e jurnalul regimului marjei, al treilea lucru.

**Deci traseul II se termină la pasul 3** — factura contabilizată — și de acolo pornesc
trasee separate. Cel care se depune e **T01**, iar factura intră în el **prin declarație**,
nu direct.

**Ce se pierde dacă rămâne scris ca traseu unic:** verificarea „factura apare în toate
ieșirile care o cuprind" pare o singură verificare, și sunt douăzeci — cu douăzeci de
perioade și douăzeci de feluri de a fi omisă. *Cazul care a produs regula (`de_preluat`
exclus din D300 și inclus în export) e exact o divergență între doi consumatori, iar un
traseu unic n-avea unde s-o pună.*

### 5b. Nota contabilă NU intră în patru registre. Are douăzeci și unu de consumatori.

Partea V scria: *„5. INTRĂ ÎN: registrul-jurnal · cartea mare · balanță · D406"*.

Măsurat — modulele care **citesc** `inregistrari_linii`:

`bilant_api` · `centre_cost_api` · `control_incrucisat` · `d100` · `d100_reconciliere` ·
`d101` · `d101_reconciliere` · `d205` · `d205_reconciliere` · `d300` · `d300_reconciliere` ·
`d406` · `d406_reconciliere` · `documente_api` · `echilibru_perioada` · `fisa_cont` ·
`jurnal_api` · `pachete_api` · `rapoarte_comerciale_api` · `reconciliere_api` · `stocuri_api`

**Douăzeci și unu.** Și aici lista veche greșea în ambele direcții:

- **lipseau**: D100, D101, D205, situațiile financiare (`bilant_api`), fișa de cont,
  echilibrul perioadei, centrele de cost, pachetul lunar către client;
- **„cartea mare" și „balanța" nu sunt trasee, sunt vederi.** `fisa_cont` și
  `documente_api` le calculează **la cerere**, din aceleași `inregistrari_linii`, și **nu
  persistă nimic**. Un registru care nu se păstrează nu are traseu — are o rută.

**Singurul dintre cele patru care e cu adevărat un traseu propriu e D406**, fiindcă are
XSD, validator, coadă și depunere. Registrul-jurnal e **T05 însuși**, nu o ieșire a lui.

**Ce se pierde dacă rămâne scris ca traseu unic:** cele patru „ieșiri" par egale, și nu
sunt. Trei sunt calcule reproducibile oricând; una pleacă la ANAF și nu se mai poate
retrage. *Regula „nota poartă documentul justificativ" contează pentru toate patru, dar
consecința unei note fără document e diferită într-o vedere și într-o declarație depusă.*

---

## 6. CELE CINCI TRASEE MANUALE, SCRISE — cu ce am citit ca să le scriu

*Comanda: „începe cu cele care ating o ieșire care se depune, și spune la fiecare ce ai
citit ca să-l scrii."*

Trei din cinci ating o ieșire care se depune: **T06** (factura, la ANAF), **T27** (UIT-ul,
la ANAF), **T15** (contractul, la REGES). Cu ele încep. **T18** și **T25** nu depun nimic.

### T06 — e-Factura

```
1. FACTURA EXISTĂ ȘI E COMPLETĂ  (cod fiscal de partener, linii, cote)
      ↓
2. GENERARE UBL          efactura_send.construieste  →  XML CIUS-RO
      ↓
3. VALIDARE DE STRUCTURĂ  fctel_validare_url("FACT1")  — fără token
      ↓
4. TOKEN SPV            spv_token pentru CIF-ul emitentului
      ↓  lipsă → stare `fara_token`, traseul se OPREȘTE aici
5. UPLOAD  mediu=test    api.anaf.ro/test/FCTEL/rest/upload
      ↓  ── MARGINEA. Ce urmează nu se testează. ──
6. INDEX DE ÎNCĂRCARE
      ↓
7. STARE MESAJ → descărcare confirmare
```

**Ce am citit:** `core/efactura_send.py` (`fctel_base`, `fctel_validare_url`,
`CUSTOMIZATION_ID`, `upload_ubl`, `stare_mesaj`, `descarca`, `lista_mesaje`, `trimite`),
`core/spv_conector.py` (URL-urile OAuth, `apel_anaf`), `core/efactura_import.py`, rutele
`/tenants/{}/import-efactura` și `/tenants/{}/facturi/{}/trimite-spv` din `main.py`, plus
numărătoarea din `public.spv_token` și `efactura_trimiteri`.

**Stări:** `fara_token` · `nevalidat` · `deja_trimisa` (la trimitere); `validata` ·
`respinsa` (la primire). **Refuzuri: 27.**
**Cine:** 4 rute care scriu, **niciuna nu verifică vreun rol**.
**Precondiție care lipsește azi:** tokenul. Fără el traseul se oprește la pasul 4, pe toate
cele 17 firme.

### T27 — e-Transport

```
1. MIȘCAREA DE BUNURI E CUNOSCUTĂ  (transport, cantități, parteneri)
      ↓
2. GENERARE XML UIT
      ↓
3. GARDA DE TIMP   declarare max 3 zile ÎNAINTE de mișcare
      ↓
4. VALIDARE PE MEDIUL DE TEST   — scrisă ca poartă obligatorie în cod
      ↓
5. UPLOAD prin spv_conector, cu tokenul SPV (același ca la e-Factura)
      ↓  ── MARGINEA ──
6. UIT ÎNTORS DE ANAF, valabil 5 zile (național) / 15 (intracomunitar)
      ↓
7. FOLOSIREA UIT-ULUI DUPĂ EXPIRARE — blocată
```

**Ce am citit:** `core/etransport_send.py` (docstringul care declară poarta pe test și
limita de parsare, garda de timp), `core/etransport.py`, rutele `/tenants/{}/etransport-xml`,
`/tenants/{}/etransport/trimite`, `/tenants/{}/etransport/trimiteri`.

**Scrie în:** `etransport_trimiteri`. **Refuzuri: 11.** **Cine:** 2 rute care scriu, niciun rol.
**Notabil:** e **singurul traseu din cele cinci manuale care are poarta pe mediul de test
scrisă explicit în cod**, înaintea trimiterii pe producție. Ce s-a decis aici acum e ce
lipsește la celelalte patru.

### T15 — Salariatul, contractul și REGES

```
1. SALARIAT CREAT          salariati_api  →  salariati + salariu_istoric
      ↓
2. CONTRACT GENERAT        contracte_api, din contracte_sabloane
      ↓
3. CHEIE REGES CONFIGURATĂ  reges_chei
      ↓  lipsă → traseul se OPREȘTE aici
4. TRIMITERE SALARIAT      reges_client  →  reges_mesaje
      ↓  ── MARGINEA ──
5. CONFIRMARE DIN REGISTRU  (reges-poll)
```

**Ce am citit:** `core/salariati_api.py`, `core/contracte_api.py`, `core/reges_client.py`,
`core/adeverinta.py`, `core/beneficii_api.py`, rutele `/tenants/{}/salariati*`,
`/tenants/{}/contracte/*`, `/tenants/{}/reges-{config,trimite-salariat,poll}`.

**Scrie în:** `salariati`, `salariu_istoric`, `contracte_sabloane`, `beneficii_lunare`,
`reges_chei`, `reges_mesaje` — și **`DELETE` pe `pontaj` și `salariu_istoric`** la ștergerea
unui salariat. **Refuzuri: 38.** **Cine:** 11 rute care scriu, din care **7 nu verifică
niciun rol**; crearea/modificarea/ștergerea salariatului cer `admin_firma`/`angajat`.
**Firme: 8** au salariați. **`contracte_sabloane` = 0 pe toate cele 17** — deci pasul 2 n-a
fost parcurs niciodată.

### T18 — Chitanța și încasarea

```
1. FACTURĂ EMISĂ, NEÎNCASATĂ
      ↓
2a. CHITANȚĂ pe hârtie     chitante  →  casa_operatiuni + notă contabilă
2b. LINK DE PLATĂ          plati.genereaza_link  →  ref secret
      ↓
3. CONFIRMARE              POST /public/plata/{ref}/confirma
      ↓
4. FACTURA MARCATĂ ÎNCASATĂ
```

**Ce am citit:** `core/chitante.py`, `core/plati.py`, ruta `/public/plata/{ref}` (textul
paginii, care declară integrarea ca nefăcută) și `/public/plata/{ref}/confirma`.

**Nu e o margine — e o absență.** Pasul 3 nu iese nicăieri: pagina e un formular care
apelează propria aplicație. **Restanță proprie:** ruta de confirmare e neautentificată și
caută `ref` prin **toate schemele de firme**. **Firme: 1** (`tenant_013`, 2 chitanțe).

### T25 — Comanda din magazinul online

```
1. CONFIGURAȚIE MAGAZIN      firma_profil
      ↓
2. SINCRONIZARE              woocommerce  →  requests.get
      ↓  ── MARGINEA ──
3. COMENZI CITITE → facturi
```

**Ce am citit:** `core/woocommerce.py`, rutele `/tenants/{}/woocommerce/{config,sincronizeaza}`.
**Refuzuri: 1** — cele mai puține din toate cele 35 de trasee. **Nicio firmă configurată.**

---

## 7. CELE TREI TRASEE PARȚIALE — ce se produce și nu se păstrează

Toate trei sunt aceeași clasă cu verdictul de la R41: **artefactul se produce, se afișează
sau se descarcă, și nu rămâne.**

- **T12 — situațiile financiare (S1003, S1005).** 4 rute, `bilant_api` **nu scrie nimic**.
  Nu intră nici în coadă (nu există `POST /coada` pentru s1003/s1005), nici în
  `declaratii_depuse`. *Artefactul care încheie exercițiul financiar n-are memorie.*
- **T17 — plata salariilor.** 2 rute, amândouă `GET`. Fișierul către bancă se generează și
  se descarcă. Nu se consemnează **că** s-a generat, **pentru ce lună**, **de cine**. Deci
  „salariile s-au plătit" nu e o stare a aplicației.
- **T33 — exportul contabil (SAGA, WinMentor).** 3 rute, toate `GET`, zero scrieri. Nu se
  știe ce s-a exportat și când — iar la o preluare inversă (firma pleacă) asta e exact
  întrebarea.

**Împreună cu R41 și cu auditul de preluare (`audit_preluare` nu scrie nimic), sunt cinci
instanțe ale aceleiași clase.** Merită o restanță proprie, nu cinci.

---

## 8. CE RĂMÂNE, NUMIT

- **Ce trebuie să fie adevărat după fiecare pas** — nescris, pentru toate cele 35. Nu se
  poate extrage din cod (Partea VII.5). E singura parte care face din inventar o listă de
  verificare, nu o hartă.
- **Traseele negative care ar trebui să existe** — se vede doar ce se tratează azi.
- **Tranzițiile interzise** — un singur tabel explicit în toată aplicația (`coada_api`).
  Restul stărilor sunt literale împrăștiate. Rămâne decizie.

---

# XII. CELE 35 DE TRASEE, SCRISE — generat din cod, 25.08.2026

Partea XI le numără și le clasifică. Partea asta le **scrie**: pentru fiecare traseu —
pașii (rutele, în ordine, cu garda și rolul cerut), modulele, tabelele în care scrie,
stările pe care le pune, numărul de refuzuri explicite, marginea dacă are una, și
**care firmă îl poate exercita azi**.

**De ce e GENERAT, și nu scris de mână.** Treizeci și cinci de trasee scrise de mână ar
fi **al doilea loc în care trăiește starea**, iar al doilea loc se învechește — regula e
chiar din `PLAN_LUCRU.md` („Unde stau: nu într-un fișier separat"). Așa, documentul
poartă conținutul, iar `core/test_trasee.py` verifică să fie **identic** cu ce produce
`scripts/scan_trasee.py --md`. Doc și cod nu pot diverge tăcut. O corectură se face în
inventar și se regenerează; editarea cu mâna a blocului **pică testul**.

**Ce NU e aici, și nu din lene:** *ce trebuie să fie adevărat după fiecare pas* și
*traseele negative care ar trebui să existe*. Codul spune ce s-a schimbat, nu ce
**trebuia** să se schimbe. Amândouă sunt decizii (Partea VII.4 și VII.5), iar un traseu
completat din presupunere e mai rău decât unul lipsă.

**Numerele de firme vin din `scripts/trasee_firme.json`**, regenerat din bază cu
`scripts/scan_trasee.py --firme`. Trăiesc ca fișier tocmai ca redarea să fie
recalculabilă fără bază de date — altfel testul care compară n-ar putea rula la poartă.
<!-- trasee:auto:start -->

*Blocul de mai jos e **generat** cu `scripts/scan_trasee.py --md`, iar
`core/test_trasee.py` verifica sa fie identic cu ce genereaza instrumentul. Nu se
editeaza cu mana: o corectura se face in inventar si se regenereaza.*

### T01 — Declarația — generare, validare, coadă, aprobare, depunere

**Clasa:** MECANIC · **rute:** 16 (din care schimba date: 8) · **refuzuri explicite:** 44

**Cine:** rol cerut: `admin_firma`, `angajat` · drept fin: `poate_depune`, `poate_valida`. **Rute care schimba date fara nicio verificare de rol: 1 din 8.**

**Pasii, din cod:**

- `GET /coada` — garda `cere_cabinet`
- `POST /coada` — garda `cere_rol` rol:admin_firma,angajat
- `POST /coada/{coada_id}/aproba` — garda `cere_rol` rol:admin_firma,angajat drept:poate_valida
- `GET /coada/{coada_id}/continut` — garda `cere_cabinet`
- `POST /coada/{coada_id}/depune` — garda `cere_rol` rol:admin_firma drept:poate_depune
- `POST /coada/{coada_id}/respinge` — garda `cere_rol` rol:admin_firma,angajat drept:poate_valida
- `GET /control-fiscal` — garda `cere_cabinet`
- `GET /control-fiscal/{tenant_id}` — garda `cere_cabinet`
- `GET /declaratii/tipuri` — garda `cere_cabinet`
- `POST /declaratii/{tip}` — garda `cere_rol` rol:admin_firma,angajat
- `POST /declaratii/{tip}/valideaza` — garda `cere_rol` rol:admin_firma,angajat
- `GET /firme/{tenant_id}/verificari` — garda `cere_cabinet`
- `GET /supervizor` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/istoric-declaratii-import` — garda `cere_rol` rol:admin_firma
- `POST /tenants/{tenant_id}/istoric-declaratii-import/incarca` — garda `cere_cabinet`
- `GET /termene` — garda `cere_cabinet`

**Module:** `afirmatii`, `coada_api`, `control_fiscal_api`, `d390`, `declaratii_api`, `declaratii_componente`, `duk`, `istoric_declaratii_import_api`, `migrare_api`, `supervizor`, `termene_api`

**Scrie in:** `declaratii_coada` (INSERT/UPDATE) · `declaratii_depuse` (DELETE/INSERT) · `migrare_status` (INSERT) · `supervizor_confirmari` (INSERT)

**Stari puse:** `aprobata`, `depusa`, `descarcata`, `ok`, `respinsa`

**Firme care il pot exercita azi: 7** — `tenant_003`, `tenant_005`, `tenant_006`, `tenant_013`, `tenant_014`, `tenant_015`, `tenant_016`

### T02 — Factura emisă — creare, contabilizare, ieșiri

**Clasa:** MECANIC · **rute:** 20 (din care schimba date: 14) · **refuzuri explicite:** 72

**Cine:** rol cerut: `admin_firma`. **Rute care schimba date fara nicio verificare de rol: 5 din 14.**

**Pasii, din cod:**

- `GET /api/v1/firme/{tenant_id}/facturi` — garda `cere_api_key`
- `POST /api/v1/firme/{tenant_id}/facturi` — garda `cere_api_key`
- `GET /tenants/{tenant_id}/facturi` — garda `cere_context`
- `POST /tenants/{tenant_id}/facturi` — garda `cere_rol` rol:admin_firma
- `GET /tenants/{tenant_id}/facturi-recurente` — garda `cere_context`
- `POST /tenants/{tenant_id}/facturi-recurente` — garda `cere_context`
- `DELETE /tenants/{tenant_id}/facturi-recurente/{sid}` — garda `cere_context`
- `PUT /tenants/{tenant_id}/facturi-recurente/{sid}` — garda `cere_context`
- `POST /tenants/{tenant_id}/facturi/emite` — garda `cere_rol` rol:admin_firma
- `GET /tenants/{tenant_id}/facturi/numerotare` — garda `cere_context`
- `PUT /tenants/{tenant_id}/facturi/numerotare` — garda `cere_rol` rol:admin_firma
- `GET /tenants/{tenant_id}/facturi/{factura_id:int}` — garda `cere_context`
- `DELETE /tenants/{tenant_id}/facturi/{factura_id}` — garda `cere_rol` rol:admin_firma
- `POST /tenants/{tenant_id}/facturi/{factura_id}/contabilizeaza` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/facturi/{factura_id}/email` — garda `cere_rol` rol:admin_firma
- `PUT /tenants/{tenant_id}/facturi/{factura_id}/notificare` — garda `cere_rol` rol:admin_firma
- `GET /tenants/{tenant_id}/facturi/{factura_id}/pdf` — garda `cere_context`
- `POST /tenants/{tenant_id}/facturi/{factura_id}/recunoaste` — garda `cere_rol` rol:admin_firma
- `POST /tenants/{tenant_id}/facturi/{factura_id}/storno` — garda `cere_rol` rol:admin_firma
- `POST /tenants/{tenant_id}/facturi/{factura_id}/transforma` — garda `cere_rol` rol:admin_firma

**Module:** `contare_facturi`, `factura_pdf`, `facturi_api`, `facturi_recurente`, `firma_profil_api`, `observare`, `scadentar`, `stocuri_cv_api`

**Scrie in:** `articole` (INSERT/UPDATE) · `factura_linii` (INSERT) · `facturi` (DELETE/INSERT/UPDATE) · `facturi_recurente` (DELETE/INSERT/UPDATE) · `firma_profil` (UPDATE) · `inregistrari` (INSERT) · `inregistrari_linii` (INSERT) · `miscari_stoc` (INSERT)

**Firme care il pot exercita azi: 12** — `tenant_001`, `tenant_002`, `tenant_003`, `tenant_004`, `tenant_005`, `tenant_007`, `tenant_009`, `tenant_010`, `tenant_013`, `tenant_014`, `tenant_016`, `tenant_017`

### T03 — Statul de plată și fluturașul

**Clasa:** MECANIC · **rute:** 8 (din care schimba date: 5) · **refuzuri explicite:** 21

**Cine:** rol cerut: `admin_firma` · drept fin: `poate_valida`. **Rute care schimba date fara nicio verificare de rol: 2 din 5.**

**Pasii, din cod:**

- `GET /tenants/{tenant_id}/fluturas/{salariat_id}` — garda `cere_rol` rol:admin_firma
- `POST /tenants/{tenant_id}/salarii-contare` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/salarii-contare/propunere` — garda `cere_cabinet`
- `GET /tenants/{tenant_id}/stat-plata` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/stat-plata/corectie` — garda `cere_cabinet` drept:poate_valida
- `GET /tenants/{tenant_id}/stat-plata/emis` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/stat-plata/emite` — garda `cere_rol` rol:admin_firma drept:poate_valida
- `POST /tenants/{tenant_id}/stat-plata/motiv` — garda `cere_cabinet` drept:poate_valida

**Module:** `salarii_contare`, `stat_plata_api`, `stat_plata_emis`

**Scrie in:** `inregistrari` (INSERT) · `inregistrari_linii` (INSERT) · `state_plata` (INSERT/UPDATE)

**Firme care il pot exercita azi: 2** — `tenant_001`, `tenant_003`

### T04 — Concediul medical

**Clasa:** MECANIC · **rute:** 5 (din care schimba date: 3) · **refuzuri explicite:** 33

**Cine:** rol cerut: `admin_firma`, `angajat`. **Rute care schimba date fara nicio verificare de rol: 1 din 3.**

**Pasii, din cod:**

- `POST /tenants/{tenant_id}/calcul-cm` — garda `cere_cabinet`
- `GET /tenants/{tenant_id}/concedii/coduri` — garda `cere_cabinet`
- `GET /tenants/{tenant_id}/salariati/{salariat_id}/concedii` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/salariati/{salariat_id}/concedii` — garda `cere_rol` rol:admin_firma,angajat
- `DELETE /tenants/{tenant_id}/salariati/{salariat_id}/concedii/{cm_id}` — garda `cere_rol` rol:admin_firma,angajat

**Module:** `baza_cm`, `coduri_cm_api`, `salariati_api`, `salarizare`, `scadente`

**Scrie in:** `concedii_medicale` (DELETE/INSERT/UPDATE) · `pontaj` (DELETE) · `salariati` (DELETE/INSERT/UPDATE) · `salariu_istoric` (DELETE)

**Firme care il pot exercita azi: 4** — `tenant_001`, `tenant_013`, `tenant_014`, `tenant_017`

### T05 — Nota contabilă — de la document la registrul-jurnal

**Clasa:** MECANIC · **rute:** 34 (din care schimba date: 26) · **refuzuri explicite:** 185

**Cine:** rol cerut: `admin_firma`. **Rute care schimba date fara nicio verificare de rol: 23 din 26.**

**Pasii, din cod:**

- `GET /api/v1/firme/{tenant_id}/balanta` — garda `cere_api_key`
- `GET /tenants/{tenant_id}/balanta` — garda `cere_cabinet`
- `GET /tenants/{tenant_id}/documente/balanta` — garda `cere_cabinet`
- `GET /tenants/{tenant_id}/fisa-cont` — garda `cere_cabinet`
- `GET /tenants/{tenant_id}/jurnal` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/jurnal` — garda `cere_cabinet`
- `DELETE /tenants/{tenant_id}/jurnal/{nota_id}` — garda `cere_cabinet`
- `PUT /tenants/{tenant_id}/jurnal/{nota_id}` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/jurnal/{nota_id}/dezleaga` — garda `cere_rol` rol:admin_firma
- `POST /tenants/{tenant_id}/jurnal/{nota_id}/valideaza` — garda `cere_rol` rol:admin_firma
- `POST /tenants/{tenant_id}/nota-asociati` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/nota-avans` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/nota-bacsis` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/nota-chirie` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/nota-contract-special` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/nota-credit` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/nota-decont-deplasare` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/nota-inventariere` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/nota-leasing` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/nota-lichidare` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/nota-obiect-inventar` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/nota-ong` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/nota-perisabilitati` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/nota-productie` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/nota-provizion` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/nota-sgr` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/nota-sponsorizare` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/nota-subventie` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/nota-tva-incasare` — garda `cere_cabinet`
- `GET /tenants/{tenant_id}/plan-conturi` — garda `cere_context`
- `POST /tenants/{tenant_id}/plan-conturi` — garda `cere_rol` rol:admin_firma
- `GET /tenants/{tenant_id}/registru-inventar` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/registru-inventar` — garda `cere_cabinet`
- `GET /tenants/{tenant_id}/registru-inventar/propunere` — garda `cere_cabinet`

**Module:** `afirmatii`, `avansuri`, `bacsis`, `comodat_chirii`, `cont_valid`, `contare_facturi`, `contracte_speciale`, `credite`, `d406_active`, `decontari_asociati`, `deconturi`, `documente_api`, `fisa_cont`, `inventariere`, `jurnal_api`, `leasing`, `lichidare`, `obiecte_inventar`, `ong`, `perisabilitati`, `productie`, `provizioane`, `registru_inventar`, `sgr`, `sponsorizari`, `subventii`, `tenant_provisioning`, `tva_incasare`

**Scrie in:** `ai_corectii` (INSERT) · `audit_log` (INSERT) · `casa_operatiuni` (DELETE) · `extras_linii` (UPDATE) · `firma_profil` (INSERT/UPDATE) · `inregistrari` (DELETE/INSERT/UPDATE) · `inregistrari_linii` (DELETE/INSERT) · `mijloace_fixe` (INSERT/UPDATE) · `plan_conturi` (INSERT) · `registru_inventar` (INSERT) · `tenants` (INSERT/UPDATE) · `user_tenants` (INSERT)

**Stari puse:** `contat`, `potrivit`, `validata`

**Firme care il pot exercita azi: 17** — `tenant_001`, `tenant_002`, `tenant_003`, `tenant_004`, `tenant_005`, `tenant_006`, `tenant_007`, `tenant_008`, `tenant_009`, `tenant_010`, `tenant_011`, `tenant_012`, `tenant_013`, `tenant_014`, `tenant_015`, `tenant_016`, `tenant_017`

### T06 — Importul de e-Factura și transmiterea prin SPV

**Clasa:** MANUAL · **rute:** 7 (din care schimba date: 4) · **refuzuri explicite:** 28

**Cine:** rol cerut: `admin_firma`. **Rute care schimba date fara nicio verificare de rol: 2 din 4.**

**Pasii, din cod:**

- `GET /tenants/{tenant_id}/facturi-primite` — garda `cere_context`
- `POST /tenants/{tenant_id}/facturi-primite/{primita_id}/respinge` — garda `cere_context`
- `POST /tenants/{tenant_id}/facturi-primite/{primita_id}/valideaza` — garda `cere_rol` rol:admin_firma
- `GET /tenants/{tenant_id}/facturi-primite/{primita_id}/xml` — garda `cere_context`
- `POST /tenants/{tenant_id}/facturi/{factura_id}/trimite-spv` — garda `cere_rol` rol:admin_firma
- `POST /tenants/{tenant_id}/import-efactura` — garda `cere_cabinet`
- `GET /tenants/{tenant_id}/trimiteri-spv` — garda `cere_context`

**Module:** `afirmatii`, `contare_facturi`, `efactura_import`, `efactura_send`, `spv_rute`

**Scrie in:** `efactura_primite` (UPDATE) · `efactura_trimiteri` (INSERT/UPDATE) · `facturi` (UPDATE)

**Margine:** `efactura_send` (transmite factura firmei la ANAF (SPV))

**Firme care il pot exercita azi: NICIUNA.**

### T07 — Extrasul bancar și potrivirea

**Clasa:** MECANIC · **rute:** 7 (din care schimba date: 5) · **refuzuri explicite:** 20

**Cine:** nicio verificare de rol pe tot traseul — orice utilizator autentificat al cabinetului. **5 din 5 rute care schimba date.**

**Pasii, din cod:**

- `POST /tenants/{tenant_id}/banca/parse-extras` — garda `cere_cabinet`
- `GET /tenants/{tenant_id}/banca/reconciliere` — garda `cere_cabinet`
- `GET /tenants/{tenant_id}/banca/reconciliere/facturi-deschise` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/banca/reconciliere/import` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/banca/reconciliere/{linie_id}/conteaza` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/banca/reconciliere/{linie_id}/ignora` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/banca/reconciliere/{linie_id}/reactiveaza` — garda `cere_cabinet`

**Module:** `banca`, `banca_parser`, `reconciliere_api`

**Scrie in:** `extras_linii` (INSERT/UPDATE) · `inregistrari` (INSERT) · `inregistrari_linii` (INSERT)

**Stari puse:** `contat`

**Firme care il pot exercita azi: 2** — `tenant_003`, `tenant_013`

### T08 — NIR și recepția

**Clasa:** MECANIC · **rute:** 2 (din care schimba date: 1) · **refuzuri explicite:** 4

**Cine:** nicio verificare de rol pe tot traseul — orice utilizator autentificat al cabinetului. **1 din 1 rute care schimba date.**

**Pasii, din cod:**

- `GET /tenants/{tenant_id}/stocuri/nir` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/stocuri/nir` — garda `cere_cabinet`

**Module:** `stocuri_api`

**Scrie in:** `inregistrari` (INSERT) · `inregistrari_linii` (INSERT) · `nir` (INSERT) · `nir_linii` (INSERT)

**Stari puse:** `validata`

**Firme care il pot exercita azi: NICIUNA.**

### T09 — Casa și registrul de casă

**Clasa:** MECANIC · **rute:** 3 (din care schimba date: 2) · **refuzuri explicite:** 6

**Cine:** nicio verificare de rol pe tot traseul — orice utilizator autentificat al cabinetului. **2 din 2 rute care schimba date.**

**Pasii, din cod:**

- `POST /tenants/{tenant_id}/casa/operatiuni` — garda `cere_cabinet`
- `DELETE /tenants/{tenant_id}/casa/operatiuni/{op_id}` — garda `cere_cabinet`
- `GET /tenants/{tenant_id}/casa/registru` — garda `cere_cabinet`

**Module:** `casa_api`

**Scrie in:** `casa_operatiuni` (DELETE/INSERT) · `inregistrari` (DELETE/INSERT) · `inregistrari_linii` (INSERT)

**Firme care il pot exercita azi: 2** — `tenant_003`, `tenant_013`

### T10 — Inventarierea

**Clasa:** MECANIC · **rute:** 5 (din care schimba date: 1) · **refuzuri explicite:** 22

**Cine:** nicio verificare de rol pe tot traseul — orice utilizator autentificat al cabinetului. **1 din 1 rute care schimba date.**

**Pasii, din cod:**

- `GET /tenants/{tenant_id}/d406-active` — garda `cere_cabinet`
- `GET /tenants/{tenant_id}/d406-stocuri` — garda `cere_cabinet`
- `GET /tenants/{tenant_id}/rip/inventar/{an}` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/stocuri/inventar` — garda `cere_cabinet`
- `GET /tenants/{tenant_id}/verificare-stocuri` — garda `cere_cabinet`

**Module:** `d406_active`, `d406_stocuri`, `rip_api`, `stocuri_cv`, `stocuri_cv_api`

**Scrie in:** `articole` (INSERT/UPDATE) · `inregistrari` (INSERT) · `inregistrari_linii` (INSERT) · `miscari_stoc` (INSERT) · `rip_operatiuni` (DELETE/INSERT/UPDATE)

**Stari puse:** `ciorna`, `validata`

**Firme care il pot exercita azi:** *nu se poate sti din date* — traseul n-are tabela proprie.

### T11 — Închiderea lunii

**Clasa:** MECANIC · **rute:** 7 (din care schimba date: 4) · **refuzuri explicite:** 9

**Cine:** rol cerut: `admin_firma`. **Rute care schimba date fara nicio verificare de rol: 0 din 4.**

**Pasii, din cod:**

- `GET /tenants/{tenant_id}/facturi/perioada` — garda `cere_context`
- `POST /tenants/{tenant_id}/facturi/perioada/confirma` — garda `cere_rol` rol:admin_firma
- `POST /tenants/{tenant_id}/facturi/perioada/redeschide` — garda `cere_rol` rol:admin_firma
- `DELETE /tenants/{tenant_id}/perioade-blocate` — garda `cere_rol` rol:admin_firma
- `GET /tenants/{tenant_id}/perioade-blocate` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/perioade-blocate` — garda `cere_rol` rol:admin_firma
- `GET /tenants/{tenant_id}/perioade-blocate/istoric` — garda `cere_cabinet`

**Module:** `afirmatii`, `inchidere_luna`, `migrare_inchideri`

**Scrie in:** `perioade_blocate` (DELETE/INSERT) · `perioade_inchideri` (INSERT)

**Firme care il pot exercita azi: 1** — `tenant_001`

### T12 — Închiderea anului și situațiile financiare

**Clasa:** MECANIC · **rute:** 5 (din care schimba date: 2) · **refuzuri explicite:** 13

**Cine:** nicio verificare de rol pe tot traseul — orice utilizator autentificat al cabinetului. **2 din 2 rute care schimba date.**

**Pasii, din cod:**

- `GET /tenants/{tenant_id}/categorie-marime` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/s1003-valideaza` — garda `cere_cabinet`
- `GET /tenants/{tenant_id}/s1003-xml` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/s1005-valideaza` — garda `cere_cabinet`
- `GET /tenants/{tenant_id}/s1005-xml` — garda `cere_cabinet`

**Module:** `artefacte`, `bilant_api`, `categorie_marime`, `duk`

**Scrie in:** `artefacte_produse` (INSERT)

**Stari puse:** `validata`

**Firme care il pot exercita azi:** *nu se poate sti din date* — traseul n-are tabela proprie.

### T13 — Trecerea de regim fiscal

**Clasa:** MECANIC · **rute:** 8 (din care schimba date: 4) · **refuzuri explicite:** 13

**Cine:** rol cerut: `admin_firma`. **Rute care schimba date fara nicio verificare de rol: 2 din 4.**

**Pasii, din cod:**

- `GET /migrare/vector` — garda `cere_cabinet`
- `GET /tenants/{tenant_id}/firma-profil` — garda `cere_context`
- `GET /tenants/{tenant_id}/firma-profil/date` — garda `cere_context`
- `POST /tenants/{tenant_id}/firma-profil/date` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/firma-profil/model` — garda `cere_context`
- `POST /tenants/{tenant_id}/firma-profil/regim-tva` — garda `cere_rol` rol:admin_firma
- `GET /tenants/{tenant_id}/vector` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/vector` — garda `cere_rol` rol:admin_firma

**Module:** `firma_profil_api`, `migrare_api`, `vector_fiscal_api`

**Scrie in:** `firma_profil` (INSERT/UPDATE) · `migrare_status` (INSERT)

**Firme care il pot exercita azi: 17** — `tenant_001`, `tenant_002`, `tenant_003`, `tenant_004`, `tenant_005`, `tenant_006`, `tenant_007`, `tenant_008`, `tenant_009`, `tenant_010`, `tenant_011`, `tenant_012`, `tenant_013`, `tenant_014`, `tenant_015`, `tenant_016`, `tenant_017`

### T14 — Preluarea unei firme

**Clasa:** MECANIC · **rute:** 32 (din care schimba date: 21) · **refuzuri explicite:** 81

**Cine:** rol cerut: `admin_firma`. **Rute care schimba date fara nicio verificare de rol: 10 din 21.**

**Pasii, din cod:**

- `POST /control-fiscal/{tenant_id}/audit-preluare` — garda `cere_rol` rol:admin_firma
- `GET /migrare/asociati` — garda `cere_cabinet`
- `POST /migrare/fisier` — garda `cere_cabinet`
- `POST /migrare/importa` — garda `cere_rol` rol:admin_firma
- `POST /migrare/incarca` — garda `cere_cabinet`
- `GET /migrare/istoric-declaratii` — garda `cere_cabinet`
- `GET /migrare/mijloace-fixe` — garda `cere_cabinet`
- `GET /migrare/parteneri` — garda `cere_cabinet`
- `GET /migrare/plan-conturi` — garda `cere_cabinet`
- `GET /migrare/salariati` — garda `cere_cabinet`
- `GET /migrare/solduri` — garda `cere_cabinet`
- `GET /migrare/status` — garda `cere_cabinet`
- `POST /migrare/status` — garda `cere_rol` rol:admin_firma
- `GET /migrare/straturi` — garda `cere_cabinet`
- `POST /migrare/valideaza` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/articole-import` — garda `cere_rol` rol:admin_firma
- `POST /tenants/{tenant_id}/articole-import/incarca` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/asociati-import` — garda `cere_rol` rol:admin_firma
- `POST /tenants/{tenant_id}/asociati-import/incarca` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/mijloace-fixe-import` — garda `cere_rol` rol:admin_firma
- `POST /tenants/{tenant_id}/mijloace-fixe-import/incarca` — garda `cere_cabinet`
- `GET /tenants/{tenant_id}/parteneri` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/parteneri` — garda `cere_rol` rol:admin_firma
- `POST /tenants/{tenant_id}/parteneri/incarca` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/retete-import` — garda `cere_rol` rol:admin_firma
- `POST /tenants/{tenant_id}/retete-import/incarca` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/rip-import/incarca` — garda `cere_rol` rol:admin_firma
- `POST /tenants/{tenant_id}/salariati-import` — garda `cere_rol` rol:admin_firma
- `POST /tenants/{tenant_id}/salariati-import/incarca` — garda `cere_cabinet`
- `GET /tenants/{tenant_id}/solduri` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/solduri` — garda `cere_rol` rol:admin_firma
- `POST /tenants/{tenant_id}/solduri/incarca` — garda `cere_cabinet`

**Module:** `anaf_api`, `artefacte`, `articole_import_api`, `asociati_import_api`, `audit_preluare`, `cor_api`, `istoric_declaratii_import_api`, `migrare_api`, `mijloace_fixe_import_api`, `observare`, `retete_import_api`, `rip_migrare_api`, `salariati_import_api`, `solduri_api`, `solduri_parteneri_api`, `tenant_provisioning`

**Scrie in:** `artefacte_produse` (INSERT) · `articole` (INSERT) · `asociati` (DELETE/INSERT) · `audit_log` (INSERT) · `declaratii_depuse` (DELETE/INSERT) · `firma_profil` (INSERT/UPDATE) · `migrare_status` (INSERT) · `mijloace_fixe` (DELETE/INSERT) · `miscari_stoc` (INSERT) · `plan_conturi` (INSERT) · `rip_operatiuni` (INSERT) · `salariati` (INSERT) · `solduri_initiale` (DELETE/INSERT) · `solduri_parteneri` (DELETE/INSERT) · `tenants` (INSERT/UPDATE) · `user_tenants` (INSERT)

**Stari puse:** `validata`

**Firme care il pot exercita azi: 5** — `tenant_005`, `tenant_013`, `tenant_014`, `tenant_015`, `tenant_016`

### T15 — Salariatul — angajare, contract, adeverință, REGES

**Clasa:** MANUAL · **rute:** 17 (din care schimba date: 12) · **refuzuri explicite:** 45

**Cine:** rol cerut: `admin_firma`, `angajat`. **Rute care schimba date fara nicio verificare de rol: 3 din 12.**

**Pasii, din cod:**

- `GET /contracte/marcaje` — garda `cere_cabinet`
- `GET /cor` — garda `cere_context`
- `POST /tenants/{tenant_id}/contracte/genereaza` — garda `cere_rol` rol:admin_firma
- `GET /tenants/{tenant_id}/contracte/sabloane` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/contracte/sabloane` — garda `cere_cabinet`
- `DELETE /tenants/{tenant_id}/contracte/sabloane/{sid}` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/prapastie-salariu` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/reges-config` — garda `cere_rol` rol:admin_firma
- `POST /tenants/{tenant_id}/reges-poll` — garda `cere_rol` rol:admin_firma
- `POST /tenants/{tenant_id}/reges-trimite-salariat` — garda `cere_rol` rol:admin_firma
- `GET /tenants/{tenant_id}/salariati` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/salariati` — garda `cere_rol` rol:admin_firma,angajat
- `DELETE /tenants/{tenant_id}/salariati/{salariat_id}` — garda `cere_rol` rol:admin_firma,angajat
- `GET /tenants/{tenant_id}/salariati/{salariat_id}` — garda `cere_cabinet`
- `PUT /tenants/{tenant_id}/salariati/{salariat_id}` — garda `cere_rol` rol:admin_firma,angajat
- `POST /tenants/{tenant_id}/salariati/{salariat_id}/adeverinta` — garda `cere_rol` rol:admin_firma
- `PUT /tenants/{tenant_id}/salariati/{salariat_id}/beneficiu-lunar` — garda `cere_rol` rol:admin_firma,angajat

**Module:** `adeverinta`, `beneficii_api`, `contracte_api`, `cor_api`, `prapastie_salariu`, `reges_client`, `salariati_api`

**Scrie in:** `beneficii_lunare` (DELETE/INSERT) · `concedii_medicale` (DELETE/INSERT/UPDATE) · `contracte_sabloane` (DELETE/INSERT/UPDATE) · `pontaj` (DELETE) · `reges_chei` (INSERT) · `reges_mesaje` (INSERT/UPDATE) · `salariati` (DELETE/INSERT/UPDATE) · `salariu_istoric` (DELETE)

**Margine:** `reges_client` (transmite salariatul la registrul de evidență a muncii)

**Firme care il pot exercita azi: 8** — `tenant_001`, `tenant_003`, `tenant_005`, `tenant_013`, `tenant_014`, `tenant_015`, `tenant_016`, `tenant_017`

### T16 — Pontajul

**Clasa:** MECANIC · **rute:** 4 (din care schimba date: 2) · **refuzuri explicite:** 7

**Cine:** rol cerut: `admin_firma`. **Rute care schimba date fara nicio verificare de rol: 1 din 2.**

**Pasii, din cod:**

- `POST /tenants/{tenant_id}/pontaj/confirma` — garda `cere_rol` rol:admin_firma
- `GET /tenants/{tenant_id}/salariati/{salariat_id}/pontaj` — garda `cere_context`
- `PUT /tenants/{tenant_id}/salariati/{salariat_id}/pontaj` — garda `cere_context`
- `GET /util/zile-lucratoare` — garda `cere_context`

**Module:** `perioada`, `pontaj`, `scadente`

**Scrie in:** `pontaj` (DELETE/INSERT)

**Firme care il pot exercita azi: NICIUNA.**

### T17 — Plata salariilor — fișierul către bancă

**Clasa:** MECANIC · **rute:** 2 (din care schimba date: 1) · **refuzuri explicite:** 10

**Cine:** rol cerut: `admin_firma`. **Rute care schimba date fara nicio verificare de rol: 0 din 1.**

**Pasii, din cod:**

- `POST /tenants/{tenant_id}/plata-salarii-fisier` — garda `cere_rol` rol:admin_firma
- `GET /tenants/{tenant_id}/plata-salarii-preview` — garda `cere_cabinet`

**Module:** `artefacte`, `plata_salarii`

**Scrie in:** `artefacte_produse` (INSERT)

**Firme care il pot exercita azi:** *nu se poate sti din date* — traseul n-are tabela proprie.

### T18 — Chitanța și încasarea

**Clasa:** MANUAL · **rute:** 6 (din care schimba date: 3) · **refuzuri explicite:** 7

**Cine:** rol cerut: `admin_firma`. **Rute care schimba date fara nicio verificare de rol: 0 din 3.**

**Pasii, din cod:**

- `GET /public/plata/{ref}` — garda `FARA GARDA`
- `POST /public/plata/{ref}/confirma` — garda `FARA GARDA`
- `GET /tenants/{tenant_id}/chitante` — garda `cere_context`
- `POST /tenants/{tenant_id}/chitante` — garda `cere_rol` rol:admin_firma
- `GET /tenants/{tenant_id}/chitante/{chitanta_id}/pdf` — garda `cere_rol` rol:admin_firma
- `POST /tenants/{tenant_id}/facturi/{factura_id}/link-plata` — garda `cere_rol` rol:admin_firma

**Module:** `casa_api`, `chitante`, `plati`

**Scrie in:** `casa_operatiuni` (DELETE/INSERT) · `chitante` (INSERT) · `facturi` (UPDATE) · `inregistrari` (DELETE/INSERT) · `inregistrari_linii` (INSERT)

**Margine:** `plati` (linkul de plată — procesatorul (azi MOCK, vezi /public/plata))

**Firme care il pot exercita azi: 1** — `tenant_013`

### T19 — Scadențarul și notificările de scadență

**Clasa:** MECANIC · **rute:** 2 (din care schimba date: 1) · **refuzuri explicite:** 2

**Cine:** rol cerut: `admin_firma`. **Rute care schimba date fara nicio verificare de rol: 0 din 1.**

**Pasii, din cod:**

- `GET /tenants/{tenant_id}/scadentar` — garda `cere_context`
- `PUT /tenants/{tenant_id}/scadentar/opt-in` — garda `cere_rol` rol:admin_firma

**Module:** `scadentar`

**Scrie in:** `facturi` (UPDATE) · `firma_profil` (UPDATE)

**Firme care il pot exercita azi: NICIUNA.**

### T20 — Mișcarea de stoc — intrare, ieșire, transfer, reclasificare

**Clasa:** MECANIC · **rute:** 12 (din care schimba date: 7) · **refuzuri explicite:** 33

**Cine:** nicio verificare de rol pe tot traseul — orice utilizator autentificat al cabinetului. **7 din 7 rute care schimba date.**

**Pasii, din cod:**

- `GET /tenants/{tenant_id}/stocuri/analitica` — garda `cere_cabinet`
- `GET /tenants/{tenant_id}/stocuri/articole` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/stocuri/articole/{articol_id}/barcode` — garda `cere_cabinet`
- `GET /tenants/{tenant_id}/stocuri/articole/{articol_id}/fisa` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/stocuri/articole/{articol_id}/nivel-minim` — garda `cere_cabinet`
- `GET /tenants/{tenant_id}/stocuri/barcode/{cod}` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/stocuri/descarcare` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/stocuri/iesire` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/stocuri/intrare` — garda `cere_cabinet`
- `GET /tenants/{tenant_id}/stocuri/locatii` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/stocuri/reclasificare` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/stocuri/transfer` — garda `cere_cabinet`

**Module:** `stocuri_api`, `stocuri_cv_api`

**Scrie in:** `articole` (INSERT/UPDATE) · `inregistrari` (INSERT) · `inregistrari_linii` (INSERT) · `miscari_stoc` (INSERT) · `nir` (INSERT) · `nir_linii` (INSERT)

**Stari puse:** `validata`

**Firme care il pot exercita azi: 2** — `tenant_003`, `tenant_013`

### T21 — Rețeta și producția

**Clasa:** MECANIC · **rute:** 9 (din care schimba date: 7) · **refuzuri explicite:** 13

**Cine:** nicio verificare de rol pe tot traseul — orice utilizator autentificat al cabinetului. **7 din 7 rute care schimba date.**

**Pasii, din cod:**

- `GET /tenants/{tenant_id}/produse` — garda `cere_context`
- `POST /tenants/{tenant_id}/produse` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/produse/potriveste` — garda `cere_context`
- `DELETE /tenants/{tenant_id}/produse/{produs_id}` — garda `cere_cabinet`
- `PUT /tenants/{tenant_id}/produse/{produs_id}` — garda `cere_cabinet`
- `GET /tenants/{tenant_id}/retete` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/retete` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/retete/descarca` — garda `cere_cabinet`
- `DELETE /tenants/{tenant_id}/retete/{reteta_id}` — garda `cere_cabinet`

**Module:** `produse_api`, `retete_api`

**Scrie in:** `inregistrari` (INSERT) · `inregistrari_linii` (INSERT) · `miscari_stoc` (INSERT) · `produse` (DELETE/INSERT/UPDATE) · `retete` (DELETE/INSERT/UPDATE) · `retete_linii` (DELETE/INSERT)

**Firme care il pot exercita azi: 1** — `tenant_013`

### T22 — Mijlocul fix și amortizarea

**Clasa:** MECANIC · **rute:** 3 (din care schimba date: 2) · **refuzuri explicite:** 12

**Cine:** rol cerut: `admin_firma`. **Rute care schimba date fara nicio verificare de rol: 1 din 2.**

**Pasii, din cod:**

- `POST /tenants/{tenant_id}/amortizare` — garda `cere_rol` rol:admin_firma
- `GET /tenants/{tenant_id}/mijloace-fixe` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/reevaluare-imobilizare` — garda `cere_cabinet`

**Module:** `afirmatii`, `d406_active`, `reevaluare`

**Scrie in:** `inregistrari` (INSERT) · `inregistrari_linii` (INSERT)

**Firme care il pot exercita azi: 2** — `tenant_005`, `tenant_013`

### T23 — Bonul de la client — portalul și decontul

**Clasa:** MECANIC · **rute:** 9 (din care schimba date: 5) · **refuzuri explicite:** 20

**Cine:** rol cerut: `admin_firma`. **Rute care schimba date fara nicio verificare de rol: 3 din 5.**

**Pasii, din cod:**

- `POST /portal/bon` — garda `cere_context`
- `DELETE /portal/bon/{bon_id}` — garda `cere_context`
- `POST /portal/bon/{bon_id}/confirma` — garda `cere_context`
- `GET /portal/bon/{bon_id}/imagine/{n}` — garda `cere_context`
- `GET /tenants/{tenant_id}/bonuri/de-verificat` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/bonuri/{bon_id}/aproba` — garda `cere_rol` rol:admin_firma
- `GET /tenants/{tenant_id}/bonuri/{bon_id}/facturi-candidate` — garda `cere_cabinet`
- `GET /tenants/{tenant_id}/bonuri/{bon_id}/imagine/{n}` — garda `cere_rol` rol:admin_firma
- `POST /tenants/{tenant_id}/bonuri/{bon_id}/stinge` — garda `cere_rol` rol:admin_firma

**Module:** `ai_client`, `casa_api`

**Scrie in:** `bonuri` (DELETE/INSERT/UPDATE) · `casa_operatiuni` (DELETE/INSERT) · `facturi` (UPDATE) · `inregistrari` (DELETE/INSERT) · `inregistrari_linii` (INSERT)

**Firme care il pot exercita azi: 2** — `tenant_001`, `tenant_013`

### T24 — Bonul fiscal și raportul Z (AMEF, horeca)

**Clasa:** MECANIC · **rute:** 2 (din care schimba date: 2) · **refuzuri explicite:** 9

**Cine:** rol cerut: `admin_firma`. **Rute care schimba date fara nicio verificare de rol: 1 din 2.**

**Pasii, din cod:**

- `POST /tenants/{tenant_id}/horeca/import-amef` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/horeca/raport-z` — garda `cere_rol` rol:admin_firma

**Module:** `amef_import`

**Scrie in:** `inregistrari` (INSERT) · `inregistrari_linii` (INSERT)

**Firme care il pot exercita azi:** *nu se poate sti din date* — traseul n-are tabela proprie.

### T25 — Comanda din magazinul online (WooCommerce)

**Clasa:** MANUAL · **rute:** 3 (din care schimba date: 2) · **refuzuri explicite:** 2

**Cine:** rol cerut: `admin_firma`. **Rute care schimba date fara nicio verificare de rol: 0 din 2.**

**Pasii, din cod:**

- `GET /tenants/{tenant_id}/woocommerce/config` — garda `cere_context`
- `PUT /tenants/{tenant_id}/woocommerce/config` — garda `cere_rol` rol:admin_firma
- `POST /tenants/{tenant_id}/woocommerce/sincronizeaza` — garda `cere_rol` rol:admin_firma

**Module:** `woocommerce`

**Scrie in:** `facturi` (UPDATE) · `firma_profil` (UPDATE)

**Margine:** `woocommerce` (sincronizează comenzile cu magazinul online)

**Firme care il pot exercita azi:** *nu se poate sti din date* — traseul n-are tabela proprie.

### T26 — Registratura

**Clasa:** MECANIC · **rute:** 2 (din care schimba date: 1) · **refuzuri explicite:** 3

**Cine:** nicio verificare de rol pe tot traseul — orice utilizator autentificat al cabinetului. **1 din 1 rute care schimba date.**

**Pasii, din cod:**

- `GET /tenants/{tenant_id}/registratura` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/registratura` — garda `cere_cabinet`

**Module:** `registratura_api`

**Scrie in:** `registratura` (INSERT)

**Firme care il pot exercita azi: 1** — `tenant_013`

### T27 — e-Transport

**Clasa:** MANUAL · **rute:** 3 (din care schimba date: 2) · **refuzuri explicite:** 11

**Cine:** rol cerut: `admin_firma`. **Rute care schimba date fara nicio verificare de rol: 1 din 2.**

**Pasii, din cod:**

- `POST /tenants/{tenant_id}/etransport-xml` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/etransport/trimite` — garda `cere_rol` rol:admin_firma
- `GET /tenants/{tenant_id}/etransport/trimiteri` — garda `cere_context`

**Module:** `etransport`, `etransport_send`, `spv_rute`

**Scrie in:** `etransport_trimiteri` (INSERT/UPDATE)

**Margine:** `etransport_send` (transmite declarația UIT la ANAF)

**Firme care il pot exercita azi: NICIUNA.**

### T28 — Operațiunile intracomunitare, VIES și Intrastat

**Clasa:** MECANIC · **rute:** 12 (din care schimba date: 6) · **refuzuri explicite:** 53

**Cine:** rol cerut: `admin_firma`. **Rute care schimba date fara nicio verificare de rol: 5 din 6.**

**Pasii, din cod:**

- `GET /public/verifica-cui/{cui}` — garda `FARA GARDA`
- `POST /tenants/{tenant_id}/achizitie-ic` — garda `cere_rol` rol:admin_firma
- `GET /tenants/{tenant_id}/d390-clasificare` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/d390-clasificare/manual` — garda `cere_cabinet`
- `DELETE /tenants/{tenant_id}/d390-clasificare/manual/{mid}` — garda `cere_cabinet`
- `PUT /tenants/{tenant_id}/d390-clasificare/reclasificare` — garda `cere_cabinet`
- `GET /tenants/{tenant_id}/intrastat-praguri` — garda `cere_cabinet`
- `GET /tenants/{tenant_id}/registre-art321/{fel}` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/registre-art321/{fel}` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/vanzare-ic` — garda `cere_cabinet`
- `GET /tenants/{tenant_id}/verifica-cui/{cui}` — garda `cere_context`
- `GET /tenants/{tenant_id}/verifica-vies` — garda `cere_context`

**Module:** `anaf_api`, `cont_valid`, `d390_clasificare_api`, `facturi_api`, `intracomunitar`, `intrastat`, `registre_art321`

**Scrie in:** `d390_manual` (DELETE/INSERT) · `d390_reclasificare` (DELETE/INSERT) · `factura_linii` (INSERT) · `facturi` (DELETE/INSERT/UPDATE) · `firma_profil` (UPDATE) · `inregistrari` (INSERT) · `inregistrari_linii` (INSERT) · `registre_art321` (INSERT)

**Firme care il pot exercita azi: 2** — `tenant_013`, `tenant_017`

### T29 — Regimurile speciale de TVA — marjă, aur, agricultori, taxare inversă

**Clasa:** MECANIC · **rute:** 11 (din care schimba date: 10) · **refuzuri explicite:** 81

**Cine:** rol cerut: `admin_firma`. **Rute care schimba date fara nicio verificare de rol: 7 din 10.**

**Pasii, din cod:**

- `POST /tenants/{tenant_id}/achizitie-agricultor` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/achizitie-necorporala` — garda `cere_rol` rol:admin_firma
- `POST /tenants/{tenant_id}/achizitie-neinregistrat` — garda `cere_rol` rol:admin_firma
- `POST /tenants/{tenant_id}/achizitie-taxare-inversa` — garda `cere_rol` rol:admin_firma
- `POST /tenants/{tenant_id}/export-extracomunitar` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/import-extracomunitar` — garda `cere_cabinet`
- `GET /tenants/{tenant_id}/jurnal-marja` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/vanzare-agricultor` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/vanzare-aur-investitii` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/vanzare-marja` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/vanzare-marja-turism` — garda `cere_cabinet`

**Module:** `afirmatii`, `anaf_api`, `cont_valid`, `d394`, `facturi_api`, `import_export`, `taxare_inversa`, `tva_agricultori`, `tva_aur`, `tva_marja`, `tva_marja_turism`

**Scrie in:** `factura_linii` (INSERT) · `facturi` (DELETE/INSERT/UPDATE) · `firma_profil` (UPDATE) · `inregistrari` (INSERT) · `inregistrari_linii` (INSERT) · `mijloace_fixe` (INSERT)

**Firme care il pot exercita azi:** *nu se poate sti din date* — traseul n-are tabela proprie.

### T30 — Operațiunile în valută

**Clasa:** MECANIC · **rute:** 2 (din care schimba date: 2) · **refuzuri explicite:** 11

**Cine:** nicio verificare de rol pe tot traseul — orice utilizator autentificat al cabinetului. **2 din 2 rute care schimba date.**

**Pasii, din cod:**

- `POST /tenants/{tenant_id}/decontare-valuta` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/reevaluare-valuta` — garda `cere_cabinet`

**Module:** `afirmatii`, `cont_valid`, `curs_bnr`, `diferente_curs`

**Scrie in:** `curs_bnr_zilnic` (INSERT) · `inregistrari` (INSERT) · `inregistrari_linii` (INSERT)

**Firme care il pot exercita azi:** *nu se poate sti din date* — traseul n-are tabela proprie.

### T31 — Completările manuale la o declarație (D300, D301)

**Clasa:** MECANIC · **rute:** 8 (din care schimba date: 5) · **refuzuri explicite:** 10

**Cine:** nicio verificare de rol pe tot traseul — orice utilizator autentificat al cabinetului. **5 din 5 rute care schimba date.**

**Pasii, din cod:**

- `GET /tenants/{tenant_id}/d300-manual` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/d300-manual` — garda `cere_cabinet`
- `DELETE /tenants/{tenant_id}/d300-manual/{rid}` — garda `cere_cabinet`
- `GET /tenants/{tenant_id}/d301-operatiuni` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/d301-operatiuni` — garda `cere_cabinet`
- `DELETE /tenants/{tenant_id}/d301-operatiuni/{op_id}` — garda `cere_cabinet`
- `GET /tenants/{tenant_id}/registru-evidenta-fiscala` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/registru-evidenta-fiscala` — garda `cere_cabinet`

**Module:** `d300_manual_api`, `d301_operatiuni_api`, `registru_evidenta_fiscala`

**Scrie in:** `d300_manual` (DELETE/INSERT) · `d301_operatiuni` (DELETE/INSERT) · `registru_fiscal_pf` (INSERT)

**Firme care il pot exercita azi: 3** — `tenant_006`, `tenant_014`, `tenant_017`

### T32 — Registrul de încasări și plăți (partida simplă)

**Clasa:** MECANIC · **rute:** 7 (din care schimba date: 5) · **refuzuri explicite:** 4

**Cine:** nicio verificare de rol pe tot traseul — orice utilizator autentificat al cabinetului. **5 din 5 rute care schimba date.**

**Pasii, din cod:**

- `GET /tenants/{tenant_id}/rip/d212/{an}` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/rip/import-banca` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/rip/import-casa` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/rip/operatiuni` — garda `cere_cabinet`
- `DELETE /tenants/{tenant_id}/rip/operatiuni/{op_id}` — garda `cere_cabinet`
- `PUT /tenants/{tenant_id}/rip/operatiuni/{op_id}/valideaza` — garda `cere_cabinet`
- `GET /tenants/{tenant_id}/rip/registru` — garda `cere_cabinet`

**Module:** `rip_api`

**Scrie in:** `rip_operatiuni` (DELETE/INSERT/UPDATE)

**Stari puse:** `ciorna`, `validata`

**Firme care il pot exercita azi: NICIUNA.**

### T33 — Exportul contabil (SAGA, WinMentor)

**Clasa:** MECANIC · **rute:** 3 (din care schimba date: 2) · **refuzuri explicite:** 12

**Cine:** rol cerut: `admin_firma`. **Rute care schimba date fara nicio verificare de rol: 0 din 2.**

**Pasii, din cod:**

- `POST /tenants/{tenant_id}/facturi/export-saga` — garda `cere_rol` rol:admin_firma
- `POST /tenants/{tenant_id}/facturi/export-winmentor` — garda `cere_rol` rol:admin_firma
- `GET /tenants/{tenant_id}/facturi/{factura_id}/export-saga` — garda `cere_context`

**Module:** `artefacte`, `export_saga`, `export_winmentor`

**Scrie in:** `artefacte_produse` (INSERT)

**Firme care il pot exercita azi:** *nu se poate sti din date* — traseul n-are tabela proprie.

### T34 — Rapoartele comerciale, centrele de cost și rapoartele salvate

**Clasa:** MECANIC · **rute:** 14 (din care schimba date: 5) · **refuzuri explicite:** 20

**Cine:** nicio verificare de rol pe tot traseul — orice utilizator autentificat al cabinetului. **5 din 5 rute care schimba date.**

**Pasii, din cod:**

- `GET /ansamblu` — garda `cere_context`
- `GET /api/v1/firme/{tenant_id}/kpi` — garda `cere_api_key`
- `GET /cabinet/consolidare` — garda `cere_cabinet`
- `GET /tenants/{tenant_id}/centre-cost` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/centre-cost` — garda `cere_cabinet`
- `GET /tenants/{tenant_id}/centre-cost/raport` — garda `cere_cabinet`
- `GET /tenants/{tenant_id}/centre-cost/varianta` — garda `cere_cabinet`
- `PUT /tenants/{tenant_id}/centre-cost/{centru_id}` — garda `cere_cabinet`
- `PUT /tenants/{tenant_id}/centre-cost/{centru_id}/buget` — garda `cere_cabinet`
- `GET /tenants/{tenant_id}/rapoarte-comerciale` — garda `cere_cabinet`
- `GET /tenants/{tenant_id}/rapoarte-comerciale/fisa` — garda `cere_cabinet`
- `GET /tenants/{tenant_id}/rapoarte-salvate` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/rapoarte-salvate` — garda `cere_cabinet`
- `DELETE /tenants/{tenant_id}/rapoarte-salvate/{vid}` — garda `cere_cabinet`

**Module:** `ajutor`, `centre_cost_api`, `documente_api`, `kpi_client`, `rapoarte_comerciale_api`

**Scrie in:** `bugete` (INSERT) · `centre_cost` (INSERT/UPDATE) · `rapoarte_salvate` (DELETE/INSERT)

**Stari puse:** `validata`

**Firme care il pot exercita azi: 1** — `tenant_013`

### T35 — Pachetul lunar către client și solicitările lui

**Clasa:** MECANIC · **rute:** 38 (din care schimba date: 16) · **refuzuri explicite:** 61

**Cine:** rol cerut: `admin_firma`, `angajat`, `verificat-în-corp`. **Rute care schimba date fara nicio verificare de rol: 5 din 16.**

**Pasii, din cod:**

- `POST /pachete/{tenant_id}/genereaza` — garda `cere_cabinet`
- `GET /pachete/{tenant_id}/poveste` — garda `cere_cabinet`
- `POST /pachete/{tenant_id}/poveste` — garda `cere_rol` rol:admin_firma
- `GET /pachete/{tenant_id}/preview` — garda `cere_cabinet`
- `GET /pachete/{tenant_id}/rezumat` — garda `cere_cabinet`
- `POST /pachete/{tenant_id}/trimite` — garda `cere_rol` rol:admin_firma
- `GET /portal/acasa` — garda `cere_client`
- `GET /portal/acces-cont` — garda `cere_client`
- `POST /portal/acces-cont/acces` — garda `cere_client` rol:verificat-în-corp
- `DELETE /portal/acces-cont/acces/{user_id}` — garda `cere_client`
- `PUT /portal/acces-cont/email` — garda `cere_client`
- `GET /portal/cashflow` — garda `cere_client`
- `GET /portal/declaratii` — garda `cere_client`
- `GET /portal/documente/balanta` — garda `cere_client`
- `GET /portal/documente/luni` — garda `cere_client`
- `GET /portal/facturi` — garda `cere_client`
- `GET /portal/firma` — garda `cere_client`
- `GET /portal/firme` — garda `cere_client`
- `GET /portal/kpi` — garda `cere_client`
- `GET /portal/povesti` — garda `cere_client`
- `POST /portal/recomanda` — garda `cere_client`
- `GET /portal/recomanda/preview` — garda `cere_client`
- `GET /portal/solicitari` — garda `cere_client`
- `POST /portal/solicitari` — garda `cere_client`
- `GET /portal/solicitari/contor` — garda `cere_client`
- `POST /public/confirma-email` — garda `FARA GARDA`
- `POST /tenants/{tenant_id}/acces-portal` — garda `cere_rol` rol:admin_firma,angajat,verificat-în-corp
- `GET /tenants/{tenant_id}/client-acces` — garda `cere_rol` rol:admin_firma,angajat
- `POST /tenants/{tenant_id}/client-acces` — garda `cere_rol` rol:admin_firma,verificat-în-corp
- `DELETE /tenants/{tenant_id}/client-acces/{user_id}` — garda `cere_rol` rol:admin_firma
- `GET /tenants/{tenant_id}/clienti` — garda `cere_cabinet`
- `POST /tenants/{tenant_id}/clienti` — garda `cere_rol` rol:admin_firma,angajat
- `DELETE /tenants/{tenant_id}/clienti/{client_id}` — garda `cere_rol` rol:admin_firma,angajat
- `GET /tenants/{tenant_id}/clienti/{client_id}` — garda `cere_cabinet`
- `PUT /tenants/{tenant_id}/clienti/{client_id}` — garda `cere_rol` rol:admin_firma,angajat
- `GET /tenants/{tenant_id}/solicitari` — garda `cere_context`
- `POST /tenants/{tenant_id}/solicitari` — garda `cere_rol` rol:admin_firma
- `GET /tenants/{tenant_id}/urme-portal` — garda `cere_cabinet`

**Module:** `cashflow`, `clienti_api`, `control_fiscal_api`, `documente_api`, `facturi_api`, `kpi_client`, `notificari_api`, `observare`, `pachete_api`, `portal_api`, `tenant_provisioning`

**Scrie in:** `audit_log` (INSERT) · `clienti` (DELETE/INSERT/UPDATE) · `factura_linii` (INSERT) · `facturi` (DELETE/INSERT/UPDATE) · `firma_profil` (INSERT/UPDATE) · `notificari` (INSERT/UPDATE) · `pachet_povestea` (INSERT) · `schimbari_email` (DELETE/INSERT/UPDATE) · `solicitari_client` (INSERT) · `tenants` (INSERT/UPDATE) · `user_tenants` (DELETE/INSERT) · `users` (INSERT/UPDATE)

**Stari puse:** `aprobat`, `descarcata`, `validata`

**Firme care il pot exercita azi: 1** — `tenant_013`

### T36 — Ciclul de viață al firmei — creare, identitate, dezactivare, scoatere

**Clasa:** MECANIC · **rute:** 9 (din care schimba date: 5) · **refuzuri explicite:** 34

**Cine:** rol cerut: `admin_firma`. **Rute care schimba date fara nicio verificare de rol: 0 din 5.**

**Pasii, din cod:**

- `GET /firme-scoase` — garda `cere_cabinet`
- `GET /tenants` — garda `cere_cabinet`
- `POST /tenants` — garda `cere_rol` rol:admin_firma
- `DELETE /tenants/{tenant_id}` — garda `cere_rol` rol:admin_firma
- `GET /tenants/{tenant_id}` — garda `cere_cabinet`
- `PUT /tenants/{tenant_id}` — garda `cere_rol` rol:admin_firma
- `POST /tenants/{tenant_id}/activare` — garda `cere_rol` rol:admin_firma
- `POST /tenants/{tenant_id}/nume-ales` — garda `cere_rol` rol:admin_firma
- `GET /tenants/{tenant_id}/scoatere` — garda `cere_cabinet`

**Module:** `observare`, `tenant_provisioning`, `tenant_stergere`

**Scrie in:** `audit_log` (INSERT) · `firma_profil` (INSERT/UPDATE) · `firme_scoase` (INSERT/UPDATE) · `tenants` (DELETE/INSERT/UPDATE) · `user_tenants` (INSERT) · `users` (UPDATE)

**Firme care il pot exercita azi:** *nu se poate sti din date* — traseul n-are tabela proprie.

<!-- trasee:auto:stop -->
