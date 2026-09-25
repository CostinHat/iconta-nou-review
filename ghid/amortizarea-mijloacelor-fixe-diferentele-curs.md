---
title: "Amortizarea mijloacelor fixe și diferențele de curs valutar"
description: "De ce mijloacele fixe, ca elemente nemonetare, nu se reevaluează la curs valutar și nu generează diferențe de curs contabile."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Amortizarea mijloacelor fixe și diferențele de curs valutar

Un mijloc fix cumpărat în valută nu generează diferențe de curs pe durata lui de viață, indiferent cum evoluează cursul BNR. Regula contabilă e clară: imobilizările corporale sunt elemente nemonetare, iar diferențele de curs se calculează exclusiv pentru elementele monetare — creanțe, datorii și disponibilități în sumă fixă.

## Temeiul legal

::: ghid-temei
„315. - (1) Prin elemente monetare se înțelege disponibilitățile bănești și activele/datoriile de primit/de plătit în sume fixe sau determinabile. [...] (3) Caracteristica esențială a unui element nemonetar este absența unui drept de a primi (sau a unei obligații de a furniza) un număr fix sau determinabil de unități monetare. Exemplele includ: sumele plătite în avans pentru bunuri și servicii; imobilizări necorporale; stocuri; imobilizări corporale; și provizioanele care urmează a fi decontate prin furnizarea unui activ nemonetar."
— OMFP 1802/2014, pct. 315 alin. (1) și (3) (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

- Mijlocul fix (cont 21x) se înregistrează inițial la cursul BNR din data recepției/facturii (pct. 319), în lei, și rămâne acolo — valoarea lui în lei nu se mai modifică din cauza cursului valutar.
- Amortizarea se calculează pe valoarea în lei fixată la intrare, pe durata normală de funcționare — cursul valutar ulterior nu influențează nici valoarea amortizabilă, nici cheltuiala lunară cu amortizarea.
- Ce se reevaluează lunar la curs valutar e datoria față de furnizorul extern (dacă mijlocul fix a fost cumpărat pe credit comercial, nedecontat integral) — nu mijlocul fix în sine, ci obligația de plată aferentă lui.
- Diferența de curs care apare la decontarea acelei datorii (665/765) e o cheltuială sau un venit financiar, complet separat de cheltuiala cu amortizarea.

## Ce se greșește în practică

- Se reevaluează greșit valoarea de intrare a mijlocului fix la cursul BNR curent, „ca să reflecte valoarea reală" — contravine direct regulii elementelor nemonetare.
- Se confundă diferența de curs de la datoria furnizorului (665/765, corectă) cu o presupusă „diferență de curs a mijlocului fix" (inexistentă contabil).
- Se recalculează amortizarea lunară în funcție de curs, deși baza de amortizare a fost deja fixată în lei la data intrării activului.

## Ce face iConta.eu

Motorul `core/diferente_curs.py` din iConta.eu respectă exact această limită: funcția `diferenta()` acceptă strict `tip ∈ {creanta, disponibil, datorie}` — un apel cu un tip precum „mijloc fix" sau „imobilizare" ridică o eroare de validare, nu generează nicio notă. Aplicația **nu are și nu poate avea** o funcție de „diferențe de curs la mijloacele fixe", pentru că o asemenea operațiune ar fi contrară OMFP 1802/2014. Ce calculează F041 este strict diferența de curs pe datoria față de furnizorul mijlocului fix, dacă acea datorie e încă nedecontată — prin ecranele de decontare/reevaluare valutară, nu prin fișa mijlocului fix.

[iConta.eu](/)
