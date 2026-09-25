---
title: "Comisioane bancare la depunerea numerarului"
description: "Cum se clasifică în contabilitate comisioanele reținute de bancă la depunerea de numerar în cont."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Comisioane bancare la depunerea numerarului

Comisionul reținut de bancă atunci când o firmă depune numerar în cont nu e o cheltuială „specială" — e o cheltuială de exploatare obișnuită, din categoria serviciilor executate de terți, la fel ca orice alt comision bancar.

## Temeiul legal

::: ghid-temei
„Contabilitatea cheltuielilor se ține pe feluri de cheltuieli, după natura lor, astfel: a) cheltuieli de exploatare, care cuprind: [...] cheltuieli cu serviciile executate de terți, redevențe, locații de gestiune și chirii; prime de asigurare; studii și cercetări; cheltuieli cu alte servicii executate de terți (colaboratori); comisioane și onorarii; [...] cheltuieli poștale și taxe de telecomunicații, servicii bancare și altele."
— OMFP 1802/2014, pct. 450 alin. (1) lit. a) (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Ce rezultă concret pentru comisionul de depunere numerar:

- **Se încadrează la cheltuieli de exploatare** (nu financiare) — categoria „servicii bancare și altele" e listată explicit alături de cheltuielile poștale și de telecomunicații, în cadrul cheltuielilor cu serviciile executate de terți (pct. 450 alin. 1 lit. a).
- **Documentul justificativ** e extrasul de cont bancar, care înregistrează atât suma depusă, cât și comisionul reținut — ambele operațiuni apar distinct pe extras și trebuie reflectate distinct în contabilitate, nu compensate „net".
- **Deductibilitatea fiscală** urmează regulile generale ale cheltuielilor de exploatare legate de activitatea economică a firmei — comisionul bancar aferent unei operațiuni curente de trezorerie nu ridică, de regulă, probleme de deductibilitate.

## Ce se greșește în practică

- Se înregistrează în contabilitate doar suma netă ajunsă în cont (după deducerea comisionului), fără a evidenția separat cheltuiala cu comisionul bancar — pierzându-se astfel o cheltuială deductibilă reală.
- Se tratează comisionul de depunere numerar ca o cheltuială financiară, alături de dobânzi și diferențe de curs valutar, deși norma îl încadrează la cheltuielile de exploatare cu serviciile bancare.
- Se omite verificarea comisionului pe extrasul bancar la reconciliere, lăsând o diferență nejustificată între suma depusă la ghișeu și suma reflectată în soldul contabil.

## Ce face iConta.eu

La data acestui ghid, `core/banca.py` (`regula_cont()`, `detecteaza_tip()`), expus prin ruta `/tenants/{tenant_id}/banca/parse-extras` (`core/uc_tenants.py: banca_parse_extras()`), clasifică automat liniile din extrasul bancar după cuvinte-cheie din descriere — inclusiv „comision", „taxa adm", „speze" și „serviciu bancar", încadrate direct pe contul **627** „Cheltuieli cu serviciile bancare și asimilate". O linie de comision de depunere numerar, dacă descrierea din extras conține unul dintre aceste cuvinte, e deci recunoscută și contată automat, nu doar manual. Separat, `core/reconciliere.py` alocă liniile de extras care corespund unor facturi deschise ale partenerilor — comisionul, nefiind o factură, nu trece prin acest motor, ci prin clasificarea pe cuvinte-cheie de mai sus.

[iConta.eu](/)
