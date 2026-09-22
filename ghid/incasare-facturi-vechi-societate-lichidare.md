---
title: Mai poate o societate în lichidare să încaseze facturi vechi?
description: Da — societatea în lichidare își păstrează personalitatea juridică exact pentru a finaliza operațiunile în curs, inclusiv încasarea creanțelor vechi, dar aplicația nu are o operațiune dedicată pentru asta, ci se folosește motorul general de facturare.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Mai poate o societate în lichidare să încaseze facturi vechi?

Da. Lichidarea nu îngheață relația firmei cu clienții ei — dimpotrivă, încasarea creanțelor vechi este parte firească a procesului de lichidare, iar legea prevede explicit că societatea își păstrează personalitatea juridică tocmai pentru asta.

## Temeiul legal

::: ghid-temei
**Legea 31/1990, art.233 alin.(4):**
"Societatea își păstrează personalitatea juridică pentru operațiunile lichidării, până la terminarea acesteia."

**Legea 31/1990, art.252 alin.(4)-(5):**
"În afară de dispozițiile prezentului titlu, se aplică societăților în lichidare regulile stabilite prin actul constitutiv și prin lege, în măsura în care nu sunt incompatibile cu lichidarea." ... "Toate actele emanând de la societate trebuie să arate că aceasta este în lichidare."
:::

## De ce încasarea creanțelor vechi este obligatorie, nu opțională

Etapele lichidării includ explicit valorificarea activelor și încasarea creanțelor, alături de plata datoriilor — abia după acestea se ajunge la partajul final către asociați. Legea impune ca plata către asociați să nu se facă înaintea achitării creditorilor societății, ceea ce înseamnă indirect că firma trebuie să-și maximizeze mai întâi patrimoniul disponibil — inclusiv prin recuperarea facturilor vechi neîncasate — înainte de a distribui orice către asociați.

Cât timp lichidarea nu s-a terminat, societatea continuă să existe ca persoană juridică și poate emite facturi, urmări debitori și încasa sume — cu condiția ca toate actele emise să arate explicit că societatea este în lichidare.

## Ce se greșește în practică

- Se crede că, odată începută lichidarea, firma nu mai poate emite sau încasa facturi — de fapt trebuie să continue exact aceste operațiuni pentru a-și finaliza patrimoniul.
- Se emit facturi pe parcursul lichidării fără mențiunea obligatorie "societate în lichidare".
- Se lasă creanțele vechi neurmărite, reducând inutil suma disponibilă pentru plata creditorilor și, ulterior, pentru partaj.

## Ce face iConta.eu

Încasarea creanțelor este parte din procesul de lichidare descris în documentația motorului aplicației, dar nu are o funcție dedicată în modulul de lichidare — se folosește motorul general de facturare și încasări al aplicației, exact ca pentru orice altă operațiune curentă a firmei. Motorul de lichidare propriu-zis (`core/lichidare.py`) acoperă doar două note contabile punctuale: vânzarea unui mijloc fix în timpul lichidării și partajul final către asociați.

[iConta.eu](/)
