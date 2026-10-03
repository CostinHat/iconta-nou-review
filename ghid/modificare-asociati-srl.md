---
title: "Modificare asociați la SRL: cum se face"
description: Schimbarea structurii asociaților (cesiune de părți sociale, intrare/ieșire asociat) e o mențiune la Registrul Comerțului, printr-un act adițional la actul constitutiv — distinctă de contabilitatea curentă a decontărilor cu asociații existenți.
published: 2026-09-24
modified: 2026-10-03
poarta: v1
---

# Modificare asociați la SRL: cum se face

„Modificarea asociaților" înseamnă, de regulă, una din două situații: un asociat existent își cesionează părțile sociale (parțial sau integral) către altcineva, sau intră/iese un asociat din structura firmei. Ambele presupun un **act adițional la actul constitutiv** și o mențiune corespunzătoare la Registrul Comerțului — un proces juridic, nu unul contabil.

Modificarea propriu-zisă nu se face în iConta.eu și nu ține de funcționalitatea „Decontări asociați". Recomandăm consultarea unui notar/avocat pentru redactarea actului adițional și depunerea mențiunii la Registrul Comerțului.

## Temeiul legal

::: ghid-temei
„Cota-parte din profit ce se plătește fiecărui asociat constituie dividend."
— Legea 31/1990, art. 67 alin. (1) (sursă: anaf_surse/legea_31_1990_societatile.txt)
:::

::: ghid-temei
„Dividendele se distribuie asociaților proporțional cu cota de participare la capitalul social vărsat, opțional trimestrial pe baza situațiilor financiare interimare și anual, după regularizarea efectuată prin situațiile financiare anuale, dacă prin actul constitutiv nu se prevede altfel."
— Legea 31/1990, art. 67 alin. (2) (sursă: anaf_surse/legea_31_1990_societatile.txt)
:::

::: ghid-temei
„Dividendele care se cuvin după data transmiterii acțiunilor aparțin cesionarului, în afară de cazul în care părțile au convenit altfel."
— Legea 31/1990, art. 67 alin. (6) (sursă: anaf_surse/legea_31_1990_societatile.txt)
:::

::: ghid-temei
„Transmiterea are efect față de terți numai din momentul înscrierii ei în registrul comerțului."
— Legea 31/1990, art. 203 alin. (2) (sursă: anaf_surse/legea_31_1990_societatile.txt)
:::

Aceste texte devin relevante după transmiterea părților sociale. Dividendele se împart proporțional cu cotele de participare la capitalul social vărsat (dacă actul constitutiv nu prevede altfel), iar cele care se cuvin după data transmiterii aparțin noului asociat, dacă părțile nu au convenit altfel. Concret: un dividend distribuit după data transmiterii se calculează pe noile cote; unul distribuit înainte rămâne al vechilor asociați, chiar dacă se plătește după cesiune.

## Ce se greșește în practică

- Se împarte dividendul după structura asociaților din perioada în care s-a realizat profitul, sau după cea de la data plății. Legea leagă dividendul de momentul în care se cuvine: cel care se cuvine după data transmiterii părților sociale aparține cesionarului, dacă părțile nu au convenit altfel (art. 67 alin. (6)). Un dividend distribuit înainte de cesiune și plătit după rămâne al vechiului asociat; unul distribuit după cesiune revine noului asociat, chiar dacă provine din profitul unui exercițiu anterior.
- Se confundă cesiunea de părți sociale (vânzare/cumpărare a participației) cu o distribuire de dividend sau cu un împrumut — sunt operațiuni de natură juridică diferită, cu tratament fiscal diferit pentru cel care vinde participația.
- Se actualizează evidența internă a firmei fără să existe mențiunea corespunzătoare, efectiv făcută, la Registrul Comerțului — fără această mențiune, modificarea nu e opozabilă terților.

## Ce face iConta.eu

Funcționalitatea **Decontări asociați** (Operațiuni speciale > Finanțare) nu operează modificări ale structurii asociaților — aceasta rămâne un proces juridic separat, finalizat prin act adițional și mențiune la Registrul Comerțului. După cesiune, noua structură se încarcă la firmă din **Import date > Asociați**, completând **Data cesiunii** (data transmiterii părților sociale). Structura anterioară nu se șterge: rămâne valabilă până în ziua dinaintea cesiunii. La generarea D205, iConta.eu împarte fiecare dividend plătit după structura asociaților de la data distribuirii lui: tranșele distribuite înainte de cesiune merg la vechii asociați, cele distribuite după, la noii asociați. O plată se atribuie distribuirilor încă neplătite, în ordinea lor; o plată fără distribuire înregistrată se împarte după structura de la data plății. Dacă noua structură se încarcă fără dată de cesiune, iConta.eu o tratează ca pe o corectură a structurii existente și o aplică tuturor dividendelor.

[iConta.eu](/)
