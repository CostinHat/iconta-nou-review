---
title: Cum corectez D301 după ce am calculat TVA greșit?
description: Înainte de depunerea la ANAF, corectarea se face direct în grilă prin ștergerea și reintroducerea operațiunii; după depunere, legea cere o declarație rectificativă, pe care iConta.eu nu o poate genera în prezent.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum corectez D301 după ce am calculat TVA greșit?

Descoperirea unei erori de calcul TVA într-o operațiune introdusă pentru D301 ridică o întrebare importantă: momentul la care se descoperă eroarea — înainte sau după depunerea declarației la ANAF — schimbă complet modul de corectare, atât din perspectiva legii, cât și a ceea ce poate face aplicația.

## Temeiul legal

::: ghid-temei
**Articolul 324 alin. (2)**: Decontul special de taxă trebuie întocmit potrivit modelului stabilit prin ordin al președintelui A.N.A.F. și se depune până la data de 25 inclusiv a lunii următoare celei în care ia naștere exigibilitatea operațiunilor menționate la alin. (1). Decontul special de taxă trebuie depus numai pentru perioadele în care ia naștere exigibilitatea taxei.

**Ordinul ANAF 779/2024, Articolul III**: La anexa nr. 1, în formularul 301 „Decont special de taxă pe valoarea adăugată", după căsuța „Declarație rectificativă" se introduce o nouă căsuță, căsuța „Declarație rectificativă ca urmare a unei notificări de conformare". [...] Căsuța «Declarație rectificativă ca urmare a unei notificări de conformare» se bifează în situația în care rectificarea datelor declarate anterior se efectuează ca urmare a unei notificări de conformare, în condițiile Legii nr. 207/2015 [...]
:::

Potrivit legii (art. 324 coroborat cu instrucțiunile de aplicare aferente formularului 301, care prevăd că declarația depusă inițial se rectifică prin depunerea unei noi declarații, pe același format, bifând căsuța corespunzătoare), o eroare descoperită după depunere se corectează printr-o declarație rectificativă.

## Corectare înainte de depunere vs. corectare după depunere

Dacă eroarea este descoperită **înainte** de depunerea declarației la ANAF, corectarea este simplă din punct de vedere tehnic: operațiunea greșită se șterge din grila de operațiuni și se reintroduce cu cota sau valoarea corectă, apoi declarația se regenerează de la zero, pe baza operațiunilor corecte rămase în grilă.

Dacă eroarea este descoperită **după** ce declarația a fost deja depusă la ANAF, legea impune un mecanism diferit: o declarație rectificativă, depusă pe același formular 301, cu bifarea căsuței corespunzătoare ("Declarație rectificativă"), iar de la OPANAF 779/2024, eventual și căsuța suplimentară "Declarație rectificativă ca urmare a unei notificări de conformare", dacă rectificarea este consecința unei astfel de notificări din partea ANAF.

## Ce se greșește în practică

- Se presupune că orice corecție se face la fel, indiferent dacă declarația a fost deja depusă sau nu la ANAF.
- Se încearcă regenerarea declarației din aplicație și depunerea ei ca "declarație nouă" pentru o perioadă deja declarată, fără bifarea căsuței de rectificativă.
- Se ignoră faptul că, dacă rectificarea vine în urma unei notificări de conformare de la ANAF, este necesară bifarea căsuței suplimentare introduse de OPANAF 779/2024.
- Se așteaptă ca aplicația să genereze automat un XML de rectificativă, funcționalitate care nu există momentan.

## Ce face iConta.eu

Pentru corecțiile **înainte de depunere**, aplicația suportă integral fluxul: operațiunea greșită poate fi ștearsă din grilă și înlocuită cu una corectă (cotă, valoare, curs), iar declarația se regenerează pe baza operațiunilor actualizate.

Pentru corecțiile **după depunere**, trebuie spus onest: iConta.eu **nu poate genera în prezent** un XML de declarație rectificativă pentru D301. Câmpul `d_rec` (declarație rectificativă) este hardcodat la valoarea `"0"` la generarea XML-ului, indiferent de situație — nu există în prezent niciun cod care să îl seteze la `"1"`. Aceasta este o limitare de produs cunoscută, nu o simplă necunoaștere a temei: dacă ai nevoie să depui o rectificativă D301 după ce declarația inițială a fost deja depusă la ANAF, această funcționalitate nu este disponibilă momentan în aplicație.

[iConta.eu](/)
