---
title: "Cum transform o II în SRL"
description: "De ce trecerea de la o întreprindere individuală la un SRL nu e o transformare juridică, ci o radiere fiscală urmată de o constituire nouă."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum transform o II în SRL

Întreprinderea individuală (II) e o formă de organizare a persoanei fizice autorizate, reglementată de un act distinct de legea societăților. Din acest motiv, „transformarea" unei II într-un SRL nu este o operațiune juridică unică, de tipul transformărilor prevăzute de Legea nr. 31/1990 pentru societăți (SRL în SA, de exemplu) — este, de fapt, încetarea II-ului urmată de constituirea unui SRL nou, cu personalitate juridică proprie.

## Temeiul legal

```
::: ghid-temei
„(2) La încetarea calității de subiect de drept fiscal, persoanele sau entitățile înregistrate fiscal prin declarație de înregistrare fiscală potrivit art. 81 și 82 trebuie să solicite radierea înregistrării fiscale, prin depunerea unei declarații de radiere. Declarația se depune în termen de 30 de zile de la încetarea calității de subiect de drept fiscal și trebuie însoțită de certificatul de înregistrare fiscală în vederea anulării acestuia."
— Legea nr. 207/2015 privind Codul de procedură fiscală, art. 90 alin. (2) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::
```

Ce rezultă, punând cap la cap ce se poate confirma din sursele disponibile:

- **Regimul juridic al II-ului** (înființare, funcționare, încetare) e reglementat prin OUG nr. 44/2008 privind desfășurarea activităților economice de către persoanele fizice autorizate, întreprinderile individuale și întreprinderile familiale — act care, la data acestui ghid, nu se regăsește în corpusul de surse (anaf_surse) folosit pentru redactare, deci nu redăm din el citate.
- **Ce se poate confirma cu certitudine** din Codul de procedură fiscală: la încetarea activității II-ului, titularul are obligația de a depune declarația de radiere fiscală în **30 de zile**, așa cum se întâmplă pentru orice subiect de drept fiscal care își încetează activitatea.
- **Constituirea SRL-ului** e o operațiune separată, reglementată de Legea nr. 31/1990 (act constitutiv, capital social minim, înmatriculare la registrul comerțului) — un SRL nou, cu CUI propriu, nu preia automat istoricul fiscal, contractele sau autorizațiile II-ului.
- Diferența practică majoră: II-ul răspunde cu patrimoniul de afectațiune (și, subsidiar, cu tot patrimoniul persoanei fizice), în timp ce SRL-ul are răspundere limitată la capitalul social — ceea ce e, de obicei, motivul real al „transformării" dorite.

## Ce se greșește în practică

- Se caută o procedură de „transformare directă" II → SRL, de tipul celor prevăzute pentru transformarea unei societăți dintr-o formă în alta (art. 31 și urm. din Legea nr. 31/1990) — o astfel de procedură nu există pentru II, pentru că II nu e o societate în sensul acelei legi.
- Se presupune că SRL-ul nou preia automat contractele, autorizațiile sau istoricul fiscal al II-ului — de fapt, fiecare contract trebuie cesionat sau renegociat, iar SRL-ul pornește cu istoric fiscal propriu, de la zero.
- Se amână depunerea declarației de radiere fiscală a II-ului peste termenul de 30 de zile, considerând-o o formalitate secundară față de înființarea SRL-ului.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu automatizează** nici radierea fiscală a unei II, nici constituirea unui SRL — nu a fost găsită în `core/` nicio funcționalitate dedicată acestor proceduri administrative. Aplicația poate ține evidența contabilă separată a celor două entități (II-ul, până la încetare, și SRL-ul, de la constituire), dar pașii legali de închidere a uneia și deschidere a celeilalte rămân, la acest moment, în sarcina titularului/contabilului, prin canalele obișnuite (ONRC pentru II și SRL, ANAF pentru radierea/înregistrarea fiscală).

[iConta.eu](/)
