---
title: Am înregistrat greșit bacșișul din POS
description: Cea mai frecventă greșeală la bacșișul încasat prin POS este trecerea lui prin veniturile firmei. Cum recunoști eroarea și cum o corectezi, cont cu cont.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Am înregistrat greșit bacșișul din POS

Bacșișul încasat prin POS (card) urmează, ca și cel în numerar, un traseu fix prin conturi de datorii — niciodată prin conturile de venituri ale firmei. Cea mai comună greșeală e exact aceasta: suma bacșișului rămâne „lipită" de încasarea POS și ajunge, fără să vrei, în cifra de afaceri sau în baza de TVA.

## Temeiul legal

::: ghid-temei
„sumele provenite din încasarea bacșișului de la client de către operatorul economic nu pot fi asimilate unui element de natura veniturilor pentru acesta din urmă, iar distribuirea acestora către salariați nu poate fi asimilată unui element de natura cheltuielilor."

*(Legea nr. 376/2022 pentru modificarea și completarea OUG nr. 28/1999, art. 2^3 alin. (9))*
:::

## Cum arată greșeala

Cel mai des, bacșișul încasat cu cardul e contabilizat împreună cu restul încasării POS, într-o singură notă `5121 = 4111` sau direct prin cont de venituri, fără să fie separat pe un analitic distinct de datorii. Rezultatul: bacșișul intră greșit în baza de calcul a TVA sau a impozitului pe profit/venit al firmei, deși legea îl exclude explicit din sfera veniturilor (alin. (9) de mai sus).

## Cum corectezi

1. **Identifici suma de bacșiș** din totalul încasat prin POS pentru perioada respectivă (de regulă vizibilă distinct pe bonul fiscal, conform obligației de evidențiere separată — alin. (2) din aceeași lege).
2. **Stornezi înregistrarea greșită** — scoți bacșișul din contul de venituri (sau din nota unică de încasare POS) unde a ajuns din greșeală.
3. **Reînregistrezi corect, pe traseul de datorii**: `461 = 462` (creanța internă pentru bacșișul de distribuit), apoi `5121 = 461` (încasarea efectivă prin card).
4. **Distribui bacșișul integral către salariați**, conform regulamentului intern: `462 = 446` (impozitul de 10% reținut la sursă) și `462 = 5121/5311` (netul plătit).

## Ce se greșește în practică

- Bacșișul cu cardul e confundat cu restul încasării POS și trece direct prin venituri, fără analitic distinct.
- Corecția se face doar prin ajustarea cifrei de afaceri (pentru TVA), fără să se mai reconstituie și pasul de distribuire integrală către salariați — cele două corecții trebuie făcute împreună.
- Bacșișul e lăsat în soldul de casă/bancă al firmei fără nicio urmă contabilă a obligației de distribuire (cont `462`), ceea ce contrazice cerința de evidență nominală și distribuire integrală.

## Ce face iConta.eu

Modulul F010 (`core/bacsis.py`) separă explicit cele două operațiuni: `nota_incasare(bacsis, sursa="card")` generează întotdeauna `461=462` + `5121=461`, niciodată o notă care amestecă bacșișul cu venitul din vânzare. Funcția respinge orice sumă mai mică sau egală cu zero, cu un mesaj dedicat, ca să nu ajungă „bacșiș fantomă" în evidență. Pentru corectarea unei înregistrări greșite deja introduse, stornarea rămâne un pas manual — aplicația nu detectează automat o încasare de bacșiș trecută anterior prin alt cont.

[iConta.eu](/)
