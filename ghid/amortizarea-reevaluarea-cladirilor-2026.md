---
title: Amortizarea după reevaluarea clădirilor 2026
description: O clădire complet sau aproape amortizată, reevaluată, primește o nouă durată de utilizare — stabilită de evaluator, nu calculată automat — și se amortizează liniar pe valoarea justă, de la luna următoare reevaluării.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Amortizarea după reevaluarea clădirilor 2026

Clădirile vechi, complet sau aproape amortizate, sunt cazul tipic în care reevaluarea produce un efect vizibil asupra amortizării: pentru că durata inițială e epuizată (sau aproape), norma cere ca reevaluarea să vină la pachet cu o nouă durată de utilizare — nu doar cu o nouă valoare.

## Temeiul legal

::: ghid-temei
"Dacă o imobilizare corporală complet amortizată mai poate fi folosită, entitatea poate proceda la reevaluarea acesteia. Cu ocazia reevaluării imobilizării corporale, acesteia i se stabilesc o nouă valoare și o nouă durată de utilizare economică, corespunzătoare perioadei estimate a se folosi în continuare." — OMFP 1802/2014, pct. 100
:::

Pentru clădiri, câteva reguli se combină:

- **Regimul de amortizare rămâne liniar**, obligatoriu — construcțiile nu au opțiunea degresiv/accelerat (Legea 227/2015, art. 28 alin. (5) lit. a).
- **Noua durată** nu se calculează automat dintr-o formulă internă — pct. 100 cere o durată "corespunzătoare perioadei estimate a se folosi în continuare", ceea ce, în practică, vine din raportul evaluatorului autorizat care a stabilit și valoarea justă (OMFP 1802/2014 pct. 102).
- **Amortizarea pe noua bază** începe abia din luna următoare celei în care se aplică reevaluarea, nu din luna reevaluării în sine (Legea 227/2015, art. 28 alin. (12) lit. a).
- **Reevaluarea nu schimbă vechimea reală a clădirii** — data punerii în funcțiune inițială rămâne aceeași. O clădire veche, reevaluată în 2026, nu devine eligibilă pentru regimul accelerat/superaccelerat introdus pentru active noi (Legea 227/2015, art. 28 alin. (8^1), rezervat activelor din subgrupele vizate, puse în funcțiune în 2026) — reevaluarea schimbă valoarea, nu data de intrare în patrimoniu.

## Ce se greșește în practică

- Se citează pct. 113 din OMFP 1802/2014 pentru stabilirea noii durate de amortizare la o clădire complet amortizată — pct. 113 tratează cu totul alt subiect (limitele reducerii rezervei din reevaluare). Temeiul corect pentru "nouă valoare și nouă durată" e **pct. 100**.
- Se presupune că o clădire veche, reevaluată în 2026, poate intra la amortizarea superaccelerată 2026 (art. 28 alin. (8^1)) — regimul e rezervat activelor noi, nu unor clădiri vechi cărora li s-a schimbat doar valoarea contabilă.
- Se continuă amortizarea pe durata inițială (deja epuizată), aplicând noua valoare pe o durată rămasă "zero" sau fabricată arbitrar — fără raportul evaluatorului care stabilește efectiv noua durată rămasă.

## Ce face iConta.eu

Motorul de amortizare recunoaște reevaluarea drept o etapă nouă în viața activului: taie durata normală în etape, consumă lunile scurse până la reevaluare, apoi pornește etapa nouă pe valoarea justă. Dacă durata normală era deja epuizată la data reevaluării (cazul tipic al clădirilor complet amortizate), aplicația nu fabrică o durată rămasă "rezonabilă" — refuză continuarea și cere introducerea duratei stabilite prin raportul evaluatorului. Amortizarea lunii reevaluării intră deja în etapa nouă, conform art. 28 alin. (12) lit. a).

[iConta.eu](/)
