---
title: Ce faci dacă impozitul pe dividende a fost calculat cu o cotă greșită?
description: Cota de impozit pe dividende se aplică automat, pe data distribuirii (nu a plății sau a anului declarației) — de cele mai multe ori o cotă „ciudată" e de fapt corectă; dacă e totuși o eroare reală, D205 nu poate fi azi rectificată din aplicație.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Ce faci dacă impozitul pe dividende a fost calculat cu o cotă greșită?

Dacă vedeți în D205 un impozit pe dividende calculat cu o cotă care nu corespunde anului curent, primul reflex e să credeți că e o eroare. În multe cazuri însă cota e corectă — doar că nu se aplică după regula la care vă așteptați. Mai jos explicăm exact după ce dată se alege cota și ce puteți face dacă e totuși greșită.

## Temeiul legal

::: ghid-temei
„(7) Veniturile sub formă de dividende, inclusiv câştigul obţinut ca urmare a deţinerii de titluri de participare... se impozitează cu o cotă de 16% din suma acestora, impozitul fiind final. Obligaţia calculării şi reţinerii impozitului pe veniturile sub formă de dividende revine persoanelor juridice, odată cu plata dividendelor.../sumelor... de către acţionari/asociaţi/investitori." (Legea 141/2025, art.II pct.5, care modifică art.97 alin.(7) CF)

„prevederile art. II pct. 5... se aplică veniturilor din dividende distribuite începând cu data de 1 ianuarie 2026" (Legea 141/2025, art.VII alin.(1) lit.c)

„În cazul dividendelor distribuite în baza situaţiilor financiare interimare întocmite în cursul anului 2025/anului fiscal modificat care începe în anul 2025, cota de impozit pe dividende este de 10%, fără recalcularea impozitului pe dividendele respective, după regularizarea acestora pe baza situaţiilor financiare anuale aferente exerciţiului financiar 2025..., aprobate potrivit legii." (Legea 141/2025, art.VII alin.(2))
:::

## De ce cota „pare" greșită, dar de obicei nu e

Cota de impozit pe dividende s-a schimbat de mai multe ori în ultimii ani: 5% (de la 2016), 8% (de la 2023), 10% (de la 2025), 16% (de la 2026). Regula-cheie, care creează cele mai multe confuzii, este că cota aplicabilă unui dividend se stabilește după **data la care dividendul a fost distribuit** (data notei contabile de creditare a contului 457), nu după anul în care s-a făcut plata și nici după anul pentru care se depune declarația.

::: ghid-exemplu
Un dividend e distribuit (aprobat, înregistrat pe 457) în decembrie 2025 și plătit efectiv abia în ianuarie 2026. Deși plata și declararea cad în 2026, cota rămâne 10% — rata valabilă la data distribuirii din 2025 — și nu trece la 16%. Aceasta e exact regula specială din Legea 141/2025, art.VII alin.(2), pentru situațiile-limită de trecere de la un an la altul.
:::

Aceeași logică a funcționat și la trecerea 2024→2025 (8% pentru interimarele din 2024, chiar dacă regularizarea a avut loc mai târziu).

## Ce se greșește în practică

- Se compară cota afișată cu anul declarației (sau cu anul curent calendaristic), nu cu anul real al distribuirii dividendului.
- Se presupune că orice plată făcută după 1 ianuarie a unui an cu cotă nouă trebuie să folosească automat noua cotă.
- Nu se verifică data exactă a hotărârii/notei de distribuire (creditul 457) înainte de a raporta o cotă ca fiind „greșită".
- Se cere o rectificare din aplicație fără să se verifice întâi dacă impozitul e într-adevăr eronat sau doar aplică regula corectă pe altă dată decât cea așteptată.

## Ce face iConta.eu

Cota de impozit pe dividende este ținută într-un registru intern, period-aware (cu praguri istorice 2016/2023/2025/2026), și se aplică automat pe data mișcării de distribuire din contul 457, nu pe anul plății sau al declarației. Când o plată se leagă (prin potrivire cronologică, cea mai veche distribuire nestinsă întâi) de o distribuire dintr-un an anterior, impozitul e calculat cu rata valabilă la acea dată de distribuire — inclusiv pentru situațiile de graniță 2025→2026 și 2024→2025 prevăzute expres de lege. Dacă mișcarea de plată nu are nicio distribuire deschisă în registru cu care să se potrivească, aplicația calculează impozitul conservator, cu rata anului plății.

Dacă, după verificarea datei reale de distribuire, constatați că impozitul e totuși calculat greșit, rețineți că D205 nu are în acest moment un mecanism din aplicație pentru a emite o declarație rectificativă — subiect detaliat separat, în ghidul dedicat corectării impozitului declarat greșit.

[iConta.eu](/)
