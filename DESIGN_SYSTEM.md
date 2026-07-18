# iConta — Design System

*Document normativ · v2.14 · 18 iulie 2026 (migrat din docx în .md, editabil prin SSH)*

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
- **Toate datele se afișează prin `dataRo(d, stil)` din api.js** (v2.0). SINGURA formatare de dată. Stiluri: implicit `zz.ll.aaaa`; `cu_ora` → `zz.ll.aaaa HH:MM`; `lung` → `11 iulie 2026`. Stiluri: implicit `zz.ll.aaaa`; `cu_ora`; `lung`; `zi_luna` → `zz.ll` (compact, pentru termene/perioade). INTERZIS `toLocaleDateString` ad-hoc, date ISO brute în template (`${x.data}` direct), funcții locale de formatare a datei (`fmtZi`/`fmtD`/`fmtTermen` etc.). Regula DATA_DIALECT în verificator.
- **Toate sumele afișate se trec prin `bani(v)` din api.js** (v2.1). SINGURUL formator monetar. Produce format românesc (1.234,56). INTERZIS `toFixed(2)` pe sume afișate (dă `1234.56`, nepotrivit), formatări locale sau concatenare brută. Excepții permise: `value` de `<input type="number">` și payload trimis la backend (acolo se cere punct zecimal). Moneda (`lei`/`RON`) se afișează când suma stă izolat sau unitatea nu e evidentă (total factură, fluturaș, indemnizație, sold); se omite în liste/tabele dense unde contextul o face redundantă (cost/porție, coloane cu antet monetar). `bani()` e mereu obligatoriu; moneda e contextuală. INTERZISE funcții locale de format monetar (`const fmt = …toLocaleString`) — dialect care produce formate divergente (0 vs 2 zecimale). Procentele NU folosesc `bani()` (ar da `19,00%`); pentru ele funcție separată (`pct`) sau `%` simplu. Pentru cifre de ansamblu rotunjite la leu (cockpit cabinet, cifrele firmei pe portalul client) → `baniRotund(v)` canonic (0 zecimale), NU dialect local. Orice `const X = …toLocaleString("ro-RO")` local (sub orice nume, nu doar `fmt`) e INTERZIS și prins de FMT_LOCAL. Cantități fără zecimale inutile. Procente compacte (11%).
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

- **`esc` din api.js (v2.0) = SINGURA funcție de escape.** Escapează `& < > " '` (5 caractere, inclusiv apostroful). INTERZISE variante locale (`_esc`/`escB`/`escV`/`escS`/`escC`/`escJ`) care omit apostroful — risc XSS în atribute cu ghilimele simple.
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

## Changelog
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
