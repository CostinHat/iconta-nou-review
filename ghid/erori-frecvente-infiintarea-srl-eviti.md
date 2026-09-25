---
title: "Erori frecvente la înființarea unui SRL și cum le eviți"
description: "Elementele obligatorii ale actului constitutiv al unui SRL, conform art. 7 din Legea 31/1990, și cum lipsa lor complică înmatricularea."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Erori frecvente la înființarea unui SRL și cum le eviți

Majoritatea întârzierilor la înmatricularea unui SRL nu vin din complexitatea procedurii, ci din lipsa unui element obligatoriu din actul constitutiv — un document care are un conținut minim clar stabilit de lege, nu la liberă alegere.

## Temeiul legal

::: ghid-temei
„Articolul 7
Actul constitutiv al societății în nume colectiv, în comandită simplă sau cu răspundere limitată va cuprinde:
a) datele de identificare a asociaților; [...]
b) forma, denumirea și sediul social;
c) obiectul de activitate al societății, cu precizarea domeniului și a activității principale;
d) capitalul social subscris, cu menționarea aportului fiecărui asociat, în numerar sau în natură, valoarea aportului în natură, modul evaluării acestuia; la societățile cu răspundere limitată se vor preciza numărul și valoarea nominală a părților sociale, precum și numărul părților sociale atribuite fiecărui asociat pentru aportul său;
[...]
e) asociații care reprezintă și administrează societatea sau administratorii neasociați, datele lor de identificare, durata mandatului, puterile ce li s-au conferit și dacă ei urmează să le exercite împreună sau separat;
[...]
f) partea fiecărui asociat la beneficii și la pierderi;"
— Legea 31/1990 (Legea societăților), art. 7 lit. a)-f) (sursă: anaf_surse/legea_31_1990_societatile.txt)

„Articolul 36 (1) În termen de 15 zile de la data încheierii actului constitutiv, fondatorii, primii administratori [...] vor cere înmatricularea societății în registrul comerțului [...]. Ei răspund în mod solidar pentru orice prejudiciu pe care îl cauzează prin neîndeplinirea acestei obligații."
— Legea 31/1990, art. 36 alin. (1) (sursă: anaf_surse/legea_31_1990_societatile.txt)
:::

Erori concrete, legate direct de elementele obligatorii de mai sus:

- **Obiectul de activitate incomplet formulat** — art. 7 lit. c) cere precizarea explicită a domeniului și a activității principale, nu doar o listă de coduri CAEN fără ierarhizare. Confuzia dintre activitatea principală și cele secundare produce respingeri sau reveniri de la registrul comerțului.
- **Capitalul social descris ambiguu** — la SRL, legea cere explicit numărul și valoarea nominală a părților sociale, plus câte părți sociale primește fiecare asociat pentru aportul lui (art. 7 lit. d). Un act constitutiv care menționează doar suma totală a capitalului, fără repartizarea pe asociați, e incomplet.
- **Puterile administratorilor nespecificate** — art. 7 lit. e) cere să se precizeze dacă administratorii acționează împreună sau separat; omiterea acestei precizări generează ambiguitate juridică asupra cine poate angaja firma legal în relațiile cu terții.
- **Depășirea termenului de 15 zile** de la încheierea actului constitutiv pentru a cere înmatricularea (art. 36 alin. 1) — răspunderea pentru întârziere e solidară a fondatorilor și administratorilor, nu doar o formalitate administrativă fără consecințe.
- **Partea la beneficii și pierderi nemenționată** (art. 7 lit. f) — dacă actul constitutiv nu precizează cotele, apar dispute ulterioare la distribuirea dividendelor, mai ales când aportul asociaților nu e egal.

## Ce se greșește în practică

- Se copiază un model generic de act constitutiv găsit online, fără adaptare la structura reală de asociați și la obiectul de activitate specific — omisiunile din modelul generic ajung direct în documentul depus la registrul comerțului.
- Se depune cererea de înmatriculare cu întârziere față de termenul de 15 zile de la actul constitutiv, fără să se conștientizeze că fondatorii răspund solidar pentru prejudiciul cauzat de întârziere.
- Se lasă neclar modul de exercitare a puterilor administratorilor (împreună/separat), ceea ce complică ulterior semnarea contractelor și deschiderea conturilor bancare.

## Ce face iConta.eu

iConta.eu intervine după înființarea firmei, la momentul configurării ei în aplicație (`core/tenant_provisioning.py`) — verifică validitatea cifrei de control a CUI-ului (`cui_valid`) și poate precompleta datele firmei direct din ANAF (`precompleteaza_din_anaf`), reducând riscul unei erori de transcriere a CUI-ului sau a denumirii. Aplicația **nu intervine în redactarea actului constitutiv sau în procedura de înmatriculare** la registrul comerțului — acestea au loc înainte de configurarea firmei în iConta.eu, deci elementele obligatorii ale actului constitutiv (art. 7) rămân responsabilitatea celor implicați în constituirea firmei, de regulă cu asistență juridică sau notarială.

[iConta.eu](/)
