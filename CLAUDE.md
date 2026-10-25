# CLAUDE.md — Regulile permanente ale lui Code pe iConta

Versiune: 23.10.2026. Acest fișier e citit automat la fiecare pornire și după fiecare /clear.
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
Code duce lotul până la capăt fără să se oprească pentru niciun motiv: ce nu poate rezolva singur trece
în raport și continuă cu restul. Nu se trece la nimic din afara comenzii (nici agendă, nici fir intern,
nici „următorul pas din listă”). Când lotul e gata: poartă, backup, publicare, raport, apoi oprire.

## 4. Deficiențele

Fiecare deficiență are un număr pe viață, din DEFICIENTE.md: numerele simple sunt ale lui Costin,
cele găsite de Code au prefixul C (următorul C liber din DEFICIENTE.md). Orice deficiență găsită de Code
intră în raport, cu numărul ei, cu ce a găsit, ce a făcut și dovada; nu rămâne doar în registrele lui. „Rezolvată” înseamnă dovadă pe ecran, inclusiv pe documentele create înainte de
reparație, plus test automat de capăt la capăt care rămâne permanent în poartă.

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

Testele nu se slăbesc ca să treacă. Un test se scoate numai pe dovadă (duplicat, funcție scoasă, gardă
care nu poate cădea), iar raportul spune care și de ce. Durata fiecărei părți a porții se măsoară și se
raportează.

Testele grele (suita, poarta, e2e, uneltele vizuale, verificatorul) rulează una după alta, niciodată
în paralel: serverul e și producția. Subagenții lucrează în paralel numai pe fișiere diferite și rulează
doar teste pe fișiere individuale.

## 6. Publicarea

După poarta verde, Code publică imediat, fără să aștepte confirmare: backup al bazei chiar înainte,
migrările pe producție, repornirea, verificarea four-way (disc = origin/main = backup = procesul viu).
Dacă verificarea de după publicare pică, Code repară și publică din nou până trece; nu revine la
versiunea anterioară. Push pe oglinda GitHub după fiecare publicare.

## 7. Cabinetul real

Datele cabinetului real nu se citesc și nu se scriu fără aprobarea lui Costin și nu intră niciodată în
rapoarte, ZIP-uri, probe sau chat.

## 8. Raportul de lot

În această ordine:
1. Verdict: publicat sau nu, commitul publicat.
2. Fiecare număr din comandă, punctual: rezolvat / nerezolvat, dovada, testul.
3. Deficiențele noi găsite de Code, numerotate.
4. Ce nu s-a putut face și de ce.
5. Deciziile cerute lui Costin (pentru o decizie de produs, Code alege între timp varianta cea mai sigură
   pentru contabil și continuă).
6. Operațiile rulate, cu durata exactă măsurată a fiecăreia (fără estimări dinainte).
7. Publicarea: four-way, backup, calea exactă a ZIP-ului cu tot ce s-a schimbat în lot.

Registre obligatorii la fiecare lot: DEFICIENTE.md, DECIZII.md (adăugare, nu rescriere), PREDARE_LANT.md
(starea curentă). Celelalte registre se ating doar când lotul schimbă ce descriu.

La orice oprire (25.10.2026, regulă permanentă a lui Costin): ultimul rând scris e unul singur,
„OPRIT — aștept: <ce anume>” sau „OPRIT — gata: <ce s-a terminat>”, fără nimic după el.

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
