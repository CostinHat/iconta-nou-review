---
title: "Cum se stabilește pro-rata provizorie la începutul anului?"
description: "Regula legală de stabilire a pro-rata provizorii de TVA la începutul fiecărui an fiscal, pentru persoanele impozabile cu regim mixt."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se stabilește pro-rata provizorie la începutul anului?

Pentru firmele cu regim mixt de TVA (care fac atât operațiuni cu drept de deducere, cât și operațiuni fără drept de deducere), taxa aferentă achizițiilor comune se deduce pe parcursul anului pe baza unei pro-rata **provizorii**, care se regularizează abia la final de an cu pro-rata definitivă. Regula de stabilire a pro-rata provizorii e simplă: de regulă e pro-rata definitivă a anului anterior, comunicată organului fiscal până la 25 ianuarie.

## Temeiul legal

::: ghid-temei
„(9) Pro rata aplicabilă provizoriu pentru un an este pro rata definitivă, prevăzută la alin. (8), determinată pentru anul precedent, sau pro rata estimată pe baza operațiunilor prevăzute a fi realizate în anul calendaristic curent, în cazul persoanelor impozabile pentru care ponderea operațiunilor cu drept de deducere în totalul operațiunilor se modifică în anul curent față de anul precedent. Persoanele impozabile trebuie să comunice organului fiscal competent, la începutul fiecărui an fiscal, cel mai târziu până la data de 25 ianuarie inclusiv, pro rata provizorie care va fi aplicată în anul respectiv, precum și modul de determinare a acesteia."
— Codul fiscal (Legea 227/2015), art. 300 alin. (9) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Regula de bază: pro-rata provizorie = pro-rata definitivă calculată pentru anul precedent (raportul dintre operațiunile cu drept de deducere și totalul operațiunilor, potrivit art. 300 alin. (6)-(8)).
- Excepția: dacă ponderea operațiunilor cu drept de deducere se schimbă semnificativ față de anul anterior, firma poate/trebuie să estimeze o pro-rata provizorie nouă, pe baza operațiunilor prevăzute pentru anul curent.
- Comunicarea către organul fiscal competent se face **cel mai târziu până la 25 ianuarie inclusiv**, cu precizarea și a modului de determinare a pro-rata.
- Pentru firmele care abia încep să aibă operațiuni fără drept de deducere, sau care nu erau încă înființate, legea prevede reguli speciale la art. 300 alin. (10), cu termene diferite de comunicare (până la primul decont de TVA aferent perioadei relevante).
- La final de an, pro-rata definitivă se calculează pe baza operațiunilor efectiv realizate, iar diferența față de taxa dedusă provizoriu se regularizează în decontul din luna decembrie (art. 300 alin. (8) și (13)).

## Ce se greșește în practică

- Se aplică automat pro-rata definitivă a anului trecut fără a verifica dacă structura operațiunilor s-a schimbat semnificativ — situație în care legea cere o estimare nouă, nu simpla preluare a cifrei vechi.
- Se omite comunicarea către organul fiscal până la 25 ianuarie, deși legea o cere explicit, separat de depunerea decontului de TVA.
- Se confundă pro-rata provizorie cu pro-rata definitivă și se aplică direct cifra de la final de an, fără regularizarea aferentă lunii decembrie.
- Se ignoră regulile speciale pentru firme nou-înființate sau pentru cele care încep pentru prima dată operațiuni fără drept de deducere în cursul anului — acestea au termene proprii de comunicare, diferite de 25 ianuarie.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu calculează automat pro-rata** (nici provizorie, nici definitivă). În generatorul declarației D300 există un câmp `pro_rata`, care poate fi introdus manual de contabil în profilul TVA al firmei — dacă lipsește, aplicația presupune 100% (drept de deducere integral), ceea ce e corect doar pentru firmele fără regim mixt. Determinarea propriu-zisă a pro-rata provizorii (pe baza cifrelor anului precedent sau a estimării) și comunicarea ei către ANAF până la 25 ianuarie rămân, în acest moment, în sarcina contabilului, în afara aplicației.

[iConta.eu](/)
