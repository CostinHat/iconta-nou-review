---
title: "Cum apare stoc negativ și cum îl corectez?"
description: "Stocul negativ e semnul unei discrepanțe între evidența scriptică și realitatea faptică — se previne prin înregistrarea corectă a intrărilor înainte de ieșiri și se corectează prin inventariere."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum apare stoc negativ și cum îl corectez?

Fizic, nu poți vinde sau consuma mai mult decât ai în stoc. Când evidența contabilă arată totuși o cantitate negativă la un articol, înseamnă că o ieșire a fost înregistrată înaintea intrării corespunzătoare (sau că intrarea lipsește complet) — un semnal de eroare de evidență, nu o stare economică reală.

## Temeiul legal

::: ghid-temei
„41. - (1) Pentru bunurile la care sunt acceptate scăzăminte, în cazul compensării lipsurilor cu plusurile stabilite la inventariere, scăzămintele se calculează numai în situația în care cantitățile lipsă sunt mai mari decât cantitățile constatate în plus. [...] Diferența stabilită în minus în urma compensării și aplicării tuturor cotelor de scăzăminte, reprezentând prejudiciu pentru entitate, se recuperează de la persoanele vinovate, în conformitate cu dispozițiile legale."
— OMFP nr. 2.861/2009 pentru aprobarea Normelor privind organizarea și efectuarea inventarierii, pct. 41 alin. (1) (sursă: anaf_surse/omfp_2861_2009.txt)
:::

- Un stoc negativ în evidența scriptică **nu e o realitate fizică posibilă** — el semnalează fie o ieșire (vânzare, consum) înregistrată fără o intrare corespunzătoare anterioară, fie o intrare omisă sau introdusă cu întârziere.
- Corectarea corectă trece prin **inventariere**: se stabilește situația faptică reală, se compară cu evidența scriptică, iar diferențele (plusuri/lipsuri) se compensează potrivit regulilor din OMFP nr. 2.861/2009, nu prin simpla „ajustare" a cifrei din sistem.
- Dacă, după compensare, rămâne o **lipsă reală** de stoc, aceasta reprezintă prejudiciu pentru entitate și se recuperează de la persoanele vinovate, potrivit dispozițiilor legale — nu se trece pur și simplu pe cheltuială fără nicio urmă a cauzei.
- Prevenirea reală a stocului negativ ține de disciplina de introducere a datelor: intrările (NIR-uri, recepții) trebuie înregistrate în ordine cronologică, înainte de ieșirile care le consumă.

## Ce se greșește în practică

- Se înregistrează vânzarea/consumul înainte de a introduce recepția corespunzătoare (de exemplu marfa a ajuns fizic, dar NIR-ul se introduce cu întârziere în sistem), generând temporar stoc negativ scriptic pentru un articol care, fizic, exista.
- Se „corectează" stocul negativ prin majorarea manuală a cantității, fără inventariere și fără să se identifice cauza reală a discrepanței.
- Se ignoră lipsa reală de stoc constatată la inventariere, fără a stabili răspunderea sau cauza (furt, eroare de gestiune, perisabilitate peste normă), tratând-o direct ca pierdere contabilă.

## Ce face iConta.eu

La data acestui ghid, modulul de stocuri din iConta.eu (`core/stocuri.py`, `core/stocuri_api.py`, `core/repo_stocuri.py`) calculează costul mediu ponderat și mișcările de stoc pe baza NIR-urilor și descărcărilor de gestiune introduse, cu verificări care opresc calculul la valori aberante (de exemplu adaos negativ sau cost mediu ponderat negativ). Nu am găsit însă o verificare explicită care să blocheze sau să semnaleze o cantitate de stoc negativă rezultată din ordinea de introducere a intrărilor/ieșirilor — evitarea stocului negativ ține, la acest moment, de disciplina de introducere cronologică a documentelor, iar corectarea unei discrepanțe deja apărute rămâne un proces de inventariere condus de contabil, în afara aplicației.

[iConta.eu](/)
