---
title: "Se declară avansurile în D394?"
description: "Tratamentul facturilor de avans în declarația 394, cu temeiul legal explicit și modul în care iConta.eu le include în calcul."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Se declară avansurile în D394?

Un avans facturat nu e o operațiune „provizorie" din perspectiva D394 — din momentul în care s-a emis o factură, obligația de declarare există, indiferent dacă marfa sau serviciul urmează să fie livrate ulterior.

## Temeiul legal

::: ghid-temei
„Declaraţia se depune pentru orice operaţiune taxabilă în România pentru care, conform titlului VII din Codul fiscal, este emisă o factură, inclusiv pentru avansuri, precum şi pentru operaţiunile la care se aplică sistemul TVA la încasare."
— OPANAF 2194/2025, Anexa 2 pct.1 (sursă: anaf_surse/opanaf_2194_2025_d394.txt:721-723)
:::

- Regula e clară și explicită: „inclusiv pentru avansuri" — nu există o excepție sau o amânare a declarării până la factura finală de livrare/prestare.
- Aceeași frază leagă avansurile de operațiunile cu TVA la încasare: ambele intră în declarație la data emiterii facturii, nu la data exigibilității efective a TVA.
- Declarația trebuie să conțină facturile emise în perioada de raportare „indiferent de data la care intervine exigibilitatea TVA" — deci o factură de avans emisă în luna X se declară în luna X, chiar dacă TVA devine exigibilă abia la livrarea finală (de exemplu, în regim de TVA la încasare).

## Ce se greșește în practică

- Se amână declararea unei facturi de avans până la emiterea facturii finale, crezând că doar „factura completă" trebuie raportată.
- Se omite avansul din D394 pentru firmele la TVA la încasare, pe motiv că TVA nu e încă exigibilă — dar declarația urmărește data emiterii facturii, nu exigibilitatea.
- Se dublează valoarea la factura finală, incluzând din nou baza avansului deja declarată separat, în loc să se declare doar diferența rămasă.

## Ce face iConta.eu

Generatorul D394 (`core/d394.py`, cu datele preluate din `core/repo_d394.py`) nu tratează facturile de avans ca o categorie separată, pentru că legea nu cere asta — orice factură emisă din tabela de facturi a firmei, indiferent dacă e de avans sau finală, intră în calculul bazei și al TVA pe tipul de operațiune corespunzător (L pentru livrări, A pentru achiziții etc.), exact ca orice altă factură. Nu există niciun filtru care să excludă documentele marcate ca avans — ele urmează același flux de agregare pe cotă de TVA ca restul facturilor emise în perioada de raportare.

[iConta.eu](/)
