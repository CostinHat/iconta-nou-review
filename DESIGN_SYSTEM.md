# iConta — Design System

*Document normativ · v2.31 · 08 august 2026 (editabil prin SSH)*

**Acest document este REFERINȚA OBLIGATORIE pentru orice ecran nou și pentru auditul celor existente. Nicio abatere fără actualizarea prealabilă a acestui document.**

---

## 0. Principii generale

- Nicio clasă vizuală nouă. Orice element nou folosește exclusiv clasele din acest document. Clase suplimentare = doar hook JS sau poziționare (margin/width), niciodată culori/fonturi/umbre/dimensiuni.
- Când se descoperă o inconsistență: STOP, se corectează, apoi se continuă. Zero datorie tehnică vizuală.
- La orice decizie de schimbare de comportament se verifică TOATE locurile unde comportamentul vechi există, nu doar cel discutat.
- Textele afișate folosesc diacritice românești complete; codul/comentariile/markerii — fără diacritice.
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

**Feedback obligatoriu:**
- Butoane cu zonă toggle: primesc `.buton-activ` cât timp zona e deschisă; deschiderea unei zone închide zonele-frate.
- Acțiuni asincrone: butonul se dezactivează + text "Se salvează…" / "Se trimite…" pe durata cererii.

**INTERZIS**: clase de buton în afara setului (ex. `buton-ingust` — folosește margin/width inline pentru dimensionare, nu clasă nouă). Prins de regula BUTOANE din verificator (v2.5 — `buton-ingust` scos și din lista albă a verificatorului, era o excepție greșită).

## 2. Pattern fundamental: nimic vizibil decât la selecție

- Un ecran arată la deschidere DOAR: titlu + informația de stare esențială + itemii de meniu (`.acces-card`/`.meniu-card`) sau lista care e scopul ecranului.
- Formularele de adăugare/editare/configurare NU apar la deschidere — apar la apăsarea unui buton dedicat.
- Excepție: ecranele-formular, unde formularul ESTE scopul (Raport Z, Bilanț, Emitere factură).
- Formularele deschise la selecție au întotdeauna buton "Renunță" (`.btn-link` sau `.buton-secundar`) care revine la ecranul anterior.

**IMPORTANT (v2.0)**: Formularele NU se învelesc într-o casetă albă (`background:#fff`). Stau direct pe fundalul ferestrei (gri); doar câmpurile de input sunt albe cu bordură #b9c2cf. Un wrapper alb pe fundal gri-deschis face caseta invizibilă.

