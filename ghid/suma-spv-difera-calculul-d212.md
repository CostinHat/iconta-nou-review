---
title: "De ce suma din SPV diferă de calculul meu din D212?"
description: "De ce contribuția de asigurări sociale (CAS) afișată de ANAF în SPV poate fi diferită de calculul propriu al contribuabilului, din cauza cumulării tuturor veniturilor supuse contribuției."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# De ce suma din SPV diferă de calculul meu din D212?

Cea mai frecventă cauză este că baza de calcul a CAS pentru o persoană cu venituri din activități independente și/sau drepturi de proprietate intelectuală **nu se stabilește separat pe fiecare sursă de venit**, ci prin cumularea tuturor veniturilor din aceste categorii, realizate din orice sursă. Dacă la calculul propriu s-a ținut cont doar de o parte din venituri (de exemplu, de la o singură PFA sau un singur contract), iar ANAF are în evidență și alte surse deja raportate, totalul din SPV poate fi diferit.

## Temeiul legal

::: ghid-temei
„(3) Încadrarea în plafonul anual de cel puțin 12 salarii minime brute pe țară sau de cel puțin 24 de salarii minime brute pe țară, după caz, se efectuează prin cumularea veniturilor nete și/sau a normelor anuale de venit din activități independente determinate potrivit art. 68, 68^3 și 69, a venitului brut realizat în baza contractelor de activitate sportivă potrivit art. 68^1, precum și a veniturilor nete din drepturi de proprietate intelectuală determinate potrivit art. 72, 72^1 și 73, realizate în anul pentru care se datorează contribuția."
— Legea nr. 227/2015 (Codul fiscal), art. 148 alin. (3) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

De ce apar diferențe, concret:

- Plafonul de 12, respectiv 24 de salarii minime brute pe țară — care decide baza de calcul a CAS — se verifică prin **cumularea** tuturor veniturilor nete/normelor de venit din activități independente, a veniturilor din contracte de activitate sportivă și a veniturilor nete din drepturi de proprietate intelectuală, indiferent din câte surse provin (art. 148 alin. (3)).
- Dacă o persoană are, de exemplu, venituri de la o PFA plus venituri din drepturi de autor plătite de un editor (raportate de plătitor prin declarații informative proprii), calculul propriu al persoanei, dacă ia în calcul doar o singură sursă, poate subestima baza reală — pe când SPV, alimentat cu toate declarațiile depuse de toți plătitorii/contribuabilul, reflectă totalul cumulat.
- Diferențele pot apărea și din recalculări din oficiu efectuate de organul fiscal (de exemplu, în situații speciale reglementate prin proceduri ANAF), care ajustează contribuția declarată inițial pe baza unor date suplimentare deținute de administrația fiscală.

## Ce se greșește în practică

- Se calculează CAS/CASS pornind doar de la veniturile unei singure activități/surse, ignorând obligația de cumulare de la art. 148 alin. (3) pentru toate veniturile din activități independente și drepturi de proprietate intelectuală ale aceleiași persoane.
- Se presupune că suma afișată în SPV este întotdeauna greșită dacă nu coincide cu calculul propriu, fără a verifica mai întâi dacă există alte venituri, din alte surse, deja cunoscute de ANAF.
- Se ignoră faptul că baza de calcul este un **venit ales** de contribuabil (nu poate fi mai mic decât nivelul minim de 12/24 salarii minime, dar poate fi ales mai mare) — o alegere diferită de venit față de ce a presupus calculul inițial duce automat la o sumă diferită.

## Ce face iConta.eu

La data acestui ghid, iConta.eu calculează CAS/CASS pentru o PFA în sistem real doar pe baza operațiunilor introduse și validate în aplicație, prin `core/rip_api.py` (funcția `fisa_d212`) — adică pentru activitatea evidențiată în acea instanță a aplicației. Aplicația nu are acces la veniturile din alte surse ale aceleiași persoane fizice (alte PFA-uri, drepturi de autor, contracte de activitate sportivă etc.) și nu cumulează automat, la nivel de persoană, toate veniturile relevante pentru plafonul de la art. 148 alin. (3) — de aceea, dacă un contribuabil are mai multe surse de venit, calculul din iConta.eu trebuie completat manual cu celelalte venituri, pentru a corespunde cu ce va afișa ANAF în SPV.

[iConta.eu](/)
