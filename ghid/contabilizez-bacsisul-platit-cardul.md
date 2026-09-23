---
title: Cum contabilizez bacșișul plătit cu cardul?
description: Bacșișul cu cardul urmează exact același traseu ca cel în numerar — doar contul de trezorerie diferă. Fluxul complet, de la încasare la distribuire.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum contabilizez bacșișul plătit cu cardul?

Legea nu face nicio diferență de tratament fiscal între bacșișul plătit cu cardul și cel în numerar — singura diferență e contul de trezorerie folosit la încasare. Restul fluxului (evidențiere distinctă, distribuire integrală, impozitare la salariat) e identic.

## Temeiul legal

::: ghid-temei
„Sumele provenite din încasarea bacșișului se înregistrează în contabilitatea operatorilor economici pe seama conturilor de datorii folosind un analitic distinct și se distribuie integral salariaților, pe baza unei evidențe nominale a acestora."

*(Legea nr. 376/2022 pentru modificarea și completarea OUG nr. 28/1999, art. 2^3 alin. (8))*
:::

Legea cere, la alin. (2), evidențierea bacșișului pe bonul fiscal indiferent de modalitatea de încasare — card sau numerar. Diferența dintre cele două e strict la nivelul contului de trezorerie folosit, nu la tratamentul contabil sau fiscal de fond, care rămâne cel de la alin. (8) de mai sus.

## Fluxul de înregistrare

**1. Încasarea cu cardul.** Bacșișul ales de client (0-15% din consumație sau sumă fixă) e evidențiat distinct pe bonul fiscal. Contabil: `461 = 462` (creanța internă pentru bacșișul de distribuit), apoi `5121 = 461` (încasarea efectivă în contul bancar, prin POS) — spre deosebire de numerar, unde încasarea merge prin `5311`.

**2. Distribuirea.** Pe baza regulamentului intern și a evidenței nominale a angajaților, bacșișul brut se distribuie integral, cu impozit reținut la sursă: `462 = 446` (impozitul de 10%) și `462 = 5121/5311` (netul plătit salariatului, indiferent de contul din care s-a încasat inițial).

Exemplu numeric: un bacșiș brut de 100 lei, încasat cu cardul, generează un impozit de 10,00 lei (cont `446`) și un net de 90,00 lei către salariat.

## Ce se greșește în practică

Cea mai frecventă confuzie e presupunerea că bacșișul cu cardul, fiind „vizibil" în extrasul bancar odată cu restul încasării POS, nu mai trebuie separat pe un analitic distinct de datorii — el rămâne totuși supus acelorași reguli de la alin. (8)-(9): analitic distinct, fără trecere prin venituri, distribuire integrală nominală.

## Ce face iConta.eu

Funcția `nota_incasare(bacsis, sursa="card")` din modulul F010 (`core/bacsis.py`) generează automat nota corectă pentru bacșișul cu cardul (`461=462`, `5121=461`), diferențiată de varianta cu numerar (`sursa="numerar"`, care folosește `5311`) doar prin contul de trezorerie. Distribuirea ulterioară, prin `nota_distribuire`, e identică indiferent de sursa de încasare.

[iConta.eu](/)
