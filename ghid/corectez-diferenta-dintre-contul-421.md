---
title: "Cum corectez diferența dintre contul 421 și statul de salarii?"
description: "De ce brutul contabilizat pe contul 421 poate diferi legitim de baza de calcul a contribuțiilor din statul de salarii, și când o diferență chiar e o eroare de corectat."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum corectez diferența dintre contul 421 și statul de salarii?

Prima reacție când rulajul contului 421 „Personal — salarii datorate" nu se potrivește exact cu baza declarată în D112 e să presupui o eroare de contare și să cauți nota greșită. De multe ori însă diferența e legitimă: legea nu include în baza de calcul a contribuțiilor sociale tot ce intră, contabil, în remunerația brută a lunii.

## Temeiul legal

::: ghid-temei
„Nu se cuprind în baza lunară de calcul al contribuțiilor de asigurări sociale următoarele: [...] veniturile reprezentând cadouri în bani și/sau în natură, inclusiv tichete cadou, oferite salariaților [...]. În cazul cadourilor în bani și/sau în natură, inclusiv tichetele cadou, oferite de angajatori, veniturile nu sunt cuprinse în baza de calcul al contribuției în măsura în care valoarea acestora pentru fiecare persoană în parte, cu fiecare ocazie dintre cele de mai jos, nu depășește 300 lei."
— Codul fiscal (Legea 227/2015), art. 142 lit. b) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Cadourile sub pragul de 300 lei/eveniment sunt, prin lege, excluse din baza de calcul a contribuțiilor sociale, dar pot fi înregistrate contabil ca parte a costurilor cu personalul — o sursă legitimă de diferență între ce apare în baza declarată (D112) și ce apare în evidența contabilă.
- Indemnizațiile de concediu medical urmează o formulă de calcul proprie, prevăzută de OUG 158/2005 (medie a veniturilor din ultimele luni, procent în funcție de tipul certificatului), diferită de salariul contractual al lunii — deci baza de contribuții aferentă unei luni cu concediu medical nu coincide automat cu brutul contractual din acea lună.
- Legea nu prevede o „reconciliere automată" între contul 421 și baza declarată — verificarea rămâne o operațiune de analiză contabilă, nu una mecanică de egalizare a două cifre.

## Ce se greșește în practică

- Se presupune, din reflex, că orice diferență între 421 și statul de salarii e o eroare de introducere a datelor, fără să se verifice întâi dacă luna respectivă a avut cadouri, concedii medicale sau alte componente cu regim fiscal diferit.
- Se „ajustează" contul 421 manual ca să dea exact egal cu baza din D112, ceea ce falsifică evidența contabilă în loc să explice diferența reală.
- Se ignoră faptul că baza de contribuții raportată în D112 nu e sinonimă cu brutul contabil — sunt două noțiuni diferite prin construcție legală, nu doar prin rotunjire.

## Ce face iConta.eu

Funcționalitatea „Stat de plată" (F087) produce documentul lunar — calculul brut→net pentru fiecare salariat și fluturașul individual — dar nu face contabilizarea acestuia și nu compară contul 421 cu baza declarată. Contarea propriu-zisă a salariilor e o funcționalitate separată din aplicație, iar verificarea automată a declarației D112 față de conturile contabile există ca funcție distinctă, de „control încrucișat" — care compară D112 declarat cu rulajul conturilor de datorii pentru impozit și contribuții, dar exclude explicit contul 421 din verificare, cu următorul motiv consemnat direct în documentația funcționalității respective: „Brutul (contul 421) nu este verificat aici, pentru că baza de contribuții diferă legitim de brutul contabil (de ex. la concedii medicale)."

Așadar, pentru acest subiect exact — diferența dintre 421 și baza de calcul din statul de salarii — aplicația nu are (și, conform propriei sale documentații, nu-și propune) o funcție dedicată de „corectare automată". Diferența se analizează manual, pornind de la componentele lunii (cadouri, concedii medicale, alte facilități cu regim fiscal special), nu se elimină prin ajustarea contabilă a soldului.

[iConta.eu](/)
