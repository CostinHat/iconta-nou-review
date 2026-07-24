# Checklist sesiune browser — ce NU se poate testa prin SSH

Pregătit 16.07.2026 după re-testarea SSH completă (555 teste verzi, 4 bug-uri reparate).
Aici sunt DOAR verificările care cer ochi/telefon: randare reală, responsive, PWA.
Criteriile sunt obiective (Design System + breakpoint-uri reale din CSS), nu de gust.

Referință: `DESIGN_SYSTEM.md` (cap.1–16). Breakpoint-uri reale în CSS: **480, 520, 560, 760, 900px**.
Gardianul mecanic (`verificator_conformitate.py`) e deja curat pe toate — aici prindem ce el nu vede.

---

## A. PWA & mobil (P4.18–19) — pe telefon real

- [ ] **P4.18 iOS** (deja făcut 14.07, re-confirmare): Safari → Adaugă pe ecran principal → pornește **standalone** (fără bara Safari) → funcționează **offline** (avion pornit, deschide app).
- [ ] **P4.18 Android**: Chrome → banner/meniu "Instalează aplicația" → pornire standalone → offline OK. (rămas secundar din 14.07)
- [ ] **P4.19 Pozează bon**: pe telefon, portal → Pozează bon → **cameră directă** se deschide (nu doar galerie) → **multi-imagine** (2+ poze pe același bon) → flux până la nota generată.
- [ ] Manifest: iconă corectă pe ecranul principal (nu iconă generică), nume scurt lizibil.

## B. Responsive (P4.20–21) — DevTools (F12 → device toolbar) + telefon

- [ ] **P4.20 Portal <400px** (setează 360px): toate cardurile intră în lățime, **fără scroll orizontal**, fără text tăiat. Ecrane: Acasă, Facturi, Declarații, Solicitări, Cifrele firmei.
- [ ] Verifică la 480px și 520px (breakpoint-uri reale) că tranziția e curată, nu sare layout-ul.
- [ ] **P4.21 Landing <900px**: meniu/hero se rearanjează corect.
- [ ] **P4.21 Landing <560px**: o coloană, butoane full-width, fără overflow.

---

## C. Audit vizual ecrane (~20 neverificate cu ochii) — cabinet, desktop

Pentru FIECARE ecran, 4 verificări obiective din Design System:

1. **Anatomie fereastră** (cap.1 + cap.9): entitate-antet → titlu `h2` → corp. Cardul se deschide ca **fereastră/modal**, niciodată inline (cap.2a).
2. **Aliniere tabele** (cap.4): text la stânga, **sume la dreapta** cu separatorul de mii aliniat pe coloană.
3. **Panouri** (cap.16 + cap.2): fundal alb + bordură `#b9c2cf`; formularele **NU** într-un wrapper alb pe gri (caseta invizibilă gri-pe-gri).
4. **Semafoare** (cap.8): culori din tokeni (verde/galben/roșu), nu nuanțe ad-hoc.

