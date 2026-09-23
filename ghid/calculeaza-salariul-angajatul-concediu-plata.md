---
title: Cum se calculează salariul când angajatul are concediu fără plată?
description: Pentru luna cu concediu fără plată, salariul se calculează proporțional cu timpul efectiv lucrat — principiul general din Codul muncii, aplicat de motorul de calcul verificat pentru salariul obișnuit. Articolele specifice concediului fără plată nu au fost confirmate separat în acest dosar.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se calculează salariul când angajatul are concediu fără plată?

Când un angajat are, într-o lună, zile de concediu fără plată, salariul brut aferent lunii respective nu mai e cel din contract, ci se reduce proporțional cu timpul efectiv lucrat.

## Temeiul legal

::: ghid-temei
„(2) Drepturile salariale se acordă proporțional cu timpul efectiv lucrat, raportat la drepturile stabilite pentru programul normal de lucru." — Legea 53/2003 (Codul muncii), art.103 alin.(2)
:::

**De semnalat onest**: art.103 din Codul muncii se află, ca poziție în lege, în capitolul dedicat muncii cu timp parțial, iar dosarul de cercetare folosit la acest ghid l-a verificat verbatim în acest context (proporționalitatea salariului cu norma de lucru). Textul citat e însă un principiu general — salariul proporțional cu timpul efectiv lucrat — care se aplică logic și la o lună cu zile de concediu fără plată, nu doar la contractele part-time. Articolele Codului muncii care reglementează explicit condițiile și durata concediului fără plată nu au fost verificate cu citat separat în acest dosar; dacă aveți nevoie de temeiul exact pentru condițiile de acordare a concediului fără plată (nu pentru calculul salarial), verificați-l direct.

## Cum se calculează

Brut proporțional = brut contractual × (zile efectiv lucrate / zile lucrătoare din lună).

**Exemplu**: un angajat cu brut contractual 6.000 lei/lună, cu 20 de zile lucrătoare în lună, ia 4 zile de concediu fără plată (lucrează 16 din 20 de zile):

| Element | Calcul | Valoare |
|---|---|---|
| Brut proporțional | 6.000 × (16/20) | 4.800 lei |

Pornind de la acest brut redus, restul calculului (CAS 25%, CASS 10%, deducere personală, impozit 10%) urmează aceeași formulă ca la un salariu obișnuit, aplicată motorului de calcul `_calcul_salariu_2018()` din codul verificat. Dacă brutul astfel redus ajunge sub podeaua de contribuții (salariul minim aplicabil lunii, eventual redus cu facilitatea „salariul minim neimpozabil"), CAS și CASS se recalculează pe podea, nu pe brutul efectiv redus — aceeași regulă de la CF art.146 alin.(5^6), valabilă indiferent de motivul pentru care venitul e sub minim.

## Ce se greșește în practică

- Se calculează salariul integral din contract, ignorând zilele de concediu fără plată.
- Se scade suma zilelor de concediu fără plată direct din net, în loc să se recalculeze brutul proporțional și apoi întregul lanț de rețineri (CAS, CASS, impozit) pe brutul redus.
- Se uită verificarea podelei de contribuții atunci când brutul redus ajunge sub salariul minim aplicabil lunii.

## Ce face iConta.eu

Formula de calcul brut→net (`core/salarizare.py`, `_calcul_salariu_2018()`) e aceeași indiferent de motivul reducerii brutului contractual — fie normă parțială, fie zile de concediu fără plată într-o lună. Cotele și salariul minim aplicabil vin din registrul „period-aware" `core.common.COTE`, potrivit lunii calculate, iar verificarea podelei de contribuții se aplică automat oricând brutul introdus e sub pragul corespunzător.

[iConta.eu](/)
