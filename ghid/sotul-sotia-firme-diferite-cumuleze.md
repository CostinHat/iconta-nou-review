---
title: "Soțul și soția cu firme diferite trebuie să cumuleze veniturile pentru plafonul micro?"
description: "Cumularea veniturilor pentru verificarea plafonului micro depinde de raporturile de deținere dintre firme, nu de relația de familie dintre asociați."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Soțul și soția cu firme diferite trebuie să cumuleze veniturile pentru plafonul micro?

Nu automat. Legea nu cumulează veniturile a două firme doar pentru că asociații lor sunt căsătoriți — cumularea se aplică doar dacă firmele sunt „legate" printr-un raport de deținere de peste 25%, definit explicit de Codul fiscal, indiferent de relația personală dintre proprietari.

## Temeiul legal

::: ghid-temei
„În aplicarea prevederilor alin. (1) lit. c) limita privind veniturile realizate se verifică luând în calcul veniturile realizate de persoana juridică română, cumulate cu veniturile întreprinderilor legate cu aceasta [...] persoana juridică română este legată cu o altă persoană dacă există oricare dintre următoarele raporturi: a) persoana juridică română care verifică condiția deține la o altă persoană juridică română, direct și/sau indirect, peste 25% din valoarea/numărul titlurilor de participare sau al drepturilor de vot [...]"
— Legea 227/2015 (Codul fiscal), art. 47 alin. (1^1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce înseamnă, concret, „întreprinderi legate" pentru verificarea plafonului de 100.000 euro:

- Cumularea se aplică între firme unde una deține, direct sau indirect, peste 25% din cealaltă (lit. a-b), sau unde aceeași persoană deține peste 25% în ambele firme (lit. c) — indiferent cine e acea persoană.
- Există și o regulă specifică pentru asociați care au și o activitate independentă (PFA/II/întreprindere familială) alături de firmă (lit. d) — veniturile din acea activitate independentă se cumulează cu cele ale firmei.
- Legea nu prevede vreo regulă de cumulare bazată exclusiv pe faptul că doi asociați ai unor firme diferite sunt soț și soție — dacă niciuna dintre firme nu deține peste 25% din cealaltă, iar soțul și soția nu au fiecare, individual, peste 25% în ambele firme, cumularea din art. 47 alin. (1^1) nu se declanșează pe acest temei.

## Ce se greșește în practică

- Se presupune, din prudență, că orice firme deținute de soț și soție trebuie automat cumulate pentru plafonul micro — legea cere un raport de deținere de peste 25% între firme sau al aceleiași persoane în ambele, nu doar o relație de familie.
- Se ignoră situația inversă: dacă unul dintre soți deține peste 25% în ambele firme (nu doar în una), cumularea se aplică — indiferent cine e „celălalt" asociat.
- Se confundă regula de cumulare a veniturilor pentru plafonul micro cu regulile de „persoane afiliate" folosite la prețurile de transfer (art. 7 pct. 26) — sunt definiții diferite, pentru scopuri diferite ale Codului fiscal.

## Ce face iConta.eu

La data acestui ghid, iConta.eu nu are un modul care să verifice automat raporturile de deținere dintre firme diferite și să cumuleze veniturile pentru testul plafonului micro — aplicația calculează impozitul micro (`core/d100.py`) pe baza veniturilor introduse pentru firma respectivă, tratată individual. Verificarea existenței unei relații de „întreprindere legată" cu o altă firmă, potrivit art. 47 alin. (1^1), rămâne o analiză pe care contabilul o face manual, pe baza structurii acționariatului.

[iConta.eu](/)
