---
title: "Poate administratorul cu contract de mandat să îndeplinească condiția de salariat pentru micro?"
description: "Condiția de a avea cel puțin un salariat pentru încadrarea la microîntreprinderi se poate îndeplini și printr-un contract de mandat al administratorului, dacă remunerația e cel puțin la nivelul salariului minim brut pe țară."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Poate administratorul cu contract de mandat să îndeplinească condiția de salariat pentru micro?

O confuzie frecventă la firmele mici: administratorul e remunerat, plătește contribuții sociale pe remunerația de mandat — deci pare că „firma are pe cineva plătit". Întrebarea e dacă asta îndeplinește condiția legală de „cel puțin un salariat" cerută pentru regimul microîntreprinderilor. Codul fiscal are însă o definiție proprie, extinsă, a termenului „salariat" pentru acest titlu — iar ea include explicit contractul de administrare sau mandat, dacă remunerația trece de un anumit prag.

## Temeiul legal

::: ghid-temei
„[O microîntreprindere este o persoană juridică română care îndeplinește cumulativ următoarele condiții, la data de 31 decembrie a anului fiscal precedent:] g) are cel puțin un salariat, cu excepția situației prevăzute la art. 48 alin. (3)."
— Legea 227/2015 (Codul fiscal), art. 47 alin. (1) lit. g) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„(4) În sensul prezentului titlu, prin salariat se înțelege persoana angajată cu contract individual de muncă cu normă întreagă, potrivit Legii nr. 53/2003 - Codul muncii, republicată, cu modificările și completările ulterioare. Condiția se consideră îndeplinită și în cazul microîntreprinderilor care: a) au persoane angajate cu contract individual de muncă cu timp parțial dacă fracțiunile de normă prevăzute în acestea, însumate, reprezintă echivalentul unei norme întregi; b) au încheiate contracte de administrare sau mandat, potrivit legii, în cazul în care remunerația acestora este cel puțin la nivelul salariului de bază minim brut pe țară garantat în plată."
— Legea 227/2015 (Codul fiscal), art. 51 alin. (4) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Cum se combină textele:

- Art. 47 alin. (1) lit. g) cere „cel puțin un **salariat**", dar Codul fiscal **nu trimite** la definiția din Codul muncii pentru acest termen — art. 51 alin. (4), din același titlu (Titlul III), dă o definiție proprie, specifică regimului micro, mai largă decât cea din dreptul muncii.
- Potrivit acestei definiții, condiția se consideră îndeplinită și dacă administratorul are un **contract de administrare sau mandat** (nu contract individual de muncă), **cu condiția ca remunerația lui să fie cel puțin la nivelul salariului de bază minim brut pe țară garantat în plată**. Sub acest prag, contractul de mandat nu îndeplinește condiția.
- Prin urmare, un SRL condus doar de un administrator cu contract de mandat, fără niciun angajat cu contract individual de muncă, **poate totuși îndeplini condiția de salariat** de la art. 47 alin. (1) lit. g) — dacă remunerația de mandat e cel puțin egală cu salariul minim brut pe țară. Dacă remunerația e sub acest prag, condiția nu e îndeplinită doar prin contractul de mandat, iar firma trebuie să angajeze cel puțin o persoană cu CIM (sau, la firmele nou-înființate, în termenul special de 90 de zile de la înregistrare).

## Ce se greșește în practică

- Se presupune, prin analogie cu definiția „salariatului" din Codul muncii, că doar contractul individual de muncă poate îndeplini condiția — se ignoră definiția proprie, mai largă, de la art. 51 alin. (4) din Codul fiscal, aplicabilă special regimului micro.
- Se consideră suficientă orice remunerație de mandat, oricât de mică, pentru a îndeplini condiția — legea cere expres ca remunerația să fie **cel puțin la nivelul salariului minim brut pe țară garantat în plată**; un mandat neremunerat sau remunerat sub minim nu se califică.
- Nu se verifică, la firmele cu un singur om „la butoane" (administrator unic, fără personal), nici varianta contractului de mandat remunerat la minimul brut, nici eventualul contract individual de muncă pe altă funcție în firmă — oricare dintre cele două poate îndeplini condiția.

## Ce face iConta.eu

La data acestui ghid, iConta.eu tratează distinct, în motorul de calcul, remunerația administratorului cu contract de mandat (CAS 25% + CASS 10% + impozit 10%, fără CIM, fără CAM) față de salariile propriu-zise calculate din statul de plată (`core/contracte_speciale.py`). Aplicația **nu verifică automat**, la nivelul întregii firme, dacă remunerația de mandat atinge pragul salariului minim brut necesar pentru a îndeplini condiția de salariat de la art. 51 alin. (4) lit. b) și nu decide dacă firma se încadrează la micro pe acest temei; această verificare rămâne responsabilitatea contabilului.

[iConta.eu](/)
