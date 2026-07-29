# TESTE.md — planul de testare pe flux

**29.07.2026.** Registrul campaniei de testare a aplicației, organizată pe **ordinea în care
se produc faptele contabile**, nu pe module.

---

## De ce pe flux, nu pe zone

Campania din iunie a testat pe **zone** (ecrane, module): 17 zone, ~190 de teste, verde.
Nu a fost destul, și se vede din ce a scăpat:

- **D101** a trecut testele de zonă pentru că nimeni n-a verificat că registrul *de sub el*
  avea rânduri.
- **D301** avea zero teste și un rollup fiscal lipsă (S4.1→S4). Declarația era respinsă de
  ANAF pe cazul cel mai frecvent — servicii UE — dar defectul nu se putea vedea, pentru că
  nu exista nicio cale de a introduce datele.
- **D112** emitea o declarație cu salarii ZERO când o coloană dispărea din schemă:
  `SELECT *` nu crapă, rândul iese fără cheie, `get()` dă `None`, iar absența e tratată
  legitim ca 0.
- **D300/D301** erau nedepunabile pentru 2 din 3 firme (lipsă bancă/IBAN), iar verificarea
  exista în cod și nu era chemată niciodată.

Zonele ascund **propagarea**. Un test pe flux o urmărește.

## Regula cascadei

**Un eșec la etapa N invalidează toate rezultatele de la N+1 în jos.**

Nu ai voie să declari „D300 verde" dacă etapa 5 (contabilizare) n-a fost dovedită pe
aceleași date. Verdele de la o etapă se câștigă doar pe temelia dovedită a celei dinainte.

## Regula bazei nule

**Orice declarație cu bază 0, zero linii sau total 0 e EROARE până la proba contrară.**
„Fără activitate" se declară EXPLICIT (firma F7), nu se deduce din tăcere.

DUKIntegrator validează STRUCTURA, nu conținutul. Nu e gard de conținut și nu se tratează
ca atare. Dovedit de trei ori: D101 (bază zero din query rupt), D406 (registru gol sub
mască), D112 (salarii zero din coloană dispărută) — toate treceau validatorul.

---

# Partea I — Firmele de test

## De ce șapte

Setul e derivat din **legislație**, nu din ce am construit. Dimensiunile care produc
comportament diferit în aplicație, și temeiul fiecăreia:

| Dimensiune | Valori | Temei |
|---|---|---|
| Sistem contabil | partidă dublă / partidă simplă | L 82/1991; OMFP 1802/2014; OMFP 170/2015 |
| Regim TVA | neplătitor · lunar · trimestrial · la încasare · art. 317 | CF art. 310, 316, 317, 322, 282(5) |
| Impozit | micro 1%/3% · profit 16% · PFA real · PFA normă | CF Titlul II, III, IV |
| Operațiuni | achiziții IC · servicii UE · taxare inversă · salariați · fără activitate | CF art. 307, 331; OUG 158/2005 |

Ele se **combină**, dar nu toate combinațiile produc cod diferit. Șapte firme acoperă toate
ramurile distincte, fără dubluri.

## Setul

| ID | Formă | TVA | Impozit | Ce testează UNIC |
|---|---|---|---|---|
| **F1** | SRL | lunar | micro 1% | comerț cu stoc, 3 salariați, descărcare de gestiune, D300 lunar, D394, D112, D101, D406 |
| **F2** | SRL | trimestrial | profit 16% | D300 **trimestrial**, D100, amortizare, mijloace fixe, registru de casă |
| **F3** | SRL | neplătitor + **art. 317** | micro 3% | **D301** (achiziții IC bunuri + servicii UE tip 5), **D390**, taxare inversă |
| **F4** | SRL | **TVA la încasare** | micro | exigibilitate la încasare — logică complet separată de cea normală |
| **F5** | PFA | plătitor | **sistem real** | partidă simplă, RIP, **D212**, D710, contribuții PFA |
| **F6** | PFA | neplătitor | **normă de venit** | fără evidență de venituri, doar D212 pe normă |
| **F7** | SRL | plătitor | micro | **fără nicio operațiune** — singura care are voie să dea bază 0 |

**Două cabinete**, ca să se testeze și izolarea între cabinete, nu doar între firme:
- **Cabinetul A** — F1, F2, F3, F7
- **Cabinetul B** — F4, F5, F6

## Ce trebuie să aibă fiecare firmă

Un **an fiscal complet** (2026), cu cifrele așteptate **calculate de mână** din surse
oficiale, înghețate într-un fișier de așteptări.

**Fișierul de așteptări se scrie ÎNAINTE de a rula aplicația pe date.** Altfel copiezi
output-ul și testezi că 1 = 1.

