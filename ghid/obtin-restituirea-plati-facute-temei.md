---
title: "Cum obțin restituirea unei plăți făcute fără temei legal"
description: "Procedura de restituire, prevăzută de Codul de procedură fiscală, pentru sumele plătite sau încasate la buget fără să fi fost datorate."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum obțin restituirea unei plăți făcute fără temei legal

Se întâmplă: o sumă e virată către buget deși nu era datorată — o obligație fiscală calculată greșit, o dublă plată, o sumă încasată prin poprire peste ce era efectiv de recuperat. Codul de procedură fiscală tratează explicit dreptul contribuabilului la restituire în aceste situații, cu o singură condiție principală: cererea.

## Temeiul legal

::: ghid-temei
„(1) Se restituie, la cerere, contribuabilului/plătitorului orice sumă plătită sau încasată fără a fi datorată.
(2) În situația în care s-a făcut o plată fără a fi datorată, cel pentru care s-a făcut astfel plata are dreptul la restituirea sumei respective."
— Legea 207/2015 (Codul de procedură fiscală), art. 168 alin. (1)-(2) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Câteva reguli importante din același articol:

- Regula generală e cererea de restituire — dar există excepții de restituire **din oficiu**: diferențele din regularizarea anuală a impozitului pe venit al persoanelor fizice (în cel mult 60 de zile de la comunicarea deciziei de impunere) și sumele încasate prin poprire peste creanța pentru care s-a înființat poprirea (în cel mult 5 zile lucrătoare).
- Dacă suma de restituit e mai mică de 10 lei, rămâne în evidența fiscală pentru compensare cu datorii viitoare, cu excepția cazului în care contribuabilul cere expres restituirea în numerar.
- Dacă la data cererii contribuabilul are obligații fiscale restante, restituirea se face **numai după compensare** — suma de restituit se folosește întâi pentru stingerea datoriilor existente, iar diferența (dacă rămâne) se restituie efectiv.
- Restituirea sumelor reținute la sursă în cuantum mai mare decât cel legal datorat (de exemplu, impozit pe venit reținut greșit de un plătitor) urmează o procedură specială, prevăzută la art. 170 din același cod, cu termenul de prescripție a dreptului de a cere restituirea de la art. 219.

## Ce se greșește în practică

- Se așteaptă restituirea automată, fără cerere, pentru orice plată nedatorată — regula generală cere expres depunerea unei cereri; doar câteva situații punctuale se restituie din oficiu.
- Se ignoră compensarea obligatorie cu datoriile restante — dacă firma are alte obligații neplătite, suma de restituit se folosește întâi pentru acestea, iar contribuabilul primește efectiv doar diferența.
- Se confundă restituirea unei plăți nedatorate (art. 168) cu corectarea unui cod bugetar greșit pe un ordin de plată altfel corect ca sumă (art. 164) — sunt proceduri diferite, pentru situații diferite.
- Se lasă sub 10 lei „pierduți" în evidența fiscală fără să se ceară restituirea în numerar, deși legea permite explicit acest lucru la cererea contribuabilului.

## Ce face iConta.eu

Pentru cazul general al art. 168 (orice sumă plătită fără a fi datorată), iConta.eu nu automatizează depunerea cererii de restituire — nu am găsit în cod o funcție dedicată acestui proces general. Există însă, în cod, un modul dedicat exact procedurii speciale menționate mai sus, de la art. 170: declarația D110 (`core/d110.py`), „Declarație de regularizare/cerere de restituire privind impozitul pe venit reținut la sursă", care compară suma datorată cu suma reținută per obligație fiscală și generează cererea de restituire a diferenței. Codul modulului citează explicit CPF art. 168 și art. 170 ca temei. Pentru restul situațiilor de plată nedatorată, evidența corectă a obligațiilor fiscale calculate (declarații, scadențe) rămâne utilă pentru a identifica de la bun început dacă o plată a fost sau nu efectiv datorată.

[iConta.eu](/)
