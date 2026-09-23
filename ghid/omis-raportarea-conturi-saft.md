---
title: "Am omis raportarea unor conturi în SAF-T"
description: "Ce se întâmplă dacă depui o D406 și observi ulterior că lipsesc date, și cum tratează legea o declarație depusă din nou pentru aceeași perioadă."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Am omis raportarea unor conturi în SAF-T

Dacă ai depus deja o declarație D406 și observi ulterior că anumite date lipsesc din ea, soluția nu e să „repari" declarația veche, ci să depui din nou, complet, pentru aceeași perioadă.

## Temeiul legal

::: ghid-temei
„Prima Declaraţie informativă D406 validată, depusă pentru o lună sau un trimestru de către un contribuabil/plătitor este considerată declaraţie iniţială. Declaraţiile ulterioare depuse pentru aceeaşi perioadă (lună/trimestru) sunt automat considerate declaraţii rectificative." — OPANAF nr. 1783/2021, Anexa 3, pct. 18
:::

Practic, dacă redepui D406 pentru aceeași lună sau același trimestru, declarația e automat tratată drept rectificativă — nu trebuie o procedură separată de „corectare" pentru omisiuni constatate ulterior, ci o nouă declarație validă, completă, pentru acea perioadă.

Sancțiunea pentru o declarație incompletă e prevăzută explicit: „depunerea incorectă ori incompletă a fişierului standard de control fiscal" se amendează cu 500-1.500 lei (Legea 207/2015, art. 337^1 alin. 2 lit. b). Legea prevede însă o excepție directă pentru exact acest scenariu — corectarea făcută **până la termenul următoarei depuneri** nu se sancționează (art. 337^1 alin. 3).

## Ce se greșește în practică

- Se lasă declarația incompletă nemodificată, în ideea că „oricum a fost depusă" — fără să se profite de fereastra de corectare fără sancțiune până la termenul următoarei depuneri.
- Se așteaptă o notificare de la ANAF înainte de a corecta, deși corectarea din proprie inițiativă, în termen, evită amenda.
- Se confundă „declarație rectificativă" cu o operațiune tehnică specială din aplicație — conform normei, statutul de rectificativă e determinat automat de faptul că e a doua depunere pentru aceeași perioadă, nu de o bifă separată pe care contribuabilul trebuie să o completeze el însuși în conținutul D406.

## Ce face iConta.eu

Generatorul D406 (`core/d406.py`) produce declarația din datele curente din evidență la momentul generării — dacă între timp ai adăugat sau corectat înregistrări (inclusiv conturi omise inițial), o nouă generare pentru aceeași perioadă reflectă starea actualizată a contabilității. Validarea rămâne obligatorie și pentru redepunere, cu același instrument oficial (`DUKIntegrator_AnLunaUI.jar`, integrat în aplicație) — o declarație rectificativă trebuie să treacă la fel de „valid" ca prima.

Nu am găsit în dosarul de cercetare un mecanism dedicat, în aplicație, care să marcheze explicit o depunere ca „rectificativă" prin altceva decât redepunerea pentru aceeași perioadă — conform normei citate mai sus, acest statut e automat prin simplul fapt al redepunerii, nu printr-o setare separată.

[iConta.eu](/)
