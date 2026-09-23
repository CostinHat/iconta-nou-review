---
title: "Cum se înregistrează încasările prin Stripe?"
description: Stripe nu are azi nicio integrare automată în iConta.eu. Încasarea se identifică din extrasul de cont, pe suma netă virată de Stripe, iar comisionul reținut se înregistrează separat, ca o cheltuială cu serviciile bancare.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum se înregistrează încasările prin Stripe?

Stripe virează în contul bancar al firmei suma netă — încasarea brută de la client, minus comisionul reținut de Stripe. Fără o integrare automată care să citească aceste decontări, înregistrarea se face manual, pornind de la extrasul de cont: se identifică virarea Stripe, se reconstituie suma brută (cea de pe factura emisă) și comisionul, și se înregistrează amândouă distinct.

## Temeiul legal

::: ghid-temei
„Sumele virate sau depuse la bănci ori prin mandat poștal, pe bază de documente prezentate entității și neapărute încă în extrasele de cont, se înregistrează distinct în contabilitate (contul 5125 «Sume în curs de decontare»)." — OMFP 1802/2014, Reglementările contabile, pct. 302 alin. (2)

„Cu ajutorul acestui cont se ține evidența cheltuielilor cu serviciile bancare și asimilate. În debitul contului 627 [...] se înregistrează: – valoarea serviciilor bancare și asimilate plătite (471, 512)." — OMFP 1802/2014, Reglementările contabile, funcțiunea contului 627 „Cheltuieli cu serviciile bancare și asimilate"
:::

Fluxul contabil, pas cu pas:

1. **La momentul plății clientului** (dacă se dorește o evidență intermediară): suma brută încasată de Stripe, dar încă nedecontată în contul bancar al firmei, poate fi înregistrată în contul **5125 „Sume în curs de decontare"** — contul destinat explicit sumelor virate pe bază de documente, dar neapărute încă în extrasul de cont.
2. **La decontare** (când Stripe virează efectiv banii în cont, de regulă în tranșe, cu o anumită periodicitate): extrasul de cont bancar arată suma **netă** — brut minus comisionul Stripe. Suma netă se înregistrează în **cont 5121 „Conturi la bănci în lei"**.
3. **Comisionul reținut de Stripe** se înregistrează separat, ca o cheltuială: contul **627 „Cheltuieli cu serviciile bancare și asimilate"** (sau, în funcție de politica contabilă a firmei, contul **622 „Cheltuieli privind comisioanele și onorariile"** — OMFP 1802/2014 definește ambele conturi generic, fără să trateze explicit cazul „procesator de plăți online"; alegerea între cele două e o convenție internă, nu o regulă tranșată de reglementări pentru acest caz specific).

Punctul de plecare al reconcilierii rămâne factura emisă de firmă către client, pe suma brută — încasarea din Stripe trebuie potrivită cu factura pe brut, iar diferența (comisionul) explicată separat, nu „pierdută" în soldul contului bancar.

## Ce se greșește în practică

- Se înregistrează încasarea direct pe suma netă din extras, ca și cum ar fi valoarea integrală a facturii — factura rămâne, contabil, neîncasată pentru diferența de comision, ceea ce strică reconcilierea clienți-facturi.
- Se omite complet înregistrarea comisionului ca o cheltuială distinctă, tratând suma netă drept „toată încasarea" — comisionul Stripe e o cheltuială reală a firmei și trebuie evidențiată, inclusiv pentru deductibilitate.
- Se așteaptă ca aplicația să marcheze automat factura ca încasată în momentul plății online — fără o sursă care să scrie acest lucru automat, factura rămâne neîncasată contabil până la reconcilierea manuală cu extrasul.

## Ce face iConta.eu

iConta.eu nu are, azi, o integrare automată cu Stripe — funcționalitatea de link de plată pe factură a fost închisă (decizie din 06.09.2026: „nu se integrează niciun procesator — fluxul real e transfer bancar, confirmat din extras"), iar butonul și ruta aferente au fost scoase din aplicație. Încasările prin Stripe se înregistrează manual, pe baza extrasului de cont, folosind conturile 5125/5121 pentru sumă și 627 sau 622 pentru comision, exact ca orice altă reconciliere bancară. Marcarea facturii ca încasată se face tot manual, la reconciliere — aplicația nu face azi această corelare automat.

[iConta.eu](/)
