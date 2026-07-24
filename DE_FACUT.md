# iConta — DE FĂCUT

**Doar viitorul: ce e deschis. Când termini, ștergi rândul. Trecutul e în ISTORIC.md + git log.**
Ultima actualizare: 13.07.2026 seara (partea 5)

---

## 1. Testare pentru pilot (din planul P1-P5, orientat business)

### Prin SSH — deja acoperit tehnic (NU relua): zonele 8,9,11,12,13,14,15

### Cere Daniela [D] — validare fiscală, sesiuni 2h
- P1.2 Flux lunar complet pe KAI: e-Factura + extras → reconciliere → jurnal → balanță → D300 → validare ANAF
- P1.3 Salarizare: salariat nou → stat plată → **fluturaș → D112 validat** (acum și cu Concediu Medical nou!)
- P2.6 TVA la încasare: factură + încasare parțială → 4428→4427 proporțional
- P2.7 Operațiuni speciale (5 eșantion): leasing, avansuri, sponsorizare, dividende, provizioane
- P2.8 Partidă simplă: import bancă → Fișă D212 (vs calcul manual)

### Cere Costin singur [C] — DONE 14.07
Rulate 14.07 (vezi jos "Actualizare 14.07" → RAMASE): P1.1, P1.4, P1.5 (simulat), P2.9-P2.11, P5.24.
Backup automat LIVE (systemd timer zilnic 03:00, retentie 7z). Raman deschise doar [D] si [T].

### Cere telefon [T] — după HTTPS (nou.iconta.eu e sus)
- P4.18 PWA: (FACUT iOS 14.07 - standalone+offline OK) ramas doar Android, verificare secundara
- P4.19 Pozează bon: cameră, multi-imagine, flux până la notă
- P4.20/21 Responsive portal <400px, landing <900px/<560px

## 2. Blocate — DUK / desktop ANAF
- (REZOLVAT, arhivat 17.07) D394 valideaza acum headless prin core/duk.py (jar, nu GUI desktop) —
  blocajul "validare desktop" nu mai exista (duk.py:154 "dovedit 15.07", CLAUDE.md status 16.07).
  Nimic blocat pe desktop-DUK azi. (e-Transport prin API SPV = blocaj extern SPVWS2, tracked in CARENTE.)

## 3. Sesiune desktop (Word, nu SSH)
- (PARTIAL) Audit design 12.07: INCHISE (canonic + verificator TOTAL 0 pe toate 30 ecrane): formatare bani/data/procent, culori-card, iconite, tipografie, culori/borduri/raza. Design System v2.9 + verificator 9 reguli, la zi.
- RAMAS DIN AUDIT DESIGN (nefacut):
  1. Verificare VIZUALA doar ~10/30 ecrane. De vazut cu ochii restul ~20 (declaratii, control, termene, setari, recomanda, admin*, etransport, produse, tipare, semafor, validat, pachete, capacitate) - verificatorul e curat pe ele dar nu prinde tot.
  2. Categorii NEATACATE: spacing/padding/gap inline (fara inventar inca); wrapper alb pe formulare (cap.2 - verificatorul n-are regula, prins doar 1 manual); aliniere tabele (cap.4 sume la dreapta, neverificata sistematic); anatomia ferestrei (cap.1 entitate-antet/titlu-h2-corp, neauditata vizual).
  3. TASK 0a mai vechi (cerut 10.07, inca nefacut): audit cod mort + functionalitati ascunse ad-hoc fara conditie documentata + diferente cabinet/client inconsecvente.

## CARENTE — inventar (consolidat 13.07.2026, curatat 17.07.2026)
Curatenie 17.07: 7 intrari confirmate rezolvate prin verificare la sursa (grep/test) mutate in
ISTORIC.md, sectiunea "REZOLVARI CONFIRMATE 17.07 (verificate retroactiv)". Raman deschise, cu
starea reverificata azi:
1. **e-Transport — trimitere directa prin API SPV**: exista generarea XML pentru upload MANUAL in
   SPV (core/etransport.py: xml_notificare); trimiterea directa prin API SPV NU exista — blocaj
   extern SPVWS2 (acelasi blocant ca restul apelurilor SPV). Verificat 17.07: etransport.py are
   doar xml_notificare, nicio functie de trimitere.
2. **Testare pilot P1-P5**: partial. [C] (Costin) rulate 14.07 (P1.1/P1.4/P1.5-simulat/P2.9-2.11/
   P5.24) + PWA iOS (P4.18). RAMAN: [D] validare fiscala cu Daniela (P1.2/P1.3/P2.6-2.8) + [T] telefon
   (P4.19 pozeaza bon, P4.20/21 responsive, Android). Checklist manual, neverificabil prin cod.
