---
title: "Cum trece o întreprindere individuală de la normă la sistem real?"
description: "Procedura de opțiune pentru determinarea venitului net în sistem real, în locul normei de venit, conform art. 69^1 din Codul fiscal."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum trece o întreprindere individuală de la normă la sistem real?

Trecerea nu se face „din oficiu" și nu se poate răzgândi de pe o lună pe alta — legea o tratează ca pe o opțiune formală, cu o depunere explicită și un angajament de minimum doi ani.

## Temeiul legal

::: ghid-temei
„Articolul 69^1 Opțiunea de a stabili venitul net anual, în sistem real pe baza datelor din contabilitate
(1) Contribuabilii care obțin venituri din activități independente, impuși pe bază de norme de venit, au dreptul să opteze pentru determinarea venitului net în sistem real, potrivit art. 68.
(2) Opțiunea de a determina venitul net în sistem real, pe baza datelor din contabilitate, potrivit prevederilor art. 68, este obligatorie pentru contribuabil pe o perioadă de 2 ani fiscali consecutivi și se consideră reînnoită pentru o nouă perioadă dacă contribuabilul nu solicită revenirea la sistemul anterior. [...]
(3) Opțiunea pentru determinarea venitului net anual în sistem real, inclusiv în cazul contribuabililor care încep activitatea în cursul anului fiscal, se exercită prin completarea Declarației unice privind impozitul pe venit și contribuțiile sociale datorate de persoanele fizice cu informații privind determinarea venitului net anual în sistem real și depunerea formularului la organul fiscal competent în termenul legal de depunere prevăzut la art. 122 alin. (3)."
— Legea 227/2015 (Codul fiscal), art. 69^1 alin. (1)-(3) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Pașii concreți ai trecerii:

1. **Se completează Declarația Unică** (formularul 212) cu secțiunea corespunzătoare determinării venitului net în sistem real, în locul secțiunii de normă de venit.
2. **Se depune la termenul legal** prevăzut la art. 122 alin. (3) din Codul fiscal — termenul general de depunere a Declarației Unice (de regulă, 25 mai a anului următor celui de realizare a veniturilor pentru care se face opțiunea inițială, sau termenul specific pentru contribuabilii care încep activitatea în cursul anului).
3. **Angajamentul e de minimum 2 ani fiscali consecutivi** — odată exercitată opțiunea, nu se poate reveni la normă de venit înainte de expirarea acestei perioade.
4. **După cei 2 ani**, opțiunea se reînnoiește automat, an de an, dacă titularul nu solicită explicit revenirea la normă de venit — revenirea se face tot prin Declarația Unică, la termenul aferent anului următor expirării perioadei de 2 ani.
5. **Pentru cine începe activitatea în cursul anului**, opțiunea se poate exercita din primul an — perioada de 2 ani include chiar anul de start al activității și anul fiscal următor.

## Ce se greșește în practică

- Se depune opțiunea pentru sistem real, dar se dorește revenirea la normă de venit după un singur an — legea impune un angajament minim de 2 ani fiscali consecutivi, indiferent de motivul dorinței de revenire.
- Se presupune că opțiunea se poate exercita oricând în cursul anului — termenul e fix, legat de termenul de depunere a Declarației Unice (art. 122 alin. 3), nu de o dată aleasă de contribuabil.
- Se ignoră reînnoirea automată a opțiunii — dacă la expirarea celor 2 ani nu se depune explicit cererea de revenire la normă de venit, sistemul real continuă să se aplice implicit, pentru o nouă perioadă.

## Ce face iConta.eu

Generatorul Declarației 212 din iConta.eu (`core/d212.py`) tratează distinct capitolele de venit realizat pe sistem real (cap. 11) și pe normă de venit (cap. 12), permițând completarea corectă a formularului în funcție de regimul ales. La data acestui ghid, aplicația **nu urmărește automat perioada de angajament de 2 ani** impusă de art. 69^1 alin. (2) — contabilul rămâne responsabil să verifice dacă titularul poate reveni legal la normă de venit sau dacă se află încă în perioada obligatorie de aplicare a sistemului real, înainte de a completa declarația corespunzătoare.

[iConta.eu](/)
