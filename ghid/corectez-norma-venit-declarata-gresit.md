---
title: "Cum corectez norma de venit declarată greșit în D212?"
description: "Corectarea normei de venit din D212 se face printr-o declarație rectificativă, oricând pe perioada de prescripție; iConta.eu nu calculează azi norma de venit, motorul propriu acoperă doar PFA/II/IF în sistem real."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum corectez norma de venit declarată greșit în D212?

Corectarea se face prin depunerea unei declarații unice rectificative, din proprie inițiativă, oricând în interiorul termenului de prescripție — mecanismul e general, valabil pentru orice dată greșită din D212, inclusiv norma de venit.

## Temeiul legal

::: ghid-temei
„(1) Declarația de impunere poate fi corectată de către contribuabil/plătitor, pe perioada termenului de prescripție a dreptului de a stabili creanțe fiscale. [...] (3) Declarațiile prevăzute la alin. (1) și (2) pot fi corectate prin depunerea unei declarații rectificative."
— Legea 207/2015 (Codul de procedură fiscală), art. 105 (sursă: anaf_surse/legea_207_2015_consolidat.txt)

„3.1. Declarația unică [...] poate fi corectată de contribuabili din proprie inițiativă, ori de câte ori informațiile actuale nu corespund celor din declarația depusă anterior, prin depunerea unei declarații rectificative în condițiile prevăzute de Legea nr. 207/2015 [...] 3.4. Declarația rectificativă se utilizează pentru: [...] modificarea unor date referitoare la categoria/sursa veniturilor sau a nivelului acestora, potrivit legii; [...] corectarea altor informații prevăzute de formular."
— OPANAF 888/2018 (sursă: anaf_surse/opanaf_888_2018.txt)
:::

Aplicat la norma de venit: dacă ai declarat greșit norma de venit (de exemplu ai bifat activitatea greșit, ai folosit un nivel de normă din alt județ/an, sau nu ai actualizat-o la o modificare adusă de organul fiscal), corecția e o declarație rectificativă, cu datele corecte pentru capitolul de venituri pe bază de normă. Nu există un formular separat „rectificare normă de venit" — mecanismul e cel general al Declarației unice.

## Ce se greșește în practică

- Se așteaptă ca o simplă solicitare la ANAF să corecteze norma — corecția se face prin declarație rectificativă, depusă de contribuabil, nu printr-o cerere administrativă separată.
- Se confundă norma de venit (venit anual stabilit forfetar, pe activitate/zonă, de organul fiscal) cu venitul net în sistem real (venit brut minus cheltuieli deductibile) — cele două regimuri se declară în capitole diferite ale D212 și au reguli de corectare identice ca mecanism, dar baza de calcul complet diferită.
- Se presupune că aplicația de contabilitate calculează sau verifică automat norma de venit — norma e stabilită de organul fiscal pe activitate/zonă, nu de un motor de calcul intern.

## Ce face iConta.eu

Motorul de calcul D212 din iConta.eu (`core/d212_engine.py`) acoperă exclusiv **PFA/II/IF în sistem real** (partida simplă) — calculează venitul net ca diferență între venitul brut și cheltuielile deductibile din registrul de încasări și plăți, plus CAS/CASS/impozitul aferent. **Norma de venit nu are niciun calcul propriu în acest motor** — câmpurile din declarația D212 pentru norma de venit (`cap12`, cu subcâmpurile ei) se completează manual, direct în declarație, la fel ca restul datelor din generatorul separat al formularului (`core/d212.py`), care nu recalculează nimic, ci preia valorile așa cum sunt introduse.

Practic, dacă declari pe bază de normă de venit, iConta.eu nu îți verifică sau recalculează cifra — corecția unei norme greșit introduse înseamnă corectarea manuală a câmpului respectiv și redepunerea declarației rectificative, conform mecanismului general de mai sus.

[iConta.eu](/)