Pentru fiecare firmă și fiecare lună: soldurile din balanță, totalurile din jurnalul de
TVA, statul de plată, și fiecare declarație datorată — cu temeiul legal notat lângă cifră.

---

# Partea II — Cele 11 etape

Pentru fiecare: **invariantul** (ce trebuie să fie adevărat la ieșire) și **capcana**
(modul cunoscut de eșec tăcut, din cele întâlnite deja).

## 1. Migrare / preluare firmă

Sold inițial, plan de conturi, parteneri, stocuri, mijloace fixe, RIP (la PFA),
pre-fill ANAF v9.

**Invariant:** Σdebit = Σcredit pe soldul preluat; nr. rânduri importate = nr. rânduri din
fișier − duplicate raportate explicit.

**Capcană:** import „reușit" cu 0 rânduri; dedup care înghite tot; schema tenantului nou ≠
`tenant_template.sql`.

**Firme:** toate. F5/F6 testează RIP.

## 2. Configurare firmă

`tip_firma`, regim TVA și perioadă fiscală, vector fiscal, an fiscal, utilizatori, roluri.

**Invariant:** fiecare combinație de regim produce exact setul de straturi și declarații
așteptat (`straturi_pentru`, `regim_efectiv`).

**Capcană:** regim schimbat retroactiv care rescrie tăcut trecutul. `tip_firma` e
needitabil după creare — verificat 27.07, e restricție corectă.

**Firme:** toate șapte produc vectori fiscali diferiți. Ăsta e testul care le distinge.

## 3. Intrare documente primare

Facturi emise/primite, e-Factura primite, extras bancar, casă, Raport Z, NIR/stocuri,
documente fotografiate.

**Invariant:** fiecare document ajunge la exact o intrare în registru; totalul documentelor
lunii = totalul din listă = totalul din raport.

**Capcană:** parser care întoarce 0 linii tratat ca „lună fără documente"; semn inversat;
document dublat la reimport.

**Firme:** F1 (stoc, NIR), F3 (achiziții IC), F4 (exigibilitate la încasare).

## 4. Salarizare

Contracte, stat de plată, concedii medicale, part-time, fluturași, tichete.

**Invariant:** brut − reținute = net pe fiecare salariat; Σ stat = Σ rulaj
421/4315/4316/444/436.

**Capcană:** salariat exclus tăcut din stat (flag prost citit) → D112 corect structural,
incomplet real. **Sau coloană dispărută din schemă → salarii ZERO** (dovedit 27.07;
acoperit acum de `common.cere_coloane_cursor`).

**Firme:** F1 (3 salariați, unul cu CM), F5 (contribuții PFA).

## 5. Contabilizare

Motor, note automate, note manuale, patru-ochi, stornare.

**Invariant:** Σdebit = Σcredit per notă și per perioadă; nicio notă validată fără
document-sursă; storno = oglinda exactă.

**Capcană:** notă rămasă ciornă → nu intră în rulaj → **exact mecanismul bazei zero**.

**Firme:** toate cu activitate.

## 6. Operațiuni de sfârșit de lună

Închidere TVA, amortizare, descărcare de gestiune, diferențe de curs, închidere de an.

**Invariant:** după închidere, 4426/4427 sold 0; stoc cantitativ ↔ valoric coerent.

**Capcană:** operațiune rulată de două ori; rulată pe lună închisă.

**Firme:** F1 (descărcare gestiune), F2 (amortizare), F3 (diferențe de curs la IC).

## 7. Verificări interne (control fiscal)

Semafor, control încrucișat, alerte, monitor fiscal.

**Invariant:** pe firmă cu eroare **injectată deliberat**, verificatorul o GĂSEȘTE; pe
firmă curată, verde cu motiv explicit.

**Capcană:** gri raportat ca verde; verificator care compară o funcție cu ea însăși.

**Firme:** toate. F7 e cazul-limită (verde pe zero, cu motiv).

## 8. Declarații — generare

Toate declarațiile datorate, pe toate cele 7 firme, toate lunile anului.

**Invariant:** fiecare cifră din XML = cifra calculată de mână în fișierul de așteptări.
**Bază 0 doar la F7.**

**Capcană:** cea din 27.07. Query rupt → generator gol → XML valid. Sau ramură scrisă și
niciodată executată (D301 tip 5).

**Firme:** toate. Matricea firmă × declarație × lună e nucleul campaniei.

## 9. Declarații — depunere

DUKIntegrator, SPV, D710 rectificativă.

**Invariant:** declarația depusă se stochează cu hash; regenerarea produce același hash sau
se raportează diferența.

