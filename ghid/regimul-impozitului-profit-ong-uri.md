---
title: "Regimul impozitului pe profit pentru ONG-uri cu activitate economică"
description: "ONG-urile nu sunt scutite în bloc de impozit pe profit: veniturile fără scop patrimonial sunt neimpozabile, cele economice sunt scutite doar până la un plafon, iar restul se impozitează cu 16%."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Regimul impozitului pe profit pentru ONG-uri cu activitate economică

O organizație nonprofit (asociație, fundație) nu iese complet din sfera impozitului pe profit doar pentru că nu are scop lucrativ. Legea tratează diferit veniturile în funcție de natura lor: cele care țin de scopul statutar al organizației sunt neimpozabile prin definiție, iar cele dintr-o eventuală activitate economică (vânzare de bunuri, prestări de servicii, chirii etc.) intră, cu o scutire limitată, sub incidența impozitului pe profit — la fel ca la orice altă persoană juridică.

## Temeiul legal

::: ghid-temei
„(2) În cazul organizațiilor nonprofit, organizațiilor sindicale, organizațiilor patronale, la calculul rezultatului fiscal, următoarele tipuri de venituri sunt venituri neimpozabile: a) cotizațiile și taxele de înscriere ale membrilor; b) contribuțiile bănești sau în natură ale membrilor și simpatizanților; c) taxele de înregistrare stabilite potrivit legislației în vigoare; [...] e) donațiile, precum și banii sau bunurile primite prin sponsorizare/mecenat; f) veniturile din dividende, dobânzi, precum și din diferențele de curs valutar aferente disponibilităților și veniturilor neimpozabile; [...] i) resursele obținute din fonduri publice sau din finanțări nerambursabile; j) veniturile realizate din acțiuni ocazionale precum: evenimente de strângere de fonduri cu taxă de participare, serbări, tombole, conferințe, utilizate în scop social sau profesional, potrivit statutului acestora; [...]
(3) [...] pentru calculul rezultatului fiscal sunt neimpozabile și alte venituri realizate, până la nivelul echivalentului în lei a 15.000 euro, într-un an fiscal, dar nu mai mult de 10% din veniturile totale neimpozabile prevăzute la alin. (2). Aceste organizații datorează impozit pe profit pentru partea din profitul impozabil care corespunde veniturilor, altele decât cele considerate venituri neimpozabile, potrivit alin. (2) sau potrivit prezentului alineat, asupra căreia se aplică cota prevăzută la art. 17 sau 18, după caz."
— art. 15 alin. (2)-(3) din Legea 227/2015 (Codul fiscal) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Veniturile enumerate la alin. (2) — cotizații, contribuții, donații, sponsorizări, dobânzi/diferențe de curs aferente disponibilităților neimpozabile, fonduri publice/finanțări nerambursabile, acțiuni ocazionale ș.a. — sunt neimpozabile **prin natura lor**, indiferent de sumă.
- Orice alt venit (tipic: din activitatea economică) e neimpozabil doar în limita plafonului de la alin. (3): minimul dintre 15.000 EUR/an și 10% din totalul veniturilor neimpozabile de la alin. (2).
- Ce depășește acest plafon devine profit impozabil, la cota standard de impozit pe profit — **16%**, prevăzută la art. 17 din Codul fiscal.
- Regimul se aplică deopotrivă organizațiilor nonprofit, organizațiilor sindicale și organizațiilor patronale.

## Ce se greșește în practică

- Se consideră ONG-ul „scutit" în bloc de impozit pe profit doar pentru că e nonprofit — de fapt scutirea privește doar categoriile de venituri enumerate la alin. (2), plus plafonul limitat de la alin. (3).
- Se aplică cota de 16% la toate veniturile economice, fără să se scadă mai întâi plafonul de scutire la care organizația are dreptul.
- Se amestecă evidența veniturilor fără scop patrimonial cu cea a activității economice, ceea ce face imposibilă calcularea corectă a rezultatului fiscal supus impozitului pe profit.

## Ce face iConta.eu

Din ecranul „Operațiuni speciale" → „Operațiuni ONG", iConta.eu înregistrează încasarea unui venit fără scop patrimonial (cotizație, contribuție, donație, sponsorizare sau venit financiar) direct pe contul din grupa 73 corespunzător, cu nota contabilă generată automat. Separat, aplicația oferă un calculator care compară plafonul de 15.000 EUR (la cursul introdus) cu 10% din veniturile neimpozabile ale anului, reține minimul dintre ele și estimează impozitul de 16% pe partea rămasă — dar acest calcul e disponibil azi doar printr-un apel direct la API (`POST /tenants/{id}/nota-ong`), nu și din formularul din ecran, unde operația „Calcul scutire art. 15 CF" nu are încă niciun câmp de completat. Depunerea declarației de impozit pe profit (D101) rămâne, oricum, în sarcina contabilului.

[iConta.eu](/)
