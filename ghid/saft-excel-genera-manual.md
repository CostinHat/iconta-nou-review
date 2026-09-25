---
title: "SAF-T din Excel: se poate genera manual?"
description: Excel nu e un format acceptat pentru SAF-T. D406 se depune ca fișier XML pe schema SAF-T, verificat cu validatorul ANAF și atașat unui PDF semnat electronic. OPANAF 1783/2021, anexa 3, permite însă ca XML-ul să fie pregătit manual, cu un editor de XML.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# SAF-T din Excel: se poate genera manual?

Un fișier Excel nu se poate depune ca D406. Declarația conține un fișier XML construit pe schema SAF-T, atașat unui PDF semnat electronic. Datele pot proveni dintr-un tabel ținut manual. Condiția este ca XML-ul rezultat să treacă de validatorul ANAF.

### Ce cere ordinul

OPANAF 1783/2021 definește fișierul: „SAF-T este un fișier în format electronic, de tip XML, conținând date extrase automat din sistemele informatice ale contribuabililor/plătitorilor, exportate și stocate într-un format standardizat.”

Anexa 3 descrie fluxul obligatoriu, în trei pași (pct. 1):

1. generarea fișierului SAF-T în format XML;
2. verificarea structurii și a corelațiilor cu programul „Validator” pus la dispoziție de ANAF;
3. generarea D406 ca PDF cu XML-ul atașat, semnat electronic.

Pct. 10 adaugă că D406 se transmite „doar în situația în care procesarea a fost realizată cu succes”. Declarația se semnează cu certificat calificat (anexa 2, pct. 6).

### Varianta „manuală” prevăzută de ordin

Anexa 3, pct. 3, enumeră trei metode de pregătire a XML-ului:

- **a)** generare automată din programul de contabilitate sau din ERP;
- **b)** „pregătirea cu un editor de XML a declarației prin editarea pe schema SAF-T cu introducerea directă a datelor relevante”. Ordinul precizează că metoda poate fi folosită de contribuabilii fără sisteme informatice de contabilitate sau ERP;
- **c)** generare externă, printr-un operator de date specializat, pentru contabilitatea externalizată.

Metoda b) este forma legală de „manual”. Excel poate servi ca sursă de date. Documentul depus rămâne însă XML-ul pe schema SAF-T, nu foaia de calcul.

### Ce înseamnă în practică

Un XML scris manual trebuie să respecte aceleași reguli ca unul generat automat:

- structura schemei SAF-T, cu secțiunile obligatorii pentru tipul de raportare;
- corelațiile verificate de validator, de exemplu soldurile din balanță față de nomenclatoare și totalurile din jurnale;
- dimensiunea maximă din ghidul contribuabilului (anexa 3, pct. 11).

Dacă PDF-ul nu e generat cu programul ANAF, anexa 3, pct. 5, cere metadate precise și respectarea modelului din anexa 2.

### Exemplu

Un SRL mic ține evidența într-un program care nu exportă SAF-T. Contabilul are balanța și jurnalele în Excel. Pașii:

1. Mapează conturile din balanță pe nomenclatorul SAF-T.
2. Construiește XML-ul, cu un editor de XML sau cu un script care transformă tabelul în XML pe schemă.
3. Rulează validatorul ANAF și corectează erorile raportate, apoi rulează din nou.
4. Generează din validator PDF-ul cu XML atașat, semnează-l și depune-l.

La o raportare cu multe tranzacții, editarea de mână devine greu de ținut sub control. Metoda b) e realistă pentru volume mici.

### De reținut

- D406 conține un fișier XML pe schema SAF-T, nu un fișier Excel (OPANAF 1783/2021).
- Pregătirea manuală cu un editor de XML e o metodă prevăzută expres (anexa 3, pct. 3 lit. b)).
- Fără validare reușită, declarația nu se transmite (anexa 3, pct. 10).
- Pentru transmitere, PDF-ul cu XML atașat se semnează cu certificat calificat.
