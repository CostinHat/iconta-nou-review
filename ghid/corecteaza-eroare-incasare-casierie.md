---
title: "Cum se corectează o eroare de încasare în casierie"
description: "Cum se corectează corect o eroare de sumă înregistrată în registrul de casă, pe baza documentelor justificative, conform normelor generale de contabilitate."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se corectează o eroare de încasare în casierie

O sumă greșită înregistrată în registrul de casă nu se șterge și nu se rescrie peste operațiunea inițială — orice corectare într-o evidență contabilă trebuie să se sprijine pe un document justificativ nou, care să arate clar ce s-a corectat și de ce.

## Temeiul legal

::: ghid-temei
„Documentele justificative care stau la baza înregistrărilor în contabilitate angajează răspunderea persoanelor care le-au întocmit, vizat și aprobat, precum și a celor care le-au înregistrat în contabilitate."
— OMFP 2634/2015 (norme generale privind documentele financiar-contabile), pct. 5 (sursă: anaf_surse/omfp_2634_2015_anexa1_norme_generale.txt)
:::

Ce presupune, concret, o corectare făcută corect:

- Documentele justificative trebuie să cuprindă, printre altele, conținutul operațiunii economico-financiare și datele cantitative/valorice aferente — o corecție se face tot printr-un document, nu prin ștergerea celui greșit.
- O eroare de sumă la o încasare în numerar se corectează, de regulă, printr-o notă de stornare (înregistrare inversă a sumei greșite) urmată de înregistrarea corectă, ambele cu document justificativ și dată.
- Registrul de casă, ca document contabil, trebuie să reflecte un sold corect și verificabil zi de zi — o corecție aplicată retroactiv, fără urmă, sparge trasabilitatea soldului rulant.

## Ce se greșește în practică

- Se modifică direct suma dintr-o operațiune deja înregistrată în registrul de casă, fără document nou — la un control, lipsa urmei arată o evidență modificată netransparent.
- Se corectează eroarea doar în extrasul fizic/registrul pe hârtie, fără ca modificarea să fie reflectată și în notele contabile (creditul/debitul contului 5311) — soldul contabil rămâne, în acest caz, greșit.
- Se ignoră plafoanele legale de încasări/plăți în numerar (de exemplu 5.000 lei per partener persoană juridică) la momentul corectării — o corecție care mută suma pe altă zi poate crea, la rândul ei, o depășire de plafon nesesizată.

## Ce face iConta.eu

Modulul de casierie al iConta.eu (`core/casa.py`) calculează soldul rulant al registrului de casă pe baza operațiunilor introduse și verifică automat depășirile plafoanelor legale de numerar (sold zilnic, încasări/plăți per partener). Aplicația nu are însă, la acest moment, o funcție dedicată de „corectare a unei erori de încasare" — o sumă greșit introdusă se corectează prin introducerea unei operațiuni de stornare (inversă) urmată de operațiunea corectă, ca în orice evidență contabilă manuală; aplicația nu automatizează generarea acestei perechi de operațiuni.

[iConta.eu](/)
