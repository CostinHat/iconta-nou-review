---
title: "Ce declarații fiscale trebuie depuse trimestrial în 2026?"
description: "D100 (impozitul pe veniturile microîntreprinderilor) e mereu trimestrial; D300, D394 și D406 devin trimestriale doar pentru firmele cu decontul de TVA trimestrial sau pentru neplătitorii de TVA."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce declarații fiscale trebuie depuse trimestrial în 2026?

O singură declarație e trimestrială necondiționat: D100, impozitul pe veniturile microîntreprinderilor. Restul declarațiilor „trimestriale" din practică nu au o regulă proprie de trimestrialitate — devin trimestriale doar pentru că firma respectivă are decontul de TVA trimestrial (sau, în cazul SAF-T, pentru că nu e deloc plătitoare de TVA).

## Temeiul legal

::: ghid-temei
„Calculul și plata impozitului pe veniturile microîntreprinderilor se efectuează trimestrial, până la data de 25 inclusiv a lunii următoare trimestrului pentru care se calculează impozitul."
— Codul fiscal, art. 56 alin. (1) — D100 (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„Prin excepție de la prevederile alin. (1), perioada fiscală este trimestrul calendaristic pentru persoana impozabilă care în cursul anului calendaristic precedent a realizat o cifră de afaceri... care nu a depășit plafonul de 100.000 euro... cu excepția situației în care persoana impozabilă a efectuat în cursul anului calendaristic precedent una sau mai multe achiziții intracomunitare de bunuri."
— Codul fiscal, art. 322 alin. (2) — condiția pentru decontul de TVA trimestrial, care determină și D300 (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„...la tip plătitor se înscrie perioada fiscală declarată pentru depunerea decontului de taxă pe valoarea adăugată (formularul 300), prevăzută la art. 322 din Codul fiscal, respectiv L - luna, T - trimestrul, S - semestrul, A - anul."
— OPANAF 2194/2025, instrucțiuni de completare, Secțiunea 1 lit. a) — D394 urmează periodicitatea decontului de TVA (sursă: anaf_surse/opanaf_2194_2025_d394.txt)

„Contribuabilii/Plătitorii transmit Declarația informativă D406 lunar sau trimestrial, urmând perioada fiscală aplicabilă pentru taxa pe valoarea adăugată (TVA). Contribuabilii care au ca perioadă fiscală aplicabilă pentru taxa pe valoarea adăugată semestrul sau anul transmit Declarația informativă D406 trimestrial."
— OPANAF 1783/2021, Anexa 4, pct. 2 (sursă: anaf_surse/opanaf_1783_2021_saft_d406.txt)

„Contribuabilii care nu sunt înregistrați în scopuri de TVA transmit Declarația informativă D406 trimestrial."
— OPANAF 1783/2021, Anexa 4, pct. 3 (sursă: anaf_surse/opanaf_1783_2021_saft_d406.txt)
:::

Descompus pe declarație:

- **D100** — trimestrial mereu, indiferent de altceva, pentru orice firmă cu regim de impozitare pe veniturile microîntreprinderilor. Termenul e ziua 25 a lunii următoare trimestrului.
- **D300** (decontul de TVA) — trimestrial doar dacă firma îndeplinește condiția art. 322 alin. (2): cifră de afaceri sub 100.000 € în anul precedent ȘI nicio achiziție intracomunitară de bunuri în anul precedent. Altfel rămâne lunar (regula generală).
- **D394** — trimestrială pentru firmele cu decont de TVA trimestrial (aceeași periodicitate ca D300, prin construcție), cu termen fix pe ziua 30.
- **D406/SAF-T** — trimestrial în două situații distincte: (a) firma are TVA cu perioadă semestrială sau anuală (cazuri rare), sau (b) firma nu e deloc înregistrată în scopuri de TVA. Un neplătitor de TVA nu are, prin definiție, un „decont trimestrial", dar tot depune D406 trimestrial, conform pct. 3.

## Ce se greșește în practică

- Se crede că „trimestrial" e o categorie fixă de declarații, în loc de o consecință a profilului de TVA al fiecărei firme.
- Se presupune că un neplătitor de TVA nu are nicio obligație legată de periodicitate — de fapt, chiar neplătitorii depun D406 trimestrial, conform pct. 3 al Anexei 4.
- Se aplică termenul standard de 25 pentru D394, deși termenul specific e ziua 30.
- Se ignoră condiția dublă de la art. 322 alin. (2) (plafon ȘI absența achizițiilor intracomunitare) — o singură achiziție IC în anul precedent scoate firma din regimul trimestrial de TVA, chiar dacă cifra de afaceri rămâne sub plafon.

## Ce face iConta.eu

Pentru setul de declarații legate de TVA (D300, D394, D406), iConta.eu **nu decide** singură periodicitatea — citește câmpul „tip decont" din Vectorul fiscal al firmei (secțiunea completată manual de contabil la Date firmă) și afișează periodicitatea corespunzătoare în ecranul de Declarații. Pentru D100, periodicitatea trimestrială e fixă în cod, conform art. 56. Aplicația **nu verifică automat** dacă firma îndeplinește efectiv condiția legală pentru decont trimestrial (plafonul de 100.000 € și absența achizițiilor intracomunitare din anul precedent) — alegerea „lunar" sau „trimestrial" rămâne integral responsabilitatea contabilului la completarea Vectorului fiscal; iConta.eu doar aplică, consecvent, valoarea declarată acolo.

[iConta.eu](/)
