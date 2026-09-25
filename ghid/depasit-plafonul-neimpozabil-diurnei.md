---
title: "Ce fac dacă am depășit plafonul neimpozabil al diurnei?"
description: "Diurna acordată peste plafonul neimpozabil (2,5x nivelul stabilit pentru instituțiile publice) devine venit impozabil de natură salarială pentru partea care depășește plafonul."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce fac dacă am depășit plafonul neimpozabil al diurnei?

Angajatorii din mediul privat pot acorda o diurnă mai mare decât nivelul stabilit pentru personalul bugetar, dar scutirea de impozit se oprește la un plafon calculat ca multiplu al nivelului diurnei bugetare — ce depășește acest plafon se impozitează ca venit salarial obișnuit.

## Temeiul legal

::: ghid-temei
„...indemnizația de delegare, indemnizația de detașare, inclusiv indemnizația specifică detașării transnaționale, [...] precum și orice alte sume de aceeași natură, altele decât cele acordate pentru acoperirea cheltuielilor de transport și cazare, primite de salariați potrivit legislației în materie, pe perioada desfășurării activității în altă localitate, în țară sau în străinătate, în interesul serviciului, pentru partea care depășește plafonul neimpozabil stabilit astfel..."
— Legea nr. 227/2015 (Codul fiscal), art. 76 alin. (2) lit. k) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Plafonul neimpozabil al diurnei interne se calculează ca **multiplu (2,5x) al nivelului legal stabilit pentru personalul din instituțiile publice** prin hotărâre de Guvern — nivel care s-a schimbat de-a lungul timpului (de la 20 lei/zi conform HG nr. 714/2018, la 23 lei/zi de la 1 aprilie 2023, prin Ordinul nr. 1235/2023).
- Ce se acordă **peste** acest plafon (2,5x nivelul bugetar în vigoare la data deplasării) devine **venit asimilat salariilor**, impozabil și, după caz, supus contribuțiilor sociale, exact ca restul salariului.
- Plafonul se raportează la nivelul bugetar în vigoare **la data deplasării**, nu la un nivel fix aplicat retroactiv — o schimbare a nivelului bugetar (cum a fost cea din 2023) nu se aplică deplasărilor anterioare intrării ei în vigoare.
- Diurna acordată administratorilor și directorilor cu contract de mandat urmează aceleași reguli de plafonare, prevăzute distinct în Codul fiscal pentru această categorie.

## Ce se greșește în practică

- Se aplică nivelul curent al diurnei bugetare (folosit pentru calculul plafonului) retroactiv, pentru deplasări din perioade în care era în vigoare un nivel bugetar mai mic.
- Se consideră întreaga diurnă neimpozabilă doar pentru că a fost stabilită „prin regulament intern" ca politică a firmei, ignorând plafonul legal care limitează scutirea fiscală, indiferent de politica internă.
- Se omite calculul separat pentru partea care depășește plafonul, tratând-o eronat tot ca diurnă neimpozabilă, în loc de a o include în baza de calcul a impozitului pe venit și a contribuțiilor.

## Ce face iConta.eu

La data acestui ghid, modulul de decontări din iConta.eu (`core/deconturi.py`, funcția `plafon_diurna`) calculează automat plafonul neimpozabil ca minimul dintre 2,5x diurna bugetară internă și 3x salariul de bază raportat la zilele lucrătoare din lună, exact formula de la art. 76 alin. (2) lit. k) și alin. (4^1) din Codul fiscal, și separă automat suma neimpozabilă de partea impozabilă a diurnei acordate. Nivelul diurnei bugetare folosit ca bază e sensibil la perioadă — 20 lei/zi până la 31.03.2023 (HG nr. 714/2018), 23 lei/zi de la 1 aprilie 2023 (Ordinul MF nr. 1235/2023) — astfel încât calculul nu aplică retroactiv valoarea actuală unor deplasări din trecut.

[iConta.eu](/)
