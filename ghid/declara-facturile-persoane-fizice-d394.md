---
title: "Se declară facturile către persoane fizice în D394?"
description: "Regula oficială pentru raportarea în declarația 394 a facturilor emise către persoane fizice: de la 01.01.2017, individual, ca operațiuni cu partener neînregistrat, nu prin câmpurile de rezumat PF."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Se declară facturile către persoane fizice în D394?

Da — dar nu prin câmpurile speciale de rezumat pentru persoane fizice. Structura oficială a declarației 394 conținea, până la 01.01.2017, un rezumat agregat separat pentru facturile emise către persoane fizice; de la acea dată, acele câmpuri sunt **obligatoriu 0**, iar facturile respective se declară individual, ca orice altă operațiune, cu partenerul încadrat la tipul „neînregistrat în scopuri de TVA".

## Temeiul legal

::: ghid-temei
„bazaL_PF — Valoare bază impozabilă facturi emise tip L către persoane fizice, cu valoare individuala/persoana mai mică sau egală cu 10000 lei [...] Obligatoriu 0 începând cu 01.01.2017."
„nrFacturiL_PF — Numar facturi emise tip L către persoane fizice, cu valoare individuala/persoana mai mică sau egală cu 10000 lei [...] Obligatoriu 0 începând cu 01.01.2017."
„nrFacturiLS_PF [...] val_LS_PF — Valoare livrari tip LS către persoane fizice, cu valoare individuala/persoana mai mică sau egală cu 10000 lei [...] Obligatoriu 0 începând cu 01.01.2017."
— Structura oficială D394, pozițiile 109, 132, 133, 134 (sursă: anaf_surse/d394_struct_anaf.txt)
:::

Ce rezultă de aici pentru o firmă care vinde către persoane fizice:

- Câmpurile `bazaL_PF`, `tvaL_PF`, `nrFacturiL_PF`, `nrFacturiLS_PF` și `val_LS_PF` sunt **câmpuri moarte**: structura le cere prezente în declarație, dar cu valoarea **obligatoriu 0**, de la 01.01.2017 — nu se mai completează cu sumele reale.
- Facturile emise cu regim normal de taxare (tip L) sau scutite cu drept de deducere (tip LS) către o persoană fizică se raportează ca **operațiune obișnuită** în secțiunea de operațiuni (`op1`), cu partenerul încadrat la tipul „persoană neînregistrată în scopuri de TVA" — alături de celelalte operațiuni de același tip și aceeași cotă, în rezumatul pe tip de partener și cotă.
- Toate câmpurile de mai sus rămân **obligatorii ca prezență** în declarație, chiar dacă valoarea lor e mereu 0 — absența lor din declarație e o eroare de validare, nu o omisiune acceptată.

## Ce se greșește în practică

- Se crede că vânzările sub 10.000 lei către persoane fizice trebuie cumulate în `bazaL_PF`/`tvaL_PF`/`nrFacturiL_PF` — de la 01.01.2017 aceste câmpuri sunt obligatoriu 0; valorile reale se declară individual, ca operațiuni cu partener neînregistrat.
- Se consideră că vânzările către persoane fizice nu trebuie deloc raportate în D394, pentru că nu există un CUI de partener de înscris — de fapt se raportează, individual, în secțiunea de operațiuni.
- Se completează câmpurile PF (`bazaL_PF`, `tvaL_PF` etc.) cu sumele reale calculate manual, generând o declarație respinsă la validare — regula oficială cere exact 0 pentru aceste câmpuri, indiferent de volumul vânzărilor către persoane fizice.

## Ce face iConta.eu

La data acestui ghid, iConta.eu clasifică automat partenerii fără CUI valid de pe facturile emise ca „persoană neînregistrată în scopuri de TVA" și le declară individual, ca operațiuni obișnuite (tip L/LS) în secțiunea de operațiuni a **D394**, agregate pe tip de partener și cotă alături de restul operațiunilor de același fel (`core/d394.py`). Câmpurile vechi de rezumat pentru persoane fizice (`bazaL_PF`, `tvaL_PF`, `nrFacturiL_PF`, `nrFacturiLS_PF`, `val_LS_PF`) sunt scrise mereu cu 0, conform regulii oficiale în vigoare din 01.01.2017, fără să existe vreo cale în aplicație de a le completa altfel.

[iConta.eu](/)
