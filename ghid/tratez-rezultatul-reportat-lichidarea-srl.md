---
title: Cum tratez rezultatul reportat la lichidarea SRL-ului?
description: Rezultatul reportat poate fi profit sau pierdere — un sold creditor se distribuie la partaj ca și câștig impozabil, unul debitor trebuie acoperit înainte, din profit, rezerve, prime de capital sau capital social.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum tratez rezultatul reportat la lichidarea SRL-ului?

Contul de rezultat reportat poate sta, la data intrării în lichidare, în oricare din două stări opuse — sold creditor (profit din anii anteriori, neredistribuit) sau sold debitor (pierdere neacoperită) — iar tratamentul practic depinde exact de care dintre ele se aplică situației tale.

## Temeiul legal

::: ghid-temei
„Cu ajutorul acestui cont se ține evidența rezultatului sau părții din rezultatul exercițiului precedent nerepartizat de către adunarea generală a acționarilor/asociaților, respectiv a pierderii neacoperite [...]. Contul 117 «Rezultatul reportat» este un cont bifuncțional."
— OMFP 1802/2014, funcțiunea contului 117
:::

::: ghid-temei
„Pierderea contabilă reportată se acoperă din profitul exercițiului financiar curent [...], din rezerve, prime de capital și capital social, potrivit hotărârii adunării generale [...], cu respectarea prevederilor legale."
— OMFP 1802/2014, pct. 423 alin. (1)
:::

Dacă rezultatul reportat e sold creditor (profit nerepartizat din anii anteriori), el se tratează exact ca profitul curent rămas la lichidare: intră în câștigul impozabil distribuit asociaților prin partaj, nu în capitalul neimpozabil. Dacă e sold debitor (pierdere neacoperită), regula de acoperire e cea de la pct. 423 alin. (1): întâi din profitul exercițiului curent, apoi din rezerve, prime de capital și, în ultimă instanță, din capitalul social — fiecare pas cu aprobarea adunării generale.

Ce nu tranșează explicit sursele verificate e situația în care, la finalul lichidării, toate aceste surse au fost epuizate și pierderea rămâne parțial neacoperită. Nu există, în textul verificat, o sursă suplimentară de acoperire dincolo de cele patru enumerate — practic, într-o asemenea situație, asociații nu mai au din ce recupera pierderea prin mecanismele descrise, iar ea rămâne, de fapt, suportată prin absența oricărei sume de distribuit la partaj, nu printr-o notă contabilă separată. E o interpretare rezonabilă din structura textului, nu un citat explicit — dacă firma ta are o pierdere semnificativă rămasă neacoperită la lichidare, discută tratamentul ei cu un expert contabil sau consultant fiscal înainte de a finaliza bilanțul.

## Ce se greșește în practică

- Se tratează rezultatul reportat creditor (profit) ca parte a capitalului neimpozabil la partaj — rămâne un câștig impozabil, la fel ca profitul curent.
- Se sare peste ordinea de acoperire de la pct. 423 pentru un rezultat reportat debitor — de exemplu, se reduce capitalul social înainte de a epuiza rezervele și primele de capital, fără aprobarea corespunzătoare a adunării generale pentru fiecare pas.
- Se presupune că o pierdere rămasă neacoperită la radiere „dispare" automat, fără nicio consecință pentru asociați — de fapt, ea reduce direct suma pe care aceștia o mai pot primi la partaj.

## Ce face iConta.eu

Motorul de calcul al partajului de lichidare din aplicație e construit pentru cazul unui câștig net de distribuit către asociați (capital social, rezerve și profituri pozitive) și respinge explicit valori negative introduse pentru rezerve sau profituri. Dacă rezultatul reportat al firmei tale e sold debitor (pierdere neacoperită) la intrarea în lichidare, aplicația nu oferă un calcul automat pentru acest caz — tratează bilanțul de lichidare și repartizarea între asociați împreună cu un expert contabil, în afara calculului automat al aplicației. Dacă rezultatul reportat e sold creditor (profit), el intră în câmpul „profituri" al operațiunii „Partaj către asociați", calculat cu aceeași cotă de impozit folosită pentru dividendele obișnuite.

[iConta.eu](/)
