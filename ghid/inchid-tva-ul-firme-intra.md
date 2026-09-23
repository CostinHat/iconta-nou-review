---
title: "Cum închid TVA-ul unei firme care intră în lichidare?"
description: "Ce presupune închiderea conturilor de TVA în contabilitatea unei firme în lichidare și ce rămâne de făcut manual, în afara aplicației."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum închid TVA-ul unei firme care intră în lichidare?

Închiderea TVA la o firmă în lichidare are două fețe distincte: pe de o parte, închiderea contabilă a soldurilor conturilor de TVA în cadrul operațiunilor de lichidare; pe de altă parte, modificarea/radierea efectivă a calității de plătitor de TVA în vectorul fiscal la ANAF.

## Temeiul legal

::: ghid-temei
Ordinul MFP nr. 897/2015, art. 1: „Se aprobă Normele metodologice privind reflectarea în contabilitate a principalelor operațiuni de fuziune, divizare, dizolvare și lichidare a societăților [...], cuprinse în anexa nr. 1, care face parte integrantă din prezentul ordin."
:::

Normele metodologice propriu-zise, cu monografiile contabile detaliate, sunt publicate separat, ca anexă la ordin, în Monitorul Oficial — textul ordinului citat mai sus doar le aprobă, fără a le reda integral.

## Ce se greșește în practică

- Se confundă închiderea contabilă a soldurilor de TVA (parte din procesul de lichidare) cu radierea calității de plătitor de TVA în vectorul fiscal, care e un demers administrativ separat, la ANAF.
- Se presupune că, odată închise conturile de TVA în contabilitate, firma este automat scoasă din evidența plătitorilor de TVA — cele două nu sunt echivalente.

## Ce face iConta.eu

Funcționalitatea de lichidare/radiere din iConta.eu include, printre cele patru etape ale procesului, închiderea TVA-ului și a impozitelor curente prin transferul rezultatului în contul 121, alături de valorificarea activelor, încasarea creanțelor/plata datoriilor și partajul final.

Modificarea vectorului fiscal (inclusiv radierea calității de plătitor de TVA), care se face de regulă printr-o declarație de mențiuni (D700), **nu este generată de iConta.eu** — funcționalitatea a fost respinsă tehnic, întrucât acest formular nu are un validator XML oficial disponibil pentru depunere de sine stătătoare. Acest pas trebuie parcurs manual, în afara aplicației.

[iConta.eu](/)
