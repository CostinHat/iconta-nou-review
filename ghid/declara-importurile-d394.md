---
title: "Se declară importurile în D394?"
description: "De ce achizițiile de bunuri din afara UE nu apar în D394 și cum tratează iConta.eu, automat, achizițiile provenite de la parteneri non-UE."
published: 2026-09-26
modified: 2026-10-13
poarta: v1
---

# Se declară importurile în D394?

D394 e o declarație despre operațiuni „pe teritoriul național" — iar importul de bunuri, prin natura lui, are un regim de TVA propriu, colectat de regulă în vamă, nu prin mecanismul de taxare inversă pe care D394 îl urmărește pentru achizițiile interne.

## Temeiul legal

::: ghid-temei
„Se vor declara numai operaţiunile taxabile pentru care locul livrării/prestării este în România conform art. 275, respectiv art. 278 din Codul fiscal şi, în cazul achiziţiilor de bunuri/servicii, beneficiarul este obligat la plata TVA conform art. 307 alin. (2), (3), (5) şi (6) din Codul fiscal. Nu vor fi declarate operaţiunile de export şi import de bunuri (inclusiv în cazul persoanei impozabile pentru care s-a acordat certificat de amânare de la plata în vamă a TVA), precum şi operaţiunile care se înscriu în declaraţia recapitulativă privind livrările/achiziţiile/prestările intracomunitare (formular 390)."
— OPANAF 2194/2025, Anexa 2, Cartuș F pct.10 (sursă: [OPANAF nr. 2194/2025 pentru modificarea OPANAF nr. 3769/2015 (declarația informativă D394)](https://legislatie.just.ro/Public/DetaliiDocument/302310))
:::

- Importul de bunuri, chiar și cel efectuat cu certificat de amânare de la plata TVA în vamă, nu se declară în D394 — regimul lui de TVA e altul (plată/amânare la vamă, nu taxare inversă raportată aici).
- Instrucțiunea nu exclude achizițiile de servicii de la prestatori stabiliți în afara UE pentru care beneficiarul din România plătește TVA (art. 307 alin. (2)): ele nu sunt import de bunuri și nu se înscriu în D390, deci intră în D394.
- Excluderea se completează cu cea a operațiunilor din declarația recapitulativă (D390) — practic, D394 nu cuprinde importurile și exporturile de bunuri și nici operațiunile intracomunitare declarate în D390.

## Ce se greșește în practică

- Se declară un import de bunuri ca operațiune cu taxare inversă (tip C), confundându-l cu achizițiile pentru care beneficiarul plătește taxa conform art. 307 — importul de bunuri nu se declară deloc în D394.
- Se declară exporturile de bunuri în D394, ca livrări cu cota 0 — instrucțiunea le exclude la fel ca pe importuri: „Nu vor fi declarate operaţiunile de export şi import de bunuri”.
- Se amestecă certificatul de amânare de la plata TVA în vamă cu o scutire de declarare în altă parte — amânarea privește doar momentul plății TVA la import, nu obligația de declarare (care rămâne oricum în afara D394).

## Ce face iConta.eu

iConta.eu încadrează partenerii după codul fiscal de pe factură: cod românesc, fără cod, cod cu prefix de țară din UE sau cod cu prefix de țară din afara UE.

- **La achiziții (facturile primite)**, aplicația scoate din D394 **orice** factură de la un partener din UE sau din afara UE — achiziții intracomunitare, importuri de bunuri și, la fel, achizițiile de servicii cu taxare inversă de la acești parteneri: niciuna nu intră automat în D394. La întocmire, aplicația afișează numărul achizițiilor excluse, cu mesajul că nu intră în D394 și se declară în D390 (VIES).
- **La livrări (facturile emise)**, facturile către parteneri din UE sau din afara UE intră în D394 ca livrări (tip L, sau LS la cota 0), fără să se deosebească exporturile de bunuri și livrările intracomunitare, pe care instrucțiunea de mai sus le exclude. Verifică aceste facturi înainte de depunere.

Aici aplicația exclude mai mult decât cere instrucțiunea: o achiziție de servicii de la un prestator din afara UE, cu taxare inversă, nu intră automat în D394, deși instrucțiunea de mai sus nu o exclude (iar mesajul de la întocmire o trimite, impropriu, la D390). Dacă firma are astfel de achiziții, includerea lor în D394 rămâne în sarcina contabilului, înainte de depunere.

[iConta.eu](/)
