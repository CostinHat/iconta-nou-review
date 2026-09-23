---
title: Cum verific rapid ce clienți au D406 nedepusă?
description: Pastila roșie din lista de portofoliu marchează firmele cu restanțe — un clic pe fiecare arată exact dacă restanța e la D406 sau la altă declarație.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum verific rapid ce clienți au D406 nedepusă?

Când portofoliul are zeci de firme, verificarea manuală a D406 firmă cu firmă nu e practică. Semaforul de conformare fiscală rezolvă exact acest caz: firmele cu restanțe ies vizual în evidență, iar detaliul spune dacă restanța e la D406 sau la alta dintre cele 9 declarații urmărite.

## Temeiul legal

::: ghid-temei
„Declaraţia informativă D406 se transmite în format electronic, data-limită de transmitere fiind: - ultima zi calendaristică a lunii următoare perioadei de raportare, respectiv luna/trimestrul calendaristic, după caz, pentru alte informaţii decât cele privind secţiunile «Stocuri» şi «Active»..."

*(OPANAF nr. 1783/2021, Anexa 4, pct. 1)*
:::

## Cum arăți rapid restanțele de D406

1. Deschizi ecranul de Control fiscal — lista de firme e sortată automat cu restanțele (pastilă roșie) primele.
2. Fiecare firmă cu pastilă roșie afișează numărul de declarații restante direct în listă.
3. Dai clic pe firmă pentru detaliu — verdictul complet arată exact care declarații sunt restante, cu motivul pentru fiecare; D406 apare separat de celelalte 8, cu propriul termen calculat (ultima zi a lunii următoare perioadei de raportare).
4. Firmele marcate „gri" (nu se pot verifica) nu înseamnă că D406 e la zi — înseamnă că lipsește o informație din profil (de exemplu regimul de TVA) necesară pentru a decide periodicitatea D406; acestea merită verificate separat, nu ignorate.

## Ce se greșește în practică

- Se citește doar sumarul de portofoliu („X firme cu restanță"), fără să se intre pe fiecare firmă pentru a vedea dacă restanța e chiar la D406 sau la altă declarație din cele 9.
- Se tratează starea „gri" ca fiind echivalentă cu „la zi" — de fapt înseamnă că semaforul nu are suficiente date pentru a decide, ceea ce, pentru D406, apare tipic când regimul de TVA al firmei nu e completat.

## Ce face iConta.eu

Funcția `obligatii_datorate()` din modulul F022 (`core/control_fiscal_api.py`) evaluează D406 separat pentru fiecare firmă din portofoliu, cu reguli distincte după regimul de TVA: plătitorii cu perioadă lunară primesc verdict lunar, cei cu perioadă trimestrială/semestrială/anuală și neplătitorii de TVA primesc verdict trimestrial. Fiecare restanță de D406 poartă motivul explicit — un termen deja depășit fără declarație confirmată ca depusă — vizibil în detaliul firmei, nu doar în sumarul de portofoliu.

[iConta.eu](/)
