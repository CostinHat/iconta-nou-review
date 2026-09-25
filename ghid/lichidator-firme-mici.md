---
title: "Cine poate fi lichidator al unei firme mici"
description: "Cine numește lichidatorul unei societăți dizolvate, potrivit Legii 31/1990, și de ce nu poate fi ales liber de asociați dintre orice persoană disponibilă."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cine poate fi lichidator al unei firme mici

Lichidatorul unei societăți nu e o funcție pe care asociații o pot atribui oricui, chiar dacă firma e mică și lichidarea pare simplă. Legea rezervă calitatea de lichidator unei categorii profesionale reglementate separat, iar numirea trece printr-o procedură formală la registrul comerțului.

## Temeiul legal

::: ghid-temei
„După rămânerea definitivă a hotărârii judecătorești de dizolvare, Oficiul Național al Registrului Comerțului, prin registrator, la cererea societății, a oricărei persoane interesate sau din oficiu, numește, prin încheiere, un lichidator înscris în Tabloul practicienilor în insolvență. Remunerarea lichidatorului se face din averea societății dizolvate sau, în lipsă, din fondul de lichidare, constituit potrivit legii. Remunerația lichidatorului este în cuantum fix de 1.500 lei, decontul final al cheltuielilor efectuate de lichidator în legătură cu lichidarea societății urmând a se face, pentru situația în care nu există bunuri în averea societății dizolvate, de către Uniunea Națională a Practicienilor în Insolvență din România, la solicitarea lichidatorului."
— Legea 31/1990, art. 237 alin. (6) (sursă: anaf_surse/legea_31_1990_societatile.txt)
:::

Ce rezultă, concret, pentru o firmă mică aflată în dizolvare/lichidare:

- Lichidatorul trebuie să fie o persoană **înscrisă în Tabloul practicienilor în insolvență** — nu poate fi, așadar, un asociat, un administrator sau un contabil fără această calitate profesională reglementată.
- Numirea se face de **Oficiul Național al Registrului Comerțului, prin registrator**, printr-o încheiere — nu prin simpla decizie a asociaților, chiar dacă cererea de numire poate fi formulată de societate sau de orice persoană interesată. Registrul comerțului poate numi lichidatorul și din oficiu, dacă nimeni nu solicită numirea.
- Remunerația lichidatorului e stabilită **în cuantum fix**, plătită din averea societății dizolvate sau, în lipsa acesteia, din fondul de lichidare — nu e negociabilă liber între asociați și lichidator.
- Legea 31/1990 a fost modificată în 2025 (prin Legea 239/2025) inclusiv la acest capitol; pentru situația în care nicio persoană interesată nu formulează cerere de numire, procedura de numire din oficiu de către registrator rămâne aplicabilă, conform reglementării actualizate.

## Ce se greșește în practică

- Se numește lichidator un asociat sau administratorul firmei, din dorința de a simplifica și ieftini procesul — legea impune calitatea de practician în insolvență înscris în Tabloul aferent, indiferent de mărimea firmei.
- Se presupune că lichidarea unei firme mici, fără activitate sau active semnificative, poate ocoli formalitatea numirii unui lichidator prin registrul comerțului — procedura rămâne aceeași indiferent de dimensiunea sau complexitatea patrimoniului societății.
- Se negociază liber remunerația lichidatorului cu asociații, ignorând cuantumul fix stabilit de lege și mecanismul de decontare din averea societății sau din fondul de lichidare.

## Ce face iConta.eu

Modulul de lichidare al iConta.eu (`core/lichidare.py`) oferă funcții de calcul contabil pentru operațiunile de lichidare — nota contabilă la vânzarea unui activ în cadrul lichidării, partajul capitalului social, rezervelor și profiturilor între asociați. La data acestui ghid, iConta.eu **nu gestionează desemnarea sau înregistrarea lichidatorului** la Oficiul Național al Registrului Comerțului — această etapă, reglementată de Legea 31/1990, rămâne un demers administrativ separat, în afara aplicației, iar iConta.eu intervine abia la partea de calcul contabil al operațiunilor de lichidare deja decise.

[iConta.eu](/)
