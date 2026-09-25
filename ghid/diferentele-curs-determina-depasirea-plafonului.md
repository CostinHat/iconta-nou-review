---
title: "Diferențele de curs pot determina depășirea plafonului micro?"
description: "Cum se verifică plafonul de venituri al microîntreprinderilor și de ce cursul valutar folosit la calculul echivalentului în euro este fixat, nu variabil pe parcursul anului."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Diferențele de curs pot determina depășirea plafonului micro?

Multe firme cu venituri parțial în valută se întreabă dacă fluctuațiile cursului de schimb din timpul anului le pot împinge, „artificial", peste plafonul de venituri al microîntreprinderilor. Răspunsul scurt este că legea folosește un curs de schimb fix pentru verificarea plafonului — nu cursul zilei fiecărei încasări — dar asta nu înseamnă că diferențele de curs sunt complet irelevante pentru acest calcul.

## Temeiul legal

::: ghid-temei
„(5) Limitele fiscale prevăzute la alin. (1) se verifică pe baza veniturilor înregistrate cumulat de la începutul anului fiscal. Cursul de schimb pentru determinarea echivalentului în euro este cel valabil la închiderea exercițiului financiar precedent."
— Codul fiscal (Legea 227/2015), art. 52 alin. (5) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

::: ghid-temei
„a realizat venituri care nu au depășit echivalentul în lei a 100.000 euro. Cursul de schimb pentru determinarea echivalentului în euro este cel valabil la închiderea exercițiului financiar în care s-au înregistrat veniturile;"
— Codul fiscal (Legea 227/2015), art. 47 alin. (1) lit. c) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Verificarea plafonului micro în cursul anului (dacă firma rămâne microîntreprindere sau trebuie să treacă la impozit pe profit) se face cumulat de la începutul anului fiscal, dar echivalentul în euro se calculează la un **curs de schimb fix**: cel de la închiderea exercițiului financiar **precedent** (art. 52 alin. (5)). Astfel, mișcările cursului valutar din timpul anului curent nu schimbă, în sine, pragul euro-lei folosit pentru verificarea intermediară a plafonului.
- Pentru verificarea condiției de eligibilitate la 31 decembrie a anului anterior (art. 47 alin. (1) lit. c) — plafonul de 100.000 euro), cursul folosit este cel de la închiderea exercițiului financiar **în care s-au realizat veniturile respective** — deci cursul de la sfârșitul anului anterior, nu cursul curent.
- Ceea ce poate totuși duce indirect la depășirea plafonului sunt diferențele de curs valutar contabilizate ca venituri financiare (de exemplu diferențele favorabile de curs valutar din decontarea unor creanțe/datorii în valută) — acestea intră, ca orice alt venit, în cifra de afaceri cumulată de la începutul anului care se compară cu pragul, chiar dacă mecanismul de conversie euro-lei al pragului însuși rămâne fixat la cursul de închidere a exercițiului anterior.

## Ce se greșește în practică

- Se crede că un curs valutar în creștere, în cursul anului, „reduce automat" spațiul până la plafonul micro — de fapt pragul de comparație în euro folosește un curs fix (de la închiderea exercițiului precedent), nu cursul curent al fiecărei zile.
- Se omit diferențele de curs valutar favorabile (venituri financiare din reevaluarea creanțelor/datoriilor în valută) din calculul veniturilor cumulate care se compară cu plafonul, deși acestea sunt venituri ca oricare altele și intră în baza de verificare.
- Se folosește greșit cursul de la data fiecărei încasări în valută pentru verificarea plafonului anual, în loc de cursul unic, fix, prevăzut de lege pentru acest calcul.

## Ce face iConta.eu

La verificarea codului, iConta.eu nu are, în prezent, o constantă sau o funcție dedicată verificării automate a plafonului micro de venituri — un comentariu explicit din codul aplicației (`control_fiscal_api.py`) confirmă acest lucru: „nicio constantă de plafon micro în `core/`". Aplicația gestionează generarea declarațiilor de impozit (D100 pentru regimul micro, D101 pentru impozit pe profit) în funcție de regimul fiscal introdus de utilizator, dar nu calculează și nu alertează automat asupra apropierii sau depășirii pragului de 100.000 euro — această verificare, inclusiv efectul diferențelor de curs valutar asupra ei, rămâne în prezent responsabilitatea contabilului.

[iConta.eu](/)
