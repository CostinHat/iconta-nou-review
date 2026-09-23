---
title: "Cum se contabilizează încasările prin Netopia?"
description: Contabilizarea unei încasări prin Netopia separă suma netă intrată efectiv în bancă de comisionul reținut de procesator — o înregistrare manuală, pornind de la extrasul de cont, nu o funcție automată a aplicației.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum se contabilizează încasările prin Netopia?

Ca la orice procesator de card, Netopia reține un comision și virează în contul bancar al firmei doar suma netă. Contabil, cele două componente — suma netă și comisionul — trebuie evidențiate separat, iar factura emisă către client rămâne, ca document, la valoarea brută.

## Temeiul legal

::: ghid-temei
„Sumele virate sau depuse la bănci ori prin mandat poștal, pe bază de documente prezentate entității și neapărute încă în extrasele de cont, se înregistrează distinct în contabilitate (contul 5125 «Sume în curs de decontare»)." — OMFP 1802/2014, Reglementările contabile, pct. 302 alin. (2)

„Cu ajutorul acestui cont se ține evidența cheltuielilor reprezentând comisioanele datorate [...] comisioanele de intermediere [...]." — OMFP 1802/2014, Reglementările contabile, funcțiunea contului 622 „Cheltuieli privind comisioanele și onorariile"
:::

Pas cu pas, pentru o încasare Netopia:

1. Se identifică în extrasul de cont suma virată de Netopia — de regulă suma netă, agregată pe o perioadă (Netopia decontează în tranșe, nu tranzacție cu tranzacție).
2. Pentru intervalul dintre plata clientului și decontarea efectivă, dacă se ține o evidență intermediară, suma brută poate trece prin **cont 5125 „Sume în curs de decontare"**.
3. La decontarea efectivă, suma netă intră în **cont 5121 „Conturi la bănci în lei"**.
4. Comisionul reținut de Netopia se înregistrează ca o cheltuială separată, în **cont 622 „Cheltuieli privind comisioanele și onorariile"** sau, alternativ, **cont 627 „Cheltuieli cu serviciile bancare și asimilate"** — reglementările contabile definesc ambele conturi generic; care dintre ele se folosește pentru comisionul unui procesator de plăți online e o convenție internă a firmei, nu o regulă tranșată explicit de OMFP 1802/2014.

Reconcilierea corectă se face pe suma brută a facturii, nu pe suma netă din extras — altfel apare o diferență nereconciliată în soldul clientului, exact egală cu comisionul reținut.

## Ce se greșește în practică

- Se contabilizează direct suma netă din extras ca fiind toată încasarea facturii, fără separarea comisionului — soldul clientului rămâne deschis pentru diferență, deși banii au ajuns la firmă.
- Se tratează fiecare decontare Netopia ca pe o singură plată, deși de regulă acoperă mai multe tranzacții dintr-o perioadă — reconcilierea trebuie făcută pe grupul corespunzător de facturi, nu pe o singură factură.
- Se așteaptă ca înregistrarea contabilă (sumă netă + comision) să fie generată automat de aplicație, pe baza unei presupuse integrări cu Netopia — fără o sursă de date care să citească automat aceste decontări, operațiunea rămâne manuală.

## Ce face iConta.eu

iConta.eu nu are, azi, o integrare automată care să citească decontările Netopia — funcționalitatea de link de plată pe factură a fost închisă (decizie din 06.09.2026: „nu se integrează niciun procesator — fluxul real e transfer bancar, confirmat din extras"), iar ruta aferentă a fost scoasă din aplicație. Contabilizarea încasărilor prin Netopia se face manual: suma netă din extras se înregistrează în 5121 (eventual prin 5125, pentru intervalul de decontare), iar comisionul se înregistrează separat, în 622 sau 627, conform politicii contabile a firmei.

[iConta.eu](/)
