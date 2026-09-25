---
title: "Comparație: micro vs profit pentru firmele din HoReCa"
description: "Ce diferă real între impozitul pe veniturile microîntreprinderilor și impozitul pe profit pentru un restaurant sau bar, după eliminarea impozitului specific HoReCa."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Comparație: micro vs profit pentru firmele din HoReCa

Firmele din HoReCa nu mai au un regim fiscal special propriu de câțiva ani — impozitul specific pe activități (hoteluri, restaurante, baruri) a fost eliminat, iar o firmă din acest sector alege astăzi între aceleași două regimuri ca orice altă firmă: microîntreprindere sau impozit pe profit. Diferența dintre ele nu ține de codul CAEN, ci de condițiile generale din Codul fiscal.

## Temeiul legal

::: ghid-temei
„În sensul prezentului titlu, o microîntreprindere este o persoană juridică română care îndeplinește cumulativ următoarele condiții, la data de 31 decembrie a anului fiscal precedent: (...)
c) a realizat venituri care nu au depășit echivalentul în lei a 100.000 euro. (...)
g) are cel puțin un salariat, cu excepția situației prevăzute la art. 48 alin. (3)."
— Legea 227/2015, art. 47 alin. (1) lit. c) și g) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Pentru un restaurant sau bar, alegerea reală e:

- **Regim micro**: cotă unică de **1%** aplicată la venituri (de la 1 ianuarie 2026, art. 51), dacă firma respectă condițiile de la art. 47 — plafon de 100.000 euro venituri, cel puțin un salariat, situații financiare depuse la termen, asociați care nu dețin peste 25% în mai multe firme micro simultan.
- **Impozit pe profit**: cotă de 16% aplicată la profitul impozabil (venituri minus cheltuieli deductibile, cu ajustările specifice), potrivit regulilor generale ale Titlului II — avantajos când marja reală de profit e mică față de cifra de afaceri, situație frecventă în HoReCa din cauza costurilor mari cu materia primă și personalul.
- Bacșișul încasat de la clienți, specific HoReCa, are un regim fiscal separat de venitul din vânzări: nu intră în baza de TVA, nu e supus CAS/CASS și e impozitat cu 10% (impozit pe venit din alte surse), potrivit Legii 376/2022 și art. 115 din Codul fiscal — un element care nu influențează alegerea micro/profit, dar trebuie tratat corect indiferent de regim.
- Restaurantele cu venituri peste 100.000 euro/an trec obligatoriu la impozit pe profit (art. 52), indiferent dacă ar prefera regimul micro.

## Ce se greșește în practică

- Se caută în continuare un „impozit specific HoReCa" separat de micro/profit — acest regim a fost eliminat, iar comparația relevantă azi e strict între cele două regimuri generale.
- Se decide regimul fiscal doar pe baza cifrei de afaceri, fără să se estimeze marja reală de profit — la o marjă mică, impozitul pe profit (16% pe profit) poate fi mai avantajos decât 1% pe toate veniturile, chiar dacă firma s-ar încadra la micro.
- Se tratează bacșișul ca parte din venitul din vânzări la calculul plafonului de 100.000 euro pentru micro, deși regimul lui fiscal e distinct (impozit pe venit din alte surse, reținut la sursă, nu venit din activitatea de bază a firmei).

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu face o comparație automată micro vs. profit** pentru o firmă din HoReCa — alegerea regimului rămâne o decizie a contabilului, pe baza cifrelor reale ale firmei. Aplicația are însă un motor real pentru tratamentul fiscal al bacșișului (`core/bacsis.py`), separat corect de baza de TVA și de contribuțiile sociale, cu impozitare la 10% reținut la sursă, conform Legii 376/2022 și art. 115 din Codul fiscal — o piesă reală din contabilitatea HoReCa, nu o simulare.

[iConta.eu](/)
