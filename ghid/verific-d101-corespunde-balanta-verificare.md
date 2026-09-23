---
title: "Cum verific dacă D101 corespunde cu balanța de verificare?"
description: Există o reconciliere reală între D101 și balanță, dar acoperă doar baza contabilă (veniturile și cheltuielile din clasele 6/7) — nu profitul impozabil, nu ajustările fiscale manuale și nu contul 441.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum verific dacă D101 corespunde cu balanța de verificare?

Da, există o verificare automată — dar cu o limită precisă de scop, care merită înțeleasă înainte să te bazezi pe ea integral.

## Temeiul legal

::: ghid-temei
„Balanța de verificare este documentul contabil utilizat pentru verificarea înregistrării corecte în contabilitate a operațiunilor efectuate și controlul concordanței dintre contabilitatea sintetică și cea analitică [...]" — OMFP nr. 2634/2015, Anexa 1 „Norme generale", pct. 52.
:::

## Ce acoperă reconcilierea

D101 pornește, pentru partea contabilă, de la patru valori agregate din balanță: venituri din exploatare, cheltuieli din exploatare, venituri financiare, cheltuieli financiare (împărțite pe clasele de conturi 7, respectiv 6). Există un recalcul **independent** al acestor patru valori, direct din notele validate ale anului, care nu reia codul generatorului declarației, ci le calculează separat și le compară cu ce a folosit generatorul. O divergență e blocantă și numește exact rândul și ambele valori, ca să fie clar unde a apărut diferența.

## Ce NU acoperă

**Profitul impozabil** (rezultatul după ajustările fiscale) **nu** e verificat de această reconciliere. Ajustările fiscale — deduceri, venituri neimpozabile, cheltuieli nedeductibile, pierderi reportate — sunt intrări manuale ale contabilului, iar formula care le combină în profitul impozabil e verificată separat, dar nu față de balanță.

**Valorile suprascrise manual** de contabil peste cele patru agregate contabile nu sunt acoperite de reconciliere — dacă introduci manual o valoare diferită de cea din balanță, verificarea nu o mai prinde.

**Contul 441/4411** (impozitul pe profit înregistrat) nu e comparat cu ce rezultă din D101 — vezi ghidul separat despre reconcilierea manuală a contului 441.

## Ce se greșește în practică

- Se presupune că „D101 corespunde cu balanța" verificat automat înseamnă că **tot** ce apare în declarație e corect — de fapt doar baza contabilă (veniturile/cheltuielile) e verificată, nu profitul impozabil final.
- Se suprascriu manual valorile P1/P2/P4/P5 fără să se realizeze că, în acel caz, reconcilierea automată nu se mai aplică asupra lor.
- Se citește o reconciliere „trecută" ca dovadă că nu mai trebuie verificat contul 441 — sunt verificări diferite, pentru scopuri diferite.

## Ce face iConta.eu

Recalculează independent baza contabilă a D101 (venituri/cheltuieli din exploatare și financiar) direct din notele validate, o compară cu ce folosește generatorul declarației, și blochează cu mesaj explicit orice divergență, numind rândul și ambele valori. Pentru profitul impozabil (ajustările fiscale manuale) și pentru contul 441, verificarea rămâne responsabilitatea contabilului — nu extindem reconcilierea peste o zonă unde ar presupune date pe care doar el le deține.

[iConta.eu](/)
