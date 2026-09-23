---
title: "Simulare: cât plătește un asociat din dividende în 2026"
description: "Cât impozit se reține din dividendele plătite unui asociat în 2026 și de ce cota aplicabilă poate fi diferită de 16% dacă dividendul a fost distribuit înainte de 2026."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Simulare: cât plătește un asociat din dividende în 2026

Suma pe care o încasează efectiv un asociat depinde nu doar de cota lui de participare, ci și de data la care dividendul a fost distribuit — nu de data la care este plătit efectiv.

## Temeiul legal

::: ghid-temei
"(2) În cazul dividendelor distribuite în baza situațiilor financiare interimare întocmite în cursul anului 2025/anului fiscal modificat care începe în anul 2025, cota de impozit pe dividende este de 10%, fără recalcularea impozitului pe dividendele respective, după regularizarea acestora pe baza situațiilor financiare anuale aferente exercițiului financiar 2025 [...], aprobate potrivit legii."
— Legea 141/2025, art. VII alin. (2)
:::

Regula generală, de la 1 ianuarie 2026, este cota de 16% (Legea 141/2025, art. II pct. 5, care modifică art. 97 alin. (7) din Codul fiscal). Dar dacă dividendul a fost distribuit înainte de 2026, la o cotă mai mică, iar plata se face abia în 2026 (eșalonat sau integral), impozitul se calculează la cota valabilă la data distribuirii, nu la cea de la data plății.

## Ce se greșește în practică

Greșeala tipică este aplicarea automată a cotei din anul plății (16% în 2026) pentru orice dividend încasat în 2026, indiferent de anul în care a fost aprobată distribuirea. De exemplu, un dividend distribuit pe 20.12.2025 (cotă 10%) și plătit pe 15.01.2026 trebuie impozitat cu 10%, nu cu 16% — folosirea cotei greșite duce la reținerea unei sume incorecte din suma cuvenită asociatului.

O altă situație frecventă este plata eșalonată: dacă un dividend distribuit este plătit în mai multe tranșe, fiecare tranșă trebuie potrivită cu distribuirea (distribuirile) din care provine, folosind cota de la data acelei distribuiri — nu o cotă unică aplicată la finalul anului.

## Ce face iConta.eu

Cota de impozit pe dividende este ținută într-un registru central, aplicat în funcție de perioadă (5% în 2016–2022, 8% în 2023–2024, 10% în 2025, 16% de la 2026), și se aplică după data distribuirii, nu după data plății sau 31 decembrie a anului declarației.

Pentru situațiile în care distribuirea și plata cad în ani diferiți, sau plata este eșalonată, iConta.eu potrivește automat, tip FIFO, fiecare tranșă de plată cu distribuirile deschise, folosind cota de la data fiecărei distribuiri. Acest mecanism de calcul este folosit identic atât la generarea declarației, cât și pe o cale independentă de reconciliere, pentru a evita erorile de calcul.

Exemplu confirmat: un dividend distribuit 10.000 lei, plătit parțial 6.000 lei, la o cotă de 16%, generează un impozit de 960 lei calculat pe partea efectiv plătită (6.000 lei bază de impozitare).

[iConta.eu](/)
