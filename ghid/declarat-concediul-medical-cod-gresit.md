---
title: "Ce fac dacă am declarat concediul medical pe cod greșit?"
description: "Cum se corectează o eroare de raportare a unui concediu medical (cod de indemnizație greșit) prin declarația rectificativă D112, conform Codului de procedură fiscală."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce fac dacă am declarat concediul medical pe cod greșit?

Un certificat de concediu medical raportat cu alt cod de indemnizație decât cel real (de exemplu boală obișnuită în loc de urgență medicală, sau invers) nu se remediază printr-o notă internă — declarația D112, prin care se raportează indemnizațiile lunar, se corectează prin declarație rectificativă, ca orice altă declarație informativă.

## Temeiul legal

::: ghid-temei
„(2) Declarația informativă poate fi corectată de către contribuabil/plătitor indiferent de perioada la care se referă.
(3) Declarațiile prevăzute la alin. (1) și (2) pot fi corectate prin depunerea unei declarații rectificative."
— Legea 207/2015 (Codul de procedură fiscală), art. 105 alin. (2) și (3) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

D112 are, pentru scopul angajatorului, natură de declarație cu obligații fiscale declarate prin autoimpunere, dar componenta nominală (inclusiv codul certificatului de concediu medical) e corectabilă oricând, fără limitarea de prescripție care se aplică declarațiilor de impunere:

- Corectarea se face prin **depunerea unei noi declarații D112**, cu tipul „rectificativă", pentru luna în care a fost raportat inițial concediul cu cod greșit.
- Dacă eroarea de cod a dus și la un calcul greșit al cuantumului indemnizației (coduri diferite pot avea baze de calcul sau plafoane diferite), rectificarea trebuie să corecteze atât codul, cât și suma, nu doar unul dintre ele.
- Un cod de indemnizație greșit poate afecta modul în care se calculează contribuția de asigurări sociale de sănătate aferentă perioadei respective — de aceea corectarea D112 trebuie verificată și la nivelul contribuțiilor recalculate, nu doar la nivelul liniei salariatului.
- Nu există un termen-limită separat pentru corectarea declarațiilor informative (spre deosebire de declarațiile de impunere, supuse prescripției) — corectarea rămâne posibilă „indiferent de perioada la care se referă".

## Ce se greșește în practică

- Se corectează doar în evidența internă (statul de plată) a firmei, fără să se depună o D112 rectificativă, lăsând eroarea vizibilă în baza de date ANAF.
- Se schimbă codul certificatului fără să se recalculeze suma indemnizației, deși coduri diferite de concediu medical pot avea baze legale de calcul diferite.
- Se așteaptă un control ANAF pentru a corecta, deși legea permite corectarea din proprie inițiativă, oricând, fără sancțiuni suplimentare pentru simpla rectificare.

## Ce face iConta.eu

iConta.eu permite corectarea unui certificat de concediu medical introdus greșit (cod, perioadă, indemnizație) direct din modulul de salarizare, cu recalculul contribuțiilor aferente noii încadrări. Dacă luna respectivă are deja D112 confirmată, aplicația nu marchează însă automat noua declarație ca „rectificativă" în structura XML transmisă (atributul care indică acest lucru e emis mereu ca declarație inițială) — contabilul trebuie fie să deschidă din nou perioada (deconfirmarea D112 din aplicație), fie să depună manual, la ANAF, o D112 rectificativă pentru luna respectivă.

[iConta.eu](/)
