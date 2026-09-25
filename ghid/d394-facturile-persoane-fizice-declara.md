---
title: "D394 și facturile de la persoane fizice: se declară"
description: "Cum se raportează în declarația 394 facturile emise către persoane fizice și achizițiile de la persoane fizice, potrivit structurii oficiale a formularului."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# D394 și facturile de la persoane fizice: se declară

Persoanele fizice nu au, de regulă, cod de înregistrare în scopuri de TVA, așa că mulți contabili presupun că tranzacțiile cu ele nu apar în declarația 394. Structura oficială a formularului spune altceva: facturile către persoane fizice se raportează, dar agregat, iar achizițiile de la persoane fizice apar defalcat pe categorii de produs.

## Temeiul legal

::: ghid-temei
„bazaL_PF — Valoare bază impozabilă facturi emise tip L către persoane fizice, cu valoare individuala/persoana mai mică sau egală cu 10000 lei [...] Obligatoriu 0 începând cu 01.01.2017."
„nrFacturiL_PF — Numar facturi emise tip L către persoane fizice, cu valoare individuala/persoana mai mică sau egală cu 10000 lei [...] Obligatoriu 0 începând cu 01.01.2017."
— Structura oficială D394, poziții 109 și 132 (sursă: anaf_surse/d394_struct_anaf.txt)

„<op11> [...] Aparitie numai pentru tip in (L,A,V,C,AI) pt tip_partener=1 și tip=N pt (tip_partener=2 și cota=0)."
„codPR — Cod produs [...] Verificare cu nomenclator produse."
— Structura oficială D394, poziția 233/235 (sursă: anaf_surse/d394_struct_anaf.txt)
:::

Din structura oficială rezultă două mecanisme, dintre care primul e depășit:

- **Facturile emise către persoane fizice** aveau, până la 01.01.2017, un rezumat agregat separat — bază impozabilă (`bazaL_PF`), TVA (`tvaL_PF`) și număr de facturi (`nrFacturiL_PF`). Textul citat mai sus ("Obligatoriu 0 începând cu 01.01.2017") spune exact opusul a ce pare la prima vedere: nu că agregarea e obligatorie, ci că **de la acea dată aceste câmpuri trebuie completate cu 0** — sunt înghețate, nu se mai populează. De atunci, o factură emisă către o persoană fizică (partener neînregistrat în scopuri de TVA) se raportează **individual**, ca orice altă operațiune, cu tip `L` (dacă e taxabilă) sau `LS` (dacă e scutită), în secțiunea `op1` — la fel ca o factură către orice alt partener neînregistrat, fără agregare și fără plafonul de 10.000 lei.
- **Achizițiile de la persoane fizice** (tip_partener=2), atunci când bunul se încadrează la categoriile din art. 331 (cereale, deșeuri, materiale reciclabile etc.), se raportează cu tip `N`, cu secțiunea `op11` obligatorie, cod de produs (`codPR`) verificat față de nomenclatorul ANAF de produse și cu bază impozabilă pe fiecare cod.

## Ce se greșește în practică

- Se presupune că, întrucât persoana fizică nu are cod de TVA, tranzacția nu trebuie declarată deloc în D394 — de fapt, structura oficială obligă la raportare individuală, cu tip L/LS (facturi emise) sau N cu `op11`/`codPR` (achiziții încadrate la art. 331).
- Se caută (sau se completează manual) câmpurile agregate `bazaL_PF`/`tvaL_PF`/`nrFacturiL_PF` pentru facturile emise către persoane fizice — acestea sunt câmpuri moarte de la 01.01.2017; completarea lor cu altceva decât 0 e respinsă de validator.
- Se omite codul de produs (`codPR`) la achizițiile de la persoane fizice încadrate la art. 331, deși secțiunea `op11` îl cere ca verificare față de nomenclatorul de produse.

## Ce face iConta.eu

La data acestui ghid, iConta.eu generează **D394** din facturile introduse în aplicație (`core/d394.py`), clasificând automat partenerii fără CUI valid ca neînregistrați în scopuri de TVA (persoane fizice) și raportând facturile emise către aceștia individual, cu tip `L` sau, dacă cota e 0, reclasificate automat la `LS` — nu în câmpurile agregate `bazaL_PF`/`nrFacturiL_PF`, pe care aplicația le completează mereu cu 0, conform regulii validatorului oficial pentru perioadele de raportare de după 01.01.2017. Pentru achizițiile de la persoane fizice care necesită defalcare pe cod de produs (`op11`/`codPR`, tip N, categoriile art. 331), aplicația respinge cu motiv explicit generarea declarației dacă lipsește categoria de bun cerută de validator, în loc să depună tacit o declarație incompletă.

[iConta.eu](/)
