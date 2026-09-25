---
title: "Micro la firmele HoReCa: condiția de salariat 2026"
description: "Excepția specială pentru CAEN-urile de HoReCa de la condiția de salariat s-a încheiat în 2024 — în 2026 aceste firme aplică regula generală, cu grațierile ei uzuale."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Micro la firmele HoReCa: condiția de salariat 2026

Firmele cu coduri CAEN de HoReCa (hoteluri, restaurante, baruri, catering) au avut, pentru o vreme, un regim special în sistemul de impozitare a microîntreprinderilor. În 2026 însă, condiția de salariat pentru aceste firme nu mai e diferită de a oricărei alte microîntreprinderi — excepția specifică HoReCa s-a încheiat.

## Temeiul legal

::: ghid-temei
„Microîntreprinderile care au desfășurat, până la data de 31 decembrie 2023 inclusiv, activități corespunzătoare codurilor CAEN: 5510 - Hoteluri și alte facilități de cazare similare, 5520 - Facilități de cazare pentru vacanțe și perioade de scurtă durată, 5530 - Parcuri pentru rulote, campinguri și tabere, 5590 - Alte servicii de cazare, 5610 - Restaurante, 5621 - Activități de alimentație (catering) pentru evenimente, 5629 - Alte servicii de alimentație n.c.a., 5630 - Baruri și alte activități de servire a băuturilor aplică condiția de a nu mai fi fost plătitoare de impozit pe veniturile microîntreprinderilor, prevăzută la alin. (2), începând cu anul fiscal 2024."
— Codul fiscal (Legea 227/2015), art. 48 alin. (2^2), astfel cum a fost introdus de OUG 115/2023 (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce rezultă din text pentru condiția de salariat:

- Art. 48 alin. (2^2) leagă firmele HoReCa de condiția de la **alin. (2)** — cea de a nu mai fi fost plătitoare de impozit micro anterior — nu de o excepție privind salariatul. Norma nu prevede, pentru 2024 încoace, nicio scutire specială de la condiția „cel puțin un salariat" (art. 47 alin. (1) lit. g)) pentru codurile CAEN 5510, 5520, 5530, 5590, 5610, 5621, 5629, 5630.
- **Concluzia practică pentru 2026**: o firmă HoReCa care aplică regimul micro trebuie să îndeplinească **aceeași condiție de salariat ca orice altă microîntreprindere** — art. 47 alin. (1) lit. g) — fără vreo derogare specifică sectorului.
- Regulile generale de grațiere rămân aplicabile și firmelor HoReCa, la fel ca oricărei microîntreprinderi: firma nou-înființată are 90 de zile de la înregistrare să angajeze primul salariat (art. 48 alin. (3)); un raport de muncă suspendat sub 30 de zile, prima dată în an, nu rupe condiția (art. 48 alin. (3^1)); concediul medical cumulat sub 30 de zile/an nu o rupe (art. 48 alin. (3^3)); iar dacă unicul salariat pleacă, firma are 30 de zile să angajeze un înlocuitor înainte să treacă la impozit pe profit (art. 52 alin. (3)).
- Firmele HoReCa care erau deja plătitoare de micro la 31.12.2023 nu au fost automat scoase din regim — condiția introdusă de alin. (2^2) e cea deja existentă (nu mai fi fost plătitor de micro anterior), aplicată acum și lor, nu o condiție nouă legată de salariați.

## Ce se greșește în practică

- Se presupune, din amintirea unui regim mai vechi, că firmele HoReCa mai au vreo scutire de la condiția de salariat pentru micro — art. 48 alin. (2^2), în forma sa curentă, nu prevede așa ceva; leagă aceste CAEN-uri de o cu totul altă condiție (cea de la alin. (2)).
- Se ignoră grațierile generale (90 de zile la înființare, 30 de zile suspendare fără repetare în an, 30 de zile concediu medical cumulat, 30 de zile înlocuire salariat unic) — firma HoReCa beneficiază de ele exact ca oricare altă microîntreprindere, dar trebuie urmărite atent, pentru că depășirea lor înseamnă trecere la impozit pe profit din trimestrul următor.
- Se confundă condiția de salariat (art. 47 alin. (1) lit. g)) cu plafonul de venituri de 100.000 euro (art. 52 alin. (1)) — sunt condiții separate de ieșire din regimul micro, cu reguli și termene diferite.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu are o constantă sau o verificare dedicată condiției de salariat pentru regimul micro** — comentariile din `core/control_fiscal_api.py` confirmă explicit că nu există nicio constantă de plafon sau condiție micro urmărită automat în cod. Regimul fiscal (micro/profit) e un câmp declarat de utilizator, folosit pentru a decide între D100 și D101, dar aplicația nu verifică dacă firma mai are salariat, dacă o suspendare a depășit 30 de zile sau dacă termenul de 90/30 de zile de la art. 48 a expirat. Modulul de salariați (`core/salariati_api.py`, `core/repo_salariati.py`) urmărește datele de angajare/încetare, dar nu e conectat la o verificare a condiției de menținere în regimul micro. Verificarea acestor termene rămâne, la acest moment, manuală.

[iConta.eu](/)
