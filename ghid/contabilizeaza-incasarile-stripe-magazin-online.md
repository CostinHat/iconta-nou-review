---
title: "Cum se contabilizează încasările prin Stripe într-un magazin online?"
description: Pentru un magazin online cu volum de comenzi, decontările Stripe sunt de regulă agregate pe mai multe tranzacții — reconcilierea și contabilizarea corectă se fac pe grupul de facturi corespunzător, manual, pe baza extrasului de cont.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum se contabilizează încasările prin Stripe într-un magazin online?

Diferența față de o încasare izolată prin Stripe e volumul: un magazin online primește, de regulă, decontări agregate — o singură sumă în extrasul de cont corespunde mai multor comenzi plătite de clienți diferiți, într-o perioadă. Principiul de contabilizare rămâne același (sumă netă în bancă, comision ca cheltuială separată), dar reconcilierea se face pe grup, nu pe fiecare comandă izolat.

## Temeiul legal

::: ghid-temei
„Sumele virate sau depuse la bănci ori prin mandat poștal, pe bază de documente prezentate entității și neapărute încă în extrasele de cont, se înregistrează distinct în contabilitate (contul 5125 «Sume în curs de decontare»)." — OMFP 1802/2014, Reglementările contabile, pct. 302 alin. (2)

„Cu ajutorul acestui cont se ține evidența cheltuielilor cu serviciile bancare și asimilate. În debitul contului 627 [...] se înregistrează: – valoarea serviciilor bancare și asimilate plătite (471, 512)." — OMFP 1802/2014, Reglementările contabile, funcțiunea contului 627 „Cheltuieli cu serviciile bancare și asimilate"
:::

Pentru un magazin cu multe comenzi zilnice:

1. Fiecare comandă se facturează normal, la valoarea brută plătită de client.
2. Stripe agregă plățile dintr-o zi (sau dintr-un interval stabilit prin contract) și virează o singură sumă netă, după deducerea comisionului cumulat pentru toate tranzacțiile din grup.
3. Sursa care apare în extras nu poate fi potrivită, individual, cu o singură factură — trebuie identificat grupul de comenzi/facturi care corespunde acelei decontări, de regulă pe baza datei sau a raportului de decontare oferit de Stripe (dacă e disponibil în afara aplicației).
4. Suma netă intră în **cont 5121 „Conturi la bănci în lei"** (eventual, pentru intervalul dintre plată și decontare, prin **cont 5125 „Sume în curs de decontare"**), iar comisionul cumulat pe grup se înregistrează ca o cheltuială, în **cont 627 „Cheltuieli cu serviciile bancare și asimilate"** sau **cont 622 „Cheltuieli privind comisioanele și onorariile"**, după politica contabilă a firmei.

Fără o mecanică de import automat al raportului de decontare Stripe, identificarea grupului de comenzi corespunzător fiecărei tranșe rămâne o operațiune manuală, făcută pe baza documentelor puse la dispoziție de Stripe (extras din contul de comerciant, raport de decontare) coroborate cu extrasul bancar.

## Ce se greșește în practică

- Se încearcă potrivirea „factură cu factură" a fiecărei decontări Stripe, deși aceasta acoperă de regulă mai multe comenzi agregate — rezultă diferențe care par nereconciliate, deși sunt doar un efect al agregării.
- Se contabilizează suma netă din extras ca fiind egală cu totalul comenzilor din grup, fără să se separe comisionul cumulat — apar solduri deschise de clienți, nejustificate.
- Se presupune că aplicația importă și potrivește automat raportul de decontare Stripe cu facturile emise — la momentul actual, această funcție nu există; potrivirea rămâne manuală.

## Ce face iConta.eu

iConta.eu nu are, azi, o funcție de import automat al raportului de decontare Stripe și nici o integrare care să genereze linkuri de plată sau să confirme automat încasările — funcționalitatea de link de plată pe factură a fost închisă (decizie din 06.09.2026: „nu se integrează niciun procesator — fluxul real e transfer bancar, confirmat din extras"). Pentru un magazin online, contabilizarea decontărilor Stripe se face manual: identificarea grupului de comenzi corespunzător fiecărei tranșe, sumă netă în 5121 (eventual prin 5125) și comisionul cumulat în 627 sau 622.

[iConta.eu](/)
