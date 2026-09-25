---
title: "Cum corectez o eroare în Declarația Unică D212?"
description: "O eroare descoperită după validare se corectează prin declarație rectificativă, depusă în termenul de prescripție de 5 ani — nu prin redepunerea declarației inițiale."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum corectez o eroare în Declarația Unică D212?

Odată validată, o D212 nu se „suprascrie" — se corectează exclusiv prin declarație rectificativă, iar legea îți dă un termen generos pentru asta: cinci ani, nu câteva zile.

## Temeiul legal

::: ghid-temei
„Declarația de impunere poate fi corectată de către contribuabil/plătitor, pe perioada termenului de prescripție a dreptului de a stabili creanțe fiscale. [...] Declarațiile prevăzute la alin. (1) și (2) pot fi corectate prin depunerea unei declarații rectificative."
— Legea 207/2015 (Codul de procedură fiscală), art. 105 alin. (1) și (3) (sursă: anaf_surse/legea_207_2015_consolidat.txt)

„Dreptul organului fiscal de a stabili creanțe fiscale se prescrie în termen de 5 ani, cu excepția cazului în care legea dispune altfel."
— Legea 207/2015, art. 110 alin. (1) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Ce spune combinația celor două articole pentru D212:

- D212 e o declarație de impunere (nu informativă), deci corectarea urmează regula de la art. 105 alin. (1) — se poate depune rectificativă oricând în termenul de prescripție.
- Termenul de prescripție e, de regulă, 5 ani, calculat de la 1 iulie a anului următor celui pentru care se datorează obligația (art. 110 alin. (1)-(2)).
- Pentru diferențele de obligații fiscale rezultate dintr-o rectificativă, termenul de plată e chiar data depunerii rectificativei (art. 105 coroborat cu regulile de scadență din procedura fiscală).
- Excepție importantă: după anularea rezervei verificării ulterioare pe perioada respectivă, declarația nu mai poate fi de regulă corectată (art. 105 alin. (5)), cu excepțiile limitate de la alin. (6) — o condiție prevăzută de lege care impune corectarea, sau o hotărâre judecătorească definitivă.

## Ce se greșește în practică

- Se încearcă „redepunerea" declarației inițiale, ca și cum s-ar putea suprascrie — corect e depunerea unei declarații rectificative, care înlocuiește-o pe cea eronată.
- Se crede că o eroare veche (de acum câțiva ani) nu mai poate fi corectată — de fapt termenul e de 5 ani de la 1 iulie a anului următor, mult mai lung decât se presupune de obicei.
- Se ignoră excepția rezervei verificării ulterioare — o rectificativă depusă după ce ANAF a anulat rezerva pe acea perioadă poate fi respinsă, dacă nu se încadrează în situațiile de excepție.

## Ce face iConta.eu

Generatorul D212 al iConta.eu (`core/d212.py`) expune pe rădăcina declarației câmpurile obligatorii de rectificare (`rectif1`, `rectif2`), care marchează declarația ca inițială sau rectificativă, respectând structura validată de ANAF. Decizia de a corecta o eroare, identificarea sursei ei și verificarea încadrării în termenul de prescripție rămân responsabilitatea contabilului — aplicația nu ține un istoric fiscal al declarațiilor D212 depuse anterior și nu compară automat versiunile pentru a semnala diferențele.

[iConta.eu](/)
