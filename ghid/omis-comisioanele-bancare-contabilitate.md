---
title: "Ce fac dacă am omis comisioanele bancare din contabilitate?"
description: "Cum se corectează contabil o cheltuială bancară omisă, conform reglementărilor OMFP 1802/2014 privind corectarea erorilor contabile."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce fac dacă am omis comisioanele bancare din contabilitate?

Comisioanele bancare omise dintr-o lună sau dintr-un exercițiu financiar anterior nu se „adaugă" pur și simplu la luna curentă — reglementările contabile fac o distincție clară între eroarea din exercițiul curent și cea din exerciții precedente, cu tratamente diferite.

## Temeiul legal

::: ghid-temei
„65. - (1) Erorile constatate în contabilitate se pot referi fie la exercițiul financiar curent, fie la exercițiile financiare precedente. (2) Corectarea erorilor se efectuează la data constatării lor. [...] 67. - (1) Corectarea erorilor aferente exercițiului financiar curent se efectuează pe seama contului de profit și pierdere. (2) Corectarea erorilor semnificative aferente exercițiilor financiare precedente se efectuează pe seama rezultatului reportat (contul 1174 «Rezultatul reportat provenit din corectarea erorilor contabile»). (3) Erorile nesemnificative aferente exercițiilor financiare precedente se corectează, de asemenea, pe seama rezultatului reportat. Totuși, potrivit politicilor contabile aprobate, erorile nesemnificative pot fi corectate pe seama contului de profit și pierdere."
— OMFP 1802/2014, pct. 65 și pct. 67 (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Practic, pentru comisioanele bancare omise:

- dacă omisiunea aparține **exercițiului financiar curent** (nu s-a închis încă anul), corectarea se face simplu, pe seama contului de profit și pierdere (contul 627 „Cheltuieli cu serviciile bancare și asimilate", pe baza extrasului de cont);
- dacă omisiunea aparține unui **exercițiu financiar anterior deja închis**, iar suma e semnificativă, corectarea se face pe seama contului 1174 „Rezultatul reportat provenit din corectarea erorilor contabile" — nu se rescriu situațiile financiare deja depuse ale anului respectiv (pct. 68: corectarea erorilor din exerciții precedente nu determină modificarea situațiilor financiare ale acelor exerciții);
- dacă suma e **nesemnificativă**, politica contabilă a firmei poate permite corectarea directă pe cheltuieli curente, chiar dacă eroarea aparține anului trecut — pragul de semnificație trebuie însă documentat în politicile contabile ale firmei;
- notele explicative la situațiile financiare trebuie să menționeze natura erorii și perioada afectată, dacă suma e semnificativă (pct. 68 alin. 3).

## Ce se greșește în practică

- Se înregistrează comisionul omis direct pe cheltuiala lunii curente, indiferent de vechimea lui — pentru sume semnificative din exerciții financiare deja închise, corectarea corectă trece prin rezultatul reportat (1174), nu prin contul de profit și pierdere curent.
- Se ignoră pragul de semnificație — fără o politică contabilă scrisă care să-l definească, orice eroare de exercițiu anterior tinde să fie tratată „la vedere", ceea ce poate distorsiona rezultatul fiscal al anului curent.
- Se uită să se refacă reconcilierea bancară pentru perioada respectivă, ceea ce lasă riscul ca aceeași omisiune (sau alta similară) să nu fie detectată la următorul control al extraselor.

## Ce face iConta.eu

iConta.eu importă extrasele bancare și recunoaște automat liniile de comision bancar din descrierea tranzacției (cuvinte-cheie precum „comision", „taxa adm", „speze", „serviciu bancar" — vezi `core/banca.py`), contabilizându-le direct pe contul 627. Acest mecanism reduce riscul de omisiune la importurile viitoare, dar nu corectează retroactiv comisioane deja omise dintr-un extras neimportat sau dintr-un exercițiu deja închis — corecția pentru acele sume rămâne o operațiune manuală a contabilului, conform regulilor de mai sus.

[iConta.eu](/)
