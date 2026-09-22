---
title: Cum se declară impozitul micro trimestrial?
description: Impozitul micro se declară prin D100 până pe 25 ale lunii următoare fiecărui trimestru, cu excepția trimestrului IV, pentru care termenul este 25 iunie anul următor, nu 25 ianuarie.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se declară impozitul micro trimestrial?

Declararea impozitului micro urmează regula generală „25 a lunii următoare" pentru trei din cele patru trimestre — dar trimestrul IV are o excepție importantă, care generează frecvent confuzie chiar și în interiorul aplicațiilor de contabilitate.

## Temeiul legal

::: ghid-temei
**CF art. 51 alin. (1):**
> „Cota de impozit pe veniturile microîntreprinderilor este de 1%."
— sursă: `anaf_surse/cod_fiscal_227_2015_consolidat.html`

**OPANAF 587/2016, Anexa 4, Cap. I, pct. 1.2 lit. d):**
> „impozit pe veniturile microîntreprinderilor. Pe perioada aplicării prevederilor art. I din Ordonanța de
> urgență a Guvernului nr. 153/2020, pentru contribuabilii plătitori de impozit pe veniturile
> microîntreprinderilor, prin derogare de la prevederile art. 56 din Codul fiscal, termenul pentru
> depunerea declarației aferente trimestrului IV este până la data de 25 iunie inclusiv a anului
> următor;"
— sursă: `anaf_surse/opanaf_587_2016_aprobarea_modelului_continutului_formularelor_utilizate.txt:932-936`

**Structura tehnică D100, nomenclator poz. 5, cod 121:**
> „5. 121 (poz.5) Impozit pe veniturile microîntreprinderilor ... art.47 și 56 din Legea nr.227/2015
> privind Codul fiscal — 5503 — T ... 25 a lunii următoare perioadei de raportare. Excepție: scadența
> 25.06.an+1 pentru trim.IV an (până în anul de raportare 2025 inclusiv). Exemplu: Excepție 25.06.2022
> pentru trim.IV 2021"
— sursă: `anaf_surse/d100_struct_anaf.txt:767-812`
:::

## Termenele, trimestru cu trimestru

Pentru trimestrele I-III, termenul e cel general: 25 a lunii următoare încheierii trimestrului (25 aprilie, 25 iulie, 25 octombrie). Pentru **trimestrul IV, excepția se aplică**: declarația se depune până la **25 iunie anul următor**, nu 25 ianuarie cum ar rezulta din aplicarea mecanică a regulii generale.

O notă tehnică mai veche din structura ANAF limitează formal această excepție „până în anul de raportare 2025 inclusiv", dar norma consolidată curentă (OPANAF 587/2016, forma actualizată în 2026) păstrează neschimbată regula celor 25 iunie, fără limită de an, iar validatorul oficial de declarații respinge orice altă dată pentru trimestrul IV al impozitului micro. Practic, excepția rămâne valabilă și pentru anii următori.

**Atenție la afișajul din aplicație pentru trimestrul IV:** dacă lista de termene/scadențe din semafor arată pentru trimestrul IV data de 25 ianuarie anul următor, acea dată nu corespunde regulii corecte (25 iunie) — verificați întotdeauna data de scadență din declarația D100 generată efectiv, nu doar afișajul din lista de obligații, pentru trimestrul IV.

## Ce se greșește în practică

- Se aplică regula generică „25 a lunii următoare" și pentru trimestrul IV, rezultând termenul greșit de 25 ianuarie, în loc de 25 iunie.
- Se citește nota tehnică veche „excepție valabilă până în 2025 inclusiv" ca fiind încă în vigoare și se presupune (greșit) că din 2026 excepția nu se mai aplică.
- Se depune declarația pe bază zero (fără venituri în trimestru), deși structura oficială nu permite un XML fără nicio obligație pozitivă.
- Se confundă cota (obligatorie doar pentru cod 121) cu alte câmpuri ale declarației, completând-o greșit pentru alte obligații.

## Ce face iConta.eu

`core/d100.py`, funcția `_scadenta_cod`, calculează corect scadența declarației: pentru trimestrele I-III, 25 a lunii următoare; pentru trimestrul IV al impozitului micro (cod 121), 25 iunie anul următor — confirmat inclusiv printr-un test dedicat (`core/test_d100_scadenta_trimiv.py`). Cota de 1% (poziția 17a din formular) e completată automat doar pentru cod 121, conform cerinței structurii oficiale.

**De reținut:** acest calcul corect există în generatorul propriu-zis al XML-ului. Modulul de scadențar folosit de semaforul de obligații/dashboard (`core/scadente.py`) nu are însă o ramură dedicată pentru tipul „d100" și, pentru trimestrul IV, cade pe regula generică din cod, care calculează 25 ianuarie anul următor — o dată diferită de cea generată efectiv în declarație. E o divergență internă cunoscută, între ceea ce arată semaforul și ceea ce depune efectiv declarația, în special pentru trimestrul IV; dacă vedeți în listă un termen de 25 ianuarie pentru trimestrul IV al impozitului micro, tratați-l cu rezervă și verificați scadența reală din declarația D100 generată.

[iConta.eu](/)
