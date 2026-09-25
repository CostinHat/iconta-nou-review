---
title: "Cum plătesc CASS pentru PFA?"
description: "CASS datorată de un PFA se calculează prin D212, cu aceleași termen și condiții ca impozitul pe venit — declarația și plata se fac până la 25 mai a anului următor."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum plătesc CASS pentru PFA?

Contribuția de asigurări sociale de sănătate pentru un PFA nu se plătește separat, printr-un formular propriu — se stabilește și se plătește prin D212, la același termen la care se declară și impozitul pe venit.

## Temeiul legal

::: ghid-temei
„Persoanele fizice care realizează venituri din cele prevăzute la art. 155 alin. (1) lit. b) stabilesc și declară contribuția, depun Declarația unică privind impozitul pe venit și contribuțiile sociale datorate de persoanele fizice la termenele și în condițiile prevăzute la titlul IV - Impozitul pe venit, pentru persoanele fizice care realizează venituri din activități independente."
— Codul fiscal (Legea 227/2015), art. 174 alin. (3) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce rezultă din trimiterea la titlul IV:

- Termenul de declarare și plată a CASS pentru un PFA e cel general de la art. 122 alin. (3) — 25 mai inclusiv a anului următor celui de realizare a veniturilor.
- CASS se calculează pe baza anuală stabilită la art. 170 alin. (1) — venitul net anual cumulat din toate sursele de activități independente, plafonat la nivelul a 72 de salarii minime brute pe țară pentru veniturile din 2026 (60 de salarii minime pentru 2025).
- Sub pragul minim de 6 salarii minime brute, CASS nu e obligatorie — dar contribuabilul poate opta pentru plata ei (art. 180).
- Dacă declarația se depune și se achită integral (impozit, CAS, CASS) până la 15 aprilie 2026, pentru veniturile din 2025, se aplică bonificația de 3% din impozitul pe venit (OUG 8/2026).

## Ce se greșește în practică

- Se caută un „formular separat" pentru plata CASS — nu există; suma rezultă direct din D212, ca și impozitul pe venit.
- Se plătește CASS pe venitul net efectiv, ignorând plafonul maxim (72 sau 60 de salarii minime brute, în funcție de an) — orice venit peste plafon nu mai mărește baza de calcul.
- Se omite verificarea pragului minim de 6 salarii minime brute — sub acest nivel, CASS nu e datorată automat, ci doar dacă se optează pentru plata ei.

## Ce face iConta.eu

Motorul `core/d212_engine.py` (funcția `calculeaza_cass`) calculează CASS liniar pe venitul net, cu pragul minim opțional de 6 salarii minime brute și plafonul maxim de 72 de salarii minime brute pentru veniturile din 2026 (60 pentru 2025), citite din registrul de cote al aplicației, nu hardcodate. Funcția `fisa_d212` (`core/rip_api.py`) produce calculul complet — CASS, CAS și impozit — pornind de la operațiunile validate din Registrul-jurnal de încasări și plăți, pentru un PFA la sistem real, doar pentru anii 2025 și 2026.

Aplicația nu emite instrucțiuni de plată sau nu inițiază transferul sumei către bugetul de stat — calculul se oprește la fișa de calcul, iar plata efectivă se face separat, prin canalele obișnuite (ghiseul.ro, ordin de plată).

[iConta.eu](/)
