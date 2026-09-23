---
title: "Cum tratez fiscal cadourile acordate salariaților?"
description: Cadourile acordate salariaților sunt neimpozabile până la 300 lei/persoană/ocazie, dar doar pentru patru evenimente strict definite de lege — orice alt eveniment sau orice sumă peste plafon se taxează integral ca venit salarial.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum tratez fiscal cadourile acordate salariaților?

Cadourile acordate salariaților au un regim de neimpozitare condiționat strict de ocazia cu care sunt oferite, nu de simplul fapt că e vorba de un cadou — condiția de ocazie e la fel de importantă ca plafonul valoric.

## Temeiul legal

::: ghid-temei
Codul fiscal, art. 76 alin. (4) lit. a): „În cazul cadourilor în bani și/sau în natură, inclusiv tichetele cadou, oferite de angajatori, veniturile sunt neimpozabile, în măsura în care valoarea acestora pentru fiecare persoană în parte, cu fiecare ocazie din cele de mai jos, nu depășește 300 lei: (i) cadouri ... cu ocazia Paștelui, Crăciunului și a sărbătorilor similare ale altor culte religioase; (ii) cadouri oferite angajatelor cu ocazia zilei de 8 martie; ... (iii) cadouri oferite angajaților în beneficiul copiilor minori ai acestora cu ocazia zilei de 1 iunie."
:::

Aceeași regulă, cu aceleași trei ocazii (Paște/Crăciun, 8 Martie, 1 Iunie), se aplică și pentru CASS, potrivit art. 142 lit. b) din Codul fiscal. **Doar patru evenimente sunt „legale" în acest sens**: Paște, Crăciun (inclusiv sărbătorile similare ale altor culte religioase), 8 Martie și 1 Iunie. Orice alt eveniment — aniversare, performanță, „welcome pack" sau altă ocazie inventată de angajator — face ca valoarea cadoului să fie taxabilă **integral**, ca venit salarial obișnuit, indiferent cât de mică e suma, fără să beneficieze de plafonul de 300 lei.

Pentru cele patru evenimente legale, plafonul de 300 lei e per persoană, per ocazie — nu anual, cumulat. Ce depășește 300 lei la un eveniment legal se taxează doar pentru excedent, nu integral.

## Ce se greșește în practică

- Se aplică plafonul de 300 lei neimpozabil la orice cadou, indiferent de ocazie — de exemplu la o „zi a companiei" sau la o aniversare de angajat, ocazii care nu se numără printre cele patru evenimente legale.
- Se calculează plafonul de 300 lei ca sumă anuală cumulată pe toate cadourile din an, în loc de plafon separat pentru fiecare din cele patru ocazii legale.
- Se presupune că excedentul peste 300 lei, la un eveniment legal, anulează scutirea pentru toată suma — de fapt doar excedentul devine taxabil, nu valoarea integrală a cadoului.

## Ce face iConta.eu

Modulul de beneficii (`core/beneficii_api.py`) calculează automat partea taxabilă a cadoului: neimpozabil până la 300 lei/persoană/ocazie, doar pentru cele patru evenimente legale (Paște, Crăciun, 8 Martie, 1 Iunie); pentru orice alt eveniment, întreaga valoare e tratată ca taxabilă. Partea taxabilă intră automat în brutul declarat în D112, la rândul E3_73; partea neimpozabilă (sub 300 lei, eveniment legal) apare doar în stat de plată și fluturaș, fără reținere. Verificat direct în cod: suma taxabilă a cadoului chiar intră în calculul și declararea D112 — ce nu e încă automatizat complet e doar fluxul/interfața de semnalare a cadourilor peste prag (marcate ca „de verificat" în aplicație), nu calculul fiscal propriu-zis, care e deja funcțional.

[iConta.eu](/)
