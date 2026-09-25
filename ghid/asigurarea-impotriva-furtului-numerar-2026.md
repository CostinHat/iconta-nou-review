---
title: "Asigurarea împotriva furtului de numerar 2026"
description: "Regimul fiscal al primelor de asigurare împotriva furtului de numerar din casierie și condițiile în care aceste cheltuieli sunt deductibile la calculul impozitului pe profit."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Asigurarea împotriva furtului de numerar 2026

Firmele care gestionează sume importante de numerar în casierie — retail, unități HoReCa, magazine cash and carry — încheie deseori polițe de asigurare împotriva furtului de numerar. Din punct de vedere fiscal, întrebarea nu e dacă o astfel de asigurare e permisă, ci dacă riscul acoperit are legătură cu activitatea economică a firmei — pentru că exact acest criteriu decide deductibilitatea primei.

## Temeiul legal

::: ghid-temei
„g) cheltuielile cu primele de asigurare care **nu privesc activele și riscurile asociate activității contribuabilului**, cu excepția celor care privesc bunurile reprezentând garanție bancară pentru creditele utilizate în desfășurarea activității pentru care este autorizat contribuabilul sau utilizate în cadrul unor contracte de închiriere sau de leasing, potrivit clauzelor contractuale;"
— Legea nr. 227/2015 (Codul fiscal), art. 25 alin. (4) lit. g) — cheltuieli cu deductibilitate limitată (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Norma este formulată „pe dos" — enumeră ce **nu** e deductibil — dar tocmai de aceea confirmă, per a contrario, regula generală: o primă de asigurare care privește un activ sau un risc asociat activității economice a firmei este deductibilă. Pentru asigurarea împotriva furtului de numerar:

- Numerarul din casieria unei firme este un activ direct legat de activitatea sa economică (încasări din vânzări, plăți curente) — riscul de furt al acestui numerar este, prin natura lui, un risc asociat activității, nu unul străin de ea.
- Excluderea de la deductibilitate din art. 25 alin. (4) lit. g) vizează situația opusă: prime de asigurare pentru bunuri sau riscuri fără legătură cu activitatea (de exemplu, bunuri personale ale asociaților, asigurate pe cheltuiala firmei).
- Deductibilitatea unei cheltuieli trebuie citită, în orice caz, împreună cu regulile generale de deducere — cheltuiala trebuie efectuată în scopul desfășurării activității economice și justificată cu documente.

## Ce se greșește în practică

- Se presupune, din prudență excesivă, că orice primă de asigurare e supusă unei limitări legale, fără a verifica dacă riscul asigurat are sau nu legătură cu activitatea — majoritatea polițelor „de activitate" (numerar, marfă, echipamente) nu intră sub incidența excluderii de la art. 25 alin. (4) lit. g).
- Se confundă asigurarea de bunuri/riscuri operaționale (numerar, stocuri) cu asigurările de persoane sau cu polițele fără nicio legătură cu activitatea firmei, care pot avea într-adevăr un regim de deductibilitate diferit.
- Nu se păstrează documentația care leagă polița de un activ/risc concret al firmei (de exemplu, valoarea medie a numerarului din casierie), documentație utilă în cazul unui control care pune la îndoială legătura cu activitatea.

## Ce face iConta.eu

Pentru acest subiect nu am identificat în cod un modul dedicat evidenței sau deductibilității primelor de asigurare (nu există în modulele verificate — de exemplu `core/d407.py`, care raportează polițele de asigurare de viață în cadrul schimbului automat de informații, o funcționalitate diferită, de raportare informativă, nu de calcul al deductibilității cheltuielilor cu asigurările). Încadrarea corectă a unei asigurări împotriva furtului de numerar rămâne, la acest moment, o verificare manuală a contabilului.

[iConta.eu](/)
