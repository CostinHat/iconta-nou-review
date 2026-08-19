---
title: D406 pe august 2026: termenul efectiv și ce înseamnă recipisa
description: Termenul D406 e ultima zi calendaristică a lunii următoare, deci 30 septembrie 2026 pentru luna august, nu 25; recipisa confirmă doar validarea structurală a fișierului, nu corectitudinea datelor față de D300 (OPANAF nr. 1783/2021).
published: 2026-08-19
modified: 2026-08-19
---

# D406 pe august 2026: termenul efectiv și ce înseamnă recipisa

Termenul de depunere a D406 e **ultima zi calendaristică a lunii următoare** perioadei de raportare. Pentru august 2026, la contribuabilii cu perioadă fiscală lunară, termenul e **30 septembrie 2026**.

Nu 25, ca la celelalte declarații. Aceasta e distincția care produce cele mai multe depuneri întârziate.

## Periodicitatea urmează TVA-ul

**Perioadă fiscală lunară la TVA** → D406 lunar, cu termen la sfârșitul lunii următoare.

**Perioadă fiscală trimestrială** → D406 trimestrial, cu termen la sfârșitul lunii următoare trimestrului.

**Neplătitori de TVA** → D406 trimestrial.

Deci o firmă care a trecut de la trimestrial la lunar în cursul anului își schimbă și periodicitatea SAF-T. Verificarea se face în vectorul fiscal, nu din memorie.

## Secțiunile cu termen propriu

D406 nu e un fișier unic depus la același termen. Are trei componente, cu regimuri diferite:

**Secțiunile lunare/trimestriale** — plan de conturi, jurnale, parteneri, facturi, plăți. Se depun la termenul obișnuit.

**Secțiunea Stocuri** — se depune **la cererea organului fiscal**, cu termen stabilit de acesta, nu mai puțin de 30 de zile.

**Secțiunea Active** — se depune **anual**, la termenul de depunere a situațiilor financiare anuale, fără perioadă de grație.

Ultima e cea care surprinde: nu are amânare, iar termenul e legat de bilanț, nu de SAF-T-ul lunar.

## Perioada de grație

La intrarea în obligație, fiecare categorie de contribuabili a beneficiat de o perioadă de grație pentru primele depuneri — 6 luni pentru depunătorii lunari, 3 luni pentru cei trimestriali, de la prima raportare.

Pentru contribuabilii aflați deja în sistem, perioada de grație s-a consumat. Depunerile din 2026 sunt la termen, cu sancțiuni pentru întârziere.

## Ce înseamnă recipisa

Recipisa confirmă că fișierul a fost **primit și validat structural** de sistem. Nu confirmă că datele sunt corecte.

Distincția e aceeași ca la validarea DUKIntegrator: se verifică schema XML, tipurile de date, obligativitatea câmpurilor — nu concordanța cu evidența contabilă.

O recipisă fără erori pe un fișier cu jurnale incomplete e un fișier acceptat și greșit.

## Ce se verifică înainte de depunere

Programul pilot ANAF compară automat datele din SAF-T cu decontul de TVA. Reconcilierile de făcut în cabinet, înainte:

**Totalul TVA colectată din jurnalul de vânzări** față de rândurile corespunzătoare din D300.

**Totalul TVA deductibilă din jurnalul de cumpărări** față de D300.

**Numărul de facturi** din secțiunea de facturi față de evidența internă.

**Partenerii** — codurile fiscale valide, denumirile complete, fără identificatori interni.

**Planul de conturi** — corelat cu balanța, fără conturi lipsă.

Divergențele găsite înainte de depunere se corectează. Cele găsite de ANAF produc notificare.

## Erorile frecvente la validare

**Coduri de parteneri lipsă sau invalide** — un partener fără CUI blochează validarea secțiunii.

**Diacritice codate greșit** — produce caractere invalide în XML.

**Conturi analitice nedeclarate** în secțiunea de plan de conturi, dar folosite în jurnale.

**Perioada greșită** în antetul fișierului — cea mai gravă, fiindcă fișierul se validează și se depune pentru o lună care nu era cea intenționată.

**Sume cu semn greșit** la stornări.

## Sancțiunile

Pentru nedepunerea la termen sau depunerea incorectă a D406, Codul de procedură fiscală prevede amenzi distincte, aplicabile după expirarea perioadei de grație.

Separat, nedepunerea declarațiilor pe durata unui semestru e criteriu de inactivitate fiscală.

## Ce verifică un contabil în calendar

**Sfârșitul lunii, nu 25.** Termenul D406 e diferit de al celorlalte declarații și se ratează exact din acest motiv.

**Periodicitatea corectă** pentru fiecare firmă, din vectorul fiscal.

**Secțiunea Active** — programată la termenul situațiilor financiare, nu uitată.

**Recipisa descărcată și arhivată** pentru fiecare depunere. E singura dovadă a depunerii.

## Temeiul legal

- OPANAF nr. 1783/2021 privind natura informațiilor pe care contribuabilul trebuie să le declare prin fișierul standard de control fiscal, structura și modelul de raportare;
- OPANAF nr. 407/2025 — calendarul de intrare în obligație pe categorii;
- Codul de procedură fiscală — sancțiunile pentru nedepunere;
- schema XSD publicată de ANAF, pentru validarea structurală.

## De reținut

**30 septembrie, nu 25** — pentru D406 aferent lunii august.

Iar recipisa confirmă doar structura. Corectitudinea datelor se probează prin reconcilierea cu D300, făcută înainte de depunere, nu după notificarea de neconcordanță.
