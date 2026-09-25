---
title: "D112 pentru firmele cu un singur salariat: cum se depune"
description: "Cum se aplică regula depunerii trimestriale a D112 pentru angajatorii mici, cu până la 3 salariați, potrivit Codului fiscal, și de ce nu e vorba de o declarație diferită."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# D112 pentru firmele cu un singur salariat: cum se depune

O firmă cu un singur salariat nu depune o versiune simplificată a D112, ci aceeași declarație — doar la un ritm diferit. Codul fiscal oferă angajatorilor mici opțiunea depunerii trimestriale, în loc de lunară, dar cu o precizare tehnică importantă despre cum arată, concret, acea depunere trimestrială.

## Temeiul legal

::: ghid-temei
„Prin excepție de la prevederile alin. (1), impozitul aferent veniturilor fiecărei luni, calculat și reținut la data efectuării plății acestor venituri, se plătește, până la data de 25 inclusiv a lunii următoare trimestrului pentru care se datorează, de către următorii plătitori de venituri din salarii și venituri asimilate salariilor: [...] b) persoanele juridice plătitoare de impozit pe profit care, în anul anterior, au înregistrat venituri totale de până la 100.000 euro și au avut un număr mediu de până la 3 salariați exclusiv; c) persoanele juridice plătitoare de impozit pe veniturile microîntreprinderilor care, în anul anterior, au avut un număr mediu de până la 3 salariați exclusiv [...]"
— Legea 227/2015, art. 80 alin. (2) lit. b) și c) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„Prin excepție de la prevederile alin. (1), plătitorii de venituri din salarii și asimilate salariilor prevăzuți la art. 80 alin. (2), în calitate de angajatori sau de persoane asimilate angajatorului, depun trimestrial Declarația privind obligațiile de plată a contribuțiilor sociale, impozitului pe venit și evidența nominală a persoanelor asigurate aferentă fiecărei luni a trimestrului, până la data de 25 inclusiv a lunii următoare trimestrului.
(5) Depunerea trimestrială a declarației prevăzute la alin. (1) constă în completarea și depunerea a câte unei declarații pentru fiecare lună din trimestru."
— Legea 227/2015, art. 147 alin. (4) și (5) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce rezultă concret pentru un angajator cu un singur salariat:

- Condiția de eligibilitate pentru depunerea trimestrială e **numărul mediu de până la 3 salariați** din anul anterior (exclusiv), plus, pentru plătitorii de impozit pe profit, un plafon de venituri totale de 100.000 euro — un singur salariat se încadrează, evident, sub acest plafon.
- „Trimestrial" **nu înseamnă o singură declarație cumulată** pentru cele trei luni: art. 147 alin. (5) precizează explicit că se depun **câte o declarație pentru fiecare lună** din trimestru, doar că toate trei se depun deodată, până la data de 25 a lunii următoare încheierii trimestrului.
- Deci firma cu un salariat nu completează un formular D112 „simplificat" sau „unic pe trimestru" — completează trei formulare lunare, dar le depune toate trei la un singur termen trimestrial, nu lunar.

## Ce se greșește în practică

- Se presupune că firma mică depune o singură declarație D112 „cumulată" pe trimestru — corect e depunerea a trei declarații separate, câte una pentru fiecare lună, dar toate la termenul trimestrial.
- Se aplică regimul trimestrial din reflex, fără verificarea prealabilă a numărului mediu de salariați din anul anterior (până la 3 salariați exclusiv) — o firmă care a avut, la un moment dat în anul anterior, 4 salariați, nu se mai încadrează la excepție.
- Se confundă termenul lunar obișnuit (25 a lunii următoare celei pentru care se plătesc veniturile) cu termenul trimestrial al angajatorilor mici (25 a lunii următoare trimestrului) — aplicarea termenului greșit duce la declarare cu întârziere sau la depunere prematură.

## Ce face iConta.eu

iConta.eu generează D112 din datele statului de plată emis pentru fiecare lună (vezi `core/d112.py`), completând obligațiile fiscale (`ObligatieD112`, cu `cod_oblig` și `cod_bugetar`) conform structurii oficiale ANAF. Aplicația nu determină însă automat, la nivelul firmei, eligibilitatea pentru depunerea trimestrială de la art. 80 alin. (2) — adică nu verifică singură dacă numărul mediu de salariați din anul anterior s-a încadrat sub pragul de 3 și nu comută automat ritmul de depunere. Alegerea și aplicarea corectă a regimului lunar sau trimestrial de depunere a D112 rămân, la acest moment, decizii ale contabilului.

[iConta.eu](/)
