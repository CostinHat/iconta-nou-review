---
title: "Ce documente sunt necesare pentru deducerea personală?"
description: "Deducerea personală la salariu se calculează pe un tabel legat de venitul brut și numărul persoanelor aflate în întreținere — dovada persoanelor în întreținere e documentul-cheie pentru acordarea ei corectă."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce documente sunt necesare pentru deducerea personală?

Deducerea personală reduce venitul net impozabil din salariu, dar valoarea ei nu e fixă — depinde de nivelul venitului brut lunar și de numărul persoanelor aflate în întreținerea salariatului. Acordarea corectă a sumei mai mari (pentru persoane în întreținere) ține de existența unei dovezi, nu de simpla declarație verbală a angajatului.

## Temeiul legal

::: ghid-temei
„(1) Persoanele fizice prevăzute la art. 59 alin. (1) lit. a), alin. (2) și (2^1) au dreptul la deducerea din venitul net lunar din salarii a unei sume sub formă de deducere personală, acordată pentru fiecare lună a perioadei impozabile numai pentru veniturile din salarii la locul unde se află funcția de bază. (2) Deducerea personală cuprinde deducerea personală de bază și deducerea personală suplimentară și se acordă în limita venitului impozabil lunar realizat."
— Legea nr. 227/2015 (Codul fiscal), art. 77 alin. (1)-(2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Deducerea personală se acordă **numai la locul unde se află funcția de bază** a salariatului — nu se poate acorda simultan la mai mulți angajatori pentru aceeași persoană.
- Valoarea deducerii **de bază** depinde de venitul brut lunar (comparat cu salariul minim brut pe țară) și de **numărul persoanelor aflate în întreținere**, potrivit unui tabel cu procente din salariul minim, prevăzut la art. 77 alin. (4).
- Deducerea personală cuprinde, distinct, o componentă **de bază** și una **suplimentară** — fiecare cu condiții proprii, ambele acordate în limita venitului impozabil lunar realizat.
- Pentru a beneficia de deducerea majorată pentru persoane în întreținere, angajatul trebuie să facă dovada acestei calități — în practică, printr-o declarație pe propria răspundere însoțită, după caz, de documente justificative (certificate de naștere, acte de studii pentru copii majori, dovezi de venit ale persoanei întreținute etc.).

## Ce se greșește în practică

- Se acordă deducerea pentru persoane în întreținere doar pe baza unei mențiuni verbale a angajatului, fără nicio declarație scrisă sau document care să susțină calitatea de persoană în întreținere.
- Se acordă deducerea personală la mai mult de un angajator pentru aceeași persoană, deși legea o leagă explicit de locul funcției de bază.
- Se aplică un procent fix de deducere, indiferent de venitul brut lunar concret al salariatului, ignorând faptul că procentul scade pe măsură ce venitul brut crește peste salariul minim, conform tabelului din lege.

## Ce face iConta.eu

La data acestui ghid, motorul de salarizare din iConta.eu (`core/salarizare.py`, `core/salariati_api.py`) calculează impozitul pe venitul din salarii pornind de la datele introduse pentru fiecare salariat, inclusiv informațiile despre persoanele aflate în întreținere, dacă acestea au fost înregistrate în profilul salariatului. Aplicația nu gestionează însă documentele justificative propriu-zise (declarații pe propria răspundere, certificate de naștere) care stau la baza acestei informații — colectarea și păstrarea acestor documente rămâne un proces separat, în sarcina departamentului de resurse umane sau a contabilului.

[iConta.eu](/)