**NUMEROTARE CANONICĂ (fixată 23.07.2026):** pozițiile 1–12 = ordinea ACESTEI liste, nu ordinea în care sunt
atacate. Se scrie „poziția N" (fixă), nu „N/12" derivat din ordinea de lucru. Ordinea DE ATAC o dă Costin,
independent de poziție. (Corecție la commitul de închidere care numea Control fiscal „1/12" — e poziția **2**.)
**ÎNCHISE: poziția 1 (Declarații) + poziția 2 (Control fiscal) + poziția 3 (Termene) — 23.07.2026; pozițiile 4 (Setări cont), 5 (Recomandă), 6 (Admin), 7 (e-Transport), 8 (Produse) și 9 (Tipare) — 24.07.2026. Poziția 10 (Semafor/coadă) ÎNCHISĂ PARȚIAL [~] 24.07.2026 (rest [B] decizie amânată). Rămân 3** (10–12, din care 10 parțial).

Ecrane de parcurs (din DE_FACUT.md §3, verificatorul e curat pe ele dar nu prinde randarea):

1. [x] **Declarații** — **ÎNCHIS 23.07.2026** (comituri 497c83c→a552a78 + d6485f4 + ac288ea). `declaratii_api.py` + `declaratii.js`.
   Verificat vizual pe 3 firme (2 PFA + 1 SRL): dropdown D100/D101/D406 dezactivate + temei pe PFA, cardul Declarații
   vizibil la PFA, filtrarea cardurilor pe `regim_contabil`. Reparat (vezi ISTORIC 23.07 poz.1): G1 `neaplicabile_forma`
   (o mapare, 3 consumatori, poartă 422), `DOAR_SRL` pe Declarații = fals negativ, listele `DOAR_SRL`/`DOAR_PFA`
   eliminate (cardul declară `regim`, vizibilitatea derivă prin `regim_contabil` — gardă CARD_REGIM), G2/G3/G4.
   BUG cache/instanță surfacat aici: antet lipsă pe calea Termene (firme.js importat cu versiuni divergente) → gardă
   IMPORT_VERSIUNE (DS cap.19) + antet explicit în meniuFirma (DS cap.9).
   RĂMAS consemnat (nereparat): Casă card „ambele" (5311 partidă dublă, filtrare fină în interior); D710 LIVE inaccesibil UI; D301 fără writer.
2. [x] **Control fiscal** — **ÎNCHIS 23.07.2026** (SRL+PFA, comituri ac5ab4f→9693c1f). Semafor cross-portofoliu + Declarație vs contabilitate. `control_fiscal_api.py` + `control.js`.
   **Consolidare 24.07** (comituri 4e43254 + ac7e135, vezi ISTORIC 24.07 poz.2): 3 renderere per-firmă alegeau chei `vc` pe nume, fiecare cu altă omisiune tăcută (DANTE: salarii + 5121 nu apăreau pe card) → renderer UNIC de corp (`control_verdict.js`, detaliu + card fișă) + gardă **VERDICT_PARITATE** cu 2 parități (randare + severitate); `ecranVerificari` scoped + declarat (`VC_VERIFICARI`). DS cap.20. Nimic vizual nou — nu cere re-verificare pe ecran.
3. [x] **Termene** — **ÎNCHIS 23.07.2026** (comituri 80c260b→b3fb563). `termene_api.py` + `termene.js`.
   8 reparații (vezi ISTORIC 23.07 poz.3): sub-raportare D394/D406/D101 (consolidare pe primitivă unică), D390 pe
   fapt lunar (nu flag fix), d205_vs_457 roșu fals (cod mort scos), neevaluate gri cu temei, regresie d301 negardat,
   §4 mărginire TVA, edge decembrie an+1, dataLunga → dataRo + gard DATA_DIALECT extins. Prezentare P1–P4.
   RĂMAS vizual (Costin): eticheta de perioadă cu an se vede abia în decembrie (fereastra traversează anul).
4. [x] **Setări cont** — **ÎNCHIS 24.07.2026** (comituri b1878f0 + f700e2d + c7bee1f, vezi ISTORIC 24.07 poz.4). `setari.js` + `cabinet.js`/`asistent.js`.
   3 bug-uri: (1) XSS latent — `esc` local slab în setari.js (nume cheie API în conținut de element) → 5 ecrane mutate pe `esc` canonic + gardă ESC_LOCAL extinsă la redefiniri (DS cap.10); (2) etichete Prenume/Nume inversate — doar etichete UI, datele corecte (verificat auth_api + round-trip); (3) acces lipsă rol asistent — omisiune, deblocat prin gating existent (card ultimul pe dashboard asistent, fără ecran nou). Verificat vizual pe DANTE + cont asistent senior.
   RĂMAS consemnat (colateral, neatins): CARENTE 6 salut asistent `u.nume`→`u.prenume`; CARENTE 5 `padStart` ocolește DATA_DIALECT.
5. [x] **Recomandă** — **ÎNCHIS 24.07.2026** (verificat vizual complet: cabinet + asistent + client via magic-link DANTE; vezi ISTORIC 24.07 poz.5). Două features separate: cabinet `recomanda.js` (`/recomanda`) + client `portal.js/ecranRecomanda` (`/portal/recomanda`).
   Bug reparat: culoare text succes lipsă pe portal client → `.msg-ok`/`.msg-eroare` pe text (commit 0610f32); cabinet avea deja verde via arataMesaj "ok". Colateral: recomanda.js:35 esc canonic (c15a15d).
   RĂMAS: CARENTE 10 — mesaj generic „A apărut o eroare" în previzualizarea admin read-only (Facturare gratuită → Recomandă) + rest Facturare gratuită netestat.
6. [x] **Admin*** — **ÎNCHIS 24.07.2026** (verificat vizual pe cont superadmin real, fără reparații; vezi ISTORIC 24.07 poz.6). 5 sub-ecrane (`admin.js` desktopAdmin: Raportări, Activitate cabinete, Facturare gratuită, Anunțuri, Sănătate server — grafice SVG). Toate randează corect.
   RĂMAS: CARENTE 8 — „bulină roșie = fără răspuns" din Raportări neverificată (lipsă date de test); CARENTE 7 — gating admin inconsecvent (risc mic).
7. [x] **e-Transport** — **ÎNCHIS 24.07.2026** (verificat vizual pe DANTE localhost:8010; vezi ISTORIC 24.07 poz.7). `etransport_ecran.js` + `/etransport-xml`/`trimite`.
   Guard câmpuri required (commit d67b347) dovedit în browser, 5 probe: form gol + „generează"/„trimite" → blocaj cu mesaj per câmp; bun cu denumire goală → blocaj „Bun 1: Denumire marfă" (silent-drop reparat); rând complet gol → ignorat (anti-fals-pozitiv); XML pe disc = 1 `<bunuriTransportate>`, rândul gol absent (validare↔scriere consecvente); namespace `...declaratie:v2`.
   RESTANȚĂ (CARENTE 12): validarea XSD offline blocată — schema v2 nu e pe server. Guard = prezența câmpurilor, nu formate/enum-uri.
8. [x] **Produse** — **ÎNCHIS 24.07.2026** (verificat vizual pe DANTE, cont principal + cont asistent; vezi ISTORIC 24.07 poz.8). `produse_ecran.js` + `/produse` (cere_context).
   FUNCȚIONEAZĂ: stare goală canonică, potrivire AI cotă cu discriminare reală (21% consultanta/capcană, 11% pâine albă, temei art.291 alin.(2)), persistă în DB, ștergere cu confirmare, acces asistent complet.
   RĂMAS (CARENTE 13, sesiune dedicată): C2 refuz tăcut denumire + fără asterisc; C3 `catch {}` gol (salvare eșuată tăcută); C2b fără mesaj succes; minor pret||0; minor `um` nevalidat (DANTE `buc1`); p123 UI editare lipsă (PUT orfan, DECIS păstrat). Rol client pe /produse = restanță DECIS (DE_FACUT).
9. [x] **Tipare** (asistenți) — **ÎNCHIS 24.07.2026** (verificat vizual: patron localhost + asistent nou.iconta.eu; vezi ISTORIC 24.07 poz.9). Două ecrane: `tipare.js` (`/tipare` cere_rol admin_firma) + `asistenti.js` (`/asistenti*` cere_cabinet + `_cer_admin_cabinet`).
   FUNCȚIONEAZĂ: management asistenți (permisiuni, calitate 30z, patru-ochi, firme alocate); „Dezactivează" absent pe propriul card; Tipare sub Activitate → „Tipare de erori", stare goală canonică; asistentul nu vede Activitate/Asistenți.
   PARȚIAL (limită): Tipare cu date reale + F120 (AI) NEVERIFICATE — ecran gol pe DANTE (fără respingeri). RĂMAS: CARENTE 13 C2c (fără mesaj succes la salvare). Notă proces: alarmă falsă auto-escaladare (RBAC enforced via `_cer_admin_cabinet`), patch revertit fără restart.
10. [~] **Semafor** (validat / de validat) — **ÎNCHIS PARȚIAL 24.07.2026** (verificat vizual pe DANTE, patron + asistent, flux complet Declarații pas 1–3 → coadă → aprobare; vezi ISTORIC 24.07 poz.10). `validat.js` + rute coadă `main.py`.
   FUNCȚIONEAZĂ: ecran „De validat" cu stare goală canonică; coada afișează pregătitorul + badge „neverificat"; patru-ochi la nivel de flux (patron pregătește, asistent validează); flagurile valida/depune independente; eroarea de rol e vizibilă, nu tăcută (cap.6).
   REPARAT [A]: delegarea validării — cele 3 rute (`/coada/{id}/aproba|respinge|depune`) treceau de `cere_rol("admin_firma")` cu 403 „rol insuficient" înainte ca poarta fină `_are_permisiune` să conteze (cod mort pt asistenți) → `cere_rol("admin_firma","angajat")` + `_are_permisiune("poate_valida")` pe `/respinge`. Commit c4cb8da, vezi DECIZII 24.07.
   RESTANȚĂ [B] (rămâne [~], nu [x]): declarație cu erori DUK în coadă prezentată ca succes (buton nerestricționat, confirmare cu bifă verde, backend nu re-validează DUK) — decizie AMÂNATĂ, propunere de transparență în DECIZII.md. Colateral: [C] bug generare D300 iulie (`cont` vid); [minor] etichetă perioadă vs termen în coadă.
11. [x] **Pachete lunare** — **ÎNCHIS 24.07.2026** (vezi ISTORIC 24.07 poz.11). (a) calea NEAPROBATA verificată direct pe API (400 `{"detail":"Aproba povestea inainte de trimitere."}`); (b) semnătură reală din DB (nume contabil + cabinet, diacritice), verificată funcțional + în preview (livrarea end-to-end a emailului NU a fost testată în această sesiune); (c) portal client verificat la sursă — **XSS stocat cabinet→client găsit și reparat** (esc pe `p.text`). Plus: poveste alimentată cu restanțe reale, preview = același `_html` ca trimiterea, editor umple modalul, stare colorată canonic. Comituri 293df99/f35c28c/f99c469/09258f1/f0c2d99/aedc4ea. `pachete.js` + `pachete_api.py`.
12. [x] **Capacitate** — **ÎNCHIS ca audit 24.07.2026** (vezi ISTORIC 24.07 poz.12). Panou verificat la sursă (`capacitate_api.py`); reparat `pct_acceptare` pe cohortă (fără negativ prin construcție) + etichete de perioadă (commit 6f6b536). Atribuire firmă↔asistent (`user_tenants`) verificată — există, populată, NU de construit. RĂMAS **stadiul 1** (re-JOIN Capacitate pe `user_tenants`, model SET) — specificat, neconstruit (vezi DECIZII 24.07).

**Pozițiile 11 și 12 închise în sesiunea SSH 24.07.2026** (vezi ISTORIC 24.07 — sesiune SSH). Stările pozițiilor 4–10 sunt cele marcate de FONDATOR în rândurile respective — de confirmat de fondator, NEverificate în această sesiune (nu le presupun închise aici).

## D. Categorii neatacate sistematic (DE_FACUT §3.2) — de decis, nu neapărat de reparat

- [ ] **Spacing/padding inline**: închis explicit ca datorie acceptată (v2.11). Doar de confirmat că nu deranjează vizual.
- [ ] **Wrapper alb pe formulare** (cap.2): verificatorul n-are regulă; prins doar 1 manual. De scanat vizual formularele.
- [ ] **Aliniere tabele** (cap.4): sume la dreapta — neverificat sistematic pe toate tabelele.
- [ ] **Anatomia ferestrei** (cap.1): entitate-antet/titlu-h2-corp — neauditată vizual pe toate.

---

## Ce e DEJA verificat (NU relua)
- Backend/logică/declarații/securitate/provisioning/cron: 555 teste + validare DUK (sesiunea SSH 16.07).
- Gardian mecanic DS: `verificator_conformitate.py` = 0 pe toate ecranele (formatare bani/dată/procent, culori, iconițe, tipografie, borduri/rază, semafor).
- Audit vizual ~22 ecrane deja făcut 14.07 (INCHISE azi în DE_FACUT §Actualizare).

## Bug găsit în sesiune → deschide-l pe telefon/browser și confirmă vizual dacă vrei
- Niciunul din cele 4 bug-uri reparate azi nu e vizual (toate backend). Nimic de re-confirmat cu ochii.

---

## E. F131 Scadențar (construit 17.07) — verificare vizuală

Cardul **Facturi → Scadențar** (și badge-ul roșu pe cardul Facturi):
- [ ] Badge roșu cu nr. de restante apare pe cardul Facturi (dacă există restante).
- [ ] Scadențar: rezumat cu 3 pastile-semafor (restante roșu / scad curând galben / în termen verde), listă sortată pe urgență.
- [ ] Bulinele de stare per factură au culorile corecte (cap.8).
- [ ] Buton „Fișă client" comută la vederea agregată (sold + restant per client).
- [ ] Comutator opt-in (checkbox) — la activare fără email de firmă → mesaj de eroare (nu se activează); cu email → se activează.
- [ ] Supape per factură (când opt-in activ): „nu notifica" / „amână 30 zile" / „reia" funcționează și starea se reflectă.
- [ ] Sume prin `bani()`, date prin `dataRo()` (fără format brut).

Backend/logică deja testate prin SSH (18 teste + funcțional); aici doar randarea.

## F. F136 Adeverință salariat (construit 17.07) — verificare vizuală

Salariați → rând salariat → buton **Adeverință**:
- [ ] Formularul se deschide ca fereastră; câmpuri DS (`.camp`/`.camp-input`), scop marcat obligatoriu (`.oblig`).
- [ ] Caseta de atenție (bancă) apare clar.
- [ ] „Generează PDF" → se deschide PDF-ul; conține firma+CUI, nume+CNP, funcție COR, data angajării, brut+net, vechime, scop, temeiul art. 34(5).
- [ ] Fără scop completat → mesaj de eroare (nu generează).

## G. F135 Pontaj (construit 17.07) — verificare vizuală

Salariați → rând salariat → buton **Pontaj**:
- [ ] Grila arată doar zilele lucrătoare (weekendul + sărbătorile legale, inclusiv Vinerea Mare, lipsesc).
- [ ] Rezumatul (prezent/absent/concediu) se actualizează la schimbarea unei stări.
- [ ] Salariat angajat la mijloc de lună: zilele dinainte de angajare nu apar.
- [ ] Navigarea ← lună / lună → funcționează.
