---
title: Care este diferența dintre gestiunea cantitativ-valorică și global-valorică?
description: Diferența dintre cele două metode de gestiune a mărfurilor implementate în iConta.eu — cantitativ-valorică (CMP) și global-valorică (preț cu amănuntul) — și când se folosește fiecare.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Care este diferența dintre gestiunea cantitativ-valorică și global-valorică?

iConta.eu implementează două mecanisme distincte, separate în cod, pentru evidența mărfurilor: gestiunea **cantitativ-valorică** (cost mediu ponderat, CMP) și gestiunea **global-valorică** (metoda prețului cu amănuntul). Sunt funcționalități diferite, cu formule și note contabile diferite, nu două fețe ale aceleiași funcționalități.

## Temeiul legal

::: ghid-temei
„... pentru determinarea costului pot fi folosite, de asemenea, metoda costului standard, în activitatea de producție sau metoda prețului cu amănuntul, în comerțul cu amănuntul."
— OMFP 1802/2014, Anexa 1 – Reglementări contabile (formă consolidată), pct. 286 alin. (1)
:::

## Diferența, pe scurt

**Gestiunea global-valorică** (funcționalitatea descrisă în acest ghid) ține evidența mărfurilor la nivel de cont, nu de articol individual. Costul de achiziție, adaosul comercial și TVA neexigibilă se urmăresc separat, pe conturile 371 (mărfuri), 378 (diferențe de preț/adaos) și 4428 (TVA neexigibilă). Costul mărfii vândute nu se calculează articol cu articol, ci lunar, agregat, printr-un coeficient de repartizare (K) aplicat la valoarea totală a vânzărilor lunii.

**Gestiunea cantitativ-valorică** (funcționalitate separată în aplicație, cu temei legal propriu la pct. 96 din același act normativ) urmărește fiecare articol individual, cu costul mediu ponderat recalculat după fiecare intrare și o fișă de magazie cronologică per articol. Notele contabile sunt directe, pe articol: marfă (607=371) sau materii prime (601=301). Aplicația validează cronologic ieșirile, care nu pot depăși stocul existent la data lor.

| | Global-valorică (acest ghid) | Cantitativ-valorică (CMP) |
|---|---|---|
| Urmărire | Pe cont, agregat | Pe articol individual |
| Cost ieșiri | Coeficient K, lunar | Cost mediu ponderat, la fiecare mișcare |
| Conturi cheie | 371, 378, 4428 | 371/301, 607/601 |
| Fișă de magazie per articol | Nu | Da |

## Ce se greșește în practică

- Se presupune că cele două metode dau, în timp, exact aceleași rezultate contabile — nu e garantat: metoda global-valorică lucrează pe marje agregate, în timp ce cantitativ-valorica urmărește costul real al fiecărui articol la fiecare mișcare.
- Se schimbă metoda pentru aceleași stocuri de la o lună la alta, fără motiv documentat — reglementarea cere consecvență a metodei aplicate între exerciții.

## Ce face iConta.eu

Aplicația ține cele două metode ca funcționalități separate în cod, fiecare cu motorul ei de calcul propriu, și permite alegerea metodei potrivite pe tip de gestiune sau natură a stocurilor, așa cum permite și reglementarea contabilă atunci când stocurile au natură sau utilizare diferită.

[iConta.eu](/)
