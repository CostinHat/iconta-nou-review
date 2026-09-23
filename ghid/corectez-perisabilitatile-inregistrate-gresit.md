---
title: Cum corectez perisabilitățile înregistrate greșit?
description: Corectarea unei note de perisabilitate greșite depinde de ce anume a fost greșit — procentul de limită, contul de stoc sau ajustarea de TVA — și se face prin ștergerea notei (cât timp e încă ciornă) și reintroducerea ei cu datele corecte.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum corectez perisabilitățile înregistrate greșit?

O notă de perisabilitate greșită are, de regulă, una din trei cauze: procentul de limită introdus greșit, contul de stoc greșit sau ajustarea de TVA calculată greșit (aplicată când nu trebuia, sau omisă când trebuia). Corectarea nu presupune un calcul separat — presupune ștergerea notei greșite (rămasă în status ciornă) și reintroducerea ei cu datele corecte prin același ecran.

## Temeiul legal

::: ghid-temei
„Următoarele cheltuieli au deductibilitate limitată: [...] d) scăzămintele, perisabilitățile, pierderile rezultate din manipulare/depozitare, potrivit legii; [...]"

*(Codul fiscal — Legea nr. 227/2015, art. 25 alin. (3) lit. d))*
:::

## Cele trei greșeli tipice și cum se corectează

1. **Procentul de limită greșit** — motorul calculează `limita = valoare_intrari × procent_limita / 100`; dacă procentul introdus nu corespunde grupei de mărfuri (conform anexelor HG 831/2004), tot calculul din aval e greșit: partea deductibilă, partea nedeductibilă și eventuala ajustare de TVA. Corectarea înseamnă ștergerea notei (cât timp e ciornă) și reintroducerea ei cu procentul corect — nu există o corecție parțială, doar pe linia de TVA.
2. **Contul de stoc greșit** — motorul acceptă orice cont de stoc valid din planul de conturi al firmei (parametrul `cont_stoc`, implicit „371", dar testat și cu „301"); dacă produsul aparține altei categorii de stoc, se re-emite nota cu contul corect.
3. **Ajustarea de TVA calculată greșit** — motorul face ajustarea `635=4426` doar dacă există parte nedeductibilă ȘI nu s-a bifat degradare dovedită distrusă. Dacă ajustarea a fost făcută deși degradarea era dovedită (sau invers, omisă când nu era), se corectează prin refacerea notei cu parametrul corect.

## Ce se greșește în practică

- Se corectează doar linia de TVA sau doar procentul, fără să se refacă întreaga notă — riscul e ca 607-ul deductibil/nedeductibil să rămână nealiniat cu noua bază de calcul.
- Se modifică manual o notă deja transmisă în declarație, în loc de stornare și reintroducere.
- Se schimbă contul de stoc fără să se verifice că noul cont există și e valid în planul de conturi al firmei.

## Ce face iConta.eu

Nota de perisabilitate e scrisă inițial cu statusul `'ciorna'` (`core/uc_tenants.py:4085`, funcția `nota_perisabilitati`), ceea ce permite corectarea ei înainte de închiderea lunii; contul de stoc e validat prin `cont_valid.cere_cont`, care respinge un cont inexistent în planul firmei. Motorul de calcul (`core/perisabilitati.py`) nu are o funcție de „recalculare" a unei note existente — corectarea unei perisabilități greșite înseamnă ștergerea/stornarea notei din ciornă și reintroducerea ei cu parametrii corecți prin ecranul Operațiuni speciale > „Perisabilități și scăzăminte".

[iConta.eu](/)
