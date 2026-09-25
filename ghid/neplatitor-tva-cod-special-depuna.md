---
title: "Un neplătitor de TVA cu cod special trebuie să depună D390?"
description: "Când o firmă neplătitoare de TVA, înregistrată cu cod special conform art. 317 din Codul fiscal, datorează declarația recapitulativă D390."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Un neplătitor de TVA cu cod special trebuie să depună D390?

Da — dacă firma neplătitoare de TVA are cod special de înregistrare (art. 317 din Codul fiscal) și a desfășurat, în luna raportată, operațiuni intracomunitare care intră în sfera declarației, D390 se datorează exact ca pentru o firmă plătitoare de TVA obișnuită.

## Temeiul legal

::: ghid-temei
„1.1. Declaraţia recapitulativă se depune lunar, în condiţiile prevăzute la art. 325 din Legea nr. 227/2015 privind Codul fiscal, cu modificările şi completările ulterioare (Codul fiscal), până la data de 25 inclusiv a lunii următoare unei luni calendaristice, de către persoanele impozabile înregistrate în scopuri de TVA conform art. 316 sau 317 din Codul fiscal.
1.2. Persoanele impozabile înregistrate în scopuri de TVA depun declaraţia recapitulativă numai pentru lunile calendaristice în care ia naştere exigibilitatea taxei [...]"
— OPANAF 705/2020 (aprobarea formularului 390 VIES), Anexa 2, Instrucțiuni, pct. 1.1-1.2 (sursă: anaf_surse/opanaf_705_2020_d390.txt)
:::

Ce rezultă din text:

- Obligația de a depune D390 nu e legată doar de înregistrarea „obișnuită" în scopuri de TVA (art. 316) — legea numește explicit și înregistrarea specială conform **art. 317**, care privește persoanele care efectuează achiziții intracomunitare sau primesc/prestează servicii intracomunitare fără să fie plătitoare de TVA „normală".
- Termenul e identic pentru ambele categorii: **până pe 25** ale lunii următoare celei de raportare.
- D390 nu se depune „pe zero" — doar pentru lunile în care **ia naștere exigibilitatea taxei** pe operațiunile intracomunitare relevante. O lună fără astfel de operațiuni nu generează obligație de depunere.

Concret: o firmă neplătitoare de TVA, dar înregistrată conform art. 317 (de exemplu pentru că a depășit plafonul de achiziții intracomunitare sau primește servicii de la un prestator dintr-un alt stat membru), depune D390 în lunile în care are asemenea operațiuni — exact ca o firmă plătitoare de TVA.

## Ce se greșește în practică

- Se presupune că D390 e o obligație exclusivă a firmelor plătitoare de TVA (art. 316) — legea o extinde explicit și la înregistrarea specială art. 317.
- Se depune D390 „pe zero" în lunile fără operațiuni intracomunitare, deși declarația se depune doar când ia naștere exigibilitatea taxei pe astfel de operațiuni.
- Se confundă codul special de TVA (art. 317, pentru neplătitori cu operațiuni intracomunitare) cu codul „normal" de înregistrare în scopuri de TVA (art. 316) — sunt regimuri diferite, dar ambele generează, în condițiile arătate mai sus, obligația de D390.

## Ce face iConta.eu

Aplicația are un câmp dedicat în profilul firmei (`inreg_art317`) care marchează explicit dacă firma e înregistrată special în scopuri de TVA conform art. 317, separat de statutul de plătitor „obișnuit" de TVA. Motorul care determină ce declarații datorează firma (folosit pentru semnalizarea obligațiilor fiscale și pentru termene) verifică acest marcaj: dacă firma are operațiuni intracomunitare și e neplătitoare de TVA, dar are bifat art. 317, D390 apare corect ca declarație datorată; dacă marcajul lipsește, aplicația nu presupune tacit obligația, ci semnalează explicit contabilului să confirme înregistrarea art. 317 în profil. Generarea propriu-zisă a declarației D390 verifică, la rândul ei, dacă există operațiuni intracomunitare cu exigibilitate în luna respectivă și refuză generarea pe zero, exact cum cere norma de mai sus.

[iConta.eu](/)
