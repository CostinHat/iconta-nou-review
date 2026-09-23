---
title: "Am omis perisabilitatea la alimente: ce risc"
description: Omiterea notei de perisabilitate lasă lipsa din gestiune nedocumentată — riscul e ca întreaga pierdere să fie tratată ca lipsă neimputabilă nedeductibilă, cu TVA aferent datorat, nu doar partea peste limita legală.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Am omis perisabilitatea la alimente: ce risc

Dacă pierderea la alimente (scăzăminte firești în procesul de comercializare) nu e înregistrată deloc printr-o notă de perisabilitate, marfa lipsă din gestiune rămâne, din perspectiva legii, o lipsă neimputabilă nedocumentată — nu una încadrată în limitele HG 831/2004. Riscul nu e doar pierderea limitei deductibile, ci tratarea întregii valori ca nedeductibilă, cu TVA de plată.

## Temeiul legal

::: ghid-temei
„Următoarele cheltuieli nu sunt deductibile: [...] c) cheltuielile privind bunurile de natura stocurilor sau a mijloacelor fixe amortizabile constatate lipsă din gestiune ori degradate, neimputabile, precum și taxa pe valoarea adăugată aferentă, dacă aceasta este datorată potrivit prevederilor titlului VII. [...]"

*(Codul fiscal — Legea nr. 227/2015, art. 25 alin. (4) lit. c), teza introductivă)*
:::

## De ce omisiunea costă mai mult decât o notă întârziată

Dacă perisabilitatea e recunoscută și documentată la timp (verificare faptică, aprobarea administratorului, proces-verbal), partea din pierdere care se încadrează în coeficientul HG 831/2004 aplicat la valoarea intrărilor e deductibilă fără ajustare de TVA (art. 25 alin. (3) lit. d)). Dacă însă marfa lipsă nu e niciodată recunoscută printr-o notă de perisabilitate, la un control ea rămâne o simplă „lipsă din gestiune, neimputabilă" — categoria de la art. 25 alin. (4) lit. c), care e **nedeductibilă integral**, cu TVA aferent datorat, în afara excepțiilor enumerate expres la acel alineat (printre care degradarea calitativă dovedită cu dovada distrugerii). Omisiunea, deci, nu doar amână problema — schimbă regimul fiscal aplicabil dintr-unul limitat-deductibil într-unul integral nedeductibil.

## Ce se greșește în practică

- Se presupune că neînregistrarea perisabilității nu are efect fiscal, atâta timp cât marfa lipsă nu apare în vreun document.
- Se descoperă lipsa abia la inventar, fără proces-verbal contemporan cu constatarea — ceea ce face imposibilă justificarea ei ca perisabilitate în limitele legale, chiar dacă valoarea s-ar fi încadrat în coeficient.
- Se înregistrează cu întârziere, în altă lună decât cea a constatării faptice, fără să se poată dovedi condițiile cerute (verificare faptică, aprobare, proces-verbal) la momentul potrivit.

## Ce face iConta.eu

Nota de perisabilitate (`core/uc_tenants.py:4085`, `nota_perisabilitati`) cere luna deschisă și separă automat 607 deductibil de nedeductibil pe baza procentului introdus, cu ajustarea de TVA aferentă părții peste limită — dar aplicația nu detectează singură o lipsă neînregistrată din gestiune; dacă nota nu e introdusă deloc, nimic din motorul F066 nu intervine, iar riscul de recalificare ca lipsă nedeductibilă rămâne integral al contabilului care nu a înregistrat-o la timp.

[iConta.eu](/)
