---
title: Cum se tratează avansurile încasate de un PFA?
description: Avansul încasat de un PFA intră integral în venitul brut al anului în care a fost încasat, chiar dacă se referă la un serviciu prestat în alt an fiscal — contabilitatea în partidă simplă e pe bază de casă (cash-basis).
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se tratează avansurile încasate de un PFA?

Un PFA în sistem real conduce contabilitate pe bază de încasări și plăți (cash-basis), nu pe bază de facturare. Asta schimbă fundamental modul în care se tratează un avans: momentul relevant fiscal nu este data facturii sau data prestării serviciului, ci data la care banii ajung efectiv la PFA.

## Temeiul legal

::: ghid-temei
Codul fiscal, art. 68 alin. (1): "Venitul net anual din activități independente se determină în sistem real, pe baza datelor din contabilitate, ca diferență între venitul brut și cheltuielile deductibile efectuate în scopul realizării de venituri ..."

Codul fiscal, art. 68 alin. (2) lit. a): venitul brut cuprinde "sumele încasate și echivalentul în lei al veniturilor în natură din desfășurarea activității".

HG 1/2016 (Norme metodologice), pct. 7 alin. (1): "Potrivit prevederilor art. 68 din Codul fiscal, în venitul brut se includ toate veniturile în bani și în natură, cum ar fi: venituri din vânzarea de produse și de mărfuri, venituri din prestarea de servicii și executarea de lucrări, venituri din vânzarea sau închirierea bunurilor din patrimoniul afacerii, și orice alte venituri obținute din exercitarea activității, inclusiv încasările efectuate în avans care se referă la alte exerciții fiscale, precum și veniturile din dobânzile primite de la bănci pentru disponibilitățile bănești aferente afacerii, din alte activități adiacente și altele asemenea. În venitul brut se includ și veniturile încasate ulterior încetării activității independente, pe baza facturilor emise și neîncasate până la încetarea activității."

OMFP 170/2015, Cap. V, Secțiunea a 2-a: "Încasările din Registrul-jurnal de încasări şi plăți cuprind: - sumele încasate din desfăşurarea activității; ..."
:::

## De ce avansul se impozitează la încasare, nu la prestare

Norma metodologică e explicită: chiar dacă un avans "se referă la alte exerciții fiscale" (adică serviciul sau produsul se livrează abia anul viitor), suma intră în venitul brut al anului în care a fost încasată. Nu există noțiunea de "venit în avans" amânat la un exercițiu următor, așa cum există în contabilitatea de angajamente a societăților.

::: ghid-exemplu
Un PFA încasează pe 20 decembrie 2026 un avans de 6.000 lei pentru un proiect care se execută integral în ianuarie 2027. Cei 6.000 lei se înregistrează ca încasare (categoria "activitate") în Registrul-jurnal la data de 20.12.2026 și intră în venitul brut al anului fiscal 2026, indiferent că serviciul propriu-zis se prestează abia anul următor.
:::

## Ce se greșește în practică

- Se amână înregistrarea avansului până la emiterea facturii finale sau până la finalizarea serviciului, în loc să fie înregistrat la data încasării efective.
- Se consideră avansul "neimpozabil" pentru că nu e "câștigat" încă, prin analogie greșită cu regulile de angajamente de la firme.
- Se confundă avansul de la un client cu un aport al titularului în afacere — sunt categorii complet diferite în registru.
- Nu se păstrează documentul justificativ (contract, proformă, chitanță/extras) care leagă avansul de operațiunea economică.
- Se înregistrează avansul doar în evidența internă a facturării, fără reflectare separată în Registrul-jurnal de încasări și plăți.

## Ce face iConta.eu

În `core/rip_api.py`, orice sumă încasată se înregistrează ca operațiune de tip `incasare`, cu categoria `activitate` din lista validă `CATEGORII_INCASARE = {"activitate", "aport", "credit", "subventie", "alte_incasari"}`. Validarea (`_valideaza`) cere obligatoriu tip, metodă (numerar/bancă), sumă pozitivă, dată și explicație pentru fiecare operațiune — inclusiv pentru un avans, care se înregistrează la data efectivă a încasării, exact așa cum cere regula cash-basis. Când plata vine prin bancă, `import_banca` generează automat o ciornă din extrasul bancar (categorie propusă implicit `activitate`), pe care contabilul o validează, confirmând astfel data și suma exactă a avansului.

[iConta.eu](/)
