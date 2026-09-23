---
title: "Când este o livrare intracomunitară scutită de TVA?"
description: "Cele două condiții cumulative pentru scutirea de TVA la o livrare intracomunitară de bunuri (LIC), conform art. 294 alin. (2) lit. a) CF."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Când este o livrare intracomunitară scutită de TVA?

O livrare de bunuri către un client dintr-un alt stat membru UE (LIC) este scutită de TVA cu drept de deducere doar dacă sunt îndeplinite, simultan, două condiții. Lipsa oricăreia dintre ele face ca operațiunea să nu mai califice pentru scutire.

## Temeiul legal

::: ghid-temei
CF art. 294 alin. (2) lit. a): „Scutire LIC cu drept de deducere — condiții: cod TVA valid al cumpărătorului comunicat furnizorului + dovada transportului în alt SM.” (sursă: `intracomunitar.py`, docstring; text complet `cod_fiscal_227_2015_consolidat.txt`, L18397+)
:::

Cele două condiții cumulative sunt:

1. **Cod de TVA valid al cumpărătorului**, comunicat furnizorului și verificabil în sistemul VIES la data operațiunii — nu în registrul ANAF de CUI-uri, ci specific în VIES (Registrul de schimb de informații privind TVA la nivel european).
2. **Dovada transportului** bunurilor din România în celălalt stat membru — fără această dovadă, scutirea nu se poate justifica în fața unui control, indiferent dacă partenerul are sau nu cod de TVA valid.

Dacă lipsește oricare dintre cele două, livrarea nu mai e o LIC scutită: se facturează cu TVA românesc, ca o livrare internă.

## Ce se greșește în practică

- Se aplică scutirea pe baza unui cod de TVA „văzut cândva ca valid”, fără verificare la data facturii curente — codul poate fi anulat între timp.
- Se consideră suficient faptul că marfa a plecat fizic din depozit, fără a păstra un document doveditor al transportului (CMR, confirmare de recepție, aviz de însoțire semnat la destinație etc.).
- Se aplică regula LIC (bunuri) unor prestări de servicii, care au un temei și o declarare diferite (art. 278 alin. 2, cod P în D390, nu cod L).

## Ce face iConta.eu

În formularul de vânzare intracomunitară (`vanzare_ic`), aplicația validează exact aceste două condiții — client non-RO, cod valid VIES, dovadă de transport prezentă — și, dacă una dintre ele lipsește, semnalează explicit că trebuie facturat cu TVA, în loc să lase scutirea aplicată „din oficiu”. Verificarea codului de TVA se face live, direct în VIES, la momentul emiterii facturii.

[iConta.eu](/)
