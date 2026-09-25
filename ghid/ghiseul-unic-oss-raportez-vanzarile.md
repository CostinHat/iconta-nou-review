---
title: "Ghișeul unic OSS: cum raportez vânzările intra-UE"
description: "Regimul special OSS permite declararea și plata centralizată, din România, a TVA-ului datorat pentru vânzările la distanță și serviciile B2C către alte state membre UE."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ghișeul unic OSS: cum raportez vânzările intra-UE

Odată ce o firmă din România depășește pragul de 10.000 euro pe an pentru vânzări la distanță de bunuri și servicii electronice către persoane fizice din alte state membre UE, TVA-ul datorat devine cel al statului membru al clientului. În loc să se înregistreze separat în fiecare țară unde are clienți, firma poate opta pentru regimul special OSS (One Stop Shop) — „ghișeul unic" — și declară totul centralizat, din România.

## Temeiul legal

::: ghid-temei
„Prezentul regim special poate fi utilizat de către orice persoană impozabilă care are sediul activității economice în România sau, în cazul în care nu are sediul activității economice în Uniunea Europeană, dispune de un sediu fix în România. [...] Regimul special poate fi utilizat în următoarele cazuri: a) de către orice persoană impozabilă care efectuează vânzări intracomunitare de bunuri la distanță. [...] c) de către orice persoană impozabilă care prestează servicii către o persoană neimpozabilă, atunci când persoana impozabilă nu este stabilită în statul membru de consum."
— Cod fiscal (Legea 227/2015), art. 315 alin. (2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Mecanismul, pe scurt:

- Regimul special de la art. 315 (cunoscut ca „regimul UE" al OSS) acoperă atât vânzările intracomunitare de bunuri la distanță, cât și prestările de servicii B2C către persoane neimpozabile din alte state membre, atunci când prestatorul nu e stabilit în statul de consum.
- Firma se înregistrează o singură dată, în România (statul membru de înregistrare), pentru toate vânzările acoperite de regim, indiferent în câte state membre are clienți.
- Declarația OSS se depune trimestrial, iar TVA-ul colectat la cotele fiecărui stat membru de consum se plătește centralizat către organul fiscal român, care îl redistribuie statelor respective.
- Alegerea regimului OSS nu elimină obligația de a cunoaște cota de TVA aplicabilă în fiecare stat membru de consum — TVA-ul colectat pe fiecare factură trebuie calculat la cota țării clientului, nu la cea a României.
- Există și un regim distinct pentru persoanele impozabile nestabilite în UE care prestează servicii către persoane neimpozabile din UE (art. 314), cu reguli de înregistrare similare, dar aplicabil altei categorii de contribuabili.

## Ce se greșește în practică

- Se confundă opțiunea pentru OSS cu o scutire de TVA — OSS este doar un mecanism de declarare și plată centralizată, TVA-ul rămâne datorat integral, la cota țării de consum.
- Se emit facturi cu TVA românesc și după înregistrarea în OSS, din obișnuință, în loc de a aplica cota țării clientului.
- Se depune declarația OSS cu întârziere sau incomplet, considerând-o o formalitate secundară față de declarațiile naționale de TVA.
- Nu se păstrează dovezile privind localizarea clientului (adresă, țară a cardului, IP), cerute pentru a justifica TVA-ul aplicat pe fiecare stat membru de consum raportat prin OSS.

## Ce face iConta.eu

La verificarea codului sursă, iConta.eu are un modul dedicat (`d398.py`) care generează și validează declarația D398 — „Declarație specială de TVA pentru regimurile speciale UE/non-UE/import (OSS)" — acoperind atât regimul UE de la art. 315, cât și regimul non-UE (art. 314) și regimul de import/IOSS (art. 315^2). Declarația este însă **manuală**: aplicația nu ține evidența automată a operațiunilor OSS pe stat de consum și cotă străină din facturile emise, așa că toate sumele (TVA defalcat pe state membre, cotele aplicate) trebuie introduse de utilizator, nu sunt deduse automat din registrele contabile ale firmei. Înregistrarea inițială în regimul OSS rămâne, de asemenea, în afara aplicației.

[iConta.eu](/)
