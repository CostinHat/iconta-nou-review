---
title: Cine poate aplica sistemul TVA la încasare?
description: Sistemul e deschis firmelor înregistrate în scopuri de TVA, cu sediul activității economice în România, aflate sub plafonul valabil — dar legea exclude explicit membrii unui grup fiscal unic, firmele nestabilite în România și cele care au depășit deja plafonul.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cine poate aplica sistemul TVA la încasare?

Nu orice firmă sub plafonul de cifră de afaceri poate opta pentru TVA la încasare — legea pune, pe lângă condiția de plafon, câteva condiții pozitive și câteva excluderi explicite, iar ambele contează la fel de mult.

## Temeiul legal

::: ghid-temei
**Art. 282 alin. (3) din Codul fiscal (Legea 227/2015)**: *„...exigibilitatea taxei intervine la data încasării contravalorii integrale sau parțiale a livrării de bunuri ori a prestării de servicii, în cazul persoanelor impozabile care optează în acest sens..."*

**Art. 282 alin. (3^1) CF** (rezumat din dosarul de cercetare, fără text exact citat în sursă): sunt eligibile persoanele impozabile înregistrate în scopuri de TVA conform art. 316, cu sediul activității economice în România (art. 266 alin. (2) lit. a)), a căror cifră de afaceri din anul calendaristic precedent nu a depășit plafonul aplicabil pentru anul respectiv (lit. a); sau persoanele nou-înregistrate în scopuri de TVA în cursul anului, cu opțiune de la data înregistrării sau ulterior (lit. b).

**Art. 282 alin. (4) CF** (rezumat din dosar): nu sunt eligibile — membrii unui grup fiscal unic (lit. a); persoanele nestabilite în România (lit. b); cele care au depășit deja plafonul în anul precedent (lit. c); cele înregistrate în cursul anului cu depășire a plafonului anul precedent sau curent (lit. d).
:::

## Condițiile pozitive

Trei condiții cumulate, pentru firmele deja înregistrate: să fie plătitoare de TVA conform art. 316, să aibă sediul activității economice în România și cifra de afaceri din anul precedent sub plafonul valabil pentru anul intrării. O firmă nou-înregistrată în cursul anului poate opta încă de la data înregistrării în scopuri de TVA sau ulterior.

## Cine e exclus, chiar dacă îndeplinește condițiile de mai sus

Legea exclude explicit patru categorii, indiferent de cifra de afaceri: membrii unui grup fiscal unic, firmele nestabilite în România, cele care au depășit deja plafonul anul precedent, respectiv cele nou-înregistrate în cursul anului care au depășit deja plafonul (fie în anul precedent, fie în cel curent).

## Ce se greșește în practică

- **Se verifică doar cifra de afaceri**, ignorând condițiile de eligibilitate legate de statutul de plătitor de TVA și de sediul activității economice în România.
- **Se ignoră excluderile de la alin. (4)** — mai ales pentru membrii unui grup fiscal unic sau firmele nestabilite în România, care rămân neeligibile chiar dacă cifra de afaceri e sub plafon.
- **Se aplică un plafon fix, indiferent de an**, deși plafonul diferă între perioade (4.500.000 lei până la 29.02.2026, 5.000.000 lei din 01.03.2026, 5.500.000 lei din 01.01.2027).

## Ce face iConta.eu

Eligibilitatea de plafon se verifică pe baza plafonului valabil la data de referință (`plafon_la(data)`, din `core/common.py`). Verificarea celorlalte condiții de eligibilitate — statutul de plătitor de TVA, sediul activității economice, apartenența la un grup fiscal unic — nu e confirmată în acest dosar ca fiind automatizată; rămâne, conform cercetării de față, o verificare manuală a contabilului.

[iConta.eu](/)
