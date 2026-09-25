---
title: "Evaluarea stocului pentru bilanț la 31 decembrie"
description: "Regula contabilă de evaluare a stocurilor la data bilanțului și cum preia iConta.eu ajustările de depreciere în F10."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Evaluarea stocului pentru bilanț la 31 decembrie

Stocul nu intră în bilanț la costul de achiziție „brut", fără verificare. La data bilanțului, regula contabilă cere confruntarea valorii contabile cu valoarea reală de recuperare a stocului — iar dacă valoarea contabilă e mai mare, diferența trebuie ajustată, nu ignorată.

## Temeiul legal

::: ghid-temei
„(1) Activele de natura stocurilor se evaluează la cost, mai puțin ajustările pentru depreciere constatate. Ajustări pentru depreciere se constată inclusiv pentru stocurile fără mișcare. În cazul în care valoarea contabilă a stocurilor este mai mare decât valoarea de inventar, valoarea stocurilor se diminuează până la valoarea realizabilă netă, prin constituirea unei ajustări pentru depreciere."
— OMFP 1802/2014, Reglementările contabile privind situațiile financiare anuale, pct. 88 (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

- Evaluarea se face în cadrul inventarierii obligatorii de la finalul exercițiului financiar, care cuprinde toate elementele de active, datorii și capitaluri proprii, nu doar stocurile (pct. 82).
- La stabilirea valorii de inventar se aplică principiul prudenței: se ține cont de toate ajustările de valoare datorate deprecierilor sau pierderilor de valoare, indiferent dacă rezultatul exercițiului e profit sau pierdere (pct. 84).
- Stocurile fără mișcare intră explicit sub obligația de ajustare — vechimea în stoc, fără vânzare, e ea însăși un indiciu de depreciere posibilă, nu doar deteriorarea fizică vizibilă.
- Ajustarea se constituie prin diminuarea valorii stocului până la **valoarea realizabilă netă** (prețul estimat de vânzare, minus costurile de finalizare și de vânzare) — nu printr-o reducere arbitrară.

## Ce se greșește în practică

- Se raportează stocul la valoarea contabilă brută, fără să se verifice dacă valoarea de inventar (realizabilă netă) e mai mică — mai ales la stocuri vechi, cu mișcare lentă sau deteriorate.
- Se confundă inventarierea fizică (numărarea cantităților) cu evaluarea la inventar — legea cere ambele: mai întâi se constată cantitativ ce există, apoi se evaluează la valoarea corectă de raportare.
- Se ignoră stocurile fără mișcare, considerând că lipsa deteriorării fizice exclude nevoia unei ajustări — regula le include explicit, indiferent de starea fizică.
- Se constituie ajustarea de depreciere fără să fie reflectată corect în bilanț, prin diminuarea rândului de stocuri — ajustarea contabilizată dar netransmisă corect în F10 lasă bilanțul cu o valoare a stocului mai mare decât cea reală.

## Ce face iConta.eu

Bilanțul generat de iConta (F10, formularul S1005) preia automat conturile de stoc (materii prime, materiale, produse finite, mărfuri etc.) și scade din ele soldul conturilor de ajustare pentru depreciere a stocurilor (391-398), exact cum cere structura oficială a formularului — rândul de stocuri din bilanț apare deja net de orice ajustare înregistrată în contabilitate.

Important de precizat: aplicația **nu calculează ea însăși ajustarea de depreciere** — nu compară valoarea contabilă a stocului cu o valoare realizabilă netă estimată și nu propune o sumă de ajustat. Constatarea deprecierii (stocuri fără mișcare, deteriorate sau cu valoare de piață scăzută) și înregistrarea notei contabile corespunzătoare (cheltuială cu ajustarea = cont de ajustare) rămân integral pe seama contabilului, în urma inventarierii anuale; iConta doar preia corect, în bilanț, ce a fost deja înregistrat.

[iConta.eu](/)
