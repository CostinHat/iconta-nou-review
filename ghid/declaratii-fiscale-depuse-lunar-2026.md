---
title: "Ce declarații fiscale trebuie depuse lunar în 2026?"
description: "Nucleul declarațiilor cu periodicitate lunară în 2026 — D112, D301, D390, D394 și, condiționat de profilul firmei, D300 și D406 — cu temeiul legal al fiecăreia."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce declarații fiscale trebuie depuse lunar în 2026?

Nu există un răspuns unic „aceste declarații se depun mereu lunar" — periodicitatea depinde de tipul declarației și, pentru cele legate de TVA, de profilul concret al firmei (dacă e plătitoare de TVA și cu ce periodicitate a decontului). Există totuși un nucleu de declarații cu regulă lunară clară în lege, plus altele care devin lunare doar când firma are decont de TVA lunar.

## Temeiul legal

::: ghid-temei
„...sunt obligate să depună lunar, până la data de 25 inclusiv a lunii următoare celei pentru care se plătesc veniturile, Declarația privind obligațiile de plată a contribuțiilor sociale, impozitului pe venit și evidența nominală a persoanelor asigurate."
— Codul fiscal, art. 147 alin. (1) — D112 (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„Perioada fiscală este luna calendaristică."
— Codul fiscal, art. 322 alin. (1) — regula generală pentru decontul de TVA, D300 (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„Decontul special de taxă [...] se depune până la data de 25 inclusiv a lunii următoare celei în care ia naștere exigibilitatea operațiunilor menționate la alin. (1). Decontul special de taxă trebuie depus numai pentru perioadele în care ia naștere exigibilitatea taxei."
— Codul fiscal, art. 324 alin. (2) — D301, decontul special de TVA (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„Persoanele impozabile înregistrate în scopuri de TVA depun declarația recapitulativă numai pentru lunile calendaristice în care ia naștere exigibilitatea taxei..."
— OPANAF 705/2020, anexa 2, pct. 1.2 — D390 (sursă: anaf_surse/opanaf_705_2020_d390.txt)

„Declarația se depune la organul fiscal competent până în data de 30 inclusiv a lunii următoare încheierii perioadei de raportare, declarate pentru depunerea decontului (luna, trimestrul etc.)..."
— OPANAF 2194/2025, pct. 2 — D394 (sursă: anaf_surse/opanaf_2194_2025_d394.txt)

„Declarația informativă D406 se transmite în format electronic, data-limită de transmitere fiind: - ultima zi calendaristică a lunii următoare perioadei de raportare..."
— OPANAF 1783/2021, Anexa 4, pct. 1 — D406/SAF-T (sursă: anaf_surse/opanaf_1783_2021_saft_d406.txt)
:::

Descompus pe declarație:

- **D112** (contribuții sociale, impozit pe venit din salarii) — lunar ca regulă generală, art. 147 alin. (1). Excepție, conform alin. (4): angajatorii mici (venituri sub 100.000 euro și cel mult 3 salariați în medie în anul anterior, printre alte categorii de la art. 80 alin. 2) depun trimestrial — nu e cazul general.
- **D300** (decontul de TVA) — lunar e regula implicită (art. 322 alin. 1). Devine trimestrial doar pentru plătitorii care îndeplinesc condiția de la art. 322 alin. (2) — cifră de afaceri sub plafon în anul precedent și fără achiziții intracomunitare.
- **D301** (decontul special de TVA) — nu e o declarație periodică regulată, ci depusă doar în lunile în care ia naștere exigibilitatea taxei pentru operațiunile vizate (achiziții intracomunitare de anumite persoane, servicii primite din străinătate etc.).
- **D390** (declarația recapitulativă VIES) — la fel, depusă doar pentru lunile calendaristice cu operațiuni intracomunitare reale (livrări/achiziții IC, anumite prestări de servicii) — nu „pe zero" în lunile fără astfel de operațiuni.
- **D394** — periodicitatea urmează explicit periodicitatea decontului de TVA (L/T/S/A), cu termen fix pe ziua 30 (nu 25) a lunii următoare.
- **D406/SAF-T** — lunar doar pentru plătitorii de TVA cu perioadă fiscală lunară; cei cu TVA semestrial/anual sau neplătitorii depun D406 trimestrial (vezi ghidul dedicat SAF-T pentru detalii).

## Ce se greșește în practică

- Se presupune că toate cele șase declarații de mai sus sunt „mereu lunare", fără verificare a periodicității reale de TVA a firmei (multe devin trimestriale).
- Se depune D390 și în lunile fără nicio operațiune intracomunitară, deși legea cere declarația doar pentru lunile cu exigibilitate reală.
- Se confundă termenul D394 (ziua 30) cu termenul standard de 25 folosit de restul declarațiilor.
- Se ignoră că D112 poate deveni trimestrial pentru anumite categorii de angajatori mici, tratându-l ca fiind mereu lunar.

## Ce face iConta.eu

iConta.eu generează prin ecranul „Declarații" un set de 9 tipuri de declarații parametrizate pe an/lună/trimestru (D100, D101, D112, D205, D300, D301, D390, D394, D406) — dintre acestea, șase au periodicitate lunară statică în registrul intern al aplicației (D112, D300, D301, D390, D394, D406), dar pentru setul legat de TVA (D300, D394, D406), periodicitatea afișată efectiv urmează periodicitatea reală a firmei (câmpul din Vector fiscal), nu o listă fixă. Aplicația **nu produce un calendar consolidat „ce am de depus luna asta"** din acest ecran — acela e rolul Semaforului de conformare fiscală, care compară declarațiile efectiv datorate (calculate din vectorul fiscal al firmei) cu cele deja depuse. Există și alte 41 de tipuri de declarații pe care aplicația le poate genera, dar doar la cerere directă (nu prin acest selector lunar/trimestrial/anual), unele dintre ele având și ele periodicitate lunară — nu apar automat în lista de mai sus.

[iConta.eu](/)
