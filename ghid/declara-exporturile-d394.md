---
title: "Se declară exporturile în D394?"
description: "De ce livrările către parteneri din afara UE intră în D394 la fel ca cele intracomunitare, și cum le clasifică automat iConta.eu."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Se declară exporturile în D394?

Spre deosebire de importuri, exporturile de bunuri **intră** în D394 — declarația are secțiuni proprii, dedicate operațiunilor cu parteneri stabiliți în alt stat membru și cu parteneri din afara Uniunii Europene, iar scutirea de TVA nu înseamnă scutire de declarare.

## Temeiul legal

::: ghid-temei
„E. Rezumat declaraţie privind operaţiunile desfăşurate cu persoane nestabilite în România care sunt stabilite în alt stat membru, neînregistrate şi care nu sunt obligate să se înregistreze în scopuri de TVA în România [...] F. Rezumat declaraţie privind operaţiunile desfăşurate cu persoane impozabile neînregistrate şi care nu sunt obligate să se înregistreze în scopuri de TVA în România, nestabilite pe teritoriul Uniunii Europene."
— OPANAF 3769/2015, Anexa 2 (sursă: anaf_surse/opanaf_3769_2015_d394_baza.txt:975-1004)
:::

- Formularul are secțiuni dedicate exact pentru operațiunile cu parteneri din alte state membre (lit. E) și cu parteneri din afara UE (lit. F) — exporturile de bunuri se încadrează firesc aici, ca livrări.
- O livrare cu cotă 0 (export sau livrare intracomunitară) trebuie declarată drept tip LS (livrare scutită), nu doar bifată ca „scutită" undeva în alt document — indiferent de tipul partenerului.
- Nu există, pentru livrări, o excludere similară celei de la achiziții/import: regula „nu vor fi declarate operațiunile de export şi import de bunuri" din instrucțiuni privește doar achizițiile cu taxare inversă de la parteneri nestabiliți, nu și livrările efectuate de firma ta către parteneri din afara UE.

## Ce se greșește în practică

- Se presupune că, la fel ca importurile, exporturile nu se declară în D394 — de fapt regula de excludere privește doar direcția de achiziție, nu și livrările.
- Se lasă o livrare la cotă 0 (export) neclasificată ca LS, iar validatorul ANAF o poate respinge sau contabilul o poate omite din rezumatul pe cote.
- Se confundă exportul cu livrarea intracomunitară în privința tratamentului declarativ — deși sunt operațiuni diferite ca regim vamal, în D394 amândouă apar ca livrări scutite, la cotă 0.

## Ce face iConta.eu

Funcția `tip_operatiune()` din `core/d394.py` clasifică orice livrare (`emisa=True`) către un partener de tip UE sau non-UE drept tip „L", care trece apoi prin aceeași regulă de reclasificare folosită pentru orice livrare scutită: la cotă 0, tipul devine automat „LS", indiferent de categoria partenerului. Practic, exporturile sunt tratate identic cu livrările intracomunitare din perspectiva D394 — ambele apar ca livrări scutite cu drept de deducere, în secțiunile E sau F ale declarației, corespunzător țării partenerului.

[iConta.eu](/)
