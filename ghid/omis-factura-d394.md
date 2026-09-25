---
title: "Ce fac dacă am omis o factură din D394?"
description: "Cum se corectează o factură omisă din D394: nu există rectificativă parțială, se depune o declarație nouă, completă, care înlocuiește integral declarația inițială."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce fac dacă am omis o factură din D394?

D394 nu are un mecanism de „adăugare" a unei operațiuni omise: se depune o declarație nouă, completă, pentru aceeași perioadă, care înlocuiește integral declarația depusă anterior.

## Temeiul legal

::: ghid-temei
„persoana impozabilă constată existenţa unor omisiuni/erori [...] trebuie să depună o nouă declaraţie corect completată cu operaţiunile care necesită modificarea şi/sau operaţiunile care nu au fost declarate, declaraţie care înlocuieşte declaraţia informativă depusă iniţial. Nu vor face obiectul redepunerii declaraţiei facturile primite de persoana impozabilă în altă perioadă de raportare faţă de data emiterii acestora de către furnizori."
— OPANAF 2194/2025, Anexa 2 pct. 3 (sursă: anaf_surse/opanaf_2194_2025_d394.txt)
:::

Din text rezultă mecanica exactă a corecției:

- Nu se depune un „supliment" cu doar factura omisă — se reface **întreaga declarație** a perioadei, cu toate operațiunile (cele deja declarate corect + cea omisă).
- Declarația nouă **înlocuiește** integral, nu se adaugă la, cea depusă inițial.
- Excepție explicită: dacă o factură a fost primită de firmă într-o altă perioadă de raportare decât cea a emiterii ei de către furnizor, redepunerea nu e obligatorie pentru acea factură — regula generală de mai sus se aplică omisiunilor propriu-zise, nu decalajelor firești dintre data emiterii și data primirii.

Procedural, dacă la afișarea stării declarației deja depuse apar erori de structură, contribuabilul are termen de **3 zile lucrătoare** să le corecteze și să redepună (Anexa 3, neschimbată de OPANAF 2194/2025) — dar acesta e un pas de validare tehnică, nu mecanismul de adăugare a unei operațiuni omise descris mai sus.

## Ce se greșește în practică

- Se caută o funcție de „rectificativă" separată, de tip D300, care să adauge doar diferența — D394 nu funcționează așa: fiecare redepunere e o declarație completă, nouă.
- Se uită să se includă în declarația nouă operațiunile deja declarate corect, nu doar cea omisă — riscul e o declarație incompletă care „pierde" operațiuni reale.
- Se presupune că orice factură primită cu întârziere față de data emiterii trebuie neapărat să declanșeze o redepunere pe perioada emiterii — textul exceptează explicit acest caz.

## Ce face iConta.eu

Generatorul D394 (`core/d394.py`) produce declarația din tabela unică de facturi a firmei (`core/repo_d394.py`), pe baza filtrelor de perioadă și de status ale documentelor (exclude ciornele, facturile anulate/stornate). Dacă o factură a fost omisă din evidență la momentul primei generări, adăugarea ei ulterioară în aplicație și regenerarea declarației pentru aceeași lună produce automat o declarație nouă, completă, cu toate operațiunile perioadei — exact forma cerută de Anexa 2 pct. 3.

Aplicația rulează validatorul oficial ANAF (DUK) local înainte ca fișierul să fie considerat gata de depus (`core/duk.py`), dar **depunerea efectivă rămâne manuală, prin portalul SPV** — iConta.eu nu retransmite automat la ANAF.

[iConta.eu](/)
