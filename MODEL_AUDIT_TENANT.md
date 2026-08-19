# MODEL DE AUDIT MULTIFAȚETAT PER TENANT

Metodă unică de **investigare → reparare → verificare**, aplicabilă oricărui tenant. Nu e o listă de bune
intenții: **fiecare fațetă are o sondă care se rulează și un criteriu de verdict scris.** O firmă nu e „auditată"
până n-au trecut toate fațetele aplicabile, fiecare cu proba ei.

Derivă din REGULILE PERMANENTE (memoria de lucru) și le operaționalizează. Rezultatul fiecărei parcurgeri intră
ca un rând în [`ISTORIC_TENANTI.md`](ISTORIC_TENANTI.md).

---

## Principii care traversează toate fațetele

- **P1 — Sursa bate memoria.** Temeiul (legal, structură, nomenclator) se verifică la sursă în `anaf_surse/` sau
  la arbitru (DUK / XSD / validator), nu din memorie. Ce lipsește din corpus se aduce întâi.
- **P2 — Fără default fabricat.** Necunoscut rămâne necunoscut, declarat explicit. Nu inventa o valoare tăcută.
- **P3 — Nu repara cazul, repară tiparul (Regula 13).** Orice defect cu tipar: descrie-l mecanic, caută-l în
  toată aplicația, repară toate instanțele, pune gardă. Dacă tiparul nu se poate descrie mecanic, enumeră exhaustiv
  suprafața și dă verdict pe fiecare element, cu criteriul scris.
- **P4 — Cifra afișată = proba.** Selectorul răspunde la ce întrebi; captura arată ce n-ai întrebat. Orice ecran
  atins se privește ca un contabil care-l deschide prima oară.
- **P5 — Regulă nouă → gardă RED-probată, simultan în cod și în verificator.** Mutație → RED → GREEN; reversul
  mutației din **backup-copie**, NU `git checkout` pe fișier needitat-committed (șterge munca necomisă).

---

## Fațetele (ordinea = ordinea de parcurgere)

Ordinea nu e arbitrară: datele greșite otrăvesc tot ce urmează, deci se validează întâi; a11y se face pe ecranul
deja corect funcțional.

### F1 — Perimetru & inventar
**Întrebarea:** ce atinge tenantul? (declarațiile datorate din vectorul fiscal, ecranele accesibile, registrele,
gărzile care-l păzesc). **Sondă:** deschide firma cu Playwright (helper tip `~/probe_t006/wt006.py`), enumeră ce
declarații apar „de depus", ce ecrane sunt accesibile din ecranul principal. **Verdict:** ai lista completă a
suprafeței de auditat, scrisă; nimic „presupus prezent" fără să fi fost văzut.

### F2 — Corectitudinea calculului (declarații)
**Întrebarea:** fiecare declarație datorată se generează corect și trece arbitrul? **Sondă:** generează fiecare
declarație pe date reale → `DUKIntegrator -v <COD>`; confruntă câmp-cu-câmp cu `anaf_surse/*_struct` + XSD (DUK e
lenient — trece câmpuri pe care nu le verifică). **Verdict:** DUK `valid` **ȘI** temeiul citat la sursă (P1) **ȘI**
restricția legală probată (ce legea nu permite, aplicația refuză). „A trecut validarea" ≠ conform.

### F3 — Integritatea datelor (seed ↔ consumator)
**Întrebarea:** fiecare câmp folosit — cine îl scrie, cine îl citește, ajunge valoarea reală până la capăt?
**Sondă:** urmărește câmpul de la producător la consumator pe **date populate** (ruptura seed↔consumator), nu pe
fixture goale. **Verdict:** valoarea reală ajunge la consumator; niciun default fabricat pe drum (P2); nimic pierdut.

### F4 — Accesibilitatea funcțională a ecranelor
**Întrebarea:** se ajunge la funcționalitate din ecranul principal, cu interacțiune reală? **Sondă:** parcurge
traseul cu Playwright (login → navighează → verifică câmpul nou → submit), nu doar `node --check`/verificator.
**Verdict:** ecran accesibil + interacțiune reală probată. Fără ecran accesibil, funcționalitatea nu există.

### F5 — Mesajele de blocaj/refuz (limba contabilului) — Regula 14.4
**Întrebarea:** ce scrie pe ecran când provoci un refuz? **Sondă:** alimentează **date greșite / câmpuri
obligatorii neîndeplinite** și citește mesajul rendat. **Verdict — sunt defecte:** numele intern al câmpului sau
valorile din bază arătate utilizatorului; mesajul generic pus peste explicația precisă; eroarea care nu marchează
câmpul vinovat; textul fără diacritice; obligativitatea semnalată abia după apăsarea butonului; **motivul livrat
doar prin `title`** (pierdut pe touch). Mesajul trebuie să spună: ce lipsește/e greșit, unde se corectează, ce
consecință are (care declarație se blochează).

### F6 — a11y vizual + mobil (pe fiecare ecran atins) — Regula 14
**Întrebarea:** ecranul e citibil și utilizabil, pe desktop și pe telefon? **Sonde:** `frontend_test/vizual/` —
`axe_scan.py` (contrast, etichete, title-only), `scan_region_all.py` (landmarks/region), `mobil_scan.py` (Pixel5:
țintă atingere <24px AA 2.5.8, hover-pierdut pe touch, revărsare orizontală), `baseline_scan.py --compare` (diff
pixel). **Verdict:** contrast=0, region=0, ținte <24px=0, fără info livrată exclusiv prin hover/title, fără
revărsare. Captura **privită**, nu doar selectorul trecut.