**Clasa de câmp (v2.1)**: input/select normale poartă exclusiv `.camp-input` (înălțime 40px, bordură vizibilă #b9c2cf, font aplicație). INTERZIS `.mig-text` pe input/select — e croită doar pentru textarea ecranului de migrare (font monospace, bordură 0.5px invizibilă pe alb). Structura canonică de câmp: `<label class="camp"><span class="camp-eticheta">Etichetă</span><input class="camp-input"></label>` — nu `<label>text<br><input>`.
**Checkbox cu etichetă (v2.11)**: un checkbox însoțit de text-etichetă poartă EXCLUSIV `.set-bifa`. Structura canonică: `<label class="set-bifa"><input type="checkbox"> <span>Text</span></label>`. INTERZIS checkbox cu etichetă-text pe `style` inline (font-size, display) sau clase ad-hoc (`.cm-check`). Excepție: checkbox-urile fără text alături (în tabele/liste, doar bifă) nu au nevoie de `.set-bifa`.

## 2a. Deschiderea cardurilor: MEREU fereastra (modal), niciodata inline
- Orice card din grila cabinetului (`.cab-card`) se deschide EXCLUSIV prin `nav.deschide(titlu, corp, opt)` — fereastra overlay cu X.
- INTERZIS ca un card sa se deschida inline in corpul panoului (sa suprascrie `.cab-grila`/`continut`). Un card = o fereastra.
- Meniurile cu sub-optiuni (ex. Firme, Activitate) sunt tot ferestre: sub-optiunile devin `.meniu-card` in corpul ferestrei, NU un al doilea nivel inline cu breadcrumb.
- Consecinta: in corpul panoului nu apare breadcrumb ("Panou > X") si nici al doilea rand de sageti. Inchiderea se face din X-ul ferestrei.

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
- X-ul închide fereastra de oriunde. Săgeata nu ține locul lui X.
- Ecranele-poartă (configurare obligatorie) primesc `setInapoi(undefined)` ca să evite bucla.

## 4. Casete de date

- Orice bloc de date (tabel, totaluri, liste) stă în casetă pe FOND ALB cu bordură 1px var(--linie), distinct de fundalul ferestrei.
- Tabele: titlurile și valorile la STÂNGA, cu excepția coloanelor de sume monetare — titlu și valori la DREAPTA (separator zecimal pe aceeași verticală).
- **Toate datele se afișează prin `dataRo(d, stil)` din api.js** (v2.0). SINGURA formatare de dată. Stiluri: implicit `zz.ll.aaaa`; `cu_ora` → `zz.ll.aaaa HH:MM`; `lung` → `11 iulie 2026`; `zi_luna_text` → `11 iul`; `luna_an` → `iulie 2026` (perioade lunare fără zi — balanțe, deconturi; v2.20); `zi_luna` → `zz.ll` (compact). Pentru date care pot **traversa anul** (ex. termene în fereastra de 60z care intră în an+1) se folosește un stil cu an (`lung`/`scurt`/`luna_an`), NU `zi_luna`/`zi_luna_text` (ambiguu). INTERZIS `toLocaleDateString` ad-hoc, date ISO brute în template (`${x.data}` direct), funcții locale de formatare a datei (`fmtZi`/`fmtD`/`fmtTermen`, **funcție/array local de nume de luni indexat prin `parseInt` — ex. `luni[parseInt(p[1])-1]`, forma `dataLunga`, v2.20**). Regula DATA_DIALECT în verificator prinde și această formă (array de luni indexat cu `parseInt`); NU atinge pickerele de lună (`LUNI.map(...)` pentru `<option>`) sau etichetele din stare (`LUNI[S.luna-1]`, fără `parseInt`) — acelea sunt legitime.
- **Perioadă lună/an NUMERICĂ (v2.21, 27.07.2026)**: `luna_an_numeric` — `07/2026`. DECIS de Costin: antetele de ecran (Firme, Facturi) folosesc forma NUMERICĂ, nu `iulie 2026`. Motiv: e mai scurtă, se aliniază în listă cu restul cifrelor și e forma cu care lucrează contabilul pe declarații. `luna_an` („iulie 2026") rămâne pentru titluri și texte narative (balanțe, povestea lunii). Ambele trec prin `dataRo` — formatarea locală cu `padStart` rămâne INTERZISĂ (cap.4: o singură funcție de formatare).
- **Toate sumele afișate se trec prin `bani(v)` din api.js** (v2.1). SINGURUL formator monetar. Produce format românesc (1.234,56). INTERZIS `toFixed(2)` pe sume afișate (dă `1234.56`, nepotrivit), formatări locale sau concatenare brută. Excepții permise: `value` de `<input type="number">` și payload trimis la backend (acolo se cere punct zecimal). Moneda (`lei`/`RON`) se afișează când suma stă izolat sau unitatea nu e evidentă (total factură, fluturaș, indemnizație, sold); se omite în liste/tabele dense unde contextul o face redundantă (cost/porție, coloane cu antet monetar). `bani()` e mereu obligatoriu; moneda e contextuală. INTERZISE funcții locale de format monetar (`const fmt = …toLocaleString`) — dialect care produce formate divergente (0 vs 2 zecimale). Procentele NU folosesc `bani()` (ar da `19,00%`); pentru ele funcție separată (`pct`) sau `%` simplu. Pentru cifre de ansamblu rotunjite la leu (cockpit cabinet, cifrele firmei pe portalul client) → `baniRotund(v)` canonic (0 zecimale), NU dialect local. Orice `const X = …toLocaleString("ro-RO")` local (sub orice nume, nu doar `fmt`) e INTERZIS și prins de FMT_LOCAL. Cantități fără zecimale inutile. Procente compacte (11%).
- **BACKEND (Python) — text destinat utilizatorului: aceeași regulă, alt limbaj** (v2.15, 22.07.2026). Orice sumă sau dată construită în backend care ajunge la utilizator (câmpurile `mesaj` / `temei` / `cauza` / `motiv` / `avert` / `descriere` / `actiune`, mesaje de eroare afișate, corp/subiect de email, text pe PDF) se formatează prin sursele canonice **`pdf_util.bani(x, mon)`** (sume, 1.234,56) și **`pdf_util.data_ro(d, stil)`** (date — oglinda Python a lui `dataRo`; stiluri `scurt`/`cu_ora`/`lung`/`zi_luna`). INTERZIS `f"{x} lei"` / `%d lei` brut, `str(sold)`, `strftime("%d.%m…")` local pentru afișare. Motiv: gărzile JS nu văd backendul — o sumă „40800.00 lei" sau o dată ISO brută trimisă din Python scapă complet controlului (dovedit F183, 22.07). Regula **BACKEND_UI_BRUT** în verificator (scanează `.py`). EXCEPTAT (nu e afișare): XML/SAF-T (ISO cerut de spec — etransport, D406), exporturi cu format al destinației (WinMentor), câmpuri de dată ISO în JSON API (formatate client-side prin `dataRo`), log-uri/print, valori unitare `:g` intenționate. Șabloanele `.format()` din `common.CODURI` se formatează CENTRAL în `common.problema()` (bani pe câmpurile din `MONEDA_CAMP`) — orice câmp monetar nou dintr-un șablon se adaugă acolo.
- Etichetă și valoare pe același rând se separă clar (flex space-between + gap).

## 5. Casete de atenționare, confirmări și INPUT

- Stil unic: `.caseta-atentie` — fundal #fdf3f3, bordură 2px #d98c8c, mesaj în `.ca-mesaj`. Butoanele stau SUB casetă, pe clase canonice.
- **Casetă informativă standing (v2.12)**: `.caseta-info` — fundal albastru-pal #eef4fd, bordură 1px #b9c2cf, mesaj în `.ci-mesaj`. Pentru o notă IMPORTANTĂ, PERMANENTĂ, informativă (nu o confirmare, nu un mesaj de stare tranzitoriu prin `arataMesaj`). Distinctă semantic de `.caseta-atentie`: roșul rămâne EXCLUSIV pentru atenționare/acțiune distructivă; informația neutră NU se colorează roșu. INTERZIS o notă informativă ad-hoc cu fundal albastru-pal inline (`style="background:#eef4fd…"`) — se folosește `.caseta-info`. Prins de regula CASETA_INFO în verificator.
- **Casetă-poartă la o acțiune (v2.14)**: `.caseta-poarta` — o întrebare OBLIGATORIE înainte de o acțiune consecventă, cu DOUĂ alegeri care merg AMÂNDOUĂ înainte (nu confirmă/anulează — pentru acela e `confirmaCaseta`). Cazul canonic: emiterea unei facturi cu linii de stoc la o firmă cu gestiune cantitativă — „Pleacă marfa acum? DA (descarcă gestiunea) / NU (doar fiscal)". Structura: `.caseta-poarta` > `.cp-mesaj` (întrebarea + consecința) + `.cp-butoane` (butoanele canonice). Fundal neutru chihlimbar-pal #fbf7ee — distinct de `.caseta-atentie` (roșu, distructiv) și `.caseta-info` (albastru, informativ standing). Răspunsul e cerut ÎNAINTE de acțiune și NU se poate sări (nu bifă opțională, care se uită). INTERZISĂ reproducerea ad-hoc cu fundal inline (`style="background:#fbf7ee…"`) — se folosește `.caseta-poarta`. Prinsă de regula POARTA_INLINE în verificator.
- **`confirm()`, `alert()` și `prompt()` native de browser sunt INTERZISE** (v2.0 — include prompt). Confirmări via `confirmaCaseta(zona, mesaj, laConfirm, {textOk})`. Input via formular în-ecran (câmp + buton), niciodată prompt nativ.
- Mesajul spune exact ce se întâmplă și dacă e ireversibil.

## 6. Mesaje de stare, câmpuri obligatorii și ghidaj

- Succes: text verde #1d7a4d, weight 600, afișat pe ecranul principal DUPĂ revenirea din formular.
- `arataMesaj(el, txt, tip)` — singura cale de afișare a mesajelor de stare. Tipuri canonice: `eroare` (roșu), `avert` (galben), `info` (gri), `ok` (verde, succes). INTERZIS mesaj de stare prin innerHTML cu clase ad-hoc (`mig-gol`, `pf-intro`, span inline).
- Eroare de câmp/formular: `<span class="msg-eroare">` (roșu), lângă câmpul/butonul relevant. Niciodată tăcere la o acțiune eșuată.
- Validări preventive cu mesaj explicativ, nu doar refuz.
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

## 7. Documente PDF

- Tabelele PDF respectă aceleași reguli de aliniere ca HTML (cap. 4): stânga peste tot, sume la dreapta cu separator aliniat.
- Preferință: tabele reportlab Table cu colWidths explicite (ca factura_pdf.py), nu drawString cu coordonate manuale.

## 8. Semafoare

- Mereu vertical, ordinea ROȘU → GALBEN → VERDE (urgența întâi).
- Bulină LED 16px cu gradient + etichetă text 10px.
- Culori canonice: verde #1d7a4d · galben #c9961f · roșu #ff3b30.
- Se folosesc EXCLUSIV prin tokeni: `var(--verde)` / `var(--galben)` / `var(--rosu-semafor)`. Hex literal interzis în JS/CSS (excepții: definiția tokenului, nuanțele deschise din gradientul `dot:`). Prins de regula HEX_SEMAFOR în verificator (v2.11). Starea gri (necunoscut/necompletat): `var(--gri-semafor)` #9aa3b2 + fundal `var(--gri-fundal-semafor)` #eef0f3 — un singur gri de semafor, nu nuanțe ad-hoc.

- Buline de stare pe fire de conversatie (Raporteaza): ROSU = in asteptare de raspuns, VERDE (#1d7a4d) = raspuns primit. Fara concept de citit/necitit; cifra de pe card = firele in asteptare (stare noua) si scade singura la sosirea raspunsurilor.

## 9. Ferestre de lucru

- Overlay umbrit uniform rgba(20,30,45,0.55) pentru TOATE ferestrele. Card central alb.
- max-height calc(100vh - 48px); la tabele lungi: antet + butoane fixe, doar tabelul derulează.
- Grile de câmpuri în ferestre: clasa `.grila-doc` (copiii primesc `min-width:0` ca să se strângă) — fără grile inline cu display:grid care lasă inputurile să împingă fereastra în scroll orizontal.
- `.fer-larg` max-width 1000px doar pentru tabele.
- Nicio fereastră nu iese din ecran.

## 10. Escape și securitate

- **`esc` din api.js (v2.0) = SINGURA funcție de escape.** Escapează `& < > " '` (5 caractere, inclusiv apostroful). Se **importă** din api.js, niciodată nu se **redefinește local**. INTERZISE: (a) variante locale cu alt nume (`_esc`/`escB`/`escV`/`escS`/`escC`/`escJ`) care omit apostroful; (b) **redefinirea locală a lui `esc`** (`function esc` / `const|let|var esc =`) într-un ecran — o copie locală poate fi mai slabă (ex. una care escapa doar `"` → XSS pe `<>` în conținut de element) și oricum e a doua sursă de adevăr pentru o primitivă de securitate; (c) **strip inline de caractere HTML** (`.replace(/[<>&]/g, "")` și variante) ca sanitizare ad-hoc — nu e XSS (scoate `<>`), dar e **data-lossy** (scoate `&` din nume: „A&B" → „AB") și tot o a doua sursă de sanitizare. Regula **ESC_LOCAL** în verificator prinde toate trei formele (apel de variantă + redefinire locală + strip inline `[…<>&…]`).
- Orice dată user/import-controlled afișată în innerHTML se trece prin `esc()`.

## 11. Procedură de lucru

- Orice element UI nou: se alege din acest document. Dacă nu există → se discută, se adaugă AICI întâi, apoi se implementează.
- O regulă nouă intră în ACEST document ȘI (unde e cazul) în `verificator_conformitate.py` simultan.
- Audit de conformitate la fiecare ecran atins: se verifică cap. 1–10.
- Acest document se versionează în git (`.md`, editabil prin SSH — v2.0, migrat din docx).

## 12. Culori de card (meniu)

- **Cardurile-hub** (cele 9 carduri din panoul cabinetului `.cab-card` + meniurile-hub gen Firme/Activitate) folosesc EXCLUSIV paleta canonică de 7 culori-concept din `CULORI_CARD` (api.js). Fiecare card-hub: `bg` (fundal pastel) + `fg` (titlu/icon saturat).
- **Itemii-listă** (`.acces-card`/`.meniu-card` folosiți ca opțiuni înrudite într-un submeniu: Setări, portal documente, login) NU poartă culori-concept — au fundalul albastru-pal uniform al clasei `.acces-card`. Culorile-concept sunt pentru puncte de intrare majore, nu pentru liste de opțiuni.
- Paleta: **albastru** #e9f0fe/#1d4ed8 (firme, facturi, pachete) · **verde** #e6f6ec/#16a34a (termene, capacitate, cifre) · **teal** #dff4f2/#0a807b (control fiscal, declarații) · **violet** #efebfe/#6d28d9 (sinteză, raportări) · **piersică** #faece7/#993c1d (de validat, asistenți, activitate) · **chihlimbar** #fbeedd/#92500a (recomandă, anunțuri) · **ardezie** #eaeef6/#45597f (consolidare, documente, setări, suport).
- INTERZIS hex de card ad-hoc în afara paletei. Nuanțele apropiate NU se multiplică — un singur verde, un singur violet etc.
- Cardurile REFERĂ paleta, nu o copiază: `...CULORI_CARD.cheie` (import din api.js), NICIODATĂ `bg:"#..."` literal — chiar dacă valoarea coincide cu paleta. Excepție: semaforul (control.js, obiecte cu `dot:`). Prins de regula CULOARE_CARD_HEX în verificator.
- Culorile de semafor (cap.8) și cele de stare rămân separate; astea sunt doar pentru carduri de navigare.

### Spacing (decizie 12.07.2026)
- Margin/padding inline rămân valori literale (6/8/10/12/14/16px, tipar de facto consistent, ~2100 apariții). NU se canonizează în tokeni — raport risc/câștig nefavorabil. Decizie închisă, nu se redeschide fără motiv nou.

## 13. Iconițe

- Iconițele de card/UI folosesc EXCLUSIV dicționarul canonic unic `ICOANE` (api.js) — path-uri SVG interne, viewBox 24×24, stroke. NU se duplică dicționarul în ecrane (era copiat divergent în cabinet/admin/asistent).
- Fiecare concept = o iconiță sugestivă distinctă. Triada card = culoare + denumire + iconiță, toate coerente. INTERZIS iconiță generică (`report`) folosită ca fallback pe concepte diferite.
- Iconiță nouă → se adaugă în `ICOANE`, nu inline într-un ecran. Prins de regula ICOANE_LOCAL în verificator.

## 14. Tipografie

- Scară de dimensiuni canonică (tokeni CSS): `--text-titlu` 22px · `--text-sectiune` 19px · `--text` 17px · `--text-mic` 15px · `--text-desc` 13px · `--text-micut` 12px. NU se folosesc alte valori.
- Clase de tip (rol semantic, în stil.css): `.tip-titlu` · `.tip-sectiune` · `.tip-corp` · `.tip-desc` (13px gri, descrieri) · `.tip-figura` (19px bold, cifre de card) · `.tip-total` (17px bold, totaluri) · `.tip-micut` (12px, note).
- INTERZIS `font-size` cu valoare literală inline (`font-size:13px`). Se folosește clasa de tip sau, excepțional, `font-size:var(--text-*)`. Prins de regula FONT_INLINE în verificator.
- Culoarea, marginea, alte stiluri non-tipografice pot rămâne inline; doar dimensiunea fontului trece prin clasă/token.

## 15. Tokeni de culoare, bordură, rază

- Culorile din cod folosesc EXCLUSIV variabile canonice: `var(--ardezie)` (text), `var(--gri)`/`var(--gri-clar)` (secundar), `var(--rosu)`/`var(--verde)`/`var(--galben)`/`var(--albastru)` (stări), `var(--linie)` (borduri), `var(--fundal)`/`var(--alb)` (fundaluri). INTERZIS hex ad-hoc (`#ddd`, `#8a97a5`, `#fff`) în aplicație.
- Border-radius folosește `var(--raza)` (6px). INTERZIS valoare literală (`border-radius:8px`). Excepție: `50%` pentru cercuri.
- Landing page (`pagina-*`, login) e sistem vizual separat (marketing) — nu se supune paletei aplicației.

---

## 16. Panouri de conținut
- Orice casetă de conținut așezată direct pe corpul gri al ferestrei folosește clasa canonică `.panou`: fundal ALB + bordură `#b9c2cf` + `var(--raza)` + padding 12/14. Clasele specifice ecranului adaugă DOAR diferențele (margin, layout, border-style), nu redefinesc fundalul/bordura.
- INTERZIS panou transparent sau pe `var(--fundal)` direct pe corpul ferestrei — gri pe gri = invizibil. Excepții legitime: stări hover, sub-zone în interiorul unui panou alb (ex. antet de fir), zone de scroll tip `rec-modal-corp`.
- Exemple conforme: `pac-rezumat`, `pac-deschide-zona` (dashed), `grila-campuri-compacta`.

## 17. Fapte fiscale — o singură sursă, fără default tacit (backend)
- **DEFAULT_FISCAL_TACIT** (v2.16, 23.07.2026; extins v2.18, v2.19). Un câmp fiscal decisiv (`regim_fiscal`, `tip_firma`, `platitor_tva`, `tip_decont`, `operatiuni_ic`) **NU se defaultează pe LITERAL inline** — interzis `x or "micro"`, `x || "srl"`, `… else "pfa"`, `? : "trimestrial"`, `operatiuni_ic or False`, `operatiuni_ic || false` (literalele: micro/profit/srl/pfa/lunar/trimestrial + booleanul True/False/false și "da"/"nu" pentru `operatiuni_ic`). Un câmp obligatoriu care nu se poate autocompleta (ex. `tip_decont` — ANAF v9 nu aduce periodicitatea; `operatiuni_ic` — profil declarat de contabil, decide obligația D390) se cere EXPLICIT, cu criteriul afișat prin `.camp-ajutor` (cap.6), fără preselecție tacită. Faptul, normalizarea și default-ul trăiesc **într-un singur loc**: primitivele din `core/migrare_api.py` (`regim_contabil` = tip_firma→partidă simplă/dublă, `regim_efectiv` = regimul CIT efectiv cu partidă simplă⇒None, `tip_firma_nrm` = normalizare + default 'srl'). Consumatorii le importă; NU redau fallback-ul. Motiv: un `regim_fiscal or "micro"` inline în logica de obligații fabrică declarații pe firme la care nu se aplică (dovedit: termene emitea D100 pe un PFA, 23.07). Se prinde forma or/||/else — fallback pe CITIRE (`x or "micro"`, `x || "srl"`, `… else "pfa"`, ternar `? … : "micro"` cu literalul în ramura ELSE = default când câmpul lipsește); atribuirea simplă `x = "srl"` (declarație, nu fallback) și maparea valoare→etichetă `x === "profit" ? "profit" : …` (literal în ramura THEN) NU se prind. Regula **DEFAULT_FISCAL_TACIT** în verificator scanează **`.py` ȘI `.js`**; EXCEPTAT: `migrare_api.py` (primitivele — singurul loc unde literalul e legitim). Frontendul folosește FAPTUL expus de backend (`regim_contabil` prin `tenantii_userului` / `/migrare/vector`), nu defaultează inline.

## 18. Carduri pe firmă — regim obligatoriu, o singură sursă

- Fiecare card din meniul unei firme (`meniuFirma`, `optiuni`) declară `regim: "ambele" | "simpla" | "dubla"` **OBLIGATORIU** (ca `activ`), fără default tacit. Vizibilitatea derivă prin `regim_contabil` (fapt UNIC, `migrare_api`): `optiuni.filter(o => o.regim === "ambele" || o.regim === t.regim_contabil)`. INTERZISE liste hardcodate paralele pe `tip_firma` (fostele `DOAR_SRL`/`DOAR_PFA` — a 4-a sursă la aceeași întrebare, eliminate 23.07). O regulă, ca `STRATURI_META` la straturile de migrare. Regula **CARD_REGIM** în verificator (card fără `regim` = eroare).
- `t.regim_contabil` cu **contract STRICT**: expus de backend (`auth_api`); dacă lipsește pe obiectul-firmă, meniuFirma **eșuează vizibil** (throw), NU degradează tăcut la „doar ambele". Orice cale nouă către meniuFirma (ex. din Termene) trebuie să propage `regim_contabil`, ca `tip_firma`.
- Regim per concept: partidă dublă (`dubla`) = jurnal, balanță, bilanț, operațiuni speciale, stocuri (371/607), centre de cost. Partidă simplă (`simpla`) = RIP. Restul = `ambele` (declarații — un PFA datorează D112/D300/…, excluderea fină D100/D101/D406 o face `neaplicabile_forma` în ecran, nu ascunderea cardului; Casă — plafon Legea 70/2015 se aplică PFA). Un card care e „ambele" dar conține operațiuni de un singur regim se filtrează FIN în interior, NU se ascunde (ex. Casă: contarea 5311 e partidă dublă, plafonul e pentru toți).

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

## Changelog
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
**v2.19 (23.07.2026)** — DEFAULT_FISCAL_TACIT: al 5-lea câmp `operatiuni_ic` (boolean: literalele True/False/false + "da"/"nu"), `.py`+`.js` (cap.17). `operatiuni_ic` devine obligatoriu la migrare, fără preselecție „Nu" tacită (decide obligația D390 — se depune numai pentru lunile cu operațiuni intracomunitare, instr. D390 anexa OPANAF 394/2017 pct.1.2); criteriul afișat prin `.camp-ajutor`. Backend: `VectorIn.operatiuni_ic: Optional[bool]=None`, `vector_fiscal_api.salveaza` respinge None (400 IC_LIPSA), `citeste` întoarce None (nu False tacit) ca frontendul să distingă „nesetat" de „Nu". Frontend: `migrare.js` fără preselecție (valoare raw true/false/null), trimite null când nu e ales.
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
