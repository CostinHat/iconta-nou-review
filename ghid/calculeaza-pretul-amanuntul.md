---
title: Cum se calculează prețul cu amănuntul?
description: Prețul cu amănuntul se stabilește la recepție ca sumă dintre costul de achiziție (inclusiv transport/taxe accesorii) și adaosul comercial ales de firmă, iar orice schimbare ulterioară a acestui preț de vânzare cere, legal, recalcularea marjei brute.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se calculează prețul cu amănuntul?

Prețul cu amănuntul (prețul de vânzare afișat pentru client) nu e ales arbitrar — el rezultă din costul de achiziție al mărfii, la care se adaugă adaosul comercial stabilit de firmă, plus TVA-ul aferent. E baza pe care se sprijină întreaga metodă global-valorică de gestiune.

## Temeiul legal

::: ghid-temei
„În comerțul cu amănuntul poate fi utilizată metoda prețului cu amănuntul, pentru a determina costul stocurilor de articole numeroase și cu mișcare rapidă, care au marje similare și pentru care nu este practic să se folosească altă metodă. În această situație, costul bunurilor vândute se calculează prin deducerea valorii marjei brute din prețul de vânzare al stocurilor. Orice modificare a prețului de vânzare presupune recalcularea marjei brute.”

— *OMFP 1802/2014, pct. 286 alin. (8).*
:::

## Structura prețului cu amănuntul

Prețul cu amănuntul al unei mărfi e format din trei componente, înregistrate distinct la recepție:

1. **Costul de achiziție** (contul 371, componenta „cost”) — prețul plătit furnizorului, la care se adaugă costurile accesorii de transport și alte taxe direct legate de achiziție, repartizate proporțional pe articole.
2. **Adaosul comercial** (contul 378) — marja stabilită de firmă, ca sumă sau ca procent aplicat costului.
3. **TVA aferentă** (contul 4428, „neexigibilă” până la vânzare) — calculată pe suma cost + adaos, adică pe prețul de vânzare final.

Suma acestor trei componente e prețul cu amănuntul afișat clientului. Legea cere explicit ca **orice modificare ulterioară** a acestui preț de vânzare (o reducere, o majorare) să atragă recalcularea marjei brute — adică recalcularea, pentru mărfurile respective, a raportului dintre cost și adaos, nu doar ajustarea „la vedere” a prețului afișat.

## Ce se greșește în practică

- Se stabilește prețul cu amănuntul doar pe baza costului de achiziție, uitând să se includă separat și distinct adaosul comercial pe contul 378 — fără această separare, calculul lunar al coeficientului de adaos (K) nu mai are date corecte de intrare.
- Se schimbă prețul de vânzare afișat clientului (o promoție, o majorare de preț) fără a recalcula marja brută aferentă stocului deja recepționat la prețul vechi — legea (pct. 286 alin. 8, ultima teză) cere explicit această recalculare.
- Se repartizează costurile accesorii (transport, taxe) în mod egal pe toate articolele dintr-un NIR, indiferent de valoarea lor de bază, în loc de proporțional cu costul fiecărei linii.

## Ce face iConta.eu

Funcția `nir_gv(linii, cota_tva_implicita, transport, taxe, ...)` din `core/stocuri.py` calculează prețul cu amănuntul la recepție: capitalizează costurile accesorii (transport, taxe) proporțional cu costul de bază al fiecărei linii, cu restul de rotunjire alocat pe ultima linie, apoi generează notele separate pentru cost (`371=401`), TVA deductibilă (`4426=401`), transport/taxe accesorii (`371=cont_transport`/`cont_taxe`), adaos (`371=378`) și TVA neexigibilă (`371=4428`). Funcția validează explicit: cotă de TVA lipsă → eroare; cantitate ≤ 0 → eroare; preț de vânzare mai mic decât costul → eroare de „adaos negativ”.

**Limitare confirmată**: `nir_gv` fixează prețul de vânzare doar la intrarea NIR. Nu există în `core/stocuri_api.py` un endpoint dedicat de „reprețuire” a unui stoc deja recepționat — dacă modificați prețul de vânzare al unei mărfi aflate deja în stoc, recalcularea marjei brute cerută de pct. 286 alin. (8) trebuie făcută manual, printr-o notă de ajustare a adaosului, nu printr-un ecran automat dedicat.

[iConta.eu](/)
