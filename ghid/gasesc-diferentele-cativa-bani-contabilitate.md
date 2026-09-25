---
title: "Cum găsesc diferențele de câțiva bani din contabilitate?"
description: "De ce balanța de verificare, întocmită lunar, e instrumentul standard pentru localizarea unei diferențe mici, aparent inexplicabile, din contabilitate."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum găsesc diferențele de câțiva bani din contabilitate?

O diferență de câțiva bani, care „nu se leagă" între balanță și extrasul de cont sau între fișele de partener, aproape mereu are o cauză mecanică: o rotunjire aplicată greșit sau de două ori, o notă contabilă cu suma inversată la o zecimală, sau o operațiune înregistrată o dată în plus/lipsă. Balanța de verificare lunară e instrumentul prin care aceste diferențe se localizează, nu se ascund.

## Temeiul legal

::: ghid-temei
„Registrele de contabilitate obligatorii sunt: Registrul-jurnal, Registrul-inventar și Cartea mare. Întocmirea, editarea și păstrarea registrelor de contabilitate se efectuează conform normelor elaborate de Ministerul Finanțelor Publice."
— Legea contabilității nr. 82/1991, art. 20 (sursă: anaf_surse/legea_82_1991_consolidat.txt)
:::

Ce oferă, concret, aceste registre pentru localizarea diferenței:

- **Cartea mare** grupează, pe fiecare cont, toate înregistrările din Registrul-jurnal — balanța de verificare, întocmită pe baza ei, cere ca **totalul sumelor debitoare să fie egal cu totalul sumelor creditoare**, pe fiecare din cele două coloane (rulaj și sold). O diferență, oricât de mică, între cele două totaluri arată o eroare de înregistrare (o notă contabilă cu sume diferite pe debit și credit), nu o eroare de calcul fiscal.
- Dacă balanța „iese" exact (totalurile debitoare = creditoare), dar diferența apare totuși la reconcilierea cu un extras bancar sau cu fișa unui partener, cauza e alta: o rotunjire aplicată de două ori (contabilă și apoi din nou la o exportare/raportare), sau o operațiune care apare o dată în evidența internă și altă dată (sau deloc) în documentul extern comparat.
- Diferențele de „câțiva bani" sunt frecvent efectul rotunjirii aritmetice (la 2 zecimale) aplicate repetat pe același calcul, în loc de o singură dată, la final — o problemă tehnică de rotunjire dublă, nu una de conținut al operațiunii.

## Ce se greșește în practică

- Se „corectează" diferența printr-o notă contabilă artificială pe un cont de diferențe (658/758), fără să se identifice întâi cauza reală — diferența poate reapărea, cumulat, la fiecare închidere ulterioară.
- Se compară direct sume rotunjite de mai multe ori (de exemplu suma dintr-un raport generat, deja rotunjită, cu suma brută din contabilitate), fără să se verifice la ce pas a intervenit rotunjirea.
- Se ignoră balanța de verificare ca prim instrument de control, sărind direct la verificarea fiecărei facturi individuale — balanța arată rapid dacă eroarea e de echilibru contabil (debit ≠ credit) sau de altă natură.

## Ce face iConta.eu

La data acestui ghid, iConta.eu generează balanța de verificare lunară din evidența contabilă generală (jurnal, fișă de cont), utilă exact pentru acest tip de verificare. Pentru calculele fiscale proprii (contribuții, impozite), aplicația foloseşte rotunjire aritmetică (`ROUND_HALF_UP`, la 2 zecimale, o singură dată per calcul) — o disciplină internă menită să evite exact diferențele de „câțiva bani" cauzate de rotunjire bancară (half-to-even) sau de rotunjire dublă. Identificarea unei diferențe concrete, apărute din date introduse manual, rămâne însă un proces de verificare pe care contabilul îl face cu balanța ca punct de plecare.

[iConta.eu](/)
