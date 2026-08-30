# ISTORIC OPERAȚIUNI PE TENANȚI

Index pe firmă al muncii de investigare/reparare/verificare. **Un rând per (tură × tenant).** Cronologic
descrescător (cel mai nou sus). **Sursa de adevăr rămâne `git log`** (mesajele de commit, imuabile); acesta e
doar indexul pe firmă, ca să nu depinzi de `git log --grep`. Regula: **fiecare tură ADAUGĂ un rând, nu rescrie**
(spre deosebire de `PREDARE_LANT.md`, care e snapshot-ul de predare și se rescrie).

Coloane: **Data** · **Ce s-a atins** (temele turei) · **Commit(uri)** · **Rămas** (ce a lăsat deschis tura).
Metoda de lucru per tenant = [`MODEL_AUDIT_TENANT.md`](MODEL_AUDIT_TENANT.md).

---

## tenant_006 — Achizitii IC Neplatitor SRL (CUI 95451848 · schema tenant_006 · cabinet Prisma 1968 · N1, neplătitor micro cu achiziții intracomunitare)

**Perimetru (regim N1 — declarat 20.08.2026, verificat la sursă).** 006 e **purtătoarea regimului**
„neplătitor micro cu achiziții intracomunitare" (art. 317 CF), nu o firmă completă. Schema are 47 de tabele
și date în trei: `firma_profil` (1), `d301_operatiuni` (3), `plan_conturi` (185 = nomenclatorul OMFP, nu date
de firmă).

**În perimetru:** vector fiscal · D301 · D390 (derivat din D301) · D100/D406 pe fapt de venituri ·
control fiscal / semafor · cele 4 straturi de import (firme, plan conturi, solduri parteneri, vector) ·
coada de validare. Pe acest perimetru, F1–F9 din [`MODEL_AUDIT_TENANT.md`](MODEL_AUDIT_TENANT.md) = parcurse;
coloana „Rămas" se citește pe el, nu pe toată aplicația.

**În afara perimetrului (tabele care trebuie să rămână goale):** `salariati`, `salariu_istoric`, `state_plata`, `pontaj`, `concedii_medicale`, `beneficii_lunare`, `facturi`, `factura_linii`, `facturi_recurente`, `efactura_primite`, `efactura_trimiteri`, `clienti`, `furnizori`, `asociati`, `casa_operatiuni`, `bonuri`, `chitante`, `extras_linii`, `rip_operatiuni`, `produse`, `articole`, `miscari_stoc`, `nir`, `nir_linii`, `retete`, `retete_linii`, `mijloace_fixe`, `solduri_initiale`, `solduri_parteneri`, `inregistrari`, `inregistrari_linii`, `registratura`, `centre_cost`, `bugete`, `etransport_trimiteri`.

