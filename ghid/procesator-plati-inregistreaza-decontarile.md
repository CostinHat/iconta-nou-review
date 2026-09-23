---
title: "Procesator de plăți: cum se înregistrează decontările"
description: Indiferent de procesatorul de plăți folosit (Stripe, Netopia sau altul), decontarea se înregistrează în doi pași — suma netă în contul bancar, comisionul ca cheltuială separată — identificați manual din extrasul de cont, până la implementarea unei mecanici de netare automată.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Procesator de plăți: cum se înregistrează decontările

O decontare de la un procesator de plăți (Stripe, Netopia sau oricare altul) nu e o simplă „încasare" — e o sumă netă, rezultată din brutul plătit de clienți minus comisionul reținut de procesator, adesea agregată pe mai multe tranzacții. Înregistrarea contabilă corectă separă întotdeauna aceste două componente.

## Temeiul legal

::: ghid-temei
„Sumele virate sau depuse la bănci ori prin mandat poștal, pe bază de documente prezentate entității și neapărute încă în extrasele de cont, se înregistrează distinct în contabilitate (contul 5125 «Sume în curs de decontare»)." — OMFP 1802/2014, Reglementările contabile, pct. 302 alin. (2)

„Cu ajutorul acestui cont se ține evidența cheltuielilor cu serviciile bancare și asimilate. În debitul contului 627 [...] se înregistrează: – valoarea serviciilor bancare și asimilate plătite (471, 512)." — OMFP 1802/2014, Reglementările contabile, funcțiunea contului 627 „Cheltuieli cu serviciile bancare și asimilate"
:::

Principiul general, valabil pentru orice procesator de plăți:

1. **Suma brută** (cea de pe factura emisă către client) e punctul de plecare al reconcilierii — nu suma din extras.
2. **Interval de decontare**: între momentul plății clientului și momentul virării efective în contul firmei, dacă se ține o evidență intermediară, suma se poate înregistra în **cont 5125 „Sume în curs de decontare"** — contul prevăzut explicit pentru sume prezentate prin documente, dar încă neapărute în extrasul de cont.
3. **La decontarea efectivă**, extrasul de cont arată suma netă (brut minus comisionul procesatorului), care intră în **cont 5121 „Conturi la bănci în lei"**.
4. **Comisionul** procesatorului se înregistrează separat, ca o cheltuială, în **cont 627 „Cheltuieli cu serviciile bancare și asimilate"** sau **cont 622 „Cheltuieli privind comisioanele și onorariile"** — OMFP 1802/2014 definește ambele conturi generic (servicii bancare, respectiv comisioane și onorarii), fără să prevadă explicit care e „singurul corect" pentru comisionul unui procesator de plăți online; alegerea între ele e o convenție contabilă internă a firmei.

O mecanică viitoare de „netare" automată (potrivirea directă a sumei brute cu suma netă + comisionul postat automat ca cheltuială, pornind de la un fișier de decontare al procesatorului) ar simplifica acest flux, dar la momentul actual funcționează exclusiv procedura manuală descrisă mai sus.

## Ce se greșește în practică

- Se înregistrează decontarea direct ca „încasare", pe suma netă, fără să se identifice separat comisionul reținut — rezultă solduri de clienți deschise, nereconciliate, exact în valoarea comisionului.
- Se așteaptă potrivirea automată, tranzacție cu tranzacție, între facturi și decontări — decontările procesatorilor sunt de regulă agregate pe perioadă, nu unu-la-unu cu fiecare factură.
- Se contabilizează comisionul „global", fără evidență separată pe fiecare decontare — face dificilă verificarea ulterioară a costurilor reale cu procesatorul de plăți, inclusiv pentru negocierea comisionului.

## Ce face iConta.eu

iConta.eu nu are, azi, o funcție de import și netare automată a decontărilor unui procesator de plăți — o astfel de mecanică (potrivirea sumei brute cu suma netă și postarea automată a comisionului ca cheltuială) este amânată, urmând a fi construită la semnal, când apare un client cu un fișier real de decontare. Legătura directă dintre aplicație și un procesator prin link de plată a fost, de asemenea, închisă (decizie din 06.09.2026: „nu se integrează niciun procesator — fluxul real e transfer bancar, confirmat din extras"). Decontările procesatorilor de plăți se înregistrează azi manual, pe baza extrasului de cont: sumă netă în 5121 (eventual prin 5125), comision separat în 627 sau 622.

[iConta.eu](/)
