---
title: Cum se contabilizează avansul pentru organizarea unei nunți la restaurant?
description: Avansul pentru o nuntă/botez urmează regimul general de avans (TVA exigibilă la încasare), dar restaurantul poate solicita ANAF un plafon de numerar diferit de cel standard de 10.000 lei/zi, printr-o procedură specială prevăzută expres de Legea 70/2015.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se contabilizează avansul pentru organizarea unei nunți la restaurant?

Restaurantele care organizează nunți și botezuri încasează, de regulă, avansuri consistente, adesea în numerar. Legea prevede pentru acest caz particular o derogare de plafon pe care alte tipuri de evenimente nu o au.

## Temeiul legal

::: ghid-temei
"(2) Prin excepție de la prevederile alin. (1), exigibilitatea taxei intervine: ... b) la data la care se încasează avansul, pentru plățile în avans efectuate înainte de data la care intervine faptul generator. Avansurile reprezintă plata parțială sau integrală a contravalorii bunurilor și serviciilor, efectuată înainte de data livrării ori prestării acestora;"

"(1) Operațiunile de încasări în numerar efectuate de persoanele prevăzute la art. 1 alin. (1), de la persoane fizice, reprezentând cesiuni de creanțe, primiri de împrumuturi sau alte finanțări, precum și contravaloarea unor livrări de bunuri sau a unor prestări de servicii se efectuează în limita unui plafon zilnic de 10.000 lei de la o persoană."

"(1) Organizatorii de nunți și botezuri, pentru operațiunile de încasări în numerar pe zi, de la persoane fizice, pentru serviciile legate de aceste evenimente, pot solicita organului fiscal central competent... aprobarea unui alt plafon de încasări decât cel stabilit la art. 4. ... (3) Organul fiscal dispune cu privire la cererea depusă... printr-o decizie în termen de cel mult 15 zile... Decizia are valabilitate un an de la data comunicării."
:::

## Regimul TVA și plafonul special de numerar

Din punct de vedere al TVA, avansul pentru o nuntă/botez nu diferă de orice alt avans: exigibilitatea taxei intervine la data încasării, indiferent de data efectivă a evenimentului (art. 282 alin. 2 lit. b).

Diferența apare la plafonul de numerar. Regula generală (Legea 70/2015, art. 4) limitează încasările în numerar de la o persoană fizică la 10.000 lei/zi — un avans mai mare, plătit integral cash pentru o nuntă, ar depăși ușor acest plafon. Legea prevede însă, explicit pentru acest caz, o procedură de derogare: art. 4^1 permite organizatorilor de nunți și botezuri să solicite organului fiscal central competent aprobarea unui alt plafon de încasări în numerar. Cererea se soluționează printr-o decizie a ANAF în cel mult 15 zile, valabilă un an de la comunicare.

::: ghid-exemplu
Un restaurant care organizează frecvent nunți solicită ANAF, conform art. 4^1, un plafon special de 50.000 lei/zi de la o persoană fizică. Dacă decizia e aprobată, avansul de 40.000 lei încasat cash de la un miri pentru o nuntă se poate înregistra legal, fără a încălca Legea 70/2015 — decizia rămâne valabilă un an de la comunicare, după care trebuie reînnoită.
:::

## Ce se greșește în practică

- Se presupune că plafonul special de 50.000+ lei există automat pentru orice restaurant care organizează nunți, fără să existe o decizie ANAF obținută explicit conform art. 4^1 — fără decizie, se aplică plafonul standard de 10.000 lei/zi.
- Se aplică derogarea și pentru alte tipuri de evenimente găzduite de restaurant (majorate, botezuri civile, conferințe) — art. 4^1 vizează explicit doar nunțile și botezurile.
- Se ignoră valabilitatea de un an a deciziei ANAF și se continuă să se aplice plafonul special după expirare, fără reînnoire.
- Se fracționează încasarea avansului pe mai multe zile ca să se evite atât plafonul standard de 10.000 lei/zi, cât și necesitatea unei decizii ANAF — indiferent de fragmentare, suma totală încasată de la aceeași persoană fizică pentru același avans rămâne supusă plafonului din art. 4, iar peste plafon e nevoie fie de decizia prevăzută la art. 4^1, fie de o modalitate de încasare fără numerar.

## Ce face iConta.eu

Pentru avansul încasat de la client (organizatorii evenimentului), motorul folosește `nota_avans_incasat(suma_fara_tva, cota)`, generând `4111 = 419 + 4427` — mecanica standard pentru orice avans încasat, indiferent de tipul evenimentului.

Modulul `avansuri.py` nu verifică plafonul de numerar și nu are nicio logică specifică pentru derogarea de la art. 4^1 — nu știe, la momentul introducerii avansului, dacă restaurantul deține sau nu o decizie ANAF de plafon special. Obținerea deciziei, verificarea valabilității ei și respectarea plafonului aprobat rămân integral responsabilitatea contabilului/restaurantului la momentul încasării.

[iConta.eu](/)
