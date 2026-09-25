---
title: "Cum corectez un beneficiu salarial taxat greșit?"
description: "Declarația informativă (cum e D112) se poate corecta prin declarație rectificativă, indiferent de perioada la care se referă, potrivit Codului de procedură fiscală."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum corectez un beneficiu salarial taxat greșit?

Un beneficiu salarial (bonus, tichet, avantaj în natură) impozitat greșit — cu cota greșită, în baza de calcul greșită, sau pur și simplu omis — nu rămâne o eroare permanentă în evidențele fiscale. Codul de procedură fiscală prevede explicit mecanismul de corecție, iar termenul diferă în funcție de tipul declarației afectate.

## Temeiul legal

::: ghid-temei
„(1) Declarația de impunere poate fi corectată de către contribuabil/plătitor, pe perioada termenului de prescripție a dreptului de a stabili creanțe fiscale. (2) Declarația informativă poate fi corectată de către contribuabil/plătitor indiferent de perioada la care se referă. (3) Declarațiile prevăzute la alin. (1) și (2) pot fi corectate prin depunerea unei declarații rectificative."
— Legea nr. 207/2015 privind Codul de procedură fiscală, art. 105 alin. (1)-(3) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Ce înseamnă acest text pentru un beneficiu salarial taxat greșit:

- Declarația D112 are o componentă de **declarație de impunere** (obligațiile de plată calculate) și o componentă de **declarație informativă** (datele nominale pentru fiecare salariat). Corecția declarației de impunere e limitată la termenul de prescripție a dreptului organului fiscal de a stabili creanțe fiscale; corecția componentei informative se poate face **indiferent de perioada** la care se referă.
- Corecția se face întotdeauna prin **declarație rectificativă** — nu printr-o simplă notă internă sau o mențiune informală transmisă ANAF.
- Dacă eroarea a generat o diferență de impozit/contribuții de plată (beneficiul a fost subimpozitat), declarația rectificativă va genera și o obligație de plată suplimentară, cu termen de plată legat de data depunerii rectificativei (conform regulilor generale ale Codului de procedură fiscală privind stabilirea termenelor de plată pentru diferențele rezultate din rectificative).
- Dacă eroarea a fost în celălalt sens (supraimpozitare), rectificativa e mecanismul prin care se corectează și, eventual, se solicită restituirea/compensarea sumei plătite în plus.

## Ce se greșește în practică

- Se corectează greșeala doar în evidența internă (statul de plată din firmă), fără a mai depune o declarație rectificativă la ANAF — lăsând declarația inițială, cu date greșite, ca ultimă versiune oficială.
- Se presupune că orice corecție e supusă aceluiași termen de prescripție ca obligațiile de plată — de fapt, componenta informativă a declarației se poate corecta indiferent de vechimea perioadei (alin. (2)).
- Se amână corecția până la un control fiscal, sperând că eroarea nu va fi observată — riscul crește odată cu acumularea de accesorii (dobânzi/penalități) pentru diferența de plată nedeclarată la timp.

## Ce face iConta.eu

La generarea D112, iConta.eu completează atributul care marchează caracterul declarației (inițială/rectificativă) fix pe valoarea "inițială" — aplicația nu are, la acest moment, un flux dedicat prin care contabilul să regenereze o declarație a unei perioade anterioare, cu datele corectate, și să o marcheze explicit ca rectificativă în structura XML transmisă. Corectarea unui beneficiu salarial taxat greșit, dintr-o perioadă deja depusă, rămâne astfel un proces realizat în afara fluxului automatizat curent al aplicației.

[iConta.eu](/)
