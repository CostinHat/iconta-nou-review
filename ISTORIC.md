## 20.09.2026 — GARZI cat.1 sub-lotul 1: NOT NULL pe bani + chei naturale UNIQUE pe import

**Pentru un contabil:** două clase de greșeli tăcute devin acum imposibile la nivelul bazei. (1) O sumă
lipsă nu mai poate deveni NULL → 0 nevăzut: coloanele de bani sunt NOT NULL. (2) Datele-cheie importate
(furnizori/clienți pe CUI, asociați pe CNP, solduri pe cont, facturi SPV pe mesaj, articole pe cod de bare,
state de plată pe salariat×lună) nu se mai pot dubla la reimport — au cheie unică. Excepțiile firești
(cursul valutar pe o factură în lei, un client persoană fizică fără CUI) rămân permise, declarat.

**Ce s-a făcut (tehnic).** GARZI cat.1 (Intrare date), LIPSA linia 69-70. Sub-lotul 1 (decizia Costin 20.09,
DECIZII 58): NOT NULL pe 13 coloane de bani (cat. A cu 0 NULL + cat. B cu default 0; 3 candidate excluse la poartă — vezi mai jos); UNIQUE natural pe 8
tabele de import curate — cu trei corecții ridicate la sursă (produse exclus, fără câmp de cod; articole pe
`barcode` nu `cod`; solduri_parteneri pe `(cont, cui)` nu `(cont)`). `core/migrare_intrare_date_garduri.py`
+ tenant_template (aplicat pe 20 scheme reale + baza de test). Gard-ratchet `core/test_intrare_date_garduri.py`
(6 teste: coloană de bani nullable nedeclarată / tabel de import fără cheie nedeclarat PICĂ; whitelist-uri
anti-stale; funcțional UniqueViolation/NotNullViolation; mutație pe template → RED). Sub-lotul 2 (mijloace_fixe)
separat, după curățarea unui duplicat real de cod în tenant_003. Vezi DECIZII (58), GARZI cat.1.

## 20.09.2026 — C5: import extras bancar idempotent (tabel `extras_import`, hash de fișier)

**Pentru un contabil:** dacă reimporți din greșeală același extras bancar (dublu-click, sau conexiunea
a picat după ce serverul salvase deja), aplicația nu mai adaugă liniile a doua oară — îți spune „extras
deja importat: N linii" și nu dublează nimic. Înainte, un reimport dubla toate liniile → notele pe 5121
se dublau. Două tranzacții reale identice în același extras (ex. două comisioane egale în aceeași zi)
rămân amândouă — dedup-ul e pe FIȘIER, nu pe conținutul liniei.

**Ce s-a făcut (tehnic).** Restanța **C5** din auditul independent 2026-09-17, confirmată la sursă +
funcțional (2 importuri identice → 4 rânduri). Decizia Costin (20.09, varianta A): idempotență la nivel
de fișier, pe hash de conținut. (1) Tabel nou `extras_import` (`core/migrare_extras_import.py` +
tenant_template; aplicat pe cele 20 de scheme reale + baza de test) cu `UNIQUE(fisier_hash)`. (2)
`repo_banca.inregistreaza_import` (INSERT ON CONFLICT DO NOTHING RETURNING id — race-safe pe cursa
dublu-click) + `import_existent_nr_linii`. (3) `reconciliere_api.importa_extras` primește `continut`,
hash-uiește, și la reimport întoarce `{"deja_importat": True, "nr_linii": N, "linii": []}` fără să
insereze. (4) Frontend `firme.js`: mesaj vizibil „Extras deja importat: N linii" (nu no-op tăcut). Notă:
`conteaza` bloca deja dubla-contare a aceleiași linii — dublarea notelor venea EXCLUSIV din rândurile
duplicate, deci idempotența la import e fix-ul rădăcină. Garduri `core/test_c5_extras_idempotent.py` (4,
end-to-end pe schemă efemeră; mutație = gard dezactivat → reimport dublează → RED). Vezi DECIZII (56).

## 19.09.2026 — A12b (UI, A12 ÎNCHIS): clasificare destinație TVA per linie pe ecranul de validare SPV

**Pentru un contabil:** la validarea unei facturi primite din SPV (e-Factura), fiecare linie importată
primește acum un selector „destinație TVA" — **taxabilă** (implicit, deducere integrală), **scutită**
(fără deducere) sau **mixtă** (intră în pro-rata, art. 300 alin. (5)). Restul liniei rămâne read-only:
faptul importat din XML nu se editează, doar se clasifică. Alegerea ajunge exact pe achiziția din D300,
deci pro-rata se aplică doar liniilor „mixt". Închide A12 pe calea SPV (partea „UI urmează" din A12 PART A).

**Ce s-a făcut (tehnic).** (1) Regulă DS nouă **cap.28** (clasificare per-linie pe ecran de validare a
documentelor importate) + gard verificator **CLASIF_SELECT** (un `<select>` de clasificare `pr-dest` fără
`aria-label` pică poarta; `.camp-input` e deja cerut de INPUT_NECONFORM). (2) Frontend: `primitaDetaliu`
randează per linie un `<select class="camp-input pr-dest">` (taxabilă/scutită/mixtă, default `selected`),
trimis ca `destinatii[]` în ordinea liniilor. (3) Backend: `factura_primita_valideaza` aplică
`repo_facturi.actualizeaza_destinatii_linii(fid_final, destinatii)` — UPDATE în ordinea liniilor (ORDER BY
id), robustă și la dedup (liniile pre-existente). Valoare în afara setului închis → `ValueError`, nu
scriere tăcută. **Verificat la sursă:** calea „flat" (operatiuni_ecran) e complet separată de
`primitaDetaliu`; din 34 de operațiuni flat, doar 4 creează facturi, toate regimuri speciale (taxare
inversă/IC/neînregistrat/necorporală), niciuna achiziție art.300-general → varianta (a) e suficientă.
Garduri: `core/test_a12b_destinatie_linie.py` (4, end-to-end pe XML real cu 2 linii; mutație ORDER BY
DESC → 2 teste RED, revertită). Vezi DECIZII (55), DESIGN_SYSTEM cap.28.

