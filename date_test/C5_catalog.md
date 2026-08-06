# C-5 — Catalog de goluri de conformitate cap.6 (stări de blocare + date defecte)

**Natura livrării:** catalog, NU rescriere. Fiecare caz: TRIGGER → mesajul care TREBUIE (conform cap.6:
ce e greșit + ce trebuie făcut; stare-goală = gol + cauză/temei + ieșire) → CE APARE ACUM (verbatim) →
UNDE (strat + ecran). Mesajele NU se rescriu aici — rescrierea e campanie separată, cu decizia Costin.
**Tăcerea-la-eșec (acțiune eșuată fără NICIUN mesaj) = BUG, semnalat distinct**, nu gol de conformitate.

Etalon: `DESIGN_SYSTEM.md:89` cap.6. Surfacing frontend: `api.js` aruncă `{cod, mesaj}` (mesaj = detail||mesaj),
ecranele randează `e.mesaj` (inline sau `arataMesaj(...,"eroare")`).

Piese: **P1** (blocări, clasele 1-4 mai jos; clasele 5-6 izolare = gard, `test_izolare_structurala.py`) → P6 → P2 → P3 → P4 → P5 → P7.

---

## P1 — Clasa 1: Rol insuficient (403)

Trigger comun: user autentificat al cărui `rol`/proprietate nu satisface cerința rutei (`Depends(cere_rol/cere_cabinet/
cere_client)` sau check inline). Surfacing: `HTTPException(403, detail)` → `{detail}` → `e.mesaj` inline pe ecran.
**Mesajul care TREBUIE (cap.6, general pt clasă):** numește rolul/permisiunea lipsă + CINE o poate acorda (patron /
admin_firma) + acțiunea de ieșire ("cere dreptul X de la patron"). Actualul = zid, fără rol necesar, fără remediu.

| # | Ce apare ACUM (verbatim) | file:line | Verdict cap.6 | Ce lipsește (TREBUIE adăugat) |
|---|---|---|---|---|
| 1 | `rol insuficient pentru această acțiune` | main.py:152 (`cere_rol`) | TELEGRAFIC | rolul necesar + cere-l de la patron |
| 2 | `doar clienții accesează portalul` | main.py:160 | telegrafic | ieșirea (unde merge userul) |
| 3 | `clienții folosesc portalul, nu rutele de cabinet` | main.py:167 | telegrafic+ | (are redirecție implicită) |
| 4 | `Cabinetul este suspendat. Contactați furnizorul.` | main.py:176 | ~CONFORM | cauză + acțiune prezente |
| 5 | `Previzualizare — doar vizualizare. Acțiunile sunt dezactivate în modul preview.` | main.py:235 | ~conform | cauză + remediu implicit |
| 6 | `Doar Admin iConta.` | main.py:371,383,399,555,585,594,603,5183,5243 | TELEGRAFIC | ce e/cine e „Admin iConta" |
| 7 | `Site in lucru. Vei primi un email cand devine functional.` | main.py:1009 | conform | cauză + ce urmează |
| 8 | `nu ai permisiunea de a valida declarații` | main.py:3037,3057 | TELEGRAFIC | cere dreptul de validare de la patron |
| 9 | `nu ai permisiunea de a depune declarații` | main.py:3077 | TELEGRAFIC | idem depunere |
| 10 | `nu ai acces la acest tenant` | main.py:3113,3232,3263 | TELEGRAFIC | cine acordă accesul |
| 11 | `doar patronul poate schimba emailul principal` | main.py:3334 | telegrafic | (numește rolul; fără remediu) |
| 12 | `doar patronul poate adauga acces` | main.py:3351 | telegrafic | |
| 13 | `doar patronul poate revoca acces` | main.py:3386 | telegrafic | |
| 14 | `Doar administratorul cabinetului.` | main.py:4781 | telegrafic | |
| 15 | `Doar patronul.` | main.py:5016,5024 | TELEGRAFIC | |
| 16 | `Doar administratorul cabinetului poate edita datele cabinetului.` | main.py:5082 | telegrafic | |
| 17 | `Nu ai acces la aceasta raportare.` | main.py:5196 | telegrafic | |
| 18 | `Nu ai acces.` | main.py:5210,5267 | TELEGRAFIC (minim) | tot |

