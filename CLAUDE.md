# CLAUDE.md — Regulile permanente ale lui Code pe iConta

Versiune: 30.10.2026. Acest fișier e citit automat la fiecare pornire și după fiecare /clear.
Este SINGURA sursă de reguli de lucru pentru Code. Orice regulă de proces care nu e aici e radiată,
oriunde ar fi scrisă (vechiul CLAUDE.md, PLAN_LUCRU.md, PREDARE_LANT.md, DECIZII.md, memoria permanentă,
comenzi vechi). DECIZII.md rămâne istoric (de ce s-a decis), nu normă.

O regulă nouă intră numai aici, în secțiunea ei, iar cea pe care o înlocuiește se șterge din acest fișier
în același commit. Nu se adaugă reguli alături de cele vechi.

## 0. La pornire și după /clear

Înainte de orice altceva, Code citește PREDARE_LANT.md (unde a rămas lucrul) și comanda în curs, din
~/ghid_incoming/. Nimic altceva nu e obligatoriu de citit: regulile sunt toate în acest fișier.

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
Code duce lotul până la capăt și NU se oprește sub niciun motiv înainte de publicarea lui (regulă permanentă a lui
Costin, 29.10.2026): ce nu poate rezolva singur trece în raport și continuă cu restul; deciziile de pe parcurs le ia pe
varianta cea mai sigură și le listează în raport, la E (Abateri); nu cere decizii pe parcurs. Singura oprire permisă
înainte de publicare este un risc pentru producție (pierdere de date, aplicația căzută), cu motivul scris. Nu se trece la
nimic din afara comenzii (nici agendă, nici fir intern, nici „următorul pas din listă”). Când lotul e gata: poartă
(pe roșu: repară și reia, nu se publică niciodată pe roșu), backup, publicare, raport, apoi oprire.

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

## 5. Testarea

Scopul: zero regresii, fără muncă repetată degeaba.

După fiecare sarcină din lot se testează imediat codul atins și tot ce depinde de el, derivat din cod
(scripts/poarta_scurta.py). Când derivarea nu e sigură, se rulează tot ce poate fi atins. JS/CSS atins:
e2e-ul ecranelor atinse, uneltele vizuale și verificatorul.

La închiderea lotului, poarta completă rulează o singură dată (scripts/poarta_lot.sh).

Un test care a trecut deja pe exact același commit nu se mai rulează a doua oară.

Dacă poarta pică: se repară cauza, apoi se rulează testele căzute și tot ce depinde de reparație. Poarta
completă se reia numai dacă reparația a atins piese folosite în mai multe locuri sau dacă perimetrul
ei nu e sigur. Verdictul pentru commitul reparat se compune din rularea completă anterioară plus
rerularea țintită.

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
în paralel: serverul e și producția. Subagenții lucrează în paralel numai pe fișiere diferite și rulează
doar teste pe fișiere individuale.

Subagenții (regulă permanentă a lui Costin, 26.10.2026): cel mult 2 în paralel, toți pe Sonnet 5.5; Opus numai dacă Costin
îl cere explicit. Un subagent care nu a dat niciun rezultat după 1 oră se oprește, iar oprirea se raportează (ce rămăsese
neterminat).

## 6. Publicarea

După poarta verde, Code publică imediat, fără să aștepte confirmare: backup al bazei chiar înainte,
migrările pe producție, repornirea, verificarea four-way (disc = origin/main = backup = procesul viu).
Dacă verificarea de după publicare pică, Code repară și publică din nou până trece; nu revine la
versiunea anterioară. Push pe oglinda GitHub după fiecare publicare.

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

Registre obligatorii la fiecare lot: DEFICIENTE.md, DECIZII.md (adăugare, nu rescriere), PREDARE_LANT.md
(starea curentă). Celelalte registre se ating doar când lotul schimbă ce descriu.

Singurul „OPRIT” (29.10.2026, regulă permanentă a lui Costin, înlocuiește forma din 25.10.2026) este cel final, după
publicare: ultimul rând scris e „OPRIT — gata: lotul X publicat pe <commit>”, fără nimic după el. Înainte de publicare nu
se scrie „OPRIT”; singura oprire permisă acolo (risc pentru producție) se scrie cu motivul, nu cu „aștept”.

## 9. Reguli de produs

- Fereastra încape pe ecran fără derulare; acțiunea principală și mesajele de eroare se văd mereu.
- Nimic nu se deschide singur: niciun buton, card, listă sau formular fără selecția utilizatorului.
- Nimic precompletat sau afișat care poate induce în eroare contabilul.
- Textele dau instrucțiuni directe, în limba contabilului, cu diacritice; fără termeni de programator.
- Orice regulă vizuală stă în DESIGN_SYSTEM.md și în verificator; situații identice, soluții identice.

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
