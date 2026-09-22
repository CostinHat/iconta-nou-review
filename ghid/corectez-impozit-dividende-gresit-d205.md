---
title: Cum corectez impozitul pe dividende declarat greșit în D205?
description: Legea permite depunerea unei declarații rectificative D205 doar cu pozițiile corectate, dar iConta.eu nu are momentan un mecanism de generare a rectificativei — orice corecție reală trebuie tratată separat, în afara fluxului automat.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum corectez impozitul pe dividende declarat greșit în D205?

Dacă ați descoperit, după depunerea D205, că impozitul pe dividende declarat pentru un beneficiar e greșit, primul pas util este să vă asigurați că e într-adevăr o eroare (vezi ghidul despre cota de impozit calculată „greșit" — deseori e vorba de aplicarea corectă a ratei pe data distribuirii, nu de un bug). Dacă e confirmat că e o eroare reală, e important să înțelegeți limitarea actuală a aplicației înainte de a promite un flux concret.

## Temeiul legal

::: ghid-temei
„Declaraţia rectificativă se întocmeşte pe tipuri de venit şi va cuprinde numai poziţiile corectate, declarate eronat în declaraţia iniţială, sau poziţiile care, în mod eronat, nu au fost cuprinse în declaraţia iniţială." (OPANAF 179/2022, I.5.2-5.3, l.250-261)

„la col. 3-6 [cap. V dividende] se va înscrie cifra «0» (zero)" — pentru ștergerea unei poziții greșite (OPANAF 179/2022, I.5.2-5.3, l.250-261)

„Declaraţia rectifcativa N(1) DA d_rec=(0,1) 0-initiala 1-rectificativa. Declaratia rectificativa va contine doar inregistrarile care reprezinta corectii fata de raportarea initiala." (structura D205, OPANAF 102/2025, rd.4)
:::

## Ce prevede legea pentru o corecție

Legal, corectarea unei declarații D205 depuse greșit se face printr-o declarație rectificativă, care nu retransmite toată declarația, ci doar pozițiile corectate față de declarația inițială — inclusiv poziții omise inițial. Pentru a șterge complet o poziție greșit declarată la capitolul de dividende, regula ANAF cere completarea cu cifra „0" pe coloanele de sumă (distribuit, plătit, bază, impozit) pentru acea poziție, în rectificativă.

## Ce se greșește în practică

- Se așteaptă un buton „generează rectificativă" în aplicație, presupunând că funcționează la fel ca la alte declarații.
- Se retrimite integral D205 cu toate pozițiile, în loc de doar pozițiile corectate, așa cum cere procedura de rectificativă.
- Se corectează eroarea doar în contabilitatea internă (nota contabilă), fără să se depună vreo rectificativă la ANAF, lăsând declarația inițială greșită nemodificată oficial.
- Se ignoră faptul că o poziție greșită se șterge cu „0" pe coloanele de sumă, nu prin omiterea ei din rectificativă.

## Ce face iConta.eu

În acest moment, generatorul D205 emite declarația exclusiv ca declarație inițială — marcajul de „declarație rectificativă" din structura oficială ANAF este fixat intern pe valoarea „inițială" și aplicația nu are un mecanism prin care să producă o declarație rectificativă cu doar pozițiile corectate. Dacă identificați o eroare reală în impozitul pe dividende deja declarat, corectarea trebuie tratată în afara fluxului automat de generare din aplicație; vă recomandăm să verificați cu echipa de suport iConta.eu care este procedura curentă recomandată pentru situația dumneavoastră, înainte de a depune orice corecție la ANAF.

[iConta.eu](/)
