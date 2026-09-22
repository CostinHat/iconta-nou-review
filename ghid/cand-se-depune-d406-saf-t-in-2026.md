---
title: Când se depune D406 SAF-T în 2026?
description: D406 se depune lunar sau trimestrial, în funcție de perioada fiscală de TVA a firmei, cu termen-limită ultima zi calendaristică a lunii următoare perioadei de raportare — singura declarație cu scadență pe ultima zi a lunii, nu pe 25.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Când se depune D406 SAF-T în 2026?

Spre deosebire de majoritatea declarațiilor fiscale, care au termenul pe 25 ale lunii, D406 are o scadență diferită și o frecvență de raportare care depinde de perioada fiscală de TVA a firmei, nu de o regulă fixă.

## Temeiul legal

::: ghid-temei
"1. Declaraţia informativă D406 se transmite în format electronic, data-limită de
transmitere fiind: - ultima zi calendaristică a lunii următoare perioadei de raportare,
respectiv luna/trimestrul calendaristic, după caz, pentru alte informaţii decât cele privind
secţiunile "Stocuri" şi "Active"; - la termenul de depunere a situaţiilor financiare
aferente exerciţiului financiar, în cazul secţiunii "Active"; - la termenul stabilit de
organul fiscal central, care nu poate fi mai mic de 30 de zile calendaristice de la data
solicitării, în cazul secţiunii "Stocuri"."
(opanaf_1783_2021_saft_d406.txt, Anexa 4, pct. 1)

"2. Contribuabilii/Plătitorii transmit Declaraţia informativă D406 lunar sau trimestrial,
urmând perioada fiscală aplicabilă pentru taxa pe valoarea adăugată (TVA). Contribuabilii
care au ca perioadă fiscală aplicabilă pentru taxa pe valoarea adăugată semestrul sau anul
transmit Declaraţia informativă D406 trimestrial.
3. Contribuabilii care nu sunt înregistraţi în scopuri de TVA transmit Declaraţia
informativă D406 trimestrial."
(opanaf_1783_2021_saft_d406.txt, Anexa 4, pct. 2-3)

"5. (1) Contribuabilii/Plătitorii beneficiază de o perioadă de graţie de: - 6 (şase) luni
pentru prima raportare, respectiv cinci (cinci) luni pentru a doua raportare, 4 (patru) luni
pentru a treia raportare, 3 (trei) luni pentru a patra raportare, 2 (două) luni pentru a
cincea raportare, pentru contribuabilii care au obligaţia de transmitere lunară a
fişierului SAF-T; - 3 (trei) luni pentru prima raportare, pentru contribuabilii care au
obligaţia de transmitere trimestrială a fişierului SAF-T. (2) Perioada de graţie se
calculează pornind de la ultima zi a perioadei de raportare pentru care aceasta se acordă
... (3) Astfel, contribuabilii/plătitorii nu sunt sancţionaţi contravenţional, conform
prevederilor art. 337^1 din Legea nr. 207/2015 ..., dacă depun Declaraţia informativă D406
validă în termenul maxim prevăzut la alin. (1)."
(opanaf_1783_2021_saft_d406.txt, Anexa 4, pct. 5)
:::

## Cum se determină frecvența: lunar sau trimestrial

Regula de bază: D406 urmează perioada fiscală de TVA a firmei.

- Firmă neînregistrată în scopuri de TVA → raportare trimestrială, indiferent de altă condiție.
- Firmă plătitoare de TVA cu perioadă fiscală lunară → D406 lunar.
- Firmă plătitoare de TVA cu perioadă fiscală trimestrială → D406 trimestrial.
- Firmă plătitoare de TVA cu perioadă fiscală semestrială sau anuală → D406 se depune totuși trimestrial (legea "forțează" trimestrialul, semestrul și anul nefiind opțiuni pentru D406).

Termenul-limită este ultima zi calendaristică a lunii următoare perioadei de raportare — pentru toate secțiunile în afară de "Stocuri" (depusă doar la cererea ANAF) și "Active" (depusă anual, la termenul situațiilor financiare).

::: ghid-exemplu
O firmă plătitoare de TVA lunar raportează D406 pentru luna august 2026 până cel târziu pe 30 septembrie 2026 (ultima zi calendaristică a lunii următoare), nu pe 25 septembrie.
:::

Pentru firmele nou-obligate la prima raportare, legea prevede și o perioadă de grație (de la 6 luni la 2 luni, în funcție de câta raportare este, pentru cele lunare, respectiv 3 luni pentru prima raportare trimestrială), în care nu se aplică sancțiuni contravenționale dacă declarația e depusă validă în acest interval extins.

## Ce se greșește în practică

- Se aplică termenul obișnuit de 25 ale lunii, ca la alte declarații, în loc de ultima zi calendaristică a lunii următoare.
- Se raportează lunar o firmă cu perioadă fiscală de TVA semestrială sau anuală, deși legea cere trimestrial pentru acest caz.
- Se presupune eronat că "Active" și "Stocuri" se depun în același ritm ca restul secțiunilor — "Active" e anuală, "Stocuri" doar la cerere.
- Se ignoră perioada de grație pentru primele raportări ale unei firme nou-obligate și se calculează o scadență mai strânsă decât cea legală.

## Ce face iConta.eu

Tipul de raportare (lunar `"L"` sau trimestrial `"T"`) este calculat automat, prin funcția `fereastra_d406`: dacă firma nu e plătitoare de TVA, se aplică trimestrial; dacă perioada de TVA a firmei e semestrială sau anuală, se mapează forțat pe trimestrial; altfel se urmează exact perioada fiscală de TVA a firmei. Codul tipului de depunere (L/T/A) se derivă din întinderea reală a ferestrei de raportare, nu se alege manual, iar o întindere neașteptată oprește generarea în loc să cadă tacit pe lunar. Separat, calendarul de scadențe al aplicației confirmă D406 ca fiind singura declarație cu termen pe ultima zi a lunii, nu pe 25.

Perioada de grație prevăzută la primele raportări ale firmelor nou-obligate nu a fost identificată ca fiind cablată în scadențarul aplicației — contabilul unei firme nou-intrate sub obligația D406 trebuie să verifice separat dacă beneficiază de acest termen extins.

[iConta.eu](/)