**De ce nu se parcurg și restul fațetelor pe modulele astea — și de ce firma NU se exclude din matrice.**
F3 e definită pe *date populate* („nu pe fixture goale") și F7 compară *cifrele afișate cu faptele*: pe tabele
goale n-au ce contrazice, deci ar da verde fiindcă nu verifică nimic — exact falsul sentiment de acoperire pe
care `GARZI.md` îl interzice. Modulele acelea se validează pe firmele care le poartă (salarizare → t001,
SAF-T/facturi → t009 ș.a.m.d.), iar criteriul agreat e pe *funcționalitate × fațetele **aplicabile***, nu pe
firmă × toate fațetele. Excluderea lui 006 din matrice ar lăsa regimul IC netestat; umplerea ei cu date
străine de regim (soluția corectă la t005/t011/t012, care sunt SUB-EXERCITATE) ar dilua regimul, nu l-ar
întări. 006 nu e sub-exercitată — e **scopată**, și e închisă pe scopul ei.

**Criteriul de selecție al listei de mai sus** (ca să nu fie arbitrară): sunt **modulele de business ale
unor REGIMURI pe care 006 nu le poartă** — salarizare, facturare, trezorerie, stocuri, imobilizări, solduri.
Golul lor e o proprietate a regimului, deci se gardează să rămână gol. Restul tabelelor goale din schemă NU
intră în listă, fiindcă pot primi date **fără ca 006 să-și schimbe regimul**:

**În perimetru, tabele care pot primi date:** `ai_corectii`, `artefacte_produse`, `contracte_sabloane`, `d300_manual`, `d390_manual`, `d390_reclasificare`, `notificari_scadenta`, `perioada_confirmata`, `perioade_blocate`, `perioade_inchideri`, `rapoarte_salvate`, `registre_art321`, `registru_fiscal_pf`, `registru_inventar`.

Primele trei sunt căile MANUALE ale unor declarații care sunt chiar în perimetru (D390 pe 006 e auto-derivat
din D301, dar o linie manuală rămâne legitimă) — a le garda „să rămână goale" ar fi fost o greșeală, nu o
completare. Celelalte șase sunt infrastructură de aplicație (închidere de perioadă, termene, rapoarte salvate,
șabloane, corecții AI), nu module de regim.

**Gardat:** `core/test_perimetru_firma_declarat.py`, trei colți — blocul nu poate LIPSI dintr-o secțiune de
firmă; tabelele declarate în afara perimetrului trebuie să existe și să rămână GOALE (dacă firma se umple,
declarația devine roșie în aceeași zi, nu peste trei luni); și **orice tabel gol din schemă trebuie clasificat**
de una din cele două părți — un tabel nou în `tenant_template.sql` forțează decizia o dată, în loc s-o lase
ambiguă.


| Data | Ce s-a atins | Commit(uri) | Rămas |
|------|--------------|-------------|-------|
| 2026-08-19 | **temei_307 construit (excludere D390 auditabila per op)**: tip 4 poarta care alineat art. 307 (3/5/6), cerut la introducere; excluse_d301 numeste motivul+temeiul (simetric cu facturi); temei NULL=semnal. Euristica veche + confirma_local scoase (fara cod mort). Migrat pe 19 scheme. Acceptare 006/iunie verificata: D390=1 linie cod A DE136695976 baza 52.261, INV-DE-88 exclus cu semnal, tip4-fara-temei respins. | (temei_307) | — perimetru inchis. |
| 2026-08-19 | **Checksum VIES la introducere D301 (defect preview↔salvare, prins pe 006/R24.1)**: codul DE 811234567 era acceptat tacit la introducere + confirmat →D390 cod A, apoi respins de DUK. Reparat: adauga ruleaza checksum_vies (algoritm offline DE/FR/HR) + avertisment neblocant, simetric cu CUI RO. Data 006 neatinsa (cazul de reproducere). | (checksum VIES intrare) | Restul tarilor fara algoritm offline raman la DUK (nu au verificare locala - proiectare corecta). |
| 2026-08-19 | **Coada de validare oarba (defect patru-ochi, prins pe 003+006/D301)**: elementele din coada se listau dar nu se deschideau -> seniorul aproba fara sa vada declaratia/XML/verdict DUK. Reparat: endpoint GET /coada/{id}/continut + validat.js clicabil -> vizualizare read-only (verdict DUK + avertismente + XML). Bug de diacritice prins la R14 (atob brut) -> decodare UTF-8-safe. | (coada vizualizare) | — |
| 2026-08-19 | **Corectie vector 006 + sweep rute manuale**: vector corectat la scenariu (platitor_tva=False, inreg_art317=true) -> D301 devine ACTIV/datorat, D300/D394 blocate (verificat pe ecran). Sweep §8: d300_manual + d390_clasificare aveau aceeasi lipsa de verificare vector -> reparate simetric cu D301 (P3, toate 3 rutele inchise). | (sweep D300/D390) | — perimetru inchis. |
| 2026-08-19 | **Audit D301 vector<->operatiuni (006)**: mesajul selectorului D301 se bazeaza pe campul platitor_tva (control_fiscal_api); 006 are platitor_tva=True -> D301 blocat, DESI are 3 operatiuni d301_operatiuni. DEFECT: ruta adauga nu verifica statutul -> reparat (refuza platitorii). PROIECTARE: mesajul e corect. DATE: vector 006 platitor_tva=True contradictoriu cu numele+operatiunile. | (vezi commit d301 guard) | DATE: contabilul decide - firma platitoare (sterge 3 op) sau neplatitoare (corecteaza vectorul platitor_tva=False). |
| 2026-08-19 | **Audit căi achiziție IC (D390/D301/D394) + 2 reparații D390**: mapat cum intră facturile de achiziție în afara SPV (rute `achizitie-*`→facturi, ecran D301→d301_operatiuni, manual e-Factura); reparat [Q1a] dublă-sursă (factură+d301 se adună în D390 → avertisment) și [Q2] primită-fără-CUI numită distinct. Gard RED + probă vizuală R14. Q1b (D394 gol pe neplătitor IC) și Q3 (ferestre exigibilitate) = proiectare corectă. Doar cod — date 006 neatinse (seed temporar curățat). | `ade5ab6` | Datorie de date app-wide (necuantificată): câți tenanți reali au dublă-sursă/primită-fără-CUI. |
| 2026-08-19 | **F6 a11y app-wide reparat (perimetru extins 006) + 7 ecrane gardate**: auditul orchestrator pe 006 (tid 4841) a dat F2/F7 VERDE (firmă N1 fără declarații datorate; 5 neclar = necunoscute declarate P2, §5 extern legitim), F6 ROȘU pe 7 ecrane shell. Reparat cu tiparul: fără-etichetă (8 controale date/select/file -> aria-label), contrast (`.buton-sters` #ff3b30->--rosu, `.cap-titlu` #888->#6b6b6b, `.pf-frand-nume span`/`CUL.rosu` --rosu-semafor->--rosu, +2 text-uses), țintă<24px mobil (`.btn-link`+`input[file]` min-height 24). Cele 7 ecrane ÎNREGISTRATE în `nav_ecrane.ECRANE` (scan 13, gard) -> închide 7/21 din datoria hărții. | (F6 app-wide + 7 ecrane) | Latent app-wide: `CUL.galben/gri`-ca-text (contrast, de verificat când se renderizează acele stări); F3/F5 manual pe 006. |
| 2026-08-19 | **F5 nume intern D301 (perimetru 006) reparat + tipar app-wide GARDAT**: mesajele D301 `fără număr document (nr_doc gol)` / `(data_doc gol)` expuneau numele intern al câmpului (Regula 14.4) -> rescrise fără paranteză. Descoperit că tiparul e MASIV app-wide (274 mesaje / 31 generatoare, ex. `categ_venit`, `cif_c`, `nr_contract`). Gardă-ratchet `core/test_mesaje_generare_fara_camp_intern.py` (baseline per-fișier, niciun fișier nu crește; burn-down la 0). | (F5 D301 + gard app-wide) | Tipar app-wide 274 = burn-down F5 DINCOLO de perimetrul 006 (nu datoria firmei; gardat contra creșterii). |
| 2026-08-19 | **DS + mobil (F6) parcurse pe perimetrul import 006 (cerut de Costin)**: citirea DESIGN_SYSTEM a scos vector fail-fast (cap.6 pct.4) -> colectare multi-camp, marcheaza toate campurile lipsa odata; changelog DS v2.56/v2.57 (Regula 6). Trecerea Pixel 5 a scos `scrollable-region-focusable` pe corpul modal partajat `.fereastra-corp` -> `tabindex=0` app-wide. axe-pe-mobil pe firme/vector/plan/parteneri = 0, body 393, tinte >=24 (AA), title-unic 0. §5 perimetru = GOL (DS + F6 incluse). | `b94fcf2`, `6683623` | — |
| 2026-08-19 | **Plan de conturi (Adauga cont) - camp gol MARCAT + obligativitate inainte de buton**: inchide ultima datorie de field-marking din PERIMETRUL plan_conturi (tenant_006) - asterisc `.oblig` (obligativitate inainte de buton) + campul gol marcat (`.camp-invalid`) cu mesaj care numeste ce lipseste (simbol vs denumire); duplicatul marcheaza simbolul. Gard RED (4) + probat live (ambele goale->ambele rosii; doar simbol->doar denumirea; axe 0). §5 pe perimetrul straturilor de import 006 = GOL. | `ebd05c6` | — |
| 2026-08-19 | **Strat import VECTOR FISCAL - camp obligatoriu marcheaza campul vinovat**: provocat pe tenant_001 (firma fara vector) - platitor TVA fara periodicitate decont -> salvare respinsa (nicio scriere), mesaj corect DAR grupul nu era marcat (Regula 14.4 pct.4). Fix: `salveaza()` intoarce `camp` -> ruta `erori_campuri` -> `migrare.js` marcheaza grupul (`.camp-invalid`+aria-invalid). Gard RED (5) + probat live (contur rosu privit, axe 0). Cele 4 straturi import 006 INCHISE. | `73522f5` | — (in perimetru; tiparul in alte formulare = pattern app-wide, nu datoria firmei) |
| 2026-08-18 | **Straturi import solduri_parteneri + vector_fiscal verificate + a11y contrast P3**: solduri_parteneri = mesaj conform by-design (poarta Q5 preview=salvare: per-rand DE CE + Salvare blocata, probat live cu conturi ne-partener); vector_fiscal = obligativitate marcata inainte de buton (asterisc) + fara default tacit (probat live). axe pe preview parteneri a scos 2 contrast `.mig-sold-cont` #347ab8=3.86<4.5 pe #e9edf3 (fix-ul Control fiscal asumase «pe alb», gresit) -> baza #2f6fa6 (P3, toate instantele) + gard. | `2bdac14` | — (vector inchis in 73522f5) |
| 2026-08-18 | **Strat import PLAN DE CONTURI - suprascriere tacuta reparata**: adaugarea manuala facea `ON CONFLICT DO UPDATE` -> simbol duplicat (101) redenumea tacut contul OMFP standard «Capital». Acum refuz 409 in limba contabilului, cont standard neatins (re-cautare «101» = «Capital»). Gard RED + probat live (axe 0, mobil 393). | `a651fec` | — (field-marking inchis in `ebd05c6`) |
| 2026-08-18 | **Strat import FIRME - drop tacut reparat**: intrare fara cifre (typo/antet, «ABC») era eliminata inainte de ANAF fara niciun semn (Regula 4). Acum `separa_cui()` -> banner vizibil «N intrari nu contin un CUI: ...». Gard RED (7) + probat live (banner vizibil, axe 0, mobil 393). | `fd224d2` | - |
| 2026-08-18 | **Re-test complet cu audit_tenant.py** (F2/F6/F7): scos ce scapase - D301 mesaj 'nr_doc gol' (nume intern), a11y app-wide (etichete lipsa fa-stocuri/registratura/banca/rapoarte, contrast fa-control/etransport/centrecost, mobil tinte<24px) | (audit, necomis-fix) | campanie colectii date valide+invalide: F5 mesaj D301 + a11y P3 + colectii invalide |
| 2026-08-18 | **Mobil touch-target AA 2.5.8** pe 5 ecrane → 0 ținte <24px (.fir-veriga 19→24, .ajutor-btn 20→24, bug flex-shrink `#pc-cauta` 40→20px reparat) + **import motiv VIZIBIL** (nu title-only) pe 4 straturi, probat live salariați | `dc1ee22`, `e4fee31` | provocare **individuală** straturi import: firme (CUI ANAF), vector_fiscal, solduri_parteneri, plan_conturi; mobil pe casă/bancă, facturi, produse |
| 2026-08-18 | **axe landmarks app-wide → 0** (fix structural navigator.js: `<header>` banner + role=dialog + role=status) + **D406 conturi 731-738** verificat la sursă = excludere corectă din norma A (sunt în planul ONG) | `0392b3b`, `6be6a53` | — |
| 2026-08-18 | **D390↔d301** rezolvat pe corectitudine + **auto-derivare d301→D390 cod A/S** (decizia Costin) + rafinări tip 3/4 verificate la sursă + confirmare "nu e serviciu" per-furnizor + a11y contrast grila D301 | `8ceed16`, `0a47512`, `bce45bc`, `cba1856`, `abea0b6`, `a8c2f1e`, `4349d4b`, `816cf65` | — |
| 2026-08-18 | **D100 micro pe fapt de venituri** (semafor, restanță falsă stinsă) + a11y contrast Control fiscal + import blockages verificate + **field-level error marking** (contur roșu pe câmpul cu eroare, app-wide) | `b196943`, `2d9bc00`, `9638da3`, `c55308f` | — |
| 2026-08-18 | **D710** formular manual pornit pe tenant_006 (declarația 1/6 din campania de formulare _DOAR_API — detalii la secțiunea Global) | `e8d8cdc`, `885afe9` | — |
| 2026-08-17 | **Semafor: existenta_firma_an** numără achizițiile IC + casă/bancă (coerență) + cluster a11y contrast (WCAG AA) | `288f886`, `50c3ebf`, `128f239` | fronturi a11y/D390/field-marking (închise ulterior mai sus) |

---

## tenant_001 — Panificatie Salarii Speciale SRL (CUI 96653616 · schema tenant_001 · cabinet Prisma 1968 · S4, salarizare în situații speciale)

**Perimetru (celula S4 — declarat 20.08.2026, verificat la sursă).** t001 e purtătoarea dimensiunii
**„D112 complex"** din `date_test/C2_firme.md`: 12 salariați, 11 certificate de concediu medical pe 8 coduri
(01, 07, 08, 09, 10, 15, 17, 91), part-time sub minim, plafon 12 salarii minime, tichete parțiale, angajare la
mijloc de an. Vectorul fiscal a fost completat în această tură conform C-2 (`profit`, plătitor TVA `lunar`,
fără operațiuni intracomunitare) — până atunci era gol și bloca 7 declarații cu „nu pot ști".

**În perimetru:** salarizare completă (salariați, istoric salarial, concedii medicale, beneficii, plată pe
card) · D112 · D100/D101 · D300/D394 · D406 · D205 · bilanț (S1005/S1003) · control fiscal / semafor ·
vector fiscal · e-Factura.

**În afara perimetrului (tabele care trebuie să rămână goale):** `d301_operatiuni`, `d390_manual`, `d390_reclasificare`.

Criteriul: firma are `operatiuni_ic=False`, deci NU datorează D301 (art.317) și nici
D390 (recapitulativa IC) — nici pe cale automată, nici manuală. Regimul IC e purtat de t004 și t006.

**În perimetru, tabele care pot primi date:** `ai_corectii`, `artefacte_produse`, `articole`, `asociati`, `bugete`, `casa_operatiuni`, `centre_cost`, `chitante`, `clienti`, `contracte_sabloane`, `d300_manual`, `efactura_primite`, `efactura_trimiteri`, `etransport_trimiteri`, `extras_linii`, `facturi_recurente`, `furnizori`, `inregistrari`, `inregistrari_linii`, `mijloace_fixe`, `miscari_stoc`, `nir`, `nir_linii`, `notificari_scadenta`, `perioade_inchideri`, `pontaj`, `produse`, `rapoarte_salvate`, `registratura`, `registre_art321`, `registru_fiscal_pf`, `registru_inventar`, `retete`, `retete_linii`, `rip_operatiuni`, `solduri_initiale`, `solduri_parteneri`, `state_plata`.

**De ce lista de mai sus e scurtă, spre deosebire de 006.** t001 nu e *scopată*, e **SUB-EXERCITATĂ**: o
brutărie cu 12 salariați, profit și TVA lunar poate avea în mod legitim clienți, furnizori, facturi, casă,
bancă, stocuri, NIR, rețete, mijloace fixe și solduri. Golul lor e o stare de moment, nu o proprietate a
regimului — deci nu se gardează să rămână gol. `state_plata` e gol prin datoria declarată (nu se persistă la
emitere, vezi `test_datorie.py`), nu prin regim. `reg_com`, `banca` și `iban` din `firma_profil` rămân NULL
deliberat: C-2 nu le fixează, iar lipsa lor e chiar cazul de test care a scos refuzul de bilanț și cel de D300.

**Ce lipsește ca să exercite regimul complet (măsurat 20.08.2026 contra matricei S4 din C-2).**
„Sub-exercitată" nu e o etichetă, e lista de mai jos. Primele două **dezactivează fațete**, restul lasă
dimensiuni ale regimului neatinse.

1. **`pontaj` = 0 rânduri.** CAEN 1071 a fost ales tocmai pentru „forță de muncă numeroasă, ture,
   part-time". Fără pontaj, zilele lucrate se derivă din calendar (`_nzl` − zile CM), deci turele,
   absențele și lunile parțiale reale nu se exercită. **F3 e definită pe date populate — aici lipsește
   chiar producătorul lanțului.**
2. **`inregistrari` = 0.** Statul de plată nu e contabilizat, deci constatarea „Salarii declarate diferă
   de contabilitate" **nu poate deveni verde**. **F7 compară cifrele afișate cu faptele; fără note nu are
   ce contrazice** — roșu prin construcție verifică tot atât cât verdele pe tabel gol.
3. **`este_continuare = 0` pe toate cele 11 certificate**, deși 4 sunt cod 01. Progresia 55/65/75 e pe
   EPISOD (OUG 158/2005 art.17(1)); fără un certificat inițial + continuare, escaladarea nu e atinsă.
4. **Niciun certificat cod 05 sau 51.** `core/test_datorie.py` (datoria din 31.07, îngustată 02.08) spune
   verbatim că sub-rândurile C2 infectocontagioase (Rd.1.1–1.4, condiționate de `D_12`/dată) rămân
   nedefalcate „cât timp nu există cod 05 în lună". Un singur certificat închide datoria.
5. **`program_national = 0`** → `D_9a`, unul dintre cele 13 câmpuri noi din 07/2026 (datoria D112
   v1.03-072026), nu e atins de nicio dată.
6. **Cod 92 absent** — singurul din lista S4 care lipsește (există 01, 07, 08, 09, 10, 15, 17, 91).
7. **`data_incetare` NULL pe toți 12** — încetarea de contract e chiar cazul pe care `sterge_salariat` îl
   descrie în contract („la PLECARE nu se șterge, se completează data încetării").
8. **Exces tichete de vacanță peste plafonul de 6 salarii minime** — specul cere „→ INTRĂ în bază";
   există un rând `vacanta` în `beneficii_lunare`, valoarea nu a fost verificată.
9. **Facilitate salariu minim** (agroalimentar, aplicabilă la CAEN 1071) — cerută de spec, neverificat
   dacă vreun salariat o poartă.

**Cum se citește un verdict pe firma asta până se umplu 1 și 2.** F2 se sprijină pe date reale
(`salariu_istoric`, `concedii_medicale` — populate), DAR zilele lucrate din D112 vin din calendar, nu
dintr-un pontaj; F6/F9 pe ecranele fără date („curat" pe listă goală înseamnă „n-a avut ce strica");
F7 pe latura de reconciliere. Pe astea, verdictul e **necontrazis, nu verificat** — exact distincția pentru
care există gardul de perimetru. Cine reia firma trece întâi 1 și 2, apoi re-rulează fațetele.

| Data | Ce s-a atins | Commit(uri) | Rămas |
|------|--------------|-------------|-------|
| 2026-08-20 | **Audit cap-coadă F1–F9 (10 defecte) + 4 gărzi pe clase.** F2 DUK: atenționarea B4_5P pe toate cele 7 luni (baza part-time fără cei 300 lei) + D112/aprilie nedepusibilă (cod `91` refuzat de gardă, ACCEPTAT de arbitru). F3: 24/30 rânduri `salariu_istoric` orfane. F5: 14 mesaje publicate rescrise (nume interne 4→0). F6: contrast `.cf-galben` 4.02. F9: bilanț 500 gol + stocuri 400 în limba programatorului. Plus: GET care comitea, poarta închisă de o citire, datoria care se contrazicea, orchestrator care citea `stare` în loc de `severitate`. Vector completat conform C-2. Reziduul sondelor (24 `state_plata` + 2 `nir`) șters țintit. | (audit t001) | **D1** (scăderea celor 300 lei) și **D2** (Nomenclatorul 9 ca sursă) — decise, neimplementate; odată cu ele cele 3 etichete inversate din UI (02/03, 16, 17). Orfanii `salariu_istoric` + FK-ul pe `salariu_istoric`/`pontaj` (migrare pe 19 scheme) — nedecis. |
| 2026-08-17 | Audit tenant_001: default fabricat pe selecturile de vector din Date firmă (vezi ISTORIC 17.08) | — | — |

---

## Global — funcționalități care nu sunt per-firmă (probate pe firme demo)

Muncă de produs care atinge TOATE firmele; se probează pe o firmă demo, dar nu e „a tenantului". Ținută aici ca
să nu se piardă între rândurile per-firmă.

| Data | Ce | Commit(uri) | Probat pe |
|------|-----|-------------|-----------|
| 2026-08-18 | **Campania 6 formulare manuale `_DOAR_API`** (D710, D311, D307, D107, D177, D207) — scoase din `_DOAR_API`, formular UI + gardă formular-gol + DUK valid + Playwright (axe/mobil). **ÎNCHISĂ.** | `e8d8cdc`, `238deb0`, `ad74bcd`, `bca0cc8`, `06cbeb1`, `89c3a26` | ALFA MICRO (8396); D710 pe tenant_006 |

---

## Alți tenanți (probe/scanuri, sesiuni anterioare — din `git log` complet, nu în fereastra de mai sus)

- **tenant_003 — Comert Micro TVA SRL**: firma de referință pentru uneltele vizuale (`nav_ecrane.ECRANE`: import mijloace fixe, vector fiscal, plan conturi, stat plată, declarații) + D100 pe venituri 0 corectat. Scanurile a11y/mobil de mai sus (dc1ee22, 0392b3b) rulează pe ecranele acestei firme (componente tenant-agnostice).
- **tenant_002 / t004 / t005**: probe cap-coadă în sesiuni anterioare (walk-uri Playwright în `frontend_test/`). Detalii în `git log` — de migrat aici la prima atingere nouă.

> Notă: acest fișier a fost creat pe 2026-08-18 și populat retroactiv din `git log` recent (turele documentate în `PREDARE_LANT.md`). Istoricul complet dinainte trăiește în `git log`; nu a fost reconstituit integral — se completează pe măsură ce fiecare tenant e atins din nou.
