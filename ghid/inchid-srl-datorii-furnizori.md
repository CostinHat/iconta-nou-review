---
title: Cum închid un SRL cu datorii către furnizori?
description: Ce presupune stingerea pasivului față de furnizori la lichidare și de ce, dacă datoriile nu pot fi acoperite, procedura poate depăși cadrul obișnuit al Legii 31/1990.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum închid un SRL cu datorii către furnizori?

Datoriile către furnizori rămase la data dizolvării nu dispar odată cu decizia de lichidare — stingerea lor este, dimpotrivă, condiția pentru a putea trece la partajul dintre asociați.

## Temeiul legal

::: ghid-temei
asociații pot hotărî, o dată cu dizolvarea, „modul de lichidare a societății, atunci când sunt de acord cu privire la repartizarea și lichidarea patrimoniului societății și când asigură stingerea pasivului sau regularizarea lui în acord cu creditorii."
— L31/1990, art. 235 alin. (1)
:::

Lichidarea simplificată, pe acord unanim al asociaților, este condiționată explicit de stingerea pasivului sau de o înțelegere cu creditorii — inclusiv furnizorii. Doar dacă acest lucru este asigurat se poate merge mai departe la repartizarea activelor rămase.

## Ce se greșește în practică

Se presupune uneori că, dacă datoriile către furnizori nu pot fi acoperite integral din activele disponibile, procedura rămâne oricum cea „simplă" descrisă de art. 235 din Legea 31/1990. Legea prevede însă că, în lipsa acordului unanim privind împărțirea bunurilor sau a stingerii pasivului, „va fi urmată procedura lichidării prevăzută de prezenta lege" — adică procedura de drept comun, mai formală, cu numire de lichidator și termene stricte (art. 260). Iar dacă societatea îndeplinește condițiile de insolvență, radierea se poate face pe temeiul Legii nr. 85/2014, la care Legea 31/1990 trimite explicit pentru acest caz (art. 260 alin. 10).

**Notă de transparență:** textul integral al Legii 85/2014 (legea insolvenței) nu a fost disponibil în dosarul de cercetare folosit la redactarea acestui ghid, deci nu putem cita aici prevederi specifice din ea. Dacă datoriile către furnizori depășesc activele disponibile ale societății și există risc de insolvență, procedura corectă (reorganizare judiciară sau faliment) trebuie stabilită împreună cu un practician în insolvență sau consilier juridic — nu poate fi acoperită integral doar prin operațiunile contabile din aplicație.

## Ce face iConta.eu

Datoriile către furnizori se sting, în cursul lichidării, prin operațiunile obișnuite de plată din aplicație, la fel ca înainte de deschiderea procedurii — societatea își păstrează personalitatea juridică pentru aceste operațiuni până la terminarea lichidării (L31/1990, art. 233 alin. 4). Motorul dedicat de lichidare (`core/lichidare.py`, F057) intervine abia la etapele de valorificare a activelor (`nota_vanzare_activ`) și de partaj final (`partaj`) — stingerea datoriilor curente către furnizori nu are o funcție separată în acest motor, ci urmează fluxul normal de plăți.

[iConta.eu](/)
