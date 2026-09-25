---
title: "Cum corectez registrul de evidență fiscală?"
description: "Regula legală de modificare a Registrului de evidență fiscală atunci când se constată diferențe față de veniturile sau cheltuielile înregistrate inițial."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum corectez registrul de evidență fiscală?

Registrul de evidență fiscală nu este un document „bătut în cuie" din momentul completării — legea prevede explicit că se poate modifica atunci când apar diferențe față de ce a fost trecut inițial, cu o singură condiție de timp: până la depunerea declarației rectificative aferente.

## Temeiul legal

::: ghid-temei
„Registrul de evidență fiscală se modifică ori de câte ori se constată diferențe cu privire la veniturile și/sau cheltuielile înregistrate inițial, până la data depunerii declarației rectificative."
— OMFP nr. 3254/2017 privind Registrul de evidență fiscală pentru persoanele fizice, contribuabili potrivit titlului IV din Legea nr. 227/2015 privind Codul fiscal, art. 6 (sursă: anaf_surse/omfp_3254_2017_registru_evidenta_fiscala_persoane_fizice.txt)
:::

Notă de context: acest ordin reglementează registrul de evidență fiscală al **persoanelor fizice** care determină venitul net anual în sistem real (activități independente, cedarea folosinței bunurilor etc.). Există, distinct, și obligația de registru de evidență fiscală a **persoanelor juridice** plătitoare de impozit pe profit, prevăzută de art. 19 din Codul fiscal, al cărei conținut este stabilit prin normele de aplicare (HG nr. 1/2016).

Ce rezultă din text pentru corectarea registrului:

- Corectarea e permisă oricând se constată o diferență, nu doar la închiderea anului fiscal — practic, de fiecare dată când apare un document uitat sau o eroare de calcul.
- Termenul-limită pentru operarea corecției este **data depunerii declarației rectificative** aferente — după acel moment, corecția trebuie să fie deja reflectată în registru, nu ulterioară lui.
- Registrul trebuie să corespundă, în orice moment, cu ce este înscris în Declarația privind venitul realizat din România (sau, după caz, în Declarația anuală de venit pentru asocieri fără personalitate juridică), inclusiv cu orice declarație rectificativă depusă ulterior.

## Ce se greșește în practică

- Se corectează doar declarația fiscală (declarația rectificativă), fără a opera aceeași modificare în Registrul de evidență fiscală, lăsând cele două documente pe cifre diferite.
- Se așteaptă finalul anului pentru a „aduna" toate corecțiile într-o singură operațiune, deși legea permite (și, practic, cere) corectarea imediat ce diferența e constatată.
- Se șterg/rescriu rândurile inițiale în loc să se opereze corectura ca atare, pierzând urma modificării — o practică de audit mai sigură este păstrarea evidenței corecției, nu suprascrierea tăcută.

## Ce face iConta.eu

Da — iConta.eu are un modul dedicat (`core/registru_evidenta_fiscala.py`) care distinge explicit între cele două registre prevăzute de lege: varianta „profit" (persoane juridice, derivată din declarația D101 și contabilitate, pe temeiul art. 19 din Codul fiscal și HG nr. 1/2016) și varianta „venituri PF" (persoane fizice, pe temeiul art. 68 și al OMFP 3254/2017). Modulul construiește rândurile registrului din sursele deja existente în aplicație, astfel încât o corecție a declarației să se reflecte automat și în registru, fără o operațiune manuală separată.

[iConta.eu](/)
