---
title: "Greșeala de a nu calcula marja pe produs"
description: "Explică de ce regimul special TVA la marjă cere calcul individual pe fiecare bun vândut, nu o marjă medie pe activitate."
published: 2026-09-26
modified: 2026-10-13
poarta: v1
---

# Greșeala de a nu calcula marja pe produs

În regimul special de marjă pentru bunuri second-hand, TVA-ul nu se calculează pe o marjă medie sau globală a activității — legea cere determinarea taxei colectate pentru fiecare livrare în parte.

Norma leagă explicit taxa colectată de "fiecare livrare" — adică de fiecare bun vândut individual, cu prețul lui de cumpărare și prețul lui de vânzare — nu de o marjă calculată global, la nivel de perioadă, din diferența dintre totalul vânzărilor și totalul achizițiilor. În plus, obligația de a ține jurnal special de cumpărări și de vânzări presupune, structural, o evidență per bun, nu una agregată.

## Ce se greșește în practică

Cea mai frecventă greșeală e aproximarea unei marje medii pe activitate (de exemplu un adaos procentual aplicat la toate vânzările) și calcularea TVA-ului pe acea medie, în loc de a urmări costul de achiziție al fiecărui bun vândut. Această practică distorsionează taxa colectată — dacă unele bunuri se vând cu marjă mai mare și altele cu marjă mică sau negativă, media ascunde diferența, iar bunurile revândute în pierdere (fără TVA de colectat, conform normei) nu mai sunt tratate corect.

## Ce face iConta.eu

Motorul de calcul primește, pentru fiecare vânzare în parte, prețul de vânzare și prețul de cumpărare al bunului respectiv și calculează marja și TVA-ul individual, prin procedeul sutei mărite, cu cota de TVA obligatorie ca parametru (fără valoare implicită). Nota contabilă generată la fiecare vânzare în regim de marjă reflectă separat costul, marja netă și TVA-ul acelei tranzacții — nu există în aplicație o funcție care să agregheze mai multe vânzări într-o marjă medie pentru calculul TVA.

[iConta.eu](/)
