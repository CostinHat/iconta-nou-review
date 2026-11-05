# CLAUDE.md — Regulile permanente ale lui Code pe iConta

Versiune: 05.11.2026 (16.4). Acest fișier e citit automat la fiecare pornire și după fiecare /clear.
Este SINGURA sursă de reguli de lucru pentru Code. Orice regulă de proces care nu e aici e radiată,
oriunde ar fi scrisă (vechiul CLAUDE.md, PLAN_LUCRU.md, PREDARE_LANT.md, DECIZII.md, memoria permanentă,
comenzi vechi). DECIZII.md rămâne istoric (de ce s-a decis), nu normă.

O regulă nouă intră numai aici, în secțiunea ei, iar cea pe care o înlocuiește se șterge din acest fișier
în același commit. Nu se adaugă reguli alături de cele vechi.

## 0. La pornire și după /clear

Înainte de orice altceva, Code citește PREDARE_LANT.md (unde a rămas lucrul) și comanda în curs, din
~/ghid_incoming/. Nimic altceva nu e obligatoriu de citit: regulile sunt toate în acest fișier.

R9. La începutul fiecărui lot: /clear, apoi citești CLAUDE.md, comanda lotului și corectii_<lot>.txt dacă există. Nu pornești un lot cu contextul lotului anterior.

## 1. Rolurile

Costin decide direcția și produsul. Arhitectul (Claude în chat) decide arhitectura și formulează comenzile.
Code execută și decide singur tot ce ține de implementare: fișiere, structură, ordine, forma testelor.
Comanda spune ce trebuie obținut, nu cum.

## 2. Ținta curentă

Pilotul: o lună completă de contabil, cap-coadă, pe o firmă (SRL de comerț cu salariați), fără deficiențe
grave — cele 43 de poziții marcate „pilot” în planul de testare. Până atunci nu se construiesc funcții noi.
Exporturile spre SAGA/WinMentor se amână până după pilot.

Pilotul are un scenariu automat al lunii complete a firmei-pilot, parcurs pe ecran ca un contabil, cu
cifrele exacte așteptate la fiecare pas, până la declarații. Scenariul crește cu fiecare poziție pilot
rezolvată și rulează permanent în poartă. Pilotul e atins când scenariul e verde de la cap la coadă.

## 3. Lotul

Lotul e unitatea de lucru, de publicare și de raport. Comenzile poartă numărul lotului (12.1, 12.2…).
Code duce lotul până la capăt: ce nu poate rezolva singur trece în raport și continuă cu restul; deciziile de pe parcurs le
ia pe varianta cea mai sigură și le listează în raport, la E (Abateri). Nu se trece la nimic din afara comenzii (nici agendă,
nici fir intern, nici „următorul pas din listă”). Poarta de publicare, jurnalul și publicarea sunt scripturi; scriptul e regula, textul doar o numește (comanda 16.1):
- Baza: `sh scripts/poarta_lot.sh --baza` rulează poarta completă pe un worktree curat al commitului de bază și scrie docs/dovezi/<lot>/baza.json (rezultat, durată și
  aserțiuni pe test; sha-ul bazei, hash-ul manifestului, snapshotul, mediul). Fără baza.json, cu alt merge-base sau cu alt manifest, poarta refuză.
- Poarta: `POARTA_PLASA_FIX=scripts/plasa_16_2.manifest sh scripts/poarta_lot.sh` (scripts/poarta_rulare.py): verificator, pytest (nucleul + testele atinse), plasa e2e din
  manifest, baza restaurată înainte de pytest și înainte de plasa e2e (niciodată per test), toate treptele rulează, și după una roșie. Clasificarea o scrie poarta
  (scripts/poarta_clasifica.py): regresie de lot, restanță numerotată, test nou, test invalid, eroare de infrastructură (reluată o dată, apoi oprire). Un test roșu și pe
  bază, nenumerotat în scripts/poarta_e2e_restante.txt, oprește lotul: baza s-a mișcat; a doua regresie de lot nouă oprește lotul. „Zero restanțe” = zero picături
  neclasificate și nenumerotate, nu zero picături absolute. Selecția veche după fișiere atinse există numai ca diagnostic (`POARTA_DIAGNOSTIC=1`), niciodată pentru publicare.
