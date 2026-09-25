---
title: "Cum se declară excepțiile pentru part-time în D112?"
description: "Cele cinci situații care scutesc un salariat part-time de baza minimă de contribuții și de ce, azi, marcarea formală a motivului exact rămâne o limită reală a interfeței."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se declară excepțiile pentru part-time în D112?

Nu orice salariat cu contract part-time și venit sub salariul minim e supus bazei minime de contribuții. Legea prevede cinci situații explicite de excepție, iar angajatorul trebuie să poată justifica, cu documente, care dintre ele se aplică — și, la nivelul declarației 112, să marcheze formal acest lucru.

## Temeiul legal

::: ghid-temei
„Prevederile alin. (5^6) nu se aplică în cazul persoanelor fizice aflate în una dintre următoarele situații: a) sunt elevi sau studenți, cu vârsta până la 26 de ani, aflați într-o formă de școlarizare; [...] b) sunt ucenici, potrivit legii, în vârstă de până la 18 ani; [...] c) sunt persoane cu dizabilități sau alte categorii de persoane cărora prin lege li se recunoaște posibilitatea de a lucra mai puțin de 8 ore pe zi; [...] d) au calitatea de pensionari pentru limită de vârstă în sistemul public de pensii [...]; [...] e) realizează în cursul aceleiași luni venituri din salarii sau asimilate salariilor în baza a două sau mai multe contracte individuale de muncă, iar baza lunară de calcul cumulată aferentă acestora este cel puțin egală cu salariul de bază minim brut pe țară."
— Legea 227/2015 (Codul fiscal), art. 146 alin. (5^7) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.html)
:::

- Sunt exact cinci categorii de excepție, nu o listă deschisă — un contabil nu poate scuti un salariat de baza minimă pe alt motiv decât unul dintre cele cinci.
- Pentru majoritatea situațiilor, legea cere documente justificative: „angajatorul solicită documente justificative persoanelor fizice aflate în situațiile prevăzute la alin. (5^7) lit. a), c) și d)" — Codul fiscal, art. 146 alin. (5^8). Pentru situația de la lit. e) (cumul de contracte), procedura de aplicare se stabilește separat, prin ordin al ministrului finanțelor.
- Excepția nu înlătură obligația de declarare — salariatul rămâne în declarație, doar că fără suprataxarea la nivelul bazei minime; formularul 112 cere marcarea formală a motivului excepției (un cod din nomenclator, 1–5), nu doar omiterea calculului suprataxării.

## Ce se greșește în practică

- Se scutește un salariat de baza minimă doar pe baza declarației lui verbale, fără documentul justificativ cerut de lege pentru categoriile a), c) și d).
- Se presupune că excepția „cumul de contracte" (lit. e) se aplică automat, fără verificarea că baza lunară cumulată pe toate contractele atinge efectiv salariul minim brut — dacă nu-l atinge, excepția nu se aplică, indiferent de numărul de contracte.
- Se bifează scutirea de contribuție minimă în softul de salarizare, dar nu se păstrează evidența motivului exact aplicat pentru fiecare salariat — la un control, lipsa acestei trasabilități e o vulnerabilitate reală.

## Ce face iConta.eu

iConta are un mecanism funcțional pentru scutirea de la suprataxarea bazei minime: din formularul de salariat se poate bifa „Scutit contribuție minimă", iar acest lucru oprește corect calculul suprataxării în statul de plată și în declarația 112 deopotrivă.

Există însă o limită reală, descoperită direct în cod la data acestui ghid: **structura de date a aplicației citește și poate emite motivul exact al excepției (codul 1–5 cerut de nomenclatorul ANAF), dar formularul de salariat din interfață nu are niciun câmp prin care acest motiv să poată fi introdus** — nici manual, nici prin importul din fișier. Practic, un contabil poate opri corect suprataxarea (calculul valoric iese bine), dar nu poate marca, azi, prin interfața normală a aplicației, care dintre cele cinci motive legale se aplică fiecărui salariat scutit — acel detaliu al declarației rămâne necompletabil din fluxul obișnuit de lucru. E o lacună reală, nu o funcție care există dar e ascunsă — merită cunoscută de orice contabil care se bazează pe iConta pentru acest aspect al D112.

[iConta.eu](/)
