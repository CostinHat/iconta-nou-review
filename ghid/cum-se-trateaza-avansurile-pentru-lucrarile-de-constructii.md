---
title: Cum se tratează avansurile pentru lucrările de construcții?
description: Avansurile pentru lucrări de construcții se înregistrează în conturi distincte de cele pentru stocuri sau imobilizări, cu TVA exigibilă la fiecare plată, iar la contracte cu situații de plată succesive suma cumulată pentru regularizare trebuie urmărită separat de sistem.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se tratează avansurile pentru lucrările de construcții?

Contractele de execuție lucrări (construcții, amenajări, instalații) implică frecvent plăți eșalonate înainte de recepția finală — avansuri la semnarea contractului, situații de plată intermediare pe măsura avansării lucrării. Fiecare astfel de plată are regim fiscal și contabil propriu.

## Temeiul legal

::: ghid-temei
"(2) Prin excepție de la prevederile alin. (1), exigibilitatea taxei intervine: ... b) la data la care se încasează avansul, pentru plățile în avans efectuate înainte de data la care intervine faptul generator. Avansurile reprezintă plata parțială sau integrală a contravalorii bunurilor și serviciilor, efectuată înainte de data livrării ori prestării acestora;"

"311. - (1) Avansurile acordate furnizorilor, precum și cele primite de la clienți se înregistrează în contabilitate în conturi distincte. (2) Avansurile acordate furnizorilor de imobilizări se reflectă distinct de avansurile acordate altor furnizori. ..."

"Contul 409 «Furnizori ‐ debitori» — Cu ajutorul acestui cont se ține evidența avansurilor acordate furnizorilor pentru cumpărări de bunuri de natura stocurilor, prestări de servicii, imobilizări corporale sau necorporale. Contul 409 «Furnizori ‐ debitori» este un cont de activ. În debitul contului 409 se înregistrează: ‐ valoarea avansurilor acordate (401, 404); ..."
:::

## Ce cont analitic se folosește

Pentru o firmă care plătește avans unui constructor (beneficiarul lucrării), contul folosit e `409x`, iar analiticul depinde de natura lucrării: dacă e vorba de o prestare de servicii de construcții-montaj obișnuită, contul e `4092 "Avansuri acordate pentru prestări de servicii"`; dacă lucrarea se capitalizează direct ca imobilizare corporală în curs (ridicarea unei clădiri proprii, de exemplu), analiticul corect e `4093`. Pentru firma de construcții care încasează avansul de la beneficiar, contrapartida e `419`, conform mecanicii standard.

TVA devine exigibilă la fiecare plată/încasare intermediară, nu doar la recepția finală a lucrării — fiecare situație de plată asimilată unui avans generează propria linie de TVA exigibilă, la data plății respective.

## Ce se greșește în practică

- Se așteaptă recepția finală a lucrării pentru a înregistra TVA, tratând situațiile de plată intermediare ca simple "facturi de progres" fără efect de exigibilitate — greșit dacă acestea sunt, în fapt, plăți înainte de livrare/prestare.
- Se folosește analiticul greșit (4091 în loc de 4092/4093) pentru avansurile de construcții, amestecând evidența cu cea a avansurilor pentru stocuri.
- Se pierde evidența sumei cumulate a tuturor avansurilor/situațiilor de plată intermediare pe un contract cu execuție îndelungată, ceea ce complică regularizarea finală.
- Se confundă avansul contractual (plată înainte de orice lucrare executată) cu situația de plată pe lucrări deja executate (care poate avea alt regim de facturare, apropiat de o livrare parțială reală, nu de un avans propriu-zis) — distincția contractuală trebuie clarificată înainte de a alege tratamentul contabil.

## Ce face iConta.eu

Pentru avansul plătit unui constructor, motorul folosește `nota_avans_platit(suma_fara_tva, cota, destinatie="servicii")` (sau `"imobilizari"`, după caz), generând `409x + 4426 = 401`. Pentru avansul încasat de firma de construcții de la beneficiar, `nota_avans_incasat(suma_fara_tva, cota)` generează `4111 = 419 + 4427`. Cota trebuie transmisă explicit la fiecare apel.

O limitare de reținut pentru contractele cu plăți eșalonate: `avansuri.py` **nu agregă** automat mai multe avansuri/situații de plată pe aceeași comandă. Fiecare apel produce o notă separată, iar la momentul regularizării finale, suma cumulată corectă a tuturor avansurilor anterioare trebuie calculată și transmisă de utilizator — motorul nu are context despre plățile anterioare pentru a verifica sau corecta automat o sumă greșită.

[iConta.eu](/)