**Verdict clasă:** guard-urile centrale (cere_rol #1, poate_valida #8, poate_depune #9, Doar Admin #6) sunt uniform
TELEGRAFICE — numesc zidul, niciodată rolul necesar sau „cere dreptul de la patron/admin_firma". ~4/18 sunt aproape
conforme (#3,4,5,7). Gol de conformitate, NU bug (produc mesaj).

---

## P1 — Clasa 2: Perioadă închisă (423)

### 2a. HARD — luna contabilă închisă
- **Trigger:** postare/editare notă a cărei lună e în `{schema}.perioade_blocate` (blocată de admin_firma).
- **ACUM:** `perioada este blocată (luna închisă)` — main.py:3538 (`_cere_perioada_deschisa`, predicat `_perioada_blocata` main.py:3523), HTTP 423 → ecranul notei.
- **Verdict:** TELEGRAFIC — dă cauza (luna închisă), NU ieșirea. **TREBUIE:** + cine poate redeschide (admin_firma) sau calea de rectificare.

### 2b. SOFT — perioadă neconfirmată (blocaj motivat) — MODEL CONFORM
- **Trigger:** calcul care depinde de o lună încă NECONFIRMATĂ → `PerioadaNeconfirmata(ValueError)` (core/perioada.py:11).
- **ACUM (verbatim, core/perioada.py:15-20):** `"PERIOADA_BLOCATA: <Declaratie> nu se poate calcula pentru LL.AAAA:
  pontajul lunii (...) nu e CONFIRMAT - datele sunt informative, nu autoritative (temei). Confirma <X>-ul lunii
  (buton, rol admin_firma, la inchidere) sau corecteaza datele; pana atunci calculul e blocat."` Handler global
  `_handler_perioada_blocata` (main.py:104-111) → 423 `{detail: "Perioada <detaliu>."}`.
- **Verdict:** COMPLET CONFORM cap.6 — gol (calcul blocat) + cauză/temei (lună neconfirmată, date informative) +
  ieșire (confirmă luna ca admin_firma / corectează). **Model de urmat** pentru restul clasei (contractul 3-părți
  trăiește chiar în constructorul excepției).

---

## P1 — Clasa 3: Date lipsă (`erori_generare`, 11 generatoare) — CONFORM pe conținut

- **Trigger:** generare declarație cu profil incomplet. `erori_generare(prof)` → liste `"LIPSĂ …"`; `genereaza()`
  ridică `ValueError("<Dxxx> nu se poate genera: " + " ".join(erori))`.
- **Traseu end-to-end (ex. D301):** d301.py:262 ridică → `declaratii_api.genereaza` propagă → rutele
  `POST /coada` (main.py:3000), `/declaratii/{tip}/valideaza` (3237), `/declaratii/{tip}` (3270) fac
  `except ValueError: raise HTTPException(422, str(e))` → declaratii.js pas2 (:183-192) randează `e.mesaj` verbatim
  în `.dec-eroare` (specific, nu generic — comentat `[G2]`).
- **Mesaje (distincte, `LIPSĂ <câmp> (obligatoriu la <D>)`):** d100:178-182, d101:290-296, d205:102-106, d710:165-169,
  d300:380-388 (bancă/IBAN/CAEN), d301:173-179, d390:229-231, d394:723-731, d406:425-431.
- **Verdict:** CONFORM pe conținut — fiecare LIPSĂ numește câmpul exact + declarația care-l cere; „ce trebuie făcut"
  (completează în profil) e implicit clar; surfacing corect (specific). **TREBUIE (îmbunătățire, nu bug):** adaugă
  „unde se completează" (ecranul date_firma) — cap.6 „câmp neajutabil → camp-ajutor".
- **NECONFORMITATE DE CONSISTENȚĂ (nu bug funcțional):** `d112.py:607,609` și `bilant_api.py:61,63` emit `LIPSA`
  (fără diacritice) în loc de `LIPSĂ` — cosmetic, dar rupe uniformitatea. Semnalat.

---

## P1 — Clasa 4: Patru ochi (403) — CONFORM

- **Trigger:** aprobatorul == pregătitorul (`creat_de_id == aprobat_de_id`), cu patru-ochi activat de patron și fezabil.
- **ACUM (verbatim, coada_api.py:186-187):** `nu poți aproba o declarație pe care ai pregătit-o tu însuți (control
  intern: pregătirea și validarea se fac de persoane diferite)` → `{ok:False, cod:"PATRU_OCHI", mesaj}` → ruta
  `POST /coada/{id}/aproba` (main.py:3038) mapează `cod=="PATRU_OCHI"` → 403 (main.py:3042) → validat.js:150 `#val-eroare`.
- **Verdict:** COMPLET CONFORM — ce e greșit (nu-ți aprobi propria muncă) + temei (control intern) + ieșire implicită
  (alt coleg aprobă). Fără gol.

---

## P1 — TĂCERE-LA-EȘEC (BUG-uri, distinct de golurile de conformitate)

Acțiune eșuată care nu produce NICIUN mesaj (încalcă „Niciodată tăcere la o acțiune eșuată") = BUG, nu gol.
**Semnalate pentru decizia Costin (fix = campanie separată, ca marcaje).**

| # | Loc | Ce se întâmplă | De ce e bug |
|---|---|---|---|
| B1 | `declaratii.js:62-64` (`incarcaTipuri`) `catch { S.tipuri=[]; ... }` | Dacă `GET /declaratii/tipuri` pică, lista de declarații se randează GOALĂ, fără eroare | Fundătură tăcută: userul vede „nicio declarație", nu un eșec |
| B2 | `declaratii.js:257` (`randeazaClasificareD390`) `catch { zona.innerHTML=""; return; }` | Panoul de clasificare D390 se golește tăcut la eșec de load | Fundătură tăcută |
| B3 | `declaratii.js:313` (`randeazaOperatiuniD301`) `catch { zona.innerHTML=""; return; }` | Panoul operațiuni D301 se golește tăcut la eșec | Fundătură tăcută |
| B4 | `main.py:3044-3047` (`aproba`) `try _notif_pregatitor(...) except: pass` | Aprobarea reușește, dar notificarea pregătitorului e înghițită la eșec | Pregătitorul nu află că a fost aprobat/blocat (minor) |
| B5 | `main.py:3064-3067` (`respinge`) `try _notif_pregatitor(...,"respinsa") except: pass` | Respingerea reușește, dar notificarea e înghițită | Pregătitorul nu află că trebuie să corecteze (minor) |

Verificate și CURATE (produc mesaj → conforme): validat.js:35 („Nu am putut încărca coada."), declaratii.js:49
(„Nu am putut încărca firmele."), validat.js:150 (`e.mesaj`), reclasificări/manual add-del (arataMesaj eroare).
`core/perioada.py` și `core/coada_api.py` NU au `except: pass` — toate căile de blocare întorc `{ok:False, mesaj}` explicit.

---

## Rezumat P1 (clasele 1-4)
- **Clasa 1 (rol):** ~14/18 goluri telegrafice (lipsă rol-necesar + remediu); ~4 aproape conforme. Gol, nu bug.
- **Clasa 2 (perioadă):** 2a hard = telegrafic (lipsă ieșire); 2b soft = MODEL conform (blocaj motivat 3-părți).
- **Clasa 3 (date lipsă):** conform pe conținut; îmbunătățire = „unde se completează"; consistență: `LIPSA` fără
  diacritice la d112/bilant.
- **Clasa 4 (patru ochi):** conform.
- **BUG-uri tăcere-la-eșec:** B1-B3 (fundături UI reale, declaratii.js), B4-B5 (notificări înghițite, minore).

---

# P6 — Cens complet câmpuri obligatorii (`.oblig`), toate 34 ecranele (reluare integrală sweep 24.07)

Formă: trigger → ce TREBUIE (cap.6) → ce apare acum → unde. Nimic rescris. Două direcții de minciună:
**backend-obligatoriu fără asterisc UI = gol**; **asterisc UI fără backend-obligatoriu = gol (minte invers, distinct)**.
Marker canonic = `<span class="oblig">*</span>`; ajutor = `<span class="camp-ajutor">`; eroare de câmp = `<span class="msg-eroare">`.

## Acoperire (toate 34, confirmat `ls static/js/ecrane/*.js`=34)
- **~15 ecrane FĂRĂ formular de submit** (dashboards/liste/randere): tipare, preturi, asistent, cabinet, control,
  activitate_cabinet, admin_activitate, termene, capacitate, admin_sanatate, semafor, control_verdict (+ woo=formular
  fără nicio validare/obligativitate). Cens vacuu — nimic de reconciliat.
- **~19 ecrane cu formular**: login, date_firma, emitere_ecran, facturi_ecran, produse_ecran, asistenti, portal, firme,
  flux_concediu, migrare, rip_ecran, etransport_ecran, validat, declaratii, operatiuni_ecran, setari, admin,
  admin_raportari, pachete, recomanda, raporteaza.

## Sănătatea markerului canonic
- **date_firma.js = MODEL CONFORM:** setul `.oblig` UI (nume/cui/reg_com/caen/adresa/banca/iban/telefon + regim_fiscal/
  platitor_tva) == `firma_profil_api.OBLIGATORII` (core/firma_profil_api.py:146-155) EXACT. Zero goluri.
- **Deviații de marker (obligatoriu marcat NON-canonic — nu `.oblig`):**
  - `operatiuni_ecran.js:312` și `etransport_ecran.js` — asterisc = TEXT literal `" *"` în etichetă, nu `<span class="oblig">`.
  - `firme.js:551,554` (formular salariat) — `" *"` literal via helper local `camp()`, nu `.oblig`.
  - `login.js` — erori la submit în casetă generică sus `.login-eroare`, nu `.msg-eroare` per câmp.

## Gol dir. 1 — BACKEND-OBLIGATORIU fără asterisc UI (câmpul e cerut, dar UI nu-l marchează)
| Ecran | Câmp | Backend cere (loc) | Marcaj UI | Surfacing acum |
|---|---|---|---|---|
| login | reg-termeni | 400 `if not accept_termeni` (main.py:1023) | fără `.oblig` | client validează (`:477`), generic sus |
| flux_concediu | cm-venit (cod 10) | 422 „La codul 10 completeaza venitul brut realizat" (salariati_api.py:369) | fără | doar backend 422 în `#cm-rezultat`, fără pre-check JS |
| migrare | vf-regim (SRL/partidă dublă) | 400 REGIM_INVALID (vector_fiscal_api.py:85) | fără (button-group) | **înghițit → mesaj generic** (vezi bug) |
| facturi | pr-motiv (respinge) | 422 „motivul respingerii e obligatoriu" (main.py:6905) | fără | client validează, generic |
| facturi | fd-chit-data / fd-chit-suma | `ChitantaEmite` fără default + 400 suma≤0 (main.py:4224,4235) | fără | prefill (mitigat) |
| produse | pr-den | `ProdusCreeazaIn.denumire` fără default (main.py:846) | fără | **client SILENT (doar focus)** — vezi bug |
| asistenti | asi-email | 422 „email invalid" (main.py:4816) | fără | client validează |
| portal | ac-email-nou-val (schimbă email) | 400 (main.py:3327) | fără | **fără validare client** (spre deosebire de fratele adaugă-acces) |
| firme | sn-nume (salariat) | `SalariatIn.nume` fără default (main.py:792) | `" *"` literal, nu `.oblig` | client validează |
| date_firma | operatiuni_ic | IC_LIPSA (vector_fiscal_api.py:55) | fără | mitigat (select default „nu", nu trimite None) |

**Ce TREBUIE:** fiecare = `<span class="oblig">*</span>` pe etichetă + (unde valoarea nu-i evidentă) `camp-ajutor` + la
submit `.msg-eroare` lângă câmp. Acum: majoritatea validează generic-sus sau doar backend; câteva silent.

## Gol dir. 2 — ASTERISC UI fără backend-obligatoriu (minte invers — semnalat DISTINCT)
| Ecran | Câmp | Marcaj UI | Backend NU cere (loc) | Efect |
|---|---|---|---|---|
| login | reg-cui | `.oblig` `:381` | `RegisterIn.cui: Optional=None` (main.py:729); cont creat oricum | asterisc fals; nici client nu validează |
| emitere | em-nume (Denumire beneficiar) | `.oblig` | `EmitereIn.tert_nume: Optional=None` (main.py:877), handler nu verifică | asterisc; enforcement (dacă există) e în facturi_api = **nedeterminabil** |
| **flux_concediu** | **cm-sfarsit (Data sfârșit)** | `.oblig` | **niciun check** (nici JS, nici backend) | **salvează `data_sfarsit=NULL` și raportează succes** — vezi bug |
| **etransport** | **valoare_fara_tva** | `" *"` literal | absent din client guard ȘI din `etransport.py:60 campuri_required_lipsa` | marcat obligatoriu, enforce-uit nicăieri |
| **firme** | **sn-salariu_brut** | `" *"` literal | `SalariatIn.salariu_brut: float=0` (main.py:798), client nu validează | trimite/stochează 0 tăcut sub un „*" |

## Acoperire `camp-ajutor` și `msg-eroare` (cap.6: „niciun câmp obligatoriu gol fără context" / „eroare lângă câmp")
- **`camp-ajutor` RAR** — prezent doar pe câteva câmpuri neevidente (firme fn-tip/reges/contract-continut; flux_concediu
  condiționale urgență/CNP/venituri-6-luni; migrare decont/ic; setari SPV-buton). **Majoritatea câmpurilor obligatorii NU
  au `camp-ajutor`** chiar unde valoarea nu-i evidentă (ex. iban/reg_com/caen în profil, cota/curs în D301). Gol de cap.6.
- **`.msg-eroare` per-câmp RAR** — validarea dominantă e generic-sus prin `arataMesaj(...,"eroare")`. `.msg-eroare` lângă
  câmp apare doar pe: flux_concediu (condiționale), emitere, facturi (chitanțe/email), firme (reges/client-acces),
  validat (motiv), migrare (plan conturi). Restul = eroare generică sus. Gol de cap.6 („eroare lângă câmpul relevant").

## TĂCERE-LA-EȘEC descoperită în P6 (BUG-uri, distinct de goluri) — semnalate pt decizia Costin
| # | Loc | Ce se întâmplă | Gravitate |
|---|---|---|---|
| B7 | `produse_ecran.js:~20` (`randeazaProduse` catch) | `arataMesaj(zona,…)` dar `zona` NU e în scope → **ReferenceError**; eroarea reală de load nu se arată și handler-ul crapă. Textul zice „salva" pe un read | BUG real (cod rupt) |
| B8 | `flux_concediu` cm-sfarsit | câmp cu asterisc, fără niciun check → salvează `data_sfarsit=NULL` și zice succes | BUG (date corupte tăcut) |
| B9 | `migrare.js:464` | handler citește `e.message`, dar api.js aruncă `{cod,mesaj}` → erorile specifice (REGIM/DECONT/IC) se pierd, mereu „Nu am putut salva" | BUG (mesaj înghițit) |
| B10 | `produse_ecran.js:~140` pr-den | gol la Salvează → `focus(); return;` fără mesaj | tăcere |
| B11 | `portal.js:338` sol-input | gol → `if(!txt) return;` submit nu face nimic, fără feedback | tăcere |
| B12 | `control.js:79` | `catch {}` pe GET verdict → randează firmă „curată" din default gol; load eșuat = firmă fără probleme | BUG (fals-curat) |
| B13 | `admin_activitate.js:117` | `catch {}` timeline → panou gol „Niciun eveniment"; eșec = gol | tăcere |
| B14 | `raporteaza.js:91` urcaPoze | `catch {}` → upload imagini eșuează tăcut, dar sesizarea zice „Sesizare trimisă" (atașamente pierdute) | BUG (succes fals) |
| B15 | `admin_raportari.js:194` | close-sesizare `catch { btn.disabled=false }` fără mesaj | tăcere |
| B16 | `raporteaza.js:180` legaFir | reply-in-thread `catch { btn.disabled=false }` fără mesaj | tăcere |
| — | load-path `catch {}` (benigne, default vizibil): setari:50/87/139/182/328, admin:66/150/166, woo:12, rip:26, etransport:218, facturi scadentar reload:313, portal refaPoza, cabinet:473 | panou cu valori implicite, fără notiță | minore |
| — | **INFO-LEAK:** `operatiuni_ecran.js:381` — mesajul de eroare include `JSON.stringify(corpReq)` (tot payload-ul) vizibil | semnalat (nu tăcere; scurgere în mesaj) |

(B1-B6 din P1/batch-D rămân: declaratii.js:62/257/313, main.py:3044/3064 notify înghițit, admin_activitate:117=B13.)

## Nedeterminabil static (declarat explicit, per regula „cale neacoperibilă → declarată cu motivul")
- `operatiuni_ecran.js`: obligativitatea per câmp pe ~40 rute `ruta` separate — definită client-side prin `REGISTRU.optional`; rutele backend necitite.
- `declaratii.js` D390 manual-add (`/d390-clasificare/manual`) — rută necitită.
- `emitere` em-nume / `facturi` fr-nume — enforcement în `core/facturi_api`, nu în main.py.
- `firme` reges rg-adresa — enforce-uit downstream în serviciul REGES, nu în main.py.
- `date_firma` regim_fiscal pt partidă simplă — backend cere gol (REGIM_LA_PARTIDA_SIMPLA), UI oferă doar micro/profit; depinde de `tip_firma` citit server-side (runtime).
- Constrângerile DB NOT NULL (ex. `concedii_medicale.data_sfarsit`) — DDL necitit; inserția trece `None` fără eroare → coloane probabil nullable, dar neconfirmat.

## Rezumat P6
- Cens complet: 34/34 ecrane; ~19 cu formular, ~15 fără. **date_firma = model conform** (UI==backend exact).
- **Gol dir.1 (backend cere, UI nu marchează): 10 cazuri** (login termeni, flux venit, migrare regim, facturi ×3, produse den, asistenti email, portal email, firme sn-nume, date_firma ic-mitigat).
- **Gol dir.2 (asterisc fals, distinct): 5 cazuri** — critice cm-sfarsit (NULL tăcut) și etransport valoare_fara_tva.
- **Deviații marker canonic:** operatiuni/etransport/firme-salariat (`" *"` literal) + login (casetă generică).
- **`camp-ajutor` și `.msg-eroare` per-câmp = rare** → gol cap.6 sistemic (context + eroare-lângă-câmp).
- **Tăcere-la-eșec: B7-B16** (distinct de goluri) + info-leak operatiuni:381. Fix = campanie separată, decizia Costin.

---

# P2 — Date lipsă / incomplete (catalog EXTINS, dincolo de `erori_generare` profil + `PerioadaNeconfirmata`)

Formă: trigger → ce TREBUIE (cap.6: gol + cauză/temei + ieșire) → ce apare acum (verbatim) → unde. Nimic rescris.
Surfacing global: `main.py:103-111` prinde orice mesaj cu `PERIOADA_BLOCATA` → **423**; restul per-rută (422/409/404) sau `{eroare}`/`{ok:false,cod}` inline.

## Cluster A — Excepții custom de date lipsă/indisponibile (4 clase + 1)
| Excepție | Trigger | Ce apare ACUM (verbatim + loc) | Unde | Verdict cap.6 |
|---|---|---|---|---|
| `CursIndisponibil` (curs_bnr.py:37) | curs BNR absent la data facturii | `"Cursul BNR pentru <moneda> la data <data> nu e disponibil momentan."` (curs_bnr.py:172) | facturi_api.py:272 prinde → `{ok:false,cod:CURS_INDISPONIBIL, mesaj:"Cursul BNR nu e disponibil momentan."}` | **PARȚIAL** — spune CE (curs absent), dar **pierde ieșirea** („reîncearcă/introdu manual") pe suprafața facturi_api; TREBUIE: + ce faci |
| `PerioadaIndisponibila` (common.py:480) | valoare (COTE) necerută la sursă înainte de o dată | `"<data> nu poate fi calculata: valoarea '<nume>' nu e definita inainte de <prima_data> ... se completeaza in COTE la sursa (decizie de dezvoltator)."` (common.py:597) | main.py:103 → 423 | **EXEMPLAR** (gol+cauză+ieșire+cine decide) |
| `PlafonCulturalIndisponibil` (common.py:506) | plafon tichete culturale în fereastră GRI (semestru fără ordin) | `"PERIOADA_BLOCATA: Tichete culturale - plafon indisponibil pentru <data>: <motiv>"` (common.py:543) | beneficii_api.py:72 → `{eroare}` inline | **EXPLICIT** (ce + motiv) |
| `EDateIncomplete` (efactura_send.py:108) | firmă București fără sector în adresă la trimitere e-factura | `"Localitate incompleta (<et>): firma e in Bucuresti dar lipseste sectorul (SECTOR1..6) ... Completeaza sectorul inainte de trimitere."` (efactura_send.py:124) | main.py:6719 → 422 | **EXEMPLAR** (ce lipsește + ce faci) |
| `ReconciliereEmis` (reconciliere_emis.py:24) | totalPlata_A absent din XML emis | `:38` „...totalPlata_A absent din XML EMIS - artefactul nu contine totalul de plata" / `:51` „d112: totalPlata_A absent din XML EMIS" | poartă pe artefact | `:38` explicit; **`:51` TELEGRAFIC** (bare, fără ieșire) |

## Cluster B — Nomenclator lipsă / cod nemapat (generatoare) — majoritar EXPLICIT
| Trigger | Ce apare ACUM (verbatim + loc) | Verdict |
|---|---|---|
| D100 cod_oblig fără cont bugetar | `"D100: cod_oblig %r fara cont bugetar (... COD_BUGETAR); atributul cod_bugetar e OBLIGATORIU (ANAF C(10)), nu se omite tacit."` (d100.py:140) | EXPLICIT (ce+temei+de ce nu tacit) |
| D301 curs absent/invalid | `"D301: curs de schimb absent sau invalid (%r). CF art.290 alin.(2) ... pentru RON e 1, pentru valută trebuie completat."` (d301.py:72) | EXEMPLAR |
| Cotă TVA lipsă pe operațiune API | `"cotă TVA obligatorie: operațiunea trebuie să declare explicit cota (... nu cotă standard)"` (common.py:288) | EXPLICIT |
| Cotă gol în registru (period-aware) | `"<nume>: valoarea din <din> (<temei>) a fost valabila pana la <out> ... gol in registru. Adauga valoarea valabila in COTE."` (common.py:589) | EXEMPLAR (gol+cauză+ieșire) |
| D710/D100 micro fără cotă (R17) | d710.py:211 / d100.py:223 „...121 (micro) CERE cota... validator R17/ERR" | EXPLICIT-TERSE (fără „unde completezi") |

## Cluster C — Goluri pe zero / date goale (nu se depune pe zero)
| Trigger | Ce apare ACUM (verbatim + loc) | Verdict |
|---|---|---|
| D390 pe zero operațiuni IC | `"D390 nu se depune pe zero: luna ... nu are nicio operatiune intracomunitara. ... Daca ar fi trebuit sa existe, verifica daca facturile UE sunt introduse si daca partenerii au cod de TVA valid."` (d390.py:425) | **EXEMPLAR** (gol+temei+ieșire) |
| D205 fără beneficiar de venit | `"D205 fara niciun beneficiar de venit - nu se genereaza ..."` (d205.py:113) | EXPLICIT-TERSE (mai puțină ieșire ca d390) |
| D406 GeneralLedger gol | NU e stop — emite `<GeneralLedgerEntries/>` „pe zero", valid (d406.py:685-700) | CONFORM-prin-design (contra-exemplu: gol ≠ stop la d406) |
| D406 factură fără linii | NU e stop — linie sintetică cu descriere „detaliul lipsește" (d406.py:1172-1178) | CONFORM-prin-design (semnal-în-XML) |

## Cluster D — Rateuri de lookup entitate (adiacent date-lipsă, greutate mică)
- `facturi_recurente.py:48/57` → `{eroare:"sablon inexistent"}` — **TELEGRAFIC**.
- `raportari_api.py:103` → `{ok:false,cod:"MESAJ_INEXISTENT"}` — **doar cod, fără mesaj** (telegrafic la API).
- `mijloace_fixe_import_api.py:161` → `{motiv:"cod_lipsa",mesaj:"%s: fara cod de inventar"}` — explicit-terse per rând.
- (main.py: 216 hits `lipsă|inexistent|...` = majoritar guarde 404 tenant/entitate = **izolare/lookup, în afara scopului P2** — cataloage la P4/P5, nu aici.)

## TĂCERE-LA-EȘEC în P2 (BUG distinct)
| # | Loc | Ce se întâmplă | Gravitate |
|---|---|---|---|
| **B17** | `d406.py:1160` (apel `uom_unece`) | `um_cod, _um_stiut = uom_unece(um)` — flag-ul `_um_stiut` (semnalare „unitate necunoscută") e ARUNCAT (underscore). O UM necunoscută devine **tăcut** `H87`, fără niciun mesaj (gol+cauză promise în docstring, moarte). | **BUG LIVE** (fallback tăcut pe date incomplete) |
| — | `d406.py:154-170` `_partener_registration_number` | țară non-ISO → număr best-effort fără semnal (nu-i stop) | minor (fallback tăcut) |
| — | `d301_operatiuni_api.py:61` `except (PerioadaIndisponibila,ValueError): continue` | omite o opțiune de cotă invalidă pt perioadă („nu se oferă fals") | **legitim, NU bug** (semnalat ca să nu fie re-flag) |
| — | (istoric remediat) `d406.py:1061/1103/1204/...` | fostul `except: pass` care golea GL tăcut (MASCA SCOASA 27.07) → azi `RuntimeError("D406: ... a esuat - %s")` | remediat (clasă vânată, acum zgomotos) |

## Rezumat P2
- **Stopurile fiscale de generator (d100/d301/d390/d205/common cotă) = majoritar EXPLICITE/EXEMPLARE** (gol+temei+ieșire) — cel mai bun strat din C-5 până acum. Model: PerioadaIndisponibila, EDateIncomplete, D390-pe-zero, common:589.
- **Puncte slabe (goluri de conformitate):** (a) `CursIndisponibil` pierde ieșirea la suprafața `facturi_api`; (b) `ReconciliereEmis:51` telegrafic; (c) `d710/d100` micro-cotă fără „unde completezi"; (d) stratul de lookup entitate (`sablon inexistent`, `MESAJ_INEXISTENT` cod-only) telegrafic.
- **BUG tăcere-la-eșec: B17** (d406 unitate necunoscută → H87 tăcut). + fallback țară minor. Fix = campanie separată.
