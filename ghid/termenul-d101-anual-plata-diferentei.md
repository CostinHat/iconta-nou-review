---
title: "Termenul pentru D101 anual și pentru plata diferenței"
description: "Termenul legal pentru D101 este 25 iunie a anului următor, dar aplicația poate încă afișa o dată nealiniată pentru anul fiscal 2026."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Termenul pentru D101 anual și pentru plata diferenței

Termenul de depunere a D101 (și, implicit, de plată a diferenței de impozit rezultate din definitivare) trebuie verificat cu atenție pentru anul fiscal 2026, unde există o discrepanță activă documentată.

## Temeiul legal

::: ghid-temei
"Art.42 alin.(1) (modificat de OUG 8/2026 art.6 pct.12, MO 147/25.02.2026, aplicabil «începând cu anul fiscal 2026» — art.10 alin.(2) OUG 8/2026): «Contribuabilii au obligația să depună o declarație anuală privind impozitul pe profit până la data de 25 iunie inclusiv a anului următor...»" — dosarul de cercetare F027, pe baza `anaf_surse/cod_fiscal_227_2015_consolidat.txt`.
:::

Pentru perioada 2021–2025, termenul a fost tot 25 iunie, printr-o derogare specială (OUG 153/2020 art.I alin.(13) lit.a), aplicabilă 2021–2025 conform art.VI). Practic, termenul de 25 iunie nu se schimbă de fapt față de anii anteriori, deși baza inițială din Codul fiscal (înainte de OUG 8/2026) prevedea 25 martie.

**Atenție, discrepanță documentată:** codul din `core/d101.py` (liniile 193–232) emite astăzi data de **25 martie** pentru declarațiile aferente anului fiscal 2026 și ulterior, aliniat la un validator intern (DUKIntegrator) instalat local, care nu a fost încă actualizat de ANAF — nu la textul legii. Decizia de a menține alinierea cu validatorul, în locul legii, a fost asumată explicit intern, cu un semnal ca testul aferent să pice automat când validatorul oficial se va actualiza.

## Ce se greșește în practică

Cea mai riscantă greșeală e să vă bazați exclusiv pe data afișată de aplicație pentru un D101 aferent anului fiscal 2026 (declarat în 2027), fără să verificați manual termenul legal.

## Ce face iConta.eu

Pentru anii fiscali 2022–2025, data generată de aplicație corespunde termenului legal (25 iunie); pentru anul fiscal 2021, aplicația nu are o regulă de calcul definită și nu generează termenul. Pentru anul fiscal 2026 (declarat în 2027), aplicația poate genera încă data de 25 martie 2027, în timp ce termenul legal real este **25 iunie 2027**. Recomandăm verificarea manuală a termenului până la actualizarea validatorului.

[iConta.eu](/)
