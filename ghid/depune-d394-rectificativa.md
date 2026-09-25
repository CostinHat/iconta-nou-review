---
title: "Se poate depune D394 rectificativă?"
description: "D394 nu are un formular distinct de rectificativă: corecția se face printr-o declarație nouă, completă, care înlocuiește integral declarația depusă inițial pentru aceeași perioadă."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Se poate depune D394 rectificativă?

Nu în sensul clasic de „declarație rectificativă" separată. La D394, corecția înseamnă depunerea unei noi declarații, complete, pentru aceeași perioadă, care ia locul celei depuse inițial.

## Temeiul legal

::: ghid-temei
„persoana impozabilă constată existenţa unor omisiuni/erori [...] trebuie să depună o nouă declaraţie corect completată cu operaţiunile care necesită modificarea şi/sau operaţiunile care nu au fost declarate, declaraţie care înlocuieşte declaraţia informativă depusă iniţial."
— OPANAF 2194/2025, Anexa 2 pct. 3 (sursă: anaf_surse/opanaf_2194_2025_d394.txt)
:::

Câteva precizări importante despre acest mecanism:

- Nu există o bifă distinctă „declarație rectificativă" pe formularul D394, spre deosebire de alte declarații (ex. D212, unde rectificarea e marcată explicit pe document).
- Declarația nouă trebuie să conțină **toate** operațiunile perioadei, corect completate — cele deja declarate corect, plus corecțiile/adăugările — pentru că înlocuiește integral declarația anterioară, nu o completează.
- Excepție: facturile primite de firmă într-o altă perioadă de raportare decât cea a emiterii lor de către furnizor nu fac obiectul redepunerii pentru acea diferență.
- Separat de acest mecanism de fond, dacă portalul semnalează erori de structură la afișarea stării declarației deja depuse, contribuabilul are termen de **3 zile lucrătoare** să corecteze și să redepună (Anexa 3, rămasă neschimbată din 2015).

## Ce se greșește în practică

- Se caută în aplicație o funcție separată „D394 rectificativă" — nu există, pentru că legea nu prevede o formă distinctă; corecția e tot o declarație normală, redepusă.
- Se redepune doar diferența (operațiunea corectată/omisă), fără restul operațiunilor deja declarate corect — riscă să șteargă din declarație operațiuni valide, pentru că noua depunere înlocuiește integral cea veche.
- Se amestecă terminologia: Anexa 3 (termenul de 3 zile lucrătoare) tratează erori de structură semnalate de portal, nu corectarea de fond a conținutului declarației, descrisă în Anexa 2 pct. 3.

## Ce face iConta.eu

Generatorul D394 (`core/d394.py`) reconstruiește declarația din tabela unică de facturi a firmei la fiecare generare, pentru perioada cerută — nu păstrează „diferențe" față de o depunere anterioară. Regenerarea, după corectarea sau completarea evidenței (facturi, operațiuni manuale de tip bonuri/borderouri), produce automat o declarație nouă, completă, exact forma cerută de Anexa 2 pct. 3 pentru corecție.

Înainte de a considera fișierul gata, aplicația îl rulează prin validatorul oficial ANAF instalat local (`core/duk.py`). **Depunerea rămâne manuală, prin portalul SPV** — iConta.eu nu depune automat la ANAF, nici la prima declarație, nici la o redepunere corectivă.

[iConta.eu](/)
