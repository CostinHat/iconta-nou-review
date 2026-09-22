---
title: Calendar fiscal 2026: ce termene privesc încasările și plățile unui PFA?
description: Registrul-jurnal de încasări și plăți se totalizează lunar, documentele se arhivează 10 ani, plafonul de numerar zilnic este 50.000 lei/tranzacție, iar Declarația Unică (D212) pentru veniturile anului se depune până la 25 mai anul următor.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Calendar fiscal 2026: ce termene privesc încasările și plățile unui PFA?

Dincolo de termenele de plată a impozitelor și contribuțiilor, un PFA în sistem real are și o serie de obligații legate direct de modul în care ține Registrul-jurnal de încasări și plăți — termene de totalizare, de arhivare și limite pentru operațiunile în numerar.

## Temeiul legal

::: ghid-temei
OMFP 170/2015, Cap. V, Secțiunea a 2-a: "Sumele înregistrate în Registrul-jurnal de încasări şi plăți se totalizează lunar."

OMFP 170/2015, Cap. IV, pct. 2: "Termenul de păstrare a Registrului-jurnal de încasări şi plăți (cod 14-1-1/b) şi a Registrului-inventar (cod 14-1-2/b) este de 10 ani."

Legea 70/2015 art.3: "incasarile/platile in numerar ... se pot efectua in limita unui plafon zilnic de 50.000 lei/tranzactie."

Codul fiscal, art. 122 alin. (3): "Declarația unică privind impozitul pe venit și contribuțiile sociale datorate de persoanele fizice se completează și se depune la organul fiscal competent, pentru fiecare an fiscal, până la data de 25 mai inclusiv a anului următor celui de realizare a veniturilor."
:::

## Cele patru repere ale anului

1. **Totalizare lunară** — sumele din Registrul-jurnal de încasări și plăți se închid la finalul fiecărei luni; nu e o recomandare, e o cerință explicită a OMFP 170/2015.
2. **Plafonul de numerar** — orice încasare sau plată în numerar este limitată la 50.000 lei pe tranzacție, în fiecare zi a anului.
3. **Depunerea D212** — venitul net calculat pe baza operațiunilor validate în Registrul-jurnal al anului 2026 se declară prin Declarația Unică depusă până la 25 mai 2027.
4. **Arhivarea** — fiecare registru și fiecare document justificativ rămân disponibile pentru control timp de 10 ani de la data completării, nu doar pe durata termenului de prescripție fiscală generală.

::: ghid-exemplu
Un PFA validează, în decembrie 2026, toate operațiunile din anul fiscal 2026. Registrul-jurnal e totalizat lunar de-a lungul anului; pe baza sumelor validate, fișa de calcul D212 pentru venitul anului 2026 se generează și se depune cel târziu pe 25 mai 2027. Documentele (registre, extrase, facturi) se păstrează până cel puțin în 2036.
:::

## Ce se greșește în practică

- Se totalizează registrul o singură dată, la final de an, în loc de lunar, cum cere explicit OMFP 170/2015.
- Se acceptă o încasare/plată în numerar peste plafonul zilnic de 50.000 lei pe tranzacție, cel mai adesea prin fragmentarea greșită a unei singure operațiuni economice în mai multe "tranzacții" artificiale.
- Se confundă termenul de depunere a D212 (25 mai anul următor) cu termenul de plată al obligațiilor fiscale, care poate diferi.
- Se arhivează documentele doar 5 ani, prin analogie cu alte obligații fiscale, în loc de cei 10 ani ceruți explicit pentru Registrul-jurnal și Registrul-inventar.
- Se validează operațiuni la începutul anului următor fără să se mai verifice dacă acestea corespund exercițiului fiscal corect.

## Ce face iConta.eu

Funcția `lista(conn, schema, an, luna=None, status=None)` din `core/rip_api.py` permite citirea operațiunilor filtrate pe lună, susținând direct totalizarea lunară cerută de OMFP 170/2015, cu calculul `total_incasari`, `total_plati` și `sold`. Fișa de calcul D212 (`fisa_d212(conn, schema, an, optiune_cas, optiune_cass)`) folosește exclusiv operațiunile cu status `validata` din anul respectiv și refuză să calculeze pentru anii ale căror plafoane fiscale nu au fost verificate la sursă — `_e.ANI_VERIFICATI = (2025, 2026)` — un mecanism explicit de siguranță împotriva calculelor pe bază de plafoane neconfirmate legal. Doar operațiunile trecute din `ciorna` în `validata` (prin funcția `valideaza`) intră în calculul fiscal final; o operațiune validată devine definitivă în registru și nu mai poate fi ștearsă, coerent cu logica arhivării pe termen lung.

[iConta.eu](/)
