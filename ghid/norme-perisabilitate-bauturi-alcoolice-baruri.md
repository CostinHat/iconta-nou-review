---
title: "Norme de perisabilitate la băuturi alcoolice pentru baruri 2026"
description: "Explică unde se găsesc procentele legale de perisabilitate pe grupe de mărfuri și cum introduce iConta.eu limita aplicabilă."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Norme de perisabilitate la băuturi alcoolice pentru baruri 2026

Procentul exact de perisabilitate admis pentru băuturile alcoolice se stabilește prin anexele HG 831/2004 — un tabel de coeficienți pe grupe de mărfuri, publicat în Monitorul Oficial. Acest ghid explică regula generală și de unde se ia procentul, fără să reproducă un procent nesigur.

## Temeiul legal

::: ghid-temei
"Se aprobă Normele privind limitele admisibile de perisabilitate la mărfuri în procesul de comercializare, prevăzute în anexa care face parte integrantă din prezenta hotărâre."
— HG 831/2004, art. 1, `anaf_surse/hg_831_2004_aprobarea_normelor_limitele_admisibile_perisabilitate.txt`, dosar de cercetare F066.

"Următoarele cheltuieli au deductibilitate limitată: [...] d) scăzămintele, perisabilitățile, pierderile rezultate din manipulare/depozitare, potrivit legii;"
— Codul fiscal (Legea 227/2015), art. 25 alin. (3) lit. d), `anaf_surse/cod_fiscal_227_2015_consolidat.txt`, dosar de cercetare F066.
:::

Limita maximă deductibilă a perisabilității se calculează aplicând coeficientul grupei de mărfuri (stabilit în anexele 1-3 la HG 831/2004) la prețul de înregistrare al produselor intrate în gestiune — nu la stocul final, nici la vânzări. Coeficientul concret pentru băuturile alcoolice depinde de grupa exactă în care se încadrează produsul (anexele fac diferența pe categorii) — de aceea recomandăm consultarea directă a anexei HG 831/2004 publicate în Monitorul Oficial nr. 522/10.06.2004, pentru procentul aplicabil grupei dumneavoastră de produse, în loc de un procent preluat din surse neoficiale.

## Ce se greșește în practică

Greșeala frecventă e aplicarea unui procent "din auzite" sau preluat de la un alt bar, fără verificarea grupei exacte din anexa HG 831/2004 — coeficienții diferă pe categorii de mărfuri, iar o eroare de încadrare duce la o limită deductibilă greșită. A doua greșeală e omiterea condițiilor obligatorii care însoțesc aplicarea limitei: verificare faptică (inventariere/recepție/predare gestiune), aprobarea administratorului și proces-verbal — fără aceste documente, deductibilitatea poate fi contestată chiar dacă procentul aplicat e corect.

## Ce face iConta.eu

iConta.eu nu are un tabel încorporat cu coeficienții de perisabilitate pe grupe de mărfuri (aceștia lipsesc, ca text, chiar din sursele locale verificate pentru acest ghid) — procentul se introduce manual de contabil, în câmpul dedicat din ecranul Operațiuni speciale → "Perisabilități și scăzăminte". Odată introdus, motorul (`core/perisabilitati.py`) calculează limita ca procent aplicat la valoarea intrărilor, împarte pierderea constatată în parte deductibilă (607/cont de stoc) și, dacă e cazul, parte nedeductibilă, cu ajustare de TVA aferentă (635=4426) pe partea care depășește limita — exceptând cazul în care degradarea calitativă și distrugerea sunt dovedite documentat, situație în care ajustarea de TVA nu se aplică. Nota generată e sufixată automat cu referința "HG 831/2004", dar procentul rămâne responsabilitatea contabilului, stabilit din anexa oficială.

[iConta.eu](/)
