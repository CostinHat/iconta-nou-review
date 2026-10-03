---
title: "Sumele de serviciu din raportul Z: ce sunt și cum apar în soldul de casă?"
description: "Sumele de serviciu sunt banii pentru rest dați casierului la începutul zilei. Nu sunt vânzări, apar distinct în raportul Z și se regăsesc în soldul contului de casă, inclusiv la sfârșitul zilei."
published: 2026-10-02
modified: 2026-10-02
poarta: v1
---

# Sumele de serviciu din raportul Z: ce sunt și cum apar în soldul de casă?

Sumele de serviciu sunt **banii puși la dispoziția casierului la începutul fiecărei zile de lucru**, ca să poată da rest clienților. Nu sunt încasări din vânzări și nu se emite bon fiscal pentru ele. Raportul Z al aparatelor de marcat noi le arată distinct. Legea spune expres că ele se regăsesc în soldul contului de casă și în soldul de la sfârșitul zilei de lucru.

Pentru contabil, sumele de serviciu explică diferența dintre numerarul din sertar și încasările în numerar din raportul Z. Dacă nu sunt declarate în aparat, banii de rest pot fi socotiți la control sumă nejustificată.

## Temeiul legal

::: ghid-temei
„Raportul fiscal de închidere zilnică emis de aparatul de marcat electronic fiscal definit la art. 3 alin. (2) trebuie să conțină pe lângă datele definite la alin. (6) și următoarele date: [...] numărul și valoarea reducerilor, anulărilor, sume de serviciu, precum și sumele rezultate pentru fiecare mijloc de plată utilizat. Sumele de serviciu reprezintă sumele de bani utilizate pentru plata restului către client, puse la dispoziția operatorului aparatului de marcat electronic fiscal la începutul fiecărei zile de lucru. Acestea se regăsesc în soldul contului de casă și, de asemenea, în soldul de la sfârșitul zilei de lucru."
— OUG 28/1999, art. 4 alin. (7) (sursă: anaf_surse/oug_28_1999.html)
:::

Ce rezultă:

- **Nu sunt venit.** Sunt numerarul firmei mutat din casierie în sertarul casei de marcat. Încasările din vânzări sunt cele defalcate pe mijloace de plată în același raport.
- **Apar în raportul Z separat de vânzări.** În structura XML a raportului de închidere zilnică aprobată prin OPANAF 146/2018 (anexa 2, secțiunea II.7) există două câmpuri distincte: sumele de serviciu declarate la începerea zilei de lucru (`sume_serv_in`) și cele declarate la sfârșitul ei (`sume_serv_out`).
- **Rămân în soldul contului de casă.** Sumele de serviciu nu scad soldul de casă al firmei. Banii sunt doar în alt loc, în sertar. La sfârșitul zilei, sertarul conține sumele de serviciu plus numerarul încasat.
- **Legătura cu documentele justificative.** OUG 28/1999 cere document pentru sumele introduse în unitatea de vânzare care nu provin din bonuri sau din registrul special (art. 4 alin. (12) lit. h)). Sumele de serviciu sunt declarate în aparat și apar în raportul Z. Prudent este să existe și un document pentru mutarea lor din casieria firmei, mai ales când casieria e ținută separat.

Cum se verifică numerarul la sfârșitul zilei:

> numerar în sertar = sume de serviciu de la începutul zilei + încasări în numerar din raportul Z

Dacă numerarul fizic diferă de rezultat, diferența trebuie explicată prin documente, de exemplu sume extrase pentru o depunere la bancă sau sume introduse cu dispoziție de încasare.

::: ghid-exemplu
La SC Exemplu SRL, casiera primește dimineața 200 lei pentru rest și îi declară în aparat ca sume de serviciu. Raportul Z de seară arată:

- sume de serviciu la începutul zilei: 200 lei;
- încasări în numerar: 3.450 lei;
- încasări cu cardul: 1.200 lei.

Numerarul care trebuie să fie în sertar: 200 + 3.450 = **3.650 lei**. Cei 1.200 lei încasați cu cardul nu sunt în sertar, ci ajung în contul bancar.

Casiera predă la casieria centrală 3.450 lei și păstrează 200 lei pentru a doua zi, declarați ca sume de serviciu la sfârșitul zilei. În contabilitate, vânzarea zilei se înregistrează pe încasările din raport: 3.450 lei numerar și 1.200 lei card, cu TVA colectată aferentă. Cei 200 lei nu generează venit. Ei rămân în soldul de casă al firmei.
:::

## Ce se greșește în practică

- Sumele de serviciu se înregistrează ca vânzări sau ca încasări de la clienți, ceea ce umflă veniturile.
- Banii de rest se pun în sertar fără să fie declarați în aparat. La control, diferența față de raportul Z apare ca sumă nejustificată.
- Soldul de casă din registrul de casă se micșorează cu sumele de serviciu, deși legea spune că ele se regăsesc în soldul contului de casă.
- La închiderea zilei se predau și sumele de serviciu, fără ca soldul de sfârșit de zi să fie declarat corespunzător.

## Ce face iConta.eu

La importul raportului Z (XML sau .p7b), iConta.eu preia încasările pe tipuri de plată și TVA pe cote. Nota propusă, în stare de ciornă, duce numerarul în 5311, cardul și celelalte plăți în 5125, iar TVA în 4427. Câmpurile cu sumele de serviciu din raport nu sunt preluate și nu generează înregistrări, pentru că nu sunt vânzări. Verificarea numerarului fizic față de raport și ținerea registrului de casă rămân operațiuni ale contabilului, iar registrul de casă din aplicație păstrează soldul zilnic.

[iConta.eu](/)
