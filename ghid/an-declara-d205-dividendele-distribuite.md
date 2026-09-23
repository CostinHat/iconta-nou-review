---
title: "În ce an se declară în D205 dividendele distribuite, dar neplătite?"
description: "Regula legală privind anul de raportare pentru dividendele aprobate spre distribuire dar neîncasate de asociați până la 31 decembrie."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# În ce an se declară în D205 dividendele distribuite, dar neplătite?

Un dividend poate fi aprobat spre distribuire într-un an și plătit efectiv abia în anul următor (sau eșalonat). Legea spune clar în ce an intră obligația de declarare.

## Temeiul legal

::: ghid-temei
"(7) [...] Termenul de virare a impozitului este până la data de 25 inclusiv a lunii următoare celei în care se face plata. În cazul dividendelor/câștigurilor obținute ca urmare a deținerii de titluri de participare, distribuite, dar care nu au fost plătite acționarilor/asociaților/investitorilor până la sfârșitul anului în care s-a aprobat distribuirea acestora, impozitul pe dividende/câștig se plătește până la data de 25 ianuarie inclusiv a anului următor distribuirii. Impozitul datorat se virează integral la bugetul de stat."
— Codul fiscal, art. 97 alin. (7) (`anaf_surse/cod_fiscal_227_2015_consolidat.txt:9470-9474`)
:::

Instrucțiunile de completare a formularului D205 confirmă și ele explicit anul de raportare:

::: ghid-temei
"Impozitul aferent dividendelor distribuite, dar care nu au fost plătite acționarilor sau asociaților până la sfârșitul anului în care s-a aprobat distribuirea acestora se cuprinde în declarația aferentă perioadei în care s-a aprobat distribuirea dividendelor."
— OPANAF 179/2022, instrucțiuni de completare D205 (`anaf_surse/opanaf_179_2022_d205_d207_baza.txt:381-400`)
:::

Deci: dividendul se declară în D205 pentru **anul în care a fost aprobată distribuirea**, chiar dacă plata către asociați se face abia anul următor. Termenul de virare a impozitului pentru acest caz este 25 ianuarie a anului următor distribuirii — distinct de termenul general de depunere a D205 (ultima zi a lunii februarie a anului curent, pentru anul expirat).

## Ce se greșește în practică

Cea mai frecventă confuzie este raportarea dividendului abia în anul în care este efectiv plătit, pe motiv că "nu există impozit de reținut cât timp nu s-a plătit nimic". Legea leagă însă obligația de anul aprobării distribuirii, nu de anul plății.

## Ce face iConta.eu

Aici este important să fim exacți: aplicația calculează corect cota și impozitul atunci când un dividend distribuit într-un an este plătit ulterior (motorul FIFO din `dividende_curs.py` aplică cota de la data fiecărei distribuiri, verificat prin teste dedicate). **Însă**, pentru cazul specific din acest ghid — dividend distribuit, dar deloc plătit până la 31 decembrie — generatorul D205 (`core/d205.py`) exclude din declarație orice beneficiar pentru care suma plătită este zero, deci acel dividend nu apare automat în declarația anului aprobării. Acesta este un gol de conformitate cunoscut și documentat intern la iConta, nu un comportament corect din punct de vedere legal. La acest moment, iConta nu are în interfață o opțiune de adăugare manuală a unui beneficiar la generarea D205 (spre deosebire de alte declarații din aplicație, care au un astfel de ecran) — pentru acest caz, suma trebuie tratată de contabil separat de fluxul automat al aplicației, pentru a nu pierde obligația de declarare.

[iConta.eu](/)
