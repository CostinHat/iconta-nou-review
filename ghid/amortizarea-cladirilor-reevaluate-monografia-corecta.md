---
title: "Amortizarea clădirilor reevaluate: monografia corectă"
description: O clădire complet amortizată, reevaluată, nu primește o durată rămasă "din oficiu" — evaluatorul o stabilește explicit, iar amortizarea repornește, pe valoarea justă, din luna următoare reevaluării.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Amortizarea clădirilor reevaluate: monografia corectă

Pentru o clădire complet (sau aproape complet) amortizată, monografia reevaluării are un pas suplimentar față de cazul general: durata de utilizare rămasă nu rezultă dintr-un calcul automat — trebuie stabilită explicit, odată cu noua valoare.

## Temeiul legal

::: ghid-temei
"Dacă o imobilizare corporală complet amortizată mai poate fi folosită, entitatea poate proceda la reevaluarea acesteia. Cu ocazia reevaluării imobilizării corporale, acesteia i se stabilesc o nouă valoare și o nouă durată de utilizare economică, corespunzătoare perioadei estimate a se folosi în continuare." — OMFP 1802/2014, pct. 100
:::

Monografia, aplicată unei clădiri (cont 212, amortizare cont 2812/2813, după caz):

1. **Eliminarea amortizării cumulate**: 2812 = 212, pentru toată amortizarea strânsă până la data reevaluării.
2. **Stabilirea noii valori și a noii durate**, pe baza raportului evaluatorului — norma cere explicit ambele elemente (pct. 100), nu doar valoarea justă.
3. **Înregistrarea diferenței**, pe rezervă/venit/cheltuială, după regula generală creștere/scădere (OMFP 1802/2014 pct. 111 alin. (1)-(2); tipic, la o clădire veche reevaluată în plus, întreaga creștere merge pe 212 = 105, dacă nu a existat o descreștere anterioară recunoscută pe 655).
4. **Amortizare nouă**, liniară (obligatoriu pentru construcții — Legea 227/2015, art. 28 alin. (5) lit. a), calculată pe valoarea justă și pe durata rămasă stabilită la pasul 2, începând din luna următoare celei în care reevaluarea produce efect (art. 28 alin. (12) lit. a).

Fiscal, rezerva astfel constituită (105) nu e "gratuită" pe termen lung: devine impozabilă pe măsură ce se consumă prin amortizarea fiscală ulterioară sau integral la scoaterea clădirii din evidență (Legea 227/2015, art. 26 alin. (6)).

## Ce se greșește în practică

- Se citează pct. 113 din OMFP 1802/2014 ca temei pentru stabilirea noii durate — citarea corectă e **pct. 100**; pct. 113 vorbește despre limitele reducerii rezervei din reevaluare, subiect diferit.
- Se continuă amortizarea pe o "durată rămasă" dedusă automat dintr-o formulă internă, fără raport de evaluare care s-o stabilească explicit.
- Se pornește amortizarea nouă din luna reevaluării, nu din luna următoare validării ei.
- Se ignoră impozitarea ulterioară a rezervei constituite (art. 26 alin. (6)), tratând-o ca pe o sumă definitiv scutită.

## Ce face iConta.eu

Când o clădire cu durata normală de amortizare deja epuizată e trimisă la reevaluare, aplicația nu fabrică o durată rămasă implicită — refuză operațiunea și cere introducerea duratei rămase stabilite prin raportul evaluatorului, tocmai pentru a respecta pct. 100. Odată introdusă, motorul de amortizare taie durata în etape (etapa veche, epuizată la data reevaluării, și etapa nouă pe valoarea justă) și calculează corect amortizarea lunară a etapei noi, începând din luna următoare.

[iConta.eu](/)
