---
title: "Ce curs valutar folosesc la decontarea unui avans în euro?"
description: "De ce un avans plătit sau încasat în valută nu generează diferențe de curs și rămâne înregistrat la cursul din ziua plății."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce curs valutar folosesc la decontarea unui avans în euro?

Un avans plătit sau încasat în euro nu se „decontează la un curs" în sensul diferențelor de curs valutar — el rămâne înregistrat, pe toată durata lui, la cursul BNR din ziua în care a fost plătit/încasat efectiv. Avansul e un element nemonetar și nu se mai reevaluează ulterior, indiferent cum evoluează cursul.

## Temeiul legal

::: ghid-temei
„315. - (1) Prin elemente monetare se înțelege disponibilitățile bănești și activele/datoriile de primit/de plătit în sume fixe sau determinabile. [...] (3) Caracteristica esențială a unui element nemonetar este absența unui drept de a primi (sau a unei obligații de a furniza) un număr fix sau determinabil de unități monetare. Exemplele includ: sumele plătite în avans pentru bunuri și servicii; imobilizări necorporale; stocuri; imobilizări corporale; și provizioanele care urmează a fi decontate prin furnizarea unui activ nemonetar."
— OMFP 1802/2014, pct. 315 alin. (1) și (3) (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

- Cursul relevant e cel BNR din data plății/încasării efective a avansului (pct. 319) — un singur curs, fixat o singură dată.
- Avansul rămâne la acea valoare în lei până la regularizarea lui prin factura finală — nu se reevaluează lunar și nu generează diferențe de curs pe durata în care stă „în așteptare".
- La regularizare, factura primită/emisă se înregistrează la cursul din data ei; diferența dintre valoarea facturii și valoarea avansului deja plătit **nu** e o diferență de curs valutar — e, contabil, o simplă compensare a două sume deja fixate, fiecare la cursul ei de la data plății.
- Dacă, după regularizare, rămâne un rest de plată/încasare (creanță sau datorie), abia acel rest devine element monetar și intră sub incidența diferențelor de curs (pct. 322, 325).

## Ce se greșește în practică

- Se caută un „curs de decontare" pentru avans, presupunând greșit că avansul se reevaluează la fel ca o creanță sau o datorie.
- Se reevaluează lunar soldul contului de avansuri (4092/4093 sau 419) la cursul BNR curent, generând o diferență de curs fictivă, fără bază legală.
- Se calculează greșit diferența la regularizare, tratând tot restul de plată ca „diferență de curs", deși e vorba de sume care nu au fost niciodată exprimate la același curs.

## Ce face iConta.eu

Motorul de diferențe de curs valutar din iConta.eu (`core/diferente_curs.py`) respectă corect limita elementelor monetare: funcția `diferenta()` acceptă doar `tip ∈ {creanta, disponibil, datorie}`, iar un apel cu tipul „avans" ridică o eroare de validare. Aplicația **nu automatizează** o funcție de „diferențe de curs pentru avansuri" — pentru că, legal, o asemenea funcție n-ar avea temei. Ce calculează F041 este diferența de curs pe soldul rămas după regularizarea avansului cu factura finală, dacă acel sold e o creanță sau o datorie efectivă, nedecontată integral.

[iConta.eu](/)
