# iConta — Design System

*Document normativ · v2.103 · 24 octombrie 2026 (editabil prin SSH)*

**Acest document este REFERINȚA OBLIGATORIE pentru orice ecran nou și pentru auditul celor existente. Nicio abatere fără actualizarea prealabilă a acestui document.**

---

## 0. Principii generale

- Nicio clasă vizuală nouă. Orice element nou folosește exclusiv clasele din acest document. Clase suplimentare = doar hook JS sau poziționare (margin/width), niciodată culori/fonturi/umbre/dimensiuni.
- Când se descoperă o inconsistență: STOP, se corectează, apoi se continuă. Zero datorie tehnică vizuală.
- La orice decizie de schimbare de comportament se verifică TOATE locurile unde comportamentul vechi există, nu doar cel discutat.
- Textele afișate folosesc diacritice românești complete; codul/comentariile/markerii — fără diacritice.
- **Numeralul se acordă cu substantivul (Lotul 5, 15.10.2026, deficiențele 261 / 263):** un număr afișat trece prin `cate(n, singular, plural)` (`static/js/plural.js`; în Python `core/common.cate`) — „1 notă”, „2 note”, „20 de note”, „101 note”; niciodată o formă scrisă fix după număr („1 note”, „1 facturi”, „5 absent”). Gard: `NUMERAL_NEACORDAT` în verificator + `core/test_plural_dupa_numar.py` (JS și Python), excepțiile numite acolo cu motivul.
- **Textul afișat e limba contabilului (v2.84, comanda Costin „Retest 08.10” pct.14):** fără identificatori de cod (`common.COTE`, `R3_1_1`,
  `d100_fapt`, `False`/`None`, nume de coloană) și fără majuscule de accent („ATENTIE”, „NU”, „LIPSĂ”); un rând de cod D300 se spune
  „rândul 5.1”, o cheie de cotă prin eticheta ei. Gard: `core/test_text_afisat_limbaj.py`.
- Mesajele către utilizator sunt clare și strict folositoare: spun ce s-a întâmplat și ce are de făcut.

## 1. Butoane — set ÎNCHIS

Toate butoanele au umbră. Butoanele deschise la culoare au și bordură. Padding unic 9px 18px (excepții: `.buton-mic`, `.btn-nav`). NU se adaugă clase noi.

| Clasă | Rol |
| --- | --- |
| `.buton-primar` | Acțiunea principală. Albastru #3d8fd6, text alb, fără bordură. |
| `.buton-secundar` | Acțiuni secundare. Alb, text ardezie, **bordură 1px #b9c2cf** (v2.0 — era #e2e5ea/var(--linie), invizibil pe fond alb). |
| `.buton-sters` | Ștergere/revocare/distructiv. Roșu #ff3b30, text alb. |
| `.buton-verde` | Aprobare/confirmare pozitivă. Verde #1d7a4d. |
| `.buton-mic` | MODIFICATOR de mărime, se combină (ex: `buton-sters buton-mic`). Singurul modificator de mărime permis. |
| `.btn-link` | Acțiune discretă tip link. Fără fundal/bordură/umbră. Albastru subliniat. |
| `.btn-nav` | Exclusiv navigare. 32×32px, portocaliu #f97316. Duce MEREU un pas înapoi. |
| `.buton-activ` | STARE (nu buton): marchează butonul cu zona toggle deschisă. Albastru închis #1a5a94. |

- **Butonul dezactivat arată dezactivat (v2.87, 10.10.2026, deficiența 222).** Fiecare clasă de buton din set are regula ei `:disabled`
  (`.buton-primar`: fundal gri; celelalte: estompat `.55`, cursor obișnuit), iar hover-ul nu se aplică unui buton dezactivat. Gard
  `BUTON_DEZACTIVAT` (verificator).
- **Acțiunea pe o declarație e inactivă până se alege tipul declarației (v2.87, 10.10.2026, comanda Costin, deficiența 222: „«Trimite
  în coadă» e activ fără tip de declarație ales”).** Pe un ecran cu select de tip de declarație, butoanele care lucrează pe ea
  (Validează, Descarcă XML, Trimite în coadă, Continuă) sunt `disabled` cât timp tipul e „— alege —” — ca „Continuă” din Declarații.
  Refuzul de lângă câmp (`cereAlegerile`, cap.17) rămâne în handler. Gard `ACTIUNE_FARA_TIP` (verificator).
  **Și până se completează datele fără de care serverul refuză (v2.88, 12.10.2026, comanda Costin, deficiența 228: „în bilanț,
  «Validează» și «Trimite în coadă» sunt inactive până se completează coloana «An precedent», cu motivul afișat lângă ele.”).** Bilanțul:
  „Validează”, „Descarcă XML” și „Trimite în coadă” sunt `disabled` cât timp coloana „An precedent” a anului și tipului alese lipsește
  sau nu e încă citită; motivul stă lângă ele (`#bl-actiuni-motiv`). Gard `ACTIUNE_FARA_TIP` (extins).
- **Butonul declanșator în timpul unei scrieri (v2.81, 08.10.2026).** `api.js` (`blocheazaButon`) dezactivează automat butonul
  apăsat cât durează orice scriere și îi pune `aria-busy`. „Se lucrează...” se scrie NUMAI pe un buton de text simplu, iar la
  final textul lui revine. Un buton care conține ELEMENTE (rândul-buton al unei liste, cardul, iconița) nu se rescrie: textul
  l-ar aplatiza și ar detașa elementul acțiunii, iar ecranul n-ar mai putea arăta rezultatul (instanța: „Contează” pe rândul
  facturii rămânea după contare — 45 de butoane cu elemente, în 10 fișiere). Gard: `core/test_buton_blocat_structura.py`
  (în browser, pe modulul real).

**Feedback obligatoriu:**
- Butoane cu zonă toggle: primesc `.buton-activ` cât timp zona e deschisă; deschiderea unei zone închide zonele-frate.
- **Vederea aleasă e activă, nu dezactivată (lotul 12, deficiența 469).** Între două sau mai multe vederi ale aceluiași ecran, butonul ales poartă `.buton-activ` și `aria-pressed="true"`; niciunul nu e `disabled` — un buton ales care arată gri pare că nu merge, iar cel neales pare cel activ. Verificatorul îl prinde (`lot12`, `ALEGERE_DEZACTIVATA`).
- Acțiuni asincrone: butonul se dezactivează + text "Se salvează…" / "Se trimite…" pe durata cererii.

**INTERZIS**: clase de buton în afara setului (ex. `buton-ingust` — folosește margin/width inline pentru dimensionare, nu clasă nouă). Prins de regula BUTOANE din verificator (v2.5 — `buton-ingust` scos și din lista albă a verificatorului, era o excepție greșită).

## 2. Pattern fundamental: nimic vizibil decât la selecție

- Un ecran arată la deschidere DOAR: titlu + informația de stare esențială + itemii de meniu (`.acces-card`/`.meniu-card`) sau lista care e scopul ecranului.
- Formularele de adăugare/editare/configurare NU apar la deschidere — apar la apăsarea unui buton dedicat.
- Excepție: ecranele-formular, unde formularul ESTE scopul (Raport Z, Bilanț, Emitere factură).
- Formularele deschise la selecție au întotdeauna buton "Renunță" (`.btn-link` sau `.buton-secundar`) care revine la ecranul anterior.
- **Ascuns = invizibil (v2.74, lotul 07.10 pct.20):** un element cu atributul `hidden` nu se vede, orice `display` ar avea în stil sau în clasă — regula globală `[hidden] { display: none !important; }` din `stil.css`. INTERZIS `hidden` împreună cu `style="…display:…"` pe același element (instanța: „NIR nou” deschis fără să fie cerut, plus Casa ×2 și Încasări/plăți). Gard: verificator `HIDDEN_CU_DISPLAY`.

**IMPORTANT (v2.0)**: Formularele NU se învelesc într-o casetă albă (`background:#fff`). Stau direct pe fundalul ferestrei (gri); doar câmpurile de input sunt albe cu bordură #b9c2cf. Un wrapper alb pe fundal gri-deschis face caseta invizibilă.

