---
title: "Poate un magazin cu amănuntul să țină gestiune cantitativ-valorică?"
description: "Dreptul de opțiune între metoda cantitativ-valorică și metoda global-valorică (preț cu amănuntul) în comerțul cu amănuntul, conform OMFP 1802/2014."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Poate un magazin cu amănuntul să țină gestiune cantitativ-valorică?

Există ideea că un magazin cu amănuntul e obligat să țină evidența mărfurilor la preț de vânzare (metoda global-valorică), pentru că are prea multe articole pentru o fișă de magazie pe fiecare produs. Legea nu impune acest lucru — global-valorică e o opțiune, nu o obligație.

## Temeiul legal

::: ghid-temei
„289. - Contabilitatea stocurilor se ține cantitativ și valoric sau numai valoric prin folosirea inventarului permanent sau a inventarului intermitent. [...] 287. - (8) În comerțul cu amănuntul poate fi utilizată metoda prețului cu amănuntul, pentru a determina costul stocurilor de articole numeroase și cu mișcare rapidă, care au marje similare și pentru care nu este practic să se folosească altă metodă."
— OMFP 1802/2014, pct. 289 și pct. 287 alin. (8) (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Din formulare rezultă clar structura de opțiuni:

- Norma spune că metoda prețului cu amănuntul (global-valorică) **„poate fi utilizată"** — formulare de opțiune, nu de obligație — și doar pentru stocuri „numeroase și cu mișcare rapidă", cu marje similare, pentru care altă metodă „nu este practică".
- Regula generală de la pct. 289 e simetrică: contabilitatea stocurilor se ține **„cantitativ și valoric sau numai valoric"** — ambele variante sunt prevăzute explicit de normă, pentru orice tip de activitate, inclusiv comerț cu amănuntul.
- Un magazin cu amănuntul cu un sortiment restrâns sau cu sisteme de gestiune care permit urmărirea pe cantitate (case de marcat conectate la stoc, coduri de bare) poate opta pentru metoda cantitativ-valorică fără nicio problemă legală — decizia ține de politica contabilă a entității, documentată și aplicată cu consecvență.

## Ce se greșește în practică

- Se presupune că "amănuntul" înseamnă automat global-valorică — mulți contabili aplică metoda din obișnuință, fără să verifice dacă activitatea concretă (sortiment, volum) justifică opțiunea.
- Se schimbă metoda de la un exercițiu la altul fără motivare — norma cere consecvență în aplicarea metodei alese pentru elemente similare de stocuri, iar o schimbare cere prezentarea motivului și a efectelor în notele explicative.
- Se combină cele două metode pe aceeași gestiune, fără separare clară pe grupe de stocuri — norma permite metode diferite doar pentru stocuri cu natură sau utilizare diferită, nu arbitrar în cadrul aceleiași categorii.

## Ce face iConta.eu

La data acestui ghid, iConta.eu susține ambele mecanisme: `core/stocuri_cv.py` calculează evidența **cantitativ-valorică**, la cost mediu ponderat (CMP), recalculat după fiecare intrare (OMFP 1802/2014 pct. 96), iar `core/stocuri.py` (`nir_gv`, `coeficient_k`, `descarcare_gv`) susține evidența **global-valorică**, cu adaos comercial și coeficient de repartizare K. Alegerea metodei pentru fiecare gestiune rămâne o decizie a firmei, pe care aplicația o poate opera tehnic în oricare dintre cele două variante.

[iConta.eu](/)
