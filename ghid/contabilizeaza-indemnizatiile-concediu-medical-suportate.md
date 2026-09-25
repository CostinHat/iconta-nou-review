---
title: "Cum se contabilizează indemnizațiile de concediu medical suportate din FNUASS?"
description: "De ce partea de indemnizație suportată din bugetul FNUASS nu e o cheltuială a angajatorului, ci o creanță recuperabilă, și ce oferă iConta.eu pentru evidența ei."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se contabilizează indemnizațiile de concediu medical suportate din FNUASS?

Din a doua parte a perioadei de incapacitate temporară de muncă, indemnizația nu mai e suportată din banii angajatorului — e suportată din bugetul Fondului național unic de asigurări sociale de sănătate (FNUASS). Practic, angajatorul plătește totuși suma către salariat (odată cu salariul), dar apoi o recuperează de la casa de asigurări de sănătate. Contabil, această diferență contează: nu e o cheltuială definitivă, ci o sumă de recuperat.

## Temeiul legal

::: ghid-temei
„[...] din bugetul Fondului național unic de asigurări sociale de sănătate, începând cu: a) ziua următoare celor suportate de angajator [...] și până la data încetării incapacității temporare de muncă a asiguratului [...]."

„Sumele reprezentând indemnizații, care se plătesc asiguraților și care [...] se suportă din bugetul Fondului național unic de asigurări sociale de sănătate, se recuperează din bugetul Fondului național unic de asigurări sociale de sănătate din creditele bugetare prevăzute cu această destinație. Aceste sume nu pot fi recuperate din sumele constituite reprezentând contribuție de asigurări sociale de sănătate."
— OUG 158/2005, art. 12 lit. B și art. 38 alin. (1) (sursă: anaf_surse/oug_158_2005_consolidat.txt)
:::

Consecința pentru contabilitate:

- Suma pe care angajatorul o plătește salariatului pentru zilele suportate din FNUASS **nu e o cheltuială a firmei** — e o sumă avansată, pe care angajatorul are dreptul (și obligația de a solicita, prin cerere de restituire) s-o recupereze de la casa de asigurări de sănătate.
- Contabil, această sumă se reflectă printr-o **creanță față de bugetul asigurărilor sociale de sănătate**, prin conturile de decontări cu asigurările sociale — nu prin conturile de cheltuieli (645) folosite pentru partea suportată efectiv de angajator.
- Legea exclude explicit compensarea acestei sume cu contribuția de asigurări sociale de sănătate datorată de angajator — recuperarea se face separat, din creditele bugetare ale FNUASS, nu prin diminuarea CASS de plată.
- Fața de salariat, suma rămâne datorie („Personal – salarii datorate"), la fel ca partea suportată de angajator — distincția e doar la contrapartida angajatorului, nu la modul de plată către salariat.

## Ce se greșește în practică

- Se înregistrează întreaga indemnizație de concediu medical ca o cheltuială a firmei, inclusiv partea care va fi recuperată de la FNUASS.
- Se compensează suma suportată de FNUASS direct cu CASS-ul de plată al lunii, deși legea interzice explicit această compensare.
- Se lasă suma „în aer", fără să fie urmărită ca o creanță distinctă, până la depunerea cererii de restituire la casa de asigurări de sănătate.

## Ce face iConta.eu

iConta.eu calculează corect, prin motorul de salarizare, ce parte din indemnizație revine FNUASS pentru fiecare certificat de concediu medical introdus în fișa salariatului, și afișează suma separat — „Suportat FNUASS" — la introducerea certificatului în fișa salariatului. Pe fluturașul de salariu apare doar suma brută totală a indemnizației, cu mențiunea că e suportată de angajator și de FNUASS împreună, nu defalcarea pe cele două surse. Verificat direct în cod: aplicația **nu generează astăzi o notă contabilă automată** care să reflecte suma din FNUASS ca o creanță distinctă — funcția care produce automat notele contabile lucrează doar cu rezultatul calculului de salariu obișnuit, nu și cu partea de concediu medical suportată din fonduri publice. Evidența acestei creanțe și urmărirea recuperării ei rămân, pentru moment, în sarcina contabilului.

[iConta.eu](/)
