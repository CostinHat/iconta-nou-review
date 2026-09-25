---
title: "Ce metodă este mai potrivită pentru stocuri: FIFO sau CMP?"
description: "Ce spune legea despre alegerea între FIFO și CMP pentru evaluarea stocurilor, și de ce răspunsul depinde de politica contabilă a firmei, nu de o recomandare legală."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce metodă este mai potrivită pentru stocuri: FIFO sau CMP?

Întrebarea „care metodă e mai bună" apare frecvent la contabilii care organizează pentru prima dată evidența unui stoc, dar legea românească nu oferă un răspuns tranșant — le pune pe amândouă (plus LIFO) pe picior de egalitate, ca opțiuni de politică contabilă. Alegerea „potrivită" depinde de specificul afacerii, nu de o normă care să indice una ca superioară.

## Temeiul legal

::: ghid-temei
„96. - (1) Costul de achiziție sau costul de producție al stocurilor din aceeași categorie și al tuturor elementelor fungibile se calculează prin aplicarea uneia din următoarele metode: a) metoda costului mediu ponderat - CMP; ... b) metoda primul intrat-primul ieșit - FIFO; ... c) metoda ultimul intrat-primul ieșit - LIFO."
— OMFP 1802/2014, pct. 96 alin. (1) (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

- Legea prezintă cele trei metode ca alternative valabile, fără nicio ierarhie sau recomandare între ele — formularea „uneia din următoarele metode" nu privilegiază niciuna.
- Alegerea concretă ține de politica contabilă a entității, stabilită de regulă prin decizia internă a administratorului sau prin manualul de politici contabile al firmei.
- Factori practici care influențează alegerea (nu impuși de lege, ci de bun-simț contabil): natura mărfii (perisabilă sau nu), frecvența și volatilitatea prețurilor de achiziție, volumul de tranzacții și capacitatea sistemului informatic de a susține metoda aleasă.
- Nicio prevedere din pct. 96-98 nu obligă o firmă la o metodă anume în funcție de domeniul de activitate — decizia rămâne una internă.

## Ce se greșește în practică

- Se caută un răspuns „corect" universal, deși legea nu îl oferă — decizia trebuie luată în funcție de realitatea concretă a stocurilor firmei, nu copiată de la altă companie.
- Se schimbă metoda de evaluare fără să se documenteze motivul și fără să se respecte principiul permanenței politicilor contabile, care cere consecvență de la un exercițiu la altul.
- Se alege o metodă doar pentru că „așa face concurența", fără să se verifice dacă sistemul informatic folosit o susține efectiv.

## Ce face iConta.eu

Această întrebare este, în esență, una de recomandare contabilă generală, nu o instrucțiune despre o funcție din aplicație — iConta.eu **nu oferă FIFO ca opțiune** pentru evaluarea stocurilor. Pentru gestiunea cantitativ-valorică, aplicația implementează exclusiv metoda CMP (`core/stocuri_cv.py`); pentru comerțul cu amănuntul există separat metoda global-valorică (prețul cu amănuntul, cu adaos comercial), complet diferită de FIFO sau CMP. Prin urmare, un utilizator care se întreabă „ce metodă aleg în iConta" nu are de fapt de ales între FIFO și CMP în aplicație — singura opțiune reală pentru evidența pe articol este CMP.

[iConta.eu](/)
