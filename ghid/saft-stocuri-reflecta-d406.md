---
title: "SAF-T pentru stocuri: cum se reflectă în D406"
description: "Secțiunea Stocuri e un fragment separat, generat distinct pentru fiecare perioadă solicitată de ANAF — nu o parte automată a fișierului lunar SAF-T principal."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# SAF-T pentru stocuri: cum se reflectă în D406

Spre deosebire de restul secțiunilor SAF-T (tranzacții, jurnale, parteneri), care intră automat în fișierul lunar/trimestrial principal, secțiunea Stocuri se comportă ca un **fragment separat**: nu se atașează la declarația D406 obișnuită, ci se generează distinct, pentru intervalul de timp cerut de ANAF, eventual în mai multe declarații — una pentru fiecare lună sau trimestru cuprins în solicitare.

## Temeiul legal

::: ghid-temei
„9. Informaţiile privind «stocurile de produse» şi «producţie în curs» sunt transmise pe baza unei solicitări specifice din partea organelor fiscale centrale. În funcţie de perioada pentru care se solicită furnizarea informaţiilor privind stocurile prin fişierul standard de control fiscal (SAF-T), contribuabilii furnizează una sau mai multe declaraţii informative cuprinzând subsecţiunile din fişierul SAF-T relevante pentru «Stocuri», separate pentru fiecare dintre lunile/trimestrele calendaristice cuprinse în perioada pentru care a fost trimisă solicitarea din partea organelor fiscale centrale."
— OPANAF 1783/2021, Anexa 4, pct. 9 (sursă: anaf_surse/opanaf_1783_2021_saft_d406.txt)
:::

Consecința tehnică a acestui text: fișierul de Stocuri nu e „o secțiune în plus" adăugată la fișierul lunar, ci o **declarație informativă separată**, generată câte una pentru fiecare perioadă calendaristică din intervalul solicitat — dacă ANAF cere stocurile pe ultimele trei luni, contribuabilul depune (cel puțin) trei fișiere distincte, nu unul singur cu toate cele trei luni cumulate.

## Ce se greșește în practică

- Se așteaptă ca secțiunea Stocuri să apară automat, lunar, în fișierul SAF-T generat curent, la fel ca celelalte secțiuni — dependența de solicitarea ANAF face imposibilă generarea ei „din oficiu".
- Se generează un singur fișier cumulat pentru un interval de mai multe luni cerut de ANAF, în loc de câte o declarație separată pentru fiecare lună/trimestru din interval.
- Se presupune că „secțiunea Stocuri" înseamnă doar soldurile finale ale lunii curente, ignorând că fragmentul trebuie să reflecte exact perioada cerută explicit de organul fiscal, care poate fi din trecut.

## Ce face iConta.eu

Structura tehnică confirmă exact acest tipar: în iConta.eu, fragmentul Stocuri se generează printr-un endpoint separat de cel al declarației D406 lunare principale, cu un interval de date (`data_start`/`data_end`) introdus explicit — nu e legat automat de ciclul lunar de generare a SAF-T-ului obișnuit. Fragmentul citește mișcările de stoc din gestiunea cantitativ-valorică și calculează soldul de deschidere și de închidere pentru fiecare articol cu mișcări în interval.

Trei limite de spus onest: (1) la data acestui ghid, generarea acestui fragment nu are ecran dedicat în interfață — se apelează direct, tehnic, nu dintr-un buton vizibil contabilului; (2) fragmentul acoperă exclusiv firmele care țin gestiune **cantitativ-valorică** — pentru o firmă care ține gestiune global-valorică (metoda prețului de vânzare cu amănuntul), mișcările de stoc nu sunt înregistrate în sursa de date citită de acest fragment, deci cererea nu găsește niciun articol cu mișcări în perioadă; (3) aplicația nu generează automat câte o declarație separată pentru fiecare lună/trimestru dintr-un interval mai lung — fiecare apel produce un singur fragment, pentru intervalul exact dat, iar împărțirea pe perioade calendaristice separate, dacă ANAF o cere așa, rămâne în sarcina contabilului.

[iConta.eu](/)
