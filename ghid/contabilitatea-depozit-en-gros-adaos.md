---
title: "Contabilitatea unui depozit en-gros: adaos și descărcare"
description: "De ce metoda global-valorică (preț cu amănuntul) nu se potrivește, de regulă, unui depozit cu vânzare en-gros, și spre ce evidență se orientează astfel de gestiuni."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Contabilitatea unui depozit en-gros: adaos și descărcare

Titlul cere aplicarea mecanismului de adaos și descărcare (metoda global-valorică) la un depozit cu vânzare en-gros. Pe baza dosarului tehnic verificat, trebuie spus onest: legea leagă explicit metoda prețului cu amănuntul de **comerțul cu amănuntul**, nu de vânzarea cu ridicata (en-gros).

## Temeiul legal

::: ghid-temei
OMFP 1802/2014, Anexa 1 — Reglementări contabile, pct. 286 alin. (1): „... pentru determinarea costului pot fi folosite, de asemenea, metoda costului standard, în activitatea de producție sau metoda prețului cu amănuntul, în comerțul cu amănuntul."

(Text consolidat OMFP 1802/2014, verificat pe mirrorul local la 17.09.2026.)
:::

Textul legal condiționează explicit metoda prețului cu amănuntul de comerțul **cu amănuntul**. Un depozit en-gros vinde, prin definiție, cu ridicata — de regulă către alți comercianți, nu către consumatorul final, la un preț de vânzare fix afișat la raft. Cerința de la pct. 286 alin. (8) — „articole numeroase și cu mișcare rapidă, care au marje similare, pentru care nu este practic să se folosească altă metodă" — descrie profilul unui magazin cu amănuntul, nu al unei relații de vânzare en-gros, unde prețul și marja se negociază de regulă pe client sau pe tranzacție.

## Ce se greșește în practică

Greșeala tipică este aplicarea automată a metodei global-valorice (cu conturile 378 „Diferențe de preț" și 4428 „TVA neexigibilă") la un depozit en-gros doar pentru că firma vinde marfă cu adaos. Metoda global-valorică presupune un preț de vânzare fix, afișat, pe stoc — o premisă care de regulă nu se potrivește vânzării cu ridicata.

## Ce face iConta.eu

Pentru gestiuni pe cantități și costuri individuale — mai apropiate de profilul unui depozit en-gros — iConta.eu are un motor separat, cantitativ-valoric (CMP): `core/stocuri_cv.py` / `core/stocuri_cv_api.py`, care recalculează costul mediu ponderat după fiecare intrare, ține o fișă de magazie cronologică per articol și nu permite unei ieșiri să depășească stocul existent la data ei.

Această legătură cu profilul „depozit en-gros" nu este însă verificată explicit în dosarul tehnic care stă la baza acestui ghid — cercetarea a confirmat doar legătura dintre evidența cantitativ-valorică și rețetarul HoReCa, nu una specifică pentru vânzarea en-gros. Recomandăm, pentru un depozit en-gros concret, o verificare punctuală a metodei de gestiune potrivite, în funcție de modul real de stabilire a prețurilor de vânzare, înainte de a alege între cele două motoare de calcul ale aplicației.

[iConta.eu](/)
