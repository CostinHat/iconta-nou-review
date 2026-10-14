---
title: "D205 rectificativă: cum corectez dividendele declarate"
description: "Ce poate și ce nu poate face în prezent iConta.eu pentru corectarea unei declarații D205 deja depuse la ANAF."
published: 2026-09-26
modified: 2026-10-13
poarta: v1
---

# D205 rectificativă: cum corectez dividendele declarate

Dacă o declarație D205 a fost deja depusă la ANAF cu date greșite despre dividende, corecția standard se face printr-o declarație rectificativă. Este important să știți, înainte de a căuta acest flux în aplicație, ce este și ce nu este acoperit în acest moment.

Structura oficială D205 este reglementată prin OPANAF 179/2022 (bază), modificat prin OPANAF 102/2025 și, cel mai recent, OPANAF 303/2026 — niciuna dintre modificările recente nu afectează regulile privind dividendele (tip_venit "08"). Mecanismul de rectificare are temei explicit, citat mai jos: Codul de procedură fiscală (art. 105) permite corectarea unei declarații informative prin declarație rectificativă, indiferent de perioada la care se referă, iar instrucțiunile de completare a formularului 205 (OPANAF 179/2022, pct. 5.1–5.2) cer ca rectificativa să se întocmească pe tipuri de venit și să cuprindă numai pozițiile corectate sau pe cele omise din declarația inițială.

## Temeiul legal

::: ghid-temei
„Declarația informativă poate fi corectată de către contribuabil/plătitor indiferent de perioada la care se referă. [...] Declarațiile prevăzute la alin. (1) și (2) pot fi corectate prin depunerea unei declarații rectificative.”
— Legea nr. 207/2015 privind Codul de procedură fiscală, art. 105 alin. (2) și (3) (sursă: [Legea nr. 207/2015 privind Codul de procedură fiscală](https://legislatie.just.ro/Public/DetaliiDocument/170007))

„ori de câte ori plătitorul de venit constată erori în declarația depusă anterior, acesta completează și depune o declarație rectificativă, în condițiile art. 105 și 170 din Legea nr. 207/2015 privind Codul de procedură fiscală [...] Declarația rectificativă se întocmește pe tipuri de venit și va cuprinde numai pozițiile corectate, declarate eronat în declarația inițială, sau pozițiile care, în mod eronat, nu au fost cuprinse în declarația inițială.”
— OPANAF nr. 179/2022, anexa nr. 1, Instrucțiuni privind completarea formularului 205, cap. I pct. 5.1 lit. b) și pct. 5.2 (sursă: [OPANAF nr. 179/2022 pentru aprobarea formularelor 205 și 207](https://legislatie.just.ro/Public/DetaliiDocument/251562))
:::

## Ce se greșește în practică

Se presupune că, la fel ca la generarea declarației inițiale, corecția unor date greșite se poate face direct din iConta, regenerând declarația și redepunând-o ca și cum ar fi una rectificativă.

## Ce face iConta.eu

Aici trebuie spus explicit, fără ambiguitate: **iConta nu generează în acest moment o declarație D205 rectificativă** — parametrul intern care marchează caracterul rectificativ al declarației este fixat pe "nerectificativă" (`d_rec="0"`, hardcodat în generator), indiferent de situație. Este un gol de funcționalitate cunoscut și documentat intern, nu o opțiune ascunsă în interfață. Dacă aveți nevoie să corectați o D205 deja depusă, corecția datelor trebuie pregătită și depusă în afara fluxului automat al aplicației (de exemplu prin formularul oficial ANAF, folosind ca sursă de date corectate contul 457 și cotele asociaților din iConta). Înainte de a redepune, verificați totuși ca sursa (nota contabilă pe contul 457) să fie corectă — mecanismul de reconciliere internă al iConta vă poate confirma dacă baza și impozitul calculate corespund cu ce este înregistrat contabil, chiar dacă nu poate produce, el însuși, XML-ul rectificativ.

[iConta.eu](/)
