---
title: "Ce fac dacă am depus D300 cu o factură lipsă?"
description: "Mecanismul legal de corectare a unui decont de TVA în care a rămas o factură nedeclarată și ce verifică automat iConta.eu pe această temă."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce fac dacă am depus D300 cu o factură lipsă?

O factură uitată dintr-un decont deja depus nu se repară prin redepunerea decontului cu cifra corectată — TVA are propriul ei mecanism de corecție, diferit de rectificativa clasică folosită la alte declarații. Se corectează în decontul lunii sau trimestrului următor, la rândurile de regularizări.

## Temeiul legal

::: ghid-temei
„Datele înscrise incorect într-un decont de taxă se pot corecta prin decontul unei perioade fiscale ulterioare şi se vor înscrie la rândurile de regularizări."
— Codul fiscal (Legea 227/2015), art. 323 alin. (3) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Nu se depune o „rectificativă" clasică peste decontul greșit: corecția intră în decontul **următor**, la rândurile dedicate regularizărilor, nu prin reluarea integrală a decontului vechi.
- Codul de procedură fiscală distinge explicit: erorile de fond din decontul de TVA „se realizează potrivit prevederilor Codului fiscal" (deci pe calea art. 323 alin. 3), în timp ce erorile pur materiale (fără impact pe cuantum) urmează o procedură separată, aprobată prin ordin al președintelui ANAF (art. 105 alin. 4 Cod procedură fiscală).
- Termenul limită pentru orice corecție e cel general de prescripție a dreptului organului fiscal de a stabili creanțe fiscale: **5 ani**, calculați de la 1 iulie a anului următor celui pentru care se datorează obligația (art. 110 alin. 1-2 Cod de procedură fiscală).
- Dacă factura lipsă era o livrare sau achiziție intracomunitară de bunuri, corecția din decontul viitor va apărea și în comparația D390 (declarația recapitulativă) vs. D300, pentru că cele două se bazează pe aceleași facturi — o factură IC adăugată ulterior schimbă ambele declarații simultan.

## Ce se greșește în practică

- Se încearcă redepunerea decontului vechi cu factura adăugată, ca la alte declarații — mecanismul specific TVA cere corecție prin decontul perioadei următoare, nu prin retransmiterea celui greșit.
- Se așteaptă până la un control fiscal pentru a corecta, deși legea permite (și impune, în fond) corecția din proprie inițiativă, în decontul următor.
- Se tratează orice factură lipsă ca fiind automat sesizabilă de aplicație — de fapt aplicația verifică doar anumite corespondențe (vezi mai jos), nu detectează în sine „lipsa" unei facturi din decontul deja depus.

## Ce face iConta.eu

iConta **nu are o funcție care să detecteze, de una singură, că o factură a lipsit dintr-un decont D300 deja depus** — nu există în aplicație un mecanism generic de „factură nedeclarată". Ce există e o verificare mai specifică: pentru facturile de bunuri intracomunitare, aplicația compară automat declarația D390 cu rândurile R1_1 (livrări) și R5_1 (achiziții) ale **D300 efectiv depus prin aplicație** pentru cea mai recentă perioadă disponibilă. Dacă factura lipsă era o livrare sau achiziție IC, adăugarea ei ulterioară în evidență va produce o diferență între D390 (recalculat) și D300-ul deja depus, semnalată roșu, cu remediul sugerat „rectificativă D300 sau corectarea D390" — decizia și acțiunea rămân ale contabilului, aplicația nu corectează nimic automat.

Pentru orice altă factură (internă, fără componentă intracomunitară), nu există niciun avertisment automat în aplicație — descoperirea și corectarea rămân integral responsabilitatea contabilului, care aplică mecanismul legal de mai sus: introduce regularizarea în decontul perioadei curente, nu redepune decontul greșit.

[iConta.eu](/)
