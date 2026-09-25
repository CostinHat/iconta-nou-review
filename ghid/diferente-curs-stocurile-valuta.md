---
title: "Diferențe de curs la stocurile în valută"
description: "De ce stocurile cumpărate în valută nu se reevaluează la cursul BNR și rămân înregistrate la cursul din data recepției."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Diferențe de curs la stocurile în valută

Stocurile cumpărate în valută nu au „diferențe de curs" propriu-zise. Sunt un element nemonetar, deci rămân înregistrate la valoarea în lei stabilită la data intrării, indiferent cum evoluează ulterior cursul BNR — spre deosebire de datoria față de furnizor, care e element monetar și chiar se reevaluează.

## Temeiul legal

::: ghid-temei
„315. - (1) Prin elemente monetare se înțelege disponibilitățile bănești și activele/datoriile de primit/de plătit în sume fixe sau determinabile. [...] (3) Caracteristica esențială a unui element nemonetar este absența unui drept de a primi (sau a unei obligații de a furniza) un număr fix sau determinabil de unități monetare. Exemplele includ: sumele plătite în avans pentru bunuri și servicii; imobilizări necorporale; stocuri; imobilizări corporale; și provizioanele care urmează a fi decontate prin furnizarea unui activ nemonetar."
— OMFP 1802/2014, pct. 315 alin. (1) și (3) (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

- Stocul intră în contabilitate la cursul BNR din data recepției/facturii (pct. 319) — un singur curs, fixat o singură dată, pentru toată durata de viață a stocului până la vânzare/consum.
- Nu există „reevaluare lunară a stocului" la cursul BNR, așa cum există pentru creanțe, datorii și disponibilități — pct. 325 vorbește explicit doar despre elemente monetare.
- Ce se reevaluează, dacă marfa nu e plătită integral, e datoria rămasă către furnizor (cont 401) — și aceea generează diferențe de curs (665/765), nu stocul.
- Dacă marfa a fost plătită în avans, avansul e la rândul lui un element nemonetar (exemplu explicit în textul de mai sus), deci nici avansul nu se reevaluează.

## Ce se greșește în practică

- Se recalculează valoarea stocului la finalul lunii, la cursul BNR curent, generând o „diferență de curs" fictivă pe cont de stoc — operațiune fără bază legală.
- Se amestecă diferența de curs reală (de pe datoria față de furnizor) cu o presupusă diferență de curs pe stoc, dublând eronat cheltuiala sau venitul financiar.
- Se ignoră faptul că valoarea stocului rămâne fixă în lei chiar dacă factura furnizorului se decontează mult mai târziu, la un curs diferit.

## Ce face iConta.eu

Motorul de diferențe de curs din iConta.eu (`core/diferente_curs.py`) respectă corect această regulă: funcția `diferenta()` acceptă exclusiv `tip ∈ {creanta, disponibil, datorie}`, iar un apel cu tipul „stoc" ridică o eroare de validare — aplicația **nu generează și nu poate genera** o notă de diferență de curs pe un cont de stoc. Ce calculează F041, dacă marfa din stoc a fost cumpărată pe credit comercial neplătit, este diferența de curs pe datoria față de furnizor (401), prin ecranele de decontare sau reevaluare valutară — nu pe stocul propriu-zis.

[iConta.eu](/)
