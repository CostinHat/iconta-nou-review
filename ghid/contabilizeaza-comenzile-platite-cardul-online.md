---
title: "Cum se contabilizează comenzile plătite cu cardul online?"
description: Indiferent de procesatorul folosit (Stripe, Netopia sau altul), o comandă plătită cu cardul online se contabilizează pe două componente — suma netă intrată în bancă și comisionul procesatorului — identificate manual din extrasul de cont, până când decontarea automată a acestor date devine o funcție a aplicației.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum se contabilizează comenzile plătite cu cardul online?

Un magazin online care acceptă plata cu cardul, prin orice procesator (Stripe, Netopia sau altul), nu primește în contul bancar suma exactă a comenzii, ci o sumă netă — brut minus comisionul procesatorului, adesea agregată pentru mai multe comenzi dintr-o singură decontare. Contabilizarea corectă separă cele două componente, indiferent de procesatorul folosit.

## Temeiul legal

::: ghid-temei
„Sumele virate sau depuse la bănci ori prin mandat poștal, pe bază de documente prezentate entității și neapărute încă în extrasele de cont, se înregistrează distinct în contabilitate (contul 5125 «Sume în curs de decontare»)." — OMFP 1802/2014, Reglementările contabile, pct. 302 alin. (2)

„Cu ajutorul acestui cont se ține evidența cheltuielilor cu serviciile bancare și asimilate. În debitul contului 627 [...] se înregistrează: – valoarea serviciilor bancare și asimilate plătite (471, 512)." — OMFP 1802/2014, Reglementările contabile, funcțiunea contului 627 „Cheltuieli cu serviciile bancare și asimilate"
:::

Principiul e același pentru orice procesator de plăți online:

1. Se emite factura pe valoarea comenzii (suma brută plătită de client).
2. Suma încasată de procesator, dar neapărută încă în extrasul bancar al firmei, poate fi evidențiată distinct în **cont 5125 „Sume în curs de decontare"** — contul prevăzut explicit pentru această situație.
3. La decontarea efectivă (virarea în contul firmei), extrasul arată suma netă, care intră în **cont 5121 „Conturi la bănci în lei"**.
4. Diferența dintre brut și net — comisionul procesatorului — se înregistrează ca o cheltuială, în **cont 627 „Cheltuieli cu serviciile bancare și asimilate"** sau **cont 622 „Cheltuieli privind comisioanele și onorariile"**, după politica contabilă a firmei (reglementările contabile definesc ambele conturi generic, fără să prevadă expres cazul comisionului unui procesator de plăți online).

Pentru un magazin cu volum de comenzi, decontările sunt de regulă agregate — o singură sumă în extras poate corespunde mai multor comenzi/facturi dintr-o perioadă. Reconcilierea corectă presupune potrivirea sumei nete cu totalul brut al facturilor din grup, plus comisionul aferent, nu potrivirea „factură cu factură" pe suma netă.

## Ce se greșește în practică

- Se contabilizează fiecare decontare ca fiind încasarea unei singure comenzi, deși reprezintă de fapt o sumă agregată — apar diferențe nereconciliate greu de urmărit ulterior.
- Se marchează comenzile încasate pe suma netă din extras, fără separarea comisionului — soldurile de clienți rămân deschise pentru diferența de comision, chiar dacă banii clientului au ajuns efectiv la firmă.
- Se așteaptă ca aplicația să facă automat netarea (potrivirea sumei brute cu suma netă și comisionul aferent) — la momentul actual, această mecanică nu e implementată; netarea automată a decontărilor procesatorilor de card e o funcționalitate amânată, nu una activă.

## Ce face iConta.eu

iConta.eu nu are azi o funcție dedicată de import și netare automată a decontărilor procesatorilor de card — o astfel de mecanică (potrivire pe suma brută + comision postat automat ca cheltuială) este amânată, se construiește la semnal, când apare primul client e-commerce cu un fișier real de decontare. Legătura directă dintre aplicație și procesator prin link de plată pe factură a fost, de asemenea, închisă (decizie din 06.09.2026: „nu se integrează niciun procesator — fluxul real e transfer bancar, confirmat din extras"). Contabilizarea comenzilor plătite cu cardul online se face azi manual, la reconcilierea cu extrasul de cont, cu suma netă în 5121 (eventual prin 5125) și comisionul separat, în 627 sau 622.

[iConta.eu](/)
