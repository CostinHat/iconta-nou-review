---
title: "D205 rectificativă: cum corectez dividendele declarate"
description: "Ce poate și ce nu poate face în prezent iConta.eu pentru corectarea unei declarații D205 deja depuse la ANAF."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# D205 rectificativă: cum corectez dividendele declarate

Dacă o declarație D205 a fost deja depusă la ANAF cu date greșite despre dividende, corecția standard se face printr-o declarație rectificativă. Este important să știți, înainte de a căuta acest flux în aplicație, ce este și ce nu este acoperit în acest moment.

## Temeiul legal

::: ghid-temei
"nu suportă declarație rectificativă (`d_rec="0"` hardcodat, `GARZI.md:2765`)"
— stare documentată intern a generatorului D205 din iConta, referitoare la limitele curente ale funcționalității F029
:::

Structura oficială D205 este reglementată prin OPANAF 179/2022 (bază), modificat prin OPANAF 102/2025 și, cel mai recent, OPANAF 303/2026 — niciuna dintre modificările recente nu afectează regulile privind dividendele (tip_venit "08"). Notă onestă: dincolo de faptul documentat mai sus (`d_rec="0"` hardcodat în generatorul iConta), acest ghid nu a putut verifica în corpusul de surse locale prevederile punctuale ale formularului oficial privind mecanismul de rectificare — pentru procedura exactă de rectificare la ANAF, consultați instrucțiunile oficiale de completare a D205.

## Ce se greșește în practică

Se presupune că, la fel ca la generarea declarației inițiale, corecția unor date greșite se poate face direct din iConta, regenerând declarația și redepunând-o ca și cum ar fi una rectificativă.

## Ce face iConta.eu

Aici trebuie spus explicit, fără ambiguitate: **iConta nu generează în acest moment o declarație D205 rectificativă** — parametrul intern care marchează caracterul rectificativ al declarației este fixat pe "nerectificativă" (`d_rec="0"`, hardcodat în generator), indiferent de situație. Este un gol de funcționalitate cunoscut și documentat intern, nu o opțiune ascunsă în interfață. Dacă aveți nevoie să corectați o D205 deja depusă, corecția datelor trebuie pregătită și depusă în afara fluxului automat al aplicației (de exemplu prin formularul oficial ANAF, folosind ca sursă de date corectate contul 457 și cotele asociaților din iConta). Înainte de a redepune, verificați totuși ca sursa (nota contabilă pe contul 457) să fie corectă — mecanismul de reconciliere internă al iConta (`core/d205_reconciliere.py`) vă poate confirma dacă baza și impozitul calculate corespund cu ce este înregistrat contabil, chiar dacă nu poate produce, el însuși, XML-ul rectificativ.

[iConta.eu](/)
