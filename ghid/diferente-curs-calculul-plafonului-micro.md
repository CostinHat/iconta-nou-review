---
title: "Diferențe de curs în calculul plafonului micro"
description: "Distincția dintre plafonul de încadrare ca microîntreprindere (cifră de afaceri) și baza impozabilă lunară a impozitului micro, unde diferențele de curs chiar apar, dar se scad."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Diferențe de curs în calculul plafonului micro

Aici trebuie separate două calcule diferite, ușor de confundat: **plafonul** care decide dacă rămâi microîntreprindere (100.000 euro cifră de afaceri) și **baza impozabilă** pe care se aplică efectiv cota de 1%/3% în fiecare trimestru. Diferențele de curs valutar nu intră deloc în primul, dar apar explicit — ca sumă care se scade — în al doilea.

## Temeiul legal

::: ghid-temei
„(1^1) În aplicarea prevederilor alin. (1) lit. c) limita privind veniturile realizate se verifică luând în calcul veniturile realizate de persoana juridică română, cumulate cu veniturile întreprinderilor legate cu aceasta, iar veniturile care se iau în calcul sunt cele care constituie cifra de afaceri definită potrivit reglementărilor contabile aplicabile [...]
[Art. 53] Baza impozabilă a impozitului pe veniturile microîntreprinderilor o constituie veniturile din orice sursă, din care se scad: [...] h) veniturile din diferențe de curs valutar; [...] i) veniturile financiare aferente creanțelor și datoriilor cu decontare în funcție de cursul unei valute, rezultate din evaluarea sau decontarea acestora [...]"
— Legea 227/2015 (Codul fiscal), art. 47 alin. (1^1) și art. 53 alin. (1) lit. h) și i) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- **La plafon (art. 47)**: se ia în calcul doar cifra de afaceri, definiție contabilă — veniturile din activitatea curentă (vânzări, servicii). Veniturile din diferențe de curs (cont 765) sunt venituri financiare și nu se cuprind aici deloc.
- **La baza impozabilă lunară/trimestrială (art. 53)**: se pornește de la veniturile din orice sursă, dar apoi se **scad** explicit veniturile din diferențe de curs valutar (lit. h) și veniturile financiare din creanțe/datorii cu decontare în funcție de curs (lit. i) — deci nu se impozitează cu 1%/3%.
- Excepție la scădere: în trimestrul IV (sau ultimul trimestru al perioadei impozabile), se **adaugă** înapoi la bază diferența favorabilă netă dintre veniturile și cheltuielile din curs valutar cumulate de la începutul anului (art. 53 alin. (2) lit. b) — o regularizare anuală, nu o taxare lunară.
- Concluzie practică: diferențele de curs nu influențează niciodată dacă rămâi sau nu microîntreprindere, dar influențează, o singură dată pe an, în trimestrul IV, cât impozit plătești ca microîntreprindere.

## Ce se greșește în practică

- Se include veniturile din 765 la calculul plafonului de 100.000 euro, riscând o ieșire eronată din regimul micro (sau, invers, o rămânere eronată în regim, când plafonul contabil real ar fi fost depășit).
- Se impozitează lunar/trimestrial veniturile din diferențe de curs cu 1%/3%, deși legea le scade explicit din baza fiecărui trimestru, urmând să fie regularizate o singură dată, cumulat, în trimestrul IV.
- Se omite regularizarea din trimestrul IV — diferența favorabilă netă cumulată de la începutul anului se adaugă înapoi la bază exact în acel trimestru, nu se lasă complet neimpozitată.

## Ce face iConta.eu

Funcționalitatea de diferențe de curs valutar din iConta.eu (`core/diferente_curs.py`) generează notele contabile pe 665/765, dar **nu calculează impozitul pe veniturile microîntreprinderilor** și nu aplică distincția de mai sus (scădere lunară vs. regularizare de trimestrul IV) — căutare în cod confirmă că niciun modul de declarație D710/plafon micro nu citește sau nu procesează aceste conturi. Rulajul 665/765 generat automat de F041 rămâne materia primă din care contabilul calculează separat baza impozabilă micro, pentru declarația trimestrială.

[iConta.eu](/)