**Capcană:** DUK tratat ca dovadă de conținut. **Nu e.** Plus: validare care nu rulează
deloc și raportează gri permanent (dovedit 27.07 la D406 — `an`/`luna` nepasate).

## 10. Ieșiri externe

SAGA, WinMentor, D406, rapoarte, portal client, export GDPR.

**Invariant:** totalurile din export = totalurile din aplicație, calculate pe **a doua
cale** (nu aceeași funcție).

**Capcană:** rută inaccesibilă (a mușcat deja la SAGA); encoding; denumire de fișier.

## 11. Transversal (rulează la FIECARE etapă, nu la sfârșit)

Izolare tenanți, acces/roluri, integritate în timp, backup + **restaurare**.

**Invariant:** două firme cu date identice, citire încrucișată → 0 rânduri; apel
neautentificat → 401; obiect din alt tenant → 404; restaurare din off-site reproduce baza.

**Capcană:** `search_path` nesetat; constrângere nescopată la `current_schema()` (a mușcat
la `salariati_cnp_uniq`); job de fundal pe tenantul greșit.

---

# Partea III — Cele trei niveluri

| Nivel | Ce dovedește | Regula |
|---|---|---|
| **N1 — calcul pur** | formula fiscală | fără DB, fără fake; cifre din exemplul oficial |
| **N2 — integrare pe DB reală** | granița cod ↔ bază | Postgres real, INSERT + ROLLBACK; **fake interzis pe `core.d*`** |
| **N3 — cap-coadă pe firmă de test** | că fluxul întreg produce adevărul | pornește de la import, termină la XML validat |

Cele ~1049 de teste actuale sunt aproape toate N1. N2 a apărut pe 27.07
(`test_pull_declaratii.py`). **N3 nu există** — e ce construiește campania asta.

---

# Partea IV — Ordinea de execuție

## Faza 0 — curățenie (blocantă)

Ștergerea completă a datelor actuale: firme, cabinete, utilizatori. Tot ce e acum e de
test, nimic real. Fără asta, se construiește peste resturi.

## Faza 1 — cele 7 firme

Creare prin **interfață**, ca un contabil care intră prima dată — nu prin script. Așa se
testează etapele 1–2 și se prind problemele pe care le vede omul, nu doar baza.

Fișierul de așteptări se scrie **înainte**.

## Faza 2 — etapele 3→11, în ordine, cu regula cascadei

Fiecare etapă se închide înainte de a începe următoarea.

## Faza 3 — gardurile care împiedică regresia

Ce s-a găsit devine test permanent. Vezi `GARZI.md` pentru categoriile de eșec și starea
fiecărui gard.

---

# Partea V — Cum se consemnează

- **Rezultatul fiecărei etape** se scrie aici, în tabelul de mai jos, cu data.
- **Defectele găsite** intră în `DECIZII.md` cu cauza, nu doar cu simptomul.
- **Ce nu se repară imediat** devine `xfail(strict=True)` în `core/test_datorie.py` — NU
  notă într-un fișier. Un registru pe care trebuie să ți-l amintești nu funcționează.
- **Gardurile noi** se consemnează în `GARZI.md`, în aceeași zi.

## Starea campaniei

| Etapă | Stare | Data | Observații |
|---|---|---|---|
| Faza 0 — curățenie | | | |
| Faza 1 — cele 7 firme | | | |
| 1. Migrare | | | |
| 2. Configurare | | | |
| 3. Documente primare | | | |
| 4. Salarizare | | | |
| 5. Contabilizare | | | |
| 6. Sfârșit de lună | | | |
| 7. Verificări interne | | | |
| 8. Declarații — generare | | | |
| 9. Declarații — depunere | | | |
| 10. Ieșiri externe | | | |
| 11. Transversal | | | |

---

## Reguli de lucru pentru această campanie

1. **Verificare la sursă înainte de orice afirmație.** Valorile fiscale se verifică la
   ANAF/lege, nu din memorie. Trigger: „lipsește", „nu există", „e greșit".
2. **Proba pe date reale.** Nicio etapă nu e „gata" pentru că trece validatorul sau pentru
   că testele sunt verzi. Un test care rămâne verde când generatorul întoarce `[]` nu
   testează nimic.
3. **Ancorele se citesc din fișier, nu se scriu din memorie.**
4. **Nicio comandă de commit fără poartă** — pe suită ȘI pe proba funcțională.
5. **Nu se repară pe suspiciune.** Se măsoară întâi. Pe 27.07, „float pe bani e greșit" era
   adevărat ca principiu și fals ca diagnostic: 0 din 5000 de valori pierdeau precizie.