**Automatizat + GĂRDAT:** `frontend_test/vizual/interactiune_scan.py` rulează axe pe **desktop ȘI mobil** (combinația prinde `scrollable-region-focusable`, care apare doar când conținutul depășește viewportul) + țintă<24 + F9 → scrie `acoperire_vizuala.json`; `core/test_acoperire_vizuala.py` **pică** dacă UI-ul s-a schimbat fără re-scan curat.

### F9 — Comportament sub interacțiune (ce NU e aparent) — Regula 14 (cerut de Costin, 19.08.2026)
**Întrebarea:** dacă apeși butoanele ecranului, se strică ceva? dacă completezi casetele cu text la limită, se
trunchiază textul / se rupe alinierea? **Sondă:** `frontend_test/vizual/interactiune_scan.py` — apasă butoanele
din conținutul ferestrei (ne-destructive, cu re-navigare ca să le acopere pe toate) și prinde erori JS de consolă
+ rupturi de layout; umple fiecare casetă cu text lung + diacritice și prinde revărsarea orizontală + elementele
împinse dincolo de viewport (aliniere ruptă / text împins afară). **Verdict:** zero erori de consolă la apăsare,
zero layout rupt, zero revărsare / element peste viewport la completare. **Aparentul (F6: contrast/diacritice/
culori) NU acoperă comportamentul** — se verifică amândouă, mereu.

### F7 — Registrele la zi
**Întrebarea:** semaforul / vectorul fiscal reflectă realitatea? **Sondă:** compară cifrele afișate (restanțe,
„de depus") cu faptele (venituri, operațiuni, plăți) pe date reale. **Verdict:** cifrele coincid (Regula 14.2 —
totalul = suma rândurilor; previzualizare = buton = rezultat); nicio restanță falsă, nimic stătut. Când o coloană
are aceeași valoare pe toate rândurile, oprește-te și verifică la sursă dacă e reală sau fabricată.

### F8 — Gărzile (închiderea buclei)
**Întrebarea:** ce am reparat, rămâne reparat? **Sondă:** pentru fiecare regulă nouă, gardă RED-probată (P5),
simultan în cod + verificator; rând în `FUNCTIONALITATI.csv` dacă e funcționalitate. **Verdict:** poarta verde
(suita + verificator 0 roșu); four-way după poartă (publish origin + backup + restart iconta-nou, start-time >
commit).

---

## Cum se aplică tuturor tenanților

1. **Un tenant pe rând, cap-coadă.** Parcurgi F1→F8. Perimetrul e tot ce atinge obiectul (cod, date, ecrane,
   registre, gărzi, temei), nu doar numele din comandă.
2. **Tiparul, nu cazul (P3).** Când un defect găsit la un tenant are tipar (ex. „motiv title-only", „flex-shrink
   strivește input în fereastră largă", „region orfan în shell"), reparația e **app-wide** — se rezolvă o dată în
   shell-ul comun și profită toți tenanții. Astfel de fixuri se notează ca „Global" în `ISTORIC_TENANTI.md`.
3. **Ce nu se poate verifica se raportează (Regula 12).** La final, raportează doar: ce depinde de un răspuns
   extern pe care nu-l poți obține; ce cere o alegere de produs (nu de corectitudine); ce ai văzut dar nu poți
   verifica din cod. Perimetrul e tot restul — nu se „raportează ca rămas" ce ținea de audit.
4. **Estimarea la început, predarea la oprire (Regula 15).** La început spui cât estimezi că apuci; la oprire,
   prima linie din `PREDARE_LANT.md` e comanda exactă de repornire, iar `ISTORIC_TENANTI.md` primește rândul turei.
5. **Metoda e POARTĂ, nu doar document (Costin, 19.08.2026).** F6 + F9 sunt cuplate mecanic de diff prin
   `core/test_acoperire_vizuala.py`: orice schimbare de UI (`static/js/**.js` + `stil.css`) invalidează scanul
   (ui_hash) și pică suita până rulezi `frontend_test/vizual/interactiune_scan.py` și comiți artefactul curat.
   **Nu te poți abate:** o regulă scrisă și citită NU e o regulă păzită — doar poarta ține (ca `test_agenda` /
   `test_versionare_assets`). Se folosește INSTRUMENTUL standard, nu probă ad-hoc.

---

## Selftest al modelului — CONSTRUIT: `frontend_test/audit_tenant.py <tenant_id> [--fara-vizual]`
Orchestrator care rulează fațetele automatizabile și tipărește un raport per fațetă cu verdict verde/roșu (iese 1 pe roșu):
- **F2** — pt fiecare declarație datorată/de urmărit din semafor: generează + `DUKIntegrator` (valid/erori/gri); un refuz
  pe zero (422) = semnal de posibilă restanță falsă (către F7).
- **F7** — starea semaforului + constatările ROȘII (motivul, nu doar culoarea).
- **F6** — descoperă ecranele accesibile ale firmei (`button.firme-optiune[id^=fa-]`) și rulează pe fiecare, desktop +
  Pixel5: axe (contrast, region/landmark, etichetă) + țintă atingere <24px + revărsare. Navigare PROASPĂTĂ per ecran.
- **F3 / F5** rămân MANUALE (cer date deliberat greșite + citirea ecranului) — scriptul le listează ca reminder.

Autentificare: userul `fe_test` (vede firmele cabinetului lui de test). Pentru un tenant din alt cabinet, orchestratorul
are nevoie de credențialele acelui cabinet (de parametrizat când e nevoie). Probat 18.08 pe ALFA MICRO (8396): F2 DUK
valid pe D300/D112, F7 constatări roșii reale, F6 a scos contrast/etichetă pe ~8 ecrane (control, jurnal, bancă,
etransport, centrecost, stocuri, registratura, rapoarte) — backlog a11y app-wide de reparat cu tiparul (P3).
