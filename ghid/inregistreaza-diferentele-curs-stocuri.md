---
title: "Cum se înregistrează diferențele de curs la stocuri"
description: "Pas cu pas: de ce nu există o notă de diferență de curs pentru stocuri și cum se înregistrează, de fapt, o achiziție de marfă în valută."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se înregistrează diferențele de curs la stocuri

Răspunsul scurt: nu se înregistrează, pentru că nu există. Stocul e un element nemonetar — se înregistrează o singură dată, la cursul din data recepției, și rămâne acolo. Ce se înregistrează în schimb, separat, e diferența de curs de pe datoria față de furnizor, dacă marfa n-a fost plătită integral la recepție.

## Temeiul legal

::: ghid-temei
„315. - (1) Prin elemente monetare se înțelege disponibilitățile bănești și activele/datoriile de primit/de plătit în sume fixe sau determinabile. [...] (3) Caracteristica esențială a unui element nemonetar este absența unui drept de a primi (sau a unei obligații de a furniza) un număr fix sau determinabil de unități monetare. Exemplele includ: sumele plătite în avans pentru bunuri și servicii; imobilizări necorporale; stocuri; imobilizări corporale; și provizioanele care urmează a fi decontate prin furnizarea unui activ nemonetar."
— OMFP 1802/2014, pct. 315 alin. (1) și (3) (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Practic, o achiziție de marfă în valută se înregistrează în doi pași distincți, niciunul dintre ei nefiind o „diferență de curs a stocului":

- **La recepție**: marfa intră la valoarea în lei calculată la cursul BNR din data operațiunii (pct. 319) — % 371 = 401, la acel curs, o singură dată.
- **La decontarea datoriei** (plata furnizorului): dacă între recepție și plată cursul BNR a variat, apare o diferență — dar ea se înregistrează pe datorie (401), nu pe stoc (371): 401 = 5124 + 665 (dacă a crescut cursul, pierdere) sau 401 + 765 = 5124 (dacă a scăzut cursul, câștig).
- **La reevaluarea lunară**, dacă datoria rămâne nedecontată la finalul lunii: se ajustează soldul contului 401 la cursul BNR din ultima zi bancară a lunii, cu diferența în 665/765 — tot fără să atingă stocul.
- Stocul rămâne, în toate aceste cazuri, la valoarea fixată la recepție, până la vânzare sau consum.

## Ce se greșește în practică

- Se caută în mod repetat o „notă de diferență de curs pe stoc" care, contabil, nu are cum să existe — confuzie cu diferența de curs de pe datoria aferentă.
- Se modifică manual costul de achiziție al stocului la fiecare închidere de lună, „ca să corespundă cursului curent" — practică incorectă, care denaturează costul de ieșire din gestiune.
- Se omite complet înregistrarea diferenței de curs reale, de pe datoria față de furnizor, tocmai pentru că atenția se concentrează greșit pe stoc.

## Ce face iConta.eu

Funcționalitatea de diferențe de curs valutar (`core/diferente_curs.py`) respinge explicit tipul „stoc": funcția care calculează diferența acceptă doar `creanta`, `disponibil` sau `datorie`. Aplicația nu generează, deci, nicio notă de diferență de curs pe conturile de stoc — corect, conform regulii de mai sus. Ce automatizează F041 este diferența de curs pe datoria față de furnizorul mărfii (cont 401), prin ecranele „Operațiuni speciale" → decontare sau reevaluare valutară; înregistrarea inițială a stocului la cursul de recepție se face separat, din ecranul de facturare/achiziții.

[iConta.eu](/)