- Reluarea după roșu: `sh scripts/poarta_lot.sh --reia` rulează numai numele picate și testele fișierelor schimbate de la commitul roșu; cel mult două pe lot; refuză
  (cu numele fișierului) orice fișier din `git diff --name-only <roșu>..HEAD` care nu era în diff-ul lotului la commitul roșu, nu e al unui test picat (cu aserțiunile
  nescăzute față de bază) sau nu e în ~/ghid_incoming/exceptii_<lot>.txt (scris de arhitect; un rând = fișier + motiv; hash-ul în jurnal). Reluarea e diagnostic, nu rulare
  completă. Cu cel puțin o reluare, raportul are secțiunea „diff-ul reluărilor” și fraza de risc din scripts/publica_lot.py. Verdictul de publicare îl dă numai rularea completă
  finală (cel mult două pe lot; a treia numai cu rândul „rulare_completa 3 | motiv: …” din exceptii_<lot>.txt, o singură dată, hash în jurnal), cu zero regresii de lot; picături
  noi la o reluare opresc lotul, nepublicat. Regula strămoșului (`publica_lot.py --verifica <C> <HEAD>`): verdictul și rândurile jurnal_verificare.csv produse pe C (ultima rulare
  completă) sunt valabile pentru HEAD dacă C e strămoș al lui HEAD și `git diff --name-only --no-renames C..HEAD` atinge numai jurnal_verificare.csv (rânduri adăugate), capturi/*.png (din orice director capturi/ al lotului), *.pdf (descărcate de parcurs) și *.out (ieșirile lansatorului, numai adăugate, niciodată modificate)
  exact sub docs/dovezi/<lot>/<parcurgere>/<verificator>/ (nu direct în docs/dovezi/<lot>/, nu mai adânc), registre_<lot>.md, DEFICIENTE.md, DECIZII.md, PREDARE_LANT.md. Raportul numește C (commitul verificat); HEAD e în verdictul PASS. Commiturile de după C ating numai dovezile și registrele, niciodată CLAUDE.md.
  Hook-urile reference-transaction și pre-push acceptă VERDE pe C numai cu PASS pe HEAD care numește C și trece aceeași funcție `--verifica`; fără PASS pe HEAD refuză.
- Baza lotului: fiecare lot de unelte sau de produs își are baza lui (docs/dovezi/<lot>/baza.json); un lot de corecție fără bază proprie moștenește baza lotului de bază (`poarta_lib.lot_baza`).
- Oracolul pașilor (16.1-C3): pasi_<lot>.txt din ~/ghid_incoming (scris de arhitect; rând: „aserțiune | pas | ecran | operator | valoare | descriere | sursă”, operatori egal / contine / nr_randuri / lipseste / interval_px / activ / text_contine) are hash-ul în rândul „pornire” (scris de coadă); docs/dovezi/<lot>/pasi.json copiază literal operator și valoare ale fiecărei aserțiuni și adaugă „cheia” lui Code; scripts/verifica_pas.py compară numai operator + valoare cu ce citește prin cheie din pagina vie (`dom:<selector>|<măsură>`, `json:<url>|<cale.in.json>`, `pdf:<url>` sau `pdf:fisier:<cale>`); publica_lot.py refuză cu STOP „oracol modificat” (aserțiune lipsă, în plus sau diferită, hash schimbat). Un lot de produs cere fișierul; lotul de unelte fără fișier nu are oracol.
- Parcursul (16.3): un lot de produs are docs/dovezi/<lot>/parcurs_<lot>.py cu punctul de intrare fix `ruleaza(pagina, ctx)`. Acțiunile (deschide fereastra, scrie, bifează, apasă, descarcă prin clic) le scrie Code, în docs/dovezi/<lot>/; așteptările le scrie arhitectul, în pasi_<lot>.txt; compară și marchează numai scripts/verifica_pas.py (`verifica_pagina`); lansează numai scripts/lanseaza_verificator.py --verificator code|haiku. Parcursul importă numai playwright, biblioteca standard și verifica_pas.py (orice alt import = refuz la lansare, cu numele modulului) și nu scrie verdicte. Fiecare rând din jurnal_verificare.csv (unul pe aserțiune; coloana „pas” = id-ul aserțiunii) are marcaj HMAC scris de verifica_pas.py; `publica_lot.py --verifica` și publicarea refuză rândurile fără marcaj valid (STOP „verdict în afara oracolului”; scutite, în lista fixă din publica_lot.py: 16.1, 16.1-C2, 16.1-C3). Captura nu se suprascrie: docs/dovezi/<lot>/<parcurgere>/<verificator>/capturi/<lot>_<parcurgere>_<pas>_<sha8>.png (parcurgeri: inainte, dupa, haiku_1, haiku_2; verificator: code sau haiku); cheia de unicitate a unui rând e (lot, parcurgere, pas, sha, verificator), iar `jurnal_verificator.sh controleaza` judecă după cheie, existența capturii și marcaj, nu după mtime. Un parcurs pornește numai prin lanseaza_verificator.py; Code nu rulează Playwright pe 8019 altfel.
- Verificatorul independent (16.3): Haiku 5.5 judecă fiecare aserțiune față de coloana „descriere” și de captură (Read numai pe directorul capturilor lui) cu una din trei: corespunde / nu corespunde / nejudecabil din captură (aserțiunile cu operator interval_px sau cu cheia pdf: sunt automat nejudecabile: lansatorul nu le dă agentului și scrie direct „nejudecabil din captură (pdf)”, cu marcaj; publica_lot.py le exclude din numărătoarea „neefectuată” prin cheie și operator, nu prin textul răspunsului, iar verdictul oracolului „pică” pe una dintre ele pe C rămâne STOP); răspunsul stă în coloana „verificator_independent”. La „nu corespunde” pe o aserțiune cu verdictul „trece”, o a doua instanță Haiku, cu context proaspăt și numai cu aserțiunea și captura ei, răspunde în „verificator_independent_2” (același rând, nu rundă nouă); STOP la publicare („dezacord oracol–verificator”, aserțiunea numită) numai dacă și a doua spune „nu corespunde”. Dacă toate aserțiunile judecabile (în afara celor cu interval_px sau pdf:) sunt „nejudecabil”, faza e „neefectuată” = STOP. Faza „verificator” o scrie lansatorul, nu mâna: scripts/lanseaza_verificator.py scrie în jurnal (implicit jurnalul comun, sau --jurnal), cu marcaj HMAC pe rând (cheia ~/.iconta/cheie_oracol), „verificator | inceput” înainte de parcurs și „verificator | sfarsit” după răspunsul ultimei instanțe Haiku (rezultat „parcurs” = toate răspunsurile primite; „intrerupt” = lansatorul a ieșit cu eroare), cu numărul aserțiunilor corespunde / nu corespunde / nejudecabil în detalii; la --verificator code scrie la fel faza „parcurs_code”. La un lot „produs”, publica_lot.py refuză cu STOP „faza verificator scrisă de mână” orice fază „verificator” fără marcaj valid (scrisă cu jurnal_verificator.sh sau cu textul marcajului copiat) și, la publicare (nu la `--verifica`), cu STOP „fără verificator independent pe C” un jurnal_verificare.csv fără nicio parcurgere cu verificator=haiku pe C; la un lot „unelte” faza și parcurgerea nu se cer. Coloana „descriere” din pasi_<lot>.txt al unui lot de produs nu conține cuvintele trece / pică / corespunde (publica_lot.py refuză; fișierul de probă al lotului de unelte le conține, pentru calibrare). Lansatorul instalează un handler SIGTERM înainte de începutul fazei („verificator” sau „parcurs_code”): un lansator oprit cu SIGTERM iese normal (143) și scrie sfârșitul cu rezultat „intrerupt”, marcat; la SIGKILL nu se scrie nimic, iar `faze_stop` dă STOP pe un început fără sfârșit (calibrat în core/test_faze_verificator_16_4.py și scripts/calibreaza_16_4.py, 16.4 pct.2).
- Lista permisă a lotului „unelte” (16.3): `publica_lot.py --verifica` și publicarea refuză, cu numele fișierului, orice fișier din static/, core/ (în afara testelor core/test_*.py), templates/ sau frontend_test/ al diff-ului unui lot „unelte” care nu e numit în scripts/praguri_<lot>.txt; permise implicit: scripts/, scripts/githooks/, frontend_test/e2e/conftest.py, CLAUDE.md, DEFICIENTE.md, DECIZII.md, PREDARE_LANT.md, docs/dovezi/<lot>/. La un lot „produs” lista `fisiere_permise` din scripts/praguri_<lot>.txt se aplică pe diff-ul merge-base..HEAD (`--verifica` și publicarea): orice fișier din afara ei = refuz cu numele (liniile listei sunt fișiere sau directoare cu „/” la sfârșit; textul dintre paranteze se ignoră; „CLAUDE.md (numai inainte de C)” = permis în diff-ul merge-base..C, refuzat după C); praguri de «produs» fără listă = refuz.
- Contractul la început (16.1-C3): `publica_lot.py --proba <lot>`, declanșat de scripts/githooks/post-commit pe ramurile lucru/* la primul commit după merge-base cu main, verifică rândul pasului a) din jurnal_verificare.csv (există, captura există, verdict „trece”, sha = commitul de bază) și scrie faza „proba_contract”; fără ea verde = STOP la publicare. Un lot „unelte” fără docs/dovezi/<lot>/pasi.txt trece verde cu eticheta „unelte, fără oracol”; un lot de produs fără rândul pasului a) rămâne roșu.
- Lacătul (16.1-C3): ~/.iconta/lacat_test (pid + ora de start din /proc; pid mort sau refolosit = preluat; reentrant prin LACAT_TEST_PID) ține iconta_test și 8019; îl iau poarta_lot.sh, baza_test.sh salveaza/restaureaza și scripts/lanseaza_verificator.py (lansatorul parcursului și al verificatorului independent: Haiku 5.5, fișierele date, parcursul prin verifica_pas.py, fără acces la diff). Regula: pe 8019 și iconta_test se intră numai prin poarta_lot.sh, baza_test.sh și lanseaza_verificator.py.
- Clasele inventarului = clasele porții (scripts/poarta_e2e_restante.txt, scripts/poarta_clasifica.py::CLASE_INVENTAR): a (test prost) → restanță; b (stare/dată) → restanță; c (defect numerotat) → restanță; d (șters) → nu există în poartă; e (verde fără aserțiuni) → invalid; f (inexistent) → nu există în poartă; clasele porții rămân regresie / restanță / invalid / infra / nou. Un manifest cu un fișier cu rând „e” e refuzat. Eticheta jurnalului pentru o treaptă verde cu restanțe scăzute este „verde_cu_restante” (rămâne o rulare completă la contor; rândurile vechi nu se rescriu).
- Căile spre producție (16.1-C3): restartul îl face numai scripts/publica_prod.sh, pas numit „restart” în publica_lot.sh după push și înainte de sfârșitul fazei „publicare”, și refuză fără `PASS <HEAD>`; post-commit nu mai repornește nimic. `core/migrari_registru.py ... --productie` (ruleaza, marcheaza, baza) și scripturile care scriu pe producție cu `--productie` (scripts/lot13_firme2_curata_731.py, lot14_3_reclaseaza_117.py, stoc2_409_1_dubluri_corectie.py, stoc2_619_documente_pe_jumatate.py, valideaza_note_interne_pfa.py, prin scripts/productie_pass.py) refuză fără PASS pentru commitul curent al lui main. Căile care doar citesc (cifre_referinta, amprente_declaratii, ciorne_depasite: sesiune read-only; backup-ul pg_dump din config/; verificarea migrărilor `verifica`) nu cer PASS. Orice cale nouă spre producție cere PASS sau intră aici cu motivul.
- Încheierea comenzii (16.1-C3): O comandă se încheie numai prin scripts/incheie_lot.sh <nr> <stare>, care scrie ~/ghid_incoming/OPRIT_<nr>.txt; Code nu scrie fișierul de mână și nu scrie «OPRIT — gata» înainte de a-l apela. publica_lot.sh îl apelează la sfârșit (publicat sau STOP). Coada (~/coada_code.sh) și veghea (~/veghe_code.sh) pornesc comanda următoare numai când fișierul OPRIT_<nr> al comenzii curente există și tura e inactivă în tmux (fără „esc to interrupt”); fișierul se mută în ~/ghid_incoming/oprite/ înainte de pornire.
- Jurnalul: scripts/jurnal_lot.py scrie în ~/iconta_nou/.lot_jurnal.log începutul și sfârșitul fiecărei faze obligatorii (pornire, hook, verificator, treptele porții,
  publicare); pluginul pytest din conftest.py, scripts/cronometru.sh și scripts/bin/{pytest,playwright} înregistrează rulările; o fază fără sfârșit e „intrerupt”.
  Duratele din raport sunt copia ieșirii `python scripts/defalcare.py <lot>`. Verificarea pe pas: docs/dovezi/<lot>/jurnal_verificare.csv, scris de
  scripts/verifica_pas.py (verdictul vine din compararea JSON-ului ecranului cu așteptarea) și controlat încrucișat de scripts/jurnal_verificator.sh. Rândurile pe alt sha decât C rămân în
  fișier, sunt ignorate de verdict și pot avea orice verdict; numai rândurile pe C trebuie „trece” și fiecare pas al scenariului are rând pe C. O rundă a verificatorului independent = un sha
  distinct cu rânduri verificator=Haiku pe pașii „după”; parcurgerea „înainte” pe commitul de bază nu e rundă; publica_lot le numără din CSV față de `runde_verificator_max` din
  scripts/praguri_<lot>.txt (cheie lipsă = 0 runde permise, lot fără verificator, cum sunt loturile de unelte).
  Un lot de produs pornește numai din coadă; o comandă lipită direct în prompt nu are rândul «pornire» cu marcaj și nu se publică. ~/coada_code.sh scrie rândul „pornire” (scripts/jurnal_lot.py
  pornire-coada: ora reală, hash-ul pragurilor și al scripturilor porții, marcaj de proveniență din ~/ghid_incoming/cheie_coada.txt); publica_lot cere pentru un lot de produs unul singur, cu marcaj
  valid (lipsa lui = STOP „lipsă pornire”); rândul „reconstituit” (--ora-reala) se acceptă numai când scripts/praguri_<lot>.txt e „unelte” și nu există alt rând „pornire”.
- Publicarea: numai `sh scripts/publica_lot.sh` (ZIP, verificări, `PASS <sha>`, push, restart prin scripts/publica_prod.sh, sfârșitul fazei „publicare”). Hook-ul reference-transaction, pre-push și
  scripts/publica_prod.sh refuză fără PASS; poarta, publica_lot.sh, baza_test.sh, nucleul, conftest.py nu se ating în afara loturilor marcate „unelte” în scripts/praguri_<lot>.txt.
- Limite declarate: jurnalul dovedește fazele obligatorii înregistrate (început și sfârșit), nu toate execuțiile posibile pe un server cu shell (o comandă cu cale absolută
  ocolește PATH-ul); publicarea e condiționată de înregistrarea fazelor obligatorii, nu de interceptarea tuturor execuțiilor. Autorul fișierului de excepții al arhitectului
  nu e autentificat mecanic (un singur utilizator pe server); la fel, marcajul cozii și fișierele arhitectului (pasi_<lot>.txt, exceptii_<lot>.txt, OPRIT_<nr>.txt) sunt urme, nu bariere față de Code; la fel marcajul HMAC al rândurilor jurnalului verificării: cheia ~/.iconta/cheie_oracol (600, în afara depozitului) e citibilă de Code, deci marcajul e urmă, nu barieră. Lacătul oprește intrările scriptate: o comandă pytest sau
  curl lansată direct de Code pe 8019, ori `sudo systemctl restart` (sudoers îl permite), nu e oprită — regulile de mai sus le interzic, nu le împiedică mecanic. „Fără acces la diff” al verificatorului independent = director de lucru fără depozit, nu barieră.
Plasa fixă (scripts/plasa_16_2.manifest, hash în verdict): manifestul poate crește în lot numai prin rânduri adăugate pentru fișiere de test noi, prezente în diff-ul lotului față de
main și absente pe main; orice rând lipsă, modificat (inclusiv numărul de teste al unui fișier existent) sau adăugat pentru un fișier existent pe main = refuz cu numele lui (poarta și
scripts/publica_lot.sh, aceeași funcție `poarta_lib.manifest_refuzuri`). Un test nou de poziție pilot e deci fișier nou (e2e_pilot_<poziție>.py), nu test adăugat într-un fișier din manifest.
Când lotul e gata: poartă (pe roșu: repară
și reia, nu se publică niciodată pe roșu), backup, publicare, raport, apoi oprire.

R2. Un lot = o singură poartă și o singură publicare, la sfârșit. Nu publici pe zonă, pe ecran sau pe etapă, chiar dacă o comandă veche spune altfel. Starea bazei o fixează baza.json (§3): ce e roșu pe bază nu se repară în lot și nu se numără ca regresie; dacă e nenumerotat în inventar, lotul se oprește.

## 4. Deficiențele

Fiecare deficiență are un număr pe viață, din DEFICIENTE.md: numerele simple sunt ale lui Costin,
cele găsite de Code au prefixul C (următorul C liber din DEFICIENTE.md). Orice deficiență găsită de Code
intră în raport, cu numărul ei, cu ce a găsit și ce a făcut; nu rămâne doar în registrele lui.

Procesul pe fiecare deficiență primită (regulă permanentă, 30.10.2026; motiv: deficiențe raportate „rezolvat” au picat la retestul
lui Costin, pentru că testele lui Code îi confirmau propria interpretare — dovada nu mai vine de la Code):
1. Înainte de orice modificare, Code scrie într-o frază cum a înțeles deficiența și ce rezultat urmărește. Fraza intră în raport, neschimbată.
2. Scenariul deficienței (textul din comandă) se dă unui verificator independent: un subagent nou (Sonnet 5.5) al cărui prompt este
   exact textul scenariului plus instrucțiunea fixă, nimic altceva — nu vede modificările, notele sau testele lui Code. Instrucțiunea fixă:
   „Rulează scenariul de mai jos în aplicație, pe mediul de test, exact cum e scris, cu uneltele de capăt la capăt existente. Nu modifici
   cod. Răspunzi doar cu: TRECE sau NU TRECE, pașii făcuți, ce ai văzut la fiecare pas, capturile de ecran, și orice abatere de la
   scenariu.” Rulează înainte de reparație (trebuie NU TRECE; altfel deficiența e „nereprodusă” și nu se repară nimic în locul ei) și
   după reparație, cu un subagent nou de fiecare dată. Răspunsul lui intră în raport cuvânt cu cuvânt.
3. Se repară cauza oriunde se aplică aceeași regulă, nu doar în cazul din scenariu, iar locurile atinse se listează.
4. Cel mult două runde pe o deficiență. Dacă după a doua tot NU TRECE, modificările ei se anulează și deficiența se raportează
   nerezolvată, cu motivul. Nu blochează publicarea celorlalte.
5. „Rezolvat” înseamnă doar TRECE de la verificator. Testele lui Code nu sunt dovadă. Scenariul deficienței rămâne test permanent.

Scutirea 278.1 din regula 11.2 (16.4 pct.1; decizia arhitectului 05.11, regula Costin 04.11): `core/test_deficiente.py::DOVADA_PRIN_E2E` (mulțime închisă: 642, 278.1) și `DOVADA_PRIN_PILOT` (278.1). Un rând 278.1 `rezolvată` fără capturi pe firmele de test are `lipsuri_dovada_pilot`: numai teste `test_pilot_…` în plasa e2e și în plasa de publicare, „ce lipsește” exact `dovada e2e: docs/dovezi/16_2_C/jurnal_verificare.csv; pasi: c.1, …, d.1` și, pentru fiecare pas, un rând code / dupa / trece și un rând haiku / haiku_1 / trece cu „corespunde”, pe același commit, cu captura în index. Orice alt număr < 712 rămâne pe regula capturilor.

R5. Orice criteriu de produs primit de la arhitect (ce înseamnă „migrat”, „pe piese”, „corect”) intră în același commit în promptul fix al verificatorului sau într-un script care refuză; nu rămâne doar aplicat de mână. Orice corecție primită în chat o scrii întâi, cuvânt cu cuvânt, în ~/ghid_incoming/corectii_<lot>.txt, apoi o aplici; după /clear o recitești de acolo.

R6. Verificatorii independenți nu rulează niciodată pe producție; rulează pe serverul de lucru (port 8019). Verificatorul „înainte” e obligatoriu la fiecare lot; fără el nu există „după”.

## 5. Testarea

Scopul: zero regresii, fără muncă repetată degeaba.

După fiecare sarcină din lot se testează imediat codul atins și tot ce depinde de el, derivat din cod
(scripts/poarta_scurta.py). Când derivarea nu e sigură, se rulează tot ce poate fi atins. JS/CSS atins:
e2e-ul ecranelor atinse, uneltele vizuale și verificatorul.

Poarta DIAGNOSTIC (`POARTA_DIAGNOSTIC=1 sh scripts/poarta_lot.sh`; poarta de publicare e cea din §3, pe plasa fixă) este scripts/poarta_lot.sh (regulă permanentă, comanda 15.G, 30.10.2026) și rulează numai: testele picate la
ultima rulare, testele fișierelor atinse de la ultima publicare, scenariile deficiențelor, testele de nucleu fiscal și calcul
(declarații, TVA, solduri, stocuri, salarii) și verificatorul. Plasa e2e implicită ia numai: (a) fișierele e2e numite în
~/ghid_incoming/scenarii_<comanda>.txt (câte unul pe rând; îl scrie arhitectul sau Code la începutul comenzii, cu e2e-urile
deficiențelor comenzii, îl pune în raport la D și pornește poarta cu POARTA_COMANDA=<comanda>; lipsă = (a) gol), (b) e2e-urile
fluxurilor atinse de la main, după harta scripts/poarta_harta.txt, (c) cele picate la ultima rulare. Nimic altceva din plasă. Durata se măsoară și se scrie la final. Pe roșu: se repară cauza și
se rulează din nou poarta implicită (ea reia singură testele picate). Rularea completă (tot pytest + toată plasa e2e) este doar cea
de noapte, scripts/poarta_completa.sh: pornește numai cu cheia ~/ghid_incoming/cheie_poarta_completa_<lot>.txt, pe care o creează
numai comanda arhitectului; Code nu o rulează în timpul comenzilor și nu creează cheia. Marcajul global de sărire (POARTA_SARE=1 în
scripts/poarta.env) ține în afara porții testele din scripts/poarta_sare.txt și scripts/poarta_forma.txt; nu se oprește decât la
cererea arhitectului. Un test nou verifică sensul (de exemplu „există restanța D301 09/2026 la F3”), nu un șir de caractere literal;
datele și sumele din teste trec prin aceleași funcții de format ca aplicația.

Ordinea porții și oprirea la prima treaptă roșie (regulă permanentă, 31.10.2026): poarta_lot.sh rulează în ordinea 1. verificatorul de design,
2. pytest țintit, 3. plasa e2e. Prima treaptă roșie oprește poarta și scrie ROȘU imediat, fără să continue cu treptele de după. scripts/inainte_de_commit.sh
(verificatorul de design și pytest-ul țintit pe fișierele atinse) este parte din hook-ul de git `pre-commit` (regulă permanentă, 03.11.2026): commitul se
refuză cât scriptul e roșu; poarta pornește numai pe un commit care l-a trecut. Nu se editează arborele cât rulează poarta (verdictul ar deveni „arbore schimbat”).

R1. Turul se încheie numai cu „publicat <lot> pe <commit>” sau „OPRIT — gata: <lot>”, după ce scripts/incheie_lot.sh a fost apelat (§3). La o întrebare primită în prompt răspunzi într-un rând și continui lucrul în același tur. Nu te oprești după un răspuns, după o intenție („continui cu…”) sau după un monitor expirat.

R3. Cât rulează o poartă sau un test lung nu folosești monitor și nu aștepți pasiv. Aștepți cu o singură comandă shell blocantă care citește logul la 60 de secunde și iese la verdict sau după 90 de minute. Din loguri citești numai ultimele 40 de linii și liniile FAILED. Cel mult un subagent, pe Sonnet 5.5, oprit și raportat dacă nu are rezultat după o oră.

Reluarea după roșu (regulă permanentă, 31.10.2026): la prima rulare a unei zone, „fișierele atinse” se socotesc față de main; la orice reluare după roșu,
„atinse” înseamnă doar fișierele schimbate de la ultima rulare a porții (commitul ei se reține în scripts/poarta_ultima.txt, ignorat de git, scris
de poarta_lot.sh pe ROȘU și șters pe VERDE), plus testele picate (--lf, fișierul de căzute al plasei). Scenariile și verificatorul rămân mereu. Durata
fiecărei reluări se raportează la D.

Plasa de fluxuri atinse (b), limita de 20 (regulă permanentă, comanda 15.1, 31.10.2026; înlocuiește (b) de mai sus când depășește): dacă e2e-urile
fluxurilor atinse după harta scripts/poarta_harta.txt depășesc 20 de fișiere, (b) se înlocuiește cu e2e-urile ecranelor numite în
~/ghid_incoming/scenarii_<comanda>.txt sub titlul FLUXURI (cel mult 20, scrise de arhitect sau de Code la începutul comenzii); lista completă
din hartă se scrie de poartă în poarta_flux_harta.txt și intră în raport la D. Raportul spune, la D, câte și care e2e-uri au picat la prima rulare
roșie. Când pytest și verificatorul sunt deja verzi pe un commit și se reia numai plasa, se folosește POARTA_DOAR_PLASA=<sha>: poarta refuză dacă de
atunci s-a schimbat altceva decât fișierele porții și registrele, iar verdictul e compus (pytest + verificator pe <sha>, plasa pe commitul curent).

Un test care a trecut deja pe exact același commit nu se mai rulează a doua oară.

Dacă poarta pică numai pe cifrele de referință F1–F5 și diferențele se explică prin datele de retest și
prin codul lotului, Code actualizează referința, o notează în DECIZII și continuă. Cifrele neexplicate
trec în raport.

Testele nu se slăbesc ca să treacă. Durata fiecărei părți a porții se măsoară și se raportează.

Ce rămâne în poartă (regulă permanentă, 30.10.2026): un test rămâne dacă verifică o cifră, o dată, o regulă fiscală, un lucru salvat
sau ce vede contabilul pe ecran. Iese din rulare (fără să fie șters) dacă verifică doar forma codului: nume, importuri, funcții,
plural, texte „azi/acum”, registre generate, capturi de referință, structuri de fișiere. Scenariile deficiențelor rămân teste
permanente. Registrele generate și capturile de referință se refac o singură dată pe lot, la publicare. Un test rămas care pică se
repară; un test scos care ar fi picat nu e motiv să fie pus la loc. Code nu adaugă verificări din proprie inițiativă.

Testele grele (suita, poarta, e2e, uneltele vizuale, verificatorul) rulează una după alta, niciodată
în paralel: serverul e și producția.

R10. Testele legate de data de azi primesc un moment de referință fix, nu data calendarului (regulă permanentă, 03.11.2026): testele de browser din core/ iau ziua din
`core.ceas_proba.DATA_REF`, iar pagina primește același ceas fix (`pagina_cu_ceas_fix`); gard: core/test_ceas_fix.py.

R11. Înainte de primul commit al unui lot, poarta rulează în modul „listează” (`sh scripts/poarta_lot.sh --lista [fișier…]`, fără fișiere: cele atinse față de `main`; implementare: `scripts/poarta_selectie.py::lista`) și scrie ce teste va rula pentru fișierele pe care lotul le va atinge: testele de browser din core/ ȘI fluxurile e2e (frontend_test/e2e, după hartă și FLUXURI din scenarii), cel mult 20 de fișiere. O atingere a lui stil.css, navigator.js, api.js sau cadru.js înseamnă „toate ecranele”: plafonul întreg. Dacă zona atinsă nu e acoperită (ieșire 1), harta scripts/poarta_harta.txt se extinde întâi, abia apoi începe lotul. Lista intră în raport la D.

## 6. Publicarea

După poarta verde, Code publică imediat, fără să aștepte confirmare, numai prin `sh scripts/publica_lot.sh` (§3): backup al bazei chiar înainte,
migrările pe producție, repornirea, verificarea four-way (disc = origin/main = backup = procesul viu).
Push pe oglinda GitHub după fiecare publicare.

## 7. Cabinetul real

Datele cabinetului real nu se citesc și nu se scriu fără aprobarea lui Costin și nu intră niciodată în
rapoarte, ZIP-uri, probe sau chat.

## 8. Raportul de lot

Modelul (regulă permanentă, 30.10.2026), obligatoriu la fiecare comandă, în această ordine, fără alte secțiuni:
A. Rezultat: commitul publicat, backupul, calea ZIP-ului; câte deficiențe primite, câte TRECE, câte NU TRECE, câte nereproduse.
B. Tabelul deficiențelor, un rând pe număr: numărul; fraza de la §4 punctul 1; reprodusă înainte (da/nu); cauza, într-o frază; locurile
   atinse; verdictul verificatorului după (TRECE / NU TRECE / nereprodusă); runde; durata măsurată.
C. Timp măsurat, pe comandă: de la pornire la „OPRIT”; pe reproducere, reparație, verificare, poartă, publicare; cel mai lung pas și de ce.
D. Poarta: durata; câte teste au rulat; testele picate, fiecare cu „greșeală reală” sau „test de reparat”; verificări adăugate sau
   scoase, cu motivul.
E. Abateri de la comandă: orice s-a făcut în plus sau altfel decât scria, cu motivul; deciziile luate pe varianta cea mai sigură.
F. Ce a lipsit din comandă sau din scenarii ca să fi mers mai repede sau mai sigur (o frază pe punct; „nimic” e un răspuns valid).
G. Răspunsurile verificatorului, cuvânt cu cuvânt, ca anexă.
Nimic altceva: fără rezumate ale propriilor teste, fără planuri de viitor, fără estimări. Pentru o decizie de produs, Code alege între
timp varianta cea mai sigură pentru contabil și o listează la E.

R4. Cronometru: pentru fiecare număr de deficiență notezi ora de început și de sfârșit; pentru fiecare poartă, durata exactă și verdictul. Raportul lotului dă pe fiecare număr durata și, la final, ore pe deficiență și ore în porți.

Registre obligatorii la fiecare lot: DEFICIENTE.md, DECIZII.md (adăugare, nu rescriere), PREDARE_LANT.md
(starea curentă). Celelalte registre se ating doar când lotul schimbă ce descriu.

Singurul „OPRIT” (29.10.2026, regulă permanentă a lui Costin, înlocuiește forma din 25.10.2026) este cel final, după
publicare: ultimul rând scris e „publicat <lot> pe <commit>” sau „OPRIT — gata: <lot>” (R1), fără nimic după el. Înainte de publicare nu
se scrie „OPRIT”; singura oprire permisă acolo (risc pentru producție) se scrie cu motivul, nu cu „aștept”.

## 9. Reguli de produs

- Fereastra încape pe ecran fără derulare; acțiunea principală și mesajele de eroare se văd mereu.
- Nimic nu se deschide singur: niciun buton, card, listă sau formular fără selecția utilizatorului.
- Nimic precompletat sau afișat care poate induce în eroare contabilul.
- Textele dau instrucțiuni directe, în limba contabilului, cu diacritice; fără termeni de programator.
- Orice regulă vizuală stă în DESIGN_SYSTEM.md și în verificator; situații identice, soluții identice.

R7. Un ecran e migrat numai când verificatorul de design dă TRECE pe toate rândurile criteriului „migrat” din promptul lui (bara de sus, fereastra de lucru cu bara de jos fixă, tabelul DS, card-rezumat și semnale pe rând, acțiune = buton, titluri și texte din catalog, funcția unică de format, cota TVA ca grup cu categorii). Un singur PICĂ înseamnă nemigrat. Pixelii (derulare, margini, text tăiat) nu înlocuiesc piesele.

R8. Nicio reparație de aspect cu stil scris direct în ecran (inline style, sed pe un fișier de ecran). Defectul se repară o dată, în piesa sau clasa DS, și toate ecranele o iau. Dacă piesa lipsește din modele, o întrebi la F în raport, nu o inventezi.

## 10. Reguli tehnice (lecții plătite)

- Orice valoare fiscală, structură de declarație sau temei se verifică la sursa oficială înainte de
  folosire; niciodată din memorie. Pentru declarații, validatorul DUK e judecătorul final. Valorile
  fiscale noi se aprobă prin verificarea independentă a arhitectului.
- Înainte de a declara ceva inexistent sau de a construi, grep pe tot ~/iconta_nou.
- Rotunjirea sumelor fiscale: Decimal cu ROUND_HALF_UP, niciodată round() din Python.
- CUI/CNP de test numai cu cifra de control verificată.
- Proba funcțională reală (apel cu date), nu doar verificare de sintaxă; SQL testat pe Postgres.
- Reparație reală: fără cod mort, fără logică dublată; se repară clasa, nu instanța.
- La commit, fișierele se pun pe nume, niciodată git add -A.
- Exit-code-ul real al lui pytest, nu al ultimei comenzi din pipe.
- Mutație: revert din copie de backup, nu git checkout; după mutație se șterge __pycache__.
- Fixture-urile pe tabele partajate folosesc perioade sintetice (2099), în rollback.
