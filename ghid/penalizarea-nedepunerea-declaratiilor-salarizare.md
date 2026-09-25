---
title: "Penalizarea pentru nedepunerea declarațiilor de salarizare"
description: "Amenda pentru nedepunerea la termen a D112 și riscul mult mai grav, separat, al reținerii fără virare a impozitelor și contribuțiilor salariale."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Penalizarea pentru nedepunerea declarațiilor de salarizare

D112 — declarația unică privind obligațiile de plată a contribuțiilor sociale, impozitului pe venit și evidența nominală a persoanelor asigurate — e supusă aceleiași reguli generale de sancționare ca orice declarație fiscală. Dar riscul real, pentru o firmă cu salariați, nu se oprește la simpla întârziere a declarației: legea tratează mult mai aspru situația în care banii reținuți de la salariați nu ajung efectiv la buget.

## Temeiul legal

::: ghid-temei
„(1) Constituie contravenții următoarele fapte [...]: b) neîndeplinirea de către contribuabil/plătitor la termen a obligațiilor de declarare prevăzute de lege, a bunurilor și veniturilor impozabile sau, după caz, a impozitelor, taxelor, contribuțiilor și a altor sume [...]; [...] o) nereținerea, potrivit legii, de către plătitorii obligațiilor fiscale, a sumelor reprezentând impozite și contribuții cu reținere la sursă; p) reținerea și nevărsarea în totalitate, de către plătitorii obligațiilor fiscale, a sumelor reprezentând impozite și contribuții cu reținere la sursă;
(2) [...] d) cu amendă de la 1.000 lei la 5.000 lei pentru persoanele juridice încadrate în categoria contribuabililor mijlocii și mari și cu amendă de la 500 lei la 1.000 lei, pentru celelalte persoane juridice [...], în cazul săvârșirii faptei prevăzute la alin. (1) lit. a), b) și i) - m); [...] f) cu amendă de la 4.000 lei la 6.000 lei [...] și cu amendă de la 1.000 lei la 1.500 lei [...] în cazul săvârșirii faptelor prevăzute la alin. (1) lit. o) și p), dacă obligațiile fiscale sustrase la plată sunt de până la 50.000 lei inclusiv; g) cu amendă de la 12.000 lei la 14.000 lei [...] și cu amendă de la 4.000 lei la 6.000 lei [...], dacă obligațiile fiscale sustrase la plată sunt cuprinse între 50.000 lei și 100.000 lei inclusiv; h) cu amendă de la 25.000 lei la 27.000 lei [...] și cu amendă de la 6.000 lei la 8.000 lei [...], dacă obligațiile fiscale sustrase la plată sunt mai mari de 100.000 lei."
— Legea 207/2015 (Codul de procedură fiscală), art. 336 alin. (1) lit. b), o), p) și alin. (2) lit. d), f), g), h) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Două niveluri de risc, distincte, pentru o firmă cu salariați:

- **Simpla nedepunere la termen a D112** (fapta de la lit. b) intră la sancțiunea „standard": 1.000-5.000 lei pentru contribuabili mijlocii/mari, 500-1.000 lei pentru restul persoanelor juridice și pentru persoanele fizice.
- **Reținerea fără virare a impozitului/contribuțiilor din salarii** (lit. o și p) e tratată mult mai grav, iar amenda crește proporțional cu suma sustrasă: 4.000-6.000 lei sub 50.000 lei sustrași, 12.000-14.000 lei între 50.000 și 100.000 lei, și 25.000-27.000 lei peste 100.000 lei (valori pentru contribuabili mijlocii/mari; mai mici pentru celelalte persoane).
- **Diferența practică**: nedepunerea declarației e o problemă administrativă; reținerea banilor din salariul angajaților fără virarea lor la buget e tratată de lege ca o faptă mai gravă, cu amenzi net superioare și cu prag de creștere legat direct de suma neplătită.
- **Cele două fapte pot coexista** — o firmă care nici nu depune D112, nici nu virează sumele reținute, cumulează riscul ambelor contravenții, evaluate separat.

## Ce se greșește în practică

- Se tratează întârzierea D112 ca pe o simplă formalitate administrativă, ignorând că, dacă în spatele ei stă și nevirarea sumelor reținute de la salariați, riscul financiar real e cel de la lit. o)/p), nu cel „standard" de la lit. b).
- Se presupune că amenda pentru reținere-fără-virare e fixă, când de fapt crește pe praguri (până la 50.000 lei, 50.000-100.000 lei, peste 100.000 lei) — o firmă trebuie să știe pe ce prag se încadrează suma efectiv nevirată.
- Se confundă nedepunerea declarației cu neplata sumei declarate — sunt fapte separate, sancționate potrivit unor articole și cuantumuri diferite, chiar dacă ambele apar frecvent împreună la o firmă cu probleme de lichiditate.

## Ce face iConta.eu

La data acestui ghid, iConta.eu generează D112 și urmărește termenul ei de depunere prin `core/control_fiscal_api.py` (`obligatii_datorate()`, cu callback-ul `d112_fapt`, verificat față de scadența calculată pentru fiecare lună). Aplicația nu calculează și nu afișează cuantumul amenzii pentru nedepunere și nu distinge, în avertismentele generate, între simpla întârziere a declarației și riscul mult mai grav al reținerii fără virare a sumelor din salarii — urmărirea scadenței arată doar dacă D112 e restantă, nu și consecința financiară potențială.

[iConta.eu](/)
