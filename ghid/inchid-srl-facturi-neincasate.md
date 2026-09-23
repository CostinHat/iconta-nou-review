---
title: Cum închid un SRL cu facturi neîncasate?
description: Ce se întâmplă cu creanțele neîncasate la lichidare și de ce încasarea lor rămâne o etapă obligatorie înainte de radiere.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum închid un SRL cu facturi neîncasate?

Facturile emise și neîncasate până la data dizolvării nu se anulează automat — creanțele societății fac parte din patrimoniul care trebuie lichidat, iar încasarea lor este una dintre atribuțiile explicite ale lichidatorilor.

## Temeiul legal

::: ghid-temei
„lichidatorii pot [...] «să lichideze și să încaseze creanțele societății»"
— L31/1990, art. 255 alin. (1) lit. e) (citat în dosarul de cercetare F057)
:::

La finalul procesului, situația creanțelor trebuie prezentată explicit în raportul final:

::: ghid-temei
„În termen de 15 zile de la terminarea lichidării, lichidatorii vor depune la registrul comerțului cererea de radiere a societății [...], pe baza raportului final de lichidare și a situațiilor financiare de lichidare prin care se prezintă situația patrimoniului, a creanțelor și repartizarea activelor rămase [...]."
— L31/1990, art. 260 alin. (6)
:::

## Ce se greșește în practică

Se crede uneori că, odată deschisă procedura de lichidare, societatea nu mai poate acționa normal pentru recuperarea creanțelor (somații, acțiuni în instanță, negocieri cu debitorii). Legea spune contrariul: societatea „își păstrează personalitatea juridică pentru operațiunile lichidării, până la terminarea acesteia" (L31/1990, art. 233 alin. 4), deci încasarea facturilor restante rămâne o activitate legitimă și necesară în această perioadă, nu o excepție.

## Ce face iConta.eu

Dosarul de cercetare pentru F057 nu a găsit, în motorul de lichidare (`core/lichidare.py`), o funcție dedicată separată pentru încasarea creanțelor — acesta acoperă doar vânzarea activelor imobilizate (`nota_vanzare_activ`) și partajul final (`partaj`). Încasarea facturilor neîncasate se face, ca înainte de deschiderea lichidării, prin operațiunile obișnuite de încasare din aplicație. Abia după ce toate creanțele recuperabile au fost încasate (sau, după caz, scoase din evidență ca nerecuperabile) se poate întocmi corect situația patrimonială finală și, ulterior, rula operația de partaj.

[iConta.eu](/)
