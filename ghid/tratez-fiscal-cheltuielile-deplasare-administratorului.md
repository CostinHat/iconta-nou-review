---
title: "Cum tratez fiscal cheltuielile de deplasare ale administratorului?"
description: "Regimul de neimpozabilitate plafonată aplicabil indemnizațiilor de deplasare ale administratorilor și directorilor cu contract de mandat, cu aceeași formulă ca la salariați."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum tratez fiscal cheltuielile de deplasare ale administratorului?

Un administrator sau un director cu contract de mandat nu are, de regulă, un contract individual de muncă — dar, pentru sumele primite pe perioada deplasării în interesul activității, legea îi tratează, fiscal, aproape identic cu un salariat obișnuit în delegare, doar cu bază de calcul diferită ca denumire.

## Temeiul legal

::: ghid-temei
„m) indemnizațiile și orice alte sume de aceeași natură, altele decât cele acordate pentru acoperirea cheltuielilor de transport și cazare primite pe perioada deplasării în altă localitate, în țară și în străinătate, în interesul desfășurării activității, [...] de către administratorii stabiliți potrivit actului constitutiv, contractului de administrare/mandat, de către directorii care își desfășoară activitatea în baza contractului de mandat potrivit legii, [...] pentru partea care depășește plafonul neimpozabil stabilit astfel: (i) în țară, 2,5 ori nivelul legal stabilit pentru indemnizație [...], în limita a 3 remunerații prevăzute în raportul juridic; ... (ii) în străinătate, 2,5 ori nivelul legal stabilit pentru diurnă [...], în limita a 3 remunerații prevăzute în raportul juridic. [...] Plafonul aferent valorii a 3 remunerații [...] se calculează distinct pentru fiecare lună [...]"
— Codul fiscal, art. 76 alin. (2) lit. m) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce e identic și ce diferă față de regimul salariaților:

- Formula plafonului e **matematic identică** cu cea de la lit. k) pentru salariați: minimul dintre 2,5× nivelul legal al indemnizației/diurnei și un al doilea prag legat de veniturile proprii ale persoanei, raportate la zilele lucrătoare din lună.
- Singura diferență e **terminologică**: baza de calcul a celui de-al doilea prag nu se numește „salariu de bază", ci **„remunerație prevăzută în raportul juridic"** — remunerația de administrator sau de director cu mandat, stabilită prin actul constitutiv sau contractul de mandat.
- Ca și la salariați, partea care depășește plafonul devine venit impozabil.
- Cheltuielile de transport și cazare rămân, ca și la salariați, în afara acestui calcul — se decontează separat, pe bază de documente justificative.

## Ce se greșește în practică

- Se presupune că administratorii/directorii cu mandat nu au deloc dreptul la o indemnizație de delegare neimpozabilă, pentru că nu au contract de muncă — legea le acordă explicit acest regim, la o literă separată (m), dar cu aceeași logică de plafon.
- Se folosește, din grabă, salariul de bază al unui angajat obișnuit ca bază de calcul pentru administrator, în loc de remunerația efectivă din contractul de mandat.
- Se confundă remunerația de administrator cu eventualele dividende sau alte venituri din activitatea de conducere — doar remunerația prevăzută explicit în raportul juridic contează pentru acest calcul.

## Ce face iConta.eu

Funcția de calcul a plafonului (`plafon_diurna`, din `core/deconturi.py`) este generică — primește ca parametru o bază de calcul numită, la nivel de cod, `salariu_baza`, indiferent dacă persoana pentru care se calculează plafonul este un salariat sau un administrator/director cu mandat. Codul nu are o ramură separată explicit dedicată „administratorului", dar formula fiind identică matematic cu cea de la lit. k), acoperă corect și acest caz — cu condiția ca operatorul să introducă la acest parametru remunerația de mandat a administratorului, nu un salariu de angajat.

Ca pentru toate celelalte calcule de plafon din acest modul, trebuie menționat: funcția rămâne accesibilă doar la nivel de API, fără un ecran dedicat în interfața iConta unde să fie introdusă remunerația administratorului și să fie afișat plafonul rezultat. Calculul corect al plafonului pentru un administrator rămâne, astăzi, un calcul pe care contabilul trebuie să-l facă manual, folosind formula de mai sus.

[iConta.eu](/)
