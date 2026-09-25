---
title: "Cum contabilizez diferențele de curs la avansurile în valută?"
description: "Răspunsul scurt: nu există. De ce avansurile în valută sunt elemente nemonetare și ce se întâmplă, de fapt, la regularizarea lor."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum contabilizez diferențele de curs la avansurile în valută?

Nu contabilizezi diferențe de curs la avansuri, pentru că nu apar. Un avans acordat sau primit în valută e un element nemonetar — se înregistrează o singură dată, la cursul BNR din ziua plății, și rămâne acolo până se regularizează cu factura aferentă. Ce se schimbă de la un caz la altul e doar cum tratezi restul de sold rămas după regularizare, dacă există unul.

## Temeiul legal

::: ghid-temei
„315. - (1) Prin elemente monetare se înțelege disponibilitățile bănești și activele/datoriile de primit/de plătit în sume fixe sau determinabile. [...] (3) Caracteristica esențială a unui element nemonetar este absența unui drept de a primi (sau a unei obligații de a furniza) un număr fix sau determinabil de unități monetare. Exemplele includ: sumele plătite în avans pentru bunuri și servicii; imobilizări necorporale; stocuri; imobilizări corporale; și provizioanele care urmează a fi decontate prin furnizarea unui activ nemonetar."
— OMFP 1802/2014, pct. 315 alin. (1) și (3) (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Practic, pentru un avans plătit unui furnizor extern:

- **La plata avansului**: se înregistrează 4092 = 5124, la cursul BNR din ziua plății — o singură dată.
- **Pe durata avansului**: contul 4092 nu se reevaluează la finalul lunilor următoare, chiar dacă rămâne deschis mai multe luni — spre deosebire de o datorie comercială obișnuită.
- **La regularizare** (primirea facturii finale): factura se înregistrează la cursul ei propriu, iar avansul se stinge (401 = 4092, la valoarea deja fixată a avansului) — nu apare nicio „diferență de curs" din această compensare.
- **Dacă rămâne un rest de plată** (factura e mai mare decât avansul, sau invers), acel rest e o datorie/creanță monetară obișnuită, care de acum încolo se reevaluează lunar (pct. 325) și generează diferențe de curs la decontarea ei finală (pct. 322).

## Ce se greșește în practică

- Se calculează o „diferență de curs" între cursul de la plata avansului și cursul de la primirea facturii, tratând-o ca 665/765 — corect, această diferență nu e o diferență de curs valutar, e doar o consecință a compensării a două sume fixate separat.
- Se reevaluează greșit soldul avansurilor (4092/4093) la finalul fiecărei luni, alături de creanțe și datorii propriu-zise.
- Se ține avansul deschis mult timp fără regularizare, complicând ulterior reconcilierea între suma plătită și factura efectivă, mai ales dacă intervin mai multe livrări parțiale.

## Ce face iConta.eu

`core/diferente_curs.py` validează explicit tipurile de solduri acceptate la `creanta`, `disponibil` și `datorie` — un avans nu se încadrează în niciuna dintre acestea, iar un apel cu tipul „avans" produce o eroare, nu o notă contabilă. Aplicația **nu are** o funcție dedicată de „diferențe de curs la avansuri", pentru că o asemenea funcție ar contrazice regula elementelor nemonetare. Regularizarea avansului cu factura finală și înregistrarea restului de sold ca datorie/creanță rămân operațiuni pe care contabilul le face separat, prin ecranele de facturare, respectiv de decontare valutară (F041) doar pentru restul rămas, dacă există.

[iConta.eu](/)
