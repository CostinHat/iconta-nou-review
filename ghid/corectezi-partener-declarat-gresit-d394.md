---
title: Cum corectezi un partener declarat greșit în D394
description: D394 e o declarație informativă și se poate corecta prin declarație rectificativă indiferent de perioada la care se referă, conform art. 105 din Codul de procedură fiscală.
published: 2026-09-24
modified: 2026-10-13
poarta: v1
---

# Cum corectezi un partener declarat greșit în D394

D394 (declarația privind livrările/prestările și achizițiile efectuate pe teritoriul național de persoanele înregistrate în scopuri de TVA) e o declarație informativă. Regimul ei de corectare e mai permisiv decât cel al declarațiilor de impunere — nu există un termen limită legat de prescripție.

### Baza legală

Art. 105 din Codul de procedură fiscală distinge două regimuri de corectare:

- **alin. (1)**: declarația de impunere (cum e D101 sau D112) poate fi corectată pe perioada termenului de prescripție a dreptului organului fiscal de a stabili creanțe fiscale;
- **alin. (2)**: **declarația informativă poate fi corectată de contribuabil indiferent de perioada la care se referă** — fără limita de prescripție aplicabilă declarațiilor de impunere;
- **alin. (3)**: ambele categorii se corectează prin depunerea unei declarații rectificative.

D394 e o declarație informativă (raportează operațiuni pe cod de partener, fără să stabilească ea însăși o obligație de plată), deci intră sub incidența art. 105 alin. (2) — se poate corecta oricând, chiar și pentru perioade vechi, fără să fie blocată de termenul de prescripție care limitează corectarea declarațiilor de impunere.

::: ghid-temei
„(2) Declarația informativă poate fi corectată de către contribuabil/plătitor indiferent de perioada la care se referă. (3) Declarațiile prevăzute la alin. (1) și (2) pot fi corectate prin depunerea unei declarații rectificative.”
— Legea nr. 207/2015 (Codul de procedură fiscală), art. 105 alin. (2)-(3) (sursă: [Legea nr. 207/2015 privind Codul de procedură fiscală](https://legislatie.just.ro/Public/DetaliiDocument/170007))

„3. În cazul în care, după depunerea declaraţiei, persoana impozabilă constată existenţa unor omisiuni/erori în datele declarate, aceasta trebuie să depună o nouă declaraţie corect completată cu operaţiunile care necesită modificarea şi/sau operaţiunile care nu au fost declarate, declaraţie care înlocuieşte declaraţia informativă depusă iniţial.”
— OPANAF 2194/2025, Anexa 2 pct. 3 (sursă: [OPANAF nr. 2194/2025 pentru modificarea OPANAF nr. 3769/2015 (declarația informativă D394)](https://legislatie.just.ro/Public/DetaliiDocument/302310))
:::

### Ce înseamnă practic "cod eronat de partener"

Formularul D394 raportează, pentru fiecare partener de TVA cu care firma a avut operațiuni în perioada de raportare, codul de identificare fiscală (CUI/CIF), valorile livrărilor/achizițiilor și, după caz, ale bazei de TVA aferente. O eroare tipică e introducerea unui CUI greșit (cifră transpusă, partener confundat) sau alocarea unei operațiuni la un partener greșit, deși valoarea totală declarată e corectă.

O formă mai greu de observat e clasificarea greșită a partenerului. Tipul partenerului se stabilește după prefixul CUI: cu prefix „RO” valid — partener român; fără CUI — partener fără cod fiscal; cu prefix de țară UE recunoscut — partener din UE; cu prefix de țară non-UE recunoscut — partener din afara UE. O eroare de tastare la CUI-ul unui partener român (de exemplu un prefix scris greșit) poate duce, dacă nu e prinsă, la clasificarea tacită drept partener străin, iar operațiunea ajunge declarată în locul greșit.

### Pașii de corectare

1. **Identifică perioada de raportare afectată** (luna/trimestrul din declarația inițială cu partenerul greșit) și corectează CUI-ul/clasificarea partenerului în evidență, apoi verifică din nou toate operațiunile perioadei.
2. **Redepune declarația D394 completă și corect completată** pentru acea perioadă, cu bifa de "declarație rectificativă", conform art. 105 alin. (3) CPF — nu se transmite doar diferența, ci întreaga declarație în forma corectă.
3. **Verifică efectul asupra partenerului afectat greșit** — dacă operațiunea a fost atribuită unui partener real cu care firma n-a avut de fapt acea tranzacție, corectarea trebuie să elimine complet operațiunea eronată de la acel cod și s-o mute la partenerul corect.
4. **Nu e nevoie de justificare specială de întârziere** — spre deosebire de alte tipuri de corecții unde legea cere un temei (eveniment neimputabil, hotărâre judecătorească etc. — vezi art. 105 alin. 6-7 pentru declarațiile de impunere după anularea rezervei verificării ulterioare), corectarea unei declarații informative ca D394 nu are o astfel de condiționare.

### Diferența față de o eroare de TVA colectat/dedus

Dacă eroarea de partener a fost însoțită și de o eroare de sumă care a afectat TVA-ul colectat sau dedus declarat prin decont (D300), corectarea acelei componente urmează regimul separat prevăzut de Codul fiscal pentru erorile din deconturile de TVA (art. 105 alin. 4 CPF trimite la procedura aprobată prin ordin al președintelui ANAF pentru erorile materiale din decontul de TVA) — corectarea D394 nu înlocuiește, dacă e cazul, corectarea D300.

### Ce se greșește în practică

- Se lasă neverificat un CUI care pare „străin” doar pentru că prefixul e neobișnuit — poate fi de fapt un CUI românesc scris greșit.
- Se presupune că orice prefix alfabetic necunoscut e automat un cod de țară valid — un prefix nerecunoscut trebuie tratat ca posibilă eroare de tastare, nu ca partener străin cert.
- Se corectează doar linia partenerului greșit, fără să se redepună întreaga declarație a perioadei.

### Ce face iConta.eu

Clasificarea partenerului se face automat din prefixul CUI, dar un prefix alfabetic pe care aplicația nu îl recunoaște ca fiind cod de țară nu e tratat tacit drept partener străin — e semnalat ca posibilă eroare de tastare a unui CUI românesc, pentru verificare de către contabil.
