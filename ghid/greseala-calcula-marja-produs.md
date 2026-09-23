---
title: "Greșeala de a nu calcula marja pe produs"
description: "Explică de ce regimul special TVA la marjă cere calcul individual pe fiecare bun vândut, nu o marjă medie pe activitate."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Greșeala de a nu calcula marja pe produs

În regimul special de marjă pentru bunuri second-hand, TVA-ul nu se calculează pe o marjă medie sau globală a activității — legea cere determinarea taxei colectate pentru fiecare livrare în parte.

## Temeiul legal

::: ghid-temei
"pentru determinarea taxei colectate aferente fiecărei livrări, din marja profitului [...] se calculează suma taxei colectate [...] prin aplicarea procedeului sutei mărite"
— HG 1/2016 (norme metodologice CF), pct. 86 alin. (4) lit. c), `anaf_surse/hg_1_2016_norme_cod_fiscal.txt` (linia 8919-8920, Titlul VII), dosar de cercetare F098.

"persoana impozabilă revânzătoare va îndeplini următoarele obligații: a) va ține un jurnal special de cumpărări [...]; b) va ține un jurnal special de vânzări [...]; c) va ține un registru care permite să se stabilească, la finele fiecărei perioade fiscale, totalul bazei de impozitare pentru livrările efectuate în respectiva perioadă fiscală, pe fiecare cotă de TVA aplicabilă, și, după caz, taxa colectată"
— HG 1/2016 (norme metodologice CF), pct. 86 alin. (6) lit. a)-c), `anaf_surse/hg_1_2016_norme_cod_fiscal.txt` (linia 8981-8992, Titlul VII), dosar de cercetare F098.
:::

Norma leagă explicit taxa colectată de "fiecare livrare" — adică de fiecare bun vândut individual, cu prețul lui de cumpărare și prețul lui de vânzare — nu de o marjă calculată global, la nivel de perioadă, din diferența dintre totalul vânzărilor și totalul achizițiilor. În plus, obligația de a ține jurnal special de cumpărări și de vânzări presupune, structural, o evidență per bun, nu una agregată.

## Ce se greșește în practică

Cea mai frecventă greșeală e aproximarea unei marje medii pe activitate (de exemplu un adaos procentual aplicat la toate vânzările) și calcularea TVA-ului pe acea medie, în loc de a urmări costul de achiziție al fiecărui bun vândut. Această practică distorsionează taxa colectată — dacă unele bunuri se vând cu marjă mai mare și altele cu marjă mică sau negativă, media ascunde diferența, iar bunurile revândute în pierdere (fără TVA de colectat, conform normei) nu mai sunt tratate corect.

## Ce face iConta.eu

Motorul de calcul (`core/tva_marja.py`) primește, pentru fiecare vânzare în parte, prețul de vânzare și prețul de cumpărare al bunului respectiv și calculează marja și TVA-ul individual, prin procedeul sutei mărite, cu cota de TVA obligatorie ca parametru (fără valoare implicită). Nota contabilă generată la fiecare vânzare în regim de marjă reflectă separat costul, marja netă și TVA-ul acelei tranzacții — nu există în aplicație o funcție care să agregheze mai multe vânzări într-o marjă medie pentru calculul TVA.

[iConta.eu](/)
