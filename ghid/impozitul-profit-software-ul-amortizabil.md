---
title: Impozitul pe profit și software-ul amortizabil - cum tratez?
description: Cum se amortizează fiscal un software achiziționat sau dezvoltat, ce metode permite Codul fiscal și ce metodă aplică efectiv iConta.eu pentru imobilizările necorporale.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Impozitul pe profit și software-ul amortizabil - cum tratez?

Un program informatic (software) cumpărat sau dezvoltat pentru firmă nu e o cheltuială simplă —
e o imobilizare necorporală, cu regulă proprie de amortizare fiscală, diferită de cea a unui
mijloc fix corporal obișnuit.

## Temeiul legal

::: ghid-temei
Cheltuielile aferente achiziționării de brevete, drepturi de autor, licențe, mărci de comerț
sau fabrică, drepturi de explorare a resurselor naturale și alte imobilizări necorporale
recunoscute din punct de vedere contabil... se recuperează prin intermediul deducerilor de
amortizare liniară pe perioada contractului sau pe durata de utilizare, după caz. Cheltuielile
aferente achiziționării sau producerii programelor informatice se recuperează prin
intermediul deducerilor de amortizare liniară sau degresivă pe o perioadă de 3 ani. Pentru
brevetele de invenție se poate utiliza și metoda de amortizare degresivă sau accelerată.

— Codul fiscal (Legea 227/2015), art.28 alin.(9)
:::

Pentru software, legea permite explicit **oricare dintre metoda liniară sau degresivă**, pe o
durată fixă de **3 ani (36 de luni)**. Contul de imobilizare aferent este 208 (imobilizări
necorporale), cu amortizarea cumulată pe contul 2808, iar amortizarea începe, ca la orice
mijloc fix, din luna următoare punerii în funcțiune.

## Ce se greșește în practică

- Se amortizează software-ul pe o durată arbitrară aleasă de contabil, în loc de cei 3 ani ficși
  prevăzuți explicit de lege pentru programele informatice.
- Se tratează achiziția de software ca o cheltuială curentă, deductibilă integral, deși e o
  imobilizare necorporală care trebuie amortizată.
- Se presupune că orice imobilizare necorporală (licență, brevet, software) are aceeași durată și
  aceleași metode permise, deși legea le tratează diferit (licența ia durata din contract,
  cheltuielile de constituire au maximum 5 ani, software-ul are exact 3 ani).

## Ce face iConta.eu

Achiziția de software se înregistrează prin fluxul dedicat de imobilizări necorporale
(`achiziție-necorporală`), cu tipul "software": cont imobilizare 208, cont amortizare 2808,
durată **fixă de 36 de luni**, calculată automat — nu trebuie introdusă manual, spre deosebire
de licențe/brevete (unde durata vine obligatoriu din contract). Activul intră apoi în același
registru unic de mijloace fixe și trece prin același motor de calcul al amortizării ca oricare
alt activ.

**Limitare reală, de spus deschis**: deși legea (alin.9) permite explicit metoda degresivă
pentru software, pe fluxul de achiziție a imobilizărilor necorporale iConta.eu înregistrează
**întotdeauna** metoda ca "liniară", fără opțiune de alegere la introducere. Dacă firma dvs.
vrea să aplice metoda degresivă pentru un software, acest lucru nu e disponibil direct din
fluxul dedicat de achiziție necorporală — ar trebui gestionat separat/manual, în afara acestui
flux.

[iConta.eu](/)
