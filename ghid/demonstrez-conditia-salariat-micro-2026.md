---
title: "Cum demonstrez condiția de salariat pentru micro în 2026"
description: "Una din condițiile pentru încadrarea ca microîntreprindere e să ai cel puțin un salariat — cum se dovedește îndeplinirea acestei condiții și ce excepție prevede legea."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum demonstrez condiția de salariat pentru micro în 2026

Pe lângă plafonul de venituri și structura acționariatului, o firmă trebuie să aibă cel puțin un salariat pentru a rămâne microîntreprindere. Condiția pare simplă, dar dovada ei ține de existența unui contract individual de muncă activ, nu doar de intenția de a angaja.

## Temeiul legal

::: ghid-temei
„În sensul prezentului titlu, o microîntreprindere este o persoană juridică română care îndeplinește cumulativ următoarele condiții, la data de 31 decembrie a anului fiscal precedent: [...] g) are cel puțin un salariat, cu excepția situației prevăzute la art. 48 alin. (3)."
— Legea nr. 227/2015 (Codul fiscal), art. 47 alin. (1) lit. g) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Condiția se verifică, la fel ca celelalte condiții de încadrare ca micro, **la 31 decembrie a anului fiscal precedent** — nu în orice moment al anului curent.
- Dovada existenței salariatului e, în practică, **contractul individual de muncă activ** raportat în Revisal/REGES-ONLINE — nu simpla intenție sau o colaborare cu o persoană fizică autorizată, care nu are calitatea de salariat. Condiția se poate îndeplini și fără CIM, printr-un **contract de administrare sau mandat** al administratorului, dacă remunerația e cel puțin la nivelul salariului minim brut pe țară (art. 51 alin. (4) lit. b) din Codul fiscal).
- Legea prevede o **excepție** la art. 48 alin. (3), pentru situații specifice (de regulă legate de firmele nou-înființate, în anul înființării) — condiția de salariat nu se aplică rigid tuturor microîntreprinderilor, în toate momentele.
- Pierderea condiției (de exemplu încetarea contractului unicului salariat, fără angajarea altuia într-un termen stabilit de lege) poate duce la ieșirea din regimul micro și trecerea la impozit pe profit, potrivit regulilor de la art. 48-52 din Codul fiscal.

## Ce se greșește în practică

- Se consideră îndeplinită condiția pentru că administratorul sau asociatul „lucrează în firmă", deși nu are contract individual de muncă, ci doar calitate de administrator/asociat.
- Se ignoră termenul legal de înlocuire a salariatului, atunci când singurul contract de muncă încetează în cursul anului, expunând firma riscului de a pierde regimul micro fără să se fi luat nicio măsură.
- Se aplică excepția de la art. 48 alin. (3) fără verificarea condițiilor ei specifice, presupunând că orice firmă nou-înființată e automat scutită de condiția salariatului, indiferent de situație.

## Ce face iConta.eu

La data acestui ghid, iConta.eu are un modul complet de salarizare și evidență a salariaților (`core/salariati_api.py`, `core/repo_salariati.py`) prin care se pot urmări contractele active. Nu am găsit însă o funcție care să verifice automat, la 31 decembrie, dacă firma are cel puțin un contract de muncă activ și să semnaleze riscul de ieșire din regimul micro pentru anul următor — coroborarea condiției de salariat cu regimul fiscal al firmei rămâne, la acest moment, în sarcina contabilului.

[iConta.eu](/)
