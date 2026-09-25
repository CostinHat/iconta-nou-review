---
title: "Ce fac dacă am trimis declarația la termen, dar recipisa a venit după termen?"
description: "Ce dată contează legal pentru o declarație depusă electronic — momentul transmiterii sau momentul primirii mesajului de confirmare — conform Codului de procedură fiscală."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce fac dacă am trimis declarația la termen, dar recipisa a venit după termen?

Îngrijorarea e frecventă: declarația a fost transmisă electronic înainte de miezul nopții din ultima zi de termen, dar mesajul de confirmare (recipisa) a sosit abia a doua zi. Legea rezolvă exact această situație — și răspunsul depinde de ce spune, de fapt, recipisa.

## Temeiul legal

::: ghid-temei
„(4) Data depunerii declarației fiscale prin mijloace electronice de transmitere la distanță este data înregistrării acesteia pe portal, astfel cum rezultă din mesajul electronic transmis de sistemul de tranzacționare a informațiilor, cu condiția validării conținutului declarației. în cazul în care declarația nu este validată, data depunerii declarației este data validării astfel cum rezultă din mesajul electronic.
(5) Prin excepție de la prevederile alin. (4), în situația în care declarația fiscală a fost depusă până la termenul legal, iar din mesajul electronic transmis de sistemul de tranzacționare a informațiilor rezultă că aceasta nu a fost validată ca urmare a detectării unor erori în completarea declarației, data depunerii declarației este data din mesajul transmis inițial în cazul în care contribuabilul/plătitorul depune o declarație validă până în ultima zi a lunii în care se împlinește termenul legal de depunere."
— Legea nr. 207/2015 (Codul de procedură fiscală), art. 103 alin. (4), (5) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Din text rezultă două situații complet diferite, în funcție de ce arată recipisa:

- Dacă mesajul electronic confirmă că declarația a fost **înregistrată și validată** pe portal, data depunerii este chiar acea dată de înregistrare — nu momentul la care recipisa a ajuns fizic în căsuța de e-mail sau a fost descărcată de contabil. Dacă înregistrarea s-a făcut înainte de termen, declarația e depusă la termen, indiferent când a fost citit mesajul.
- Dacă mesajul arată că declarația **nu a fost validată** (erori de completare), data depunerii devine data validării — și, prin excepția de la alin. (5), dacă declarația inițială fusese transmisă până la termenul legal, iar contribuabilul depune o variantă validă până în ultima zi a lunii în care se împlinește termenul, se păstrează data inițială de transmitere ca dată a depunerii.
- Diferența dintre „am primit recipisa târziu" (situația din alin. (4), fără consecințe — declarația e depusă la termen) și „recipisa arată respingere/erori" (situația din alin. (5), cu o fereastră de remediere până la finalul lunii) trebuie verificată direct din conținutul mesajului electronic, nu presupusă.

## Ce se greșește în practică

- Se presupune că întârzierea recipisei înseamnă automat depunere cu întârziere, fără să se verifice data reală de înregistrare din mesajul electronic.
- Se ignoră o recipisă care arată de fapt o respingere (erori de completare), considerând-o o simplă confirmare întârziată — și se pierde astfel fereastra de remediere până la finalul lunii, prevăzută la alin. (5).
- Nu se păstrează recipisa/mesajul electronic ca dovadă a datei reale de înregistrare, în caz de dispută ulterioară cu organul fiscal.

## Ce face iConta.eu

La data acestui ghid, iConta.eu generează și pregătește declarațiile fiscale pentru depunere (module dedicate pe fiecare tip de declarație, de exemplu `core/d100.py`, `core/d300.py`, `core/d112.py`), dar transmiterea efectivă și recepția confirmării de la portalul ANAF/SPV se fac prin canalele oficiale ale statului, în afara aplicației. iConta.eu **nu interpretează automat conținutul unei recipise** pentru a stabili dacă declarația a fost validată sau respinsă — verificarea mesajului electronic primit de la ANAF și, dacă e cazul, redepunerea unei variante corectate rămân responsabilitatea contabilului.

[iConta.eu](/)
