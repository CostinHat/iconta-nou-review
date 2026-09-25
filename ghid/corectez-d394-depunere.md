---
title: "Cum corectez D394 după depunere?"
description: "Procedura legală de rectificare a declarației 394 — o declarație nouă, completă, care înlocuiește integral pe cea depusă greșit — și ce automatizează iConta.eu în acest proces."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum corectez D394 după depunere?

D394 nu are un formular separat de „rectificativă". Când se descoperă o eroare sau o omisiune, contribuabilul depune o declarație nouă, completă, pentru aceeași perioadă — care înlocuiește integral declarația depusă inițial.

## Temeiul legal

::: ghid-temei
„persoana impozabilă constată existenţa unor omisiuni/erori... trebuie să depună o nouă declaraţie corect completată cu operaţiunile care necesită modificarea şi/sau operaţiunile care nu au fost declarate, declaraţie care înlocuieşte declaraţia informativă depusă iniţial. Nu vor face obiectul redepunerii declaraţiei facturile primite de persoana impozabilă în altă perioadă de raportare faţă de data emiterii acestora de către furnizori."
— OPANAF 2194/2025, Anexa 2 pct.3 (sursă: anaf_surse/opanaf_2194_2025_d394.txt:756-760)
:::

- Corectarea nu se face prin adăugarea unor rânduri la declarația veche, ci prin depunerea unei **declarații complet noi**, pentru aceeași perioadă, care înlocuiește integral declarația greșită.
- Noua declarație trebuie să conțină atât operațiunile care necesitau modificarea, cât și cele care nu fuseseră declarate deloc inițial.
- Excepția din 2025: dacă o factură primită a fost înregistrată de furnizor în altă perioadă de raportare decât cea în care a fost emisă, această diferență **nu** obligă la redepunerea declarației — excepție care nu exista în textul din 2015.
- Separat, dacă la afișarea stării declarației pe portalul ANAF apar erori de validare, contribuabilul are „**termen de 3 zile lucrătoare**" să le corecteze și să redepună declarația (procedură rămasă neschimbată din 2015, Anexa 3).

## Ce se greșește în practică

- Se încearcă „adăugarea" unor operațiuni omise printr-o declarație parțială, în loc de o declarație nouă și completă pentru toată perioada.
- Se redepune declarația doar pentru o factură primită târziu de la furnizor, deși legea scutește explicit de redepunere acest caz (factură emisă de furnizor în altă perioadă de raportare decât cea în care a ajuns la beneficiar).
- Se ignoră termenul de 3 zile lucrătoare pentru corectarea erorilor semnalate de portalul ANAF, ceea ce poate bloca validarea declarației.

## Ce face iConta.eu

Fișierul D394 generat de iConta trece printr-o validare locală, pe validatorul oficial ANAF instalat (`core/duk.py`, funcția `valideaza()`), înainte de a fi considerat gata de depus — deci erorile de structură sunt prinse înainte de trimitere, nu după. În plus, generatorul rulează o a doua cale de calcul, independentă (`core/d394_reconciliere.py`), care recalculează totalurile pe cotă direct din liniile brute ale facturilor și **oprește generarea** dacă rezultatul diferă de cel al generatorului principal — semnalând divergența înainte ca fișierul greșit să ajungă la depunere.

Ce nu face iConta: nu depune automat la ANAF (nici declarația inițială, nici o eventuală redepunere) — depunerea rămâne manuală, prin portalul SPV, cu fișierul deja validat local. Regenerarea unei declarații complete pentru o perioadă deja depusă se face din nou, din datele curente ale firmei pentru acea lună/trimestru — aplicația nu ține o evidență separată de „ce s-a schimbat față de depunerea anterioară", așa că verificarea diferențelor rămâne responsabilitatea contabilului.

[iConta.eu](/)
