---
title: "Pot deduce mesele din deplasare la PFA?"
description: "Ce cheltuieli de deplasare poate deduce o persoană fizică autorizată și de ce mesele/diurna nu sunt printre ele, spre deosebire de regimul salariaților."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Pot deduce mesele din deplasare la PFA?

Regimul fiscal al PFA e diferit de cel al unui salariat, iar diferența contează exact aici: un angajat poate primi o diurnă neimpozabilă plafonată, dar o persoană fizică autorizată nu are un echivalent al acesteia pentru masă. Legea îi permite să deducă doar cazarea și transportul din perioada deplasării — nu și mesele.

## Temeiul legal

::: ghid-temei
„(4) Condițiile generale pe care trebuie să le îndeplinească cheltuielile efectuate în scopul desfășurării activității independente, pentru a putea fi deduse, în funcție de natura acestora, sunt: [...] h) să fie efectuate pe perioada deplasării contribuabilului care își desfășoară activitatea individual și/sau într-o formă de asociere, în țară și în străinătate, în scopul desfășurării activității, reprezentând cheltuieli de cazare și transport, altele decât cele prevăzute la alin. (7) lit. k)."
— Codul fiscal, art. 68 alin. (4) lit. h) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce rezultă direct din text:

- Legea enumeră explicit doar **două categorii** de cheltuieli de deplasare deductibile pentru PFA: **cazarea** și **transportul** — nicio a treia categorie, deci nicio mențiune despre masă sau diurnă.
- Spre deosebire de salariat (unde indemnizația de delegare/diurna are un regim de neimpozabilitate plafonat, la art. 76 CF), Codul fiscal **nu prevede** pentru PFA vreun echivalent al diurnei — nu există un plafon zilnic neimpozabil pentru masă la activitățile independente.
- Trimiterea „altele decât cele prevăzute la alin. (7) lit. k)" exclude din cheltuielile de transport deductibile aici partea deja acoperită de regula specială a limitării la 50% pentru cheltuielile cu vehiculele rutiere (ca să nu se deducă de două ori aceeași cheltuială de transport).
- Condiția de bază rămâne cea generală: cheltuiala trebuie **efectuată în scopul desfășurării activității**, justificată prin documente și cuprinsă în cheltuielile exercițiului financiar al anului plății.

## Ce se greșește în practică

- Se aplică prin analogie regimul salariatului (diurnă neimpozabilă plafonată) la PFA, deși legea nu prevede așa ceva pentru activitățile independente.
- Se deduc bonuri de masă/restaurant din deplasare ca „diurnă", fără să existe temei legal pentru asta la art. 68 CF.
- Se confundă cheltuielile de deplasare ale PFA cu cele ale unui angajat al PFA (dacă PFA are personal angajat) — pentru angajați se aplică regulile de la art. 76 CF (inclusiv diurna), nu regulile de la art. 68 CF, care privesc titularul activității independente.

## Ce face iConta.eu

Modulul de deconturi de deplasare și diurnă (`core/deconturi.py`, ecranul „Decont deplasare / diurnă") funcționează exclusiv la nivelul unei firme plătitoare de partidă dublă — generează note contabile de tip 542/625/4426/641, specifice contabilității în partidă dublă. PFA-urile țin, în schimb, Registrul de încasări și plăți (partidă simplă), un flux complet diferit. Nu există în cod nicio legătură între modulul de deconturi și evidența unei PFA.

Concret, iConta.eu **nu are astăzi o funcție dedicată** pentru cheltuielile de deplasare ale unei PFA — nici pentru cazare/transport (singurele deductibile conform art. 68 alin. (4) lit. h) CF), nici, cu atât mai puțin, pentru mese, care oricum nu au temei de deducere separată. Titularul unei PFA trebuie să înregistreze aceste cheltuieli prin instrumentele generale de evidență a activității independente din aplicație, nu prin ecranul de deconturi construit pentru salariați.

[iConta.eu](/)