## 19.09.2026 — A12 (nucleu fiscal): pro-rata TVA doar pe achizițiile mixte, clasificate per linie

**Pentru un contabil:** la o firmă cu regim mixt (pro-rata < 100%), ajustarea de pro-rata se aplică
acum DOAR pe achizițiile marcate „mixt", nu pe tot deductibilul. O achiziție „exclusiv taxabilă" se
deduce integral chiar la pro-rata sub 100%; una „exclusiv scutită" nu se mai deduce deloc (și se
semnalează). Clasificarea e per LINIE de achiziție (`destinație TVA`), implicit „exclusiv taxabilă".

**Ce s-a făcut (tehnic).** Coloană nouă `factura_linii.destinatie_tva` (`core/migrare_destinatie_tva.py`
+ tenant_template; aplicată pe cele 20 de scheme reale). În `d300`, destinația călătorește prin
`_segmente` → bucla `ded`: scutit exclus (art.300 alin.4), mixt izolat → `R31_2` pe `ded_mixt_t` (alin.
3/5/11), nu pe tot `r28_2`. Garduri (test_d300): pro-rata **-42 nu -84** (mutație), taxabil neatins la
pro_rata<100, scutit exclus; DUK valid. LIMITĂ: la TVA la încasare decontările pierd destinația liniei
→ baza pro-rata rămâne r28_2 (combinație rară). Vezi DECIZII (54). **UI (câmpul pe formular) urmează.**

## 19.09.2026 — A9 part 2 (A9 ÎNCHIS): tvaDedAI = TVA pe facturile AI achitate în perioadă

**Pentru un contabil:** câmpul `tvaDedAI` din D394 (TVA dedusă pe achizițiile de la furnizori cu TVA la
încasare) nu mai e 0 fix, ci reflectă **TVA-ul de pe facturile AI plătite efectiv în perioadă** (deducerea
e amânată până la plată, art.297 alin.2). Plată integrală → toată TVA-ul; plată parțială → proporțional;
neplătit → 0.

**Ce s-a făcut (tehnic).** `d394._tva_ded_ai_platite` calculează, în `pull()`, TVA dedusă per cotă din
decontările reale, reutilizând tiparul plăți-AI din D300 (`repo_d300.select_inregistrari_2` = plăți pe cont
401 pe facturi cu `furnizor_tva_incasare`, + `d300._aloca_pe_cote` = apartajarea sumei plătite pe cote) —
SURSĂ UNICĂ, nu a doua interogare. `calcul_d394` rămâne pur (primește `date["tva_ded_ai"]`). Garduri:
plată integrală→210, parțială 605→105, neachitat→0; DUK valid cu tvaDedAI populat. Vezi DECIZII (53).
**A9 (audit R2) e ÎNCHIS** (part 1 tip AI + freeze; part 2 tvaDedAI real).

## 19.09.2026 — A9 part 1: D394 emite tipul AI, iar statutul furnizorului vine din ANAF

