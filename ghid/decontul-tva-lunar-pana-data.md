---
title: "Decontul de TVA lunar: până la ce dată îl depun"
description: "Termenul legal de depunere a decontului de TVA lunar (formularul 300), cu excepția decontului lunii noiembrie, care se depune până la 21 decembrie, conform OPANAF 174/2026, Codului fiscal și Codului de procedură fiscală."
published: 2026-09-24
modified: 2026-10-03
poarta: v1
---

# Decontul de TVA lunar: până la ce dată îl depun

Termenul decontului de TVA e printre cele mai stabile din calendarul fiscal — dar are o excepție de sfârșit de an pe care mulți contabili o uită. Iată exact ce spune legea pentru perioada fiscală lunară.

## Temeiul legal

::: ghid-temei
„Persoanele înregistrate conform art. 316 trebuie să depună [...] un decont de taxă, până la data de 25 inclusiv a lunii următoare celei în care se încheie perioada fiscală respectivă."
— Cod fiscal (Legea 227/2015), art. 323 alin. (1) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))
:::

::: ghid-temei
„Creanțele fiscale administrate de organul fiscal central pentru care, potrivit Codului fiscal sau altor legi care le reglementează, scadența și/sau termenul de declarare se împlinesc la 25 decembrie, sunt scadente și/sau se declară până la data de 21 decembrie. În situația în care data de 21 decembrie, este zi nelucrătoare, creanțele fiscale sunt scadente și/sau se declară până în ultima zi lucrătoare anterioară datei de 21 decembrie."
— Legea 207/2015 (Codul de procedură fiscală), art. 155 alin. (2) (sursă: [Legea nr. 207/2015 privind Codul de procedură fiscală](https://legislatie.just.ro/Public/DetaliiDocument/170007))
:::

Ce rezultă din temeiul de mai sus, coroborat cu instrucțiunile formularului:

- **Termenul general**: data de **25 inclusiv** a lunii următoare celei pentru care se depune decontul — pentru perioada fiscală lunară, confirmat și de instrucțiunile formularului 300, versiunea 2026: „până la data de 25 inclusiv a lunii următoare celei pentru care se depune decontul... perioada fiscală este luna calendaristică, potrivit prevederilor art. 322 din Codul fiscal" (OPANAF 174/2026, Anexa 2, lit. a).
- **Perioada fiscală lunară e regula**, aplicabilă implicit oricărui plătitor de TVA (Cod fiscal art. 322 alin. (1)); perioada trimestrială e o excepție condiționată de cifra de afaceri a anului precedent și de absența achizițiilor intracomunitare de bunuri.
- **Excepția de sfârșit de an**: decontul al cărui termen s-ar împlini la 25 decembrie — pentru perioada fiscală lunară, decontul lunii **noiembrie** — se depune **până la 21 decembrie**; dacă 21 decembrie e zi nelucrătoare, până în ultima zi lucrătoare dinaintea ei. Temei: Codul de procedură fiscală art. 155 alin. (2), reluat explicit în instrucțiunile OPANAF 174/2026. Decontul lunii **decembrie** urmează regula generală: până la 25 ianuarie a anului următor.
- Formularul valabil în 2026 (structura XML ANAF v12) e cel aprobat prin OPANAF 174/2026, aplicabil „începând cu declararea obligațiilor fiscale aferente primei perioade fiscale din anul 2026" (OPANAF 174/2026, art. 6).

## Ce se greșește în practică

- Se aplică termenul de 25 decembrie și decontului lunii noiembrie, ignorând excepția legală de depunere până pe 21 decembrie; sau, invers, se crede că și decontul lunii decembrie trebuie depus tot în decembrie, deși el urmează regula generală (25 ianuarie).
- Se confundă termenul de depunere cu termenul de plată — cele două coincid la TVA (art. 326 alin. (1) din Codul fiscal leagă plata de termenul de depunere a decontului), dar contabilul care vine din alte declarații (unde termenele diferă) poate presupune greșit o dată de plată separată.
- Se presupune că formularul din 2025 mai poate fi folosit la începutul lui 2026, deși OPANAF 174/2026 impune noul formular începând cu prima perioadă fiscală din 2026.

## Ce face iConta.eu

Funcționalitatea **Declarația D300** calculează automat decontul de TVA din facturile firmei, pe cote (21%/11%/9%), cu tratarea distinctă a livrărilor/achizițiilor intracomunitare, a taxării inverse și a TVA la încasare, și validează XML-ul generat cu DUKIntegrator, validatorul oficial ANAF rulat local, înainte de a-l pune la dispoziția contabilului. Perioada fiscală (lunară sau trimestrială) e determinată automat pe baza vectorului fiscal al firmei. Calendarul de termene al aplicației (semaforul și lista de termene) afișează pentru decont data de 25 a lunii următoare, iar pentru obligațiile lunii noiembrie, 21 decembrie (sau ultima zi lucrătoare dinaintea ei), potrivit art. 155 alin. (2) din Codul de procedură fiscală.

Aplicația **nu depune** automat declarația la ANAF — validarea confirmă doar că XML-ul e corect structurat, nu că a fost transmisă; depunerea rămâne în sarcina contabilului, prin SPV. De asemenea, aplicația **nu automatizează** alegerea dintre rambursarea și reportarea unei sume negative de TVA (bifa din decont) — calculează corect soldul, dar decizia rămâne manuală. Cotele atipice (19%, 5%) nu au rând automat în decont; dacă apar pe facturi, aplicația generează un avertisment explicit, nu le omite tăcut.

[iConta.eu](/)
