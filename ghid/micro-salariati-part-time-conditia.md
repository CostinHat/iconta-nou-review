---
title: "Micro cu salariați part-time: condiția de salariat"
description: "Ce spune Codul fiscal despre condiția de a avea cel puțin un salariat pentru regimul micro și cum se consideră îndeplinită prin contracte cu timp parțial însumate."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Micro cu salariați part-time: condiția de salariat

Una dintre condițiile de încadrare ca microîntreprindere e să existe cel puțin un salariat. Legea definește „salariat", în acest context, ca angajat cu normă întreagă — dar prevede explicit o excepție pentru situația în care firma nu are un singur angajat full-time, ci mai mulți angajați cu timp parțial: dacă fracțiunile lor de normă, însumate, fac o normă întreagă, condiția e considerată îndeplinită.

## Temeiul legal

::: ghid-temei
„În sensul prezentului titlu, prin salariat se înțelege persoana angajată cu contract individual de muncă cu normă întreagă, potrivit Legii nr. 53/2003 - Codul muncii, republicată, cu modificările și completările ulterioare. Condiția se consideră îndeplinită și în cazul microîntreprinderilor care: a) au persoane angajate cu contract individual de muncă cu timp parțial dacă fracțiunile de normă prevăzute în acestea, însumate, reprezintă echivalentul unei norme întregi; b) au încheiate contracte de administrare sau mandat, potrivit legii, în cazul în care remunerația acestora este cel puțin la nivelul salariului de bază minim brut pe țară garantat în plată."
— Legea 227/2015 (Codul fiscal), art. 51 alin. (4) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce înseamnă concret pentru o firmă cu angajați part-time:

- **Regula de bază** e norma întreagă: un singur contract cu normă întreagă îndeplinește direct condiția de la art. 47 alin. (1) lit. g).
- **Excepția pentru part-time** (lit. a): dacă firma are mai mulți salariați cu fracțiuni de normă, condiția e îndeplinită doar dacă **suma fracțiunilor** e echivalentul unei norme întregi — de exemplu, doi salariați cu jumătate de normă fiecare (0,5 + 0,5) satisfac condiția; un singur salariat cu jumătate de normă, singur, nu o satisface.
- Există și o cale alternativă independentă de contractul de muncă (lit. b): contracte de administrare/mandat, dacă remunerația e cel puțin la nivelul salariului minim brut pe țară.
- Există și excepții privind absența temporară a salariatului: dacă raportul de muncă e suspendat sau salariatul e în concediu medical, condiția rămâne îndeplinită dacă perioada nu depășește 30 de zile cumulate în anul fiscal (art. 48 alin. 3^1 și 3^3 Cod fiscal); dincolo de acest prag se aplică regulile de pierdere a regimului micro din art. 52 alin. (3).

## Ce se greșește în practică

- Se presupune că orice contract part-time, indiferent de fracțiunea de normă, satisface singur condiția de salariat — legea cere explicit ca fracțiunile **însumate** să echivaleze cu o normă întreagă.
- Se ignoră calea alternativă a contractelor de administrare/mandat cu remunerație minimă — o firmă fără niciun salariat part-time poate totuși îndeplini condiția pe această cale, dacă administratorul e remunerat corespunzător.
- Se pierde regimul micro fără să se observe la timp — o suspendare de contract sau un concediu medical care depășește 30 de zile cumulate în an schimbă situația de încadrare, cu efecte de la termenele prevăzute la art. 52 alin. (3).

## Ce face iConta.eu

Verificarea condiției de încadrare la regimul micro (inclusiv testul „normă întreagă echivalentă" pentru salariații part-time) **nu are o funcționalitate dedicată în iConta.eu** — nu există în cod un modul care să calculeze automat fracțiunile de normă însumate și să confirme sau infirme îndeplinirea condiției de salariat pentru regimul micro. Decizia de încadrare rămâne, azi, o evaluare pe care contabilul o face manual, pe baza contractelor de muncă ale firmei.

Ce are aplicația, tangențial la acest subiect, e generatorul **Declarației D112** (`core/d112.py`), care calculează corect contribuțiile și baza minimă pentru salariații part-time — inclusiv mecanismul de suprataxare la contract parțial cu venit sub salariul minim (art. 146 alin. 5^6 și art. 168 alin. 6^1 Cod fiscal) — dar acesta e un calcul de contribuții sociale, nu o verificare a condiției de eligibilitate pentru regimul micro. Cele două subiecte sunt distincte: D112 confirmă corectitudinea contribuțiilor plătite pentru salariații part-time existenți, nu dacă suma fracțiunilor lor de normă satisface condiția de „salariat" cerută de art. 51 alin. (4) pentru regimul micro.

[iConta.eu](/)
