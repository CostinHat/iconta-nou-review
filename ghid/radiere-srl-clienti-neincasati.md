---
title: Pot radia un SRL care mai are clienți neîncasați?
description: Situația financiară finală de lichidare trebuie să arate explicit situația creanțelor, deci creanțele neîncasate trebuie recuperate sau tratate contabil corect înainte de radiere — după radiere, firma nu mai există ca să le urmărească.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Pot radia un SRL care mai are clienți neîncasați?

Din punct de vedere strict formal, nu există o interdicție explicită de radiere cât timp mai există creanțe neîncasate — dar legea cere ca situația creanțelor să fie prezentată clar în dosarul de radiere, iar practic, odată radiată, firma nu mai are cine să urmărească acei debitori.

## Temeiul legal

::: ghid-temei
**Legea 31/1990, art.233 alin.(4):**
"Societatea își păstrează personalitatea juridică pentru operațiunile lichidării, până la terminarea acesteia."

**Legea 31/1990, art.253 alin.(3):**
"Lichidatorii sunt datori, îndată după preluarea funcției, ca împreună cu directorii și administratorii... să facă un inventar și să încheie un bilanț, care să constate situația exactă a activului și pasivului societății, și să le semneze."

**Legea 31/1990, art.260 alin.(6):**
"În termen de 15 zile de la terminarea lichidării, lichidatorii vor depune la registrul comerțului cererea de radiere a societății din registrul comerțului, pe baza raportului final de lichidare și a situațiilor financiare de lichidare prin care se prezintă situația patrimoniului, a creanțelor și repartizarea activelor rămase, după caz..."
:::

## Ce cere legea despre creanțe la radiere

Cererea de radiere se depune pe baza raportului final și a situațiilor financiare de lichidare, care trebuie să prezinte explicit "situația patrimoniului, a creanțelor și repartizarea activelor rămase" (art.260 alin.6). Cu alte cuvinte, creanțele neîncasate nu pot fi pur și simplu omise din dosar — trebuie fie recuperate înainte de radiere, fie tratate contabil corect (scoase din evidență ca pierdere, cu documentele care justifică asta), astfel încât situația prezentată să fie completă și corectă.

Cât timp societatea își păstrează personalitatea juridică pentru operațiunile lichidării (art.233 alin.4), ea are cadrul legal să urmărească și să încaseze acei clienți. După radiere, personalitatea juridică încetează — iar cadrul simplu de urmărire a debitorilor în nume propriu dispare odată cu ea.

## Ce se greșește în practică

- Se radiază firma cu facturi neîncasate active, sperând că situația "se rezolvă de la sine" ulterior — de fapt, după radiere, nu mai există cine să urmărească acele creanțe în numele firmei.
- Se omite menționarea creanțelor neîncasate din situația financiară finală de lichidare, deși legea cere prezentarea explicită a situației creanțelor.
- Se confundă o creanță greu de recuperat cu una tratată corect contabil — scoaterea din evidență ca pierdere are nevoie de documentație și justificare, nu se face doar prin omisiune din raportul final.

## Ce face iConta.eu

La fel ca la încasarea altor creanțe vechi pe parcursul lichidării, motorul dedicat de lichidare al aplicației nu are o funcție specifică pentru gestionarea creanțelor neîncasate — se folosește motorul general de facturare/încasări. Modulul de lichidare (`core/lichidare.py`) nu conține nicio validare care să blocheze sau să semnaleze existența unor creanțe neîncasate înainte de a rula partajul — este strict un calculator ("zero SQL, zero db"), fără acces la evidența creanțelor. Confirmarea că situația creanțelor este corect prezentată în dosarul de radiere rămâne responsabilitatea contabilului.

[iConta.eu](/)