3. **Audit design ramas**: spacing/padding inline (inchis explicit ca datorie acceptata), migrare
   paleta iconite (decizie amanata), anatomia ferestrei + alinierea tabelelor nesistematizate vizual
   (~20/30 ecrane nevazute cu ochii; verificatorul e curat pe ele dar nu prinde asezarea).
   **Inventar 19.07 (harta DS acoperit/manual):** verificatorul = regex pe linii, scaneaza doar
   static/js/ecrane/*.js -> prinde SEMNATURA TEXTUALA, NU randarea. 28 gardieni (2 noi 19.07: ESC_LOCAL
   cap.10 securitate + CASETA_ATENTIE cap.5). **9 reguli DS RAMAN verificare vizuala manuala** (randat/
   comportamental, neautomatizabile): aliniere tabele (cap.4), anatomia ferestrei (cap.9), contrast randat
   gri-pe-gri (cap.16/5), nimic-vizibil-decat-la-selectie (cap.2), navigare/setInapoi (cap.3), feedback
   butoane (cap.1), structura semafor (cap.8), mesaje de stare semantice (cap.6), tabele PDF (cap.7).
   Ecrane post-14.07 NEVERIFICATE vizual: control fiscal, e-Transport, SPV/gratuit, WinMentor UI.
   **3 candidati de automatizare RESPINSI (fals-pozitive, nu se automatizeaza):** (a) card-inactiv fara
   'activ' cap.2b - semnatura {cheie:...desc:...} partajata cu pasi wizard migrare (nr:), line-regex nu
   distinge cert; (b) panou gri-pe-gri cap.16 - vizibilitatea depinde de parinte (panou alb vs corp gri) +
   bordura, context necunoscut de regex (3 apariti background:var(--fundal): operatiuni:266+portal:424 au
   bordura=vizibile, firme:1187 <pre> erori ambiguu - de privit vizual, nu clar violari); (c) background/
   border hex ad-hoc cap.15 - prea multe bg-uri inline legitime, fals-pozitiv. Raportate, nu gardian.
4. **Inventar declarații LIVE vs. accesibile din UI** (constatat 23.07 la închiderea poziției 1 CHECKLIST_BROWSER):
   un motor de declarație poate fi LIVE în backend dar fără intrare din interfață. Cazuri consemnate azi:
   **D710 LIVE dar inaccesibil din UI**; **D301 fără writer** (contabilul nu poate introduce operațiuni IC din
   aplicație — vezi și ISTORIC 23.07 poz.3, gap D301). DE FĂCUT: inventar sistematic care declarații LIVE au / n-au
   cale din UI, ca să nu existe capabilități moarte pentru utilizator. Sursa motoarelor: `core/declaratii_api.py`.
5. **Formator de dată local care ocolește DATA_DIALECT** (constatat 24.07 la investigarea `ecranVerificari`,
   `firme.js`): antetul „Verificări" formatează perioada cu `${String(luna).padStart(2,"0")}/${an}` (luna/an
   compus manual) în loc de `dataRo(...)` — încalcă DS cap.4, dar garda DATA_DIALECT nu-l prinde (caută
   `luni[...]`/`toLocaleDateString`/`split("-")`, nu forma `padStart`). Separat de consolidarea verdictului
   (neatins azi). DE DECIS: (a) reparație punctuală → `dataRo("luna_an")`; (b) extindere DATA_DIALECT să prindă
   forma `padStart(...)/${an}` (risc de fals-pozitiv pe alte `padStart`). O regulă nouă intră simultan în DS + verificator.
6. **Salutul asistentului folosește `u.nume` (nume de familie) în loc de `u.prenume`** (constatat 24.07 la deblocarea
   accesului Setări pentru asistent, `asistent.js:32`): `const prenume = u.nume || u.email` → antetul afișează
   „Salut, {nume de familie}". Aceeași familie cu etichetarea inversată Prenume/Nume din Setări (confuzie nume/prenume).
   Neatins azi (temă separată). DE FĂCUT: `u.prenume || u.nume || u.email` (fallback la nume dacă prenumele lipsește),
   reparație punctuală în `asistent.js`.
7. **Gating admin inconsecvent — `Depends(cere_rol("superadmin"))` vs. `cere_cabinet` + gardă inline** (constatat 24.07
   la investigarea poziției 6 Admin, `main.py`): rutele `/admin/*` sunt gate-uite pe două tipare, ambele corecte azi —
   (a) prin dependință `Depends(cere_rol("superadmin"))` (`/admin/anunturi`, `/admin/alerte-fiscale`); (b) prin
   `Depends(cere_cabinet)` + `if ctx["rol"] != "superadmin": raise 403` în corp (`/admin/sanatate*`,
   `/admin/activitate/cabinete`, `/admin/cabinete/{id}/suspenda|reactiveaza`, `/admin/conturi-gratuite`). **NU e
   vulnerabilitate** (toate verifică efectiv superadmin), **risc mic**. Dar tiparul (b) e FRAGIL: o rută admin nouă
   copiată din șablonul `cere_cabinet` care uită linia inline ar fi tăcut expusă oricărui non-client (inclusiv
   `suspenda cabinet`). DE FĂCUT (amânat, nu reparat azi): standardizare pe `cere_rol("superadmin")` sau helper
   `cere_superadmin`. Niciun gardian nu-l prinde (backend, nu DS) — dacă se repară, eventual o gardă mecanică pe
   rutele `/admin/*` fără gate superadmin explicit.
8. **Logica „bulină roșie = fără răspuns" din Raportări (Admin) neverificată vizual — lipsă date de test** (constatat
   24.07 la închiderea poziției 6): ecranul Admin → Raportări (`admin_raportari.js` + `/raportari/admin`) marchează
   sesizările fără răspuns cu bulină roșie, dar nu există nicio sesizare în sistem, deci starea „fără răspuns" n-a
   putut fi produsă la verificarea vizuală pe superadmin. NU e bug cunoscut — doar neverificat. DE FĂCUT: creează o
   sesizare de test (sau așteaptă una reală) și confirmă vizual bulina roșie + tranziția la „cu răspuns".
9. **[SECURITATE — nu UI] Poarta `BETA_COD_ACCES` ocolită complet + oracol de credențiale la login** (constatat
   24.07, `main.py`; verificat la sursă):
   - **Finding A — bypass total prin magic-link.** `BETA_COD_ACCES` se verifică într-un SINGUR loc: `/auth/login`
     (main.py:998), după validarea parolei. Căile publice `/public/magic-link` (1236) + `/public/magic-login` (1262)
     emit **sesiune completă FĂRĂ** verificarea codului. Orice titular de cont **activ** își cere un link pe email și
     intră, ocolind poarta. Anulează scopul porții („site în lucru") pentru exact populația vizată (conturi existente
     valide). Nu dă acces non-titularilor (magic-link cere user activ + acces la inbox), dar golește poarta de sens.
   - **Finding B — oracol de credențiale.** Poarta e DUPĂ verificarea parolei: credențiale greșite → `401`; corecte +
     fără cod → `403 "Site in lucru"`. Răspunsul distinge perechile email+parolă **valide** (403) de invalide (401)
     chiar fără codul beta → scurgere de validitate credențiale. (Enumerarea de email e evitată corect la magic-link,
     dar nu aici.)
   NEREPARAT azi (cerut explicit). PROPUNERE (neimplementată) — **opțiunea 1: mută poarta la reverse proxy** (nginx
   basic-auth / IP-allowlist): acoperă TOT (inclusiv `/public/*`), fără găuri per-rută și fără oracol; `main.py` scapă
   de preocuparea de infra. Alternativă (opțiunea 2): aplică `BETA_COD_ACCES` pe TOATE căile de emitere a sesiunii
   (+`magic-login`) ȘI repară oracolul (același răspuns pt parolă greșită vs. parolă bună fără cod, sau poarta ÎNAINTE
   de credențiale) — necesară doar dacă unele `/public/*` (ex. magic-link) trebuie să rămână deschise intenționat.
10. **[UI, prioritate mică] Mesaj generic „A apărut o eroare" în modul previzualizare admin (read-only)** (constatat
   24.07 la închiderea poziției 5, `portal.js:456`): în previzualizarea portalului client (F197, read-only, accesată
   prin Facturare gratuită → previzualizare cont, DANTE), acțiunea client „Recomandă" (POST `/portal/recomanda`) e
   blocată **intenționat** de middleware-ul read-only → catch-ul generic afișează „A apărut o eroare. Încearcă din
   nou." Acțiunea e dezactivată corect, dar mesajul NU comunică asta (ar trebui „dezactivat în previzualizare").
   DE VERIFICAT altă dată: (1) dacă ALTE acțiuni din modul previzualizare afișează același mesaj generic în loc de unul
   explicit „dezactivat în previzualizare"; (2) restul ecranului **Facturare gratuită** (admin), netestat azi dincolo
   de acest caz particular. Prioritate mică (nu blochează, doar UX de mesaj).
11. **[DECIZIE DE PRODUS — nu bug tehnic] e-Transport `/trimite` + `/trimiteri` pe `cere_context` (inclusiv client)
   vs `etransport-xml` pe `cere_cabinet`** (constatat 24.07, main.py:5979/6009 vs 5956): `/tenants/{id}/etransport/trimite`
   (submit SPV, F121) și `/etransport/trimiteri` (listă) acceptă orice rol autentificat cu acces la tenant, **inclusiv
   `client`**; `etransport-xml` (generare XML) e cabinet-only. **NU e cross-tenant** (`schema_tenant` enforced inline),
   **NU e reachable din UI azi** (ecranul e doar în meniuFirma cabinet; portalul client nu-l are). ÎNTREBAREA DE DECIS
   (produs, nu reparație tehnică): clientul ar trebui să poată trimite **singur** notificări e-Transport la SPV —
   analog dreptului legal de reprezentant care depune declarații fără contabil — SAU restrâns la cabinet ca
   `etransport-xml`? Dacă decizia e „restrâns" → `trimite`/`trimiteri` devin `cere_cabinet` (aliniat cu sibling-ul).
   Rămâne decizie de scop. Familie apropiată de CARENTE 7 (gating inconsecvent), dar aici întrebarea e de DREPT, nu de robustețe.
12. **[FISCAL] Validare XSD offline e-Transport BLOCATĂ — lipsă schema v2** (constatat 24.07 la implementarea guard-ului
   de câmpuri required): aplicația generează XML eTransport **v2** (`mfp:anaf:dgti:eTransport:declaratie:v2`), dar
   singurul XSD local e **v1** (`~/duk/xsd/etr/SchemaSimtic_20230126.xsd`, `targetNamespace=…declaratie:v1`), **structural
   diferit** — dovedit cu lxml pe exemplul oficial v2: atribute transport redenumite (`codOrgTransport` v2 vs
   `codTaraTransportator` v1), elemente locație redenumite (`locStartTraseuRutier` v2 vs `locIncarcare` v1), enum
   `codScopOperatiune` (`101` v2 vs 6 cifre `100101…` v1). Validarea v2 pe XSD v1 e **imposibilă**. Guard-ul de PREZENȚĂ
   a câmpurilor required (`core/etransport.py:campuri_required_lipsa`, client+backend) e LIVE și acoperă cazul găsit
   (codTarifar/denumire goale), dar **NU** e validare completă de schemă (nu prinde enum-uri invalide, formate, tipuri).
   DE FĂCUT: obține XSD-ul eTransport **v2** de la ANAF (`static.anaf.ro` / SPV) → validare `lxml.etree.XMLSchema` la
   generare, ca plasă autoritară. Sursa DUK (`~/duk`) are doar v1.
13. **[UI/FISCAL — sesiune dedicată, verificare vizuală pe fiecare ecran ca la poziția 7] Asteriscuri fără enforcement**
   (audit 24.07, sweep 10 ecrane). Regula: DS cap.6 — „Niciodată tăcere la o acțiune eșuată" + „Validări preventive cu
   mesaj explicativ". Cazuri verificate la sursă:
   - **[C — PRIORITAR] emitere_ecran.js L131/L352** — „Denumire beneficiar" cu asterisc, `tert_nume: …||null` fără
     check; `emite_factura` (facturi_api.py:195) validează DOAR `linii`. Rezultat: **factură emisă „cu succes" fără
     beneficiar** (clonă etransport, pe document fiscal). PREREECHIZIT înainte de a decide garda: **verificare la sursă
     Cod fiscal art.319 alin.(20)** — elementele obligatorii ale facturii — ca să decizi gardă pe `client_id` SAU
     `tert_nume`. Fix-ul trebuie să acopere AMBELE moduri de emitere (client salvat + terț one-off).
   - **[B] rip_ecran.js L103** — zero validare client-side; backend respinge vizibil (`rip_api.py:30/32`, OMFP 170/2015).
     Doar UX preventiv lipsă.
   - **[B] login.js L428/L514** — asterisc pe CUI, absent din pre-check-ul client; backend înregistrare îl prinde. UX
     preventiv.
   - **[minor]** `0` acceptat pe câmp numeric cu asterisc: emitere `pret_unitar`, rip `suma`, flux_concediu `data_sfarsit`.
   - **[C2 — clasă distinctă] produse_ecran.js L138-146 (`#pr-salveaza`)** — `denumire` e blocat, dar refuzul e TĂCUT
     (`focus()+return`, fără `arataMesaj`) ȘI câmpul nu e marcat cu asterisc (`.oblig`/`*`). Invers față de cazurile de mai
     sus: acolo asterisc fără enforcement, aici enforcement fără mesaj și fără asterisc. Ambele goluri cap.6. Fix: asterisc
     + `arataMesaj "eroare"`, ambele.
   - **[minor] produse `pret_unitar: parseFloat(...)||0`** — 0 acceptat. `pret_unitar` alimentează F144 (profit pe produs);
     la reparare de verificat dacă 0 falsifică marja sau e legitim.
   - **[candidat, NEDECIS]** gardian mecanic în verificator pentru cap.6 („ecran cu asterisc + `api.post` fără validare
     de câmp") — risc mare de fals-pozitive, temă separată.

## Editare produs — UI lipsă (24.07)
- **PUT `/tenants/{id}/produse/{produs_id}`** (main.py:2224) există în backend **fără consumator frontend**. Marcatorul
  `[p123_scot_butoane]` din `ecrane/produse_ecran.js` **nu e documentat nicăieri**: absent din DECIZII.md / ISTORIC.md /
  DE_FACUT.md / CHECKLIST_BROWSER.md, prezent doar în snapshotul inițial `cbf24ce` fără commit incremental, absent din
  build-ul vechi `/opt/iconta` (altă arhitectură, fără ecran de produse). Istoric pierdut la snapshot, motiv nerecuperabil.
- **DECIS 24.07**: endpoint-ul **NU e cod mort** — se păstrează, se construiește UI de editare. **Temei (CORECTAT 24.07,
  verificat la sursă)**: ștergerea+recrearea pierde metadata cotei — `justificare`, `categorie`, `sursa`, `confirmat`
  (`produse` L969), rezultatul potrivirii AI și argumentul la un control fiscal; editarea (denumire, preț de listă, cotă
  TVA) e legitimă și trebuie s-o păstreze. **CORECȚIE**: temeiul inițial (`articol_id` în podul factură→stoc + F144) e
  FALS — `produse` și `articole` sunt tabele complet separate, fără FK în niciun sens; `DELETE FROM produse` nu atinge
  niciun istoric. Formulat din memorie, neverificat (încălcare regula 7 — verificare la sursă). Decizia rămâne, temeiul e altul.

## 4. Infra
- **Reboot kernel** — inca necesar (verificat 17.07: /var/run/reboot-required prezent; ruleaza
  6.8.0-117, in asteptare 6.8.0-124/-134). Fereastra linistita (downtime clienti, Daniela pilot).
  (systemd 8010 REZOLVAT 13.07 — arhivat, vezi ISTORIC:17 "iconta-nou.service enabled".)
- **Cache-Control immutable pe asset-uri versionate `?v=`** (optimizare, NU blocant). Azi 21.07 s-a scutit `/static/`
  de rate limit nginx (regresie config nou-iconta → 429 pe module ES → pagină albă; vezi DECIZII/ISTORIC 21.07). Secundar:
  `_StaticNoCache` pune `Cache-Control: no-cache` → browserul revalidează fiecare modul la fiecare load (cerere la
  server chiar și pt 304). Pentru fișierele cerute cu `?v=N` (URL unic per versiune) s-ar putea servi `Cache-Control:
  public, max-age=…, immutable` → browserul nici nu revalidează → taie zeci de cereri per load. Neversionatele
  (app.js, sesiune.js, index.html) rămân `no-cache`. Câștig: mai puține cereri + load mai rapid. Nu urgent — rate
  limit-ul e deja rezolvat prin exceptare.

## 5. Iterații viitoare (nu urgente)
- **Breadcrumb/subtitlu preview „Facturare gratuită"** — deschis 21.07 (audit vizual F197). În preview-ul
  portalului client, când contul e gratuit (fără cabinet) subtitlul arată „Facturare gratuită"; de verificat că
  breadcrumb-ul/antetul din modul preview nu induce în eroare cabinetul (e portal client, nu contul gratuit al
  cabinetului). Cosmetic, necesită privit cu ochiul pe cazul gratuit real.
- **Nume fișier la descărcarea balanțelor** — deschis 21.07. De uniformizat numele fișierului descărcat (balanță)
  cu tiparul celorlalte exporturi (`export_<tip>_<an>_<luna>`), ca la SAGA/WinMentor. Minor, de confirmat vizual.
- **Mesaje de eroare `.mig-gol` -> `arataMesaj`: FACUT 18.07 (48/53).** Cele ~50 utilizari `.mig-gol` din blocuri catch/validare/loading convertite la `arataMesaj(zona, txt, tip)` (eroare/avert/info) in rip_ecran/operatiuni/etransport/cabinet/migrare/firme/facturi_ecran. RAMAN 5 template-embedded (NU catch, HTML in template - lasate deliberat, nu se ghiceste): asistenti.js:330 (ternar in render), firme.js:428 (eroare conditionala inline in panou), :1315 (ramura ternar `${r.mesaj}`), :1343 (lista .map de mesaje - continut, nu feedback), :1689 (nota permanenta 'Atentie: nota legata de factura'). Verificator TOTAL 0. LIMITA: caile de eroare din catch nu au fost declansate runtime (greu de atins) - conversie mecanica + node-check + aliniere cu tiparul arataMesaj existent in app.
- **Export către programul contabilului — SAGA (F171) + WinMentor (F187) LIVRATE; Ciel BLOCAT pe spec.**
  SAGA (F171 18.07): facturi emise în XML propriu, format de la manual.sagasoft.ro topic-76.
  WinMentor (F187 19.07 LIVE): două fișiere INI (Facturi.txt + Articole.txt) co-locate, structură de la
  sursa OFICIALĂ (download.winmentor.ro/.../22 Structuri import, Facturi clienti.pdf Rev.1.2 + Articole noi.pdf),
  encoding Windows-1250 cu gard, cod articol derivat consecvent. NU e self-contained ca SAGA — dependență de
  config nomenclator WinMentor al cabinetului (clasă/gestiune/UM); v1=servicii, stoc complex=v2. Vezi DECIZII 19.07.
  LIMITA (ambele): round-trip real (import efectiv) pending cabinet real — cod+spec verificate, necolorat verde live.
  (Excluderea 'anulata'/'storno' din export = RESPINS 21.07: facturile n-au acel status, iar ascunderea notei de
  credit ar rupe contabilitatea din programul destinație. Temei complet în DECIZII 21.07.)
- **Ciel — BLOCAT PE SPECIFICAȚIE (NU planificat orb).** 3 necunoscute verificate la sursă 19.07: (1) versiune —
  Ciel v6/v7/NextUp au formate DIFERITE (facturis.ro); (2) spec neclar publică (nu există portal oficial ca
  WinMentor); (3) cere coduri ANALITICE pe care iConta poate să nu le aibă la granularitatea Ciel. Se deblochează
  DOAR cu specificația de la sursa Ciel / un cabinet real care importă în Ciel. NU se construiește pe sursă
  secundară (ar rupe importul, ca BR-RO). [BLOCAT]
- **Igienă cont gratuit / CUI dublu emitent — ACOPERIT de F092 (coliziune_gratuit_v1) + F185 (gardul invers).**
  Verificat la sursă 19.07. Preluarea tenant = create-new e CORECT (contul gratuit e unealtă de emitere, nu sursă
  contabilă; datele reale vin prin migrare — DECIZII commit afd67d9, retenție 1 an). Riscul „același CUI emite din
  două locuri (gratuit + cabinet)" e DETECTAT + gestionat, NU restanță deschisă:
  - **F092 (18.07, direcția gratuit→cabinet):** la crearea tenantului de cabinet pe un CUI care are cont gratuit
    activ, se SEMNALEAZĂ cabinetului (tenant_creeaza + migrare_importa). Poartă enforcement: cont gratuit suspendat
    (activ=false) nu poate fi selectat/emite (auth_api.py:335). Închidere = superadmin (/admin/conturi-gratuite/
    {id}/suspenda). Auto-close RESPINS explicit (GDPR — deținătorul decide).
  - **F185 (19.07, direcția inversă cabinet→gratuit):** register gratuit pe un CUI deja sub cabinet → semnal
    simetric la înregistrare (inregistreaza_cont_gratuit), tot fără blocaj/auto-close.
  REZIDUAL: vizibilitate persistentă (raport superadmin de coliziuni active) = PLANIFICAT mai jos, nu gard critic.
- Cod 10 CM (reducere timp muncă, art. 19) — INTEGRAT, nu mai e iterație viitoare (corectat 17.07:
  nota veche "exclus din dropdown, `calcul_cm_cod10` neintegrat" era contrazisă de cod). Dovadă:
  `calcul_cm_cod10` definit (salarizare.py:208) + apelat în flux real (salariati_api.py:222) + în
  dropdown (flux_concediu.js:14) + câmp venit condiționat (:105) + testat (test_salarizare.py).
  Vezi ISTORIC "REZOLVĂRI CONFIRMATE 17.07".
- **F133 tichete/bilete de valoare — Faza 1 (masă) + 2a (vacanță) + 2b1 (cadou neimpozabil) LIVE; RĂMÂNE 2b2.**
  Închise 20.07 (stat+fluturaș+monografie+UI+D112 unde e cazul; detaliu ISTORIC 20.07 + DECIZII). **Deschis: Faza 2b2 —
  cadou TAXABIL (>300 lei/eveniment sau eveniment nelegal).** În 2b1 se SEMNALEAZĂ roșu pe stat dar NU se taxează automat
  (contabilul tratează manual până la 2b2). 2b2 = chirurgie pe calcul_salariu + D112: DIFERENȚA peste prag (nu toată suma)
  se taxează INTEGRAL ca salariu (CAS 25% + CASS 10% + CAM 2.25% + impozit 10%, adăugată la brut) — pistă diferită de
  masă/vacanță (care e doar CASS+impozit). AMÂNAT deliberat la caz real (rar); vezi DECIZII 20.07 F133 Faza 2b1. [PLANIFICAT]
  RESIDUAL 2b1: multiplicatorul per copil minor la plafon (300 × (1+copii)) — nemodelat, tot 2b2/temă separată.
- **F134 plata salariilor pe card (fișier SEPA pain.001) — LIVE 20.07; RĂMÂNE round-trip bancă reală.**
  Generatorul ISO 20022 pain.001.001.03 e LIVE (commit-uri a93e4f3 + f240054; detaliu ISTORIC 20.07 + DECIZII
  20.07 F134): sumă = net cash, IBAN salariat cu validare mod-97, salariați fără IBAN excluși+raportați, XML
  validat pe XSD-ul oficial înainte de download. **Deschis (necolorat verde live): importul REAL într-o bancă
  anume** — round-trip pe platforma corporate a băncii pilot, de dovedit cu un cont bancar real. Aceeași natură
  ca limita SAGA/WinMentor (jos): cod + XSD verificate la sursă, dar nu importat efectiv într-o bancă. NU e
  blocaj de construit — e probă cu bancă reală. Reziduu: doar RON domestic (RO IBAN); plăți în valută/IBAN
  străin = temă separată dacă apare cazul.
- **F137 coduri COR pe contracte — LIVE 20.07; RĂMÂNE refresh snapshot la ordin nou + flux REGES contract.**
  Nomenclator COR național validat e LIVE (commit bf9cbd3; detaliu ISTORIC 20.07 + DECIZII 20.07 F137):
  public.cor_ocupatii cu 4422 ocupații din fișierul oficial data.gov.ro (Ordin 573/180/2024), lookup căutabil +
  validare la salvare. **Deschis:** (1) nomenclatorul e un SNAPSHOT — la un ordin nou de actualizare COR se
  rerulează `cor_incarca.py` cu fișierul nou (întreținere periodică, nu bug); (2) fluxul REGES `AdaugareContract`
  (care trimite codul COR + versiunea la ANAF) NU e încă cablat — `mesaj_adaugare_contract` există în
  reges_client.py dar nu e apelat; când se cablează, ia codul din salariatul deja validat. NU e blocaj — extindere.
- **F125 clasificare manuală D390 — LIVE 21.07; RĂMÂNE (opțional) marcaj tip pe factură.**
  Reclasificare + adăugare e LIVE (commit-uri 6ead435 + ff272aa; detaliu ISTORIC 21.07 + DECIZII 21.07 F125):
  contabilul reclasifică operațiunile auto (L/A → P/S/T/R) + adaugă linii manuale, pe pasul 2 al D390, persistat,
  fără dublă numărare, validat DUK. **Deschis (opțional, scop mai mare — NU blocaj):** marcajul `tip_d390` direct
  pe factură (la emitere/editare), ca D390 să citească tipul din factură în loc de reclasificare per-perioadă.
  Amânat deliberat — atinge modelul de facturi + fluxul de emitere; reclasificarea per-perioadă acoperă nevoia acum.
- **F120 educație AI pe tipare — LIVE 21.07; nimic critic deschis.**
  Analiza generativă AI pe ecranul G (Tipare de erori) e LIVE (commit a557889; detaliu ISTORIC 21.07 + DECIZII
  21.07 F120): buton „Generează analiză AI" → Claude explică tiparele de respingere + recomandări, grounded pe
  agregatele F094, on-demand, doar patron. **Deschis (mic, opțional):** analiza nu se persistă (se regenerează la
  cerere) — dacă se dorește istoric al analizelor AI, e o extindere; nu blocaj. Analiza e sugestie, nu verdict.
- (VERIFICAT vizual 21.07.2026) raporteaza.js — data "cu_ora" în feed afișează corect dată+oră completă
  ("21.07.2026 12:06") pe fir (`.rap-fir-data`) și pe fiecare mesaj (`.rap-mesaj-data`), prin `dataRo(iso,"cu_ora")`.
  Ecran: dashboard cabinet → card "Suport" → "Sesizările mele". Verificat cu o sesizare de test (ștearsă după).
- (VERIFICAT, curat 21.07.2026) Date CM de test invalide în alte tenant-uri — scanate TOATE tenant-urile
  (doar tenant_001 + tenant_002 există), 0 rânduri în `concedii_medicale` pe fiecare → nimic invalid, nimic de
  șters. Criterii aplicate la sursă (OUG 158/2005): cod ne-numeric (tip „CCMAD") / cod în afara nomenclatorului
  (01-10, 12-15, 17, 51) / imposibil net>0 & brut=0 / salariat orfan / zile≤0 & indemnizație>0. CCMAD-ul corupt
  fusese deja șters din tenant_002.

---

## ANEXA — Inventar functionalitati
Stersa 17.07: era duplicat al FUNCTIONALITATI.csv (registru canonic din 16.07, 164 pozitii cu
ID / Stare / Sursa cod / Temei legal / Testat). Doua inventare = drift garantat. Sursa unica:
**FUNCTIONALITATI.csv**.

## Actualizare 14.07.2026 (sfarsitul zilei)
- INCHISE azi: F113, F152, F153 (gratuit v1+v2), descrieri CSV 103/103, dosarul rutelor 0a, audit vizual complet (~22 ecrane), regresia tenant_template
> NOTA numerotare (19.07): sursa de adevar pentru F-numbers = FUNCTIONALITATI.csv (registrul canonic).
> Planurile de mai jos primisera informal F162/F163/F164/F169, dar registrul foloseste deja acele numere
> pentru features LIVRATE (F162=D112, F163=D390, F164=push control fiscal, F169=control incrucisat TVA).
> Re-numerotate aici la F180+ (peste max registru=179) ca sa nu coliza. Istoria (ISTORIC.md) ramane neatinsa.
- F180 (re-numerotat din F162 — coliziune cu F162=D112 din registru): platitor_tva editat manual vs ANAF -> avertisment la salvare vector fiscal + semafor rosu Control fiscal la divergenta [LIVRAT 22.07.2026]
  Model: snapshot ANAF separat (firma_profil.platitor_tva_anaf + data) + live valideaza_cui la salvarea manuala
  (regim-tva/vector, signal-not-block) + constatare Control fiscal offline (verde/rosu/gri). Verificat fiscal la
  sursa (v9 scpTVA = boolean; TVA la incasare/split = fatete separate). Vezi DECIZII 22.07 F180 + FUNCTIONALITATI.csv.
  RAMAS (enhancement, NU blocant): firma needitata la care ANAF s-a schimbat post-onboarding ramane verde pana la
  o reimprospatare -> cron periodic F184-style care reinterog. ANAF scpTVA pe portofoliu si updateaza snapshot-ul.
  De construit CAND exista semnal real ca se rateaza divergente, nu speculativ. [PLANIFICAT]
- F165: auditor conformitate schema tenant vs template [LIVRAT 22.07.2026] core/audit_schema.py.
  Realizat: motor diff (ref din template in ROLLBACK + introspectie information_schema, normalizeaza zgomotul
  nextval) + poarta (test_audit_schema.py pica la drift template->tenant) + CLI on-demand (python3 -m
  core.audit_schema) care SUGEREAZA SQL (corp migrare_*), NU aplica. Drift curent verificat = ZERO (link_plata/
  sursa_externa deja backfill-uite; nu era "tenant_003/004", inventarul era gresit - doar tenant_001/002 exista).
  RESPINS in implementare (vezi DECIZII 22.07): auto-ALTER (lasa gaura in migrari - suggest-don't-apply);
  whitelist tabele extra (cupleaza la lista extensibila - poarta doar pe directia template->tenant, extra=info);
  ecran superadmin (YAGNI). LIMITA: compara data_type+nullable, NU precizia varchar/numeric si NU default-uri.
- F168: la lansare publica, email automat catre conturile create in perioada beta (site in lucru); sterge BETA_COD_ACCES din env pt acces public [PLANIFICAT]
- F181 (re-numerotat din F163 — coliziune cu F163=D390 din registru): control incrucisat RAMAS D101 / D100 / D394. LIVRAT 19.07: D112=F162, D390=F163 (vezi registru). Text tehnic pastrat: extindere control incrucisat la D112 / D101 / D100 / D390 / D394; acelasi tipar ca TVA. CONSTATARE 15.07 (analiza la sursa): D300 intoarce (xml, res) cu res['R'] = randurile -> comparabil direct. D112 intoarce doar (xml, avertismente) si isi tine agregatele in variabile de structura XML (c2_d14/d15/d16...), NU expune totaluri contabile. Doua cai: (a) parsare XML = fragil, se rupe tacut la schimbare de structura ANAF; (b) d112.genereaza sa intoarca si totalurile (CAS/CASS/impozit/CAM) = refactor pe modul validat DUKIntegrator. Recalcularea paralela din salarizare.calcul_salariu NU e echivalenta (ar compara contabilitatea cu propriul calcul, nu cu ce se declara efectiv - un bug in D112 ar trece neobservat). Conturi tinta (verificate in salarizare.py): CAS=4315, CASS=4316, impozit=444, CAM=436, brut=421. Decizie de arhitectura, nu extindere mecanica [PLANIFICAT]
- F166: parser MT940 (SWIFT) - LIVE 14.07 in banca_parser (marker :61:/:20:). RAMAS: validare pe fisier MT940 real din banca (campul :86: variaza per banca)
- F167: Open Banking automat prin Enable Banking (AIS EU; tier gratuit Restricted Production pt conturi proprii = dogfooding; productie = contract + KYB + cost pe conexiuni). Dupa MT940. Automatizeaza ADUCEREA extrasului, nu doar citirea [PLANIFICAT-etapa-2]
- F183 (re-numerotat din F169 — coliziune cu F169=control incrucisat TVA din registru): audit de PRELUARE firma - LIVE 22.07 in core/audit_preluare.py. CORECTIE la concepția inițială: NU e "același motor control_incrucisat aplicat la migrare" - la preluare ambele surse sunt EXTERNE (documente de la contabilul anterior), nu declaratie-generata-in-iConta vs note-iConta; ruland control_incrucisat pe luna preluata rulaje_luna=0 -> rosu fals pe tot. Deci motor SEPARAT care REUTILIZEAZA anatomia (3 stari + temei + remediu) + verifica_echilibru + coerenta parteneri. v1: balanta + parteneri + istoric-vs-solduri-fiscale + RIP(PFA). Raport datat, repetabil, in fisa firmei (Control fiscal). NEVERIFICAT v1 (ramas gri vizibil): asociati/cote, mijloace fixe, salariati, vector-vs-documente [LIVE 22.07]
- GARD preventiv teste (INAINTE de primul client real): testele NU pot DROP SCHEMA fara prefix de test explicit
  (test_*) sau tid dintr-un range rezervat. Motiv: la testul F185 (19.07), un cont gratuit provizionat de test a
  primit numele reutilizat 'tenant_003' (max-existing+1, nu id-based) - DROP-ul de curatare a fost corect (schema
  FRESH, verificat inainte), dar numele reutilizabil poate induce in eroare. Azi toate datele sunt de test -> fara
  risc; devine OBLIGATORIU la primul cabinet real, cand un DROP gresit ar sterge date reale. [PLANIFICAT]
- RAMASE: teste [C] DONE 14.07 (P1.1/P1.4/P1.5-simulat/P2.9-2.11/P5.24); backup automat LIVE (systemd timer zilnic 03:00, retentie 7z); [D] raman ca teste proprii; blocate extern: F034 D394 DUK, F044 e-Transport API SPV; F154-F161 roadmap gratuit PLANIFICATE; parse-extras de clarificat vs rip/import-banca

## Actualizare 16.07.2026 — re-testare completa a aplicatiei (portiunea SSH)

Toate testele pe date INVENTATE verificate la sursa oficiala (lege/structuri ANAF/DUK),
zero opinii de contabil. Suita: 555 teste verzi. 8 commit-uri.

INCHISE azi:
- **Declaratii 9/9 + bilanturi S1005/S1003 VALID** pe validatorul oficial DUK, izolat SI pe
  date reale (d68dbfc, 6813537, 2d0a943). Vezi git log pentru fiecare.
- **Audit migrare firme noi** cap-coada: 3 arhetipuri (micro/profit/neplatitor), toate
  declaratiile datorate valide. Bug D100 micro reparat (09183e6: cod_oblig era pozitia 5,
  nu codul 121 + cota lipsa).
- **Re-testare zone marcate PASS** (ghidata de churn git, nu incredere oarba): gasite si
  reparate 2 bug-uri exact in cod nou/schimbat de la ultimul PASS:
  - validare cifra de control CUI LIPSEA la inregistrare (9b2dde6) - CUI malformat devenea
    tenant real cand ANAF era jos.
  - control_incrucisat compara D300 R31_2 (ajustare pro-rata, gol) in loc de R27_2 (TVA
    deductibila) -> rosu fals pe orice firma cu achizitii (0a0c3a0).
- **Infrastructura teste**: suita nu putea rula (test_bilant import gresit) - reparat (3578be5).
- **D212 (PFA)** intrat in plasa de regresie (8a9021b) - testele erau doar in __main__.
- Verificat OK fara reparatii: Facturare (numerotare/TVA/storno/contare), Securitate
  (0 rute neprotejate din 313, poarta beta, izolare tenant), Admin (13/13 guard superadmin),
  Cron recurente (scadenta+idempotenta), reconciliere/MT940/WooCommerce (acoperite de suita).

BUG-URI DE FOND notate separat (NU in scopul re-testarii de azi, de investigat):
1. **An fiscal modificat** (necalendaristic): lipsa coloana; stocuri_api.py/d101.py presupun
   calendaristic (date(an,1,1) hardcodat). Firma cu exercitiu modificat nu e suportata.
   (D394-absent din semafor: REZOLVAT 18.07 - semafor faza 3 conecteaza D394+D406, acum 9/9.)
2. **Fus orar** [VERDICTELE REZOLVATE 22.07; DISPLAY browser-local ramane]. CORECTIE la premisa veche
   ("UTC pe Hetzner"): verificat la sursa 22.07 (timedatectl + SHOW timezone) -> serverul E Europe/Bucharest
   (EEST +03) SI PG timezone = Europe/Bucharest. Deci NU era bug azi - toate verdictele de zi foloseau ora RO.
   Riscul era LATENT si dublu: (i) salt de zi pe verdictele Python (date.today) daca OS-ul ar deveni UTC;
   (ii) nepotrivire OS<->PG intre cele doua laturi ale aceluiasi verdict. REPARAT: (a) garda de boot
   main.verifica_fus_orar - app-ul REFUZA sa porneasca daca OS TZ sau PG timezone != Europe/Bucharest
   (invarianta de provisionare, langa verifica_secrete_obligatorii); (b) helper common.azi_ro() folosit DOAR
   in cele 3 puncte verdict-critical (semafor _clasifica, fereastra UIT e-Transport, cron alerte) + extragere
   PG a data_depunere cu AT TIME ZONE 'Europe/Bucharest'. Adaugat ulterior: termene_api.termene_firma + portofoliu
   (fereastra [azi, azi+60] decide CE VEDE contabilul - un termen scadent azi ar disparea din lista exact in ziua
   critica -> e verdict, nu afisare) trec si ele pe azi_ro. NU s-au convertit cele 46 date.today() (restul e
   afisare/context, OS-TZ corect ajunge). Vezi DECIZII 22.07. RAMAS DISPLAY: timestamp-urile "cu_ora"
   (datetime.now() in antete/feed) arata acum ora serverului = Bucharest (corect, garda o impune); daca vreodata
   un user din alt fus vrea ora LUI, se trece pe ISO+offset + dataRo converteste la ora browserului - decizie de
   display separata, low-prio (publicul e romanesc).
3. **Ramura PFA a auditului de preluare (F183)** [PARCURSA REAL 22.07, DECIZII [PROD]]: creat tenant_003
   PFA de test prin fluxul real (POST /tenants tip_firma='pfa') + 3 operatiuni RIP prin rutele reale ->
   auditul HTTP arata DOAR constatarea RIP (verde), ZERO termeni de partida dubla. RAMIFICAT pe regim: limita
   + NEVERIFICAT arata la PFA doar ce-l priveste (via straturi_pentru + mapare text<->strat minima). obs3:
   RIP fara operatiuni validate -> gri cu temei (nu raport gol). RAMAS (obs4, nota de reachabilitate, NEREPARAT):
   categoria 'neclasificat' NU se poate adauga manual la RIP (rip_api._valideaza respinge categorie invalida) ->
   constatarea gri-pe-neclasificat din audit se declanseaza DOAR pe date IMPORTATE (rip-import), nu pe intrare
   manuala. De decis daca importul permite neclasificat (ar trebui, pt reclasificare) sau daca e ok asa.
4. **test_spv_conector rosu permanent** — REZOLVAT 22.07 (core/conftest.py). Cauza reala (verificata la
   sursa): spv_conector citeste ANAF_CLIENT_ID/REDIRECT_URI la IMPORT (constante de modul); setdefault-ul
   din test_spv_conector.py rula PREA TARZIU cand alt test importa modulul tranzitiv (via main) primul ->
   constanta inghetase goala in suita completa (trecea izolat). FIX: mutat setdefault in core/conftest.py
   (ruleaza inaintea colectarii -> inaintea oricarui import), placeholdere NU secrete (redirect_uri = URL
   public de callback, client_id fictiv). Curatat duplicarea din test (os/Fernet neutilizate scoase).
   DOVADA: suita completa 438 passed 0 failed; mutatie negativa (redirect_uri gresit -> testul PICA) =
   verifica real construcția URL-ului, nu trece vacuu.
5. **TEMA config lazy: env citit la NIVEL DE MODUL** (inventar 22.07, aceeasi clasa care a produs item 4).
   19 variabile in 5 fisiere importate TRANZITIV (via main) citesc os.getenv/os.environ la IMPORT ->
   constanta INGHETATA la primul import, ordine accidentala. In productie merge (systemd incarca env
   inainte de proces), dar in teste/orice context programatic e capcana (item 4 = dovada; conftest a stins
   ROSUL, nu fragilitatea structurala).
   FIX aplicat: helper `cfg(cheie, default="", cast=str)` in common.py -> citire la APEL.

   FACUT 22.07 (fir 6, commit config-lazy): verificare la sursa a tuturor 19 (unde e folosita fiecare +
   depinde ceva de stabilitatea in-proces). Concluzie: env inghetat de systemd -> citire-la-import ==
   citire-la-apel bit-cu-bit; nimeni nu compara cu un snapshot inghetat; niciun consumator extern nu importa
   bindingul. CONVERTITE 15 + 1 STERSA (REVOKE_URL era declarat dar NEFOLOSIT nicaieri -> cod mort, eliminat):
   observare.py (6: praguri float + emailuri + BREVO_KEY), efactura_send.py (2: FCTEL_BASE/VALIDARE ->
   accesori fctel_base/fctel_validare_url), etransport_send.py (2: BASE + VERSIUNE int), spv_conector.py
   (5 non-secret: CLIENT_ID/SECRET, REDIRECT_URI, AUTHORIZE_URL, TOKEN_URL). DOVADA: suita 438 verde dupa
   FIECARE fisier + verificator DS 0 + test functional (env setat DUPA import schimba comportamentul).
   Decizia "17 vs 15+deleted, si de ce raman cele JWT" -> DECIZII.md 22.07.

   CELE 3 JWT [REZOLVAT 22.07.2026 — S-A DOVEDIT VULNERABILITATE, nu tema de config]. La analiza inainte de
   conversie s-a gasit ca SECRET + STATE_SECRET aveau default GOL (os.environ.get("JWT_SECRET", "")) folosit
   TACUT prin HMAC-ul din nucleu (fara garda pe secret gol) -> daca JWT_SECRET lipseste, tokenurile se semneaza
   cu cheie goala (publica) = BYPASS COMPLET de auth (oricine forjeaza orice uid/rol). Reparat pe 3 straturi:
   (1) nucleu.creeaza_token/verifica_token ridica la secret gol/None; (2) common.cfg_secret (exceptie dura la
   absenta/gol, elimina default-ul) pt SECRET+STATE_SECRET; (3) main.verifica_secrete_obligatorii = fail-fast la
   pornire (app-ul refuza sa porneasca fara JWT_SECRET). DURATA_TOKEN_SEC -> lazy prin cfg (nu-i secret). Vezi
   DECIZII 22.07. SPV_FERNET_KEY avea si el default gol DAR era deja gardat (if not cheie: raise) -> nu era vuln,
   neatins.
   EXCLUSE cu motiv (raman la import, OK): cron-uri standalone (spv_poll/receive/refresh - proces propriu,
   env systemd, nu-s importate in teste) si main.py (entry-point, TENANT_TEMPLATE_PATH are default).

6. **TEMA suita depinde de env-ul din shell (db.env), nu de un mediu de test controlat** (constatat 22.07
   la baseline-ul temei config lazy). Shell-ul interactiv NU are env-ul DB pe care systemd il injecteaza
   serviciului (EnvironmentFile=/home/costin/.iconta/db.env). Fara `set -a; . db.env; set +a` inainte de
   pytest, suita da 1 ROSU de mediu ("pool neinitializat - cheama init_pool()") la
   test_etransport_send::test_trimite_nevalidat_nu_uploadeaza_prod (nu are skipif pe DB) + alte DB-teste sar.
   Cu db.env sursat: 438 verde. ACEEASI CLASA cu item 4 (test_spv_conector rosu in suita completa): un rosu
   de MEDIU e indistinct de un rosu REAL -> ascunde regresii sau da alarme false.
   FIX de decis (verifica intai ce exista): (a) conftest.py sa sourceze db.env la colectare (os.environ.setdefault
   din fisier, ca pentru JWT_SECRET/ANAF azi), SAU (b) un runner/Makefile care porneste pytest cu env-ul complet
   (EnvironmentFile-urile serviciului), ca rularea suitei sa nu depinda de ce ai in shell. Atentie: db.env are
   secrete reale de prod (parola DB) - conftest care le citeste NU se comiteste cu ele hardcodate; se citeste
   fisierul, nu se copiaza continutul. De confirmat: testele care ating DB lovesc iconta_v2 real (tenant_002)
   sau o baza de test separata? Daca real -> conftest care sourceaza prod e riscant, prefera runner explicit.
   PARTIAL 22.07: accesul psql interactiv rezolvat separat - functia idb() in ~/.bashrc (sourceaza db.env intr-un
   subshell + psql "$DATABASE_URL" ca iconta_user; parola ramane in db.env, NU in .bashrc/git). Rezolva "role costin
   does not exist" (user OS costin != user DB iconta_user). RAMAS: pytest care depinde de db.env in shell (fix a/b).

RAMAS — cere ochii/telefonul, NU SSH: **vezi CHECKLIST_BROWSER.md** (PWA P4.18-19, responsive
P4.20-21, audit vizual ~12 ecrane ramase). Grup fiscal/D101G si ONG: lasate deoparte (fara cod nou).

### REZULTAT INVENTAR (17.07.2026) - comparatie mecanica cu lista oficiala ANAF
Sursa: static.anaf.ro/static/10/Anaf/Declaratii_R/descarcare_declaratii.htm

CONSTRUITE (10 motoare + bilanturi): D100, D101, D112, D205, D212 (prin rip_api,
flux separat de declaratii_api), D300, D301, D390, D394, D406 (+ _active, _stocuri),
bilanturi S1005/S1003.

LIPSA - NIVEL 2 (rutina de cabinet, MERITA construite):
  D230 - redirectionare 3.5% impozit. Anual, multi salariati.
  D307 - ajustare TVA la transfer de active.
  (D106 RESPINS 18.07 - eroare de inventar: NU e "cea mai frecventa", e in afara publicului iConta.
   "Declaratie informativa privind dividendele cuvenite actionarilor" se depune DOAR de societatile
   nationale / companiile nationale / firmele cu capital de stat (OPANAF 1292/2014 + instr_106_2014,
   potrivit OG 64/2001). Clientii iConta = firme PRIVATE (SRL/PFA/micro) -> zero utilizatori.
   Dividendele private sunt acoperite de D205 (LIVE). Vezi DECIZII.md 18.07.)

LIPSA - NIVEL 3 (nisa, de decis explicit; nu se cara nedecise):
  D204 (asocieri fara pers. juridica), D104/D107 (ONG), D108 (reprezentante),
  D180 (nota certificare consultant fiscal), D223, D209, D221.

LIPSA - NIVEL 4 (RESPINS: administrative, nu se genereaza din evidenta contabila;
contabilul le face direct in SPV la infiintare/mentiuni):
  D010, D017, D060, D093.

LIPSA - marginale (de respins sau amanat cu motiv):
  D393, D395, D711, D089, D600, D603, D200, D201, D220, D224.

DECIZIE DEJA LUATA, documentata in cod (core/d101.py:43): D101G (grup fiscal) -
"se adauga cand apare un caz real care le cere". NU e gaura, e scop.

CONCLUZIE: "toate tipurile de declaratii" = 2 motoare reale (D230, D307), nu 40
(D106 RESPINS 18.07 - firme de stat, in afara publicului). Restul = respingeri
motivate. Mentenanta creste cu 2 abonamente, nu cu 30.

REGULA PERMANENTA: orice declaratie noua intra in monitorul fiscal ODATA cu ea.
Construita si nemonitorizata = datorie, nu functionalitate.

### RESTANTE DIN 17.07.2026 (consemnate ca sa nu se piarda)

1. COD MORT OAUTH in main.py (~liniile 4953-5015): 3 rute scrise orb, netestate:
   /anaf/oauth/start, /efactura/callback, /anaf/oauth/stare.
   Dovada ca n-au rulat: public.anaf_tokens NU EXISTA in iconta_v2 (psql: relation
   does not exist), iar CREATE TABLE era in handler. Zero consumatori in *.js/*.html.
   /efactura/callback NU corespunde cu ce e inregistrat la ANAF (/anaf/oauth/callback).
   SE STERG la construirea conectorului (regula 0a). E in BRIEF_CODE_CONECTOR_SPV.md.

2. ALERTELE FISCALE NU AJUNG LA OM. Constatat 17.07: alerta monitor_fiscal despre
   OPANAF 138/2026 (modificare D204) a stat 6 zile necitita in inboxul personal,
   printre 104 mesaje. Monitorul PRINDE corect - dar mesajul se pierde.
   Alertele fiscale trebuie sa apara IN APLICATIE (unde se uita contabilul oricum),
   nu doar pe email. De verificat ce exista deja (F103 are banner/anunturi?) inainte
   de a construi ceva nou.
   NOTA: alerta asta a fost declansatorul intregului inventar declarativ. Monitorul
   si-a facut treaba; canalul de livrare e problema.

3. D212 IESE DIN TIPAR: merge prin core/rip_api.py + core/d212_engine.py, in afara
   core/declaratii_api.py, unde sunt toate celelalte 9 (d100...d406).
   INTREBARE DESCHISA pentru Costin: e intentionat (D212 = PF/PFA, alt regim) sau
   e drift de arhitectura? Daca e intentionat -> se scrie motivul. Daca nu -> se aliniaza.
   Pana la raspuns, NU se atinge.

## Actualizare 18.07.2026 — SPV/OAuth complet (e-Factura + e-Transport LIVE); ce ramane

Clusterul SPV/OAuth construit si testat izolat (ISTORIC 18.07 partile 5-7): e-Factura (F126/F160/F176-F179)
+ e-Transport (F044/F121). F126, F044, F121 -> LIVRAT. Ce ramane, separat pe DE PROBAT (blocat pe drept)
vs DE CONSTRUIT (munca reala):

### DE PROBAT (blocat pe drept SPV — nu de construit, de dovedit cu un patron real)
- **Dus-intors LIVE e-Factura (trimite recipisa + primeste factura reala)**: cod complet (F160 send + F178
  poll + F179 receive + four-eyes), NEDOVEDIT live. Dev token (certificat admin) n-are drept SPV pe niciun
  CIF real. Se probeaza doar cu primul patron real cu certificat inrolat pe CIF-ul LUI. Necolorat verde (ca F176).
- **Dus-intors LIVE e-Transport (upload UIT + primeste codul UIT de la ANAF)**: cod complet (F121 mecanism +
  UI, garda de timp), NEDOVEDIT live - pending drept e-Transport pe CIF real (acelasi token, drept unificat).
  Ecran testat cu notificare injectata + poarta validare pe TEST.
- La primul caz real, **de confirmat LA SURSA** (parsarea defensiva e in cod, formele sunt din docs, nu live):
  formatul exact JSON + structura ZIP din raspunsul stareMesaj/descarcare; cuota ZILNICA ANAF; timpul normal
  de prelucrare (pragul de 2 zile pt starea 'investigatie' e conservator).

### DE CONSTRUIT (munca reala ramasa)
- **F127/F128 — AMANATE**: pendinte pe ANAF adaugand OAuth la SPVWS2. Deadline review 17.08.2026 (raspuns
  asteptat de la spv.webservice@mfinante.ro). Fara raspuns pana atunci -> raman AMANATE.
- **v2 F163 — persistarea randurilor decontului depus** [LIVRAT 22.07.2026, INCL. VERSIONARE varianta A]
  public.declaratii_depuse are xml text + randuri jsonb + nr_depunere (versiune). La depunere
  (coada_api.marcheaza_depusa) se persista XML + `res` serializat (asdict+default=str) cu nr_depunere=MAX+1;
  "curenta" = vederea public.declaratii_depuse_curente; cei 6 cititori de logica trec pe vedere, istoricul ramane
  in tabel. d112 -> randuri NULL (nu expune totaluri, F181). Versionare (A, nu B) - vezi DECIZII 22.07 F163v2 +
  [INFRA] GRANT CREATE.
- **F163 D-vs-D real (D390 vs D300 depus)** [LIVRAT 22.07.2026] control_incrucisat.compara_d390_vs_d300 +
  _d300_depus_randuri, a treia comparatie in verifica_d390 (citeste declaratii_depuse_curente.randuri->R->R1_1/
  R5_1). Deblocat de F198. Reguli directionale ca v1 (D390>0 & D300 nu declara -> rosu; cifre diferite -> gri;
  randuri NULL / zero depus -> gri; R1_1/R5_1 absente manual-only -> temei explicit). UI + push F164 agnostice.
  Vezi DECIZII 22.07 F163 D-vs-D. LIMITA: dovada functionala pe depunere FABRICATA (zero D300 depus real prin app).
  RAMAS: servicii IC (P/S) = v3 - d300 nu expune R3_1_1/R7_1_1 (D390 le ia manual); doar bunuri azi.
- **FRICTIUNE PRODUS: admin de cabinet nu-si poate depune propria munca fara sa-si activeze singur competente**
  [PLANIFICAT — intrebare deschisa de PRODUS, nu bug, NU se repara acum]. Descoperit 22.07 la primul parcurs REAL
  al fluxului de depunere (care nu fusese exercitat niciodata - coada complet goala, toate 5 depunerile = migrare).
  CONSTATARE: poate_valida/poate_depune au default false; _are_permisiune n-are bypass de owner (doar superadmin);
  four-eyes off nu blocheaza, dar permisiunile blocheaza -> adminul (rol admin_firma) lovește 403 "nu ai permisiunea
  de a valida" la aprobare. Exista self-serve POST /eu/competente (isi seteaza singur, fara restrictii), DAR nimic in
  fluxul de depunere nu-l indruma acolo. Plauzibil de-asta n-a depus nimeni prin app.
  INTREBAREA DESCHISA (de decis, nu de reparat): un OWNER cu bypass automat (admin = poate tot implicit) ar rezolva
  frictiunea DAR ar goli four-eyes de sens la cabinetele cu UN SINGUR om (acolo pregatirea si validarea sunt oricum
  aceeasi persoana - patru_ochi_posibil deja False). Alternativ: onboarding care indruma adminul sa-si activeze
  competentele la prima depunere; sau un default poate_* = true pentru rolul admin_firma la creare. De cantarit intre
  "control intern real" (four-eyes) si "un om nu se poate bloca singur". PARCURS O DATA 22.07 (tenant_002 test, DECIZII
  [PROD]) - fluxul MERGE cap-coada odata activate competentele; frictiunea e onboarding-ul, nu mecanismul.
- **BUG tip case: canonizare la stocare + CHECK** [REZOLVAT 22.07.2026, varianta b]. `tip` = cheie de join ->
  canonic LOWERCASE la stocare; forma ANAF uppercase in duk.CHEIE_DUK, upper DOAR la randare. CHECK (tip=lower(tip))
  pe declaratii_depuse + declaratii_coada apara cauza. Fix: istoric_import (store lowercase; validarea ramane upper
  contra nomenclator), declaratii_datorate/termene/audit/marcheaza_depusa lowercase, UPDATE 5 randuri, upper la
  randare (3 motiv backend + control.js/termene.js/activitate_cabinet.js). Respins (a) normalizare la citire (patch,
  lasa date inconsistente). Dovada: semafor tenant_002 2026/06 arata "D300 iun depusa" (era nedepusa). DECIZII 22.07.
- **Conventie migrari pe schema PUBLIC** [REZOLVAT 22.07.2026]. Cauza (migrare_* bucla doar tenant_, iconta_user
  n-avea CREATE pe public -> ALTER-uri lazy ca workaround) e inchisa: GRANT CREATE ON SCHEMA public TO iconta_user
  (DECIZII 22.07 [INFRA]) face migrarile pe public first-class ca app-user. Tipar stabilit: migrare_*.py cu un
  singur ALTER/DDL pe public (fara bucla tenant), aplica/verifica/_main - ex. migrare_declaratii_depuse_randuri +
  _versiune. Workaround-ul lazy asigura_coloana_sursa ELIMINAT (sursa mutata in migrare normala, fara cod mort).
- **PRIVILEGII + BOOTSTRAP DB NEREPRODUCTIBILE** [REZOLVAT 22.07.2026] `infra/bootstrap_public.sql`. Starea de prod
  care nu se putea reconstrui din git (GRANT + DDL-ul tabelelor publice fara CREATE nicaieri in git) e acum intr-un
  script SQL checked-in, rulat o data ca postgres la provisionarea unui server nou (header explica cum/cand/ordine).
  Categorizare la sursa (o singura sursa de adevar): EXCLUSE cele 5 cu CREATE deja in git (alerte_control_emise,
  migrare_status, cor_ocupatii, spv_token, spv_cui_acoperit); INCLUSE 23 fara CREATE, din care declaratii_depuse la
  GENESIS (migrarile ii adauga coloanele). GRANT CREATE + SET SESSION AUTHORIZATION iconta_user (ownership uniform
  fara ALTER OWNER). Idempotent (IF NOT EXISTS + guard pe constrangeri/identity), DOVEDIT pe baza temporara locala
  (rulat de 2 ori zero erori, 23 tabele + 16 secvente iconta_user, FK/identity functionale; NU pe prod). Fara date/
  secrete. REGULA PERMANENTA in header: orice obiect public nou intra prin migrare_*, NU in bootstrap.
- **NU EXISTA procedura de deploy / provisionare server nou** [PLANIFICAT]. Constatat 22.07 (cautare: grep
  provisionare/deploy/server nou pe toate .md + docs/ gol + fara README): nu exista nicaieri o secventa "cum ridici
  un server iConta de la zero". Ce exista = note operationale RAZLETE, nu procedura: CLAUDE.md sectiunea
  Infrastructura (restart, cale venv, info DB - 4 note), BRIEF_CODE_PACHET_18IUL.md (backup Storage Box). Consecinta:
  infra/bootstrap_public.sql are in header sub-secventa lui (createdb+role -> bootstrap -> app -> migrare_*), dar nu
  are procedura-gazda care sa-l inglobeze; pasii dispersati (deps OS, install postgres, creare rol+baza, venv,
  systemd unit iconta-nou.service, env files ~/.iconta/db.env + api_keys.env, aplicare tenant_template + *.sql DDL,
  lantul migrare_*, bootstrap_public) nu sunt scrisi nicaieri cap-coada. NU s-a inventat una acum (regula: nu
  inventez procedura). DE DECIS separat cat de departe merge: runbook complet cap-coada vs checklist minim vs doar
  o sectiune "Server nou" in CLAUDE.md care insiruie pasii + trimite la fisierele-sursa (bootstrap header ramane
  sursa, nu se copiaza). Referinta la bootstrap se adauga ATUNCI, in procedura-gazda, nu razlet.
  SECRETE: procedura va TRIMITE la main.verifica_secrete_obligatorii ca lista canonica a secretelor (referinta, nu
  copie — lista traieste in cod si e executabila: app-ul refuza sa porneasca fara ele); env files (~/.iconta/*.env)
  sunt parte din provisionare, nu din git (secretele nu intra in git, nici ca nume).
  FUS ORAR = invarianta de provisionare: OS TZ + PG timezone = Europe/Bucharest, impuse de garda de boot
  main.verifica_fus_orar (referinta, nu copie - app-ul refuza sa porneasca daca fusul e gresit). Procedura seteaza
  TZ-ul (timedatectl set-timezone Europe/Bucharest + PG timezone) inainte de primul boot.
- **F165 NU acopera schema PUBLIC** [PLANIFICAT — acum cu REFERINTA]. Ramane de construit auditul public (analog
  F165, poarta in suita). Acum are reper: `infra/bootstrap_public.sql` (genesis) + migrarile public (evolutie) =
  starea asteptata a schemei public; un audit-public ar compara schema live cu (bootstrap + migrari aplicate),
  exact cum F165-tenant compara cu tenant_template.sql. Blocajul de privilegii e ridicat (GRANT CREATE) -> suggest/
  auto-migrare fezabil ca iconta_user. De decis: template public versionat unic vs (bootstrap + lant de migrari).
- **v2 F164 — digest email Brevo** (rezumat zilnic/saptamanal al rosurilor de control fiscal DESCHISE per cabinet,
  pentru contabilii care nu intra zilnic in app). Completeaza v1 (clopotel in-app + click, LIVE 19.07): v1 rezolva
  restanta 17.07 (alerta ajunge in app); digestul acopera cazul "contabil care nu intra zilnic". De construit CAND
  exista semnal real ca se rateaza alerte, NU speculativ. Infra Brevo gata (5 module: observare.trimite_email_html/
  _trimite_brevo, folosita de monitor_fiscal/spv_refresh/sinteza_zilnica/notificari_scadenta/pachete). [PLANIFICAT]
- **v2 F184 — declansator COTE-driven proactiv (re-verificare instant la depasirea unei date de valabilitate din
  common.COTE): RESPINS.** Temei: cotele traiesc IN COD (common.COTE); o cota noua cere oricum editare + deploy
  manual; cronul zilnic (F184 v1) prinde firmele neconforme a doua zi. Declansatorul instant n-ar castiga nimic
  real fata de un eveniment care deja implica deploy. Decalajul de o zi = nesemnificativ. [RESPINS]

### LIVRAT 18.07 (mutat din backlog; detaliu in ISTORIC + FUNCTIONALITATI.csv)
- **F126 e-Factura cap-coada**: SEND (model principal cabinet XOR gratuit + F160 + F178 poll recipisa) +
  RECEIVE (F179 cron listaMesajeFactura filtru=P -> efactura_primite, dedup + anti-scurgere cif_beneficiar) +
  FOUR-EYES (ecran validare, cont sugerat confirmat de om, cross-control TVA existent). listaMesajeFactura
  verificat la sursa oficiala (mfinante API). Ramane doar dus-intorsul LIVE (mai sus, DE PROBAT).
- **F044 + F121 e-Transport cap-coada**: F044 (generator XML UIT) -> LIVRAT (XML-ul merge la API, nu doar
  manual); F121 (trimitere) -> LIVRAT: mecanism upload_uit/stare_uit/lista_uit pe spv_principal (drept
  UNIFICAT) + garda de timp UIT (3z inainte, 5z/15z valabilitate) + UI (buton Trimite UIT, 2 semafoare
  timp/trimitere). Endpoint ETRANSPORT/ws/v1 la sursa. Ramane doar dus-intorsul LIVE (mai sus, DE PROBAT).
- Cele 3 rute OAuth moarte din main.py — sterse la pas 1 conector (f3a33f3). Daca mai apar in vreo lista, scoate-le.

## Actualizare 23.07.2026 — din închiderea ecranului 1/12 (Control fiscal)
1. **Smoke test end-to-end pe REGIM** [NEDECIS]: creează un tenant PFA, parcurge TOȚI pașii de migrare prin
   RUTELE REALE (nu unitar), aserție zero 4xx pe tot fluxul. Motiv: blocajul de onboarding PFA a trăit tot
   sprintul PFA cu 518 teste verzi + verificator TOTAL 0 — nicio poartă statică/unitară nu parcurge un regim
   întreg cap-la-cap. Ar fi prins 400-ul necondiționat de la pasul Vector fiscal. (vezi ISTORIC 23.07, constatarea de proces)
2. **Verificare a posteriori a perioadei de decont** [PLANIFICAT]: după un an de date, Control fiscal compară
   `tip_decont` declarat cu CA reală (sub/peste 100.000 € curs BNR 31.12) + existența achizițiilor
   intracomunitare de bunuri — aceeași formă ca F163 (declarat vs fapt, trei stări + temei). Art. 322 alin.(2).
3. **FINDING: `tip_firma` needitabil post-creare** [CONSEMNAT, neconstruit]: se setează doar la crearea firmei
   (selector `#fn-tip`), nu există cale UI de corecție; o firmă creată cu tip greșit (ex. cabinet individual pus
   ca SRL — cazul AMZUICĂ) cere edit DB direct. De decis dacă merită editor de tip_firma (cu re-evaluarea
   consecințelor: carduri, straturi migrare, semafor).

## Actualizare 23.07.2026 (Pasul B) — art. 317 neexpus de ANAF v9
- **D390 la neplătitor cu operațiuni IC = GRI permanent** [BLOCAT DIN EXTERIOR]: verificat LIVE (26766053 + 14399840)
  că ANAF v9 (`PlatitorTvaRest/v9/tva`) NU expune înregistrarea art. 317 (înregistrare specială pt operațiuni
  intracomunitare / cod special RO). Secțiuni disponibile: scpTVA(art.316), RTVAI, SplitTVA, stare_inactiv,
  adrese. Art. 317 / ROI = registru separat. Fără el, un neplătitor cu IC rămâne gri (nu știm dacă e înregistrat
  art. 317 → dacă datorează D390). De reevaluat dacă ANAF publică ROI/art.317 printr-un alt serviciu web.



## GAP funcționalitate — D301 fără cale de introducere operațiuni (raportat 23.07.2026, neconstruit)
D301 (Decont special TVA, F032 „LIVE") generează XML din tabela `d301_operatiuni`, dar **nimeni nu o poate popula
din aplicație**: zero INSERT în cod, nicio rută, niciun ecran (verificat la sursă 23.07 — `grep` pe INSERT/@app/UI).
Contabilul NU are cale să introducă operațiunile intracomunitare ale unui neplătitor înregistrat art. 317 (achiziții
UE de servicii/bunuri). Consecință: D301 e **inutilizabil în practică** — generatorul + validarea XML merg, dar pe o
tabelă mereu goală (populabilă doar prin SQL direct / import extern). NU e blocant (tabela e acum canonică în template,
generarea/semaforul citesc corect), dar F032 e „LIVE" doar pe jumătate (generare fără intrare). DE DECIS: ecran de
introducere operațiuni D301 (ca RIP/registru) SAU import (extras/facturi UE → d301_operatiuni), la caz real. Vezi
DECIZII 23.07. Nu construi nimic până nu apare nevoia reală (neplătitor cu achiziții IC).

## Garda style inline (display/flex/gap/color) — NEextinsa, datorie acceptata v2.11 (masurat + decis 23.07.2026)
Scop MASURAT la sursa: 136 aparitii `display:`/`flex`/`gap:`/`color:` inline in ~15 fisiere (firme.js 53, cabinet 14,
asistenti 10, portal 7, plus login/etransport/facturi/rip/flux/raporteaza). Contravin DS cap.0 (layout/culoare = clase,
nu inline). Extinderea gardii (FONT_INLINE/RADIUS_INLINE) la display/flex/color -> 136 flag-uri = curatare frontend-wide
(per fisier, verificat vizual), revenire pe decizia v2.11 (spacing gap/margin ramane acceptat). DECIZIE 23.07 (Costin,
optiunea b): ramane datorie v2.11, garda NEatinsa; curatarea = workstream dedicat cand se programeaza, NU coada de ecran.
Panoul D390 (declaratii.js) deja curatat in commitul poz.1. Vezi DECIZII 23.07.

## Casă — card "ambele" dar contarea 5311 din interior e partidă dublă (raportat 23.07.2026, nereparat)
Cardul Casă e vizibil la orice regim (regim="ambele") fiindca VERIFICAREA PLAFOANELOR (Legea 70/2015 art.1 alin.1,
plafon sold casierie 50.000 lei - FARA exceptie pentru PFA/II/IF) il priveste pe PFA. DAR operatiunile de contare din
interior (casa_api.CATEGORII: 5311=4111, 401=5311, 5311=581, 581=5311, 542=5311) sunt partida DUBLA - un PFA le vede
desi nu i se aplica (partida simpla = RIP, nu note 5311). DE FACUT: filtrare FINA in interiorul cardului (ca la
declaratii cu neaplicabile_forma) - la partida simpla se arata DOAR verificarea plafoanelor, nu operatiunile de
contare. Consemnat, neconstruit. Temei vizibilitate card: Legea 70/2015. Vezi DECIZII 23.07 + DESIGN_SYSTEM cap.18.
