---
title: "Cum număr contractele de muncă pentru micro în 2026"
description: "Definiția legală a salariatului relevant pentru condiția de eligibilitate la regimul micro, inclusiv fracțiunile de normă și contractele de administrare/mandat, potrivit art. 51 din Codul fiscal."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum număr contractele de muncă pentru micro în 2026

Condiția „cel puțin un salariat" de la art. 47 nu se verifică prin simpla numărare a contractelor individuale de muncă din REGES-ONLINE. Codul fiscal are o definiție proprie, mai largă, a ceea ce contează drept „salariat" pentru regimul micro — inclusiv fracțiuni de normă însumate și contracte de administrare sau mandat.

## Temeiul legal

::: ghid-temei
„(4) În sensul prezentului titlu, prin salariat se înțelege persoana angajată cu contract individual de muncă cu normă întreagă, potrivit Legii nr. 53/2003 - Codul muncii (...). Condiția se consideră îndeplinită și în cazul microîntreprinderilor care: a) au persoane angajate cu contract individual de muncă cu timp parțial dacă fracțiunile de normă prevăzute în acestea, însumate, reprezintă echivalentul unei norme întregi; b) au încheiate contracte de administrare sau mandat, potrivit legii, în cazul în care remunerația acestora este cel puțin la nivelul salariului de bază minim brut pe țară garantat în plată."
— Legea 227/2015, art. 51 alin. (4) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Cum se numără, corect, în 2026:

- **Contractul individual de muncă cu normă întreagă** îndeplinește direct condiția — un singur astfel de contract e suficient.
- **Contractele cu timp parțial** contează doar dacă, **însumate**, fracțiunile de normă reprezintă echivalentul unei norme întregi — doi salariați cu jumătate de normă fiecare, de exemplu, pot îndeplini condiția împreună, dar unul singur, cu fracțiune mică, nu.
- **Contractul de administrare sau mandat** (nu de muncă) poate îndeplini și el condiția, dar **doar dacă remunerația e cel puțin la nivelul salariului minim brut pe țară garantat în plată** — un mandat neremunerat sau remunerat sub minim nu se califică.
- Dacă unicul salariat pleacă, firma are **30 de zile** de la încetarea raportului de muncă să angajeze un înlocuitor cu contract pe durată nedeterminată sau determinată de cel puțin 12 luni; altfel datorează impozit pe profit din trimestrul următor încetării.
- De la 25 februarie 2026 (OUG 8/2026), condiția salariatului se consideră îndeplinită și dacă acesta e în **concediu medical**, cu condiția ca perioada cumulată pe an să nu depășească **30 de zile**, respectiv dacă raportul de muncă e **suspendat** pentru mai puțin de 30 de zile, înregistrat pentru prima dată în anul fiscal respectiv.

## Ce se greșește în practică

- Se numără doar contractele individuale de muncă cu normă întreagă, ignorând că un contract de administrare/mandat remunerat cel puțin la minimul brut poate îndeplini la fel de bine condiția.
- Se însumează greșit fracțiunile de normă (de exemplu se consideră suficiente două contracte de 1/3 de normă fiecare), fără să se verifice că suma lor atinge efectiv echivalentul unei norme întregi.
- Se ignoră fereastra de 30 de zile pentru înlocuirea salariatului unic care pleacă, declarând prematur pierderea eligibilității la micro, sau invers — se lasă termenul să treacă fără angajare, crezând că mai există timp.

## Ce face iConta.eu

La data acestui ghid, iConta.eu are evidența reală a salariaților firmei, cu un indicator simplu — `are_salariati` — derivat din numărul de rânduri active din tabelul de salariați (`core/salariati_import_api.py`). Acest indicator confirmă doar prezența salariaților în evidență, nu aplică regulile fine de la art. 51 alin. (4): aplicația **nu însumează automat fracțiunile de normă** pentru a verifica echivalentul unei norme întregi și **nu identifică separat** contractele de administrare/mandat remunerate la nivelul minim ca îndeplinind condiția — aceste verificări rămân manuale, pe baza contractelor efectiv introduse.

[iConta.eu](/)
