---
title: "Diferențele de curs intră în costul stocurilor?"
description: "Stocurile sunt elemente nemonetare și nu se reevaluează valutar — diferențele de curs se recunosc doar pentru elementele monetare (creanțe, datorii, disponibilități)."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Diferențele de curs intră în costul stocurilor?

Nu. Stocurile sunt, prin definiție, **elemente nemonetare** — costul lor se stabilește o singură dată, la înregistrarea inițială, la cursul de schimb din ziua operațiunii, și nu se mai modifică ulterior din cauza fluctuațiilor cursului valutar. Diferențele de curs (665/765) se recunosc doar pentru elementele monetare — creanțe, datorii și disponibilități — nu pentru stocuri.

## Temeiul legal

::: ghid-temei
„315. - (1) Prin elemente monetare se înțelege disponibilitățile bănești și activele/datoriile de primit/de plătit în sume fixe sau determinabile. [...] (3) Caracteristica esențială a unui element nemonetar este absența unui drept de a primi (sau a unei obligații de a furniza) un număr fix sau determinabil de unități monetare. Exemplele includ: sumele plătite în avans pentru bunuri și servicii; imobilizări necorporale; stocuri; imobilizări corporale; și provizioanele care urmează a fi decontate prin furnizarea unui activ nemonetar."
— OMFP 1802/2014, Reglementările contabile, pct. 315 alin. (1) și (3) (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Textul dă chiar exemplul explicit: **stocurile** sunt un element nemonetar. Consecința practică:

- Costul de intrare al unui stoc achiziționat în valută se stabilește o singură dată, la cursul BNR din ziua recepției (pct. 319 din aceleași reglementări) — acesta rămâne costul contabil al stocului, indiferent cum evoluează ulterior cursul valutar.
- Stocul **nu se reevaluează lunar** la cursul BNR, spre deosebire de creanțe, datorii și disponibilități, care se reevaluează la finalul fiecărei luni.
- Ce se poate reevalua, în legătură cu o achiziție de stoc în valută, e **datoria față de furnizor** — dacă rămâne neachitată, ea e un element monetar și intră în calculul diferențelor de curs la reevaluarea lunară sau la decontare. Dar asta privește datoria, nu costul stocului însuși.

## Ce se greșește în practică

- Se ajustează costul stocului la finalul lunii, în funcție de cursul BNR curent, tratându-l greșit ca element monetar.
- Se include în costul de achiziție al mărfii o „diferență de curs" calculată ulterior recepției, deși costul se fixează o singură dată, la data intrării.
- Se confundă reevaluarea corectă a datoriei față de furnizor (element monetar, dacă rămâne neachitată) cu o presupusă reevaluare a stocului propriu-zis (element nemonetar, care nu se reevaluează niciodată valutar).

## Ce face iConta.eu

Motorul de diferențe de curs din iConta.eu respectă exact această regulă: funcția de calcul acceptă strict trei tipuri de element — creanță, datorie, disponibil — și refuză explicit orice altă valoare, inclusiv „stoc". Nu există, prin construcție, o cale de a introduce un stoc ca obiect al reevaluării valutare sau al calculului de diferență de curs în această funcționalitate.

Dacă ai o datorie față de un furnizor extern, rezultată dintr-o achiziție de marfă în valută și rămasă neachitată, aceea se tratează separat, prin funcționalitatea de decontare/reevaluare a datoriilor în valută din iConta.eu — nu prin ajustarea costului mărfii.

[iConta.eu](/)
