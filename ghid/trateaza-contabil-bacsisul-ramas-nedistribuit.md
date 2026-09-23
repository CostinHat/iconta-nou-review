---
title: Cum se tratează contabil bacșișul rămas nedistribuit la sfârșitul lunii?
description: Bacșișul neredistribuit până la închiderea lunii rămâne o datorie față de salariați, vizibilă în sold — legea nu fixează un termen limită de distribuire, dar nici o variantă de a-l ține nedistribuit pe termen nelimitat.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se tratează contabil bacșișul rămas nedistribuit la sfârșitul lunii?

Dacă la închiderea lunii mai există bacșiș încasat, dar nedistribuit încă, el nu „dispare" din evidență și nu trece în nicio situație pe venituri sau pe rezultat. Rămâne exact ce a fost de la încasare — o datorie a firmei față de salariați, evidențiată pe un analitic distinct.

## Temeiul legal

::: ghid-temei
„Sumele provenite din încasarea bacșișului se înregistrează în contabilitatea operatorilor economici pe seama conturilor de datorii folosind un analitic distinct și se distribuie integral salariaților, pe baza unei evidențe nominale a acestora."

*(Legea nr. 376/2022 pentru modificarea și completarea OUG nr. 28/1999, art. 2^3 alin. (8))*
:::

## Ce înseamnă în bilanțul lunii

Bacșișul încasat, dar nedistribuit, rămâne cu sold creditor în contul `462` (bacșiș de distribuit salariaților) — o datorie curentă, nu un venit amânat sau o rezervă a firmei. La închiderea lunii, acest sold apare în balanță exact ca orice altă datorie nedecontată, până la momentul distribuirii efective.

Legea 376/2022 nu fixează un termen legal explicit până la care bacșișul trebuie distribuit (spre deosebire, de exemplu, de termenele de plată a impozitelor). Ce fixează explicit e caracterul obligatoriu și integral al distribuirii (alin. (8) de mai sus) — deci un sold `462` care rămâne nedistribuit lună de lună, fără o procedură activă de distribuire în desfășurare, e un semnal de neconformare, chiar dacă legea nu indică o dată-limită anume.

## Ce se greșește în practică

- **Bacșișul nedistribuit e „regularizat" prin trecerea lui pe venituri** la închiderea exercițiului, ca și cum ar deveni al firmei dacă nu a fost cerut de nimeni — contrazice direct alin. (9), care exclude orice asimilare la venituri.
- **Soldul `462` e lăsat să crească nesupravegheat**, fără o procedură clară și fără termen intern de distribuire stabilit prin regulamentul cerut la alin. (8).
- **Impozitul de 10% e calculat abia la distribuirea efectivă**, uneori la mult timp după încasare, fără ca acest decalaj să fie documentat sau justificat.

## Ce face iConta.eu

Modulul F010 (`core/bacsis.py`) separă strict cele două operațiuni — `nota_incasare` la momentul încasării și `nota_distribuire` la momentul plății către salariați — astfel încât soldul `462` reflectă în orice moment exact bacșișul încasat, dar nedistribuit încă. Aplicația nu impune și nu verifică automat un termen de distribuire; stabilirea procedurii și a ritmului de distribuire rămâne, conform legii, în sarcina regulamentului intern al operatorului.

[iConta.eu](/)
