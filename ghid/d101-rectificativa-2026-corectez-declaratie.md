---
title: "D101 rectificativă 2026: cum corectez o declarație depusă greșit"
description: "Mecanismul legal de corectare a declarației de impunere (D101) prin declarație rectificativă, cu termenul de plată aplicabil diferențelor rezultate."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# D101 rectificativă 2026: cum corectez o declarație depusă greșit

Corectarea unei declarații D101 depuse greșit — fie cu o bază de calcul incorectă, fie cu erori de completare — are un temei explicit în Codul de procedură fiscală, atât pentru dreptul de corectare, cât și pentru termenul de plată al eventualelor diferențe rezultate.

## Temeiul legal

::: ghid-temei
„ART. 105 Corectarea declarației fiscale
(1) Declarația de impunere poate fi corectată de către contribuabil/plătitor, pe perioada termenului de prescripție a dreptului de a stabili creanțe fiscale.
[...]
(3) Declarațiile prevăzute la alin. (1) și (2) pot fi corectate prin depunerea unei declarații rectificative.
[...]
ART. 156 Termenele de plată [...]
(4) În cazul creanțelor fiscale administrate de organul fiscal central, pentru diferențele de obligații fiscale principale stabilite de contribuabil/plătitor prin declarații fiscale rectificative, termenul de plată al diferențelor este data depunerii declarației rectificative la organul fiscal."
— Legea nr. 207/2015 (Codul de procedură fiscală), art. 105 alin. (1) și (3), art. 156 alin. (4) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Ce înseamnă acest temei pentru o D101 rectificativă în 2026:

- Corectarea se face prin **declarație rectificativă** (D101, cu bifa aferentă), depusă în interiorul termenului de prescripție a dreptului organului fiscal de a stabili creanțe fiscale — nu într-un termen scurt și fix, dar cu efecte de dobândă/penalitate care curg din scadența inițială.
- Dacă rectificativa stabilește o **diferență de impozit** (sumă suplimentară), termenul de plată al acelei diferențe este chiar **data depunerii declarației rectificative** — nu termenul general de 25 martie/iunie al declarației inițiale.
- Termenul de depunere a D101 inițiale în sine a suferit modificări legislative succesive pe parcursul ultimilor ani (schema OUG 153/2020 a mutat termenul la 25 iunie pentru 2021-2025; pentru 2026 se aplică, potrivit bazei din Codul fiscal, 25 martie, cu o modificare ulterioară prin OUG 8/2026 care mută termenul la 25 iunie începând cu declarația aferentă anului fiscal 2026) — verificarea termenului exact aplicabil anului de referință al declarației rectificate rămâne esențială înainte de a calcula eventuale accesorii.

## Ce se greșește în practică

- Se presupune că o declarație rectificativă anulează retroactiv orice dobândă de întârziere — dobânzile curg de la scadența inițială a obligației, nu se șterg prin simpla depunere a rectificativei.
- Se depune rectificativa fără a recalcula corect toate secțiunile formularului (P1-P53), presupunând că se poate modifica doar rândul cu eroarea constatată — declarația rectificativă înlocuiește integral declarația anterioară pentru perioada respectivă.
- Se confundă termenul de depunere a declarației inițiale (variabil pe ani, potrivit schemelor legislative succesive) cu termenul de plată al diferenței dintr-o rectificativă, care este întotdeauna data depunerii acesteia.

## Ce face iConta.eu

Verificat în cod: `core/d101.py` generează Declarația 101 conform structurii P1-P53 confirmate din validatorul oficial, iar `core/d101_reconciliere.py` verifică independent baza contabilă a rezultatului; aplicația nu are, la acest moment, un asistent dedicat pentru generarea automată a unei D101 rectificative pornind de la o eroare identificată ulterior — o astfel de corecție presupune recalcularea manuală a formularului pentru perioada afectată și redepunerea lui cu bifa de rectificativă.

[iConta.eu](/)
