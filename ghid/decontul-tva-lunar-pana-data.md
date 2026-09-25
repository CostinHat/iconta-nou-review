---
title: "Decontul de TVA lunar: până la ce dată îl depun"
description: "Termenul legal de depunere a decontului de TVA lunar (formularul 300), cu excepția lunii decembrie, conform OPANAF 174/2026 și Codului fiscal."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Decontul de TVA lunar: până la ce dată îl depun

Termenul decontului de TVA e printre cele mai stabile din calendarul fiscal — dar are o excepție de sfârșit de an pe care mulți contabili o uită. Iată exact ce spune legea pentru perioada fiscală lunară.

## Temeiul legal

::: ghid-temei
„Persoanele înregistrate conform art. 316 trebuie să depună [...] un decont de taxă, până la data de 25 inclusiv a lunii următoare celei în care se încheie perioada fiscală respectivă."
— Cod fiscal (Legea 227/2015), art. 323 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce rezultă din temeiul de mai sus, coroborat cu instrucțiunile formularului:

- **Termenul general**: data de **25 inclusiv** a lunii următoare celei pentru care se depune decontul — pentru perioada fiscală lunară, confirmat și de instrucțiunile formularului 300, versiunea 2026: „până la data de 25 inclusiv a lunii următoare celei pentru care se depune decontul... perioada fiscală este luna calendaristică, potrivit prevederilor art. 322 din Codul fiscal" (OPANAF 174/2026, Anexa 2, lit. a).
- **Perioada fiscală lunară e regula**, aplicabilă implicit oricărui plătitor de TVA (Cod fiscal art. 322 alin. (1)); perioada trimestrială e o excepție condiționată de cifra de afaceri a anului precedent și de absența achizițiilor intracomunitare de bunuri.
- **Excepția de sfârșit de an**: decontul aferent lunii decembrie se depune **până la 21 decembrie**, nu pe 25 ianuarie — temei Codul de procedură fiscală art. 155 alin. (2), reluat explicit în instrucțiunile OPANAF 174/2026.
- Formularul valabil în 2026 e versiunea 12 a decontului 300, aplicabilă „începând cu declararea obligațiilor fiscale aferente primei perioade fiscale din anul 2026" (OPANAF 174/2026, art. 6).

## Ce se greșește în practică

- Se aplică termenul de 25 și pentru luna decembrie, ignorând excepția legală de depunere până pe 21 decembrie.
- Se confundă termenul de depunere cu termenul de plată — cele două coincid la TVA (art. 323 alin. (1) leagă direct depunerea de plată), dar contabilul care vine din alte declarații (unde termenele diferă) poate presupune greșit o dată de plată separată.
- Se presupune că formularul din 2025 mai poate fi folosit la începutul lui 2026, deși OPANAF 174/2026 impune versiunea 12 începând cu prima perioadă fiscală din 2026.

## Ce face iConta.eu

Funcționalitatea **Declarația D300** (`core/d300.py`) calculează automat decontul de TVA din facturile firmei, pe cote (21%/11%/9%), cu tratarea distinctă a livrărilor/achizițiilor intracomunitare, a taxării inverse și a TVA la încasare, și validează XML-ul generat cu DUKIntegrator, validatorul oficial ANAF rulat local, înainte de a-l pune la dispoziția contabilului. Perioada fiscală (lunară sau trimestrială) e determinată automat pe baza vectorului fiscal al firmei.

Aplicația **nu depune** automat declarația la ANAF — validarea confirmă doar că XML-ul e corect structurat, nu că a fost transmisă; depunerea rămâne în sarcina contabilului, prin SPV. De asemenea, aplicația **nu automatizează** alegerea dintre rambursarea și reportarea unei sume negative de TVA (bifa din decont) — calculează corect soldul, dar decizia rămâne manuală. Cotele atipice (19%, 5%) nu au rând automat în decont; dacă apar pe facturi, aplicația generează un avertisment explicit, nu le omite tăcut.

[iConta.eu](/)
