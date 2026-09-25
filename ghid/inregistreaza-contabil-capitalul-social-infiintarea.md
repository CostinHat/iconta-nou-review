---
title: "Cum se înregistrează contabil capitalul social la înființarea firmei?"
description: "Conturile și termenele de vărsare a capitalului social la constituirea unui SRL, de la subscriere la vărsarea efectivă."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se înregistrează contabil capitalul social la înființarea firmei?

Capitalul social parcurge, contabil, două momente distincte: **subscrierea** (angajamentul asociaților de a aporta o sumă) și **vărsarea** (depunerea efectivă a banilor sau a bunurilor). Planul de conturi românesc reflectă exact această distincție prin două conturi separate, iar legea societăților impune termene precise pentru trecerea de la unul la celălalt.

## Temeiul legal

::: ghid-temei
„(2) Societatea cu răspundere limitată trebuie să verse 30% din valoarea capitalului social subscris nu mai târziu de 3 luni de la data înmatriculării, dar înainte de a începe operațiuni în numele societății, iar diferența de capital social subscris va fi vărsată: a) pentru aportul în numerar, în 12 luni de la data înmatriculării."
— Legea nr. 31/1990, art. 9^1 alin. (2) (sursă: anaf_surse/legea_31_1990_societatile.txt)
:::

- La subscriere, capitalul se înregistrează în contul **1011 „Capital subscris nevărsat"**, pe seama contului 456 „Decontări cu asociații privind capitalul" (planul de conturi general, OMFP 1802/2014, pct. 594).
- Pe măsură ce asociații depun efectiv sumele în contul bancar al firmei (5121 = 456), suma vărsată se transferă din contul 1011 în contul **1012 „Capital subscris vărsat"**.
- Pentru SRL, legea impune vărsarea a minimum 30% din capitalul subscris în cel mult 3 luni de la înmatriculare, iar restul (pentru aport în numerar) în 12 luni de la înmatriculare — termene diferite de cele pentru societățile pe acțiuni.
- Pentru aporturile în natură, termenul de vărsare a diferenței este de până la 2 ani de la înmatriculare, nu 12 luni.

## Ce se greșește în practică

- Se înregistrează întregul capital social direct în contul 1012 („vărsat"), chiar dacă la data înmatriculării doar 30% a fost efectiv depus — eroare care denaturează bilanțul inițial.
- Se omite complet contul tranzitoriu 456, înregistrând direct capitalul pe seama contului bancar, fără să se reflecte etapa de subscriere.
- Se ignoră termenul legal de vărsare integrală (12 luni pentru numerar, 2 ani pentru aport în natură), iar diferența rămasă nevărsată nu e urmărită și raportată corect ca „Capital subscris și nevărsat" în bilanț.
- Se confundă capitalul social cu aporturile ulterioare ale asociaților (împrumuturi asociați, cont 455) — doar sumele care trec printr-o hotărâre de majorare de capital și mențiune la registrul comerțului ajung în contul 1011/1012.

## Ce face iConta.eu

Din verificarea codului, iConta.eu recunoaște în planul de conturi atât **contul 1012 „Capital subscris vărsat"**, cât și structura generală a capitalurilor proprii, folosite de aplicație în calculul rezervei legale (funcția care aplică regula „5% din profit, plafonat la 20% din capitalul social", conform Legii 31/1990 art. 183 și OMFP 1802/2014) și în generarea bilanțului. Aplicația nu are însă, la data acestui ghid, un flux dedicat „de înființare" care să genereze automat nota contabilă inițială de subscriere și vărsare a capitalului social — această primă notă contabilă se introduce manual, urmând regulile de mai sus.

[iConta.eu](/)
