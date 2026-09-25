---
title: "Ce fac dacă am înregistrat o încasare în numerar ca încasare prin bancă?"
description: "Cum se corectează o eroare de clasificare între casă și bancă și de ce nu afectează exigibilitatea TVA la încasare."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce fac dacă am înregistrat o încasare în numerar ca încasare prin bancă?

Confuzia dintre "am primit banii cash" și "am primit banii în cont" e o greșeală de clasificare, nu una de fond fiscal — data încasării, care contează pentru exigibilitatea TVA (inclusiv la TVA la încasare), rămâne aceeași indiferent de instrumentul de plată. Problema reală e alta: contul contabil e greșit (5121 "Conturi la bănci" în loc de 5311 "Casa în lei"), iar dacă firma ține plafonul legal de numerar sau registrul de casă, o încasare "ascunsă" în extrasul bancar poate crea o discrepanță de sold la ambele instrumente de trezorerie.

## Temeiul legal

::: ghid-temei
„Erorile constatate în contabilitate se pot referi fie la exercițiul financiar curent, fie la exercițiile financiare precedente. Corectarea erorilor se efectuează la data constatării lor. [...] Corectarea erorilor aferente exercițiului financiar curent se efectuează pe seama contului de profit și pierdere. [...] Înregistrarea stornării unei operațiuni contabile aferente exercițiului financiar curent se efectuează fie prin corectarea cu semnul minus a operațiunii inițiale (stornare în roșu), fie prin înregistrarea inversă a acesteia (stornare în negru), în funcție de politica contabilă și programele informatice utilizate."
— OMFP 1802/2014, pct. 65 alin. (1)-(2), pct. 67 alin. (1) și pct. 69 (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

- O eroare descoperită în cursul aceluiași exercițiu financiar se corectează direct, la data constatării — nu se așteaptă închiderea anului.
- Corectarea se face prin stornare (în roșu sau în negru) a operațiunii greșite, urmată de înregistrarea corectă.
- Regula nu distinge după tipul erorii — se aplică la fel unei clasificări greșite casă/bancă ca oricărei alte erori de cont.
- Nimic din OMFP 1802/2014 sau din Codul fiscal (art. 282) nu leagă momentul exigibilității TVA de instrumentul de plată (numerar vs. transfer bancar) — contează exclusiv data la care banii au intrat efectiv în posesia firmei.

## Ce se greșește în practică

- Se anulează pur și simplu înregistrarea greșită și se reintroduce data cu o dată ulterioară (a corectării), ceea ce mută artificial data încasării și poate deplasa greșit exigibilitatea TVA pe altă lună/trimestru.
- Se corectează doar contul, fără să se verifice dacă suma a intrat și în registrul de casă fizic (pentru numerar) sau doar în extrasul bancar — riscând un sold de casă nereal.
- Se ignoră plafonul legal de încasări/plăți în numerar (Legea 70/2015) pentru că "oricum a fost o eroare de tastare" — controlul fiscal nu face această distincție dacă înregistrarea corectată arată o încasare cash care depășește plafonul.
- Se presupune că orice corecție de casă/bancă trebuie să treacă prin nota de TVA la încasare — de fapt corecția atinge doar contul de trezorerie (5311 vs. 5121), nu contul de TVA (4427/4428), dacă data încasării rămâne aceeași.

## Ce face iConta.eu

iConta.eu are un motor dedicat pentru contabilizarea automată a extraselor bancare: la import, liniile sunt potrivite automat cu facturile existente (`core/reconciliere.py`), iar pentru liniile fără factură de potrivit, aplicația propune un cont pe baza istoricului validărilor anterioare ale contabilului — un mecanism de sugestie „învățată" (`core/ai_incredere.py`, apelat din `core/reconciliere_api.py`), care ține evidența contului propus vs. contul confirmat final și afișează un nivel de încredere pe fiecare sugestie. Separat, pentru clasificarea generică pe tip de operațiune (comision, dobândă, salarii, impozit etc.) există un motor pe cuvinte-cheie din descriere (`core/banca.py`), fără componentă de învățare proprie. Niciunul dintre aceste mecanisme **nu e o funcție dedicată de „reclasificare casă ↔ bancă"** pentru o încasare deja înregistrată greșit din eroare de operare: corectarea unei asemenea confuzii se face manual, prin stornarea notei greșite și reintroducerea operațiunii pe contul corect, păstrând data reală a încasării.

Pentru contul de TVA aferent, dacă firma aplică TVA la încasare, motorul de exigibilitate (`core/tva_incasare.py`, folosit din `core/d300.py`) calculează exigibilitatea pe baza datei încasării alocate pe factură, nu pe baza instrumentului de plată — deci o corectare de cont trezorerie care păstrează data reală a încasării nu modifică rândul de TVA colectată din decont. iConta.eu nu automatizează însă verificarea plafonului legal de numerar la corectarea manuală a unei asemenea erori — rămâne responsabilitatea contabilului.

[iConta.eu](/)
