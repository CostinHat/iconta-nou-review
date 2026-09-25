---
title: "Cum se scurtează durata de amortizare fiscală: se poate?"
description: "Ce spune legea despre limitele între care se alege durata normală de funcționare a unui mijloc fix și dacă poate fi schimbată ulterior."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se scurtează durata de amortizare fiscală: se poate?

Întrebarea apare de obicei când o firmă vrea să recupereze mai repede, fiscal, valoarea unui mijloc fix — fie pentru optimizare, fie pentru că activul se uzează mai rapid decât s-a estimat inițial. Răspunsul depinde de momentul la care se pune întrebarea: la punerea în funcțiune sau după.

## Temeiul legal

::: ghid-temei
„4. În prezentul catalog pentru fiecare mijloc fix nou achiziționat se utilizează sistemul unor plaje de ani cuprinse între o valoare minima și una maxima, existând astfel posibilitatea alegerii duratei normale de funcționare cuprinsa între aceste limite. Astfel stabilita, durata normala de funcționare a mijlocului fix rămâne neschimbata până la recuperarea integrală a valorii de intrare a acestuia sau scoaterea sa din funcțiune."
— HG nr. 2139/2004, Anexă, Cap. I pct. 4 (sursă: anaf_surse/hg_2139_2004_catalog_clasificare_durate_mijloace_fixe.txt)
:::

Din text rezultă un răspuns în două părți, nu unul singur:

- **La punerea în funcțiune**, firma poate alege orice durată din intervalul minim-maxim prevăzut de Catalog pentru categoria respectivă de mijloc fix (de exemplu 20-30 ani pentru infrastructura de drumuri asfaltate, sau 12-18 ani pentru anumite utilaje) — deci se poate opta, legal, pentru limita minimă a intervalului, ceea ce înseamnă amortizare mai rapidă.
- **După ce durata a fost stabilită**, ea „rămâne neschimbată până la recuperarea integrală a valorii de intrare [...] sau scoaterea sa din funcțiune" — deci nu se poate scurta ulterior o durată deja aleasă, în afara intervalului stabilit la origine.
- Excepție reală: investițiile ulterioare care îmbunătățesc parametrii tehnici ai unui mijloc fix existent recalculează amortizarea pe baza valorii rămase majorate, pe durata normală de utilizare **rămasă** — nu scurtează durata inițială, ci redistribuie valoarea rămasă pe ce a mai rămas din ea.
- Dacă durata normală e deja expirată când se fac investiții ulterioare, se stabilește o durată nouă de către o comisie tehnică internă sau un expert tehnic independent — acesta e singurul mecanism legal de a „reseta" durata, și cere justificare tehnică, nu decizie contabilă discreționară.

## Ce se greșește în practică

- Se presupune că durata de amortizare poate fi modificată oricând, din motive de optimizare fiscală — legea permite alegerea doar la punerea în funcțiune, în interiorul plajei min-max.
- Se aleg duratele din mijlocul intervalului „din prudență", fără să se verifice dacă limita minimă ar fi fost la fel de legală și mai avantajoasă.
- Se confundă recalcularea amortizării la o investiție ulterioară (care redistribuie valoarea rămasă pe durata rămasă) cu o scurtare a duratei inițiale — sunt mecanisme diferite.

## Ce face iConta.eu

Verificat în cod: modulul `core/d406_active.py` calculează amortizarea (liniară sau degresivă) pe baza duratei normale de funcționare introduse pentru fiecare mijloc fix și tratează separat cazul reevaluării, care „taie" durata în etape pe baza duratei rămase reestimate de evaluator (cu temei OMFP 1802/2014). Aplicația **nu validează automat** dacă durata introdusă se încadrează în plaja minimă-maximă din Catalogul HG 2139/2004 pentru categoria respectivă de mijloc fix — alegerea duratei, la punerea în funcțiune, rămâne responsabilitatea contabilului.

[iConta.eu](/)
