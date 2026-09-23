---
title: Care este diferența dintre amortizarea contabilă și amortizarea fiscală?
description: De ce amortizarea folosită la calculul impozitului pe profit e independentă de cea din contabilitate, ce metode diferă între cele două regimuri, și cum tratează iConta.eu acest calcul unic pe fiscal.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Care este diferența dintre amortizarea contabilă și amortizarea fiscală?

Sunt două calcule separate, care pot să difere: unul pentru situațiile financiare (contabil),
unul pentru calculul impozitului pe profit (fiscal). Nu sunt neapărat egale, și legea spune
explicit că nu trebuie să fie.

## Temeiul legal

::: ghid-temei
Pentru mijloacele fixe amortizabile, deducerile de amortizare se determină fără a lua în calcul
amortizarea contabilă. Câștigurile sau pierderile rezultate din vânzarea ori din scoaterea din
funcțiune a acestor mijloace fixe se calculează pe baza valorii fiscale a acestora, diminuată cu
amortizarea fiscală, cu excepția celor prevăzute la alin. (14).

— Codul fiscal (Legea 227/2015), art.28 alin.(17)
:::

::: ghid-temei
Entitățile amortizează imobilizările corporale utilizând una dintre următoarele metode de
amortizare: a) amortizarea liniară realizată prin includerea uniformă în cheltuielile de
exploatare a unor sume fixe, stabilite proporțional cu numărul de ani ai duratei de utilizare
economică a acestora; ... b) amortizarea degresivă, care constă în multiplicarea cotelor de
amortizare liniară cu un anumit coeficient, caz în care poate fi avută în vedere legislația în
vigoare; ... c) amortizarea accelerată, care constă în includerea, în primul an de funcționare,
în cheltuielile de exploatare a unei amortizări de până la 50% din valoarea de intrare a
imobilizării... ; ... d) amortizare calculată pe unitate de produs sau serviciu, atunci când
natura imobilizării justifică utilizarea unei asemenea metode de amortizare.

— OMFP 1802/2014, pct.240(1)
:::

Diferența cheie: **amortizarea fiscală (art.28 din Codul fiscal) se calculează complet
independent de cea contabilă (OMFP 1802/2014)**. Legea o spune explicit — deducerile de
amortizare pentru impozitul pe profit "se determină fără a lua în calcul amortizarea
contabilă". Practic, cele două pot diferi din mai multe motive:

- OMFP 1802 permite și **amortizarea pe unitate de produs sau serviciu** (metoda d), o metodă
  contabilă care nu are corespondent explicit în cele patru metode fiscale de la art.28;
- coeficienții de degresiv pot fi tratați diferit între cele două reglementări, dacă firma alege
  o politică contabilă proprie;
- la vânzare sau scoatere din funcțiune, rezultatul fiscal se calculează strict pe valoarea
  fiscală diminuată cu amortizarea fiscală, indiferent de ce arată amortizarea contabilă la acel
  moment.

Diferența dintre cele două amortizări, atunci când apare, generează un decalaj între rezultatul
contabil și rezultatul fiscal, care se reflectă în calculul impozitului pe profit prin elemente
similare/nesimilare veniturilor și cheltuielilor. Acest ghid nu intră în mecanica declarării
acestor diferențe (element separat de calcul fiscal, dincolo de sfera registrului de mijloace
fixe) — pentru asta, consultați regulile specifice de calcul al impozitului pe profit.

## Ce se greșește în practică

- Se presupune că amortizarea din balanța contabilă e automat și cea folosită la calculul
  impozitului pe profit — nu e cazul dacă metodele sau duratele diferă.
- Se aplică aceeași durată și metodă în ambele evidențe "ca să fie mai simplu", fără să se ia în
  calcul că fiscal unele metode (ex. accelerată) nu sunt permise pentru toate categoriile, în
  timp ce contabil ar putea fi altă politică.
- La vânzarea/casarea unui activ, se calculează rezultatul pe baza amortizării contabile, în loc
  de valoarea fiscală diminuată cu amortizarea fiscală, cum cere explicit legea.

## Ce face iConta.eu

Motorul unic de amortizare din registrul `Firma > Mijloace fixe` calculează **amortizarea
fiscală**, pe metoda reală a fiecărui activ (una dintre cele patru permise de art.28), folosind
consecvent aceleași valori în ecranul de registru, nota lunară de amortizare, D406/SAF-T, casare
și reevaluare. Aplicația nu ține un calcul contabil separat, în paralel, cu metoda "pe unitate
de produs" din OMFP 1802 pct.240(1) lit.d — dacă firma dvs. aplică o politică contabilă diferită
de cea fiscală (de exemplu tocmai metoda pe unitate de produs), acel calcul contabil trebuie
ținut separat, în afara acestui registru.

[iConta.eu](/)