**Clasa de câmp (v2.1)**: input/select normale poartă exclusiv `.camp-input` (înălțime 40px, bordură vizibilă #b9c2cf, font aplicație). INTERZIS `.mig-text` pe input/select — e croită doar pentru textarea ecranului de migrare (font monospace, bordură 0.5px invizibilă pe alb). Structura canonică de câmp: `<label class="camp"><span class="camp-eticheta">Etichetă</span><input class="camp-input"></label>` — nu `<label>text<br><input>`.
**Checkbox cu etichetă (v2.11)**: un checkbox însoțit de text-etichetă poartă EXCLUSIV `.set-bifa`. Structura canonică: `<label class="set-bifa"><input type="checkbox"> <span>Text</span></label>`. INTERZIS checkbox cu etichetă-text pe `style` inline (font-size, display) sau clase ad-hoc (`.cm-check`). Excepție: checkbox-urile fără text alături (în tabele/liste, doar bifă) nu au nevoie de `.set-bifa`. **Ținta de clic (02.10.2026, decizia Costin):** căsuța rămâne 16×16px; ținta de atingere este ETICHETA întreagă (`<label>`), care are `min-height: 24px` în regula globală (WCAG 2.5.8 AA). Nu se mărește căsuța. Verificator: `TINTA_BIFA`.

## 2a. Deschiderea cardurilor: MEREU fereastra (modal), niciodata inline
- Orice card din grila cabinetului (`.cab-card`) se deschide EXCLUSIV prin `nav.deschide(titlu, corp, opt)` — fereastra overlay cu X.
- INTERZIS ca un card sa se deschida inline in corpul panoului (sa suprascrie `.cab-grila`/`continut`). Un card = o fereastra.
- Meniurile cu sub-optiuni (ex. Firme, Activitate) sunt tot ferestre: sub-optiunile devin `.meniu-card` in corpul ferestrei, NU un al doilea nivel inline cu breadcrumb.
- Consecinta: in corpul panoului nu apare breadcrumb ("Panou > X") si nici al doilea rand de sageti. Inchiderea se face din X-ul ferestrei.
- **Pagina principală are aceeași structură la ambele roluri (v2.88, 12.10.2026, comanda Costin, deficiențele 225 + 231: „«Recomandă» și
  «Suport» sunt două benzi înguste, una lângă alta, deasupra cardurilor, la ambele roluri, ca la Cabinet.” · „la Ana, scoate meniul din
  stânga care repetă cardurile. Pagina principală are aceeași structură la ambele roluri.”).** La contabilul-șef și la asistent: banda de
  salut (`.cab-salut`: titlul paginii și data în stânga; în dreapta benzile `.cab-banda` „Recomandă” — chihlimbar — și „Suport” — ardezie
  —, una lângă alta, scunde), apoi grila de carduri `.cab-grila`. FĂRĂ meniu lateral; „Recomandă” și „Suport” nu sunt carduri în grilă.
  Un singur loc o scrie: `salut.js` (`paginaPrincipala`, `legaBenzile`). Gard `PAGINA_PRINCIPALA_UNA` (verificator) + proba în browser
  `frontend_test/proba_pagina_principala.py` / `core/test_pagina_principala.py` (structura, benzile deasupra cardurilor, înălțimile).

- **Antetul aplicației rămâne fix la derulare (lotul 8, 18.10.2026 — comanda Costin 7.3 pct.3).** `.bara-antet` (bara de sus, bara de stare, bara 3) are `position: sticky; top: 0` în `.desktop`, care derulează el însuși (cap.22 §7, 321): anunțul „Versiune nouă” din bara de stare rămâne pe ecran oricât se derulează. Gard `BARA_ANTET_FIXA` (verificator). **Excepție (19.10.2026):** cât e deschisă o fereastră, antetul revine la `position: relative` (`body:has(.fereastra-overlay)`) — `sticky` cu z-index ar face din el un context de suprapunere, iar „Versiune nouă” n-ar mai fi apăsabil peste stratul ferestrei (deficiența 191, e2e `test_def_191_…`).
- **Barele aplicației au înălțime minimă, nu fixă (v2.87, 11.10.2026, deficiența C8).** `.bara`, `.subbara`, `.bara3`, `.subbara--admin`: `min-height`, iar bara de stare se rupe pe rânduri (`flex-wrap`). Pe telefon un mesaj lung din bara de stare ieșea din bara de 40 px și acoperea „?” din bara de sus (atingerea ajungea la mesaj). Gard `BARA_INALTIME_MINIMA` (verificator) + plasa `e2e_comanda_1010.py::test_def_c8_…` (pe 393 px, atingerea din mijlocul fiecărui buton al barelor ajunge la el).

## 2b. Carduri inactive (feature neconstruit)
- Un card al carui ecran nu exista inca poarta EXPLICIT `activ: false` in definitie.
- Aspect canonic: `disabled` + `style="opacity:.55;cursor:default"` (estompat, ne-clicabil).
- Marcaj text: descrierea cardului se termina cu ` \u00b7 in curand` (` · in curand`).
- La click NU se intampla nimic (butonul e `disabled`) — INTERZIS card inactiv care deschide fereastra goala sau crapa.
- Cand feature-ul se construieste: se seteaza `activ: true`, se leaga functia de randare, se ELIMINA marcajul "in curand". Un card `activ: true` fara ecran in spate = neconform (crapa la click).
- Orice card din meniul unei firme (`firme-optiune`) TREBUIE sa aiba campul `activ` definit explicit (true sau false), niciodata absent.

## 3. Navigare

- Săgeata portocalie (`.btn-nav`) duce MEREU exact un pas înapoi în ierarhia ecranului.
- Mecanismul: `nav.setInapoi(fn)` — obligatoriu apelat la începutul FIECĂRUI sub-ecran: rădăcina cu undefined/null, sub-ecranele cu funcția părinte.
- Ordinea la „←” (lotul 12, C140): (1) pasul intern declarat de ecran cu `setInapoi(fn)`, o singură dată; (2) pasul de pe traseu (`nav.mergi`); (3) fereastra. Rădăcina = ecranul dat lui `nav.deschide` / `nav.mergi`; ea NU declară ca pas intern ecranul altei ferestre (gard `core/test_lot12_inapoi_sageata.py`). Un ecran redesenat de la început pornește fără pas intern; `nav.reiaPasul()` redesenează pasul curent de la început.
- X-ul închide fereastra de oriunde. Săgeata nu ține locul lui X.
- Ecranele-poartă (configurare obligatorie) primesc `setInapoi(undefined)` ca să evite bucla.
- **Ce s-a tastat nu se pierde (v2.67, comanda Costin 05.10.2026).** Gard `PASTRARE_FORMULAR`. O fereastră sau un pas în care omul a
  tastat (`input`/`change`) își păstrează elementul `.fereastra-corp` când se deschide altceva peste el (`nav.deschide`, `nav.mergi`) și îl primește înapoi la
  revenire, cu evenimentul `nav:revenire` (nu o redesenare). Sesiunea expirată se reautentifică PESTE ecran (`reautentificare.js`),
  iar cererea refuzată se reia; anunțul „versiune nouă” nu reîncarcă peste un formular început. Un mesaj nu promite păstrarea
  decât unde mecanismul o face. Gard: verificator `PASTRARE_FORMULAR` + `core/test_sesiune_fara_pierdere.py`.

## 4. Casete de date

- Orice bloc de date (tabel, totaluri, liste) stă în casetă pe FOND ALB cu bordură 1px var(--linie), distinct de fundalul ferestrei.
- **O casetă de date cu derulare proprie e focusabilă (v2.91, 14.10.2026):** `tabindex="0"` și `aria-label` pe elementul care derulează (ex. `.mig-sold-tabel`, cu `max-height` + `overflow-y: auto`) — pe telefon, cu rânduri lungi, conținutul se derulează și trebuie atins din tastatură (WCAG 2.1.1, axe `scrollable-region-focusable`). Aceeași regulă ca `.fereastra-corp` (v2.57). Gard: `core/test_fereastra_focusabila.py`.
- Tabele: titlurile și valorile la STÂNGA, cu excepția coloanelor de sume monetare — titlu și valori la DREAPTA (separator zecimal pe aceeași verticală).
- **Toate datele se afișează prin `dataRo(d, stil)` din api.js** (v2.0). SINGURA formatare de dată. Stiluri: implicit `zz.ll.aaaa`; `cu_ora` → `zz.ll.aaaa HH:MM`; `lung` → `11 iulie 2026`; `zi_luna_text` → `11 iul`; `luna_an` → `iulie 2026` (perioade lunare fără zi — balanțe, deconturi; v2.20); `zi_luna` → `zz.ll` (compact). Pentru date care pot **traversa anul** (ex. termene în fereastra de 60z care intră în an+1) se folosește un stil cu an (`lung`/`scurt`/`luna_an`), NU `zi_luna`/`zi_luna_text` (ambiguu). INTERZIS `toLocaleDateString` ad-hoc, date ISO brute în template (`${x.data}` direct), funcții locale de formatare a datei (`fmtZi`/`fmtD`/`fmtTermen`, **funcție/array local de nume de luni indexat prin `parseInt` — ex. `luni[parseInt(p[1])-1]`, forma `dataLunga`, v2.20**). Regula DATA_DIALECT în verificator prinde și această formă (array de luni indexat cu `parseInt`); NU atinge pickerele de lună (`LUNI.map(...)` pentru `<option>`) sau etichetele din stare (`LUNI[S.luna-1]`, fără `parseInt`) — acelea sunt legitime.
- **Cantitățile se afișează prin `cantitate(v, um)`, costul unitar prin `pretUnitar(v)` (v2.69, 05.10.2026).** Gard `CANTITATE_BRUTA`. Stocul, cantitatea unei mișcări sau a unei linii, inventarul: `cantitate(v, um)` din api.js — „110 buc”, „1,5 kg”, fără zecimalele coloanei NUMERIC(12,3) („stoc 110.000”, „x2.000”). Costul unitar (CMP, prețul de intrare): `pretUnitar(v)` — 2–4 zecimale, cu „lei” („CMP 50.0000” → „50,00 lei”). În backend, textul pentru om folosește `pdf_util.cantitate`. EXCEPTAT: `value` de `<input type="number">` și payload-ul trimis serverului.
- **Cursul valutar se afișează prin `cursValutar(v)` din api.js (v2.101, 22.10.2026, lotul 11, C88).** Cum îl dă BNR, pe unitate: 4–6 zecimale („5,2409”; HUF „0,014719”), nu rotunjit la 4 (HUF „0,0147” dă o eroare de 0,13% pe sumă). Gol -> „—”. INTERZIS `toLocaleString(…{ minimumFractionDigits: 4 })` local pe un curs. În backend, textul pentru om folosește `curs_bnr.curs_text`. Gard `CURS_FORMAT_LOCAL`. EXCEPTAT: `value` de `<input type="number">` și payload-ul.
- **O dată produsă în interfață se scrie prin `dataIso(d)` (v2.68, 05.10.2026).** Gard `DATA_UTC`. Valoarea unui câmp de dată, „azi”, un termen calculat sau capetele unui interval se produc în ora LOCALĂ, prin `dataIso(d)` din api.js (fără argument: azi). INTERZIS `toISOString().slice(0, 10)` / `.split("T")` pentru o dată calendaristică: convertește în UTC, deci între 00:00 și 03:00 „azi” devine ieri, iar o dată construită la miezul nopții local (`new Date(an, luna, 1)`) iese cu o zi mai devreme — „luna” începea din ultima zi a lunii trecute, „UIT valabil până la” arăta o zi mai devreme. `toISOString()` întreg rămâne permis pentru un moment (marcaj de timp), nu pentru o zi.
- **Perioadă lună/an NUMERICĂ (v2.21, 27.07.2026)**: `luna_an_numeric` — `07/2026`. DECIS de Costin: antetele de ecran (Firme, Facturi) folosesc forma NUMERICĂ, nu `iulie 2026`. Motiv: e mai scurtă, se aliniază în listă cu restul cifrelor și e forma cu care lucrează contabilul pe declarații. `luna_an` („iulie 2026") rămâne pentru titluri și texte narative (balanțe, povestea lunii). Ambele trec prin `dataRo` — formatarea locală cu `padStart` rămâne INTERZISĂ (cap.4: o singură funcție de formatare).
- **Toate sumele afișate se trec prin `bani(v)` din api.js** (v2.1). SINGURUL formator monetar. Produce format românesc (1.234,56). INTERZIS `toFixed(2)` pe sume afișate (dă `1234.56`, nepotrivit), formatări locale sau concatenare brută. Excepții permise: `value` de `<input type="number">` și payload trimis la backend (acolo se cere punct zecimal). Moneda (`lei`/`RON`) se afișează când suma stă izolat sau unitatea nu e evidentă (total factură, fluturaș, indemnizație, sold); se omite în liste/tabele dense unde contextul o face redundantă (cost/porție, coloane cu antet monetar). `bani()` e mereu obligatoriu; moneda e contextuală. INTERZISE funcții locale de format monetar (`const fmt = …toLocaleString`) — dialect care produce formate divergente (0 vs 2 zecimale). Procentele NU folosesc `bani()` (ar da `19,00%`); pentru ele funcție separată (`pct`) sau `%` simplu. Pentru cifre de ansamblu rotunjite la leu (cockpit cabinet, cifrele firmei pe portalul client) → `baniRotund(v)` canonic (0 zecimale), NU dialect local. Orice `const X = …toLocaleString("ro-RO")` local (sub orice nume, nu doar `fmt`) e INTERZIS și prins de FMT_LOCAL. Cantități fără zecimale inutile. Procente compacte (11%).
- **BACKEND (Python) — text destinat utilizatorului: aceeași regulă, alt limbaj** (v2.15, 22.07.2026). Orice sumă sau dată construită în backend care ajunge la utilizator (câmpurile `mesaj` / `temei` / `cauza` / `motiv` / `avert` / `descriere` / `actiune`, mesaje de eroare afișate, corp/subiect de email, text pe PDF) se formatează prin sursele canonice **`pdf_util.bani(x, mon)`** (sume, 1.234,56) și **`pdf_util.data_ro(d, stil)`** (date — oglinda Python a lui `dataRo`; stiluri `scurt`/`cu_ora`/`lung`/`zi_luna`). INTERZIS `f"{x} lei"` / `%d lei` brut, `str(sold)`, `strftime("%d.%m…")` local pentru afișare. Motiv: gărzile JS nu văd backendul — o sumă „40800.00 lei" sau o dată ISO brută trimisă din Python scapă complet controlului (dovedit F183, 22.07). Regula **BACKEND_UI_BRUT** în verificator (scanează `.py`). EXCEPTAT (nu e afișare): XML/SAF-T (ISO cerut de spec — etransport, D406), exporturi cu format al destinației (WinMentor), câmpuri de dată ISO în JSON API (formatate client-side prin `dataRo`), log-uri/print, valori unitare `:g` intenționate. Șabloanele `.format()` din `common.CODURI` se formatează CENTRAL în `common.problema()` (bani pe câmpurile din `MONEDA_CAMP`) — orice câmp monetar nou dintr-un șablon se adaugă acolo.
- Etichetă și valoare pe același rând se separă clar (flex space-between + gap).
- **Seria și numărul, separat — `numarCuSerie` (v2.99, lotul 11, deficiența 443; comanda Costin 11.1 pct.19, verbatim: „seria și
  numărul se afișează separat peste tot (F6 nr. 1, nu F61)”):** orice document cu serie se afișează „<serie> nr. <număr>” — „F6 nr. 1”, „F1A nr. 3”, „KAI nr. 12”
  (separatorul de la capătul seriei nu se afișează); fără serie, numărul cum e („BA-1”). O singură formă: `numarCuSerie(serie, numar)` în
  api.js, `pdf_util.serie_nr(serie, numar)` în backend (refuzuri, descrierea notei, Registrul jurnal: „Factură F6 nr. 1 din 05.10.2026”).
  Numărul unei facturi emise poartă deja seria în față („F1A3”) — helperul o taie. `pdf_util.numar_cu_serie` (seria lipită) rămâne NUMAI
  pentru IDENTIFICATORUL trimis la ANAF (ID-ul facturii în e-Factura, BT-1 / BT-25). INTERZIS `${serie}${numar}`, `${serie}-${numar}`,
  `(serie || "") + numar`, `[serie, numar].join` în ecrane. Un termen afișat spune al cui e („termen de transmitere în SPV”, „termen de
  depunere”), nu „termen” singur. Gărzi: verificator SERIE_LIPITA + `core/test_lot11_u0_serie_nr.py` (Python, cu locurile de identificator
  numite).
- **Perioadele au TREI forme, una pe fel (v2.85, 09.10.2026, lotul „Retest 2” pct.14):** luna `LL/AAAA` (`07/2026`), trimestrul
  `T3/2026`, anul `2026`. În backend: `control_fiscal_api.perioada_canonica(an, luna, fel)`; în ecran: `dataRo(…, "luna_an_numeric")`
  și `T${trim}/${an}`. INTERZISE pe ecran „03.2026”, „iun 2026”, „T3 2026” / „T3” fără an. Textul narativ poate spune „iulie 2026”
  (`luna_an`), nu o formă a treia.
- **Textul de pe ecran se judecă pe ECRAN, nu în sursă (v2.85, Retest 2 pct.2)** — `core/limba_ecran.py` + `core/test_text_ecran.py`.
  Decizia Costin: „verificarea se face pe ecranul afișat, cu valorile din date și din enumerări, nu pe șirurile din codul sursă”.
  `core/limba_ecran.py` judecă textul citit din
  browser (`frontend_test/vizual/text_ecran_scan.py`, toate cardurile firmelor de test, desktopul cabinetului și declarațiile
  generate): cod (`nume_cu_underscore`, `modul.atribut`, `x=1`, `->`, proveniența internă — „decizia Costin”), diacritice (lexiconul
  derivat din corpusul legislativ, `core/lexicon_diacritice.json`, și „în afară” urmat de substantiv), majuscule de accent, sumă cu
  punct zecimal, dată ISO, perioadă în altă formă decât cele trei, acord („1 parteneri” — `common.cate`), prescurtări de programator
  („fact.vânz”), jargon („persistat”, „amprenta”). Artefactul `frontend_test/vizual/text_ecran.json` (cu `ui_hash`) e păzit de
  `core/test_text_ecran.py`. Gardul de sursă (`core/test_text_afisat_limbaj.py`) rămâne prima plasă și citește și mesajele
  excepțiilor de domeniu (`raise ValueError("…")` ajunge pe ecran ca refuz); un `raise` care nu ajunge la contabil (argumentul
  greșit al unui apelant, un registru din cod) poartă `# invariant-intern-ok: <motiv>`, cu plafon.
- **Un rând de declarație se numește pe ecran cu RÂNDUL FORMULARULUI, nu cu atributul XML (v2.85).** D300: `d300_randuri.
  rand_formular("R17_2")` → „rândul 19, coloana TVA” (formularul OPANAF 174/2026 a renumerotat de la rd.17, atributele XML nu);
  D101: `d101_randuri.rand_d101("P081")` → „rândul 8.1”. Gărzi: `core/test_d300_rand_formular.py`, `core/test_d101_rand_formular.py`
  (citesc formularul din `anaf_surse/`). Diferențele porților de reconciliere se scriu prin `pdf_util.diferenta` („în declarație
  9.999,00 lei, recalculat 1.500,00 lei (diferență 8.499,00 lei)”), nu „generator=9999 vs cale2=1500”.

## 5. Casete de atenționare, confirmări și INPUT

- Stil unic pentru atenționare și refuz: `.caseta-atentie` — fundal #fdf3f3, bordură 2px #d98c8c, mesaj în `.ca-mesaj`. Butoanele stau SUB casetă, pe clase canonice.
- **Întrebarea de confirmare (v2.102, lotul 12, 446.1):** `confirmaCaseta` o desenează în `.caseta-intrebare` — casetă NEUTRĂ (fundal alb,
  bordură gri, margine stângă albastră), cu întrebarea și cele două butoane pe un rând (se rup pe ecran îngust); niciodată `.caseta-atentie`:
  roșul rămâne al refuzului și al erorii. Ireversibilitatea se spune în text, nu prin culoare. Pusă în locul butonului principal, bara de jos
  crește cu cel mult 32 px. Aceeași casetă la întrebările scrise în ecran (motivul deblocării lunii, `cereMotivDeblocare`). Gard:
  `core/test_lot12_form2_confirmare.py`.
- **Casetă informativă standing (v2.12)**: `.caseta-info` — fundal albastru-pal #eef4fd, bordură 1px #b9c2cf, mesaj în `.ci-mesaj`. Pentru o notă IMPORTANTĂ, PERMANENTĂ, informativă (nu o confirmare, nu un mesaj de stare tranzitoriu prin `arataMesaj`). Distinctă semantic de `.caseta-atentie`: roșul rămâne EXCLUSIV pentru atenționare/acțiune distructivă; informația neutră NU se colorează roșu. INTERZIS o notă informativă ad-hoc cu fundal albastru-pal inline (`style="background:#eef4fd…"`) — se folosește `.caseta-info`. Prins de regula CASETA_INFO în verificator.
- **Casetă-poartă la o acțiune (v2.14)**: `.caseta-poarta` — o întrebare OBLIGATORIE înainte de o acțiune consecventă, cu DOUĂ alegeri care merg AMÂNDOUĂ înainte (nu confirmă/anulează — pentru acela e `confirmaCaseta`). Cazul canonic: emiterea unei facturi cu linii de stoc la o firmă cu gestiune cantitativă — „Pleacă marfa acum? DA (descarcă gestiunea) / NU (doar fiscal)". Structura: `.caseta-poarta` > `.cp-mesaj` (întrebarea + consecința) + `.cp-butoane` (butoanele canonice). Fundal neutru chihlimbar-pal #fbf7ee — distinct de `.caseta-atentie` (roșu, distructiv) și `.caseta-info` (albastru, informativ standing). Răspunsul e cerut ÎNAINTE de acțiune și NU se poate sări (nu bifă opțională, care se uită). INTERZISĂ reproducerea ad-hoc cu fundal inline (`style="background:#fbf7ee…"`) — se folosește `.caseta-poarta`. Prinsă de regula POARTA_INLINE în verificator.
- **`confirm()`, `alert()` și `prompt()` native de browser sunt INTERZISE** (v2.0 — include prompt). Confirmări via `confirmaCaseta(zona, mesaj, laConfirm, {textOk})`. Input via formular în-ecran (câmp + buton), niciodată prompt nativ.
- Mesajul spune exact ce se întâmplă și dacă e ireversibil.

- **„Pleacă marfa acum?” — o singură implementare (v2.95, 19.10.2026, decizia Costin C63):** întrebarea are o singură implementare,
`intrebarePleacaMarfa` din `ecrane/emitere_ecran.js` (casetă-poartă, v2.14); o folosesc emiterea din formular și „Transformă în factură”
(detaliul proformei / avizului, în `#fd-act-rez`). Serverul o cere prin refuzul `INTREABA_PLEACA_MARFA`, după aceeași condiție
(`facturi_api.poarta_marfa_ceruta`). Un drum nou care emite o factură cu articol de stoc refolosește funcția; nu reproduce caseta.

## 6. Mesaje de stare, câmpuri obligatorii și ghidaj

- **Câmpul cu un buton pe rândul lui (v2.102, lotul 12, 642):** `.camp-cu-buton` (ex. CUI + „Verifică la ANAF”): eroarea vine sub rând
  (`api._ancoraCamp`), ca la `.data-golibila`. Plasa „refuz nevăzut” socotește arătat un refuz când textul lui (cu spațiile strânse) sau
  FIECARE eroare de câmp a lui e în pagină: un refuz, un singur loc vizibil.
- **Datele aduse de la ANAF țin de CUI-ul lor (v2.102, lotul 12, 459.1; comanda Costin 12.2 pct.5: „la schimbarea CUI-ului denumirea adusă
  de la CUI-ul anterior rămâne completată”):** un formular în care ANAF completează câmpuri din CUI (denumirea; la factură și adresa,
  localitatea, județul) le leagă prin `legaDateAnaf` (`ecrane/date_anaf.js`): la schimbarea CUI-ului, valoarea pusă de ANAF și neatinsă de
  om dispare, iar rândul de stare de sub CUI se golește; ce a scris omul rămâne (F188). Completarea automată (fără apăsare) nu scrie peste
  ce a scris omul; „Verifică la ANAF” (cerere explicită) scrie. Primele: Adaugă firmă, NIR, casa. Rândul de sub CUI spune ce a dat ANAF
  și ce se preia la creare, fără „— verifică.”. Gard: `core/test_lot12_ui2_ecrane.py::test_def_459_1_*`.
- **Alegerea firmei într-un formular = UN control (v2.66, comanda Costin 05.10.2026):** `<select>` cu „— alege firma —”, forma de la Declarații. Nu un câmp „Caută firma” plus o listă derulantă pentru aceeași alegere (instanța: Pachete lunare). Lista de bife a firmelor unui asistent (o alegere multiplă) nu e în regulă. Gard: verificator `ALEGERE_FIRMA_DUBLA`.

- Succes: text verde #1d7a4d, weight 600, afișat pe ecranul principal DUPĂ revenirea din formular.
- `arataMesaj(el, txt, tip)` — singura cale de afișare a mesajelor de stare. Tipuri canonice: `eroare` (roșu), `avert` (galben), `info` (gri), `ok` (verde, succes). INTERZIS mesaj de stare prin innerHTML cu clase ad-hoc (`mig-gol`, `pf-intro`, span inline).
- Eroare de câmp/formular: `<span class="msg-eroare">` (roșu), lângă câmpul/butonul relevant. Niciodată tăcere la o acțiune eșuată.
- **Un mesaj, o singură dată; o listă, rând cu rând (v2.89, retestul Costin 12.10.2026, deficiențele 237, 238):** același mesaj nu apare
  de două ori pe ecran — o notă de lângă butoane care ar repeta refuzul de dedesubt trimite la el („motivul e mai jos”) **[înlocuit în
  v2.99, 440: refuzul stă lângă buton, cu textul lui, o singură dată — „Fără «motivul e mai sus»”]**. Un mesaj cu mai
  multe elemente (un rând pe cont, cu suma și acțiunea) vine cu rândurile despărțite (`\n`), iar zonele de mesaj (`.msg-eroare`,
  `.msg-avert`, `.msg-info`, `.msg-ok`, `.dec-eroare` — caseta refuzului generării; caseta erorilor DUK, făcută din blocuri, nu: `.dec-eroare:has(> .dec-avert-cap)`, v2.100 / lotul 11) le păstrează (`white-space: pre-line`). Gard: verificator MESAJ_PE_RANDURI + e2e 237 / 238.
  **Orice casetă care afișează textul serverului (`e.mesaj`, `detaliu.mesaj` …) e zonă de mesaj (v2.100, lotul 11, 440):** clasele cu
  un singur fel de conținut au `pre-line` pe clasă, într-o regulă comună (`.dec-avert-cap`, `.pacm-mail`, `.cp-mesaj`, `.val-lipsa`,
  `.anunt-text`, `.mig-eroare`, `.cf-semnal`, `.rn-mesaj`); într-o clasă de proză (`.ecran-nota`, `.ca-mesaj`, `.tip-desc`,
  `.em-cui-stare`), scrisă în sursă pe mai multe rânduri, `pre-line` NU se pune pe clasă — caseta refuzului poartă și `.pe-randuri`.
  Gard: `core/test_lot11_g2_pre_line.py` (fiecare `${esc(x.mesaj…)}` / `el.textContent = x.mesaj` din `static/js`).
- **Mesajul nu șterge formularul în care e pus (v2.82, 08.10.2026):** `arataMesaj` pe un container care ține câmpuri (`input`,
  `select`, `textarea`) scrie mesajul într-un copil propriu (`.msg-in-formular`, la capătul containerului), nu peste conținut — omul nu
  pierde ce a tastat. O zonă de mesaj fără câmpuri se rescrie ca înainte. Regula stă în mecanismul unic (`api.js`), nu în fiecare ecran;
  gard în browser `core/test_mesaj_in_formular.py` (găsit la proba „depusă în afara iConta”: „Salvează” fără dată ștergea formularul).
- **Mesajul de după un buton se aduce în vedere (v2.74, lotul 07.10 pct.3):** un refuz, o întrebare sau o confirmare apărute după apăsarea unui buton se derulează în zona vizibilă — prin `aduInVedere` din `api.js`, chemat de `arataMesaj`, `eroareCamp`, `confirmaCaseta`, iar casetele scrise direct de un ecran (`.caseta-poarta`, `.em-curs-box`, `.msg-*`, `[role=alert]`) le prinde observatorul după clasă (`SELECTOR_MESAJ`). Fără apăsare recentă nu se derulează nimic. O casetă nouă de după-buton cu altă clasă intră în `SELECTOR_MESAJ`. Gard: verificator `MESAJ_FARA_ADUCERE_IN_VEDERE`. **Linia de stare a ecranului nu se aduce în vedere (lotul 12, 171):** o zonă care spune starea citită la deschiderea ecranului și la fiecare redesenare (starea SPV a firmei, `spv_stare.randeazaStareSpv`) poartă `data-stare-ecran`; `aduInVedere` n-o derulează, oricât de aproape de un clic s-ar scrie — altfel ecranul sare după fiecare acțiune care îl redesenează. Gard: e2e `test_def_171_*`, `core/test_lot12_stare_ecran.py`.
- **Refuzul care trimite în alt ecran are buton spre el (v2.74, lotul 07.10 pct.2):** serverul pune ținta în refuz (`detail.ecran`); butonul „Deschide <ecran>” se adaugă lângă mesaj de `api.js`, oriunde e afișat, iar ecranul se deschide PESTE formular (← îl readuce; după salvare, „Înapoi la <formular>”). Ecranele-destinație stau în `ecrane/ecran_destinatie.js` (`ECRANE`). INTERZIS un refuz cu ținta numai în frază („Declar-o în Date firmă”) fără `ecran`. Gard: verificator `REFUZ_ECRAN_FARA_BUTON`.
- Validări preventive cu mesaj explicativ, nu doar refuz.
- **Câmpul care se citește, nu se scrie (v2.92, lotul 6, deficiența 272):** e `<input class="camp-input" readonly aria-readonly="true">`,
  cu `.camp-ajutor` care spune de ce și pe unde se schimbă: o valoare pe care ecranul o arată, dar n-o lasă de modificat (CUI-ul în
  Date firmă — se corectează numai pe operațiunea separată a administratorului). Arată needitabil prin regula GLOBALĂ
  `.camp-input[readonly]` din `stil.css` (fundalul paginii, fără cursor de scriere) — nu prin stil pe ecran. Un buton pus sub câmp
  (`.camp > button`) nu se întinde pe lățimea lui. Gard: verificator FEREASTRA_LOT6 (READONLY_GLOBAL) + e2e `test_def_272_*`.
- **Eroarea dispare când câmpul e corectat (v2.92, lotul 6, deficiența 290 — clasă, toate formularele):** la orice schimbare a unui câmp
  (tastare, alegere, fișier atașat) dispar eroarea lui (`eroareCamp`, cu marcajul roșu) și refuzul de formular din aceeași zonă
  (`form` / fereastra de lucru; toate dialectele zonei: `msg-`, `mig-`, `dlg-`, `login-eroare` — `api.ZONE_EROARE_FORMULAR`): formularul nu mai e cel refuzat. Un singur mecanism, în `api.js` (`stergeEroriDupaCorectare`, faza de
  captură — o eroare nouă pusă de handlerul ecranului rămâne); ecranele nu-l repetă. Refuzul de pe un rând (`refuzPeRand`) nu ține de
  formular și rămâne. Gard: verificator FEREASTRA_LOT6 (ERORI_DUPA_CORECTARE) + e2e `test_def_290_*`.
- **Acțiunea principală și mesajul ei se văd mereu (v2.92, lotul 6, deficiența 285):** stau într-o `.bara-fixa` — la un formular lung,
  bara de acțiune și zona ei de mesaj, lipite de marginea de jos a ferestrei cât se derulează conținutul: Declarații pasul 2 („Trimite în
  coadă →” + refuzul), Date firmă („Salvează” + mesajul), Emite factură. Gard: e2e `test_def_285_*` (D300 cu toate secțiunile deschise:
  butonul în fereastră, zona lipită jos). O bară urmată de alt conținut (nota de subsol a
  declarației, jurnalul din Date firmă) nu-l acoperă: marginea ei negativă de jos se aplică numai ultimului element
  (`.fereastra-corp .bara-fixa:not(:last-child)` → `margin-bottom: 0`; verificator FEREASTRA_LOT6 / BARA_NU_ACOPERA, e2e `test_def_164_*`).
- **Caseta de refuz nu stă sub antetul lipit sus (lotul 11, 436 afișare):** zona de mesaj a `.bara-fixa` (`[id$="-mesaj"]`, `[id$="-msg"]`) are cel mult 35vh și derulează ea (precedentul `.em-rezultat`, 304), ca bara să nu treacă pe sub `.rezumat-fix`; orice element adus în vedere în corp se oprește sub antet (`scroll-margin-top: calc(var(--rezumat-h) + 8px)`). Lângă butoanele „Deschide nota …” refuzul nu enumeră notele (`mesaj_langa_note`). Gard: verificator FEREASTRA_LOT6 / CASETA_SUB_ANTET, e2e `test_def_436_caseta_de_refuz_*`.
- **Avertismentul înlocuirii, o singură dată (v2.98, lotul 11, 424/446):** la un import care înlocuiește date existente, avertismentul apare o dată, prin `arataMesaj(…, "avert")` — nu e o eroare; confirmarea e o întrebare scurtă (`confirmaCaseta`), iar butonul principal e ascuns cât e deschisă (cap.9, „Fereastra cu tabel”, pct.5). Gard: `core/test_lot11_m_ferestre_import.py`.
- **„NU s-a salvat” lângă butonul apăsat, cu lista câmpurilor (v2.93, 19.10.2026, comanda Costin 9.2, deficiența 410 — clasă, TOATE
  formularele; verbatim: „la orice Salvează refuzat «NU s-a salvat» lângă buton + lista tuturor câmpurilor lipsă cu trimitere; nu se
  pierde ce s-a scris”):** după apăsarea unui buton care scrie (`data-actiune` cu POST / PUT / PATCH / DELETE, sau fără declarație — nu
  cel declarat numai de citire și nici cel `data-fara-actiune`), orice refuz de câmp
  (`eroareCamp`, și erorile de câmp ale serverului) și orice refuz de formular (`arataMesaj(…, "eroare")`) se adună în
  `.refuz-salvare` (role=alert), imediat după rândul butonului: „NU s-a salvat.”, apoi fiecare câmp cu eticheta lui și trimitere (clic =
  câmpul în vedere, cu focus; un `<details>` închis se deschide), iar refuzul fără câmp vine cu textul lui întreg (v2.99, 440; până la
  v2.98: „motivul e mai jos”, fără să-l repete). Câmpul corectat iese din listă, lista goală dispare. Un singur mecanism, în `api.js` (`refuzSalvare`), chemat de
  helperii comuni — ecranele nu-l repetă. Gard: verificator REFUZ_SALVARE + e2e `test_def_410_*`.
- **Toate erorile deodată, fiecare cu textul ei, în casetă și lângă câmp (v2.99, lotul 11, deficiența 440 — clasa, toată aplicația;
  comanda Costin 11.1 pct.16, verbatim: „toate erorile apar deodată, fiecare cu textul ei, în casetă și lângă câmp. Fără «motivul e mai
  sus». Pe toată aplicația.”):**
  1. caseta „NU s-a salvat.” de lângă butonul apăsat (`refuzSalvare`) spune FIECARE eroare cu textul ei: câmpul cu eticheta și motivul,
     refuzul de formular cu textul lui întreg, eroarea de câmp fără câmp pe ecran cu textul ei. Excepția: refuzul de formular a cărui zonă
     stă chiar lângă buton (în rândul lui sau imediat deasupra / dedesubtul lui) nu se copiază — se citește acolo, o dată. INTERZISE trimiterile fără text:
     „motivul e mai sus / mai jos”, „corectează câmpul marcat mai sus”, „(vezi mai sus)”, „motivele mai jos” (ecran și server);
  2. eroarea de câmp stă lângă câmp (`eroareCamp`), cu `aria-invalid` și `aria-describedby` spre textul ei (descrierile proprii ale
     câmpului rămân; legătura pleacă la corectare);
  3. refuzul serverului cu `erori_campuri`: helperul unic `arataRefuzul(root, e, zona, {campuri})` pune fiecare eroare lângă câmpul ei și
     textul în zona formularului; un ecran care arată numai `e.mesaj` primește oricum marcajul câmpurilor (api.js, după `catch`-ul lui,
     pentru câmpurile din fereastra butonului). Ecranele nu-și mai scriu bucla lor;
  4. validarea din ecran le marchează pe toate (`cereCompletate(root, campuri)` + `cereAlegerile`, legate cu `|`, nu `return` după primul);
     serverul le adună pe toate în `erori_campuri` (DS v2.30 pct.4 — „fail-fast e INTERZIS pe formularele multi-câmp”), inclusiv lista deja
     adunată, nu `er[0]`.
  Gărzi: verificator ERORI_TOATE + `core/test_lot11_u0_erori.py` (în browser) + `core/test_lot11_u0_verificator.py` (și textele din core/)
  + e2e `test_def_440_*`.
- **Câmpul de dată opțional se poate goli (v2.99, lotul 11, deficiența 441; comanda Costin 11.1 pct.17, verbatim: „orice câmp de dată
  opțional se poate goli.”):** orice `input[type=date]` opțional (fără `required` / `aria-required` / `data-obligatoriu`, fără `.oblig` în
  etichetă, editabil) primește lângă el butonul „×” („Golește data”, `.data-goleste`, în `.data-golibila` — un rând, fără înălțime în
  plus), la vedere cât câmpul are valoare; Delete / Backspace golesc tot câmpul. Clicul trimite `input` + `change`, ecranul trimite
  `value || null`, serverul scrie NULL. Un mecanism, în api.js (`dataGolibila`, aplicat de observator oricărui câmp desenat); ecranele nu-l
  repetă. Un câmp de dată obligatoriu se MARCHEAZĂ (`.oblig`, v2.0) — altfel primește „×”. Gărzi: verificator DATA_GOLIBILA +
  `core/test_lot11_u0_data.py` (în browser) + e2e `test_def_441_*`.
- **Refuzul unei acțiuni de pe rând stă sub textul rândului (v2.92, lotul 6, deficiența 279, clasa 259):** `api.refuzPeRand(buton,
  mesaj)` (`.msg-refuz-rand`), nu un `<span class="msg-eroare">` lipit de buton, care strângea textul rândului. Gard:
  `core/test_stare_nota_salvata.py::test_refuzul_de_pe_rand_nu_mai_se_lipeste_de_buton`.
- **Previzualizarea unui import cu rânduri care nu intră (v2.91, 14.10.2026, decizia Costin pentru C24 / C25):** rândurile pe care salvarea le refuză se arată ÎNAINTE de salvare, într-o `.caseta-atentie` deasupra butonului, fiecare cu „rândul N” (rândul din FIȘIER) și motivul; unde importul admite salvarea parțială (mijloace fixe, istoric declarații, salariați, parteneri — decizia Costin 14.10.2026), butonul spune ce salvează („Salvează cele 2 rânduri bune (declarații)”), iar mesajul de după salvare („avert”) spune câte au intrat și care nu, rând cu rând. Unde importul e un întreg (balanța, cotele asociaților), salvarea rămâne blocată. **Un câmp importat fără valoare** (persoanele în întreținere, scutirea de contribuția minimă) intră cu valoarea neutră și e MARCAT: avertismentul stă pe rândul salariatului din Stat de plată, iar confirmarea e un buton la capătul rândului („De verificat (N)”), cu câmpurile cerute (Da/Nu fără preselecție). Ce s-a citit din fișier și n-a intrat (totaluri, sinteticele înlocuite de analitice) se spune în `.mig-avert`, nu dispare.
- **Plasarea erorii per-câmp (v2.30, G10)**: eroarea unei acțiuni eșuate se afișează **lângă câmpul care a cauzat-o** (mecanismul A), nu doar într-o zonă generică sus (mecanismul B). G10 e o schimbare de PLASARE, predominant frontend; conținutul mesajelor e deja explicit (G1-G5). Reguli:
  1. **Maparea câmp→eroare.** Validările CLIENT-side cunosc câmpul pe care-l verifică → scriu direct un `<span class="msg-eroare">` imediat după inputul respectiv, printr-un helper unic `eroareCamp(idCamp, txt)`. NU se deduce câmpul din textul mesajului (ar lega plasarea de un șir afișabil — interzis structural, vezi `test_garzi_mesaje_afisabile`).
  2. **Contract backend pentru cheia de câmp.** O eroare de backend care privește un câmp anume trimite cheia de câmp ADITIV, fără a schimba `detail`: răspuns `{"detail": "<mesaj>", "camp": "<id-DOM>"}`. `detail` rămâne STRING (compatibil cu `str(e)` și cu aserțiile pe substring `in`); `camp` = id-ul DOM al câmpului. api.js citește `camp`; dacă e prezent → `eroareCamp`. Cele 77 de passthrough `str(e)` NU se restructurează.
  3. **Când A vs când B.** A = când ȘTIM câmpul (validare client SAU backend cu `camp`) ȘI `#camp` există în DOM. B (zona generică) = pentru erorile FĂRĂ câmp (business, conflict 409, permisiuni 403, izolare 404) ȘI ca **fallback OBLIGATORIU** când `camp` nu se găsește în DOM — o eroare cu câmp inexistent NU dispare, cade în B. B NU dispare; e casa erorilor non-câmp.
  4. **Erori multiple.** Pe formularele cu multe câmpuri obligatorii, validarea COLECTEAZĂ toate erorile (tiparul `erori_generare`: listă, nu `return` la prima) și plasează fiecare lângă câmpul ei — utilizatorul le vede pe TOATE odată, nu una pe rând. Fail-fast e INTERZIS pe formularele multi-câmp.
  5. **Domeniu.** Mecanismul A se aplică DOAR formularelor multi-câmp (userul completează multe câmpuri și trebuie să știe CARE e greșit). Formularele de 1-2 câmpuri rămân pe B — acolo eroarea e evident despre singurul câmp, iar A ar fi zgomot. Regula, helper-ul și contractul = o singură sursă (nu 15 implementări neuniforme).
  6. **Coexistență (mai multe erori, o singură acțiune).** A și B COEXISTĂ, nu se exclud. Doar erori de câmp → doar A (fără un B redundant de tip „completează câmpurile”). O eroare FĂRĂ câmp (business/conflict/permisiune) → B, PLUS orice erori de câmp ca A, simultan. B NU se ascunde când apar erori de câmp: un blocaj global (perioadă închisă, conflict) trebuie să rămână vizibil — altfel userul repară câmpurile și re-lovește același zid invizibil (fundătura pe care întreaga campanie a eliminat-o). B nu e niciodată o re-formulare a erorilor de câmp.
- **Cota TVA la emitere (v2.11)**: cota NU se tastează pe linie — vine din nomenclatorul de produse (F023: potrivire pe denumire, regulă+AI), la plătitorii de TVA; ne-plătitorii emit fără TVA. Regimul se setează o dată, în ecranul-poartă „Configurare emitere" (numerotare + regim TVA), obligatoriu înainte de prima factură.
- **Câmp obligatoriu (v2.0)**: marcat cu asterisc roșu prin `<span class="oblig">*</span>` lângă etichetă. Câmpurile opționale nu se marchează.
- **Ghidaj preventiv (v2.0)**: câmp care nu se poate autocompleta din date existente primește `<span class="camp-ajutor">` (albastru #3d8fd6, sub etichetă) care spune de unde ia utilizatorul valoarea. Niciun câmp obligatoriu gol fără context.
- **Stare goală (v2.13)**: o listă cu ZERO rânduri NU e mesaj de stare — nu se afișează prin `arataMesaj()`. Nu s-a întâmplat nicio acțiune; e conținut de ecran, nu feedback tranzitoriu. Clasă canonică unică: **`.stare-goala`** (modificator `.stare-goala--inline` pentru o linie într-un panou, nu listă goală pe ecran plin — altă anatomie: aliniere stânga, padding mic). Clasele `.cap-gol` și `.sa-gol` sunt ELIMINATE; `.mig-gol` NU se mai folosește pentru stări goale (utilizările lui rămase sunt mesaje de eroare din `catch`, datorie de migrat la `arataMesaj` — vezi DE_FACUT). Trei părți OBLIGATORII: (1) **golul** — ce lipsește; (2) **cauza** — de ce e gol; dacă e precondiție neîndeplinită, cu temei; (3) **ieșirea** — butonul care repară, SAU regula sistemului pe care omul n-o știa (când golul e normal: n-a început încă). INTERZISĂ fundătura: „Niciun X." fără cauză și fără ieșire. Modele: `produse_ecran.js` („Niciun produs încă. Adaugă primul produs — cota se completează automat."), `firme.js` document de verificat („Clienții pozează, aici certifici."). Regula STARE_GOALA în verificator (clasă interzisă + fundătură).

- **După generarea unei note (v2.98, 21.10.2026, decizia Costin 10.3: „8c: reparația centrală, cu DS cap. 6 actualizat.” — clasa, toată
  aplicația; instanța, raportul Z, comanda 10.2 pct.8c: „După generare, titlul «Notă generată» e roșu, conturile notei nu se văd, iar
  «Generează notă» rămâne activ.”):** orice ecran care GENEREAZĂ o notă dintr-un calcul (raportul Z și importul AMEF, amortizarea lunii și
  cea restantă, inventarul, descărcarea gestiunii, reevaluarea, compensarea, operațiunile — borderou, TVA la încasare —, salariile, casarea)
  se încheie pe un singur drum, `api.dupaGenerare(zona, buton, opt)`:
  1. confirmarea are **stilul de succes** — `.caseta-ok` (verde-pal, titlul `--verde-inchis`, role=status), niciodată culoarea refuzului
     de dinainte: zona își pierde clasele `msg-*`;
  2. arată **conturile și sumele** notei generate, rând cu rând („5311 = 707 · 200,00 lei”), cu eticheta notei și starea ei; când
     răspunsul generării dă numai id-urile notelor, ele se citesc din Registrul jurnal (`api.noteGenerate`);
  3. butonul de generare devine **inactiv, cu motivul lângă el** — implicit „Nota e generată — o vezi în Registru jurnal.”
     (`MOTIV_NOTA_GENERATA`); un motiv pe care ecranul îl dăduse deja butonului (`aria-describedby`) primește textul, nu încă unul alături.
     Butonul redevine activ numai când se schimbă datele din care s-ar genera altă notă: câmpurile formularului (`reactiveazaLa`) sau o
     scriere în alt ecran (`reactiveazaLaScriere`, după căile semnalului `iconta:schimbare` — amortizarea, după registrul mijloacelor fixe).
  4. un ecran care se redesenează după generare pune confirmarea în zona de mesaj a ecranului REFĂCUT (cap.27, C64), nu înainte.
  **Starea la deschidere:** generarea deja făcută și neînlocuibilă se vede pe buton la deschidere — „Generează amortizarea” e inactiv pe
  luna cu nota validată, cu nota numită („Amortizarea lunii e generată: nota nr. crt. N din …, validată”); cu nota în ciornă butonul e
  „Regenerează amortizarea”, iar serverul refuză, numit, a doua generare cu aceleași sume (`uc_tenants.tenant_amortizare`).
  Textul „Notă generată” stă numai în helper. Gard: verificator DUPA_GENERARE (butonul de generare poartă `data-genereaza-nota` și trece
  prin helper; helperul face cele trei lucruri; textul nu se scrie de mână) + `core/test_lot11_j_dupa_generare.py` (în browser) +
  `core/test_lot11_j_verificator.py`. Stornarea facturii rămâne pe confirmarea cap.27 (418c): e un act asupra documentului, nu o generare.
- **Contoarele și clopoțelul urmează acțiunile, fără reîncărcare (v2.98, 21.10.2026, decizia Costin 10.3, deficiența 422 — clasa 286):**
  după orice scriere reușită prin `api.*` (validare, respingere, ciornă generată, ștergere, trimitere la validare) semnalul unic
  `iconta:schimbare` (cu `detail.cai`, căile scrise) face pagina principală să-și recitească contoarele („De validat”, „De depus”, notele în
  ciornă) și coaja să-și recitească insigna clopoțelului și lista lui deschisă; ce schimbă un coleg se află din contorul notificărilor,
  recitit la `CLOPOT_INTERVAL_MS` (60 s) și la întoarcerea în filă, care trimite semnalul mai departe când s-a mișcat. Un ecran nu cheamă
  contoarele de mână. INTERZISĂ scrierea cu `fetch` direct din ecrane (ocolește semnalul și refuzul comun); excepțiile, cu motiv:
  previzualizările `…/incarca` și telemetria publică. Gard: `core/test_lot11_j_contoare.py` (în browser + garda statică).

- **Nota internă a unei firme în partidă simplă (v2.95, 19.10.2026, decizia Costin, deficiența 368):** la PFA / II / IF nota scrisă în
fundal se validează automat; starea ei se spune central, prin `stareNota` / `pasNota` (api.js): „notă internă — Poartă TVA-ul pentru D300 /
D394; evidența PFA e registrul de încasări și plăți.” (`TEXT_NOTA_INTERNA`, o singură definiție); refuzul validării automate se spune cu
motivul regulii, iar nota rămâne ciornă. Registrul jurnal deschis la PFA o spune sub titlu (`#j-interne`).

## 7. Documente PDF

- Tabelele PDF respectă aceleași reguli de aliniere ca HTML (cap. 4): stânga peste tot, sume la dreapta cu separator aliniat.
- Preferință: tabele reportlab Table cu colWidths explicite (ca factura_pdf.py), nu drawString cu coordonate manuale.
- **Antetul unui raport contabil PDF** (`documente_api.antet_raport`; v2.84, 08.10.2026, comanda Costin „Retest 08.10” pct.18) poartă
  firma, CUI-ul ei și momentul generării: „<firma> · CUI <cui> — Generată la zz.ll.aaaa hh:mm” (ora României, `data_ro(…, "cu_ora")`).
  O hârtie fără CUI nu se poate lega de firmă, iar una fără dată nu spune pe ce stare a evidenței s-a tras. Gard:
  `core/test_retest_0810_s6.py::test_pct18_pdf_balanta_are_cui_si_data`.

## 8. Semafoare

- Mereu vertical, ordinea ROȘU → GALBEN → VERDE (urgența întâi). Excepție: cardul Control fiscal de pe pagina principală — un rând (mai jos, v2.88).
- **Culorile de semafor nu colorează text (v2.70, 05.10.2026).** Gard `CULOARE_SEMAFOR_TEXT`. `--galben` (#c9961f), `--gri-semafor` (#9aa3b2) și `--rosu-semafor` sunt pentru buline, borduri, bare și fundaluri: pe alb, ca text, dau ~2,6:1 / ~2,5:1 / ~3,6:1, sub pragul WCAG 1.4.3 (4,5:1). Un text (insignă, stare, cifră, mesaj) folosește tokenii de text: `--galben-text`, `--gri`, `--rosu`, `--verde`. Regula prinde forma directă (`color:var(--galben)`, `color:${CUL.galben}`) și două forme indirecte (dicționar/variabilă și funcție care întorc o culoare de semafor, folosite în `color:${…}`); culoarea transmisă prin parametru nu se vede.
- Bulină LED 16px cu gradient + etichetă text 10px.
- Culori canonice: verde #1d7a4d · galben #c9961f · roșu #ff3b30.
- Se folosesc EXCLUSIV prin tokeni: `var(--verde)` / `var(--galben)` / `var(--rosu-semafor)`. Hex literal interzis în JS/CSS (excepții: definiția tokenului, nuanțele deschise din gradientul `dot:`). Prins de regula HEX_SEMAFOR în verificator (v2.11). Starea gri (necunoscut/necompletat): `var(--gri-semafor)` #9aa3b2 + fundal `var(--gri-fundal-semafor)` #eef0f3 — un singur gri de semafor, nu nuanțe ad-hoc.

- **Roșul semaforului fiscal = termen depășit (v2.87, 10.10.2026, decizia Costin: „Roșu înseamnă termen depășit.”, deficiența 220).**
  În Control fiscal (listă, detaliu, fișa firmei, cardul de pe pagina principală) roșul e numai al RESTANȚELOR: declarație datorată,
  nedepusă, cu termenul trecut. O neconcordanță contabilă, o declarație nedepusă înainte de termen, o verificare contabilă care nu
  trece sau un audit divergent se arată **galben** (de urmărit); ce nu se poate ști, **gri**. Serverul păstrează severitatea
  verificatorului (porțile cozii, alertele) — regula privește culoarea afișată și starea firmei (`common.pastila_firma`: o constatare
  urcă firma cel mult la galben). Gard `ROSU_DOAR_RESTANTA` (verificator) + `core/test_rosu_termen_depasit.py`.
- **Semaforul Control fiscal = PATRU lumini (v2.87, 10.10.2026, aprobat de Costin, deficiența 224).** ROȘU → GALBEN → VERDE → GRI,
  fiecare lumină cu numărul de firme în starea ei (partiția `sumar` a serverului: fiecare firmă într-o singură stare); toate patru mereu
  afișate, și cu 0. Bulina e `.cab-pct .pct-<stare>` (STANDARD_SEMAFOR), containerul `.cab-semafor4`. Gard `SEMAFOR_PATRU_LUMINI`.
  **Forma, v2.88 (12.10.2026, comanda Costin, 224 redeschisă: „Cardul arată doar un rând cu 4 buline colorate și numărul fiecăreia, fără
  text, iar înălțimea lui e la fel cu a celorlalte carduri. Textul rămâne numai în fereastră.”):** CARDUL (contabil-șef și asistent) =
  un rând, bulina și numărul, fără numele stării (`semafor.js::semaforCardControl`, `.cab-semafor4--card`; numele ajung la cititorul de
  ecran prin `aria-label`); FEREASTRA = vertical, cu numele stării (`semaforPatruLumini`). Aceeași sursă (`sumar`), aceeași ordine.
- **Eticheta stării unei firme în Control fiscal = una din cele patru stări (v2.88, 12.10.2026, comanda Costin, deficiența 226: „eticheta
  din dreapta fiecărei firme e una din cele 4 stări (restanță, de urmărit, la zi, nu se poate verifica) … Detaliul rămâne pe rândul de
  dedesubt.”).** Rândul listei și antetul detaliului folosesc `control_verdict.js::etichetaStare(stare)` = `CULORI[stare].txt`; cauza
  („neconcordanță”) și numărul („2 nu se pot verifica”) stau în detaliu. Gard `ETICHETA_PATRU_STARI` (verificator).
- Buline de stare pe fire de conversatie (Raporteaza): ROSU = in asteptare de raspuns, VERDE (#1d7a4d) = raspuns primit. Fara concept de citit/necitit; cifra de pe card = firele in asteptare (stare noua) si scade singura la sosirea raspunsurilor.

## 9. Ferestre de lucru

- Overlay umbrit uniform rgba(20,30,45,0.55) pentru TOATE ferestrele. Card central alb.
- max-height calc(100vh - 48px); la tabele lungi: antet + butoane fixe, doar tabelul derulează (aplicat mecanic din v2.96: „Fereastra cu
  tabel”, mai jos).
- Grile de câmpuri în ferestre: clasa `.grila-doc` (copiii primesc `min-width:0` ca să se strângă) — fără grile inline cu display:grid care lasă inputurile să împingă fereastra în scroll orizontal.
- `.fer-larg` max-width 1000px doar pentru tabele.
- **Fereastra cu tabele late (v2.81, 08.10.2026, decizia Costin W5)**: `.fer-tabel` (`nav.deschide(…, { lat: "tabel" })`) — lățimea o
  dă conținutul (`fit-content`), între 1000px și marginea ecranului (`100vw - 48px`); la 1920px tabelele Balanței, Mijloacelor fixe și
  Declarațiilor nu mai derulează lateral. Derularea laterală rămâne numai când tabelul e mai lat decât ecranul. **Înlocuit în v2.96**
  („Fereastra cu tabel”, mai jos): lățimea și înălțimea sunt ale ecranului, nu ale conținutului, și nicio derulare laterală.
- **Nicio fereastră cu derulare laterală (v2.92, lotul 6, deficiența 285 — clasă, toate ferestrele):** fereastra al cărei conținut e mai
  lat decât ea se lățește SINGURĂ (`navigator._lateste`: `fer-tabel` adăugat când `.fereastra-corp` are `scrollWidth > clientWidth`, la
  fiecare schimbare de conținut și la redimensionare) — nu mai depinde de ecranul care ar fi trebuit s-o ceară. Unde nici lățirea nu
  ajunge (ecran îngust), rândurile de butoane și stări se rup (`flex-wrap`, ex. `.fd-antet-sus`), iar celulele `.fd-tabel` își rup
  cuvintele lungi. Gard: e2e `test_def_285_*` (toate cardurile ferestrei firmei, detaliul facturii la 1100px, un conținut lat sintetic).
  **(19.10.2026, deficiența 349)** lățirea privește și cutia de previzualizare a importurilor (`.mig-prev-cutie`, cu derulare proprie pe
  înălțime): un tabel mai lat decât ea lățește fereastra, nu o face să deruleze lateral. Gard: e2e `test_def_349_*`. **(v2.96)** cutia nu
  mai derulează ea însăși: derulează corpul ferestrei.
  **(18.10.2026, deficiența 331)** numai cuvântul care nu încape se rupe: `overflow-wrap: break-word`, NU `anywhere` — `anywhere` coboară
  lățimea minimă a celulei la o literă și tabelul rupe și cuvintele scurte („Can t”, „servici u”). Gard: e2e `test_def_331_*`.
- **Fereastra cu tabel: aproape tot ecranul, rezumat sus, acțiune jos (v2.96, lotul 10, 421 și 424)**: `fer-tabel`, `rezumat-fix`, `bara-fixa`; gard `FEREASTRA_TABEL` / `ACTIUNE_TABEL_NEFIXATA` / `DERULARE_INLINE`.
- **Fereastra deschisă dintr-un refuz întoarce la formular, cu datele intacte (v2.99, lotul 11, deficiența 445; comanda Costin 11.1
  pct.21, verbatim: „orice buton «Deschide X» dintr-un refuz întoarce în formularul de plecare, cu datele intacte.”):** butonul
  „Deschide X” al unui refuz (`ecran_destinatie.butonSpreEcran`, și cel pus automat de api.js) anunță navigatorul (`nav.dinRefuz()`):
  (1) formularul de dedesubt se păstrează ORICUM — elementul lui, cu valorile, rândurile și refuzul afișat —, nu numai când omul a tastat;
  (2) săgeata destinației spune „← Înapoi la <formular>” (`.nav-inapoi-la`); (3) X din destinație o închide numai pe ea și întoarce la
  formular (pe orice altă fereastră X duce la pagina principală, ca înainte); (4) `inapoiLa` implicit = titlul ferestrei de plecare
  (`nav.titluCurent()`), pentru destinațiile care spun după salvare „Înapoi la …”. Un buton „Deschide …” scris de mână într-un refuz cheamă
  `nav.dinRefuz()` înainte de `nav.deschide`. Gărzi: verificator INTOARCERE_DIN_REFUZ + `core/test_lot11_u0_intoarcere.py` (în browser) +
  e2e `test_def_445_*`.
  Comanda Costin 10.1 pct.5 (clasă, toată aplicația; verbatim în DECIZII): „Regula: ferestrele cu tabele se deschid aproape pe tot ecranul
  (cum e deja Balanța de verificare); rezumatul stă fix sus și acțiunea principală fix jos; se derulează doar tabelul din mijloc,
  niciodată lateral.” Concret:
  1. Orice fereastră de lucru care CONȚINE un tabel (`<table>` sau lista-tabel `.mig-sold-tabel`) devine fereastră cu tabel — clasa
     `fer-tabel` o pune navigatorul singur (`navigator._lateste`, la fiecare schimbare de conținut), nu ecranul; `{ lat: "tabel" }` o
     pune doar mai devreme. Clasa nu se scoate cât fereastra e deschisă (fereastra nu sare la fiecare „Se încarcă…”).
  2. Fereastra cu tabel are lățimea `calc(100vw - 48px)` și înălțimea `calc(100vh - 48px)` — fixe, nu maxime. Pe telefon (≤ 560 px)
     rămâne tot ecranul.
  3. Un singur element derulează: corpul ferestrei (`overflow-x: hidden; overflow-y: auto`), niciodată lateral. Nicio cutie cu
     derulare proprie în fereastră: `.mig-prev-cutie` nu mai derulează, iar stilul inline `overflow(-x): auto|scroll` e interzis în
     șabloanele din `static/js` (gard `DERULARE_INLINE`). **(v2.97)** Nici lista-tabel `.mig-sold-tabel` (Activitate cabinet) nu mai
     derulează ea însăși în fereastra cu tabel (`max-height: none; overflow: clip`; cutia ei de 280 px lăsa corpul fără ce derula, deci
     rezumatul fix n-avea ce ține în vedere); antetul ei (`.ac-cap`) se lipește sub rezumat, ca antetul `.fd-tabel` (gard
     `FEREASTRA_TABEL`).
  4. Tabelul se încadrează în lățime: celula își rupe cuvântul care nu încape (`break-word`, 331); dacă nici așa nu încape, navigatorul
     îl strânge în trepte, cât e nevoie — `fer-strans` (litera `--text-desc`, celula mai îngustă), apoi `fer-rupt` (`--text-micut`,
     textul rupt oriunde). Cifrele (`.fd-td-num`) rămân pe un rând în toate treptele (162).
  5. **Rezumatul lipit sus** (`.rezumat-fix`: ce trebuie văzut cât derulezi tabelul — luna, cifrele ecranului, antetul documentului cu
     acțiunile lui, zona de mesaj a acțiunilor de pe rânduri); gol, nu ocupă loc. **Acțiunea principală și mesajele ei de blocare lipite
     jos** (`.bara-fixa`, cap.6 v2.92). Amândouă se lipesc numai cât e în vedere părintele lor, deci stau direct în corp sau în același
     părinte cu tabelul. Antetul tabelului `.fd-tabel` rămâne în vedere sub rezumat (`--rezumat-h`, pus de navigator).
     **Rezumatul e obligatoriu pe orice ecran care desenează un tabel de date în fereastră (v2.97, gard `REZUMAT_TABEL_LIPSA`).** Intră
     în `.rezumat-fix` blocul care stă DEJA deasupra tabelului și trebuie văzut cât derulezi: perioada / luna / anul, filtrele (contul,
     varianta, registrul), cifrele ecranului, antetul documentului cu acțiunile lui, zona de mesaj a acțiunilor; titlul și textele de
     prezentare nu se cer în el (pot rămâne deasupra lui, nelipite). ~~Rezumatul nu mută nimic: ce stă sub tabel (totalurile Fișei de
     cont, luna Stocurilor) rămâne acolo până decide Costin~~ — **înlocuit în v2.100** (decizia Costin 10.3, pct.7–8 de mai jos): ce
     trebuie văzut cât derulezi se MUTĂ în rezumat (luna Stocurilor, cu butonul și mesajul ei) sau jos (totalurile). Nu se cer: tabelele
     de machetă (`mfp-tabel`) și formularele cu tabele mici în ele (Date firmă, Operațiuni — se derulează formularul, nu un tabel;
     acțiunea stă deja în `.bara-fixa`). Fiecare excepție stă în verificator (`rezumat_exceptii`), cu motivul; cele trei „de decis de
     Costin” (Tipare, Înregistrare — cererile neconfirmate, Stocuri — situația stocului) au fost decise în v2.100 și au acum rezumat. O
     excepție fără obiect (ecranul are acum rezumat, sau nu mai desenează tabel) pică gardul.
     **(v2.98, lotul 11, 424/446)** În rezumatul lipit al unei previzualizări de import stă numai ce se vede cât derulezi (intro pe un
     rând, cifrele, banda stărilor, avertismentul); notele informative («ce s-a citit», confruntarea care se potrivește, rândurile
     ignorate) sunt pliate (`details.dec-xml`), cu concluzia în titlu. Câmpurile salvării stau pe un rând în `.bara-fixa` (`.grila-doc`).
     Avertismentul înlocuirii apare o dată, `arataMesaj(…, "avert")`; confirmarea e o întrebare scurtă (`confirmaCaseta`), iar butonul
     principal e ascuns cât e deschisă. Gard: `core/test_lot11_m_ferestre_import.py` (1280×720, toate importurile).
  6. Un buton care scrie (`data-actiune` POST / PUT / PATCH / DELETE), pus în corpul unei ferestre cu tabel, stă în `.bara-fixa` sau în
     `.rezumat-fix` — nu la capătul conținutului (gard `ACTIUNE_TABEL_NEFIXATA`). Nu se cer: acțiunile de pe un rând (în celulă, sau cu
     identificatorul rândului) și tabelele de machetă (`mfp-tabel`, modelul facturii). **(v2.97)** Regula privește și ZONELE ferestrei:
     un buton care scrie, pus după un tabel într-o zonă desenată separat (lista ajustărilor fiscale, coloana „An precedent” a
     bilanțului, propunerea contării salariilor) sau într-un formular adăugat după tabel (înscrierea în registrul fiscal PF), stă și el
     în `.bara-fixa`, cu mesajul lui când e lângă el. Butonul de deasupra tabelului ține de rezumat (pct.5). Excepții cu motiv, în
     verificator (`actiuni_exceptii`): „Adaugă” din panoul elementelor de salariu (e în rândul câmpurilor formularului; lipirea lui jos
     ar muta rândul întreg).
  7. **Totalurile tabelului rămân în vedere (v2.100, lotul 11; decizia Costin 10.3, verbatim în DECIZII „Comanda 10.3” pct.4: „Totalurile
     și rezumatul fix, mesajele lângă buton, 394 la 1280×720: da, reorganizezi ecranele; totul încape într-un ecran, fără derulare.”).**
     (a) Rândul de total aliniat sub coloane e `<tfoot>`, nu ultimul rând din `<tbody>`: în fereastra cu tabel se lipește jos, deasupra
     barei de acțiune (`bottom: calc(var(--bara-h) - 24px)`; `--bara-h` = înălțimea ultimei `.bara-fixa` din corp, pusă de navigator ca
     `--rezumat-h`). Balanța, Registrul-inventar, Rapoartele comerciale (vânzările, fișa partenerului), registrul fiscal PF (rândul
     anual al fiecărei surse), situația stocului, împărțirea dividendului. (b) Caseta de totaluri a unui registru fără coloane de aliniat
     (`.fd-totaluri`) stă în `.bara-fixa`, pe un rând care se rupe pe telefon: Cartea mare, Jurnal regim marjă, Registru jurnal, detaliul
     facturii. Gard: verificator `TOTAL_NEFIXAT` (rândul „Total” în `<tbody>`, caseta după tabel în afara barei, regula `tfoot` din
     stil.css, `--bara-h` din navigator) + `core/test_lot11_w4_ecrane.py` (Chromium, 1280×720 și 1366×768, 40 de rânduri: totalul se
     vede și neacoperit la începutul și la mijlocul tabelului).
  8. **Mesajul stă lângă butonul care îl produce (v2.100, aceeași decizie).** Zona de mesaj a butoanelor de sus stă în `.rezumat-fix`,
     a acțiunii de jos în `.bara-fixa`; nicio zonă de mesaj a ecranului nu rămâne sub tabel (Stocuri `#s-mesaj`, Înregistrare
     `#ins-cereri-msg`, Registrul fiscal `#aj-mesaj` — mutate). Rezultatul unui buton din rezumat cu text lung (Tipare, „Generează
     analiză AI”) stă chiar sub rezumat, deasupra tabelelor. Refuzul de pe un rând rămâne pe rând (`refuzPeRand`, cap.6). Gard: verificator
     `MESAJ_SUB_TABEL` (excepții cu motiv în `mesaje_exceptii`: zona panoului elementelor de salariu, lângă „Adaugă”) +
     `core/test_lot11_w4_ecrane.py` (mesajul în vedere, la ≤ 80 px de buton).
  Gard: `core/test_lot10_fereastra_tabel.py` (regula verificatorului pe fragmente bune / rele + navigatorul și stil.css reale, în
  Chromium) + e2e `test_def_421_*` / `test_def_424_*` (Balanța, Registrul-inventar, statul de plată și importul salariaților la 1366×768);
  rezumatul pe toate ecranele cu tabel: `core/test_lot10_rezumat_fix.py` (v2.97).
- Nicio fereastră nu iese din ecran.
- **Rezumatul nu mănâncă tabelul (v2.102, lotul 12, 621; comanda Costin 12.2 pct.11, verbatim: „Balanța: casetele de sus ocupă jumătate
  din fereastră, se văd 2–3 rânduri de tabel; caseta «Importă…» nu are buton spre import.”; cerința: „Casetele nu mănâncă tabelul — regulă
  globală”).** (1) În rezumatul lipit sus (`.rezumat-fix`) stă numai ce trebuie văzut cât derulezi: titlul, perioada, cifrele, butoanele, zona
  lor de mesaj, o concluzie pe un rând. O casetă (`.caseta-info`, `.caseta-atentie`, `.caseta-poarta`) NU stă în rezumat: stă sub el (se
  citește la deschidere, iar tabelul primește fereastra cât derulezi) sau, ca notă informativă, pliată (`details.dec-xml`, concluzia în
  titlu — verdictul bun al Balanței „se închide pe toate cinci”). (2) Rezumatul e strâns: blocurile lui fără marginile de pagină (4 px între
  ele). (3) La 1280×720 rezumatul are cel mult un sfert din corpul ferestrei (Balanța cu ciorne + rulaje lipsă + închidere nereușită,
  Registrul jurnal cu căutare și motivul amortizării, Stocuri, Fișa de cont). (4) O casetă care cere un import / o corectură în alt ecran
  are butonul spre el sub text (Balanța: „Deschide Import date › Solduri inițiale”). Gărzi: verificator `REZUMAT_CASETA` (șabloanele
  literale, inclusiv `${caseta…}` în rezumat) + `core/test_lot12_ui2_ecrane.py::test_def_621_*` (înălțimea, în Chromium) +
  `core/test_lot12_ui2_verificator.py`.
- **Antetul documentului pe ecranul scund (v2.103, lotul 12, C164; comanda Costin 12.3 pct.4, verbatim: „C164: pe ecranele scunde,
  antetul detaliului facturii se strânge pe un rând (număr, client, total, stare SPV); acțiunea principală rămâne fixă jos (clasa 285).”).**
  Antetul lipit sus al unui document cu acțiuni (detaliul facturii: numărul, stările, butoanele, zonele lor de rezultat, data, partenerul)
  poate fi mai înalt decât fereastra unui ecran scund — iar un rezultat scris în el nu mai intră în vedere (antetul lipit nu derulează).
  (1) **Ecranul scund** = mai scund de 700 px sau îngust ca un telefon (≤ 560 px). Pragul stă într-un singur loc, `stil.css`
  (`@media (max-height: 700px), (max-width: 560px) { :root { --antet-scund: 1; } }`); ecranul îl citește din `--antet-scund`, nu își scrie
  propriul `matchMedia`. (2) Pe ecranul scund rezumatul lipit sus e **rândul scurt** `.fd-antet-scurt`: numărul, clientul, totalul, starea
  SPV, pe UN rând (fără rupere; clientul și starea se taie cu „…”, întregi în `title`). (3) **Acțiunile coboară în bara lipită jos**
  (`.bara-fixa` › `.fd-bara-actiuni`: rândul butoanelor `.fd-bara-butoane` și zonele lor de rezultat, fiecare cel mult 30vh), deasupra
  totalurilor — acțiunea principală și mesajul ei se văd mereu (cap.6, 285). (4) Restul antetului (stările, data, partenerul, mențiunile)
  rămâne deasupra tabelului și derulează. (5) Se mută aceleași noduri (cu ascultătorii și ce s-a scris în ele) și se pun înapoi exact în
  locul lor când fereastra crește (`facturi_ecran.aseazaAntetul`, la desenare și la redimensionare); pe ecranul înalt antetul rămâne cel
  de până acum (pct.5 de mai sus). Gărzi: verificator `ANTET_SCUND` (pragul numai în `stil.css`, rândul scurt pe un rând, detaliul cu
  acțiuni are rândul scurt și bara lui) + `core/test_lot12_fe3_ecrane.py::test_def_c164_*` (1280×600 și 390×844, în Chromium) +
  `core/test_lot12_fe3_verificator.py` + e2e `frontend_test/e2e/e2e_lot12_fe3.py::test_def_c164_*`.
- **Tabelul de note (v2.102, lotul 12, 617 / 622; comanda Costin 12.2 pct.9: „Registru jurnal: fără căutare. Un câmp (cont, document,
  partener, sumă, nr. crt.) și filtru de stare; tabel cu un rând pe notă, detaliul la clic, explicațiile o singură dată.”; pct.12: „De
  validat: … Trei secțiuni cu număr, același tabel ca la 617, Validează/Respinge pe rând, căutare.”).** O singură componentă,
  `ecrane/tabel_note.js` (`htmlTabelNote` + `legaTabelNote`), pentru Registrul jurnal și pentru „De validat” (note de validat, notele tale în
  ciornă): `table.fd-tabel.tn-tabel`, fiecare notă un `tbody.tn-nota` (`data-nota-id` / `data-coada-ids`) cu rândul `.tn-rand` — Nr. crt.
  (sau data), data, [firma], explicația, documentul, conturile pe scurt, suma (`.fd-td-num`, stornarea sub ea), starea (cu semnele scurte:
  „fără document”, „depășită față de sursă” …), acțiunea principală a stării (cel mult două butoane: „Validează” + refacerea din sursă /
  trimiterea la validare; în coadă „Validează” / „Respinge”) — și detaliul `.tn-detaliu`, ascuns până la clic pe rând (sau pe butonul din
  prima celulă, `aria-expanded`): liniile notei (`table.tn-linii`, cu partenerul și centrul), documentul justificativ, mesajele notei și
  restul acțiunilor (Editează, Șterge). Explicația unui semn stă O DATĂ, deasupra tabelului (`.tn-explicatii`: `.caseta-atentie` pentru ce
  oprește validarea, `.caseta-info` pentru rest), cu numărul notelor; butonul inactiv e legat de ea (`aria-describedby`). Căutarea
  (`htmlCautare`, în rezumat) caută textul scris, întreg, în fiecare câmp al rândului și al liniilor (cont, document, partener, sumă scrisă
  „1.234,56” / „1234,56” / „1234.56”, nr. crt., firmă), lângă ea câte note se văd din câte; filtrul de stare (jurnalul): ciorne, validate, la
  validare, respinse, fără document. O întrebare de confirmare pentru un rând stă în detaliul lui (`locInDetaliu`), nu între celule. „De
  validat” are trei secțiuni cu număr — „Note de validat (n)”, „Declarații (n)”, „Notele tale în ciornă (n)” — iar o notă apare o dată
  (ciorna ta trimisă la validare stă numai în prima). Gărzi: verificator `TABEL_NOTE` + `core/test_lot12_ui2_ecrane.py::test_def_617_*` /
  `test_def_622_*`.
- **După o acțiune pe un rând, fereastra rămâne pe loc, cu confirmarea în vedere (v2.102, lotul 12, 617: „După «Validează» pagina sare sus
  fără confirmare.”).** Lista se redesenează pe loc (`peLoc`: fără „Se încarcă…”, deci conținutul nu scade și derularea rămâne), rândul arată
  starea nouă (evidențiat, `.val-evidentiat`), iar confirmarea („Ai validat nota nr. crt. 12 …”) stă în zona de mesaj din rezumatul lipit
  sus. Un ecran care trece totuși prin „Se încarcă…” după un clic într-un rând își regăsește derularea prin navigator (mecanismul de la
  observatorul ferestrei). Gard: `core/test_lot12_ui2_ecrane.py` (jurnal, coadă) + `core/test_lot12_ui2_derulare.py` (navigatorul).
- **Acțiunile unui rând de tabel stau într-un meniu (v2.83, 08.10.2026, comanda Costin „Retest 08.10” pct.13).** O celulă cu trei
  sau mai multe butoane le ține într-un `<details class="dec-xml"><summary>Acțiuni</summary>` (butoanele unul sub altul la deschidere),
  nu libere pe rând: butoanele libere lățesc coloana până când fereastra derulează lateral și acțiunile ies din vedere (Mijloace fixe
  F2, ~1700 px). Zero clase noi — e toggle-ul secundar al Declarațiilor (v2.54). Datele scurte (PIF) nu se rup pe două rânduri, iar
  o listă lungă de luni se strânge în intervale („8 luni: 01–08/2026”). Gard: `ACTIUNI_RAND_LIBERE` în verificator.
- **Pe un rând stau cifrele, nu antetele (v2.86, 09.10.2026, deficiența 162).** `.fd-td-num` ține cifra pe un rând; antetul coloanei
  numerice și nota de sub cifră (`.tip-desc`, ex. „neînregistrate: 8 luni: 02–09/2026”) se rup pe rânduri — un antet lung ținut pe un
  rând („Amortizat (calculat, până la 09/2026)”, 335 px) lățea Mijloacele fixe până la derulare laterală la 1700 px. Gard:
  `ANTET_NUMERIC_NOWRAP`.
- **Anunțul „Versiune nouă” stă deasupra ferestrelor (v2.86, 09.10.2026, deficiența 191).** `.versiune-noua` are `z-index: 101`,
  peste stratul ferestrei (`.fereastra-overlay`, 100): reîncărcarea rămâne la îndemână și cu o fereastră deschisă (cu un formular
  început butonul nu reîncarcă, spune de ce). Gard: `frontend_test/e2e/e2e_bloc_a.py::test_def_191_…` (elementul din punctul
  butonului e butonul).
- **Fereastra de scris are înălțimea ecranului (v2.86, 09.10.2026, deficiența 208).** Povestea lunii (`.pacm`) e un document: fereastra
  ține `calc(100vh - 64px)` și până la 1100 px lățime, caseta de text umple restul — și când povestea e goală (până atunci fereastra
  se strângea după conținut la 600 px, caseta la 368 px). Gard: `FEREASTRA_SCRIS`.
- **Focusul nu mută ecranul (v2.86, 09.10.2026, deficiența 159).** Un câmp care primește focusul după o apăsare (formularul deschis sub
  un rând, câmpul vinovat al unei validări) îl primește prin `api.focusFaraSalt`: fără derulare, apoi zona se mișcă numai cât să se vadă
  câmpul. `.focus()` simplu centrează câmpul (la „Marchează depusă” lista sărea 475 px). Gard: `FOCUS_CU_SALT`.
- **Închiderea (v2.64, `inchidereDialog` din `api.js`, comanda Costin 04.10.2026).** O fereastră INFORMATIVĂ — fără
  câmpuri de tastat (bun venit, anunț, lupa, ajutorul de dinainte de autentificare, paginile publice, previzualizări) — se închide din **X în antet** și cu
  **Esc**, prin mecanismul unic `inchidereDialog` din `api.js`: X-ul e `.nav-x` (pus de mecanism dacă lipsește), Esc
  închide numai fereastra de deasupra, iar X / Esc fac **exact** ce face butonul de la capăt (marchează văzut,
  confirmă) — nu o a doua cale. O fereastră cu ce se tastează (ferestrele de lucru din navigator, editoarele, fereastra
  de intrare/înregistrare) rămâne **doar cu X**: un Esc apăsat din reflex nu aruncă un formular completat. Excepția se
  declară pe linie: `/* fereastra-de-lucru: doar X — <motiv> */`. Gard: `DIALOG_FARA_INCHIDERE` în verificator.
- **Acțiunea refuzată rolului nu se afișează (v2.64, `data-actiune` + `drepturi.js`, decizia Costin 04.10.2026).** Un element
  care declanșează o scriere poartă `data-actiune="METODĂ /cale"` (șablonul rutei din `main.py`); `drepturi.js` îl ascunde (`.drept-refuzat`) dacă
  serverul o refuză utilizatorului (`GET /eu/drepturi`). Un câmp care afișează și o valoare poartă `data-actiune-camp`
  și se dezactivează în loc să dispară. Un buton care DESCHIDE formularul unei acțiuni („+ …”, „Adaugă…”, „Emite…”) poartă
  acțiunea formularului, sau `data-fara-actiune="<motiv>"` (rând în formular, navigare, portalul clientului). Gard:
  `core/test_drepturi_ui.py` + verificator `ACTIUNE_REFUZATA_NEMARCATA`.
- **Motivul acțiunilor ascunse se arată (v2.66, comanda Costin 05.10.2026).** Când poarta ascunde acțiuni într-o fereastră
  (`.fereastra-corp`, overlay-ul poveștii `.pacm`, sau o zonă `data-zona-drepturi`), pune o singură notă `.drept-motiv`:
  „Unele acțiuni de aici nu se afișează: cer dreptul «…», pe care nu-l ai. Îl acordă administratorul cabinetului, din ecranul
  Asistenți.” (nivelul vine de la server, `GET /eu/drepturi` → `motive`). Un ecran care își scrie singur mesajul pentru aceeași
  situație îi dă clasa `drept-motiv` și nota generică nu se mai pune. Gard: verificator `MOTIV_DREPT_ABSENT` + `core/test_drepturi_ui.py`.

- **Lista de pași care trebuie să încapă în fereastră (v2.95, 19.10.2026, decizia Costin, deficiența 394):** `.mig-op`, `test_394_migrare_cum_se_face.py` — instrucțiunile lungi ale unui
  ecran de pași (text de ajutor, nu date sau stare) stau pliate într-un `<details class="dec-xml"><summary>Cum se face</summary>`, închis la
  randare (toggle-ul secundar, v2.54 — zero clase noi); pașii rămân la vedere, în ordinea lor, iar de la lățimea desktop (`@media
  (min-width: 761px)`) rândul e compact: titlul și descrierea pe același rând, descrierea tăiată cu „…” și întreagă în `title`. Pe telefon
  (≤ 760 px) rândul rămâne cel întreg (≥ 44 px, ținta de atingere, cap.4). Primul ecran: Migrare cabinet. Gard:
  `core/test_394_migrare_cum_se_face.py` + e2e `test_def_394_*` (1366×768, 1700×1000, 393×851).
  **(v2.100, lotul 11 — decizia Costin 10.3: „394 la 1280×720 […] totul încape într-un ecran, fără derulare”)** Măsurat la 1280×720:
  Migrare cabinet derula 4 px fără aplicație aleasă, 92 px cu SAGA aleasă și 326 px cu „Cum se face” deschis; „Notă nouă” 8 px în
  partidă simplă. Acum: „Cum se face” stă pe rândul butoanelor aplicațiilor (`.mig-apl-rand`) și, deschis, se arată PESTE pași (panou
  alb, `position: absolute`), fără să-i împingă; rândul compact al pașilor are 28 px (≥ 24 px, ținta de atingere a desktopului); nota
  aplicației alese stă pe două rânduri. În „Notă nouă” data, descrierea și documentul stau pe un rând (`.grila-campuri`, se rup pe
  telefon). Gard: `core/test_lot11_w4_ecrane.py` (1280×720 și 1366×768: fără aplicație, SAGA, SAGA + confirmarea unui pas, „Cum se
  face” deschis; nota nouă în partidă simplă și dublă, luna în curs) + e2e `frontend_test/e2e/e2e_lot11_w4.py::test_def_394_*`.

## 10. Escape și securitate

- **`esc` din api.js (v2.0) = SINGURA funcție de escape.** Escapează `& < > " '` (5 caractere, inclusiv apostroful). Se **importă** din api.js, niciodată nu se **redefinește local**. INTERZISE: (a) variante locale cu alt nume (`_esc`/`escB`/`escV`/`escS`/`escC`/`escJ`) care omit apostroful; (b) **redefinirea locală a lui `esc`** (`function esc` / `const|let|var esc =`) într-un ecran — o copie locală poate fi mai slabă (ex. una care escapa doar `"` → XSS pe `<>` în conținut de element) și oricum e a doua sursă de adevăr pentru o primitivă de securitate; (c) **strip inline de caractere HTML** (`.replace(/[<>&]/g, "")` și variante) ca sanitizare ad-hoc — nu e XSS (scoate `<>`), dar e **data-lossy** (scoate `&` din nume: „A&B" → „AB") și tot o a doua sursă de sanitizare. Regula **ESC_LOCAL** în verificator prinde toate trei formele (apel de variantă + redefinire locală + strip inline `[…<>&…]`).
- Orice dată user/import-controlled afișată în innerHTML se trece prin `esc()`. **Gard (C37, Lotul 5, 15.10.2026):** `DATE_UTILIZATOR_NEESCAPATE` în verificator (instrumentul `scripts/scan_date_neescapate.py`, același în `core/test_date_neescapate.py`) — un nume, prenume, email, o denumire sau un mesaj scris de om, pus în HTML într-un șablon `${…}` sau lipit cu `+` lângă un tag, fără `esc()` înaintea lui. Un parametru care primește HTML gata făcut (deja escapat de apelant) o spune în nume: `confirmaCaseta(zona, mesajHtml, …)`. Limitele instrumentului (o valoare pusă întâi într-o variabilă cu alt nume, o valoare singură pe rândul ei într-un șablon început mai sus) sunt scrise în antetul lui.
- **Mesajul de eroare venit de la server (v2.65, 04.10.2026)** — `e.mesaj` / `err.message` / `r.detail` interpolat într-un șablon HTML trece prin `esc()`: mesajul poate cita ce a tastat utilizatorul (nume, email), deci e dată controlată de utilizator. Folosit doar ca test de ternar (`e.mesaj ? … : …`) nu se afișează. Gard: `MESAJ_SERVER_NEESCAPAT` în verificator.

## 11. Procedură de lucru

- Orice element UI nou: se alege din acest document. Dacă nu există → se discută, se adaugă AICI întâi, apoi se implementează.
- O regulă nouă intră în ACEST document ȘI (unde e cazul) în `verificator_conformitate.py` simultan.
- Audit de conformitate la fiecare ecran atins: se verifică cap. 1–10.
- Acest document se versionează în git (`.md`, editabil prin SSH — v2.0, migrat din docx).

## 12. Culori de card (meniu)

- **Cardurile-hub** (cele 9 carduri din panoul cabinetului `.cab-card` + meniurile-hub gen Firme/Activitate) folosesc EXCLUSIV paleta canonică de 7 culori-concept din `CULORI_CARD` (api.js). Fiecare card-hub: `bg` (fundal pastel) + `fg` (titlu/icon saturat).
- **Itemii-listă** (`.acces-card`/`.meniu-card` folosiți ca opțiuni înrudite într-un submeniu: Setări, portal documente, login) NU poartă culori-concept — au fundalul albastru-pal uniform al clasei `.acces-card`. Culorile-concept sunt pentru puncte de intrare majore, nu pentru liste de opțiuni.
- Paleta: **albastru** #e9f0fe/#1d4ed8 (firme, facturi, pachete) · **verde** #e6f6ec/#117f39 (termene, capacitate, cifre) · **teal** #dff4f2/#097a76 (control fiscal, declarații) · **violet** #efebfe/#6d28d9 (sinteză, raportări) · **piersică** #faece7/#993c1d (de validat, asistenți, activitate) · **chihlimbar** #fbeedd/#92500a (recomandă, anunțuri) · **ardezie** #eaeef6/#45597f (consolidare, documente, setări, suport).
- INTERZIS hex de card ad-hoc în afara paletei. Nuanțele apropiate NU se multiplică — un singur verde, un singur violet etc.
- Cardurile REFERĂ paleta, nu o copiază: `...CULORI_CARD.cheie` (import din api.js), NICIODATĂ `bg:"#..."` literal — chiar dacă valoarea coincide cu paleta. Excepție: semaforul (control.js, obiecte cu `dot:`). Prins de regula CULOARE_CARD_HEX în verificator.
- Culorile de semafor (cap.8) și cele de stare rămân separate; astea sunt doar pentru carduri de navigare.

### Spacing (decizie 12.07.2026)
- Margin/padding inline rămân valori literale (6/8/10/12/14/16px, tipar de facto consistent, ~2100 apariții). NU se canonizează în tokeni — raport risc/câștig nefavorabil. Decizie închisă, nu se redeschide fără motiv nou.

## 12b. Cardurile de început (deficiențele 319 + 320, comanda Costin 17.10.2026 7.2, verbatim în DECIZII „Comanda 7.2”)

- **Unde:** pe pagina principală, sub banda de salut (`#inceput-carduri`, `salut.js` — aceeași la administrator și asistent) și în portalul
  clientului, deasupra grilei. Nu sunt carduri-hub (`.cab-card`): sunt `.inceput-card`, panouri albe cu marginea stângă albastră.
- **Ce conțin:** titlul pasului, „Ce faci aici”, pașii numerotați, nota (când există), rândul „Cardul devine verde când …” și butoanele spre
  ecranele REALE (fereastră, ca orice card — cap.2a).
- **Pașii și nota stau pliați (lotul 12, deficiența 596):** la vedere rămân titlul, „Ce faci aici”, rândul „Cardul devine verde când …” și
  butoanele; pașii numerotați și nota stau în `<details class="dec-xml"><summary>Cum se face</summary>`, închis (nimic nu se deschide singur,
  CLAUDE.md §9) — cardul încape pe ecran, textul aprobat la 319 rămâne întreg.
- **Prima intrare („Înainte de a începe”, lotul 12, 561 / 596):** o fereastră (`.fereastra`, corpul derulează), cu „Continuă în aplicație” și
  rândul „ce mai lipsește” în `.bara-fixa`; „NU s-a salvat” stă lângă butonul apăsat (cap.6 v2.93), nu sub panou.
- **Starea:** verde (`.inceput-facut`, marginea și bifa `--verde`) numai când pasul e făcut în ecranul lui — citit de server
  (`GET /eu/inceput`), niciodată la apăsarea cardului.
- **Fără „închide”:** un `.inceput-card` nefăcut nu are buton de închidere și nu se ascunde; nu blochează lucrul (grila de dedesubt rămâne).
  Când toate sunt făcute (`toate_facute` din `GET /eu/inceput`), `#inceput-carduri` dispare; aceleași carduri, de citit, rămân în „?”
  (Prezentarea aplicației, „Primii pași”).
- **Prima intrare:** înainte de pagina principală, ecranul „Înainte de a începe” (telefonul, canalul, bifele din Notificări); „Continuă în
  aplicație” se deblochează după salvare. Gărzi: `core/test_319_320_inceput.py`, e2e `frontend_test/e2e/e2e_lot72_cont.py::test_def_319_*`,
  `::test_def_320_*`.

## 13. Iconițe

- Iconițele de card/UI folosesc EXCLUSIV dicționarul canonic unic `ICOANE` (api.js) — path-uri SVG interne, viewBox 24×24, stroke. NU se duplică dicționarul în ecrane (era copiat divergent în cabinet/admin/asistent).
- Fiecare concept = o iconiță sugestivă distinctă. Triada card = culoare + denumire + iconiță, toate coerente. INTERZIS iconiță generică (`report`) folosită ca fallback pe concepte diferite.
- Iconiță nouă → se adaugă în `ICOANE`, nu inline într-un ecran. Prins de regula ICOANE_LOCAL în verificator.
- **Cheia folosită există în `ICOANE` (v2.66, 05.10.2026).** `svg(cheie)` desenează `ICOANE[cheie] || ""` — o cheie greșită dă o iconiță GOALĂ, fără eroare (instanța: „Raportează” și „Raportări” cereau `report`, scos în v2.7). Prins de regula `ICOANA_INEXISTENTA` în verificator.

## 14. Tipografie

- Scară de dimensiuni canonică (tokeni CSS): `--text-titlu` 22px · `--text-sectiune` 19px · `--text` 17px · `--text-mic` 15px · `--text-desc` 13px · `--text-micut` 12px. NU se folosesc alte valori.
- Clase de tip (rol semantic, în stil.css): `.tip-titlu` · `.tip-sectiune` · `.tip-corp` · `.tip-desc` (13px gri, descrieri) · `.tip-figura` (19px bold, cifre de card) · `.tip-total` (17px bold, totaluri) · `.tip-micut` (12px, note).
- INTERZIS `font-size` cu valoare literală inline (`font-size:13px`). Se folosește clasa de tip sau, excepțional, `font-size:var(--text-*)`. Prins de regula FONT_INLINE în verificator.
- Culoarea, marginea, alte stiluri non-tipografice pot rămâne inline; doar dimensiunea fontului trece prin clasă/token.
- **Titlurile se scriu cu diacritice (v2.98, 21.10.2026, comanda Costin 11.1 pct.23: „titluri fără diacritice”):** titlul ferestrei
  (`nav.deschide("…")`), al cardului, al secțiunii, antetul de coloană, opțiunea din listă, eticheta câmpului și textul butonului —
  „Înregistrare”, „Ieșiri”, „Declarații”, „Factură” (titlul „Factura” singur e forma articulată, nu titlul). Tot așa, textele pentru
  contabil nu poartă cuvinte din cod: „neimputabilă”, nu „neimputabila”; „Document justificativ: lipsește”, nu „nederivat”. Gard:
  verificator TITLU_FARA_DIACRITICE — un dicționar de cuvinte frecvente din titluri care nu au formă corectă fără diacritice
  (`_TITLU_FARA_DIACRITICE`, crește la fiecare titlu nou găsit), plus titlul „Factura” scris singur. Limita: un cuvânt corect și fără
  diacritice în altă formă („plata”, „luna”, „factura” articulat într-o frază) nu se poate judeca din text.

## 15. Tokeni de culoare, bordură, rază

- Culorile din cod folosesc EXCLUSIV variabile canonice: `var(--ardezie)` (text), `var(--gri)`/`var(--gri-clar)` (secundar), `var(--rosu)`/`var(--verde)`/`var(--galben)`/`var(--albastru)` (stări), `var(--linie)` (borduri), `var(--fundal)`/`var(--alb)` (fundaluri). INTERZIS hex ad-hoc (`#ddd`, `#8a97a5`, `#fff`) în aplicație.
- Border-radius folosește `var(--raza)` (6px). INTERZIS valoare literală (`border-radius:8px`). Excepție: `50%` pentru cercuri.
- **Amberul de TEXT (v2.33, 25.08.2026)**: `--galben` (#c9961f) e culoarea semaforului, nu a textului — pe `--galben-fundal` dă **2.42:1**, sub prag. Textul de avertizare pe fundal deschis folosește **`var(--galben-text)`** (#92500a, 5.64:1). Adăugat cu ocazia R41 partea II, unde eticheta „verdict stătut" cerea un amber lizibil. `.cf-galben` rămâne pe hexul lui până la o migrare separată.
- **Linkul de acțiune pe rândul zebră (v2.81, 08.10.2026)**: `.btn-link` (#2f6fa6) dă **4,13:1** pe `--albastru-clar` (#d6e4f5, rândul impar
  al `.zebra-lista`) — sub 4,5:1. În `.zebra-lista`, `.btn-link` folosește albastrul închis #1a5a94 (cap.1, `.buton-activ`): 5,55:1 pe
  rândul zebră, 7,16:1 pe alb. Găsit de axe pe „Contează” din Istoric facturi (ascuns până azi de aplatizarea rândului, cap.1 v2.81).
  Gardian: `core/test_contrast_zebra.py` (calculează contrastul din `stil.css`).
- **Textul colorat pe rândul zebră al tabelelor (v2.82, 08.10.2026)**: zebra oricărui tabel (`table tbody tr:nth-child(odd) td`,
  `--albastru-clar`) redefinește pe celulă `--verde` = `--verde-inchis` (#1b7349, 4,53:1); `--verde` canonic (#1d7a4d) dădea 4,13:1
  („● se închide” pe Balanță, găsit de axe). Redefinirea de token acoperă și stilurile inline (`color:var(--verde)`) și clasele din
  celulă. Gardian: `core/test_contrast_zebra.py::test_textul_colorat_pe_randul_zebra…` (verde, roșu, gri, amber ≥ 4,5:1).
- **Griul deschis de TEXT (v2.80, 08.10.2026)**: `--gri-clar` (#8a929e) dă **3,14:1** pe alb și **2,84:1** pe fundalul notificării necitite (#eef4ff), sub pragul WCAG 1.4.3 (4,5:1) — e pentru fundaluri, borduri și `::placeholder`, nu pentru text. Textul secundar folosește **`var(--gri)`** (#5b6573, 5,91:1). Găsit de axe pe clopoțel (ora notificării); aceeași clasă cu amberul de mai sus. Gardian: `CULOARE_SEMAFOR_TEXT` în `verificator_conformitate.py` (excepție: `::placeholder`).
- Landing page (`pagina-*`, login) e sistem vizual separat (marketing) — nu se supune paletei aplicației.

---

## 16. Panouri de conținut
- Orice casetă de conținut așezată direct pe corpul gri al ferestrei folosește clasa canonică `.panou`: fundal ALB + bordură `#b9c2cf` + `var(--raza)` + padding 12/14. Clasele specifice ecranului adaugă DOAR diferențele (margin, layout, border-style), nu redefinesc fundalul/bordura.
- INTERZIS panou transparent sau pe `var(--fundal)` direct pe corpul ferestrei — gri pe gri = invizibil. Excepții legitime: stări hover, sub-zone în interiorul unui panou alb (ex. antet de fir), zone de scroll tip `rec-modal-corp`.
- Exemple conforme: `pac-rezumat`, `pac-deschide-zona` (dashed), `grila-campuri-compacta`.

## 17. Fapte fiscale — o singură sursă, fără default tacit (backend)
- **DEFAULT_FISCAL_TACIT** (v2.16, 23.07.2026; extins v2.18, v2.19). Un câmp fiscal decisiv (`regim_fiscal`, `tip_firma`, `platitor_tva`, `tip_decont`, `operatiuni_ic`) **NU se defaultează pe LITERAL inline** — interzis `x or "micro"`, `x || "srl"`, `… else "pfa"`, `? : "trimestrial"`, `operatiuni_ic or False`, `operatiuni_ic || false` (literalele: micro/profit/srl/pfa/lunar/trimestrial + booleanul True/False/false și "da"/"nu" pentru `operatiuni_ic`). Un câmp obligatoriu care nu se poate autocompleta (ex. `tip_decont` — ANAF v9 nu aduce periodicitatea; `operatiuni_ic` — profil declarat de contabil, decide obligația D390) se cere EXPLICIT, cu criteriul afișat prin `.camp-ajutor` (cap.6), fără preselecție tacită. Faptul, normalizarea și default-ul trăiesc **într-un singur loc**: primitivele din `core/migrare_api.py` (`regim_contabil` = tip_firma→partidă simplă/dublă, `regim_efectiv` = regimul CIT efectiv cu partidă simplă⇒None, `tip_firma_nrm` = normalizare + default 'srl'). Consumatorii le importă; NU redau fallback-ul. Motiv: un `regim_fiscal or "micro"` inline în logica de obligații fabrică declarații pe firme la care nu se aplică (dovedit: termene emitea D100 pe un PFA, 23.07). Se prinde forma or/||/else — fallback pe CITIRE (`x or "micro"`, `x || "srl"`, `… else "pfa"`, ternar `? … : "micro"` cu literalul în ramura ELSE = default când câmpul lipsește); atribuirea simplă `x = "srl"` (declarație, nu fallback) și maparea valoare→etichetă `x === "profit" ? "profit" : …` (literal în ramura THEN) NU se prind. Regula **DEFAULT_FISCAL_TACIT** în verificator scanează **`.py` ȘI `.js`**; EXCEPTAT: `migrare_api.py` (primitivele — singurul loc unde literalul e legitim). Frontendul folosește FAPTUL expus de backend (`regim_contabil` prin `tenantii_userului` / `/migrare/vector`), nu defaultează inline.
- **FAPT_FISCAL_NECERUT** (v2.77, 07.10.2026, comanda Costin — `scan_formulare_operatiuni`). **O cheie pe care serverul o citește și
  care e fapt fiscal (schimbă nota, baza sau impozitul) intră în formular, cerută explicit, fără preselecție. O cheie strict
  tehnică, pentru API, rămâne în afara ecranului** — cu motivul scris lângă ea (`CHEI_IN_AFARA_ECRANULUI`). Trei consecințe pe
  formularele Operațiunilor: (1) niciun select obligatoriu nu vine cu o opțiune aleasă — motorul pune „— alege —” pe oricare;
  (2) un câmp e opțional numai dacă golul lui NU e o valoare pe care serverul o pune în locul omului (`OPTIONALE_PERMISE`: sumă
  goală = 0, cont gol = 371, dată goală = data notei sunt implicite, deci câmpul e obligatoriu); (3) o cheie citită pe o ramură
  are câmpul vizibil pe acea ramură. Gard: verificator `FAPT_FISCAL_NECERUT` + `core/test_formulare_operatiuni_campuri.py`, pe
  același instrument (`scripts/scan_formulare_operatiuni.py`). LIMITA: vede formularele din registrul Operațiunilor; ecranele
  scrise de mână nu.
  **Extinsă la ecranele scrise de mână (v2.78, 07.10.2026, comanda Costin — `scan_selecturi_ecrane`):** un select a cărui valoare e fapt
  fiscal (inclusiv conținutul unei declarații către ANAF) pornește cu `ALEGE` / `alegeDacaLipseste(valoare salvată)` din `api.js`, iar
  handlerul care trimite îl cere cu `cereAlegerile(rădăcină, câmpuri)` (refuz lângă câmp). Fiecare select din aceste ecrane e fie
  conform, fie clasificat cu motivul (`CLASIFICARE`). Gard: același `FAPT_FISCAL_NECERUT` + `core/test_selecturi_ecrane.py`.
  **Corectată (v2.79, 07.10.2026, comanda Costin, lotul 07.10 B A.1) — când e permisă preselecția.** *„Preselecția e PERMISĂ când
  valoarea (a) e cazul uzual sau se deduce din date (țara din CUI-ul partenerului, regimul din profilul firmei, moneda RON), (b) se
  vede pe ecran înainte de confirmare și (c) se poate schimba. Preselecția e INTERZISĂ pentru un fapt care depinde de situația
  concretă și pe care aplicația nu-l poate ști: Da/Nu situaționale (imputabil, faliment, asigurat, certificat de amânare …),
  categoria sau temeiul dintr-o declarație, tipul imobilului, valabilitatea, opțiuni de regim alese de contribuabil. Acolo rămâne
  „— alege —”.”* Mecanic: (1) o preselecție permisă stă în `CLASIFICARE` ca `PRESELECTAT_PERMIS`, cu criteriile (a)–(c) scrise în
  motiv (moneda / țara dedusă din CUI / tipul operației / documentul la emitere, moneda facturii recurente, destinația TVA pe linie,
  cererea inițială D318); (2) **un câmp din Operațiuni nu vine precompletat și nu arată text gri** — PIVOT lotul 13 (deficiența 504, comanda Costin 13.1,
  verbatim: *„Câmpurile nu au voie să arate valori gri sau precompletate care induc în eroare […] Câmpul rămâne gol.”*), care înlocuiește
  „câmpul-cont vine precompletat VIZIBIL cu sugestia standard” din v2.79: câmpul (cont, cotă, sumă) pornește gol, contul uzual se spune
  în explicația câmpului („De regulă 707.”), iar golul se refuză lângă câmp. Mecanic: `scan_formulare_operatiuni.motor_fara_precompletare`
  (în `masoara()`, deci în verificator, `FAPT_FISCAL_NECERUT`) pică dacă motorul pune `sugestie` ca valoare sau ca `placeholder`;
  (3) **un DA/NU situațional nu e căsuță de bifat** — o căsuță nebifată răspunde „Nu” în locul omului: e `selectDaNu` din `api.js`
  („— alege —” + Da/Nu, citit cu `daNu`), cerut de handler; fiecare căsuță rămasă e în `CASUTE`, cu motivul (rectificativa = cazul
  uzual, setări de acces, selecții de lucru); (4) **un input cu valoare pusă de ecran** (literal sau `|| "x"`) e în `INPUTURI`, cu
  motivul; o valoare impusă de lege e FIXĂ (readonly), nu alegere — D398 „se întocmește în euro” (CF art.314 alin.(10)); (5) un fapt
  DA/NU din Date firmă fără implicit în schemă (`activitate_exceptata_amef`, `inreg_art317`) e `CERUT_LA_PRIMA_FOLOSIRE`: „— alege —”
  când e neales, salvarea îl lasă nul, refuzul numit (cu buton spre Date firmă) vine la prima folosire relevantă.

## 18. Carduri pe firmă — regim obligatoriu, o singură sursă

- Fiecare card din meniul unei firme (`meniuFirma`, `optiuni`) declară `regim: "ambele" | "simpla" | "dubla"` **OBLIGATORIU** (ca `activ`), fără default tacit. Vizibilitatea derivă prin `regim_contabil` (fapt UNIC, `migrare_api`): `optiuni.filter(o => o.regim === "ambele" || o.regim === t.regim_contabil)`. INTERZISE liste hardcodate paralele pe `tip_firma` (fostele `DOAR_SRL`/`DOAR_PFA` — a 4-a sursă la aceeași întrebare, eliminate 23.07). O regulă, ca `STRATURI_META` la straturile de migrare. Regula **CARD_REGIM** în verificator (card fără `regim` = eroare).
- `t.regim_contabil` cu **contract STRICT**: expus de backend (`auth_api`); dacă lipsește pe obiectul-firmă, meniuFirma **eșuează vizibil** (throw), NU degradează tăcut la „doar ambele". Orice cale nouă către meniuFirma (ex. din Termene) trebuie să propage `regim_contabil`, ca `tip_firma`.
- Regim per concept: partidă dublă (`dubla`) = jurnal, balanță, bilanț, operațiuni speciale, stocuri (371/607), centre de cost. Partidă simplă (`simpla`) = RIP. Restul = `ambele` (declarații — un PFA datorează D112/D300/…, excluderea fină D100/D101/D406 o face `neaplicabile_forma` în ecran, nu ascunderea cardului; Casă — plafon Legea 70/2015 se aplică PFA). Un card care e „ambele" dar conține operațiuni de un singur regim se filtrează FIN în interior, NU se ascunde (ex. Casă: contarea 5311 e partidă dublă, plafonul e pentru toți).

- **Grupuri în fereastra firmei (v2.71, 05.10.2026, comanda Costin).** Gard `GRUP_FIRMA`. Cardurile stau sub titluri de grup care urmează munca contabilului — Zilnic · Registre · Raportări și declarații · Operațiuni speciale · Firma — dintr-o SINGURĂ sursă: `GRUPURI_FIRMA` (firme.js) dă cheile, titlurile și ordinea; fiecare card declară `grup` imediat după `regim`. Titlul grupului e `.pf-subtitlu` (h3), cardurile rămân în `.firme-optiuni`; `.firme-grup` e doar cârlig de structură. Un titlu fără niciun card vizibil (regim SRL/PFA) nu apare. Fără arbore în fereastra firmei: un singur nivel, titlu + carduri.

- **Planul de conturi (v2.85, 09.10.2026, decizia Costin la „Retest 2” pct.13).** Card „Plan de conturi”, `regim: "dubla"`, grupul
  Firma. Ecranul urmează tiparul registrelor: o căutare după cont sau denumire; analiticele afișate sub contul lor sintetic (sinteticul
  apare când se potrivește el sau unul din analiticele lui); adăugarea unui analitic de către contabil (formularul de sus, sau „Adaugă
  analitic” pe rândul sinteticului, care precompletează `4111.`); ștergerea refuzată pe server pentru un cont folosit în note (și
  pentru un sintetic cu analitice), iar pe ecran butonul „Șterge” nici nu apare pe un cont folosit. Verbatim: „listă cu căutare după
  cont sau denumire, analiticele afișate sub contul sintetic, adăugare de analitic de către contabil, iar un cont folosit în note nu se
  poate șterge”. Gard: `core/test_retest2.py` (refuzul pe server, gruparea sub sintetic).

## 19. Consistența versiunii de modul la import — o singură instanță

- Un modul importat din mai multe locuri se importă cu **ACELAȘI token de versiune** peste tot (`?v=N` identic, sau consecvent fără). Browserul tratează `/x.js` și `/x.js?v=7` ca DOUĂ module distincte — le încarcă separat, rulează DOUĂ instanțe, iar starea/efectele uneia nu se văd în cealaltă. Se aplică și la `import()` **dinamic** (`await import("./x.js")`), nu doar la `import … from`.
- Simptom (23.07): antetul montat de `firme.js` apărea pe calea FIRME dar lipsea pe calea TERMENE — `termene.js` importa `./firme.js` fără `?v`, restul `?v=7`; a doua copie a modulului nu vedea starea primei. Aceeași clasă, prinsă de gardă: `navigator.js` deschidea `./ecrane/control.js` (dinamic, fără versiune) dublând modulul importat `?v=1` din cabinet/asistent.
- Regula **IMPORT_VERSIUNE** în verificator: grupează importurile locale (`./`, `../`) pe calea **REZOLVATĂ** relativ la fișierul care importă (nu pe basename — două fișiere omonime din directoare diferite pot avea legitim versiuni proprii); un modul cu >1 token distinct de versiune = eroare. Când bumpezi `?v=N` pe un modul, bumpezi **TOATE** site-urile lui de import odată.

## 20. Verdictul de control fiscal — un singur renderer, paritate mecanică de chei

- Corpul verdictului de control fiscal (declarații + verificări contabile) se randează **într-un singur loc**: `control_verdict.js` (`randeazaCorpVerdict`), consumat de ecranul Control fiscal (`control.js/detaliuFirma`) ȘI de cardul din fișa firmei (`firme.js/ecranControlFirma`). Amândouă cheamă același endpoint (`/control-fiscal/{id}`), deci același payload. **Sectiunile pot diferi între ecrane** (un ecran poate arăta mai puține secțiuni — altă altitudine, ex. lista de portofoliu = doar pastilă); **cheile dintr-o secțiune randată NU pot fi omise**. Interzise renderere paralele care aleg un subset hardcodat de chei — au produs constatări BLOCANTE invizibile (cazul DANTE 24.07: cele 4 roșii pe salarii + 5121 sold creditor nu apăreau pe cardul din fișă, deși payload-ul le conținea).
- **Cauza de fond:** rendererul alegea chei pe NUME din `verificari_contabile`. O cheie nouă produsă de backend fără consumator rămânea invizibilă, tăcut. De aceea regula are **gardă mecanică cu DOUĂ parități** (verificator, `VERDICT_PARITATE`), peste cheile PRODUSE efectiv (parsate din sursa `_verificari_contabile`, nu hardcodate — o cheie nouă e prinsă automat):
  1. **Randare:** fiecare cheie `vc` ∈ inventarul declarat al **fiecărui** consumator care alege chei pe nume — `VC_RANDATE` din `control_verdict.js` (verdictul: secțiune, „via d.contabil", sau contor) ȘI `VC_VERIFICARI` din `firme.js/ecranVerificari` (ecranul „Verificări", endpoint separat `/firme/{id}/verificari`: randat, sau IGNORAT-cu-motiv). Cross-check-urile declarație-vs-contabilitate sunt ignorate declarat în „Verificări" — aparțin exclusiv verdictului din Control fiscal; declarația e explicită, nu omisiune tăcută.
  2. **Severitate:** fiecare cheie `vc` fie e pliată în `contabil` (`_construieste_contabil` → `pastila_firma`), fie declarată `VC_FARA_SEVERITATE` (cu motiv) în `main.py`. Altfel un roșu apare în corp dar nu urcă header-ul (contradicția 23.07, inversată).
- **Excepțiile se DECLARĂ cu motiv, nu se judecă tăcut:** `documente_pozate` și `tva`-simplu nu urcă azi pastila — declarate explicit în `VC_FARA_SEVERITATE`; decizia de a le urca rămâne deschisă. Limita gărzii (ca la CARD_REGIM): garantează că fiecare cheie e DECLARATĂ undeva, nu că directiva chiar randează / ridică severitatea.
- Restanțele: **listă plată sortată pe termen** (C4, 23.07), nu grupate pe tip — un singur criteriu, în renderer, pe ambele ecrane.
- **Limba mesajelor de verdict** (diacritice + fără nume interne): mesajele din `neclar`/`neaplicabile`/`datorate` (secțiunile „nu pot verifica" / „nu se datorează" / restanțe) sunt text pe ecran → **diacritice complete** (DS cap.1) și **niciun nume intern de câmp/coloană** arătat contabilului (Regula 14 pct.4: se folosește label-ul UI — ex. „Data înregistrării în scopuri de TVA", NU `platitor_tva_anaf_inceput`). Gardul canonic de diacritice (`core/test_diacritice_afisate.py`) NU le vede — sunt argumente POZIȚIONALE către emitenții `gri()`/`neaplic()`/`emite_tva()` și return-uri de builder, în afara rolurilor lui (detail HTTPException / valori de dict sub chei de afișare / corpuri de excepții). Gardă dedicată: **`core/test_control_fiscal_diacritice.py`** (audit tenant_004, 17.08.2026). Clasă mai largă, NEguardată încă: erorile de generare declarații (`raise ValueError` inline în d100/d101/d112/d205/bilant_api) afișate contabilului — enumerate în GARZI; criteriul: text pe ecran ↔ diacritice vs eroare developer ↔ ASCII, distincție NE-mecanică (de aceea gardul canonic e conservator).

## 21. Marca — „iConta.eu" peste tot (material public)

- Forma canonică a mărcii, în ORICE material public, este **`iConta.eu`** (i mic, C mare, `.eu` inclus în nume) — regulă din MARKETING.md (cap. BRAND), **fără excepții**. Motiv: există alte „iConta"; `.eu` desprinde marca clar. Material public = tot ce vede utilizatorul sau clientul: textul din aplicație (bara de sus, ferestre, mesaje, butoane, **titlul filei**), **alt-urile de logo**, și literalele de email (subiect + corp) care pleacă spre cabinet/client.
- Gardă mecanică: **BRAND_EU** în `verificator_conformitate.py` — scanează frontendul (`static/**/*.{js,mjs,html}`) + literalele publice din backend (`main.py`, `core/notificari_scadenta.py`, `core/observare.py`) și semnalează orice `iConta` **neurmat de `.eu`**. Al doilea assert: **zero `iConta.eu.eu`** (dublură din corecții suprapuse).
- Excepții (fiecare cu motiv, oglindite ca listă albă în verificator; detaliu în DECIZII 26.07):
  - **„Admin iConta"** — nume propriu al panoului de administrare (breadcrumb, antet, mesaje „Doar Admin iConta"), nu o apariție a mărcii; rămâne așa. Gardă îl sare per-apariție (secvența „Admin " înaintea mărcii).
  - **`<SoftwareCompanyName>` / `<SoftwareID>` din SAF-T (`core/d406.py`)** — identificarea softului emitent către ANAF, câmp **fiscal**, nu cosmetică; schimbarea e o decizie separată. `d406.py` e în afara scopului scanat.
  - **Comentarii (`//`, `#`) și docstring-uri** — nu se randează, nu-s material public.
  - **`iconta_nou` / `iconta-nou` / `iconta_v2`** — cale de cod / unit systemd / schemă DB; cu „c" mic, nu marca.

## 22. Pagini publice de ghid

**Domeniu:** rutele `/ghid/{slug}`. Pagini publice, indexabile, care explică o problemă fiscală reală și arată cum o rezolvă iConta.eu.

**Graniță.** Ghidurile sunt **înăuntrul** sistemului de design, nu alături de el. Nu beneficiază de scutirea acordată landing-ului. Verificatorul le păzește ca pe ecranele aplicației.

---

### 1. Ce se refolosește, fără excepție

**Culori:** exclusiv tokenii din cap.15 — `--ardezie` (text), `--gri`/`--gri-clar` (text secundar), `--albastru` (accent), `--linie` (borduri), `--fundal`/`--alb` (fundaluri), plus stările `--rosu`/`--verde`/`--galben`. Niciun hex în CSS-ul ghidurilor, niciun `<style>` inline în shell.

**Tipografie:** scara din cap.14 — `--text-titlu` 22px · `--text-sectiune` 19px · `--text` 17px · `--text-mic` 15px · `--text-desc` 13px · `--text-micut` 12px — plus clasele `.tip-*`. Fără dimensiuni în pixeli scrise de mână.

**Raze:** `--raza`. Fără valori inline.

**Icoane:** exclusiv din `ICOANE`. Fără SVG-uri locale.

**Semafor:** `--verde`, `--galben`, `--rosu-semafor`, cu grila existentă.

---

### 2. Relația cu landing-ul

Landing-ul folosește azi valori hexazecimale scrise direct (accent, butoane, hero) și o familie de font proprie. Este o excepție istorică, tolerată prin lista albă a verificatorului.

**Ghidurile nu moștenesc această excepție.** Ele folosesc tokeni.

Consecința practică: dacă un token nu produce rezultatul vizual dorit lângă landing, **se schimbă tokenul**, nu se scrie hex în ghid. Divergența se rezolvă în sus, către sistem, niciodată în jos.

Alinierea landing-ului la tokeni rămâne o sarcină deschisă. Până se face, tranziția vizuală dintre landing și ghid poate fi ușor perceptibilă. Este acceptat temporar; nu este un motiv de a introduce hex în ghiduri.

---

### 3. Componente proprii

Ghidurile au cinci componente pe care aplicația nu le are, pentru că nu-i sunt necesare. Toate se construiesc din tokenii existenți.

**`.ghid-temei`** — blocul de temei legal.
Conține articolul citat exact și sursa. Se distinge prin bordură laterală, nu prin culoare de fundal proprie. Este elementul care susține credibilitatea paginii; nu se prescurtează și nu se parafrazează.

**`.ghid-exemplu`** — blocul de exemplu numeric.
Date fictive plauzibile („SC Exemplu SRL", sume rotunde credibile). Niciodată date reale de clienți, niciodată date din tenanții de test. Sumele se formatează cu funcțiile canonice de bani.

**`.ghid-semafor`** — semaforul, în rol grafic.
Aceiași tokeni și aceeași ordine roșu → galben → verde ca la capitolul semaforului. Diferă exclusiv prin mărime și prin rol: aici este ilustrație, nu stare de sistem. Nu introduce culori noi și nu inversează ordinea.

**`.ghid-comparatie`** — tabel manual contra automat.
Două coloane. Stânga descrie procedura manuală, complet și onest. Dreapta descrie ce face iConta.eu. Coloana din stânga nu se caricaturizează — un contabil recunoaște imediat o descriere falsă a propriei munci și pierde încrederea în tot restul paginii.

**`.ghid-procedura`** — pași numerotați.
Procedura manuală, pas cu pas, utilizabilă și fără produs. Aceasta este partea care aduce trafic și încredere.

---

**Componente de navigare (v2.72, 06.10.2026, comanda Costin — structură pentru indexare):**
- **`.ghid-teme`** — cuprinsul temelor de pe `/ghid`: o listă, câte un rând pe temă (titlu legat spre `/ghid/tema/{tema}`, numărul de ghiduri
  în `.ghid-numar`, descrierea temei). `/ghid` NU mai listează ghidurile — doar temele. Temele vin din `core/ghid_teme.TEME`, sursa unică.
- **`.ghid-lista`** — pagina unei teme: ghidurile ei, cu descrierea, ordonate după titlu, sub calea `.ghid-tema` („Ghiduri › Tema”).
- **`.ghid-legaturi`** — la finalul fiecărui ghid, după structura de la pct.5: „Ghiduri înrudite” (până la șase, din aceeași temă) și
  `.ghid-tema` („Tema: … · Toate temele”). Se generează, nu se scrie de mână în pagină.
- **`.ghid-actualizat`** (v2.90, 13.10.2026, comanda Costin pct.2c) — „Actualizat la zz.ll.aaaa”, imediat sub titlul fiecărui ghid, din
  `modified` al ghidului (sau data fișierului) — aceeași dată ca `dateModified` și `lastmod` din sitemap. Fără autori și fără titluri
  profesionale. Se generează (`public_ghid`), nu se scrie de mână. Gard: verificator GHID_ACTUALIZAT, `core/test_ghid_publicare.py`.
- **Contrastul paginilor publice (v2.90, 13.10.2026, axe pe /ghid):** orice text pe fundal `var(--p-…)` trece 4,5:1 — `--p-brand`
  e #0566EA (alb pe el 5,13; era #0672FE = 4,33: butonul „Intră în cont”, numărul pasului din `.ghid-procedura`). Linkul din pagină
  (`--p-link`) are față de text numai 2,7:1, deci **se deosebește și altfel decât prin culoare: e subliniat** (`.ghid-wrap a`, WCAG
  1.4.1). Gard: `core/test_a11y_contrast_tokens.py::test_paginile_publice_contrast`.

### 4. Regula variației

**Variația vine din conținut, nu din stil.**

Fiecare pagină alege dintre cele cinci componente pe cele relevante subiectului ei. O pagină despre controlul încrucișat folosește semaforul și tabelul de comparație. Una despre salarizare folosește exemplul numeric și procedura.

Paginile arată diferit pentru că *sunt* diferite, nu pentru că li se schimbă culorile, fonturile sau spațierile.

**Interzis:** paletă proprie per pagină, font propriu per pagină, componente inventate ad-hoc pentru o singură pagină.

Dacă un subiect cere o componentă care nu există, aceasta se adaugă în acest capitol înainte de a fi folosită — nu invers.

---

### 5. Structura unei pagini

Ordinea este fixă. Ce lipsește se omite; ce există nu se reordonează.

1. Titlu — problema, în cuvintele contabilului
2. Durerea concretă — ce se întâmplă azi, fără produs
3. Temeiul legal — `.ghid-temei`
4. Procedura manuală — `.ghid-procedura`
5. Exemplu numeric — `.ghid-exemplu`
6. Comparație — `.ghid-comparatie`
7. Ce face iConta.eu — scurt, la final
8. Legătură către înregistrare

Proporția: aproximativ 80% din conținut este valoare independentă de produs (temei, procedură, exemplu), aproximativ 20% este produsul. O pagină care începe cu produsul nu se clasează și nu convinge.

---

### 6. Conținut: ce se poate afirma

Fiecare afirmație dintr-o pagină provine exclusiv din lista de afirmații permise din registrul de marketing. Nicio afirmație din lista interzisă, în nicio formă, nici parafrazată.

Fiecare temei legal se verifică la sursa oficială înainte de publicare, nu din memorie.

---

### 7. Randare

Textul unei pagini stă într-un fișier Markdown separat. Nu în registrul de funcționalități — un text de 600–1000 de cuvinte într-o celulă face fișierul ilizibil.

Shell-ul care randează leagă foaia de stil canonică și folosește clase și tokeni. Fără `<style>` inline, fără culori scrise direct în șablon.

**Scroll de document.** Paginile publice folosesc scroll normal de document. Ele **NU** moștenesc regula globală `html, body { overflow-y: hidden }` — aceea aparține shell-ului aplicației/landing-ului (care are scroll intern propriu). Shell-ul public marchează `<html>` **și** `<body>` cu clasa `.pagina-publica`, iar foaia de stil readuce `overflow-y: auto` pe ea. Un shell public fără această clasă se taie la primul ecran (conținutul de sub fold devine invizibil, iar componentele par „text simplu"). Verificatorul îl prinde.

**Scroll-ul intern al aplicației (18.10.2026, deficiența 321).** Shell-ul aplicației e `.desktop` (navigator.js): are înălțimea ecranului (`height: 100dvh`) și derulează el însuși (`overflow-y: auto`). Cu `html, body { overflow-y: hidden }`, un desktop cu `min-height` în loc de `height` crește peste ecran și nu se mai derulează cu rotița — ce e sub cardurile „Primii pași” („De depus”, „Firme”) se ajungea doar cu Tab. Verificatorul îl prinde (`scroll_desktop`).

**Tot ce stă pe ecranul întreg derulează (lotul 12, deficiențele 561, 596, C111).** Sub `html, body { overflow-y: hidden }`, `#app` derulează el însuși (`height: 100dvh; overflow-y: auto`): ecranele puse direct în el (intrarea în cont, activarea, parola nouă) se ajung cu rotița până la capăt. Orice strat pe tot ecranul (`.acces-modal`, `.reaut`, `.fereastra`) are panoul cu `max-height` cât ecranul și derulare proprie, ca acțiunea principală și mesajele de eroare să se vadă mereu (CLAUDE.md §9). Verificatorul îl prinde (`lot12`, `SCROLL_APP` / `STRAT_INCAPE`).

**Formularul de înregistrare încape (v2.102, lotul 12, 642).** „Înregistrează cabinetul tău” (`.acces-modal-inreg`) are câmpurile pe două
coloane (`.reg-grila`), sigla mai mică, iar bifa termenilor, refuzul și „Creează cont” stau lipite jos (`.reg-actiune`, `position: sticky`):
la 1280×720, cu refuzul arătat, formularul încape. Gard: `core/test_lot12_form2_inregistrare.py`.

---

### 8. Verificator

Zona `/ghid` intră sub verificator, cu regulile aplicabile oricărei interfețe: culori din tokeni, tipografie din scară, raze din tokeni, icoane din setul canonic, formatare de bani și date prin funcțiile canonice.

Nu se adaugă pe lista albă a claselor publice.

## 23. Perioadă confirmată — starea care condiționează calculele din aval (v2.30)

**Tipar general**, nu doar pentru pontaj: o **perioadă** `(an, luna, domeniu)` are o stare **CONFIRMAT / NECONFIRMAT**.
Cât timp e NECONFIRMAT, datele ei sunt **informative**, iar orice calcul din aval care depinde de ele **se
blochează** cu blocaj motivat. Confirmarea o face un om, la închiderea perioadei; abia atunci datele devin
**autoritative**. Nevoia apare când absența unei intrări e ambiguă (ex. pontaj: prezent = fără rând nu distinge
o lună completă de una necompletată). Revine la **închiderea lunii contabile** și la **confirmarea inventarului**
— se folosește ACEEAȘI regulă, nu una paralelă per modul.

- **Starea**: stocată per `(an, luna, domeniu)` în schema tenantului, cu `confirmat_de` (id user) + `confirmat_la`
  (timestamp) — ca urma de la ciclul declarațiilor (creat_de/aprobat_de/depus_de). Domeniul e un șir stabil
  (`pontaj`, `contabil`, `inventar`).
- **Cine confirmă**: rolul **`admin_firma`** (RBAC). NU se inventează un rol nou.
- **Controlul** (reutilizează primitivele, ZERO pattern vizual nou): buton **`.buton-verde`** Confirmă [domeniul]
  lunii (cap.1) → **`confirmaCaseta`** (cap.5) cu întrebarea + consecința (Devine autoritativ pentru calculele
  din aval). NU `.caseta-poarta` (aceea e pentru două alegeri care merg amândouă înainte).
- **Afișarea stării**: **semafor** (cap.8) — **gri** `var(--gri-semafor)` = NECONFIRMAT, **verde** `var(--verde)` =
  CONFIRMAT. Lângă semafor, **`.caseta-info`** (cap.5): neconfirmat → nota că perioada e informativă și calculele
  din aval se blochează; confirmat → Confirmat de [nume] la [dată]. NU roșu (nu e atenționare/distructiv).
- **Calculul blocat**: blocaj MOTIVAT cu cele 4 elemente, afișat prin **`.stare-goala`** (cap.6: gol + cauză +
  ieșire). Backend: excepție cu tag care ajunge la utilizator (ca `PERIOADA_BLOCATA` → 423), nu traceback. Textul:
  ce s-a oprit (calculul X pentru luna) · de ce (perioada neconfirmată + temeiul) · ce se poate face (butonul de
  confirmare) · cine decide (admin_firma, la închidere).
- **Reversibilitate**:
  - ÎNAINTE de depunerea unei declarații pe lună: modificarea datelor perioadei **de-confirmă AUTOMAT** (revine
    NECONFIRMAT, calculele din aval re-blochează până la re-confirmare).
  - DUPĂ depunere: modificarea datelor perioadei se **BLOCHEAZĂ** (o declarație depusă e fapt la ANAF; editarea
    liberă ar face sistemul să arate alte cifre decât cele depuse, fără semnal). Ieșirea e fluxul de
    **rectificativă** (coada_api / d710). Dacă acel flux nu suportă re-depunerea pe lună, blocajul e FINAL până se
    construiește — limită declarată în GARZI, nu improvizație.

**Gardă mecanică** (verificator): orice calcul dependent de o perioadă verifică confirmarea, iar controlul de
confirmare folosește primitivele canonice. Dacă nu se poate defini curat pe criteriu structural, LISTĂ EXPLICITĂ
întreținută manual (ca markerii TEMEI), cu limita declarată.

## 24. Rânduri dinamice în formulare

Stratul de DEDESUBTUL cap.6: cap.6 guvernează PLASAREA erorii lângă câmp și presupune un id DOM stabil ca DAT.
Acest capitol spune DE UNDE vine acel id și cum se comportă o listă de rânduri care crește și scade. Se aplică
oricărui formular cu rânduri repetate adăugate de utilizator (linii de factură, bunuri e-Transport, ingrediente
rețetă, linii de jurnal). NU rescrie cap.6 — îl referă.

- **Re-randare integrală la orice mutație.** Adăugarea sau ștergerea unui rând RE-RANDEAZĂ întreaga listă din
  modelul de date (`container.innerHTML = randuri.map(...)`), nu mută/inserează/șterge noduri DOM individual
  (`appendChild`/`insertBefore`/`removeChild` de rând). Motiv: mutarea de noduri desincronizează indicii DOM de
  poziția în model; re-randarea din model garantează că id-ul `#{prefix}{i}-camp` corespunde mereu rândului `i`.
- **Id-ul de câmp derivă din poziția în listă, iar lista randată = lista validată.** Id-ul unui câmp-din-rând e
  `{prefix}{i}-{camp}`, cu `i` = poziția în modelul de date. Lista trimisă la validare e ACEEAȘI cu cea randată:
  frontendul NU filtrează rânduri înainte de validare. Un rând incomplet se VALIDEAZĂ și se RAPORTEAZĂ (eroare
  lângă câmpul lipsă, cap.6), nu se aruncă tăcut. Filtrarea tăcută rupe corespondența id↔rând (rândul 2 filtrat
  face eroarea rândului 3 să arate spre alt câmp) și ascunde un rând început — încalcă „niciodată tăcere la o
  acțiune eșuată" (cap.6).
- **Orice listă care poate crește trebuie să poată și scădea.** Un rând adăugabil e un rând ștergibil: adăugarea
  fără ștergere e INTERZISĂ (un rând introdus greșit, fără cale de retragere, e o fundătură). Ștergere per rând
  (buton `.buton-sters` pe rând) + re-randare din model (regula 1).
- **Validarea per-câmp pe rânduri aparține BACKENDULUI.** Backendul e poarta autoritară și întoarce erorile
  field-keyed per rând (`{camp, eticheta}` sau echivalent, cap.6 pct.2). Frontendul NU ține o A DOUA funcție de
  câmpuri-lipsă care oglindește backendul — oglinda DRIFTEAZĂ (un câmp verificat într-un capăt și nu în celălalt;
  dovedit: `valoare_fara_tva` verificat în backend, nu în frontendul e-Transport). Frontendul CONSUMĂ răspunsul de
  eroare al backendului și plasează erorile conform cap.6 (mecanism A pe `camp`, fallback B). O gardă de prezență
  client-side rămâne permisă DOAR ca UX preventiv nemirror, nu ca a doua listă de câmpuri-lipsă per rând.
- **Un preț sau un articol pe care nu l-a ales omul nu stă pe rând (v2.75, comanda Costin 06.10.2026 pct.1b/1c).**
  „Un preț pe care nu l-a ales nimeni nu se propune: câmp gol și obligatoriu, sau prețul de vânzare din nomenclator,
  dacă articolul îl are.” Rândul nou pornește cu prețul GOL și cu articolul NEALES (lista de articole are o opțiune goală
  și pornește pe ea — nu pe primul articol). Ce vine din PROPUNERE (prețul de vânzare din nomenclator, UM-ul articolului)
  e al denumirii pentru care s-a propus: când denumirea se schimbă, se golește. O denumire scrisă de mână, diferită de
  articolul ales, DEZLEAGĂ rândul de articol (instanța: „Carte – Ghid contabil 2026” pleca la emitere legată de „Marfa A”
  și s-ar fi descărcat din stocul ei). Un articol ales și un nume de articol nou scris în același timp se exclud. Un câmp
  de preț golit pleacă drept LIPSĂ (`null`), niciodată ca 0 (`parseFloat(…) || 0` pe un preț e INTERZIS); serverul
  refuză lipsa lângă câmp, iar 0 scris de om rămâne permis. Gard: verificator `PRET_SAU_ARTICOL_NEALES`.

- **Nicio entitate nu se alege tastându-i ID-ul intern (`op-mijloc_fix_id`, gard `ID_INTERN_TASTABIL`; v2.76, C4).** Un câmp care leagă operațiunea
  de o entitate a firmei (mijloc fix, articol, partener) e o LISTĂ din registrul ei, cu denumirea și ce ajută la recunoaștere
  (cod, valoare rămasă), nu un câmp numeric „ID …”. Instanța: „ID mijloc fix” la reevaluare și casare — contabilul trebuia să
  știe ID-ul din baza de date, iar refuzul îi cerea „alege-l din listă” fără listă. Gard: verificator `ID_INTERN_TASTABIL`.
- **Trimiterea în coadă are UN drum (v2.76, comanda Costin 07.10.2026, C1/C2/C3/C11).** Orice ecran trimite o declarație în coadă
  prin `ecrane/coada_trimite.js` (`trimiteInCoada`): același corp ca la generare, refuzul cu motivul REAL venit de la server,
  atenționările DUK afișate cu o casetă de confirmare scrisă, eroarea DUK fără portiță. INTERZIS `api.post("/coada", …)` scris de
  mână într-un ecran. Gard: verificator `COADA_UN_SINGUR_DRUM`.

**Gardă mecanică** (verificator): din cele patru reguli, doar a patra e curat verificabilă mecanic FĂRĂ a aprinde
ecrane în afara restructurării în curs.
- **MIRROR_CAMPURI_LIPSA** (regula 4): interzice în `static/js/ecrane` o funcție/variabilă de câmpuri-lipsă care
  oglindește validarea backend (nume `*campuri*lipsa*`). e-Transport + emitere = EXCEPȚIE declarată până la
  batch 3 (ca `test_g10_eroare_langa_camp` / lista G10-A). LIMITĂ: prinde convenția de nume, nu o re-implementare
  sub alt nume — restul rămâne disciplină de review.
- Regulile 1-3 NU se cablează acum: un gard pe re-randare (1), pe filtrare-înainte-de-validare (2) sau pe
  add-fără-delete (3) ar aprinde ecrane funcționale în afara batch 3 (`facturi_ecran.js`, `firme.js`
  rețete/jurnal) care azi filtrează/mută noduri legitim până la restructurare. Se cablează prin ratchet, pe măsură
  ce ecranele se conformează, nu dintr-odată.


## 25. Ecranul ca entitate — ASPECTE (proprietari) și CHIRIAȘI (ocupanți) (v2.32, 21.08.2026)

Stabilit cu Costin, 21.08.2026. Împărțirea ecranului NU se face după regiuni de pixeli, ci după
**cine deține spațiul** față de **cine îl locuiește**. Proprietarul dă spațiu și ciclu de viață;
chiriașul dă înțeles. Scopul e ca oricare să poată fi schimbat fără să-l atingă pe celălalt.

**CONTRACTUL, în două propoziții:**
1. Proprietarul **nu interpretează niciodată** ce spune chiriașul.
2. Chiriașul **nu se atinge de spațiu care nu e al lui**.

### 25.1 Aspectele — se disting prin CICLU DE VIAȚĂ (ăla nu se poate împărți)

| aspect | trăiește | se schimbă când |
|---|---|---|
| **Cadrul** | toată sesiunea | login / ieșire |
| **Zona de lucru** | un pas | navighezi |
| **Fereastra** | cât e deschisă | deschizi / închizi (ține în ea o zonă de lucru) |
| **Efemerul** | secunde | apare un mesaj și moare singur |

Aspectele se pot cuprinde unul pe altul (Cadrul are fâșii: bara de sus, bara de stare; fereastra are
antet și corp). **Chiriașii sunt frunzele.**

**Designul NU e aspect, e STRAT.** Tokenii + gărzile verificatorului traversează toate aspectele.
Independența lui funcționează invers: trebuie să fie COMUN, nu izolat — o schimbare de token mișcă tot
ecranul deodată, și ăsta e scopul. La fel accesibilitatea și limba.

### 25.2 Chiriașii — se disting prin ÎNTREBAREA la care răspund

| chiriaș | răspunde la |
|---|---|
| **Identitatea** | cine sunt, ce cabinet, ce firmă |
| **Drumul** | pe unde am umblat, unde sunt |
| **Starea de lucru** | pe ce firmă/lună lucrez acum |
| **Comunicarea** | ce s-a întâmplat, ce trebuie confirmat, ce a eșuat |
| **Acțiunile globale** | ieșire, ghid, notificări |
| **Lucrul** | conținutul util |
| **Necunoașterea declarată** | ce nu poate spune ecranul |

**Un chiriaș are UN SINGUR contract.** Dacă e în două locuri, ori sunt doi chiriași diferiți (și
trebuie numiți diferit), ori e o scurgere.

### 25.3 Diagnosticul măsurat la 21.08.2026 — chiriași fără contract

- **Drumul** stă în două locuri: verigile din `.bara` (răspund la „cine ești / ce firmă") și
  `.fereastra-fir` (răspunde la „pe unde ai umblat"). NU e dublare — sunt doi chiriași — dar nimeni
  n-a scris care e care, deci se citesc ca dublare.
- **Comunicarea** stă în PATRU: toast la login (`sumar-toast`), mesaje inline în ecrane
  (`arataMesaj`), dialogul de confirmare (`confirmaCaseta`, în `api.js`), **și bara de stare, unde un
  ecran scrie direct** (`cabinet.js:467` și `:511` fac `document.querySelector(".subbara")`).
- **Starea de lucru** e rescrisă din conținut — deci chiriașul nu-și controlează propriul contract.
  Ăsta e mecanismul incidentului „indicatorul mincinos" (patru ochi, 20.08).
- **Drumul poate fi corupt din conținut**: back-ul consumă poziția reală ÎNAINTE de un `setInapoi`
  custom, „altfel antetul acumula ferestre/pași — dovedit în browser" (`navigator.js`).
- **Necunoașterea declarată** n-are contract deloc: trăiește în docstringuri, unde contabilul n-o vede.

**Gardul care face diviziunea reală** (de construit): niciun `document.querySelector` / `getElementById`
din `static/js/ecrane/*.js` către `.bara`, `.subbara`, `.bara3`, `.bara-antet`. Excepțiile se declară
cu motiv scris, ca `# upsert-ok:`.

### 25.4 „Ce nu poate spune verificarea asta" — chiriașul nou

**Ce NU intră** (asta o salvează de la a fi coș de gunoi):
- necunoașterea legată de un OBIECT rămâne lângă obiect (o obligație pe care n-o pot verifica stă în
  „Nu pot verifica", cu tipul și perioada ei) — mutată în listă separată, se rupe de lucrul despre care
  vorbește;
- datoriile de dezvoltare (xfail) NU intră: sunt ale noastre, nu ale contabilului.

**Ce intră:** ce nu poate afirma INSTRUMENTUL, indiferent de date. E despre CAPACITATE, nu despre date.

**De ce e necesară:** câmpul `limita` există deja pe constatări, dar se randează doar când EXISTĂ o
constatare. Pe o firmă curată limitele dispar — adică exact când verdictul e cel mai ușor de citit
greșit. Verdele arată ca „am verificat tot" tocmai fiindcă n-are nimic sub el care să spună ce nu.
E aceeași eroare ca `absenta_observatie`, mutată un nivel mai sus.

**Trei feluri de conținut:**
1. **Acoperirea** — ce compar și ce NU. („Compar cu evidența din iConta. Nu compar cu ce are ANAF în
   SPV — o declarație depusă direct la ANAF, neînregistrată aici, nu apare.")
2. **Perimetrul privit** — fereastra și sursele. („Am privit dec.2025 → azi, din facturi, note
   validate, e-Factura. Ce există doar pe hârtie nu ajunge aici.")
3. **Ce ar face afirmația mai tare** — remediul. („Închide lunile pe facturi și pot spune «nu se
   datorează» cu acoperire, nu doar pe calendar.") Al treilea o face utilă, nu doar onestă.

**Formă:** jos, permanentă, necolorată, compactă (2-3 rânduri, detaliul la extindere). Nu sus (nu e
alarmă), nu într-un „?" (dispare pentru cine are nevoie), nu colorată (nu e problemă de rezolvat).
**Permanența e esențială**: dacă apare doar câteodată, prezența ei devine semnal și absența ei minte.

**Nu se scrie de mână.** Se compune din limitele declarate ca DATE de fiecare verificator care
contribuie la ecran. Gard: un verificator care apare pe ecran fără `limita` declarată → pică.

### 25.5 Afirmațiile despre datele firmei sunt OBIECTE, nu șiruri

Textul e UN atribut, nu recipientul tuturor. Atributele, descoperite empiric: `fel` (fapt /
necunoaștere / absență de observație / opinie / contradicție) · `obiect` (tip + perioadă) · `sursă` ·
`temei` (act, sau regulă de produs cu decizie+dată) · `poartă` (ce acoperă și ce nu) · `remediu` ·
`severitate` (decisă o singură dată) · `text` (scris de om, în limba contabilului).

**GRANIȚA (decisă de Costin):** regula se aplică **afirmațiilor despre datele firmei** — verdicte,
motive, blocaje, constatări. **NU** textelor de interfață (titluri, etichete, ajutoare): alea sunt
design. Fără graniță, devine un proiect de traduceri și moare.

**NU se asamblează șabloane.** Un mesaj compus din câmpuri sună a formular („Obligație: D100.
Perioadă: T4 2025."). Proza rămâne scrisă de om; structura stă lângă ea, nu în locul ei.

## 26. Un atribut ținut în DOUĂ locuri — două nume distincte, și care produce efectul (v2.61, 28.08.2026)

**Regula.** **Două lucruri diferite primesc două nume distincte.** Când aceeași entitate are un
atribut în două locuri, ecranul nu alege tăcut între ele: le arată pe amândouă, cu etichete care
spun **de unde vine fiecare**, iar când **diferă**, spune **care dintre ele produce efectul**
(pleacă pe hârtie, ajunge la client, intră în calcul). Când coincid, se spune și asta.

### 26.1 Cele două instanțe din care s-a scris

- **R63 — aceeași persoană are două adrese în aplicație.** `public.users.email` e adresa cu care
  clientul **intră** în portal; `firma_profil.email` e cea la care **primește** pachetul lunar.
  Decizia lui Costin a fost **(c)**: *rămân două, fiindcă înseamnă lucruri diferite… cine intră în
  portal și cine primește pachetul lunar chiar pot fi persoane diferite.* Ce s-a schimbat au fost
  **numele** — *Adresa de autentificare* și *Adresa la care primești pachetul lunar* —, iar
  formularul spune explicit că pachetul **nu** urmează schimbarea. Tot de acolo vine și jumătatea
  care se uită ușor: *un ecran care arată aceeași adresă în două câmpuri fără să spună că sunt
  distincte produce chiar presupunerea greșită.*
- **R81 — o firmă are denumirea în două locuri.** `public.tenants.nume` e denumirea din
  **portofoliu** — lista și bara de sus. `"<schema>".firma_profil.nume` e cea **fiscală**: pleacă în
  D100, D101, D205, D301, D390, D394, D406 și pe bilanț. Probat 27.08.2026 pe declarații generate
  într-o tranzacție întoarsă la savepoint. **Restanța rămâne deschisă** — care dintre ele e adevărul
  e decizia lui Costin —, dar partea de ecran nu așteaptă decizia: cele două se **numesc** distinct,
  iar unde diferă se spune **care pleacă pe hârtie**.

### 26.2 Cazul în care ecranul nu are amândouă valorile

Se întâmplă, și nu e o scuză să taci. Lista de firme vine din `GET /tenants`, care citește numai
`public` — denumirea fiscală nu ajunge acolo. Regula nu cere **valoarea**; cere **să nu se aleagă
tăcut**. Deci o sursă pe care ecranul n-o are se **declară lipsă**, pe nodul care o spune în limba
omului: *„pe declarații și pe bilanț pleacă denumirea fiscală, ținută separat, în «Date firmă»;
caseta asta nu o schimbă."* Ce rămâne interzis e să nu fie pomenită deloc — forma din care s-a
născut **F1**, unde caseta de alegere afirma exact invers.

### 26.3 Cum se marchează, ca să poată fi gardat

Nodul de randare își declară perechea, iar gardul citește **noduri**, nu text:

| atribut | pe ce nod | ce spune |
|---|---|---|
| `data-e1="<cheie>"` | nodul care ține perechea | „aici se arată un atribut ținut în două locuri" |
| `data-e1-sursa="<sursă>"` | nodul cu **valoarea** | din care dintre cele două locuri vine |
| `data-e1-absent="<sursă>"` | nodul care **spune** că lipsește | sursa asta nu se vede pe ecranul ăsta |
| `data-e1-efect="<sursă>"` | nodul care numește efectul | care dintre ele pleacă pe hârtie |

Cheile trăiesc în `core/scan_ecran_reguli.py::PERECHI`, cu cele două locuri scrise pe numele lor de
coloană. Gard: `core/test_reguli_ecran.py` + un bloc în `verificator_conformitate.py`.

### 26.4 Ce NU acoperă gardul, declarat

- **Nu citește textul.** Că eticheta chiar spune de unde vine valoarea e o judecată de om.
- **Nu prinde R63.** Cele două adrese trăiesc pe **două ecrane diferite**, prin chiar decizia (c) a
  restanței. Regula „același nod le arată pe amândouă" n-are ce să aserteze acolo; ce se aplică e
  partea de **nume distincte**, care nu e mecanică. Se scrie aici ca să nu pară omisiune.
- **Nu cere «când coincid, se spune și asta».** Partea aia e condiționată la rulare, iar un scan
  static nu poate deosebi ramura care se randează de cea care nu. Rămâne regulă scrisă, nepăzită.

## 27. Un act se încheie cu o CONFIRMARE VIZIBILĂ, nu cu dispariția ecranului (v2.61, 28.08.2026)

**Regula.** **Un act cu efect asupra unei entități se încheie cu o confirmare vizibilă care numește
entitatea și consecința.** Nu „Salvat": *„«BORG DESIGN SRL» a fost scoasă din portofoliu — datele ei
nu mai există."* Demontarea ecranului **nu e** confirmare: „a dispărut" arată identic cu „a reușit"
și cu „s-a rupt ceva". Cu cât actul e mai puțin reversibil, cu atât confirmarea e mai obligatorie.

**Corolar (v2.93, 19.10.2026, deficiența 418c — „După «Altă livrare», aplicația sare în fereastra firmei fără niciun mesaj de
confirmare (aceeași clasă cu 410)”):** confirmarea nu se șterge singură printr-o navigare sau o redesenare TEMPORIZATĂ
(`setTimeout(() => nav.inapoi() / randeaza…() / istoric…() / dupaEmitere(), N)`): rămâne pe ecran, iar drumul mai departe e un
buton („← Înapoi”, „Vezi factura în Istoric facturi →”); o listă care trebuie reîmprospătată se reface ACUM, iar confirmarea se pune
peste ea. Instanțele reparate: validarea / respingerea facturii primite, stornarea, emiterea, invitația asistentului, concediul
medical. Gard: verificator CONFIRMARE_TEMPORIZATA.
**Completare (v2.94, 19.10.2026, C64):** „peste ea” înseamnă în zona de mesaj a ecranului redesenat, nu în locul lui — o redesenare urmată
de `arataMesaj(corp, …)` șterge ecranul abia refăcut (la „Transformă în factură” rămânea numai „Factura … a fost emisă.”, fără drum
spre ea). Gard: verificator CONFIRMARE_PESTE_ECRAN.

### 27.1 Instanța măsurată, cu liniile ei

27.08.2026, la 19:16:24, Costin a apăsat *„Păstrez denumirea mea"*. Scrierea s-a făcut și e probată
în bază. **Ecranul n-a spus nimic.** Caseta a dispărut fiindcă `nav.acasa()` demontează ecranul, nu
fiindcă actul ar fi confirmat ceva.

Măsurat atunci în `static/js/ecrane/firme.js`: **4 din 6** acte de nivel firmă se termină fără nicio
confirmare, și sunt exact cele cu efectul cel mai mare — **alegerea de denumire** (l. 312),
**scoaterea definitivă** (l. 2465) și **cele două dezactivări** (l. 2450, l. 2493). Toate patru au
aceeași formă: `api.post`/`api.del` → `nav.acasa()` → `setFirmaInLucru("")`, fără `arataMesaj`.
Celelalte două **confirmă**: crearea (`_bannerFirmaCreata`, l. 107) și reactivarea (*„«X» e din nou
în portofoliu."*, l. 228).

**Și partea care doare:** convenția nu lipsește din fișier — e aplicată pe actul **reversibil**
(reactivarea) și lipsește pe cel **ireversibil** (scoaterea firmei). Pe calea de **eroare**, toate
patru arată un mesaj. **Ecranul știe să vorbească; tace numai când reușește.**

**Numitorul s-a corectat la măsurarea cu instrument (28.08.2026): 4 din 7, nu 4 din 6.** Numărătoarea
de atunci se uita într-un singur fișier; al șaptelea act e `PUT /tenants/{id}` din `date_firma.js`,
care **confirmă**. Cele patru tăcute sunt aceleași.

### 27.2 Ce e „act de nivel firmă", și de ce se declară

Nu se poate citi din forma căii: `/tenants/{id}/activare` și `/tenants/{id}/vector` arată identic,
iar al doilea e o **dată** a firmei, nu firma. Deci domeniul se **declară**, în
`core/scan_ecran_reguli.py::ACTE_DE_FIRMA`: creare, redenumire, scoatere, (de)activare, alegerea de
denumire. Numărul actelor găsite e el însuși clichet — o rută redenumită ar goli clasa, iar cifra ar
coborî la zero arătând ca o reparație.

### 27.3 Ce NU acoperă gardul, declarat

- **Nu judecă textul.** „Salvat" trece pe mecanică. Că mesajul numește entitatea și consecința se
  citește, nu se scanează — aceeași limită pe care o declară și R82.
- **Nu se aplică în afara domeniului declarat.** Cele 95 de mutații care lovesc `/tenants/*` în tot
  frontendul **nu** sunt în clasă; a le trata la fel ar fi confundat un act asupra firmei cu unul
  asupra datelor din ea.


### 27.4 Corolarul redenumirii: o scriere pe denumirea unei firme e SIMETRICĂ (28.08.2026)

Regula de mai sus cere ca actul să se **încheie** vizibil. Corolarul ei, dat de decizia R81, cere ca
actul să fie **întreg**: *orice act care redenumește o firmă scrie denumirea în amândouă locurile —
`public.tenants.nume` și `{schema}.firma_profil.nume` — în aceeași tranzacție, cu aceeași valoare.*

**De ce stă lângă regula confirmării, și nu numai lângă cap.26.** Cele două sunt aceeași grijă
văzută din capete diferite: acolo, ecranul tace după ce actul a reușit; aici, actul reușește **pe
jumătate** și ecranul n-are cum să spună care jumătate. Un act care atinge un singur loc din două
produce o confirmare care e adevărată și înșelătoare în același timp — *„am schimbat denumirea"*,
când pe declarație pleacă mai departe cealaltă. Instanța, probată pe viu: alegerea *„Ia denumirea de
la ANAF"*, apăsată pe 27.08.2026 la 19:16, schimba eticheta din listă și lăsa neatinsă denumirea de
pe D100, D205 și bilanț.

**Gardul e O4** — `core/scan_simetrie_denumire.py` + `core/test_simetrie_denumire.py`: o funcție care
scrie `nume` pe una din cele două tabele și nu pe cealaltă **pică poarta**. Se citește din AST, nu din
text, și prinde și `SET`-urile asamblate la rulare, unde niciun literal nu conține cuvântul `nume`.

**Limita, scrisă aici fiindcă e a regulii, nu a gardului:** simetria e o proprietate a **codului
aplicației**. Un semănător, un import sau un `UPDATE` de mână nu trec prin scriitorul unic — și chiar
așa s-au născut cele patru divergențe migrate pe 28.08. De-aia clichetul pe **date** rămâne, deși
invariantul îl face structural imposibil: *un invariant nu se crede pe cuvânt, se măsoară.*

## 28. Clasificare per-linie pe un ecran de validare a documentelor importate (v2.63, 19.09.2026)

Un ecran de **validare a unui document importat** (linii venite din e-Factura SPV, read-only) poate cere
o **decizie fiscală per linie** înainte de validare — de pildă destinația TVA a fiecărei achiziții
(taxabilă / scutită / mixtă), de care depinde pro-rata (art. 300 alin. (5)). Regula:

1. **Controlul de clasificare e un `<select class="camp-input">` la finalul rândului liniei** — nu un
   input liber, fiindcă valorile sunt un set închis. Poartă `aria-label`, iar deasupra listei de linii
   stă un `.camp-ajutor` (cap.6) care spune criteriul fiscal și consecința fiecărei valori.
2. **Un default sigur, explicit** — valoarea cea mai frecventă și fără efect advers (aici `taxabil`:
   deducere integrală, nu intră în pro-rata). Default-ul e `selected` în markup, nu tăcut. (v2.79: e preselecția PERMISĂ din
   cap.17 — cazul uzual, vizibil pe fiecare linie, schimbabil; cele două capitole spun același lucru.)
3. **Restul liniei rămâne read-only.** Faptul importat (descriere, cantitate, preț, cotă) **nu se
   editează** — se afișează, iar lângă el se **adaugă** o decizie. Distincția e normativă:
   **a CLASIFICA** (a adăuga o decizie proprie peste un fapt importat) **≠ a EDITA** (a schimba faptul
   importat, care ar rupe corespondența cu XML-ul oficial din SPV).
4. **Ordinea contează și e sursa unică.** Selectele `.camp-input` de clasificare se trimit ca listă în
   **ordinea liniilor** (`destinatii[i]` ↔ linia `i`), iar backendul le aplică pe linii **în aceeași
   ordine** (`ORDER BY id`), fiindcă liniile se inserează din XML în ordine. Fără o a doua funcție de
   potrivire pe frontend.

**De ce un capitol propriu, distinct de cap.24 (rânduri dinamice):** acolo utilizatorul **adaugă/șterge**
rânduri pe care le compune el; aici lista e **importată și fixă** — utilizatorul nu o schimbă, doar o
clasifică. Instanța: A12b — destinația TVA per linie pe `facturi_ecran.primitaDetaliu`. Gard:
`verificator_conformitate.py` (un `<select>` cu `destinatie` în markup trebuie să poarte `.camp-input`).

## Changelog
**v2.103 (24.10.2026)** — lotul 12, comanda Costin 12.3 pct.4: **cap.9 — „Antetul documentului pe ecranul scund”** (C164: pe ecranul mai
scund de 700 px sau îngust ca un telefon, detaliul facturii are sus un rând — numărul, clientul, totalul, starea SPV — iar butoanele și
zonele lor de rezultat stau în bara lipită jos; pragul numai în `stil.css`, `--antet-scund`). Gărzi: verificator `ANTET_SCUND`;
`core/test_lot12_fe3_ecrane.py`, `core/test_lot12_fe3_verificator.py`.

**v2.102 (24.10.2026)** — lotul 12, comanda Costin 12.2: **cap.9 — „Tabelul de note”** (617 / 622: o componentă, `ecrane/tabel_note.js`, pentru
Registrul jurnal și „De validat”; un rând pe notă, detaliul la clic, explicațiile o dată, căutare și filtru de stare; „De validat” în trei
secțiuni cu număr), **„Rezumatul nu mănâncă tabelul”** (621: casetele sub rezumat sau pliate, rezumatul strâns, ≤ un sfert din fereastră la
1280×720; butonul spre import sub caseta rulajelor), **„După o acțiune pe un rând, fereastra rămâne pe loc”** (617). **Cap.5** — întrebarea de
confirmare `.caseta-intrebare` (446.1). **Cap.6** — câmpul cu buton (642) și datele aduse de la ANAF legate de CUI (459.1). **Cap.22 §7** —
formularul de înregistrare încape (642). Gărzi: verificator `REZUMAT_CASETA`, `TABEL_NOTE`; `core/test_lot12_ui2_ecrane.py`,
`core/test_lot12_ui2_verificator.py`, `core/test_lot12_ui2_derulare.py`.

**v2.101 (22.10.2026)** — lotul 11, C88: **cap.4 — cursul valutar prin `cursValutar(v)`** (4–6 zecimale, cum îl dă BNR, pe unitate). Trei formatări locale cu `minimumFractionDigits: 4` (emitere, facturi, reevaluare) înlocuite. Gard: `CURS_FORMAT_LOCAL` (verificator) + `core/test_lot11_c88_curs_precizie.py::test_garda_cursul_se_afiseaza_numai_prin_cursvalutar`.

**v2.100 (22.10.2026)** — lotul 11, decizia Costin 10.3 (verbatim în DECIZII „Comanda 10.3” pct.4: „Totalurile și rezumatul fix,
mesajele lângă buton, 394 la 1280×720: da, reorganizezi ecranele; totul încape într-un ecran, fără derulare.”): **cap.9 pct.5** — cele trei
excepții „de decis de Costin” decise: Stocuri (luna, „Descarcă gestiunea lunii” și `#s-mesaj` deasupra situației, în rezumat), Tipare
(„Generează analiză AI” în rezumat, rezultatul sub el), Înregistrare (`#ins-cereri-msg` = rezumatul tabelului cererilor); Registru jurnal
are rezumat (luna, butoanele, `#j-mesaj`). **Cap.9 pct.7** — totalurile rămân în vedere: rândul de total e `<tfoot>`, lipit jos deasupra
barei (`--bara-h`, pus de navigator), iar caseta `.fd-totaluri` stă în `.bara-fixa`, pe un rând. **Cap.9 pct.8** — mesajul lângă butonul
care îl produce, nicio zonă de mesaj sub tabel. **Cap.9, „Lista de pași” (394)** — Migrare cabinet și „Notă nouă” fără derulare la
1280×720 („Cum se face” peste pași, rândul pașilor de 28 px, nota pe un rând). Gărzi: verificator `TOTAL_NEFIXAT`, `MESAJ_SUB_TABEL`;
`core/test_lot11_w4_ecrane.py`; e2e `frontend_test/e2e/e2e_lot11_w4.py`. **Cap.6 (440, g2)** — casetele textului serverului păstrează
rândurile refuzului: regula comună `pre-line` pe clasele cu un singur conținut, `.pe-randuri` pe caseta refuzului din clasele de proză.
Gărzi: verificator `MESAJ_PE_RANDURI` (clasele noi), `core/test_lot11_g2_pre_line.py`.
**v2.99 (21.10.2026)** — lotul 11, regulile transversale ale comenzii Costin 11.1 (pct.16, 17, 19, 21, verbatim în DECIZII „Comanda 11.1”):
**cap.6** — **toate erorile deodată, fiecare cu textul ei, în casetă și lângă câmp** (440: caseta „NU s-a salvat.” cu textele, fără
„motivul e mai sus”; `aria-describedby`; `arataRefuzul` și marcarea automată a câmpurilor din refuzul serverului; `cereCompletate`) — înlocuiește
trimiterea din v2.89 / v2.93; **câmpul de dată opțional se poate goli** (441: „×” + Delete, `dataGolibila`). **Cap.4** — **seria și numărul,
separat** (443: „F6 nr. 1”, `numarCuSerie` / `pdf_util.serie_nr`; `numar_cu_serie` numai pentru identificatorul trimis la ANAF; termenul
spune al cui e). **Cap.9** — **fereastra deschisă dintr-un refuz întoarce la formular** (445: `nav.dinRefuz`, formularul păstrat oricum,
„← Înapoi la <formular>”, X întoarce). Gărzi: verificator `ERORI_TOATE`, `DATA_GOLIBILA`, `SERIE_LIPITA`, `INTOARCERE_DIN_REFUZ`;
`core/test_lot11_u0_erori.py`, `core/test_lot11_u0_data.py`, `core/test_lot11_u0_serie_nr.py`, `core/test_lot11_u0_intoarcere.py`,
`core/test_lot11_u0_verificator.py`.
**v2.98 (21.10.2026)** — lotul 11 (comanda Costin 11.1 pct.1 și pct.23; deciziile 10.3 „8c: reparația centrală, cu DS cap. 6 actualizat.” și
„422 […] se repară.”): **cap.6** — **după generarea unei note**, un singur drum (`api.dupaGenerare`): confirmarea verde (`.caseta-ok`), cu
conturile și sumele notei, butonul de generare inactiv cu motivul („Nota e generată — o vezi în Registru jurnal.”), reactivat numai de o
schimbare a datelor; starea la deschidere („Generează amortizarea” inactiv pe luna cu nota validată, „Regenerează” pe ciornă, a doua
generare cu aceleași sume refuzată de server). Trecute pe helper: Raport Z (și importul AMEF), amortizarea lunii (Registru jurnal) și cea
restantă (Închidere lună), inventarul (formularul și inventarul pe mobil), descărcarea gestiunii (Stocuri și după Z), nota salariilor,
Operațiunile („Generează nota”, reactivat la o modificare a câmpurilor) și borderoul de achiziție (ecranul lui, 450); reevaluarea în
valută, compensarea și casarea / reevaluarea mijlocului fix — patch-uri în raportul subagentului J. **Cap.6** —
**contoarele și clopoțelul urmează acțiunile** (422, clasa 286): semnalul `iconta:schimbare` poartă căile scrise, iar coaja recitește
insigna și lista clopoțelului; schimbările colegilor, din contorul notificărilor (60 s / întoarcerea în filă); scrierea cu `fetch` direct
din ecrane, interzisă. **Cap.14** — **titlurile se scriu cu diacritice**, fără cuvinte din cod în textele pentru contabil. Gărzi:
verificator `DUPA_GENERARE`, `TITLU_FARA_DIACRITICE`; `core/test_lot11_j_dupa_generare.py`, `core/test_lot11_j_contoare.py`,
`core/test_lot11_j_verificator.py`.
**v2.97 (21.10.2026)** — lotul 10 (comanda Costin 10.1 pct.5, deficiențele 421 și 424 — clasa, toată aplicația): **cap.9** — **rezumatul
lipit sus e obligatoriu pe orice ecran care desenează un tabel în fereastră** (`.rezumat-fix`: perioada, filtrele, cifrele, antetul
documentului, zona de mesaj — blocul care stătea deja deasupra tabelului, fără mutări); pus pe 12 ecrane (Activitate cabinet, Invitații
cabinete, Capacitate, Declarații pasul 2, Cartea mare, Jurnal regim marjă, Registrul de evidență fiscală, Registre art. 321, Bilanț, NIR,
Rapoarte comerciale, nota de validat); lista-tabel `.mig-sold-tabel` fără derulare proprie în fereastra cu tabel. Excepții cu motiv:
formularele (Date firmă, Operațiuni) și trei ecrane de decis de Costin (Tipare, Înregistrare, Stocuri). **Cap.9 pct.6** — acțiunea care scrie
lipită jos și în zonele ferestrei cu tabel (Adaugă ajustarea, Înscrie în registru PF, Salvează coloana „An precedent”, contarea statului
de plată). Gard: verificator `REZUMAT_TABEL_LIPSA` (+ `FEREASTRA_TABEL` pentru lista-tabel), `ACTIUNE_TABEL_NEFIXATA` lărgită la zone;
`core/test_lot10_rezumat_fix.py`.
**v2.96 (20.10.2026)** — lotul 10 (comanda Costin 10.1 pct.5, deficiențele 421 și 424, verbatim în DECIZII): **cap.9** — **fereastra cu
tabel**: aproape tot ecranul (lățime și înălțime fixe), pusă de navigator pe orice fereastră care conține un tabel; un singur element
derulează (corpul), niciodată lateral; tabelul se strânge în trepte cât să încapă (`fer-strans`, `fer-rupt`); rezumatul lipit sus
(`.rezumat-fix`, nou) și acțiunea principală lipită jos (`.bara-fixa`); fără cutii cu derulare proprie (`.mig-prev-cutie`, stilul inline).
Gărzi: verificator `FEREASTRA_TABEL`, `DERULARE_INLINE`, `ACTIUNE_TABEL_NEFIXATA`; `core/test_lot10_fereastra_tabel.py`; e2e 421 / 424.
**v2.95 (19.10.2026)** — închiderea lotului 9 (deciziile Costin, verbatim în DECIZII „Închiderea lotului 9”): **cap.5** — „Pleacă marfa acum?”
o singură implementare (C63); **cap.6** — nota internă la partidă simplă (368); **cap.9** — lista de pași care încape: „Cum se face” pliat și
rândul compact de la lățimea desktop (394).
**v2.94 (19.10.2026)** — lotul 9 (C64, găsită de Code): **cap.27** — confirmarea după o redesenare stă în zona de mesaj a ecranului
refăcut, nu în locul lui (gard CONFIRMARE_PESTE_ECRAN).
**v2.93 (19.10.2026)** — lotul 9 (comanda Costin 9.2, verbatim în DECIZII): **cap.6** — **„NU s-a salvat” lângă butonul apăsat**, cu
lista câmpurilor refuzate și trimitere la fiecare (`api.refuzSalvare`, `.refuz-salvare`; 410). **cap.9** — lățirea automată privește și
`.mig-prev-cutie` (349, comanda 9.1).
**v2.92 (16.10.2026)** — lotul 6 (comanda Costin 16.10.2026 și completările, verbatim în DECIZII): **cap.6** — **câmpul care se citește, nu se scrie** (`.camp-input[readonly]` global, `.camp > button`; 272), **refuzul de pe rând sub textul rândului** (`api.refuzPeRand`; 279, clasa 259), **acțiunea principală și mesajul ei se văd mereu** (`.bara-fixa`; 285), **eroarea dispare când câmpul e corectat** (`api.stergeEroriDupaCorectare`; 290). **cap.9** — **nicio fereastră cu derulare laterală** (lățirea automată `navigator._lateste`, rândurile de butoane rupte; 285).
**v2.91 (14.10.2026)** — importul din SAGA (comanda Costin 14.10.2026, verbatim în DECIZII): **cap.4** — **caseta de date cu derulare proprie e focusabilă** (`.mig-sold-tabel`, 7 tabele; axe mobil pe previzualizarea istoricului); gard `core/test_fereastra_focusabila.py`. **cap.6** — **previzualizarea importului cu rânduri care nu intră**: caseta cu rândurile refuzate, butonul care numește ce salvează, mesajul de după salvare rând cu rând; gard e2e C24 / C25 (`frontend_test/e2e/e2e_import_saga.py`). Plus: data balanței = câmp obligatoriu (`.oblig`, `.camp-ajutor`, eroare lângă câmp — C22); coloana „Metodă” a previzualizării MF #c0492b -> #a83d22 (4,46 -> 5,63:1 pe rândul cu avertisment).
**v2.90 (13.10.2026)** — comanda Costin pct.2c: **cap.22** — **`.ghid-actualizat`**, data ultimei actualizări sub titlul fiecărui ghid (fără autori, fără titluri profesionale). Gard: verificator GHID_ACTUALIZAT, `core/test_ghid_publicare.py`. Plus **contrastul paginilor publice** (axe pe /ghid, găsit la proba vizuală a lotului): `--p-brand` #0672FE -> #0566EA (alb pe el 4,33 -> 5,13) și linkurile din pagină subliniate (`--p-link` față de text = 2,7:1, WCAG 1.4.1). Gard: `core/test_a11y_contrast_tokens.py::test_paginile_publice_contrast`.
**v2.89 (12.10.2026)** — retestul Costin de seară: **cap.6** — **un mesaj, o singură dată; o listă, rând cu rând** (deficiențele 237, 238): nota de lângă butoanele Bilanțului trimite la refuzul de dedesubt în loc să-l repete; zonele de mesaj păstrează rândurile (`white-space: pre-line`), iar refuzul soldurilor fără loc în bilanț are un rând pe cont. Gard: verificator MESAJ_PE_RANDURI, e2e 237 / 238.

- Eroare de câmp/formular: `<span class="msg-eroare">` (roșu), lângă câmpul/butonul relevant. Niciodată tăcere la o acțiune eșuată.
- **Un mesaj, o singură dată; o listă, rând cu rând (v2.89, retestul Costin 12.10.2026, deficiențele 237, 238):** același mesaj nu apare
  de două ori pe ecran — o notă de lângă butoane care ar repeta refuzul de dedesubt trimite la el („motivul e mai jos”). Un mesaj cu mai
  multe elemente (un rând pe cont, cu suma și acțiunea) vine cu rândurile despărțite (`\n`), iar zonele de mesaj (`.msg-eroare`,
  `.msg-avert`, `.msg-info`, `.msg-ok`) le păstrează (`white-space: pre-line`). Gard: verificator MESAJ_PE_RANDURI + e2e 237 / 238.
 — retestul Costin: **cap.8** — **cardul Control fiscal = un rând de patru buline cu numerele lor, fără text**, la înălțimea celorlalte carduri; textul numai în fereastră (224 redeschisă). **cap.8** — **eticheta stării firmei = una din cele patru stări** (226); gard `ETICHETA_PATRU_STARI`. **cap.2a** — **pagina principală are aceeași structură la ambele roluri**: banda de salut cu benzile „Recomandă” și „Suport”, apoi grila, fără meniu lateral (225, 231); gard `PAGINA_PRINCIPALA_UNA`. **cap.1** — **acțiunile bilanțului inactive până se completează coloana „An precedent”, cu motivul lângă ele** (228); gard `ACTIUNE_FARA_TIP` extins.

**v2.87 (10.10.2026)** — comanda Costin de seară: **cap.8** — **roșul semaforului fiscal = termen depășit** (deficiența 220): în Control fiscal o constatare urcă firma cel mult la galben, iar culoarea afișată a constatărilor e galbenă; gard `ROSU_DOAR_RESTANTA` + `core/test_rosu_termen_depasit.py`. **cap.8** — **cardul Control fiscal = semafor cu patru lumini** (deficiența 224, aprobat): vertical, roșu → galben → verde → gri, cu numărul de firme în fiecare stare; gard `SEMAFOR_PATRU_LUMINI`. **cap.1** — **acțiunea pe o declarație e inactivă până se alege tipul** (deficiența 222: Bilanțul avea „Validează”, „Descarcă XML” și „Trimite în coadă” active cu tipul „— alege —”); gard `ACTIUNE_FARA_TIP`. **cap.1** — **butonul dezactivat arată dezactivat**: regula `:disabled` pentru tot setul, hover numai pe butonul activ (un `.buton-secundar` dezactivat arăta activ); gard `BUTON_DEZACTIVAT`. **cap.2** — **barele aplicației au înălțime minimă** (deficiența C8: pe telefon mesajul din bara de stare acoperea „?”); gard `BARA_INALTIME_MINIMA`.

**v2.86 (09.10.2026)** — lotul „Retestul plasei”: **cap.9** — **focusul nu mută ecranul** (deficiența 159): un câmp deschis sub
un rând primește focusul prin `api.focusFaraSalt` — fără derulare, apoi zona se mișcă doar cât să se vadă câmpul (`nearest`); la
`<input type="date">` Chromium ignoră `preventScroll`, deci derularea strămoșilor se ține minte și se reface. Gard: `FOCUS_CU_SALT`
+ `core/test_focus_fara_salt.py`. **cap.9** — **într-un tabel, pe un rând stau cifrele, nu antetele** (deficiența 162): antetul unei
coloane numerice și nota de sub cifră (`.tip-desc`) se rup pe rânduri; la 1700 px Mijloace fixe nu mai derulează lateral. Gard:
`ANTET_NUMERIC_NOWRAP`. **cap.9** — **fereastra de scris (povestea lunii) are înălțimea ecranului** (deficiența 208): `.pacm`
`height: calc(100vh - 64px)`, lățime de document (până la 1100 px), o singură regulă. Gard: `FEREASTRA_SCRIS`.
**v2.85 (09.10.2026)** — lotul „Retest 2”: **cap.4** — perioadele în trei forme (`LL/AAAA`, `T3/2026`, `2026`); textul de pe ecran
judecat pe ecran (`core/limba_ecran.py` + `text_ecran_scan.py`, artefact păzit de `core/test_text_ecran.py`); rândul de declarație
numit cu rândul formularului (D300, D101), diferențele de reconciliere prin `pdf_util.diferenta`; marcajul `# invariant-intern-ok:`
pentru excepțiile care nu ajung la contabil. **cap.18** — ecranul „Plan de conturi” (decizia Costin O12).
**v2.84 (08.10.2026)** — lotul „Retest 08.10”: **cap.9** — în fereastra largă (corp = coloană flex) niciun copil direct nu se strânge
sub conținutul lui; se strâng (și derulează ele) numai zonele declarate (`.mig-sold-tabel`, `.rap-split`, `.pac-text`); `.dec-xml` nu
mai crește și nu mai e strivit (D406/D394: tabelul „Din ce e făcută” curgea peste „Vezi XML-ul generat”, subsol și „Trimite în coadă”;
goluri mari între secțiuni). Gard: `FER_LARG_STRIVIT`. **cap.7** — antetul unui raport contabil PDF: firma · CUI · momentul generării
(`documente_api.antet_raport`). **Textul afișat** (cap.0, „diacritice complete”, extins): nici identificatori de cod (`modul.atribut`,
`nume_cu_underscore`, `COD_CU_UNDERSCORE`, `False/None`), nici majuscule de accent („ATENTIE”, „NU”) — gard `core/test_text_afisat_limbaj.py`
pe textul serverului (inclusiv argumentele cu nume, atribuirile și `avertismente.append`) și pe ecranele JS. Antetele de tabel scrise
cu majuscule devin `text-transform: uppercase` în CSS (`.ac-cap`), textul rămâne normal.
**v2.83 (08.10.2026)** — lotul „Retest 08.10”: **cap.9** — acțiunile unui rând de tabel (trei sau mai multe butoane) stau într-un
`<details class="dec-xml">` „Acțiuni”, nu libere pe rând (Mijloace fixe la ~1700 px derula lateral, acțiunile ieșeau din vedere, PIF-ul
se rupea); lunile neînregistrate se strâng în intervale. Gard: `ACTIUNI_RAND_LIBERE`.
**v2.82 (08.10.2026)** — lotul „Deciziile 08.10”, completările: **cap.6** — mesajul pus pe un container cu câmpuri merge într-un copil
propriu (`.msg-in-formular`), nu le șterge (`api.js::arataMesaj`, mecanismul unic; gard `core/test_mesaj_in_formular.py`). Ecrane noi pe
reguli existente, fără regulă nouă: balanța cu cinci egalități (cap.9 `fer-tabel`), grupul „Înainte de preluare” și formularul în-ecran
„depusă în afara iConta” (cap.5 input în-ecran, cap.20 renderer unic), registrul MF, cardul „Închidere lună” (cap.18). **cap.15** —
textul verde pe rândul zebră al tabelelor ia `--verde-inchis` (redefinire de token în regula zebrei): #1d7a4d dădea 4,13:1.

**v2.81 (08.10.2026)** — lotul „Deciziile 08.10”: **cap.1** — butonul declanșator cu elemente nu se mai rescrie în timpul scrierii
(regula de mai sus). **cap.5 / cap.17, o instanță nouă a regulilor existente:** alegerea NIR-ului la contarea facturii primite
(`ecrane/nir_legare.js`) e o `.caseta-poarta` cu două alegeri care merg amândouă înainte („Leagă de NIR-ul ales” / „Altă livrare —
nu e niciunul”) și un select preselectat cu propunerea DEDUSĂ (același furnizor, același cost), vizibilă și schimbabilă — fără
propunere, „— alege —”. Clopoțelul arată și „rezolvată: elementul nu mai există” (notificarea de acțiune al cărei element a dispărut).
**cap.15** — linkul de acțiune pe rândul zebră ia albastrul închis (#1a5a94): #2f6fa6 dădea 4,13:1 pe `--albastru-clar`.
**cap.9** — `.fer-tabel`: fereastra cu tabele se lățește după conținut, până la marginea ecranului (Balanță, Mijloace fixe, Declarații).
**v2.80 (08.10.2026)** — **cap.15: `--gri-clar` nu e culoare de text** (lotul „Deciziile 07.10”, găsit de axe pe clopoțel): 3,14:1 pe alb;
textul secundar e `--gri`. Nouă locuri reparate (stil.css 7, admin_sanatate.js, facturi_ecran.js); `CULOARE_SEMAFOR_TEXT` din
verificator acoperă și `--gri-clar` (excepție `::placeholder`). Plus, din același lot: clopoțelul arată notificarea **rezolvată**
(„rezolvată: validată / respinsă / înlocuită”, pe rândul orei) și nu o mai numără.
**v2.79 (07.10.2026)** — **cap.17/cap.28: regula preselecției corectată** (comanda Costin, lotul 07.10 B A): permisă când valoarea e
uzuală sau dedusă, vizibilă și schimbabilă; interzisă pentru faptul situațional. Emiterea revine la RON / țara dedusă din CUI /
operațiunea normală / factura, vizibil; conturile din Operațiuni precompletate cu sugestia; 13 căsuțe DA/NU situaționale devin
`selectDaNu`; D204 forma de organizare și D208 modalitatea de transfer (trimise tacit „1”, fără câmp) intră în formular; D216 cota
de deținere nu mai vine „0.3”; D318 moneda nu mai vine „EUR”; D398 moneda e fixă (EUR, prin lege). Conflictul cap.28 pct.2 / cap.17
închis. Gard: `FAPT_FISCAL_NECERUT` extins (`PRESELECTAT_PERMIS`, `CASUTE`, `INPUTURI`, `danu_necerute`, `CONT_PRECOMPLETAT`).

**v2.78 (07.10.2026)** — **cap.17: FAPT_FISCAL_NECERUT extins la ecranele scrise de mână** (comanda Costin, „clasificarea celor 82”):
59 de selecturi fiscale pornesc cu „— alege —” și sunt cerute la trimitere (`ALEGE`, `alegeDacaLipseste`, `cereAlegerile` în `api.js`);
23 clasificate cu motiv. Conflict deschis cu cap.28 pct.2 (destinația TVA pe linie).

**v2.77 (07.10.2026)** — **cap.17: FAPT_FISCAL_NECERUT** (comanda Costin, „Cele 33 de chei”): cheia fiscală citită de server se cere
explicit în formular, fără preselecție; cea tehnică rămâne în afara ecranului, cu motiv. 31 din 33 de chei intrate în Operațiuni;
36 de selecturi obligatorii nu mai vin preselectate (regula e a motorului); câmpurile opționale cu implicit tacit devin obligatorii.
Verificator `FAPT_FISCAL_NECERUT`.

**v2.76 (07.10.2026)** — **cap.24: entitatea se alege din listă, nu prin ID; trimiterea în coadă are un singur drum.** „Mijlocul fix” (reevaluare, casare) = listă din registrul activelor; `coada_trimite.js` (`trimiteInCoada`) folosit de Declarații și Bilanț — corpul generării, refuzul real, confirmarea atenționărilor DUK (C3). Gărzi: `ID_INTERN_TASTABIL`, `COADA_UN_SINGUR_DRUM`.
**v2.75 (06.10.2026)** — **cap.24: prețul și articolul pe care nu le-a ales omul (comanda Costin 06.10.2026, pct.1b/1c).** Rândul nou fără preț și fără articol; propunerea (preț din nomenclator, UM din articol) se golește când denumirea se schimbă; denumirea scrisă de mână dezleagă articolul; prețul golit = lipsă (`null`), refuzată de server lângă câmp. Aplicat: emiterea, factura recurentă, intrarea în stoc, rețeta (ingredientul nou și prețul), transferul și reclasificarea (opțiunea goală), nomenclatorul de produse. Gard: `PRET_SAU_ARTICOL_NEALES`.
**v2.74 (06.10.2026)** — **Lotul 07.10 (retestul F5/F1): cap.2 ascuns = invizibil; cap.6 mesajul de după un buton în vedere și refuzul cu buton spre ecran.** `[hidden]{display:none!important}` global (înlocuiește excepțiile `.acces-overlay[hidden]`, `.pa-lista[hidden]`); `aduInVedere` + `SELECTOR_MESAJ` în `api.js`; `ecran_destinatie.js` (`ECRANE`, `butonSpreEcran`) + `_butonSpreEcran` în `api.js`. Clase noi: `.val-evidentiat` (elementul deschis dintr-o notificare), `.df-jurnal` / `.df-jurnal-cadru` (istoricul Date firmă încape în fereastră), `.em-ciorna` (anunțul facturii păstrate), `.ecran-destinatie`. Gărzi: `HIDDEN_CU_DISPLAY`, `MESAJ_FARA_ADUCERE_IN_VEDERE`, `REFUZ_ECRAN_FARA_BUTON`.

**v2.73 (06.10.2026)** — **Coada de validare poartă și NOTE; contrast pe „De validat” și Activitate cabinet.** Comanda Costin (răspunsul la §6 din LOT_06_10, pct.1): ecranul „De validat” are secțiunea „Note de validat” (`.val-card`, `.cf-grup-titlu`, butoanele `.val-aproba` / `.val-respinge` — ZERO clase noi), „Vezi nota” deschide liniile (`.fd-tabel`); Registrul-jurnal arată nota respinsă cu `.caseta-atentie` (motivul) și butonul „Trimite din nou la validare”; statul de plată spune unde e nota. Activitate cabinet: coloana „DECLARAȚIE / NOTĂ”, eticheta vine de la server. **Contrast (axe):** `.val-aproba` #1d9e75 sub alb = 3,39:1 -> `var(--verde)`; `.ac-cap` #8a8f98 = 3,3:1 -> `var(--gri)`. Gard: `core/test_a11y_contrast_tokens.py::test_validare_si_activitate_contrast`.

**v2.72 (06.10.2026)** — **cap.22: navigarea ghidurilor pe teme** (`.ghid-teme`, `.ghid-lista`, `.ghid-legaturi`, `.ghid-tema`, `.ghid-numar`). Comanda Costin, lotul 06.10 partea 2: `/ghid` avea 2,3 MB și 6.559 de linkuri; acum e cuprinsul celor 16 teme, fiecare temă cu pagina ei, iar fiecare ghid duce la tema lui și la ghidurile înrudite. Gard: `core/test_lot0610_p2.py`.

**v2.71 (05.10.2026)** — **cap.18: grupuri în fereastra firmei, dintr-o singură sursă.** Comanda Costin (pct.11): cele 32 de carduri sub cinci titluri (Zilnic · Registre · Raportări și declarații · Operațiuni speciale · Firma), fără arbore, titlul fără card vizibil nu apare. Pe drum: cardul Produse fără culoare (cap.12), cardul Solicitări deschis inline (cap.2a). Gard: `GRUP_FIRMA`.

**v2.70 (05.10.2026)** — **cap.8: culorile de semafor nu colorează text.** Găsită de axe pe Registrul jurnal („● Ciornă”) și la Bancă („Parțial”, „Contat ✓”) la proba pasului C din comanda „fluxul de factură pe F1”. Clasa avea 16 apariții directe + 6 indirecte (e-Transport, cifrele din Capacitate și Cabinet, procentele din Sănătate, starea SPV a facturii). Gard: `CULOARE_SEMAFOR_TEXT`.

**v2.69 (05.10.2026)** — **cap.4: cantitățile prin `cantitate(v, um)`, costul unitar prin `pretUnitar(v)`.** Din testarea fluxului de factură pe F1 (comanda Costin pct.9): „stoc 110.000”, „x2.000”, „CMP 50.0000”. Clasa avea 26 de apariții în 4 ecrane (stocuri, fișa de magazie, rețete, transfer, inventar, import, linia facturii) + descrierea notei de ieșire din stoc în backend. Gard: `CANTITATE_BRUTA` (verificator).

**v2.68 (05.10.2026)** — **cap.4: o dată produsă în interfață se scrie prin `dataIso(d)`, în ora locală.** Găsită la data implicită a facturii (comanda „fluxul de factură pe F1”, pct.4); clasa avea 21 de apariții în 10 ecrane, dintre care două greșeau ziua oricând (intervalul „luna”/„an” din activitatea cabinetului, termenul UIT din e-Transport). Gard: `DATA_UTC` (verificator).

**v2.67 (05.10.2026)** — **cap.3: ce s-a tastat nu se pierde.** Din testarea fluxului de factură pe F1 (comanda Costin pct.1): tokenul expira la 24 h în mijlocul facturii, iar aplicația se redesena la logare; navigatorul redesena factura de la zero după Date firmă. Gard: `PASTRARE_FORMULAR` (verificator) + `core/test_sesiune_fara_pierdere.py`.

**v2.66 (05.10.2026)** — **cap.9 motivul acțiunilor ascunse; cap.13 cheia de iconiță existentă; cap.6 un singur control pentru alegerea firmei.** Din testarea ca asistent (2), comanda Costin pct.3, 5, 6: fereastra poveștii fără niciun buton și fără explicație; „Raportează” fără iconiță (cheia `report`, scoasă în v2.7); Pachete cu „Caută firma” + listă pentru aceeași alegere. Gărzi: `MOTIV_DREPT_ABSENT`, `ICOANA_INEXISTENTA`, `ALEGERE_FIRMA_DUBLA` (verificator).

**v2.65 (04.10.2026)** — **cap.10: mesajul de eroare de la server se escapează în HTML.** Găsit la confirmările de drepturi (comanda Costin, pct.1/2/5): 13 interpolări `${e.mesaj}` / `${err.mesaj}` neescapate în șabloane HTML (portal 7, firme 3, cabinet, facturi, Woo) — un mesaj care citează un nume tastat cu `<` devenea marcaj. Reparate toate; gard `MESAJ_SERVER_NEESCAPAT` (verificator).

**v2.64 (04.10.2026)** — **cap.9: închiderea ferestrelor informative (X în antet + Esc, mecanism unic `inchidereDialog`) și acțiunile refuzate rolului (`data-actiune` + `drepturi.js`).** Din testarea ca asistent (comanda Costin, pct.2 și pct.4): bun-venitul se închidea numai de la butonul de la capătul listei; asistentul vedea „+ Adaugă firmă”, „Import în masă” și „Scoate”. Inventar la intrare: din 9 ferestre suprapuse, 2 aveau X și Esc, una nici X nici Esc (bun-venitul), una fără X (anunțul), restul X fără Esc. Ferestrele cu câmpuri rămân deliberat doar cu X (DECIZII 04.10.2026). Gărzi: `DIALOG_FARA_INCHIDERE` (verificator) și `core/test_drepturi_ui.py`.

**v2.63 (19.09.2026)** — **cap.28 nou: clasificare per-linie pe ecran de validare a documentelor importate.** A12b: pe `facturi_ecran.primitaDetaliu` (validarea unei facturi primite din SPV), fiecare linie importată read-only primește un `<select class="camp-input">` de destinație TVA (taxabilă implicit / scutită / mixtă), trimis ca `destinatii[]` în ordinea liniilor și aplicat de backend în aceeași ordine (`repo_facturi.actualizeaza_destinatii_linii`, ORDER BY id). Doar liniile MIXTE intră în pro-rata (art. 300 alin. (5)) — închide A12 pe calea SPV. Faptul importat rămâne needitabil; se CLASIFICĂ, nu se editează. Gard verificator: un `<select>` de destinație fără `.camp-input`.

**v2.62 (28.08.2026)** — **R81 decisă: simetrie de scriere pe denumirea unei firme** (cap.27 §27.4). Orice act care redenumește o firmă scrie `public.tenants.nume` **și** `{schema}.firma_profil.nume`, în aceeași tranzacție, cu aceeași valoare; **nu se construiește alias**. Toate cele patru căi trec printr-o singură funcție, `tenant_provisioning.scrie_denumirea`, cu poarta de unicitate înăuntru. Gard: `core/scan_simetrie_denumire.py` + `core/test_simetrie_denumire.py` — o funcție care scrie într-un singur loc din două pică poarta, iar scanul prinde și `SET`-urile compuse la rulare. **Scanul a găsit a patra cale asimetrică**, nevăzută de măsurătoarea de mână: `precompleteaza_din_anaf(seteaza_nume=True)`. **Pe ecran:** textul casetei de alegere revine la formularea simplă („denumirea aplicată e cea de pe documente"), iar marcajul `data-e1` **rămâne ca gardă de regresie**, nu ca decor — un invariant e o afirmație despre codul de azi. Cele două casete de denumire din „Date firmă" se leagă: sub simetrie, salvarea trimitea două cereri care se puteau suprascrie tăcut una pe alta.

**v2.61 (28.08.2026)** — **Două reguli de ecran, scrise și gardate: E1 (cap.26) și E2 (cap.27).** **E1:** când aceeași entitate are un atribut în două locuri, ecranul nu alege tăcut — le arată pe amândouă cu etichete care spun de unde vine fiecare, iar când diferă spune **care produce efectul**; o sursă pe care ecranul n-o are se **declară lipsă**, nu se trece sub tăcere. Instanțele: R63 (două adrese ale aceleiași persoane) și R81 (denumirea din portofoliu vs. cea fiscală). **E2:** un act cu efect asupra unei entități se încheie cu o confirmare vizibilă care numește entitatea și consecința; demontarea ecranului nu e confirmare. Instanța măsurată: **4 acte de nivel firmă din 7** se termină în tăcere, iar toate patru **vorbesc pe calea de eroare**. Ambele sunt gardate pe **structură**, nu pe text: nodurile de randare se parsează din literalii de șablon (`data-e1*`), iar actele se citesc pe **blocul `try`** care le cuprinde — un `arataMesaj` din `catch` **nu** confirmă nimic, ceea ce e chiar defectul. Instrument: `core/scan_ecran_reguli.py`; gărzi: `core/test_reguli_ecran.py` (22 de teste, din care 11 de calibrare, cu mutație pe modul propriu de eșec) + bloc în `verificator_conformitate.py`. Reparat odată cu ele: **F1/F2** — caseta de alegere a denumirii spunea *„Denumirea din aplicație e cea folosită în documente"*, ceea ce e fals, iar butoanele nu spuneau ce ating.

**v2.60 (20.08.2026)** — **Indicatorul de stare nu are voie să mintă: politică ≠ aplicabilitate (audit tenant_006, cabinet 1968).** Indicatorul patru-ochi din `.subbara` afișa „Validarea în doi asistenți ✓" ori de câte ori politica era pornită, inclusiv pe un cabinet cu UN singur validator — unde enforcement-ul permitea deja auto-aprobarea. Pe același ecran, subbara zicea „validare în doi ✓" iar cardul zicea „De depus": contradicție cu sine. **Regula:** un indicator de stare afișează ce se APLICĂ (`efectiv`), nu ce s-a CONFIGURAT (`activ`); cele două se calculează într-un singur loc consumat și de backend și de UI. **Trei stări, nu două** — pornit-și-în-vigoare (bifă + `var(--verde-inchis)`), pornit-dar-suspendat (`var(--ardezie)`, FĂRĂ bifă și FĂRĂ verde — verdele e afirmația „funcționează"), oprit (absent). **„Oprit" și „suspendat" nu se spun cu același cuvânt:** textul cozii („Patru-ochi e dezactivat") îl lăsa pe patron să creadă că i s-a stins setarea; acum spune golul + cauza + ieșirea (cap.6, stare goală): „pornită, dar suspendată: ești singurul validator… reintră în vigoare de îndată ce un coleg primește dreptul de validare (cardul Asistenți)". **Trecerea graniței se anunță în DOUĂ registre:** cromul persistent (subbara = starea, o vede oricine deschide spațiul de lucru) + punctul de acțiune (dialogul „Acorzi dreptul de validare lui X?" → mesaj `ok` la salvare = momentul). Gărzi: `core/test_patru_ochi_efectiv.py` (adevărul indicatorului + o singură definiție a mulțimii de validatori + fundătura), `core/test_a11y_contrast_tokens.py` extins (ambele culori ale indicatorului ≥4,5:1 pe bara #dfe4ea; starea suspendată nu poate purta un token verde). Vezi DECIZII 20.08.2026.

**v2.59 (19.08.2026)** — **Gard anti-suprascriere-tacuta (#1 din roadmap-ul de instrumente).** Orice `INSERT ... ON CONFLICT DO UPDATE` din producție (suprascriere TACITĂ a unui rând existent) cere o justificare inline `# upsert-ok: <motiv>`, altfel pică `core/test_upsert_motivat.py`. Suprascrierea tăcută devine o alegere CONȘTIENTĂ, cu motiv scris. Grounded: bug plan_conturi (adăugarea manuală de cont făcea `DO UPDATE` și redenumea tăcit contul OMFP standard — n-avea nicio justificare). Gardul a scos **15** upsert-uri în producție (grep-ul inițial văzuse 6) — toate revizuite și confirmate legitime (chei naturale). Roadmap-ul celor 11 instrumente propuse trăiește în `INSTRUMENTE_ROADMAP.md`, păzit de `core/test_instrumente_roadmap.py` (CONSTRUIT numește fișiere care există). Vezi [[regula-scrisa-nu-e-regula-pazita]].

**v2.59 (06.09.2026)** — **Contrastul se re-verifică pe panoul ÎNCHIS, nu doar pe cel deschis; iar când singura culoare care trece e albul, distincția se mută de pe culoare.** Regula v2.43 spunea că un token AA pe alb nu e neapărat AA pe un panou colorat (#e9edf3). Măsurat azi, două instanțe o duc mai departe, amândouă pe **panouri închise**: (1) `.btn-link` #2f6fa6 pe **subbara** `--albastru-gri` #9fb1c7 = **2.43:1** — tokenul fusese verificat pe alb (5.32) și pe #e9edf3 (4.53), amândouă mai deschise decât subbara; reparat *scoped* la #1a2535 = **7.05**, tokenul de accent pe care subbara îl folosea deja. (2) `.bara-veriga-slab` #cdddf0 pe bara albastră #347ab8 = **3.28:1** — și aici **nu exista** o reparație prin culoare: calculat, nici albul pur nu trece decât la 4.54, deci orice „albastru-deschis, dar mai luminos" ar fi rămas sub prag. Distincția verigă tare / verigă slabă a trecut de pe **culoare** pe **greutate** (600 vs 400), amândouă albe. **Regula, scrisă:** înainte de a repara un contrast prin culoare, se calculează dacă *există* o culoare care trece pe fundalul ăla; dacă maximul teoretic (alb sau negru) e sub prag, reparația trebuie să fie de altă natură — greutate, mărime, fundal — nu o nuanță care arată a reparație. **Cum au fost găsite, și de ce contează:** ambele trăiau pe elemente care **nu se randaseră niciodată** în instalarea asta — banner-ul patru-ochi cere un cabinet cu doi validatori, lanțul barei 1 cere un desktop de asistent activ. *Punctul orb nu era ecranul, era contul.* Probă nouă: `frontend_test/proba_r175_arbore_asistent.py`; gard `core/test_asistent_arbore.py`. Limita rămasă: R175.

**v2.58 (19.08.2026)** — **Verificare COMPORTAMENTALĂ (ce nu e aparent) + metoda ca POARTĂ (cerut de Costin).** Pe lângă *aparent* (F6: contrast/diacritice/culori), la orice ecran atins se verifică și *comportamentul*: apeși butoanele → se strică ceva (erori JS de consolă / layout rupt)? completezi casetele cu text la limită → se trunchiază / se rupe alinierea (revărsare orizontală / element împins peste viewport)? Instrument nou `frontend_test/vizual/interactiune_scan.py` (apasă butoanele din fereastră, ne-destructive, cu re-navigare + umple casetele cu text lung+diacritice + axe **desktop ȘI mobil** + țintă<24 AA + title-only) → artefact `acoperire_vizuala.json`. **Cuplare mecanică diff→scan:** `core/test_acoperire_vizuala.py` pică dacă un fișier UI (`static/js/**.js` / `stil.css`) s-a schimbat de la ultimul scan (`ui_hash`) SAU dacă scanul a găsit vreo violare — nu poți comite o schimbare de UI fără scan proaspăt și curat (același tipar ca `versioneaza_assets` + `test_versionare_assets`). Motiv: o regulă scrisă și citită NU e o regulă păzită — doar poarta ține (ca `test_agenda`). `MODEL_AUDIT_TENANT`: F9 nou + punctul „metoda e POARTĂ, nu document". `nav_ecrane.ECRANE` extins cu `solduri_parteneri`.

**v2.57 (19.08.2026)** — **a11y: corpul modal `.fereastra-corp` focusabil din tastatură (axe `scrollable-region-focusable`, mobil).** Trecerea F6 pe Pixel 5 (audit tenant_006, strat solduri_parteneri) a scos că pe ecran îngust (393px) conținutul ferestrei se derulează dar `.fereastra-corp` nu era focusabil din tastatură (WCAG 2.1.1). Fix app-wide într-un singur shell partajat (`navigator.js`): `tabindex="0"` pe ambele `.fereastra-corp` (fereastra de lucru + modalul de anunț) → axe mobil 0 pe preview parteneri. Gard `core/test_fereastra_focusabila.py`. **LECȚIE infra:** `axe_scan.py` e desktop-only și `mobil_scan.py` NU rulează axe → combinația axe+mobil (unde conținutul depășește viewportul) prinde ce niciunul singur nu prinde; de rulat axe ȘI pe profil telefon la ecranele cu conținut lung (gap de infra notat).

**v2.56 (19.08.2026)** — **Audit tenant_006 straturi de import: no-silent-drop, no-silent-overwrite, field-marking pe grupuri de butoane + colectare multi-câmp, contrast pe panou (extindere).** (1) FIRME (migrare): intrarea care nu-i CUI (fără cifre — typo/antet) nu mai dispare TACIT înainte de ANAF — `anaf_api.separa_cui` întoarce `(curatate, ignorate)`, ecranul le arată într-un banner `.mig-avert` (ZERO clase noi, Regula 4/14.4). (2) PLAN DE CONTURI (Adaugă cont): adăugarea manuală nu mai face `INSERT ... ON CONFLICT DO UPDATE` (suprascria TACIT un cont OMFP standard, ex. „101 Capital") — refuz 409 în limba contabilului; obligativitatea marcată cu `<span class="oblig">*</span>` ÎNAINTE de buton (cap.6) + câmpul gol marcat `.camp-invalid` cu mesaj care numește CARE câmp (simbol vs denumire), ambele goale marcate odată (cap.6 pct.4). (3) VECTOR FISCAL: eroarea de câmp obligatoriu marchează GRUPUL de butoane vinovat cu `.camp-invalid` (ramura box-shadow generică a clasei prinde și un `<div>`, nu doar `input`/`select` din v2.44) prin `erori_campuri` din backend; frontendul COLECTEAZĂ client-side toate câmpurile obligatorii lipsă și le marchează pe TOATE odată, un singur mesaj „Completează: …" (cap.6 pct.4 — fail-fast INTERZIS pe formular multi-câmp; backend-ul `salveaza` rămâne plasă de siguranță). (4) CONTRAST: baza `.mig-sold-cont` → #2f6fa6 (4.53 pe #e9edf3). v2.43 reparase DOAR scoped la Control fiscal, presupunând că `.mig-sold-cont` din migrare e „pe alb" — GREȘIT: preview-urile de import (solduri/parteneri/plan) folosesc panoul #e9edf3, unde #347ab8 = 3.86 (axe pe preview parteneri). Regula v2.43 rămâne (text pe panou non-alb se re-verifică); instanța din migrare acum acoperită. Gărzi: `test_separa_cui`, `test_migrare_ignorate_vizibil`, `test_plan_conturi_no_upsert`, `test_plan_form_fieldmark`, `test_vector_camp_marcat`, `test_a11y_contrast_tokens` (extins). F6 (mobil_scan Pixel 5 + axe_scan) pe vector_fiscal + plan_conturi: axe 0, TITLE-UNIC 0, OVERFLOW-X nu, ținte de atingere ≥24 (AA; sub-44 = doar nav-chrome pre-existent, AAA).

**v2.55 (18.08.2026)** — **D177: formular manual _DOAR_API cu ANTET + LISTA, si eticheta care urmeaza tipul.** D177 (redirectionare impozit profit) combina un antet de plafoane/perioada (campuri fixe, ca panoul d311) cu o lista de beneficiari de lungime variabila (ca d107/d307) - primul formular din campanie cu AMBELE forme intr-un `<details class="dec-xml">`. Doua comportamente noi, ZERO clase noi: (1) eticheta unui camp se schimba dupa alt camp - la tip beneficiar 3 (mecenat/PF) eticheta codului fiscal devine "CNP", altfel "CUI" (se editeaza `firstChild.textContent` al `camp-eticheta`, pastrand steluta `oblig`); (2) un camp devine irelevant conditionat - contractul se ascunde (`display:none`) pentru tip 5 (UNICEF), unde nu e cerut. Validare pe camp la adaugare (IBAN RO+22, suma>0, contract la tip<5) + refuz backend pe gol, mesaj de contabil. Totalul alocat vs. suma ramasa afisat live la randare. Confirma "forma urmeaza declaratia": antet fix acolo unde declaratia are campuri unice, lista acolo unde are 1..n.
**v2.54 (18.08.2026)** — **D107: a patra declaratie _DOAR_API cu formular manual, varianta LISTA cu ANEXA colapsata.** D107 (informativa sponsorizari/mecenat/burse) e o lista de beneficiari (ca d710/d307), fiecare cu denumire/cod fiscal/adresa si trei sume (acordata/reportata/dedusa) -> formular-lista `<details class="dec-xml">` IDENTIC cu D307 (dec-man-rand + btn-link sterge + dec-man-form de adaugare). NOU fata de d307: o SUB-sectiune `<details>` colapsata pentru anexa beneficiarilor neindividualizati - un caz rar care nu trebuie sa incarce ecranul comun; mini-lista din anexa se randeaza conditionat (doar cand suma reportata a lor > 0, regula validatorului). Tiparul "forma urmeaza declaratia": partea principala e lista, iar variabilitatea rara (anexa) sta intr-un toggle secundar in loc de a fi mereu vizibila. ZERO clase noi (aceleasi dec-man-*/camp/dec-xml); totaluri pe trei coloane + control recalculate la fiecare randare (coincid cu serverul, Regula 14.2); validare pe camp (`eroareCamp`, mesaj de contabil) + refuz backend pe gol.
**v2.53 (18.08.2026)** — **D307: a treia declaratie _DOAR_API cu formular manual, varianta LISTA (ca d710).** D307 (ajustare TVA) e o lista de operatiuni de lungime variabila -> formular-lista `<details class="dec-xml">` cu grila de operatiuni (`dec-man-rand` + buton `btn-link` sterge) + mini-form de adaugare (`dec-man-form`: tip/cod/denumire/TVA + „+ adauga"), IDENTIC cu D710. Total de ajustare recalculat la fiecare randare a listei. Confirma tiparul: declaratiile-lista (d710 obligatii, d307 operatiuni) folosesc acelasi model; d311 (structura fixa) e panou-camp. ZERO clase noi; validare pe camp la adaugare (`eroareCamp`, mesaj de contabil) + refuz backend pe gol.
**v2.52 (18.08.2026)** — **D311: varianta PANOU-CAMP a formularelor manuale _DOAR_API.** Fata de d710/d307 (lista editabila de randuri), D311 are structura FIXA (schema IV): un panou `<details class="dec-xml">` cu data anularii + motiv (select) + 3 situatii oficiale (cate un rand `dec-man-rand` cu eticheta pe linie proprie + sub-rand `flex-wrap` de doua campuri baza/TVA). ACELEASI clase (zero clase noi), dar forma urmeaza declaratia - "identitatea intre situatii similare" se aplica la nivel de clase/comportament (validare pe camp, refuz pe gol, mesaj de contabil, total calculat LIVE), nu la forma listei. ATENTIE responsiv: `.dec-recl-desc { flex:1 1 220px }` intr-un rand pe COLOANA face flex-basis-ul sa devina inaltime -> suprascris `flex:0 0 auto` (prins pe profil Pixel5).
**v2.51 (18.08.2026)** — **Formulare manuale pentru declaratiile _DOAR_API (D710 primul).** Cele 41 de declaratii fara ecran (stare AMANAT, _DOAR_API in declaratii_api) capata formular de introducere manuala in ecranul Declaratii, pe modelul panoului D301: dupa alegerea tipului + perioadei, un panou `<details class="dec-xml">` cu lista editabila (`dec-man-rand` + `dec-man-form`, clase existente, ZERO clase noi) colecteaza parametrii pe care generatorul ii cere. Declaratiile cu lista de acelasi fel (obligatii D710, situatii D311, ajustari D307) arata la fel (identitate intre situatii similare, regula 0). Validare pe camp (`eroareCamp`, mesaj de contabil, nu nume intern) + refuz backend pe formular gol. D710: panou "Obligatii corectate" (cod 121 micro / 103 profit, suma initiala/corecta, cota la micro), obligatii in memorie -> body de generare (D710 nu are tabel DB).
**v2.50 (18.08.2026)** — **a11y contrast .btn-link + .dec-xml summary (axe pe grila D301).** axe-core pe ecranul D301 a gasit 2 perechi text/fundal sub 4.5:1: `.btn-link` (butoane-link sterge/confirma/anuleaza etc., app-wide) folosea #3d8fd6 = 3.44 pe alb / 2.93 pe panoul #e9edf3; `.dec-xml summary` (toggle-ul de sectiune) folosea var(--albastru) #347ab8 = 3.86 pe #e9edf3. Reparate la #2f6fa6 (4.53 pe #e9edf3, 5.32 pe alb). Inchide "RAMAS"-ul notat la v2.42 (.btn-link inca #3d8fd6 literal pe alb). Gard browser-free extins. RAMAS: axe "region"/landmarks (structural, app-wide); tintele de atingere ale butoanelor-link (18px inaltime) sunt in randul de text -> excepatia inline WCAG 2.5.8.
**v2.49 (18.08.2026)** — **Grila D301: confirmarea "nu e serviciu" persista per-furnizor.** Cand contabilul confirma o operatiune tip 4 ca "nu e serviciu IC" (v2.48), confirmarea se aplica si viitoarelor operatiuni de la ACELASI furnizor (tara+cod, orice luna) - nu re-confirma lunar acelasi furnizor de gaz/energie. Operatiunea confirmata direct arata "✓ confirmat local" (cu "anuleaza"); cea care mosteneste confirmarea furnizorului arata "✓ furnizor confirmat local". Derivat din confirmarile per-operatiune existente (fara tabel/coloana noua). Backend: lista calculeaza multimea furnizorilor confirmati (d390_confirmat_local=true) si expune d390_furnizor_confirmat.
**v2.48 (18.08.2026)** — **Grila D301: confirmarea "nu e serviciu IC" (fals-pozitiv tip 4).** Indiciul de mis-clasificare (v2.47) pe o operatiune tip 4 cu cod TVA furnizor primeste un buton "confirma (nu e serviciu)": contabilul il apasa pentru gaz/energie/bunuri (art.307 alin.3/5) de la furnizor inregistrat, care legitim nu intra in D390 desi au cod TVA -> indiciul se stinge pentru acea operatiune (afiseaza "✓ confirmat local", cu "anuleaza" reversibil). Backend: coloana d301_operatiuni.d390_confirmat_local + PUT /d301-operatiuni/{id}/confirma-local; d390_posibil_serviciu respecta confirmarea. Indiciu, nu blocaj (Regula 4).
**v2.47 (18.08.2026)** — **Grila D301: indiciu de mis-clasificare tip 4 -> tip 5.** O operatiune tip 4 (art. 307 alin.(3)(5)(6), taxare inversa locala - nu intra in D390) care are COD TVA furnizor completat primeste in grila un indiciu SOFT: "⚠ daca e serviciu intracomunitar, foloseste tip 5 (D390 cod S)". Motivul: codul de TVA exclude alin.(6) (furnizori neinregistrati), deci un serviciu IC (art. 307 alin.2) pus gresit ca tip 4 ar ramane absent din D390. Indiciu, nu blocaj (gaz/energie alin.3/5 pot avea si ele furnizor inregistrat). Backend: flag d390_posibil_serviciu = (tip==4 si partener_cod completat) in d301_operatiuni_api.lista.
**v2.46 (18.08.2026)** — **Grila D301: clarificare per-tip pentru D390 (audit tenant_006).** Fiecare operatiune D301 din grila arata acum relatia cu D390: tip 1/3/5 cu furnizor -> "→ D390 cod A/S"; tip 1/3/5 FARA tara furnizor -> "⚠ fara furnizor — nu intra in D390" (rosu); tip 2 (transport nou) / tip 4 (art. 307 alin.(3)/(5)/(6) - taxare inversa locala) -> "(nu intra in D390 — ...)" CHIAR daca au furnizor, fiindca nu sunt operatiuni intracomunitare pentru recapitulativa. Contabilul distinge omisiunea (lipsa furnizor) de excluderea intentionata (tip neintracomunitar). Temei: CF art. 307 verificat la sursa.
**v2.45 (18.08.2026)** — **Furnizorul UE pe operatiunea D301 + auto-derivare D390 (audit tenant_006, decizia Costin).** Ecranul D301 (Declaratii -> D301 -> operatiuni) capata 3 campuri OPTIONALE de furnizor: Tara furnizor (2 litere), Cod TVA furnizor (fara prefix tara), Denumire furnizor. Daca sunt completate, achizitia IC apare AUTOMAT in D390 (tip 1/3 bunuri -> cod A; tip 5 servicii -> cod S). Grila operatiunilor D301 arata un indicator per rand: "→ D390 cod A/S" (are furnizor) sau "⚠ fara furnizor — nu intra in D390" (rosu, .mig-cnp-no). Backend: coloane partener_tara/cod/den pe d301_operatiuni (migrare + template); d390.operatiuni_din_d301 (generator) + d390_reconciliere._pull_d301 (a-doua-cale independenta). Camp optional -> nu blocheaza D301; validare usoara (tara 2 litere, cod fara prefix); checksum VIES la generarea D390.
**v2.44 (18.08.2026)** — **Marcaj vizual al campului cu eroare de validare (field-level, audit tenant_006).** La salvarea unui formular cu camp obligatoriu gol/invalid, `eroareCamp` (api.js) ancora mesajul rosu langa camp DAR nu marca INPUTUL (fara contur) -> la formulare lungi nu se vedea CARE camp e problema (Regula 14 pct.4). Acum eroareCamp adauga `.camp-invalid` (+ aria-invalid), curataEroriCamp o scoate la corectare. Contur rosu #a3231c (asortat cu .msg-eroare) + glow. CAPCANA (documentata in CSS): regula globala contrast_ferestre_v1 forteaza `border ... !important` pe toate inputurile (specificitate `input:not(...)`x6 = 0,6,1) -> un `.camp-invalid` simplu (0,1,0) NU invinge; overrideul reproduce selectorul + `.camp-invalid` (0,7,1). App-wide: 7 ecrane folosesc eroareCamp (date_firma, firme, declaratii, emitere, facturi, etransport, flux_concediu). Gard `core/test_fieldmark.py` (mutatie-probat). Captura privita pe Date firma: 2 campuri goale -> contur rosu + mesaj ancorat, dispar la corectare.
**v2.43 (18.08.2026)** — **a11y contrast Control fiscal (audit tenant_006).** axe-core pe ecranul Control fiscal (neacoperit de v2.42): 17 perechi color-contrast sub 4.5 pe panoul #e9edf3, reduse la 2 tokeni: codurile declaratiilor (`.mig-sold-cont` = `--albastru` #347ab8 = 3.87) + sub-textul verdictelor (`.cf-incr-temei` = `--gri-semafor` #9aa3b2 = 2.16). REGULA (noua): un token AA pe ALB nu e neaparat AA pe un PANOU colorat (#e9edf3) — textul pe panouri non-albe se re-verifica la contrast. Fix SCOPED (token global neatins, ca `.camp-ajutor` in v2.42): `.cf-rand-decl/.cf-incr-cap .mig-sold-cont` -> #2f6fa6 (4.53 pe #e9edf3), `.cf-incr-temei` -> #5c6675 (4.95). Gard `test_a11y_contrast_tokens.py` extins (2 perechi pe #e9edf3, mutatie-probat RED). axe contrast=0 pe Control fiscal (captura privita, identitate pastrata). Ramas: axe "region" (landmark) 8-19 noduri app-wide (moderat, structural, de evaluat separat).
**v2.42 (17.08.2026)** — **a11y contrast WCAG AA (4.5:1).** axe-core (audit tenant_005) a gasit 5 perechi text/fundal sub 4.5:1. Reparate la SURSA (token/paleta, nu instanta): `--albastru` #3d8fd6->#347ab8 (alb pe el 3.44->4.54, butoane/bara); `.camp-ajutor` var(--albastru)->#2f6fa6 (2.93->4.53); `CULORI_CARD` (api.js) verde fg #16a34a->#117f39 (2.94->4.55) + teal #0a807b->#097a76 (4.18->4.53); po-indicator (cabinet.js) var(--verde)->#1b7349 (4.16->4.57). Plus: title-only pierdut pe touch reparat prin aria-label (po-indicator + nav-ghid); `.subbara-edu` tinta atingere 18px->24px (AA 2.5.8). Gard browser-free `core/test_a11y_contrast_tokens.py` (recalcul contrast din sursa, ratchet pe token). Ramas (notat): butoanele nav (30-36px) trec AA(24) dar nu AAA(44). axe contrast=0 pe dashboard/vector/salariati.
**v2.41 (17.08.2026)** — **Backlog diacritice generatoare declaratii INCHIS.** Mesajele de blocaj/avertisment ale TUTUROR generatoarelor (d100..d710 + d101g/d212_engine/d406_active/d406_stocuri/bilant_api/declaratii_api, 58 fisiere, ~840 literale) diacriticizate integral, cu unealta gard-driven (dictionar ASCII->diacritice high-precision aplicat DOAR pe literalii-mesaj: spatiu + cuvant mapat; exclus XML-tag real `<litera`, SQL prin span execute() AST, referinta de coloana alias.coloana, chei de dict/backtick). Gard test_generatoare_declaratii_cu_diacritice extins la toate 58 fisierele; ~18 fisiere de test aliniate; suita 1965 passed, verificator 0. Unealta reutilizabila in ~/probe_t005 (server) pentru extinderi viitoare.
**v2.40 (17.08.2026)** — **Front E: corectarea identitatii/contractului salariatului din UI.** Din ecranul de salariati se editau doar salariu/IBAN/COR/incetare; nume/prenume/CNP/data_angajare/norma NU se puteau corecta, desi backendul (SalariatEdit + salariati_api._CAMPURI_API) le accepta - o eroare de tastare in nume/CNP ramanea necorectabila (MEMORY §13). Buton "Corecteaza datele" in ecranSalariati (firme.js): form nume/prenume/CNP/data angajare/norma, CNP validat client-side (checksum) inainte de PUT /salariati/{id}. stat_plata expune cnp + tip_norma (part_time->text la granita). Gard core/test_front_e_editare_identitate.py (contract backend + clamp UI).
**v2.39 (17.08.2026)** — **Front D (declaratii).** D112 scutire constructii: VERIFICAT LA SURSA, NU e defect - art.60 pct.5 CF (+ art.60^1) ABROGATE de la 01-01-2025 prin OUG 156/2024 pct.7-8 art.LXIV (MO 1334/31.12.2024); in 2026 salariatul din constructii se trateaza standard. Temei adaugat in salarizare.py (nivel MO). D205: blocheaza corect pe "fara beneficiar", 17 mesaje diacriticizate + gard test_generatoare_declaratii_cu_diacritice. BACKLOG SISTEMIC: ~50 generatoare de declaratii (~330 mesaje) fara diacritice, campanie dedicata (_GEN_DECLARATII creste). Vezi GARZI.
**v2.38 (17.08.2026)** — **Plan de conturi: adaugarea de cont reparata.** `class PlanContIn` era definit la main.py:4798, DUPA handlerul care-l foloseste (main.py:1719). Cu `from __future__ import annotations` (PEP 563) adnotarea `date: PlanContIn` e string, iar `@app.post` o rezolva la IMPORT in ordinea sursei; modelul fiind mai jos, FastAPI nu-l recunostea ca model de body si trata `date` ca QUERY param -> orice adaugare de cont pica cu 422 "date required". Fix: PlanContIn mutat inainte de handler (ca VectorIn:886 fata de 2751). Gard `core/test_rute_model_body.py`: niciun param clasificat de FastAPI ca query (inghetat la import) nu are tip BaseModel (get_type_hints, dupa import, scoate misclasificarea). Audit vizual tenant_005.
**v2.37 (17.08.2026)** — **Diacritice pe mesajele validatorilor de import.** 21 mesaje AFISATE contabilului fara diacritice (solduri/parteneri/asociati/istoric/articole/salariati/retete/mijloace + generalizare e-Factura). Scapasera gardului fiindca sunt in structuri pe care _candidati() nu le vede: raise ValueError brut, det+=, f-string, avertismente.append(...). Reparate; unde mijloace scapa si numele de camp (cont_imobilizare), corectat. Gard `test_diacritice_afisate` extins: 14 triggere high-precision + `test_validatori_import_cu_diacritice` care scaneaza INTEGRAL fisierele-validator de import (integral user-facing), excluzand argumentele `_gaseste_col` (sinonime de coloana = antetul CSV al userului) si string-urile SQL. RED-probat pe avertisment. Audit tenant_005.
**v2.36 (17.08.2026)** — cap.17: **vectorul fiscal per-firma reflecta vectorul SALVAT**. Pe traseul per-firma (meniuMigrarePerFirma -> Vector fiscal) `formularVectorFirma` primea doar {tenant_id,nume,tip_firma} si aparea GOL: regim gol, `Nu` tacit la TVA (incalca DEFAULT_FISCAL_TACIT: `nesetat` != `Nu`), CUI gol -> plator TVA aparea neplator, la salvare SUPRASCRIA vectorul. Fix: incarca `GET /tenants/{id}/vector` (citeste, sursa unica). Periodicitatea legacy: seed-ul scrie coduri `L`/`T` in tip_decont (12/20 tenanti; intentionat, motoarele le accepta prin perioada_tva_tip); UI-ul compara pe forma lunga -> aparea neselectata pe Vector SI Date firma (ambele citesc /vector). Noua primitiva `core/common.tip_decont_lung` (reia perioada_tva_tip, constanta `DECONT_LUNG`, None la gol/necunoscut - fara default tacit) normalizeaza la GRANITA UI: `vector_fiscal_api.citeste` + `portal_api.date_firma`. Motoarele fiscale NEATINSE. Garduri `core/test_tip_decont_lung.py`. Audit tenant_005.
**v2.35 (17.08.2026)** — Regula 14 pct.4 (mecanizata): **niciun mesaj user-facing nu scapa numele intern de camp** (snake_case). Sweep pe core/ + main.py (mesaje prin ROL SINTACTIC, refolosind extractia din test_diacritice_afisate._candidati): 13 instante reparate (`tip_decont`/`regim_fiscal`/`firma_profil` in vector; `zi_emitere`; `cont_stoc_nou`; `tenant_id`x3/`cabinet_id`/`state_plata`/`dnf_luni` in main.py; `admin_firma` in perioada; temei `firma_profil.platitor_tva` in control_fiscal; `salariu_brut`/`cota_dividend`/`tva_la_incasare` in reconcilieri). Contabilul vede eticheta umana, nu numele coloanei. Gard `core/test_mesaje_fara_camp_intern.py` (flagheaza token snake_case in mesaj-proza; baseline 0; 2 exceptii = temei-diagnostic pe cale de bug de cod, cu motiv). Audit tenant_005.
**v2.34 (17.08.2026)** — cap.17: import articole (stoc initial) — un articol cu `cantitate > 0` dar `pret` 0/lipsa e INVALID (`articole_import_api.extrage`, motiv afisat in preview). Parserul fabrica `pret=0.0` la coloana absenta / celula goala (default fabricat, interzis cap.17); miscarea de intrare ar avea valoare 0 -> CMP porneste de la 0, valoarea stocului sub-raportata tacit. Verificarea inline respingea DOAR negativ; extinsa la `cant>0 and pret<=0`. Generalizarea Regula 13 a defectului salariu_brut (v2.32): sweep pe toti validatorii de import — restul (mijloace fixe, solduri, istoric, retete, parteneri, asociati) CURATI. Gard `test_articole_stoc_fara_pret_e_invalid`.
**v2.33 (17.08.2026)** — cap.5/6: **editarea salariului de baza** cablata + semnal **baza lipsa** pe Stat de plata. (a) Butonul „Salariu” pe cardul de salariat deschide un input in-ecran (salariu de baza + „de la” = valabil_din), cabland `PUT /salariati/{id}` {salariu_brut, valabil_din} (endpoint existent `actualizeaza_salariat`, necablat pana acum — o marire/corectie de salariu nu se putea face din UI; `SalariatEdit.valabil_din` adaugat la model). O schimbare de salariu = intrare noua in `salariu_istoric` (UPSERT pe salariat+data). Tipar in-ecran ca IBAN/Incetare (cap.5 INPUT). (b) `stat_plata` intoarce `baza_lipsa` (baza contractuala <= 0) -> cardul arata badge rosu „salariu de baza lipsa” + sub-linie explicativa (net 0, dar cost din suprataxa sub-minim; completeaza cu „Salariu”), cifrele raman vizibile dar EXPLICATE (MEMORY §13: data lipsa se semnaleaza, nu se afiseaza tacit). Gard `test_stat_plata_semnaleaza_baza_lipsa`.
**v2.32 (17.08.2026)** — cap.6/17: `salariu_brut` OBLIGATORIU si > 0 la importul de salariati (`salariati_import_api.verifica_randuri`, motiv `salariu_lipsa`), ca la creare (salariati_api #8). Coloana de salariu absenta / celula goala NU se accepta ca 0 tacit (parser `_numar` intoarce 0.0 = default fabricat, interzis cap.17): firma ar plati CAS/CASS pe podeaua sub-minim (art.146(5^6)/168(6^1)) fara sa stie, iar Stat de plata ar arata brut 0 / cost pozitiv (incoerent, MEMORY §13). Poarta unica `verifica_randuri` (ca `norma_lipsa`/`ore_invalide`/`iban_invalid`); mesaj vizibil prin `.caseta-atentie` (gateazaPreview, cap.5). Gard `core/test_import_migrare.py::test_salariu_brut_*`.
**v2.31 (08.08.2026)** — cap.24 nou: **Rânduri dinamice în formulare** — stratul de dedesubtul cap.6 (cap.6 presupune id DOM stabil ca dat; cap.24 spune de unde vine + cum se comportă o listă care crește/scade). Patru reguli: re-randare integrală la mutație (nu mutare de noduri DOM individual); id derivat din poziție + lista randată = lista validată (fără filtrare tăcută înainte de validare — un rând incomplet se raportează, nu se aruncă); orice listă care crește trebuie să scadă (add fără delete interzis); validarea per-câmp pe rânduri = backend, frontendul nu ține o a doua funcție de câmpuri-lipsă (oglinda drifteaza — dovedit `valoare_fara_tva` verificat doar în backend). Gardă **MIRROR_CAMPURI_LIPSA** în verificator (regula 4, singura curat-mecanică): interzice funcție `*campuri*lipsa*` în `static/js/ecrane`; e-Transport + emitere = excepție declarată până la batch 3 (ca lista G10-A). Regulile 1-3 rămân disciplină (un gard mecanic ar aprinde `facturi_ecran.js`/`firme.js`, ecrane în afara batch 3). NU atinge cap.6.
**v2.30 (02.08.2026)** — cap.23 nou: **Perioadă confirmată** — tipar general (starea CONFIRMAT/NECONFIRMAT a
unei perioade `(an, luna, domeniu)` condiționează calculele din aval). Motivat de pontaj (F135): payroll-ul trebuie
să știe dacă luna e autoritativă (HG 1045/2018 art.10(3) — tichete pe zile efectiv lucrate), iar prezent = fără rând
nu distinge lună completă de necompletată. Reutilizează primitive existente (buton-verde cap.1, confirmaCaseta cap.5,
semafor gri/verde cap.8, caseta-info cap.5, stare-goală cap.6) — zero pattern nou. Confirmă `admin_firma`.
Reversibilitate: de-confirmare automată înainte de depunere; blocare edit după depunere (→ rectificativă). Gardă în
verificator. Revine la închiderea lunii contabile + confirmarea inventarului.

**v2.29 (26.07.2026)** — cap.22 nou: **Pagini publice de ghid** (`/ghid/{slug}`), INAUNTRUL sistemului de design (nu scutite ca landing-ul). Ruta publica citeste `ghid/{slug}.md`, randeaza markdown -> shell care leaga `stil.css` si foloseste clase+tokeni (fara `<style>` inline, invers fata de /public/termeni); slug inexistent -> 404 curat. 5 componente noi din tokeni: `.ghid-temei` / `.ghid-exemplu` / `.ghid-semafor` / `.ghid-comparatie` / `.ghid-procedura`; semaforul grafic refoloseste `--verde`/`--galben`/`--rosu-semafor` si ordinea din cap.8 (doar marime/rol diferit, zero culori noi). Marcaj in markdown prin containere `:::nume ... :::`. Verificator extins cu regula **GHID_ZONA** (scaneaza `ghid/*.md`: hex/style/font-size/border-radius/SVG inline interzise); clasele de ghid NU sunt pe lista alba. FUNCTIONALITATI.csv: coloana noua `ghid_slug` (goala = fara pagina). Pagina de proba `proba-ghid` (umplutura, se sterge la prima pagina reala).
**v2.28 (26.07.2026)** — cap.21 nou: marca **„iConta.eu" peste tot** în material public (MARKETING.md cap. BRAND). Gardă **BRAND_EU** în verificator: scanează frontend (`js/mjs/html`) + literalele de email din backend (`main.py`, `notificari_scadenta`, `observare`), semnalează `iConta` neurmat de `.eu`; al doilea assert `iConta.eu.eu`=0. Excepții documentate (listă albă cu motiv): „Admin iConta" (nume panou), `<SoftwareCompanyName>`/`<SoftwareID>` SAF-T (fiscal), comentarii/docstring, `iconta_nou`/`iconta-nou`/`iconta_v2`. Normalizate 21 literale backend rămase (welcome/magic-link/portal/asistent/recomandare + alerte interne + titlu API).
**v2.27 (24.07.2026)** — cap.10 extins a treia formă: `ESC_LOCAL` prinde și **strip inline** de caractere HTML (`.replace(/[<>&]/g, …)`) — sanitizare ad-hoc, data-lossy (scoate `&` din nume), a doua sursă de sanitizare. Convertite 6 apariții → `esc` canonic (tipare.js ×2, capacitate.js ×1, cabinet.js ×3; recomanda.js reparat separat). Regex robust la reordonarea clasei (prinde orice clasă ce conține `<>&`).
**v2.26 (24.07.2026)** — cap.10 extins (SECURITATE): `esc` se importă din api.js, nu se redefinește local. `ESC_LOCAL` prinde acum și **redefinirea locală** a lui `esc` (`function esc`/`const|let|var esc =`), nu doar variantele `_esc`/`escB`/… Cauză: `setari.js` avea un `esc` local care escapa DOAR `"` → XSS pe `<>` în conținut de element (numele cheii API, user-controlled, la randare). Reparate 5 ecrane care redefineau `esc` local (setari — slab; rip/operatiuni/pachete/etransport — escapau `&<>"`, dar tot copii divergente fără `'`) → toate importă acum `esc` canonic (`&<>"'`). api.js (sursa) e în static/js/, nescanat de gardă → fără auto-flag.
**v2.25 (24.07.2026)** — cap.20 extins: paritatea de randare acoperă și al doilea consumator care alege chei vc pe nume — `ecranVerificari` (firme.js, endpoint `/firme/{id}/verificari`). Inventar declarat `VC_VERIFICARI` (randat / IGNORAT-cu-motiv); cross-check-urile (`tva_incrucisat`/`d112_incrucisat`/`d390_incrucisat`/`cota_tva_conformitate`) declarate ignorate — aparțin exclusiv verdictului din Control fiscal. Fără randare nouă pe ecran (nimic nu se schimbă vizual), doar declarație + gardă. `VERDICT_PARITATE` verifică acum ambele inventare vs cheile produse.
**v2.24 (24.07.2026)** — cap.20 nou: verdictul de control fiscal are un renderer UNIC (`control_verdict.js`), consumat de detaliu (`control.js`) și de cardul din fișă (`firme.js`) — înainte, trei renderere divergente cu subseturi hardcodate de chei ascundeau constatări blocante (DANTE: salarii + 5121 invizibile pe card). Paletă unică (a înlocuit `CULORI` din control.js + `_CF_CUL` din firme.js). Gardă **VERDICT_PARITATE** cu două parități (randare vs `VC_RANDATE`; severitate vs `contabil` ∪ `VC_FARA_SEVERITATE`), pe chei parsate din sursă. Excepțiile de severitate (`documente_pozate`, `tva`-simplu) declarate cu motiv, nu judecate. Sortare C4 (pe termen) în renderer. Import `control_verdict.js?v=1` (consistent, cap.19).
**v2.23 (23.07.2026)** — cap.19 nou: consistența versiunii de modul la import (`?v=N` identic pe toate site-urile, inclusiv `import()` dinamic). Browserul instanțiază de două ori un modul importat cu tokeni divergenți (`/x.js` ≠ `/x.js?v=7`) — a doua copie nu vede starea primei. Gardă IMPORT_VERSIUNE (grupare pe calea rezolvată, >1 token = eroare). Reparate: `termene.js` (`firme.js` → `?v=7`), `navigator.js` (`control.js` dinamic → `?v=1`). A prins o a doua divergență (`control.js`) pe care sweep-ul manual grep o ratase (nu prindea `import()` dinamic). Simptom: antetul din `firme.js` lipsea pe calea Termene.
**v2.22 (23.07.2026)** — cap.18 nou: carduri pe firmă cu `regim` obligatoriu + filtrare prin `regim_contabil` (o sursă), listele `DOAR_SRL`/`DOAR_PFA` ELIMINATE. Gardă CARD_REGIM (card fără regim = eroare). Contract strict pe `t.regim_contabil` (throw dacă lipsește). 'declaratii' + 'casa' → ambele (erau ascunse la PFA — fals negativ).
**v2.21 (23.07.2026)** — Declaratii (poz.1) prezentare. DATA_DIALECT (cap.4) extins a doua oara: prinde si array de luni folosit ca ETICHETA luna-an (`luni[idx] … ${...an}`) care ocoleste `dataRo("luna_an")`; NU prinde luna-DOAR (`luni[r.luna]` fara an, fara echivalent dataRo) si nici pickerul (`LUNI.map` pt <option>). A prins 6 etichete locale (declaratii/cabinet/pachete/portal) — reparate. Panoul de clasificare D390 (F125): style inline display/flex/gap/color -> clase `.dec-recl-*`/`.dec-man-*` (cap.0); width/margin raman inline (pozitionare permisa). NOTA: garda display/flex/gap NU s-a extins — 217 stiluri inline frontend-wide = datorie acceptata (v2.11), extinderea = workstream separat.
**v2.20 (23.07.2026)** — Termene (poz.3) prezentare + gard DATA_DIALECT. dataRo: stil nou `luna_an` (`iulie 2026`, perioade lunare fără zi — balanțe/deconturi). DATA_DIALECT extins (cap.4): prinde array de nume de luni indexat prin `parseInt` (forma `dataLunga`, gaură descoperită — a patra oară azi o poartă verde peste o abatere; a scos 5 formatoare locale: termene/cabinet/portal convertite la dataRo, declaratii/pachete = pickere legitime, neatinse). P4: a 5-a stare de semafor `.pct-gri` (`var(--gri-semafor)`, cap.8) pentru incertitudine — D390 pe perioadă deschisă în Termene (posibil, nu ferm). Modal: neschimbat (cap.2a/cap.9, max-height calc(100vh-48px) + scroll intern — confirmat, DS interzice non-modal).
**v2.19 (23.07.2026)** — DEFAULT_FISCAL_TACIT: al 5-lea câmp `operatiuni_ic` (boolean: literalele True/False/false + "da"/"nu"), `.py`+`.js` (cap.17). `operatiuni_ic` devine obligatoriu la migrare, fără preselecție „Nu" tacită (decide obligația D390 — se depune numai pentru lunile cu operațiuni intracomunitare, instr. D390 anexa OPANAF 705/2020 anexa 2 pct.1.2 (anterior OPANAF 394/2017, abrogat)); criteriul afișat prin `.camp-ajutor`. Backend: `VectorIn.operatiuni_ic: Optional[bool]=None`, `vector_fiscal_api.salveaza` respinge None (400 IC_LIPSA), `citeste` întoarce None (nu False tacit) ca frontendul să distingă „nesetat" de „Nu". Frontend: `migrare.js` fără preselecție (valoare raw true/false/null), trimite null când nu e ales.
**v2.18 (23.07.2026)** — DEFAULT_FISCAL_TACIT: al 4-lea câmp `tip_decont` (+ literalele lunar/trimestrial), `.py`+`.js` (cap.17). `tip_decont || "trimestrial"` (migrare.js) și `or "lunar"` (termene_api) eliminate — periodicitatea decontului nu vine din ANAF v9, deci se cere obligatoriu la migrare (fără preselecție), cu criteriul art. 322 Cod fiscal afișat prin `.camp-ajutor`; termene nu mai ghicește (decont necompletat → nu emite termene D300).
**v2.17 (23.07.2026)** — DEFAULT_FISCAL_TACIT extins pe `.js` (cap.17): aceleași 3 câmpuri, formele `field || "lit"` și ternar `? … : "lit"` (literal fiscal în ramura ELSE). Nu prinde maparea valoare→etichetă (`=== "profit" ? "profit" : …`). Curățate: `migrare.js` (`tip_firma || "srl"` șters, `regim_fiscal` afișat null→„—"), `firme.js`. Backendul expune `regim_contabil` (`tenantii_userului` + `/migrare/vector`) — frontendul îl folosește, nu defaultează.
**v2.16 (23.07.2026)** — DEFAULT_FISCAL_TACIT (cap.17): câmpurile fiscale `regim_fiscal`/`tip_firma`/`platitor_tva` nu se defaultează pe literal inline (`or "micro"`, `|| "srl"`, `else "pfa"`); faptul + default-ul stau doar în primitivele `migrare_api` (`regim_contabil`/`regim_efectiv`/`tip_firma_nrm`). Motiv: `regim_fiscal or "micro"` în `termene_api` fabrica D100 pe un PFA. Regula în verificator scanează `.py`, exceptat `migrare_api.py`. Curățate: `termene_api`, `vector_fiscal_api`, `auth_api`, `tenant_provisioning`, `control_fiscal_api`.
**v2.15 (22.07.2026)** — formatarea sumelor/datelor în BACKEND (cap.4): text destinat utilizatorului construit în Python (`mesaj`/`temei`/`cauza`/`motiv`/`avert`/`descriere`/`actiune`, erori afișate, email, PDF) se trece prin `pdf_util.bani` + `pdf_util.data_ro` (oglinda Python a `bani`/`dataRo` din JS, `data_ro` NOU). Gărzile JS nu vedeau backendul → sume brute „40800.00 lei" și date ISO scăpau (dovedit F183). Regula BACKEND_UI_BRUT în verificator scanează `.py`; excepții documentate (XML/SAF-T, exporturi, JSON API, log, unități `:g`). Șabloanele `common.CODURI` formatate central în `common.problema` (`MONEDA_CAMP`). Reparate: `control_incrucisat` (16), `common`/`d112`/`taxare_inversa`/`main` (sume), `sinteza_zilnica`/`scadente`/`main` (date).
**v2.14 (18.07.2026)** — casetă-poartă `.caseta-poarta` (cap.5): întrebare obligatorie înainte de o acțiune consecventă, două alegeri care merg amândouă înainte (distinct de `confirmaCaseta`). Motivată de puntea factură→stoc (F172): „Pleacă marfa acum? DA/NU" înainte de emitere, la firmele cu gestiune cantitativă. Fundal chihlimbar-pal #fbf7ee, distinct de atenție (roșu) și info (albastru). Regula POARTA_INLINE în verificator.
**v2.13 (17.07.2026)** — stare goală canonică `.stare-goala` (+ modificator `.stare-goala--inline`); cap.6. Lista cu 0 rânduri = conținut de ecran (gol + cauză + ieșire), nu mesaj de stare. Elimină `.cap-gol`/`.sa-gol` (foloseau `#999` hardcodat în loc de `var(--gri)`) și utilizările de stare-goală ale `.mig-gol`. ~40 apariții migrate; mesajele de eroare `.mig-gol` din `catch` (~50) = datorie separată către `arataMesaj` (DE_FACUT). Regula STARE_GOALA în verificator (clasă interzisă `cap-gol`/`sa-gol`/`mig-gol`-stare-goală + fundătură).
**v2.12 (17.07.2026)** — casetă informativă standing `.caseta-info` (albastru-pal #eef4fd, ne-distructivă), distinctă semantic de `.caseta-atentie` (roșu = distructiv); cap.5. Motivată de ecranul de conectare SPV (avertismentul de 24h cere o notă importantă, permanentă, informativă, fără regulă până acum). Regula CASETA_INFO în verificator (prinde note info ad-hoc cu fundal albastru-pal inline).
**v2.11 (12.07.2026)** — panouri de conținut: clasa canonică `.panou` (alb + bordură #b9c2cf); reparate `pac-rezumat`/`pac-deschide-zona`/`grila-campuri-compacta` (gri pe gri); cap.16 nou. Carduri: 73 hex literal → `...CULORI_CARD.cheie` + regula CULOARE_CARD_HEX; decizie spacing închisă (rămâne literal).
**v2.9 (12.07.2026)** — canonizat culorile/bordurile/raza din cod: 3 borduri + 6 culori ad-hoc → `var()`, 4 border-radius → `var(--raza)`; cap.15 nou + reguli RADIUS_INLINE (și culoare ad-hoc) în verificator. Landing exclus (sistem separat).
**v2.8 (12.07.2026)** — sistem de tipografie: 6 tokeni de dimensiune + 7 clase de tip (stil.css); eliminat toate font-size literale inline (18 migrate în 9 ecrane); cap.14 nou + regula FONT_INLINE în verificator.
**v2.7 (12.07.2026)** — dicționar canonic unic `ICOANE` (api.js, 22 iconițe, 5 noi); eliminat dicționarele locale divergente (cabinet/admin/asistent); reasignat 8 carduri de la `report` generic la iconițe sugestive distincte; cap.13 nou + regula ICOANE_LOCAL în verificator.
**v2.6 (12.07.2026)** — consolidat sistemul de culori-card: 35 nuanțe divergente → 7 culori-concept canonice în `CULORI_CARD` (api.js); cap.12 nou (paletă card normativă).
**v2.5 (12.07.2026)** — eliminat clasa `buton-ingust` (JS + CSS + lista albă verificator); regulă DATA_BRUTA în verificator (prinde `${x.data}` afișat fără `dataRo` — a scos la iveală data REGES nemarcată în firme.js).
**v2.4 (12.07.2026)** — `baniRotund()` canonic pentru cifre rotunjite (portal cifre client + cockpit cabinet); eliminat dialectele `lei` (portal/cabinet) și `_bani`/inline (facturi) → `bani()`/`baniRotund()`; stil `zi_luna_text` (`25 feb`) pentru termene client. Regula FMT_LOCAL lărgită la orice nume de const (cap.4).
**v2.3 (12.07.2026)** — audit dată: eliminat dialectele `fmtTermen`/`fmtD` (portal) → `dataRo(…, "zi_luna")`; stil nou `zi_luna` în `dataRo`; date ISO brute (`r.data`/`f.data`/`b.data`/`det.data`) → `dataRo`; sumă din `fmtDif` → `bani()`. Regulă DATA_DIALECT în verificator (cap.4).
**v2.2 (12.07.2026)** — eliminat dialectul `fmt` local (7 definiții în firme/portal/migrare) → `bani()` canonic; `fmtZi` rezidual → `dataRo()`; procente separate ca `pct`. Regulă FMT_LOCAL în verificator; interdicție funcții monetare locale (cap.4).
**v2.1 (12.07.2026)** — adăugate: `bani()` formator monetar canonic + interdicție `toFixed` pe afișare (cap.4); `.camp-input` obligatoriu pe input/select + interdicție `.mig-text` + structură label canonică (cap.2). Ambele reguli în `verificator_conformitate.py` (BANI_NEFORMATATI întărit, MIG_TEXT nou).
**v2.0 (11.07.2026)** — migrat docx → .md; adăugate: bordură buton-secundar #b9c2cf (cap.1); interdicție wrapper alb pe formulare (cap.2); `dataRo()` canonic (cap.4); interdicție prompt() nativ (cap.5); `.oblig` asterisc roșu + `.camp-ajutor` albastru (cap.6); `esc` canonic + interdicție variante locale (cap.10).
**v1.0 (08.07.2026)** — versiune inițială, 10 capitole (docx).

## Componenta: semnul "?" de ajutor contextual (v_ajutor, 11.08.2026)
.ajutor-btn - buton mic circular (20px) cu "?", plasat langa titlul unei functionalitati DOAR unde exista ceva de spus dincolo de eticheta (reguli fiscale, preconditii, consecinte). Deschide un modal cu textul de folosire din coloana ajutor (FUNCTIONALITATI.csv), via api.js semnAjutor(fid) + handler global. NU se pune peste tot (Salveaza/Cauta/Inapoi/camp Denumire = zgomot).
