---
title: Ce faci dacă D406 nu apare în SPV după depunere?
description: Data depunerii unei declarații transmise electronic e data înregistrării pe portal, confirmată prin mesajul electronic de validare (art. 103 alin. (3)-(5) Cod de procedură fiscală) — dacă mesajul de confirmare lipsește sau declarația nu s-a validat, D406 nu se consideră depusă la acea dată, indiferent că fișierul a fost transmis.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce faci dacă D406 nu apare în SPV după depunere?

Trimiterea fișierului SAF-T nu înseamnă automat depunere reușită — între transmitere și înregistrarea efectivă a declarației există un pas de validare, iar dacă acesta eșuează, D406 nu apare (corect) în Spațiul Privat Virtual.

### Ce spune legea despre data depunerii unei declarații electronice

Potrivit **art. 103 alin. (3) din Codul de procedură fiscală** (Legea nr. 207/2015): „Data depunerii declarației fiscale este data înregistrării acesteia la organul fiscal [...]. În situația în care declarația fiscală se depune prin mijloace electronice de transmitere la distanță, data depunerii declarației este data înregistrării acesteia pe pagina de internet a organului fiscal, astfel cum rezultă din mesajul electronic de confirmare transmis ca urmare a primirii declarației."

Mai precis, **alin. (4)** clarifică: data depunerii e data înregistrării pe portal, „astfel cum rezultă din mesajul electronic transmis de sistemul de tranzacționare a informațiilor, **cu condiția validării conținutului declarației**. În cazul în care declarația nu este validată, data depunerii declarației este data validării astfel cum rezultă din mesajul electronic."

Concluzia practică: **fără mesaj de confirmare/validare, declarația nu e considerată depusă la data transmiterii** — chiar dacă fișierul a plecat de pe calculatorul dvs. și a ajuns aparent la ANAF.

### Primul pas — verificați dacă a existat un mesaj de eroare la validare

Cea mai frecventă cauză pentru care D406 nu apare în SPV e o **eroare de validare structurală** a fișierului XML (element obligatoriu lipsă, format greșit, referință incorectă între secțiuni) — sistemul ANAF respinge fișierul la validare și nu îl înregistrează ca depus, transmițând (sau ar trebui să transmită) un mesaj de eroare. Verificați întâi arhiva de mesaje/notificări din contul dvs. de utilizator asociat SPV, nu doar secțiunea de declarații depuse.

### A doua ipoteză — declarația a fost depusă, dar cu întârziere la afișare

Există un decalaj tehnic normal între momentul transmiterii și afișarea efectivă în lista de declarații din SPV — sistemul procesează fișierul (mai ales unul voluminos, cum e adesea D406) și abia după procesare apare confirmarea. Dacă a trecut un timp scurt (ore, nu zile) de la transmitere, verificarea repetată e primul pas, înainte de a presupune că depunerea a eșuat.

### Excepția care vă protejează — eroare detectată, corectată în aceeași lună

**Art. 103 alin. (5) din Codul de procedură fiscală** acoperă situația în care declarația a fost depusă până la termenul legal, dar sistemul a semnalat erori la validare: „data depunerii declarației este data din mesajul transmis inițial, în cazul în care contribuabilul/plătitorul depune o declarație validă până în ultima zi a lunii în care se împlinește termenul legal de depunere." Deci dacă transmiteți D406 la termen, primiți eroare de validare, dar corectați și retransmiteți o versiune validă **până la finalul lunii** în care era termenul de depunere, se păstrează data inițială de transmitere — nu sunteți penalizat pentru întârzierea generată de corectarea erorii.

### Pași concreți de urmat

1. Verificați jurnalul de mesaje/notificări din SPV pentru contul asociat firmei — căutați orice mesaj legat de fișierul respectiv, chiar dacă nu apare direct în lista de „declarații depuse".
2. Dacă găsiți un mesaj de eroare de validare, identificați elementul semnalat, corectați fișierul SAF-T la sursă și retransmiteți — nu editați manual XML-ul generat, corectați datele din care a fost generat.
3. Dacă nu găsiți niciun mesaj (nici confirmare, nici eroare), e posibil ca transmiterea propriu-zisă să nu fi ajuns la ANAF — verificați jurnalul local al aplicației/portalului folosit pentru transmitere și reîncercați.
4. Dacă termenul legal e aproape de expirare și nu aveți confirmare de validare, nu așteptați pasiv — o retransmitere (chiar dacă „dublează" o transmitere anterioară care s-ar putea să fi eșuat) e mai sigură decât riscul unei declarații considerate nedepuse.
5. Păstrați dovada tuturor transmiterilor (jurnal, mesaje, fișierele exacte trimise) — în caz de contestare a unei eventuale sancțiuni pentru nedepunere, dovada transmiterii la termen, chiar respinsă la validare, contează pentru aplicarea excepției de la art. 103 alin. (5) CPF.
