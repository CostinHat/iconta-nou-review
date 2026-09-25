---
title: "Cum se programează plățile pentru a evita penalități"
description: "Ce prevede legea pentru dobânzile și penalitățile de întârziere la obligațiile fiscale neplătite la scadență, și de ce iConta.eu nu programează plăți în locul tău."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se programează plățile pentru a evita penalități

Întârzierea la plata obligațiilor fiscale (TVA, contribuții sociale, impozit pe profit sau pe venitul din salarii) nu costă doar suma restantă — se adaugă automat dobânzi și penalități de întârziere, calculate zi cu zi, de la scadență până la stingerea integrală a datoriei. Cunoașterea mecanismului de calcul e primul pas către evitarea lui; programarea efectivă a plăților rămâne însă o decizie și o acțiune a contribuabilului, nu ceva ce se poate „seta" automat într-un soft.

## Temeiul legal

::: ghid-temei
„(1) Pentru neachitarea la termenul de scadență de către debitor a obligațiilor fiscale principale, se datorează după acest termen dobânzi și penalități de întârziere."
— Legea 207/2015 (Codul de procedură fiscală), art. 173 alin. (1) (sursă: anaf_surse/legea_207_2015_consolidat.txt)

„(1) Dobânzile se calculează pentru fiecare zi de întârziere, începând cu ziua imediat următoare termenului de scadență și până la data stingerii sumei datorate, inclusiv. [...] (5) Nivelul dobânzii este de 0,02% pentru fiecare zi de întârziere."
— Legea 207/2015, art. 174 alin. (1) și (5) (sursă: anaf_surse/legea_207_2015_consolidat.txt)

„(1) Penalitățile de întârziere se calculează pentru fiecare zi de întârziere, începând cu ziua imediat următoare termenului de scadență și până la data stingerii sumei datorate, inclusiv. [...] (2) Nivelul penalității de întârziere este de 0,01% pentru fiecare zi de întârziere."
— Legea 207/2015, art. 176 alin. (1) și (2) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Câteva precizări importante din text:

- Dobânda (0,02%/zi) și penalitatea de întârziere (0,01%/zi) se cumulează — nu se aplică doar una dintre ele — și curg amândouă din prima zi de după scadență, nu după o perioadă de grație.
- Penalitatea de întârziere „nu înlătură obligația de plată a dobânzilor" (art. 176 alin. (3)) — sunt două sancțiuni distincte, care se calculează în paralel.
- Accesoriile se calculează „până la data stingerii sumei datorate, inclusiv" — deci fiecare zi suplimentară de întârziere, inclusiv ziua plății efective, se adaugă la calcul.

## Ce se greșește în practică

- Se așteaptă o notificare de la ANAF înainte de a plăti — dobânzile și penalitățile curg din prima zi de întârziere, indiferent dacă a fost emisă sau nu vreo înștiințare.
- Se plătește doar suma principală restantă, presupunând că accesoriile se vor calcula și comunica separat „mai târziu" — ceea ce e adevărat, dar nu scutește de obligația de plată a lor; ele rămân datorate.
- Se confundă termenul de plată a TVA sau contribuțiilor cu termenul de depunere a declarației — sunt date diferite, iar plata cu întârziere generează accesorii chiar dacă declarația a fost depusă la timp.

## Ce face iConta.eu

iConta.eu **nu are o funcție de programare sau execuție a plăților**. Ecranul „Cifrele firmei" din portalul clientului afișează, în secțiunea „Previziune bani (8 săptămâni)", o listă de plăți estimate construită din datele deja existente în contabilitate — inclusiv obligațiile fiscale deja acumulate în balanță (conturile 4423, 431, 436, 444, 4411 — TVA, contribuții, impozit pe salarii, impozit pe profit), cu scadență presupusă pe data de 25 a lunii curente sau următoare. Ecranul e strict informativ: nu există niciun buton pentru a marca o plată drept „programată", nu se pot iniția plăți din aplicație, iar ruta tehnică din spatele ecranului e doar de citire (`GET`), fără niciun mecanism de scriere sau de declanșare a unei acțiuni. Previziunea te poate ajuta să vezi din timp o obligație fiscală care se apropie de scadență, dar plata efectivă — și evitarea dobânzilor/penalităților de mai sus — rămâne o acțiune pe care o faci tu, prin banca sau prin SPV, nu în iConta.

[iConta.eu](/)
