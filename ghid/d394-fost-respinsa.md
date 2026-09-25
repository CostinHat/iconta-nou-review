---
title: "Ce fac dacă D394 a fost respinsă?"
description: "Procedura pentru o D394 respinsă de portal: 3 zile lucrătoare pentru corectare și redepunere, plus validarea locală prin validatorul oficial ANAF folosită de iConta.eu înainte de depunere."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce fac dacă D394 a fost respinsă?

Dacă portalul ANAF afișează erori la starea declarației, ai un termen scurt și clar pentru corectare: 3 zile lucrătoare de la data la care erorile devin vizibile.

## Temeiul legal

::: ghid-temei
„3.5. În cazul în care pe pagina de vizualizare a stării declaraţiei (394) se afişează un mesaj cu erorile pe care le conţine documentul depus, contribuabilul trebuie ca, în termen de 3 zile lucrătoare, să corecteze toate erorile comunicate şi să reia procesul de depunere a declaraţiei (394)."
— OPANAF 3769/2015, Anexa 3 pct. 3.5 (sursă: anaf_surse/opanaf_3769_2015_d394_baza.txt) — procedură rămasă neschimbată, OPANAF 2194/2025 a înlocuit doar Anexele 1 și 2
:::

Ce rezultă concret din acest text:

- Termenul de **3 zile lucrătoare** curge de la data la care erorile apar la afișarea stării declarației pe portal, nu de la data depunerii inițiale.
- În acest interval, contribuabilul trebuie să corecteze conținutul declarației și **să o redepună**, nu doar să răspundă unei notificări.
- Anexa 3, care conține această procedură, nu a fost modificată de OPANAF 2194/2025 — actul din 2025 a înlocuit doar Anexele 1 și 2 (obligativitate + structură/etichete), deci termenul de 3 zile rămâne cel din 2015.

## Ce se greșește în practică

- Se confundă „declarație respinsă la validare" (eroare de structură XML, prinsă înainte de depunere) cu „declarație respinsă de portal după depunere" — primul caz se rezolvă local, înainte de a trimite fișierul; al doilea intră sub termenul de 3 zile lucrătoare.
- Se lasă corectarea pe mai târziu, „când e timp" — termenul de 3 zile lucrătoare e scurt și curge indiferent de programul contabilului.
- Se presupune că respingerea înseamnă automat amendă — nu e cazul dacă redepunerea corectă se face în termen; amenda vizează nedepunerea, nu o eroare corectată la timp.

## Ce face iConta.eu

Înainte ca fișierul D394 să fie considerat gata de depus, aplicația îl rulează prin **validatorul oficial ANAF instalat local** (`core/duk.py`, funcția `valideaza(xml, tip, an, luna)`) — aceeași unealtă (DUK) pe care o folosește și portalul ANAF pentru verificarea structurală. Asta reduce riscul unei respingeri de structură la depunere, pentru că majoritatea erorilor de acest tip sunt prinse local, înainte de a ajunge pe portal.

Separat, D394 are o a doua cale de calcul, independentă (`core/d394_reconciliere.py`), care recalculează totalurile pe cotă direct din liniile facturilor și **oprește generarea** dacă rezultatul diferă de cel al generatorului principal — un al doilea gard de conținut, nu doar de structură XML.

Dacă, în ciuda acestor verificări, portalul ANAF semnalează totuși erori după depunere, corectarea propriu-zisă a conținutului și redepunerea în termenul de 3 zile lucrătoare rămân un pas manual: **iConta.eu nu depune și nu redepune automat la ANAF** — fișierul verificat local se transmite prin portalul SPV.

[iConta.eu](/)
