---
title: Cum se calculează costul pe lucrare pentru o firmă de construcții
description: Costul pe lucrare se calculează în iConta.eu prin raportul „realizat pe centru" — cheltuielile și veniturile clasei 6/7 din notele validate, adunate pe centrul de cost al fiecărei lucrări, pentru orice interval de date.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se calculează costul pe lucrare pentru o firmă de construcții

O firmă de construcții cu mai multe lucrări în derulare simultan are nevoie să știe, pentru fiecare, cât a costat până acum — materiale, manoperă, utilaje, cheltuieli indirecte repartizate. iConta.eu calculează acest total prin mecanismul centrelor de cost, cu condiția ca alocarea costurilor pe lucrare să fi fost făcută.

## Temeiul legal

::: ghid-temei
„(6) Persoanele prevăzute la alin. (1)-(4) organizează și conduc, după caz, și contabilitatea de gestiune, potrivit reglementărilor elaborate în acest sens."

— Legea contabilității nr. 82/1991, art. 1 alin. (6)
:::

Calculul costului pe lucrare este contabilitate de gestiune — o organizare internă cerută „după caz", fără o formă sau o metodologie de calcul impusă de vreun act normativ. Legea obligă doar ținerea contabilității în partidă dublă (art. 5) și, „după caz", a unei contabilități de gestiune oarecare — nu o metodă anume de calcul al costului pe proiect.

## Ce se greșește în practică

- Se așteaptă ca aplicația să calculeze automat costul complet al unei lucrări, incluzând amortizarea utilajelor și salariile — acestea nu se alocă automat pe centru de cost; trebuie repartizate manual, altfel costul afișat pentru lucrare e subestimat.
- Se ignoră linia „nealocat" din raport — dacă suma nealocată e mare, costul afișat pe fiecare lucrare e incomplet, nu greșit calculat de aplicație.
- Se compară costul pe lucrare doar cu bugetul anual al firmei, nu cu un buget specific lucrării — bugetele din iConta.eu sunt setate per centru de cost și an, nu la nivel de firmă.

## Ce face iConta.eu

Fiecare lucrare se definește ca un centru de cost. La introducerea notelor manuale (materiale cumpărate direct pentru șantier, manoperă, repartizări de cheltuieli indirecte sau de amortizare), fiecare linie se etichetează cu centrul de cost al lucrării respective.

Raportul „realizat pe centru" adună, pentru orice interval de date ales, cheltuielile (linii cu cont debitor din clasa 6) și veniturile (linii cu cont creditor din clasa 7) din notele validate, grupate pe fiecare centru — deci pe fiecare lucrare — inclusiv lucrările fără activitate în perioadă, afișate cu zero. Diferența cheltuieli-venituri per centru dă costul net al lucrării pe intervalul respectiv. Dacă a fost setat și un buget anual pentru centru, raportul „variantă buget-realizat" arată suplimentar abaterea față de buget, cumulată pe anul calendaristic, cu roșu pentru orice depășire nefavorabilă.

Condiția pentru ca acest calcul să fie complet: toate costurile lucrării — inclusiv cele generate automat (amortizare, salarii) — trebuie repartizate manual pe centrul ei, pentru că aplicația nu face această alocare singură.

[iConta.eu](/)
