---
title: Cum se înregistrează avansurile primite pentru rezervări hoteliere?
description: Avansul pentru o rezervare hotelieră urmează regimul general de avans (TVA exigibilă la încasare, cont 419), fără nicio derogare specială de plafon numerar — derogarea din Legea 70/2015 e limitată explicit la organizatorii de nunți și botezuri.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se înregistrează avansurile primite pentru rezervări hoteliere?

Un hotel care încasează un avans pentru o rezervare (garanție de cameră, plată parțială pentru un eveniment) aplică regimul standard de avans încasat de la client — nu există un regim special pentru industria hotelieră.

## Temeiul legal

::: ghid-temei
"(2) Prin excepție de la prevederile alin. (1), exigibilitatea taxei intervine: ... b) la data la care se încasează avansul, pentru plățile în avans efectuate înainte de data la care intervine faptul generator. Avansurile reprezintă plata parțială sau integrală a contravalorii bunurilor și serviciilor, efectuată înainte de data livrării ori prestării acestora;"

"Contul 419 «Clienți ‐ creditori» — Cu ajutorul acestui cont se ține evidența clienților ‐ creditori, reprezentând avansurile încasate de la clienți. Contul 419 «Clienți ‐ creditori» este un cont de pasiv. În creditul contului 419 se înregistrează: ‐ sumele facturate clienților reprezentând avansuri pentru livrări de bunuri sau prestări de servicii (411); ... În debitul contului 419 se înregistrează: ‐ decontarea avansurilor încasate de la clienți (411); ..."

"(1) Operațiunile de încasări în numerar efectuate de persoanele prevăzute la art. 1 alin. (1), de la persoane fizice, reprezentând cesiuni de creanțe, primiri de împrumuturi sau alte finanțări, precum și contravaloarea unor livrări de bunuri sau a unor prestări de servicii se efectuează în limita unui plafon zilnic de 10.000 lei de la o persoană."
:::

## Mecanica înregistrării și limita de numerar

La încasarea avansului, hotelul emite factură de avans către client (persoană fizică sau juridică) și înregistrează TVA exigibilă imediat, chiar dacă rezervarea/livrarea serviciului are loc mai târziu — art. 282 alin. (2) lit. b) nu face nicio excepție pentru servicii de cazare. Contabil, nota generează `4111 = 419 + 4427`: creanța asupra clientului crește, iar 419 reflectă datoria hotelului față de client până la prestarea efectivă a serviciului (cazare, eveniment).

Dacă avansul e încasat în numerar de la o persoană fizică, se aplică plafonul general din Legea 70/2015 art. 4 — 10.000 lei/zi de la aceeași persoană, fără fragmentare. **Nu există o derogare specifică pentru servicii hoteliere.** Derogarea de plafon prevăzută de art. 4^1 din Legea 70/2015 este limitată explicit la organizatorii de nunți și botezuri, pentru evenimentele legate de aceste ocazii — nu se extinde la rezervări hoteliere obișnuite sau la alte tipuri de evenimente găzduite de hotel.

## Ce se greșește în practică

- Se amână înregistrarea TVA până la data cazării efective, considerând avansul o simplă "garanție" fără efect fiscal — greșit, orice sumă încasată înainte de faptul generator e avans în sensul art. 282 alin. (2) lit. b).
- Se aplică prin analogie derogarea de plafon numerar de la nunți/botezuri (art. 4^1) și pentru alte evenimente găzduite de hotel — derogarea e strict limitată la organizatorii de nunți și botezuri, nu la orice prestator care găzduiește astfel de evenimente.
- Se depășește plafonul de 10.000 lei/zi de la aceeași persoană fizică prin încasări în numerar fracționate pe mai multe zile pentru aceeași rezervare, ca să se evite plata prin card/transfer.
- Se confundă garanția returnabilă (depozit) cu avansul propriu-zis — dacă suma nu reprezintă contravaloare parțială a serviciului, ci o garanție restituibilă necondiționat, tratamentul poate fi diferit; distincția trebuie documentată clar în contract.

## Ce face iConta.eu

Pentru avansul încasat de la client, motorul folosește `nota_avans_incasat(suma_fara_tva, cota)`, care generează linia `4111 = 419 + 4427`, exact mecanica descrisă la pct. 9 din OMFP 1802/2014 pentru contul 419. Cota de TVA trebuie transmisă explicit — nu există o valoare implicită în cod, tocmai pentru a evita aplicarea unei cote învechite.

Motorul nu verifică plafonul de numerar din Legea 70/2015 și nu distinge tipul de serviciu prestat (cazare, eveniment etc.) — validarea plafonului și încadrarea corectă a sumei ca avans (și nu ca garanție returnabilă) rămân în sarcina contabilului la introducerea datelor.

[iConta.eu](/)
