---
title: "Plusul de numerar în casierie: cum se înregistrează"
description: "Tratamentul contabil al plusurilor constatate la inventarierea casieriei, potrivit normelor privind inventarierea elementelor de activ."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Plusul de numerar în casierie: cum se înregistrează

Casieria unei firme e un element de trezorerie supus inventarierii ca oricare alt activ — iar un plus constatat la numărarea efectivă a banilor urmează regula generală de evaluare și înregistrare a plusurilor de inventar.

## Temeiul legal

::: ghid-temei
„În situația constatării unor plusuri în gestiune, bunurile respective se evaluează potrivit reglementărilor contabile aplicabile."
— OMFP nr. 2.861/2009, pct. 40 alin. (1) (sursă: anaf_surse/omfp_2861_2009.txt)

„Persoanele prevăzute la art. 1 au obligația să efectueze inventarierea generală a elementelor de natura activelor, datoriilor și capitalurilor proprii deținute la începutul activității, cel puțin o dată în cursul exercițiului financiar [...]."
— Legea nr. 82/1991, art. 7 alin. (1) (sursă: anaf_surse/legea_82_1991_consolidat.txt)
:::

Ce rezultă pentru un plus de casă:

- Numerarul din casierie e un **element de activ** (element de trezorerie), supus obligației generale de inventariere anuală prevăzute de art. 7 din Legea contabilității — comisia de inventariere verifică explicit numerarul din casă, printre atribuțiile ei.
- Când suma constatată fizic în casă e mai mare decât soldul scriptic din registrul de casă, diferența e un **plus de inventar**, care se evaluează și se înregistrează „potrivit reglementărilor contabile aplicabile" — în practică, prin recunoașterea diferenței ca venit al firmei (nu ca o simplă corecție tehnică a soldului), pentru că nu există o justificare documentată a provenienței banilor.
- Comisia de inventariere solicită explicații scrise de la persoana responsabilă de gestiunea casieriei înainte de a propune modul de regularizare — plusul nu se înregistrează automat, fără parcurgerea acestei proceduri de constatare.
- Spre deosebire de lipsurile de casă (care pot angaja răspunderea patrimonială a gestionarului), plusurile nu au un regim „sancționator" — ele se regularizează prin recunoașterea sumei ca venit, întărind soldul contabil la nivelul celui faptic.

## Ce se greșește în practică

- Se „ajustează" pur și simplu soldul scriptic al registrului de casă pentru a-l face să coincidă cu banii numărați efectiv, fără o înregistrare contabilă explicită a plusului ca venit — regularizarea trebuie documentată, nu doar corectată tehnic.
- Se ignoră procedura de inventariere propriu-zisă (comisie, proces-verbal, explicații scrise) pentru un plus de casă mic, considerându-l neglijabil — obligația de inventariere din art. 7 nu face distincție de valoare.
- Se compensează un plus de casă cu o lipsă constatată în altă gestiune sau la altă dată, fără să existe riscul de confuzie între sorturi identice cerut de regulile de compensare — regula de compensare din OMFP 2.861/2009 e strict condiționată, nu generală.

## Ce face iConta.eu

Modulul de casierie din iConta.eu (`core/casa.py`) ține evidența soldului rulant al registrului de casă pe baza operațiunilor de încasare și plată introduse, dar aplicația nu are, la data acestui ghid, o funcție dedicată constatării și înregistrării automate a unui plus de inventar la numerar — regularizarea unui plus constatat la inventarierea fizică a casieriei se introduce manual, ca operațiune de venit, de către contabil.

[iConta.eu](/)
