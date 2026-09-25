---
title: "Cum verific dacă o declarație rectificativă a înlocuit declarația inițială?"
description: "Cine confirmă legal că o declarație rectificativă a înlocuit-o pe cea inițială, și de ce acest pas rămâne pe portalul ANAF, nu în aplicația de contabilitate."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum verific dacă o declarație rectificativă a înlocuit declarația inițială?

După ce depui o declarație rectificativă — inclusiv o 710 — vrei confirmarea că ANAF a înregistrat-o și că ea a înlocuit efectiv datele declarate greșit anterior. Legea leagă acest moment de un act concret: confirmarea de primire transmisă de sistemul ANAF la depunerea electronică.

## Temeiul legal

::: ghid-temei
„(3) Data depunerii declarației fiscale este data înregistrării acesteia la organul fiscal [...]. În situația în care declarația fiscală se depune prin mijloace electronice de transmitere la distanță, data depunerii declarației este data înregistrării acesteia pe pagina de internet a organului fiscal, astfel cum rezultă din mesajul electronic de confirmare transmis ca urmare a primirii declarației. (4) [...] cu condiția validării conținutului declarației. În cazul în care declarația nu este validată, data depunerii declarației este data validării astfel cum rezultă din mesajul electronic."
— Codul de procedură fiscală (Legea 207/2015), art. 103 alin. (3)-(4) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

- Confirmarea legală că o declarație (inclusiv o rectificativă) a fost primită și validată e un **mesaj electronic emis de sistemul ANAF**, nu o presupunere bazată pe faptul că ai apăsat „trimite".
- Dacă declarația nu e validată la transmitere, data depunerii se mută la data la care ANAF confirmă efectiv validarea — deci confirmarea nu e automată doar prin trimitere, ci depinde de răspunsul sistemului.
- Declarația rectificativă, ca orice altă declarație, se supune acelorași reguli de depunere (art. 103) — nu există un mecanism legal separat, „mai rapid", de confirmare pentru rectificative.

## Ce se greșește în practică

- Se presupune că generarea și trimiterea fișierului XML către ANAF înseamnă automat că declarația a fost acceptată și a înlocuit-o pe cea inițială — fără mesajul de confirmare/validare, acest lucru nu e garantat.
- Se ignoră situația în care declarația a fost respinsă la validare (erori de conținut) — data depunerii se schimbă, iar rectificativa „depusă" tehnic poate să nu fi înlocuit nimic legal, până la o depunere validă.
- Se caută confirmarea în afara portalului ANAF (SPV), deși ea e emisă exclusiv de acolo.

## Ce face iConta.eu

Pentru declarația 710, iConta.eu generează XML-ul corecției și îl rulează prin validatorul oficial ANAF (DUK) — care confirmă doar dacă structura declarației e validă, nu dacă ANAF a primit și a înregistrat efectiv depunerea. iConta.eu **nu transmite automat** declarația către SPV și **nu interoghează** starea ei ulterioară la ANAF — nu există în aplicație niciun apel către un serviciu de confirmare a depunerii pentru D710 sau pentru celelalte declarații generice. Confirmarea că o rectificativă a înlocuit declarația inițială se obține exclusiv din portalul SPV al ANAF, în afara iConta.eu, unde contribuabilul depune el însuși declarația generată și primește mesajul electronic de confirmare prevăzut de lege.

[iConta.eu](/)
