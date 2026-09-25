---
title: "Se plătesc dobânzi și penalități pentru impozitul pe profit declarat cu întârziere?"
description: "Nivelul dobânzii și al penalității de întârziere prevăzute de Codul de procedură fiscală, aplicabile și impozitului pe profit neachitat la scadență."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Se plătesc dobânzi și penalități pentru impozitul pe profit declarat cu întârziere?

Răspunsul scurt e da, iar mecanismul e dublu: pentru orice zi de întârziere la plata unei creanțe fiscale, inclusiv impozitul pe profit, se datorează atât dobândă, cât și penalitate de întârziere — două sume distincte, calculate separat, care se cumulează.

## Temeiul legal

```
::: ghid-temei
„ART. 174 Dobânzi
(1) Dobânzile se calculează pentru fiecare zi de întârziere, începând cu ziua imediat următoare termenului de scadență și până la data stingerii sumei datorate, inclusiv. [...]
(5) Nivelul dobânzii este de 0,02% pentru fiecare zi de întârziere.
ART. 176 Penalități de întârziere
(1) Penalitățile de întârziere se calculează pentru fiecare zi de întârziere, începând cu ziua imediat următoare termenului de scadență și până la data stingerii sumei datorate, inclusiv. [...]
(2) Nivelul penalității de întârziere este de 0,01% pentru fiecare zi de întârziere."
— Legea nr. 207/2015 privind Codul de procedură fiscală, art. 174 alin. (1) și (5), art. 176 alin. (1) și (2) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::
```

Ce rezultă din text, aplicat la impozitul pe profit:

- **Dobânda e de 0,02% pe zi de întârziere**, iar **penalitatea de întârziere e de 0,01% pe zi** — se calculează separat, ambele curgând din ziua imediat următoare scadenței până la data stingerii integrale a sumei.
- **Penalitatea nu înlătură obligația de plată a dobânzii** (art. 176 alin. (3)) — cele două se cumulează, nu se aplică una în locul celeilalte.
- Pentru **impozitele cu perioadă fiscală anuală** (categorie în care intră impozitul pe profit), există o regulă specială la art. 175: dobânzile pentru plățile anticipate neachitate se calculează diferit față de diferența rămasă de plată conform declarației anuale — inclusiv o regulă distinctă pentru cazul în care declarația de impunere anuală nu a fost depusă la termen, situație în care dobânda curge de la 1 ianuarie a anului următor celui de impunere.
- Penalitatea de întârziere **nu se aplică** pentru obligațiile fiscale principale pentru care se datorează deja penalitate de nedeclarare, potrivit art. 181 — o regulă anti-cumul care evită dubla sancționare a aceleiași fapte.

## Ce se greșește în practică

- Se calculează doar dobânda, omițând penalitatea de întârziere — sau invers — deși legea le prevede cumulativ, ca sume distincte.
- Se calculează dobânda pentru impozitul pe profit ca pentru orice altă obligație curentă, ignorând regula specială de la art. 175 pentru impozitele cu perioadă fiscală anuală, care schimbă momentul de la care curge dobânda în funcție de situație (plăți anticipate, diferențe din decizia anuală, nedepunerea declarației).
- Se presupune că penalitatea de întârziere se aplică suplimentar față de penalitatea de nedeclarare pentru aceeași obligație — legea exclude expres acest cumul.

## Ce face iConta.eu

Modulul `core/d101.py` și modulele conexe de reconciliere (`core/d101_reconciliere.py`) gestionează declararea impozitului pe profit; calculul automat al dobânzilor și penalităților de întârziere pentru o eventuală plată tardivă **nu a fost găsit** ca funcționalitate dedicată în `core/` — aplicația oferă evidența declarațiilor și a termenelor de plată, dar calculul accesoriilor pentru o întârziere efectivă rămâne, la acest moment, o operațiune pe care contabilul o face separat, pe baza numărului exact de zile de întârziere.

[iConta.eu](/)
