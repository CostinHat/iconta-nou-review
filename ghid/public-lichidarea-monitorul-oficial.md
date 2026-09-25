---
title: "Cum public lichidarea în Monitorul Oficial"
description: "Numirea lichidatorilor și dizolvarea unei societăți produc efecte depline față de terți doar după publicarea în Monitorul Oficial, Partea a IV-a — un pas obligatoriu, nu unul opțional."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum public lichidarea în Monitorul Oficial

O firmă care intră în lichidare nu poate considera procedura opozabilă terților din chiar momentul deciziei interne — legea leagă acest efect de publicarea în Monitorul Oficial, atât pentru dizolvare, cât și pentru numirea lichidatorilor.

## Temeiul legal

::: ghid-temei
„Dizolvarea societății înainte de expirarea termenului fixat pentru durata sa are efect față de terți numai după trecerea unui termen de 30 de zile de la publicarea în Monitorul Oficial al României, Partea a IV-a.
[Art. 252 alin. (1) lit. b)] actul de numire a lichidatorilor, precum și orice act ulterior care ar aduce schimbări cu privire la persoana lor sau la puterile conferite trebuie depuse, prin grija lichidatorilor, la oficiul registrului comerțului, pentru a fi menționate în registrul comerțului. Acestea se publică în Monitorul Oficial al României, Partea a IV-a, ori, după caz, în Buletinul electronic al registrului comerțului."
— Legea nr. 31/1990 (legea societăților), art. 234 și art. 252 alin. (1) lit. b) (sursă: anaf_surse/legea_31_1990_societatile.txt)
:::

Ce presupune, practic, procedura de publicare:

- Publicarea nu e un pas administrativ formal fără consecințe — **efectul față de terți al dizolvării** anticipate a societății se produce abia la 30 de zile de la publicarea în Monitorul Oficial, Partea a IV-a. Până atunci, dizolvarea rămâne, față de terți, neopozabilă.
- Separat de dizolvare, actul de numire a lichidatorilor (și orice schimbare ulterioară a persoanei lor sau a puterilor conferite) se depune la oficiul registrului comerțului, pentru menționare, și se publică tot în Monitorul Oficial, Partea a IV-a (sau, după caz, în Buletinul electronic al registrului comerțului).
- Ambele publicări sunt în sarcina lichidatorilor sau a societății, prin depunerea documentelor la Registrul Comerțului — Monitorul Oficial nu publică direct la cererea societății, ci pe baza actelor înregistrate acolo.

## Ce se greșește în practică

- Se consideră dizolvarea opozabilă terților din chiar ziua hotărârii asociaților, ignorând termenul de 30 de zile care curge de la publicarea în Monitorul Oficial.
- Se omite publicarea separată a actului de numire a lichidatorilor, considerând suficientă publicarea hotărârii de dizolvare — sunt două acte distincte, cu obligații de publicare proprii.
- Se depune actul de numire a lichidatorilor la Registrul Comerțului, dar nu se urmărește confirmarea publicării efective în Monitorul Oficial sau în Buletinul electronic, lăsând procedura incompletă.

## Ce face iConta.eu

Modulul de lichidare/radiere societate din iConta.eu (F057, `core/lichidare.py`) este funcționalitate live, dar e un motor **pur**, limitat la două operațiuni: vânzarea activelor imobilizate rămase (`nota_vanzare_activ`) și partajul final (`partaj`). Încasarea creanțelor și plata datoriilor curente nu au o funcție dedicată în acest motor — se fac prin operațiunile obișnuite de încasare/plată din aplicație, ca înainte de deschiderea lichidării. La partaj, aplicația calculează impozitul pe câștigul asociaților persoane fizice (rezerve + profituri repartizate) cu cota fixă de **10%, impozit final**, conform Codului fiscal art. 97 alin. (5) — codul aplicației marchează explicit că acesta **nu este regimul dividendelor** (art. 97 alin. (7), cu cotă diferită), ci un regim distinct, specific câștigului din lichidare. Aplicația **nu se ocupă de partea juridic-procedurală** a lichidării — redactarea actului de numire a lichidatorilor, depunerea lui la Registrul Comerțului și publicarea efectivă în Monitorul Oficial rămân pași separați, în afara aplicației, pe care lichidatorii îi parcurg conform Legii 31/1990.

[iConta.eu](/)