**Pentru un contabil:** o achizitie de la un furnizor care aplica TVA la incasare apare acum in D394 cu
tipul corect **AI** (inainte era raportata ca achizitie normala „A"). Statutul „furnizor cu TVA la
incasare" se ia automat din ANAF la introducerea facturii (nu mai depinde doar de bifa manuala), din
serviciul ANAF deja folosit pentru verificarea platitorului de TVA.

**Ce s-a facut (tehnic).** `anaf_api.furnizor_incasare_freeze` (oglinda `platitor_tva_freeze`, aceeasi
sursa `valideaza_cui`→`RTVAI.statusTvaIncasare`), apelat la ingestia facturii primite in
`uc_tenants.factura_creeaza` (inainte de conexiune, ca sa nu tina o conexiune peste apelul ANAF).
`repo_d394.select_facturi` aduce `furnizor_tva_incasare`; `d394.tip_operatiune`→"AI" (art.297 alin.2;
alin.3 exclude taxarea inversa/IC/import). Garduri: `test_d394` (AI vs A, mutatie + DUK valid),
`test_anaf_api` (freeze best-effort). Vezi DECIZII (53).

**Part 2 (in lucru):** `tvaDedAI*` = TVA pe facturile AI ACHITATE in perioada (art.297 alin.2), per cota
— refoloseste tiparul plati-AI din D300. Azi tvaDedAI ramane 0 (corect pentru AI neachitat; DUK valid).

## 19.09.2026 — A11 inchisa: exigibilitatea IC in D300 aliniata la art.284 (ca D390)

**Pentru un contabil:** o factura intracomunitara (achizitie/livrare in UE) intra acum in decontul de TVA
(D300) pe ACEEASI luna ca in declaratia recapitulativa (D390). Inainte, o factura IC cu faptul generator
intr-o luna si factura emisa in luna urmatoare putea aparea in D300 pe luna faptului si in D390 pe luna
facturii — aceeasi operatiune, doua luni, reconciliere ANAF rosie degeaba.

**Ce s-a facut (tehnic).** D300 aplica pe latura IC (partener UE) exigibilitatea art.284 alin.(2) /
art.283 alin.(1) — data emiterii sau a 15-a zi a lunii urmatoare faptului, oricare mai devreme (LEAST) —
nu regula generala art.282 (COALESCE). Expresia traieste intr-un singur loc (`core/d390.py::EXIG_IC`),
folosita de ambele declaratii; `core/d300.py::_exig_d300()` o combina cu regula interna. Gard nou
`test_A11_exigibilitate_IC_d300_aceeasi_luna_ca_d390`, mutatie probata. Vezi DECIZII (52).

**Supersedeaza** consemnarea din 18.09 (mai jos) care lista A11 printre restantele DESCHISE: A11 e acum
INCHISA. A9 si A12 raman deschise, blocate pe decizii de date (sursa `furnizor_tva_incasare` din registrul
ANAF; clasificarea destinatiei achizitiilor pentru pro-rata).

## 18.09.2026 — **da, s-au schimbat patru cifre pe care le depui**

**Pentru un contabil: patru corecții, fiecare la o cifră care pleacă la ANAF.** Toate au venit dintr-un
audit independent al aplicației, iar fiecare a fost reparată cu o probă care merge de la cazul contabil
până în rândul declarației.

- **Dividende (D205): cota se ia după data DISTRIBUIRII, nu după anul depunerii.** Un dividend aprobat
  în 2025 și plătit la începutul lui 2026 se impozitează acum cu **10%** (cota de la distribuire), nu cu
  16% (Legea 141/2025 art. VII: cei care au distribuit interimar în 2025 rămân la 10%, fără recalculare).
  Înainte, o astfel de plată ieșea supradeclarată cu 6% din dividend — cazul cel mai frecvent de la
  început de an.
- **Impozit pe profit (D100): se calculează CUMULAT de la 1 ianuarie.** Plata trimestrială e diferența
  față de ce s-a impozitat deja, iar pierderea unui trimestru scade cumulatul. Un trimestru cu profit
  după unul cu pierdere nu mai plătește 16% pe tot profitul lui, ci pe cumulat (art. 41 Cod fiscal).
- **Import e-Factura: baza liniei ia reducerea și prețul „la mia de bucăți".** Dacă factura UBL are o
  reducere pe linie (`AllowanceCharge`) sau un preț exprimat la o cantitate de bază (`BaseQuantity`),
  baza care intră în D300/D394 e acum cea reală — nu `cantitate × preț` brut, care o umfla.
- **Factură primită cu două cote (21 și 11): TVA deductibilă se face PE COTE.** Nota contabilă a unei
  facturi mixte nu mai aplică cota cea mai mare pe toată baza; 4426 se calculează pe fiecare cotă, iar
  controlul încrucișat cu D300 nu mai iese roșu degeaba.

**Ce s-a mai făcut, și NU se vede din scaunul contabilului:** o recalibrare mare a instrumentelor cu care
mă verific pe mine — scanerele care spun „ce rută atinge o cifră de declarație" și „ce n-are probă"
raportau cifre goale fiindcă erau oarbe pe câteva drumuri (apeluri prin parametru, citiri prin `%s`, nume
prinse dintr-un comentariu). Corectate, iar un clichet care spunea „zero" spune acum „zece", cu cele zece
rute numite. *Nu schimbă nicio cifră pe care o depui; schimbă cât de mult pot minți instrumentele mele
despre aplicație.* La fel, o reparație la o poartă internă care se blocase fiindcă a intrat a doua
jumătate a lunii (o verificare care se activează spre scadența TVA) — invizibilă din afară.

*Restanțe închise în runda asta: A1–A8, A10, B1–B4, C1–C3, E-nota, D1–D10. Restanțe rămase deschise, cu
motiv scris: A9, A11, A12, C4, C5, C6, plafonul micro, CAM pe concediul medical, `salarizare.cam`, și
căile de mașină din §0. Poarta: verde de trei ori azi — `d9de53a2`, `8bf059c2`, `5ff1b8ba`.*

## 17.09.2026, partea a doua — **nu s-a schimbat nimic pentru un contabil**

**Se scrie ca atare, nu se sare.** Restul zilei n-a atins niciun ecran, niciun refuz, nicio cifră și
nicio declarație. Dacă deschizi aplicația azi după-amiază, se poartă exact ca azi-dimineață. *O zi
fără schimbare, nescrisă, se citește peste o lună ca o zi în care nu s-a lucrat — și asta ar fi la
fel de fals ca o schimbare neconsemnată.*

**Ce s-a făcut, și de ce nu se vede din scaunul contabilului:**

- **Aplicația a primit un material de audit independent, publicat.** Tot ce se poate verifica despre
  ea — registrele, cifrele cu instrumentul care le recalculează, lista a ce **nu** e verificat,
  valorile fiscale cu temeiul și data verificării la sursă, măsurătorile brute — stă acum într-un
  singur loc, pe oglinda publică, unde poate fi citit de cineva din afară. *Nu schimbă ce face
  aplicația; schimbă cine poate să verifice ce face.*
- **S-a scris, negru pe alb, ce NU e verificat.** Fără atenuare: cele 53 de restanțe deschise cu
  starea lor, `xfail`-urile cu motivul, orbirea declarată a fiecărui instrument, rutele fără probă,
  și faptul că nicio declarație n-a fost depusă efectiv la ANAF prin aplicație. *Partea asta e cea
  care contează cel mai mult pentru un contabil care ar folosi-o pe date reale, chiar dacă nu se
  vede pe niciun ecran.*
- **Starea proiectului s-a scris ca stare:** lanțul e **în așteptarea folosirii aplicației de către
  Costin**, nu în așteptarea unei teme. Nu se mai alege nimic din backlog; ce iese din folosire
  devine lucrarea următoare.

**Ce s-a reparat, și e o reparație la un instrument al meu, nu la aplicație:** scanul care caută
chei și parole înainte de orice publicare **se număra pe sine** — mostrele lui de calibrare sunt
secrete sintetice scrise cu mâna, iar propria lui ieșire conținea fragmentele care se potriveau cu
tiparele ce le produseseră. Măsurat: 48 de potriviri cu el însuși numărat, 34 fără. *Un instrument
care se măsoară pe sine raportează creșteri care nu există în lumea măsurată.*

*Restanțe închise: niciuna. Restanțe deschise: niciuna. Poarta: verde de două ori, `b56bdca8` și
`d8034c54`.*

## 17.09.2026 — **reevaluarea nu mai poate scădea o amortizare care nu s-a înregistrat**

**Pentru un contabil: da, s-a schimbat ceva, și e un refuz nou.** Dacă reevaluezi un mijloc fix
înainte de a fi înregistrat amortizarea lunilor scurse, aplicația **nu mai trece operațiunea**. Îți
spune de ce, cu cifrele pe masă: *fișa activului arată atât, contul de amortizare are atât, diferența
e atâta* — și îți spune ce să faci: înregistrează amortizarea lipsă, apoi reevaluarea merge.

**De ce e un refuz și nu un avertisment.** Reevaluarea începe prin scoaterea din evidență a
amortizării strânse. Dacă fișa a luat-o înainte, nota ar fi scăzut din cont o amortizare care nu
există acolo — soldul ar fi trecut pe minus, iar valoarea rămasă a activului ar fi devenit o cifră
care **arată bine și e greșită**: se calculează, se afișează, pleacă în declarație, și nimic n-o
contrazice. *Un avertisment ar fi lăsat-o să plece.*

**Și a doua schimbare, tot de azi:** nepotrivirea dintre registrul de imobilizări și contul de
amortizare — găsită ieri pe trei conturi reale — **cere acum confirmare scrisă înainte de depunere**.
Constatarea spune, de la prima frază, că poate numi **contul**, nu activul: amortizarea nu se ține pe
mijloc fix. *Cine o citește află ce are și ce n-are, în loc să caute un activ pe care constatarea nu-l
poate numi.*

*Restanțe închise: R115 (a doua oară), R192. Ambele pe deciziile lui Costin din 17.09.*

## 16.09.2026, partea a patra — **cele patru lucrări numite sunt terminate**

**Pentru un contabil, ce s-a schimbat azi în total, în ordinea în care se simte:**

1. **Reevaluarea unei imobilizări ajunge, în sfârșit, și în declarație.** Până azi fișa activului
   rămânea pe valoarea veche, iar SAF-T-ul anual declara către ANAF costul vechi.
2. **Aplicația compară amortizarea pe care o declară cu cea pe care a înregistrat-o** — și a găsit
   trei nepotriviri pe firmele existente, dintre care una de 900 de lei.
3. **Opt operațiuni care ajung în declarații au acum probă până în cifră**, nu doar până la „a
   mers": ieșire de stoc, inventar, reclasificare, reevaluare, contare bancară, chitanță de casă,
   consum de rețetă, import de firmă. *Nu se schimbă nimic din ce vezi; se schimbă ce nu mai poate
   trece neobservat.*
4. **Trei verificări spuneau că le face validatorul ANAF. Nu le face.** Le facem noi, înainte de
   depunere — și acum scrie corect cine le face. *Dacă cineva s-ar fi bazat pe validator pentru un
   `totalPlata_A` greșit sau o sumă zero pe o declarație inițială, ar fi trecut.*

**Trei lecții de metodă din ziua asta, fiecare plătită:**
- *Un `valid` de la validator nu înseamnă nimic până nu dovedești că valoarea rea era în fișier.*
- *`rollback` nu întoarce o secvență* — singurul lucru care supraviețuiește tranzacției.
- *Poarta rulează arborele de lucru, nu indexul* — un lucru în curs poate înroși commitul altcuiva.

*Restanțe închise azi: R59, R191. Deschise: R192 (așteaptă o decizie de produs), R115 (redeschisă —
tăria constatării noi e a lui Costin).*

## 16.09.2026, partea a treia — **aplicația compară, în sfârșit, amortizarea pe care o declară cu cea pe care a înregistrat-o**

**Pentru un contabil: nu se schimbă nimic din ce vezi azi, dar aplicația începe să-ți spună ceva ce
până acum nu putea.** Amortizarea unui mijloc fix se calculează în două locuri: în fișa activului
(de unde pleacă raportarea SAF-T către ANAF) și în nota lunară care intră în contabilitate. Până azi
nimic nu verifica dacă cele două spun același lucru.

**Acum verifică — și prima rulare a găsit trei nepotriviri pe firmele existente**, dintre care una
mare: o firmă la care fișele activelor spun 3.500 lei amortizare strânsă, iar contul din
contabilitate are 2.600. Cauza obișnuită e simplă și reparabilă: nota lunară de amortizare n-a fost
generată pe una sau mai multe luni. Aplicația o spune acum, cu ambele cifre, și îți zice ce să faci.

**Ce NU face, deliberat: nu blochează nimic.** Constatarea se vede în supervizor și atât. Dacă cere
sau nu o confirmare înainte de depunere e o decizie a lui Costin, pe care n-o iau eu — și până o dă,
constatarea n-are niciun efect asupra depunerii.

**Când refuză să acuze.** Dacă există note încă în ciornă pe contul de amortizare, aplicația spune
*„nu mă pronunț încă"*, nu *„e greșit": diferența se poate închide chiar la validarea lor. La fel
dacă nu poate calcula amortizarea unui activ (metodă nepermisă de lege pe categoria lui) — atunci
propria ei cifră e incompletă, și n-are dreptul să acuze contabilitatea pentru asta.

**Ce a ieșit la iveală construind, și e despre unealta mea, nu despre aplicație:** prima formă a
comparației **tăcea** exact în cazul în care nu putea citi fișele — adică fix când ar fi trebuit să
strige. A prins-o propria ei probă, înainte de orice rulare pe date reale.

*Restanța închisă: R191. Restanță redeschisă: R115 (tăria constatării noi e a lui Costin). R192
rămâne deschisă: confruntarea există, decizia de produs nu.*

## 16.09.2026, partea a doua — **reevaluarea unei imobilizări ajunge, în sfârșit, și în declarație**

**Pentru un contabil: da, s-a schimbat ceva.** Până azi, când reevaluai un mijloc fix, aplicația
scria corect nota contabilă — dar **fișa activului rămânea pe valoarea veche**. Consecința pe care
n-o vedea nimeni: SAF-T-ul anual declara către ANAF **costul vechi**, iar amortizarea lunilor
următoare se calcula tot pe el. Două evidențe despre același utilaj, și nici una nu știa de cealaltă.

**Acum:** reevaluarea se consemnează ca propunere (notă ciornă, ca înainte), iar în momentul în care
**validezi nota**, fișa activului urcă la valoarea reevaluată — și declarația o declară. Măsurat pe
un activ de 3.000 lei reevaluat la 3.500: după ciornă declarația spune tot 3.000 (corect — nimic n-a
fost aprobat încă), după validare spune 3.500.

**Și ceva ce nu se vedea din cerință.** Amortizarea nu continuă pur și simplu pe valoarea nouă: la
reevaluare, amortizarea strânsă până atunci se **șterge** din valoarea activului (așa cere norma
contabilă), deci de la data aceea utilajul se amortizează de la zero, pe valoarea nouă, pe **durata
rămasă**. Dacă am fi urcat doar cifra din fișă, aplicația ar fi socotit amortizare care nu s-a
înregistrat niciodată — o greșeală mai greu de găsit decât cea reparată. Dacă durata normală s-a
epuizat deja, aplicația **refuză** și spune de ce: durata nouă se ia din raportul evaluatorului, nu
o poate inventa programul.

**Ce s-a întrebat pe validatorul oficial.** Un câmp din SAF-T (`AppreciationForPeriod`) era zero de
când există generatorul, iar acum poartă creșterea reală. Validatorul ANAF a fost rulat pe fișierul
nou: **valid**.

**Ce a ieșit la iveală reparând, și rămâne deschis:** cifra pe care nota o șterge din amortizare se
calculează din **motorul de amortizare**, nu din ce s-a înregistrat efectiv. Dacă reevaluezi înainte
de a genera amortizarea lunii, cele două nu coincid. E consemnat ca **R192** și se închide împreună
cu R191 — confruntarea dintre amortizarea declarată și cea înregistrată, care e chiar lucrarea
următoare.

*Restanța închisă: R59, deschisă pe 26.08.2026. Restanță deschisă: R192.*

## 16.09.2026 — **etapa 2 se închide; trei lucruri care schimbă ce vede contabilul, dintre care unul bloca declarația de tot**

**Pentru un contabil: da, azi s-a schimbat ceva, în trei locuri.** Nu e o zi de întărire.

**MIJLOACELE FIXE NU PUTEAU IEȘI DELOC ÎN SAF-T, de două zile.** Ruta care scoate lista de mijloace
fixe pentru D406 răspundea cu eroare la **orice** cerere — nu la una anume, la toate. Cine încerca să
genereze SAF-T-ul cu mijloace fixe nu primea nici fișier, nici un motiv pe care să-l poată citi.
Cauza, în cod: numele coloanelor se citeau **înainte** de a se face interogarea, deci veneau de la
interogarea dinainte sau lipseau cu totul. Reparat, și păzit de-acum: o gardă nouă cade dacă cineva
mai scrie vreodată cele două în ordinea greșită. *Defectul stătea de două zile și nu-l semnalase
nimeni — nu fiindcă nu se folosea, ci fiindcă eroarea era de tipul care nu ajunge la un om.*

**O ACHIZIȚIE INTRACOMUNITARĂ DE SERVICII AJUNGEA PE RÂNDUL BUNURILOR.** În decont, serviciile primite
din UE se declară la rândul 7, bunurile la rândul 5 — două rânduri diferite, cu aceeași sumă
posibilă. Aplicația întreba omul „bunuri sau servicii?" la introducere, **și apoi uita răspunsul**:
nu-l scria nicăieri, iar la generarea decontului totul cădea pe rândul bunurilor. Acum răspunsul se
scrie **pe factură**, ca o coloană a ei, și rămâne înghețat acolo: o factură emisă azi va spune
peste doi ani același lucru, indiferent ce s-a mai schimbat în fișe. *Alegerea a fost a lui Costin, și
motivul ei e mecanic: singura altă sursă posibilă — reclasificarea — ține minte perechea
partener-lună, deci n-ar fi putut despărți două operațiuni ale aceluiași partener din aceeași lună.*

**O VÂNZARE INTRACOMUNITARĂ NU PRODUCEA NICIO FACTURĂ.** Se înregistra ca operațiune, dar nu lăsa
niciun rând în facturi — iar fără rând în facturi nu ajungea nici în decont (rândurile 1 și 3), nici
în declarația 390. Practic: livrarea exista în aplicație și **lipsea din amândouă declarațiile**. Acum
emite factură, ca orice livrare, și s-a probat cap-coadă că ajunge în amândouă.

**Cât de mult s-a schimbat pe portofoliul viu:** deocamdată **nimic de recalculat**, fiindcă nicio
firmă din portofoliu n-are încă o achiziție IC de servicii sau o vânzare IC înregistrată pe calea
asta. Ca și ieri, defectele erau reale în cod și neexercitate în producție. *Diferența e că azi două
dintre ele ar fi produs o declarație greșită, nu una imposibil de generat — iar o declarație greșită
pleacă la ANAF fără să se plângă nimeni.*

**Restul zilei: etapa 2 a campaniei s-a închis.** Cele 29 de unități rămase — locurile prin care o
valoare intră în aplicație și ajunge într-o declarație — sunt acum probate una câte una, pe lanțul
întreg: valoarea intră, se înregistrează, ajunge în rândul corect al declarației cu suma corectă, iar
declarația se generează și trece validatorul oficial. **31 de lanțuri, 29 verzi.** Cele două roșii
n-au fost greșeli ale probei: erau chiar defectele de mai sus.

**Ce a mai ieșit la iveală ieri seară, și se scrie aici fiindcă ziua de ieri s-a consemnat la prânz:**
o **proformă** făcea decontul de TVA imposibil de generat, fiindcă a doua cale de verificare o
număra · o **achiziție intracomunitară** se scria ca fiind din România, deci lipsea din decont · iar
**două ortografii ale aceluiași partener** (cu și fără diacritice) fac declarația 394 de nedepus, și
nimic nu spunea asta înainte de a o trimite. Toate trei, reparate.

**Un lucru pe care l-am aflat greșind, și e de folos oricui atinge zona:** am lărgit interogarea ca să
aducă noua coloană, dar am uitat locul de dedesubt care **enumeră** câmpurile facturii — coloana
venea din bază și se pierdea o linie mai jos, tăcut, iar declarația arăta exact ca înainte. *Un
SELECT lărgit nu e o citire lărgită.* Și, tot azi: proba mea a citit greșit fișierul XML de cinci ori
la rând, iar a patra oară **a suprascris datele reale ale unui asociat** — refăcute din artefactul
probei dinainte. De-aceea fiecare probă are acum două lucruri pe care nu le avea: o verificare că
n-a măsurat în gol, și o desfacere care readuce starea de unde a plecat.

**Ce urmează nu se mai alege.** Costin a numit patru lucrări, în ordine: reevaluarea care nu ajunge la
registrul de amortizare · amortizarea calculată de două ori din surse diferite, fără nimic care să
confrunte cifrele · cele opt locuri prin care se scriu date de declarație fără nicio probă · și cele
opt trimiteri la validatorul oficial care nu se regăsesc în el. După ele nu se deschide nicio temă
nouă.

## 15.09.2026 — **planul E se închide; și, pentru prima dată în etapa asta, se schimbă o cifră pe care o vede contabilul**

**Pentru un contabil: da, azi s-a schimbat ceva** — și merită citit, fiindcă zilele dinainte au fost
toate „nimic vizibil".

**O PROFORMĂ NU MAI INTRĂ ÎN D300.** Până azi, o proformă emisă era numărată ca livrare taxabilă:
măsurat pe o firmă cu o singură operațiune în lună, o proformă de 500 + 105 lei dădea `R9_1=500`,
`R9_2=105`, TVA de plată 105. Iar dacă proforma se transforma apoi în factură, **aceeași operațiune
economică se declara de două ori**, în două luni. Cauza, în cod: interogarea principală a lui D300
filtra pe dată și pe status, dar niciodată pe **tipul documentului** — iar proforma primește un status
declarabil. Tiparul corect exista deja alături: D394 excludea proformele de mult. Acum regula trăiește
într-un singur loc (`nomenclator_status_factura.clauza_tip_document`), iar D300 o cere pe toate cele
patru drumuri ale lui prin `facturi`.

**PARTENERUL DIN D394 SE CITEȘTE DE PE FACTURĂ**, nu din fișa clientului. Până azi, o corectură de CUI
în fișa unui client schimba partenerul dintr-un D394 **regenerat pentru o lună trecută**, deși
documentul emis atunci spunea altceva. Decizia lui Costin, scrisă în registru: *factura e autoritatea;
istoria se corectează prin storno și reemitere, nu prin editarea fișei.* Fișa rămâne rezervă — o
factură veche fără cod fiscal, emisă doar pe `client_id`, și-ar pierde altfel partenerul cu totul.

**Cât de mult s-a schimbat azi, măsurat înainte de a atinge codul:** **zero**. Portofoliul viu are 47
de documente, toate de tip `factura` — nicio proformă, niciun aviz —, și 28 de facturi emise, niciuna
cu CUI diferit de fișă. Defectele erau reale în cod și **neexercitate în producție**. *Dacă
portofoliul ar fi avut proforme, reparația ar fi rescris declarații deja depuse, și ar fi cerut alt
plan — de-aia cifra se măsoară înainte, nu se presupune după.*

**Restul zilei a fost întărire**, fără efect vizibil: planul E s-a închis pe toate etapele lui.
`MODULE_CU_SQL_FARA_STRAT` **78 → 0** (E2a: registrul straturilor s-a lărgit la *orice* modul cu SQL,
cu migrările într-o clasă de excludere numită, nu tăcută) · `REPOSITORY care își deschid conexiunea`
**32 → 0** (E2b: 39 de `commit`-uri scoase din depozite, actul cursului BNR mutat în modulul lui, două
programe CLI plecate în `scripts/`, opt acte etichetate greșit care și-au primit stratul adevărat) ·
cele patru datorii fiscale din registru, **scoase** (E4) · iar subsetul rutelor care scriu în cifre de
declarație, **49 → 8**, cu probe care merg până în rândul declarației, nu până la codul HTTP.

**Două lucruri pe care le-am aflat greșind, și se scriu ca atare.** La E4, „dependența" scrisă în plan
— *o firmă de probă cu profilul potrivit* — **nu exista**: lipseau datele, nu firma, iar ele încap în
câteva rânduri semănate în schema efemeră a probei. Se aștepta de o lună și jumătate după trei
insert-uri. Și, tot la E4: pragul „75 de caractere" din datorie era **vechi** — din 03.08 fiecare câmp
are limita lui oficială, iar garda care conta **sărea** exact peste declarațiile din datorie. *Un test
care sare nu e o verificare, e o intenție.*

**E5 n-a fost închis: a fost mutat.** „Motoarele fiscale se pot citi" nu are criteriu de ieșire —
lizibilitatea nu se termină, fiindcă motoarele se schimbă odată cu legea. A devenit **regula 9** din
`PLAN_LUCRU.md`: un motor deschis pentru altceva se lasă citibil la închidere. *Un pas care nu se
poate închide, ținut în plan ca pas, e o datorie care crește tăcut în dreptul unui plan altfel
terminat.*




## 14.09.2026, partea a doua — **E1: ritmul se numără o singură dată**

Pentru un contabil: nimic vizibil. Aceleași praguri, același refuz, același text. Ce s-a schimbat e
**unde** se numără.

**Ce era.** Trei limitatoare anti-abuz țineau starea în memoria procesului — `_reset_rate`,
`_cui_rate`, `_magic_rate` —, iar funcția care le folosea își scria premisa în docstring:
*„in-memory, **single worker**"*. Premisa murise la P6 valul 3, când unitatea a primit
`WEB_CONCURRENCY=2`. Consecința, măsurată: **prag efectiv dublu** pe trei rute publice (una dintre
ele apără cheia ANAF), contoare golite la fiecare publicare, și un dicționar care nu uita niciodată
un IP — cheiat pe un antet venit din cerere.

**Ce e acum.** `public.cereri_ritm`, cu tiparul scris la P6 pentru `login_esecuri`: un rând per
cerere admisă, fereastra în `WHERE`, ștergerea celor expirate la fiecare scriere, ridicare la bază
căzută. Peste tipar, un lucru nou: un **blocaj consultativ pe `(cheie, ip)`**. La login, două
inserări concurente sunt amândouă adevărate; la ritm, două cereri simultane ar fi putut trece
amândouă de prag. *Cursa nu s-a micșorat, s-a scos.*

**Cum se știe că ține.** Nu din citirea codului: din **două procese reale**. Unul epuizează pragul
pe `/public/magic-link`, celălalt — alt PID, altă memorie — primește `429` la a șasea. Forma
dinainte ar fi răspuns `200`, fiindcă al doilea proces pornea cu dicționarul gol.

**Ce a rămas deschis, și se scrie ca să nu pară închis:** rotația jurnalelor. Fișierul e scris și
verificat (`config/iconta-logrotate`, `logrotate --debug` fără nicio notă), dar instalarea în
`/etc/logrotate.d/` cere root — ca `WEB_CONCURRENCY=2` la P6. Până atunci, `uvicorn.log` crește în
continuare, iar constatarea D3 din audit rămâne DESCHISĂ.

## 14.09.2026 — **planul de întărire P0…P7 se închide formal**

Pentru un contabil: nimic. Nicio linie de cod de producție n-a fost atinsă azi — e o zi de
consemnare, nu de lucru.

**Ce s-a scris.** Cei opt pași P0…P7 sunt marcați `CLOSED_ACCEPTED`, fiecare cu commitul lui final,
într-un tabel la capătul lui `PLAN_HARDENING.md`. Lângă el stau două lucruri care fac diferența
între o închidere și o declarație: **poarta care a lăsat-o să treacă**, copiată din ieșirea
hook-ului (5840 de teste, ruff OK, verificator `TOTAL: 0`, arbore curat), și **cele șase restanțe
care rămân deschise**, fiecare cu cifra ei și cu motivul pentru care nu blochează.

*O închidere care n-ar numi ce rămâne ar fi o cifră flatantă — exact clasa pe care planul o
păzește de opt pași.* Niciuna dintre cele șase n-are lucrare pornită, și niciuna nu contrazice
criteriul pasului ei: `_raspuns` e serializarea mutată la P5 · `D3`=1 e stratul HTTP însuși ·
cele 7 rute GRI sunt clichet, iar GRI nu e verde · cele 6 căi C5 au verdict scris · R178 și R183
sunt proprietăți ale configurației, măsurate, nu regresii.

**Ce rămâne în vigoare:** gărzile. Criteriile celor opt pași nu sunt propoziții dintr-un raport, ci
probe care rulează la fiecare commit.

## 13.09.2026, partea a cincea — **P7 · valul use-case: 385 de corpuri de rută, și faza se ÎNCHIDE**

Pentru un contabil, a cincea oară azi: nu s-a schimbat nimic. Aceleași ecrane, aceleași declarații,
aceleași refuzuri — cuvânt cu cuvânt, și asta nu mai e o promisiune, e o confruntare.

### Ce s-a schimbat, sub capotă

**Cele 385 de corpuri de rută au plecat din `main.py`** în **27 de module `core/uc_*.py`**, împreună
cu **58 de helperi** și **12 nume de modul** pe care le cereau. `main.py`: **11714 → 6546** de linii.
Fiecare rută a rămas la locul ei, cu decoratorul, semnătura și docstringul — FastAPI validează pe
semnătură, deci contractul de intrare e literal același —, iar corpul a devenit o delegare.

Cifra care a ținut faza deschisă două valuri, **`RUTE_CARE_DESCHID_SINGURE_TRANZACTIA`**, a mers
**385 → 73 → 17 → 5 → 0**. Cu ea, **toate cele patru criterii canonice ale lui P7 sunt satisfăcute**,
și faza se închide.

### Ce a făcut posibilă mutarea: un vocabular de refuz

`HTTPException` nu poate trăi în use-case — al doilea criteriu canonic o interzice. Dar decizia care
produce refuzul se ia **înăuntrul tranzacției**, adică exact în codul care pleacă. S-a scris deci
`core/erori.py`: clase care numesc **condiția** (*inexistent*, *fără drept*, *conflict*, *date
invalide*…), iar traducerea condiție → cod HTTP e **o singură hartă**, în stratul HTTP.

**Ce face traducerea sigură e o măsurătoare, nu o speranță:** `HTTPException` **nu e prinsă
nicăieri** — zero `except HTTPException` în tot repo-ul —, deci înlocuirea ei nu poate schimba niciun
flux de control. La fel s-a măsurat că niciun obiect de răspuns nu se construiește înăuntrul unei
tranzacții.

### Ce NU a trecut granița

Obiectele de protocol. Un `Response`/`FileResponse` se construiește tot în înveliș, din valorile pe
care use-case-ul le întoarce (**15 rute**); un `UploadFile` se citește în înveliș și se pasează ca
`bytes` + nume (**12 rute**); gărzile de ritm care se uită la IP-ul cererii rămân deasupra, pe primul
rând (**2 rute**). *Un use-case care vorbește HTTP n-ar fi un use-case.*

Și un al treilea fel de graniță, care n-a fost evident: `_TENANT_TEMPLATE` și `_STATIC_DIR` nu sunt
constante — se **aleg la pornire**, în stratul HTTP. Mutate ca valori, use-case-ul ar fi rămas cu
`None` iar scriitorul cu copia lui: o legătură ruptă pe tăcute, care s-ar fi văzut abia în producție.
S-au mutat invers, și așa e și corect ca strat: **HTTP-ul configurează, use-case-ul consumă.**

### Dovada că nu s-a schimbat contractul

`core/test_p7_uc.py` ia `main.py` **de la commitul dinainte de val** (`git show 43fd2197:main.py`) și
confruntă, **funcție cu funcție**, mulțimile de perechi `(cod HTTP, mesaj)` pe care le ridică —
mesajul comparat ca **arbore**, nu ca text, fiindcă dedentarea schimbă sursa fără să schimbe
valoarea. Trece cu **o singură abatere declarată**, cu motivul scris în fișier: un input-guard
telegrafic (`"suma invalida"`) care a intrat în domeniul regulii G5 odată cu mutarea și și-a primit
constrângerea în mesaj.

*Fișierul acela era citat de două ori în cod înainte să existe — `core/erori.py` și `main.py` îl
numeau ca dovadă a parității. Trimiterea la ceva inexistent se semnalează; aici s-a semnalat
construind lucrul citat.*

### Ce a ieșit la iveală mutând, și e clasa zilei

**Întreaga mașinărie de gărzi doc↔cod era ancorată pe presupunerea că logica aplicației stă în
`main.py`.** Mutând-o, ~40 de gărzi au devenit deodată oarbe sau roșii — nu fiindcă s-ar fi stricat
codul, ci fiindcă se uitau unde nu mai e nimic. Fiecare a fost re-ancorată prin accesorul comun
(`core/scan_sql_efectiv.py`), fără să-și piardă semantica.

**Patru lucruri s-au pierdut tăcut, și fiecare a fost prins de alt instrument:** două gărzi
anti-spam (`_rate_limit_*`) lăsate pe dinafară de mutator · comentariile de pe linia decoratorului,
printre care cinci marcaje `[api_intern_v1]` pe care un instrument le citește ca declarație · și un
RE-EXPORT (`main.pastila_firma`) scos de curățenia automată de importuri, care a lăsat șase firme cu
`control_fiscal` în eroare. Toate patru erau lucruri pe care codul le spunea, iar valul le-a rescris
din ceva care nu le conținea. Fiecare și-a primit garda.

**Iar două scanere aveau `main.py` ca punct orb DECLARAT** (`scan_data_curenta`, `scan_constante`):
valul le-a închis gaura, iar clichetele lor au urcat — nu fiindcă s-a scris cod nou, ci fiindcă
**instrumentul vede mai mult**. Fiecare urcare e scrisă cu lista exactă a cazurilor nou-expuse, și
fiecare caz se regăsește, la aceeași formă, în `git show HEAD:main.py`.


## 13.09.2026, partea a patra — **P7 · valul D4: 215 instrucțiuni mutate, și faza tot nu se închide**

Pentru un contabil, a patra oară azi: nu s-a schimbat nimic. Aceleași ecrane, aceleași declarații,
aceleași cifre. Ce s-a schimbat e unde stă SQL-ul — și ce știm despre cât mai avem de făcut.

### Ce s-a schimbat, sub capotă

Cele **37 de module mixte** — cele care făceau două straturi deodată, de la `core/d223.py` cu o
instrucțiune la `core/control_incrucisat.py` cu 45 și `main.py` cu 38 în helperii de modul — și-au
dat cele **215 instrucțiuni SQL** la **37 de `core/repo_*.py`**. `D4` **37 → 0**.

Mutarea a fost făcută de un instrument, `scripts/p7_d4_separa.py`, nu cu mâna. Motivul e o
măsurătoare, nu o preferință: 215 poziții în 13 forme diferite de loc, iar modul de eșec al unei
mutări manuale — parametri schimbați de ordine, un `fetchone` devenit `fetchall`, un `%s` pierdut —
**nu se vede la citire**. Instrumentul mută expresii, nu text; ce nu poate rezolva mecanic
raportează și lasă neatins. **Rest: 0 din 215.**

**Dovada că s-a mutat, nu s-a rescris:** amprenta SQL a întregului cod de producție — **1050
instrucțiuni distincte, 1307 în total** — e identică înainte și după.

### Partea care merită citită: cifra care arăta bine

După val: `D1`=0, `D2`=0, `D4`=0, **`P7_ACTION_REQUIRED`=0**. Citită singură, cifra spune că faza s-a
terminat. **Nu s-a.** Textul canonic cere patru straturi, iar despre use-case spune că *deține
tranzacția (P4) și orchestrează*. Măsurat: **385 din 421 de rute își deschid singure tranzacția**,
doar **7** deleagă către un modul `USE_CASE`, iar use-case-uri declarate sunt **4**.

*Un `ACTION_REQUIRED=0` care nu acoperă un criteriu canonic nu e o stare, e o lipsă de detector.* Am
închis golul cu un instrument și o gardă, nu cu o propoziție în predare: `scripts/p7_criterii.py`
măsoară toate patru criteriile, iar `core/test_p7_criterii.py` ține clichetul celor 385 **și
interzice planului să declare P7 închisă peste el**.

### Ce a mai scos valul, și toate trei sunt aceeași clasă

1. **O justificare ancorată prin vecinătate nu se mută cu codul.** Trei `ON CONFLICT DO UPDATE` au
   trecut în depozit, iar `# upsert-ok:` a rămas în modulul vechi. Prins de `test_upsert_motivat` la
   prima rulare — de instrument, nu de mine.
2. **Instrumentul traseelor a tăcut din nou**, a doua oară în două valuri: 12 adnotări deodată.
   Reparat cu **perechea nominală** modul ↔ `repo_<același nume>`.
3. **Citările în plan s-au mutat iar** — 8 ancore. De data asta reparate cu un instrument,
   `scripts/reancoreaza_plan.py`, care a greșit el însuși de două ori înainte să meargă: cerea
   unicitatea fragmentului pe tot planul, și lua reperul din fișierul deja editat.

### Cifre

`D4` **37 → 0** · `P7_RAW_ITEMS` **38 → 1** · `P7_ACTION_REQUIRED` **37 → 0** · straturi declarate
**167** (96 `FISCAL_ENGINE` · 65 `REPOSITORY` · 4 `USE_CASE` · 2 `HTTP`). Criteriul rămas:
**385/421**. Poarta: **5795 verzi / 0 roșii** · 12 sărite · 14 xfail ·
verificator **TOTAL 0**.

**P7 RĂMÂNE DESCHISĂ.** *Zero pe toate detectoarele nu e zero pe fază.*
