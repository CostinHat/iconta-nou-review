---
title: "Cum corectez o factură după depunerea D394?"
description: "Ce prevede OPANAF 2194/2025 despre rectificativa D394 — de ce e o declarație nouă, completă, care înlocuiește integral declarația inițială, și ce excepție există pentru facturile primite cu întârziere."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum corectez o factură după depunerea D394?

D394 nu are un formular separat de „rectificativă" în sensul în care îl are D300. Dacă descoperi, după depunere, o factură omisă sau greșit raportată, corectarea se face printr-o **declarație nouă, completă**, care înlocuiește integral declarația depusă inițial pentru acea perioadă — nu printr-un supliment care adaugă doar diferența.

## Temeiul legal

::: ghid-temei
„persoana impozabilă constată existenţa unor omisiuni/erori... trebuie să depună o nouă declaraţie corect completată cu operaţiunile care necesită modificarea şi/sau operaţiunile care nu au fost declarate, declaraţie care înlocuieşte declaraţia informativă depusă iniţial. Nu vor face obiectul redepunerii declaraţiei facturile primite de persoana impozabilă în altă perioadă de raportare faţă de data emiterii acestora de către furnizori."
— OPANAF 2194/2025 (care modifică Anexa 2 a OPANAF 3769/2015), Anexa 2 pct. 3 (sursă: anaf_surse/opanaf_2194_2025_d394.txt)
:::

Două lucruri esențiale de reținut din text:

- **Nu depui o „diferență"**, depui **toată declarația din nou**, corect completată — inclusiv operațiunile deja corect raportate prima dată, pe lângă cea corectată sau omisă. Declarația nouă înlocuiește integral declarația inițială pentru acea perioadă.
- **Excepția explicită**: o factură primită de firmă într-o perioadă de raportare diferită de data ei de emitere (tipic o factură de la furnizor ajunsă cu întârziere) **nu obligă la redepunerea declarației** perioadei de emitere — ea se declară în perioada în care a fost efectiv primită, nu impune corectarea retroactivă a unei declarații deja depuse.
- Procedural, dacă la afișarea stării declarației apar erori de validare, contribuabilul are un **termen de 3 zile lucrătoare** să le corecteze și să redepună (regulă din Anexa 3, neschimbată de OPANAF 2194/2025).

## Ce se greșește în practică

- Se încearcă redepunerea unei „diferențe" (doar factura corectată), ca la o rectificativă de tip D300, deși D394 cere declarația completă, cu tot ce era deja declarat corect.
- Se redepune declarația unei perioade anterioare de fiecare dată când sosește o factură de furnizor înregistrată cu întârziere, deși excepția din Anexa 2 pct. 3 scutește exact acest caz — factura se declară în perioada primirii, nu se corectează retroactiv perioada de emitere.
- Se confundă anexele modificate: OPANAF 2194/2025 a înlocuit doar Anexele 1 și 2 ale OPANAF 3769/2015; Anexa 3 (procedura de gestiune, inclusiv termenul de 3 zile pentru corectarea erorilor de validare) a rămas cea din 2015 — un ghid sau un contabil care citează „instrucțiunile D394" fără să distingă anexa riscă să amestece text din două versiuni.

## Ce face iConta.eu

D394 se generează în iConta.eu din aceeași tabelă de facturi (`facturi`/`factura_linii`) folosită și de restul aplicației, prin `core/d394.py` + `core/repo_d394.py`. Când o factură se corectează sau se adaugă ulterior depunerii inițiale, regenerarea D394 pentru acea perioadă produce automat **declarația completă**, cu toate operațiunile perioadei — exact forma cerută de lege pentru o redepunere (nu o declarație parțială), fiindcă generatorul nu are un mod „doar diferența".

Înainte ca fișierul regenerat să fie considerat gata de redepus, aplicația rulează aceleași două garduri ca la depunerea inițială: validarea cu **DUKIntegrator** (validatorul oficial ANAF, local) și **a doua cale de calcul independentă** (`core/d394_reconciliere.py`), care recalculează totalurile pe cotă direct din liniile brute și oprește generarea dacă diferă de rezultatul generatorului. Depunerea efectivă a declarației redepuse rămâne, ca și la depunerea inițială, manuală, prin portalul SPV — iConta nu are o funcție de transmitere automată la ANAF.

Aplicația **nu are** o funcționalitate care să aplice automat excepția facturilor primite cu întârziere (nu marchează sau exclude singură din redepunere o factură primită într-o altă perioadă decât cea de emitere) — decizia de a include sau nu o astfel de factură într-o redepunere rămâne a contabilului, pe baza excepției citate mai sus.

[iConta.eu](/)
