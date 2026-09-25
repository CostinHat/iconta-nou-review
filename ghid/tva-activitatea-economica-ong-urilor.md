---
title: "TVA pentru activitatea economică a ONG-urilor"
description: "Veniturile fără scop patrimonial nu intră în sfera TVA, dar activitatea economică a unui ONG e supusă acelorași reguli de TVA ca la orice altă persoană impozabilă, inclusiv plafonul de scutire."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# TVA pentru activitatea economică a ONG-urilor

Scutirea de impozit pe profit de la art. 15 din Codul fiscal e un subiect complet separat de TVA. Un ONG poate fi scutit de impozit pe profit pentru veniturile sale fără scop patrimonial și, în același timp, să fie obligat să se înregistreze în scopuri de TVA pentru activitatea sa economică, dacă depășește plafonul legal.

## Temeiul legal

::: ghid-temei
„(1) Persoana impozabilă stabilită în România conform art. 266 alin. (2) lit. a), a cărei cifră de afaceri anuală, declarată sau realizată, nu depășește plafonul de 395.000 lei, poate aplica scutirea de taxă, denumită în continuare regim special de scutire, pentru operațiunile prevăzute la art. 268 alin. (1), cu excepția livrărilor intracomunitare de mijloace de transport noi, scutite conform art. 294 alin. (2) lit. b)."
— art. 310 alin. (1) din Legea 227/2015 (Codul fiscal), regimul special de scutire pentru întreprinderile mici (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Veniturile fără scop patrimonial (cotizații, donații, sponsorizări) **nu intră în sfera TVA**, pentru că nu reprezintă contrapartida unei livrări de bunuri sau prestări de servicii efectuate cu titlu oneros, în cadrul unei activități economice — nu sunt operațiuni impozabile, indiferent de regimul de TVA al organizației.
- Activitatea economică a unui ONG (vânzări de bunuri, prestări de servicii, chirii) intră însă în sfera TVA, ca la orice altă „persoană impozabilă stabilită în România" — forma juridică de organizație nonprofit nu produce, prin ea însăși, nicio scutire specială de TVA.
- Regimul special de scutire pentru întreprinderile mici se aplică și unui ONG cu activitate economică, în aceleași condiții: cifra de afaceri anuală (calculată doar din operațiunile economice relevante) sub plafonul de **395.000 lei**. Peste plafon, organizația trebuie să solicite înregistrarea în scopuri de TVA, la fel ca orice altă persoană impozabilă.

## Ce se greșește în practică

- Se presupune că un ONG „scutit de impozit pe profit" e automat scutit și de TVA pentru activitatea economică — sunt două impozite diferite, cu reguli și plafoane separate.
- Se include, la calculul cifrei de afaceri relevante pentru plafonul de TVA, valoarea cotizațiilor sau donațiilor — acestea nu sunt operațiuni în sfera TVA și nu intră în acest calcul.
- Se omite înregistrarea în scopuri de TVA după depășirea plafonului de 395.000 lei, considerând greșit că statutul de ONG amână sau anulează această obligație.

## Ce face iConta.eu

Funcționalitatea de contabilitate ONG din iConta.eu (`core/ong.py`) tratează exclusiv regimul de impozit pe profit de la art. 15 Cod fiscal — clasificarea veniturilor fără scop patrimonial pe grupa 73 și calculul plafonului de scutire pentru veniturile economice. **Nu conține nicio logică de TVA**: nu calculează plafonul de scutire de la art. 310, nu urmărește cifra de afaceri relevantă pentru TVA și nu se ocupă de înregistrarea în scopuri de TVA. Dacă ONG-ul desfășoară activitate economică supusă TVA, aceasta se gestionează prin modulele generale de TVA ale aplicației, independent de această funcționalitate dedicată contabilității ONG.

[iConta.eu](/)
