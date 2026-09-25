---
title: "Cum declar în D010 operarea de achiziții intracomunitare"
description: "O firmă neplătitoare de TVA care face o achiziție intracomunitară peste plafon trebuie să solicite înregistrarea în scopuri de TVA prin D010, înainte de efectuarea achiziției."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum declar în D010 operarea de achiziții intracomunitare

O firmă care nu e plătitoare de TVA (neînregistrată conform art. 316) și care face o achiziție intracomunitară peste plafonul legal nu poate ignora TVA — trebuie să solicite înregistrare specială în scopuri de TVA, exclusiv pentru astfel de operațiuni, folosind formularul D010.

## Temeiul legal

::: ghid-temei
„Are obligația să solicite înregistrarea în scopuri de TVA, conform prezentului articol: a) persoana impozabilă care are sediul activității economice în România, [...] neînregistrate și care nu au obligația să se înregistreze conform art. 316 [...], care efectuează o achiziție intracomunitară taxabilă în România, înainte de efectuarea achiziției intracomunitare, dacă valoarea achiziției intracomunitare respective depășește plafonul pentru achiziții intracomunitare în anul calendaristic în care are loc achiziția intracomunitară."
— Legea nr. 227/2015 (Codul fiscal), art. 317 alin. (1) lit. a) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Obligația de înregistrare **precede** achiziția — cererea (D010) trebuie depusă **înainte de efectuarea achiziției intracomunitare** care depășește plafonul, nu după.
- Această înregistrare specială, conform art. 317, e diferită de înregistrarea generală în scopuri de TVA de la art. 316: firma rămâne, pentru restul operațiunilor interne, în același regim (de exemplu scutită de TVA, dacă e sub plafonul de la art. 310), dar capătă un cod valabil special pentru achizițiile intracomunitare.
- Codul de TVA obținut astfel se folosește față de furnizorul din UE, pentru ca acesta să nu mai factureze cu TVA din țara lui, urmând ca achizitorul din România să aplice regimul corespunzător (taxare inversă) pe achiziția intracomunitară.
- Aceeași logică (înregistrare specială prin acest tip de declarație, înainte de operațiune) se aplică și pentru firmele care primesc sau prestează servicii intracomunitare pentru care sunt obligate la plata taxei conform art. 307 alin. (2), potrivit lit. b) și c) ale aceluiași articol.

## Ce se greșește în practică

- Se efectuează achiziția intracomunitară peste plafon și abia apoi se solicită înregistrarea, deși legea cere depunerea cererii înainte de operațiune.
- Se confundă înregistrarea specială pentru achiziții intracomunitare (art. 317) cu înregistrarea generală în scopuri de TVA (art. 316), presupunând că firma devine automat plătitoare de TVA pentru toate operațiunile interne.
- Se ignoră plafonul anual pentru achiziții intracomunitare, presupunând că orice achiziție dintr-un stat membru UE necesită automat înregistrare, indiferent de valoare.

## Ce face iConta.eu

La data verificării codului, generarea automată a declarațiilor de înregistrare/mențiuni fiscale D010, D020 și D070 este **blocată la nivel de infrastructură**: potrivit notelor interne din `anaf_surse/d010_d020_d070_d700_status.md`, aceste formulare nu au validator XML public în canalul oficial ANAF (spre deosebire de D100…D710), fiind formulare vechi, în curs de înlocuire cu D700. Fără acest validator, iConta.eu nu construiește și nu publică XML pentru D010. Depunerea cererii de înregistrare pentru achiziții intracomunitare rămâne, la acest moment, un pas manual, direct pe portalul ANAF.

[iConta.eu](/)
