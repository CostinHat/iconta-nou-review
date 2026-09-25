---
title: "Cum corectezi o încasare bancară înregistrată pe clientul greșit?"
description: "Cum se corectează, conform reglementărilor contabile, o eroare de alocare a unei încasări bancare pe un alt client decât cel real, prin stornare."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum corectezi o încasare bancară înregistrată pe clientul greșit?

Când o încasare bancară a fost alocată din greșeală altui client decât cel care a plătit efectiv, corectarea nu înseamnă „ștergerea" notei contabile greșite — reglementările contabile cer stornarea ei și înregistrarea corectă, la data la care eroarea a fost constatată.

## Temeiul legal

::: ghid-temei
„65. - (1) Erorile constatate în contabilitate se pot referi fie la exercițiul financiar curent, fie la exercițiile financiare precedente. (2) Corectarea erorilor se efectuează la data constatării lor. [...] 69. - Înregistrarea stornării unei operațiuni contabile aferente exercițiului financiar curent se efectuează fie prin corectarea cu semnul minus a operațiunii inițiale (stornare în roșu), fie prin înregistrarea inversă a acesteia (stornare în negru), în funcție de politica contabilă și programele informatice utilizate."
— OMFP 1802/2014 pentru aprobarea Reglementărilor contabile privind situațiile financiare anuale individuale și situațiile financiare anuale consolidate, pct. 65 și pct. 69, Secțiunea 2.5.2 „Corectarea erorilor contabile" (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Practic, corectarea unei încasări alocate greșit unui client presupune:

- **Corectarea se face la data constatării erorii** (pct. 65 alin. 2) — nu se rescrie data operațiunii inițiale, iar corecția însăși se datează când s-a observat problema.
- **Stornarea** operațiunii inițiale (nota greșită, pe clientul eronat) se face fie „în roșu" (aceeași notă, cu semnul minus), fie „în negru" (nota inversă) — alegerea între cele două depinde de politica contabilă a firmei și de programul informatic folosit.
- **Reînregistrarea corectă**, pe clientul real, urmează stornării — soldul clientului greșit revine la valoarea dinaintea erorii, iar clientul corect primește încasarea care i se cuvine de fapt.
- Dacă eroarea aparține unui exercițiu financiar închis anterior și e semnificativă, corectarea nu se face pe contul de profit și pierdere al exercițiului curent, ci pe rezultatul reportat (contul 1174 „Rezultatul reportat provenit din corectarea erorilor contabile", conform pct. 67 alin. 2 din aceleași reglementări).

## Ce se greșește în practică

- Se editează direct nota contabilă greșită, schimbând clientul fără să rămână nicio urmă a corecției — pct. 69 cere stornare (în roșu sau în negru), nu suprascrierea silențioasă a înregistrării inițiale.
- Se corectează eroarea „la data operațiunii inițiale", ca și cum nu s-ar fi întâmplat niciodată — corect e ca stornarea și reînregistrarea să poarte data la care eroarea a fost efectiv constatată (pct. 65 alin. 2).
- Se corectează eroarea direct pe rezultatul curent, deși aparține unui exercițiu financiar anterior deja închis și e semnificativă ca valoare — în acest caz corecția trebuie să treacă prin rezultatul reportat (cont 1174), nu prin contul de profit și pierdere al anului curent.

## Ce face iConta.eu

iConta.eu oferă evidența contabilă generală a operațiunilor bancare și a soldurilor pe fiecare client (`core/banca.py`, `core/repo_banca.py`). Mecanismul de stornare din cod e implementat azi doar pentru facturi (`core/facturi.py: storno()`, `core/facturi_api.py: storneaza()`, expus prin ruta `facturi_storno`) — nu există un mecanism generic de stornare pentru o notă contabilă provenită dintr-o linie de extras bancar alocată greșit unui client; corectarea unei astfel de note (stornare + reînregistrare pe clientul corect) se face azi manual de contabil, folosind principiile de stornare din normă, nu printr-o funcție dedicată a aplicației. De asemenea, identificarea automată a faptului că o încasare a fost alocată unui client greșit (de exemplu, prin potrivirea denumirii plătitorului din extrasul bancar cu un alt client din baza de date) nu e automatizată — semnalarea unei posibile alocări eronate rămâne o verificare pe care contabilul o face manual, pe baza extrasului bancar și a soldurilor clienților.

[iConta.eu](/)
