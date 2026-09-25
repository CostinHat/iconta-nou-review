---
title: "Plafonul CASS pentru dividende în 2026"
description: "Cum se calculează plafonul de venit care declanșează obligația de plată a CASS pentru dividende, prin cumulare cu celelalte venituri pasive ale persoanei fizice."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Plafonul CASS pentru dividende în 2026

Dividendele încasate de o persoană fizică nu se analizează izolat pentru CASS — ele se cumulează, potrivit Codului fiscal, cu celelalte venituri „pasive" ale aceleiași persoane (chirii, dobânzi, drepturi de proprietate intelectuală, venituri din activități agricole, alte surse), iar pragul de 6, 12 sau 24 de salarii minime brute pe țară se verifică pe totalul cumulat, nu pe fiecare categorie de venit în parte.

## Temeiul legal

::: ghid-temei
„(4) Încadrarea în plafonul anual de cel puțin 6, 12 sau 24 de salarii minime brute pe țară, după caz, se efectuează prin cumularea veniturilor prevăzute la art. 155 alin. (1) lit. c)-h), după cum urmează: [...]
d) venitul și/sau câștigul/câștigul net din investiții, stabilit conform dispozițiilor art. 94-97. În cazul veniturilor din dobânzi se iau în calcul sumele plătite, diminuate cu impozitul reținut, iar în cazul veniturilor din dividende se iau în calcul dividendele plătite, diminuate cu impozitul reținut, distribuite începând cu anul 2018;"
— Legea nr. 227/2015 (Codul fiscal), art. 170 alin. (4) lit. d) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Mecanismul de calcul, pas cu pas:

1. **Se cumulează** toate veniturile din categoriile de la art. 155 alin. (1) lit. c)-h): drepturi de proprietate intelectuală, venituri distribuite din asocieri cu persoane juridice, chirii, venituri din investiții (inclusiv dividende), venituri din activități agricole/silvicultură/piscicultură și venituri din alte surse.
2. **Pentru dividende**, valoarea care intră în cumul este **dividendul net efectiv plătit** — adică suma plătită acționarului/asociatului, diminuată cu impozitul pe dividende reținut la sursă (nu dividendul brut).
3. **Se compară totalul cumulat** cu pragurile de 6, 12 și 24 de salarii minime brute pe țară (art. 170 alin. (2)-(3)): sub 6 salarii minime, CASS e opțională; între 6 și 12, baza de calcul CASS e fixată la 6 salarii minime; între 12 și 24, la 12 salarii minime; peste 24, la 24 de salarii minime.
4. **Cota CASS** (10%) se aplică asupra bazei astfel stabilite — nu asupra sumei efective a dividendelor, dacă aceasta depășește pragul aferent treptei.

## Ce se greșește în practică

- Se calculează plafonul CASS raportându-se doar la dividendele primite, ignorând obligația de cumulare cu chiriile, dobânzile, drepturile de autor sau alte venituri „pasive" ale aceleiași persoane, din același an fiscal.
- Se ia în calcul dividendul brut, deși legea prevede explicit că, pentru dividende, se folosește suma **plătită**, diminuată cu impozitul deja reținut la sursă.
- Se confundă plafonul de la art. 170 alin. (2)-(4) (6/12/24 salarii minime, pentru veniturile „pasive", inclusiv dividende) cu plafonul de 72 de salarii minime introdus de Legea 239/2025 pentru veniturile din activități independente (art. 170 alin. (1)) — sunt structuri de plafonare diferite, aplicabile unor categorii de venit diferite.

## Ce face iConta.eu

La data acestui ghid, motorul de calcul D212 al iConta.eu (`core/d212_engine.py`) calculează CASS pentru veniturile din activități independente (PFA în sistem real), cu plafonul liniar de 72 de salarii minime aplicabil veniturilor 2026, conform art. 170 alin. (1) din Codul fiscal. Codul modulului notează explicit că veniturile pasive — chirii, dividende, dobânzi — „rămân pe trepte 6/12/24 sm" și nu sunt calculate de acest motor: cumularea dividendelor cu celelalte venituri pasive ale persoanei fizice, pentru verificarea plafonului CASS de la art. 170 alin. (2)-(4), rămâne o determinare manuală, realizată de contabil.

[iConta.eu](/)
