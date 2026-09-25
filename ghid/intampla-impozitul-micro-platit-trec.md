---
title: "Ce se întâmplă cu impozitul micro plătit dacă trec la profit în același an"
description: "Ce se întâmplă cu impozitul pe veniturile microîntreprinderilor deja plătit atunci când firma depășește plafonul de 100.000 euro și trece la impozit pe profit în cursul anului."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce se întâmplă cu impozitul micro plătit dacă trec la profit în același an

O microîntreprindere care depășește în cursul anului plafonul de venituri devine, de la un moment dat, plătitoare de impozit pe profit — dar asta nu înseamnă că tot anul se recalculează retroactiv. Legea desparte clar cele două perioade: impozitul micro plătit pe trimestrele anterioare rămâne definitiv, iar impozitul pe profit se aplică doar de la trimestrul depășirii.

## Temeiul legal

::: ghid-temei
„Dacă în cursul unui an fiscal o microîntreprindere realizează venituri mai mari de 100.000 euro, aceasta datorează impozit pe profit începând cu trimestrul în care s-a depășit această limită. [...]
(6) Calculul și plata impozitului pe profit de către microîntreprinderile care se încadrează în prevederile alin. (1), (2), (4) și (7) se efectuează luând în considerare veniturile și cheltuielile realizate începând cu trimestrul respectiv."
— Codul fiscal (Legea 227/2015), art. 52 alin. (1) și (6) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Trecerea la impozit pe profit **nu e retroactivă**: firma nu recalculează și nu regularizează impozitul micro plătit pentru trimestrele anterioare depășirii plafonului — acele plăți rămân definitive, calculate conform regimului micro aplicabil la momentul respectiv.
- Impozitul pe profit se calculează **doar pentru perioada rămasă din an**, luând în calcul veniturile și cheltuielile realizate „începând cu trimestrul respectiv" — nu cumulat de la 1 ianuarie, ci strict din trimestrul în care s-a produs depășirea plafonului de 100.000 euro.
- Verificarea plafonului se face cumulat de la începutul anului fiscal: „Limitele fiscale prevăzute la alin. (1) se verifică pe baza veniturilor înregistrate cumulat de la începutul anului fiscal" (art. 52 alin. (5)) — dar odată depășit pragul, doar operațiunile ulterioare intră în baza de calcul a impozitului pe profit.
- Aceeași logică (fără recalculare retroactivă, doar aplicare de la trimestrul evenimentului) se aplică și în celelalte cazuri de ieșire obligatorie din sistemul micro în cursul anului: nedepunerea la termen a situațiilor financiare anuale (alin. (2)), pierderea condiției de a avea cel puțin un salariat (alin. (3)), sau începerea unor activități excluse de la art. 47 alin. (3) lit. f)-i) (alin. (4)).

## Ce se greșește în practică

- Se recalculează greșit tot anul ca fiind supus impozitului pe profit, inclusiv trimestrele în care firma era, legal, plătitoare de impozit micro — legea protejează explicit plățile deja făcute conform regimului anterior.
- Se calculează impozitul pe profit pornind de la veniturile și cheltuielile cumulate de la 1 ianuarie, în loc să se ia în calcul doar cele realizate din trimestrul depășirii plafonului.
- Se confundă momentul depășirii plafonului (verificat cumulat de la începutul anului) cu momentul din care se schimbă regimul de impozitare (care e strict trimestrul respectiv, nu retroactiv de la 1 ianuarie).
- Se omite verificarea celorlalte situații care obligă, separat de plafonul valoric, trecerea la impozit pe profit în cursul anului (lipsa unui salariat, nedepunerea situațiilor financiare, activități excluse).

## Ce face iConta.eu

La data acestui ghid, iConta.eu completează cota de impozit micro în declarația D100 pentru firmele plătitoare de acest regim, dar nu am găsit în cod o funcție dedicată care să detecteze automat depășirea plafonului de 100.000 euro în cursul anului și să comute regimul de impozitare de la un trimestru la altul. Trecerea de la impozit micro la impozit pe profit în cursul anului, cu separarea corectă a perioadelor, rămâne o decizie și o verificare pe care contabilul trebuie s-o facă manual.

[iConta.eu](/)
