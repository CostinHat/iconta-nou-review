---
title: "De ce diferă TVA din D394 față de TVA din D300?"
description: "Cauzele obișnuite pentru care totalul de TVA raportat în D394 nu coincide cu decontul de TVA (D300) pentru aceeași lună."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# De ce diferă TVA din D394 față de TVA din D300?

D300 (decontul de TVA) și D394 (declarația informativă privind livrările/prestările și achizițiile) se depun pentru aceeași lună și, în teorie, ar trebui să reflecte aceleași operațiuni. În practică, între cele două apar frecvent diferențe, iar cele mai multe au o cauză structurală, nu o greșeală de calcul.

## Temeiul legal

::: ghid-temei
„Prin decontul de taxă prevăzut la art. 323, persoanele impozabile trebuie să determine diferențele dintre sumele prevăzute la alin. (3) și (4), care reprezintă regularizările de taxă, și stabilirea soldului taxei de plată sau a soldului sumei negative a taxei."
— Legea nr. 227/2015, art. 303 alin. (6) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„Nu se înscriu achiziţiile intracomunitare de bunuri şi servicii pentru care există obligativitatea înscrierii în declaraţia 390."
— OPANAF 2194/2025 (structura D394), Anexa 2 - Instrucțiuni de completare (sursă: anaf_surse/opanaf_2194_2025_d394.txt)
:::

Câteva cauze reale, nu erori, pentru care sumele diferă:

- **Regularizările din decont** (art. 303) — sold reportat, diferențe stabilite de inspecția fiscală, ajustări conform art. 304/305 — intră în soldul de plată/rambursat din D300, dar nu au întotdeauna corespondent direct în rezumatul D394.
- **Achizițiile intracomunitare** generează TVA deductibilă (taxare inversă) în D300, dar sunt excluse structural din D394 — se raportează separat, prin declarația 390 — deci partea deductibilă a celor două declarații nu poate coincide automat când firma are și achiziții intracomunitare în lună.
- **Rotunjirile** — cele două declarații pot rotunji diferit la nivel de linie de factură versus la nivel de total, mai ales când o factură are mai multe cote de TVA pe linii diferite.

Notă: facturile emise către persoane fizice **nu** sunt o cauză de diferență — de la 01.01.2017 ele se raportează în D394 ca operațiuni obișnuite (tip L/LS, partener „neînregistrat"), agregate în același rezumat pe cotă ca restul livrărilor, deci intră în totalul de TVA colectată din D394 la fel ca în D300.

## Ce se greșește în practică

- Se compară direct totalul „TVA colectată" din D394 cu rândul de TVA colectată din D300, ignorând regularizările (sold reportat, diferențe de inspecție) care apar doar în decont.
- Se investighează o „eroare" când, de fapt, diferența de pe partea deductibilă vine din achizițiile intracomunitare ale lunii, care intră în TVA deductibilă din D300 dar sunt excluse structural din D394 (raportate prin D390).
- Se recalculează manual TVA pe cotă din totalul facturii, în loc să se folosească liniile de factură (cu cota fiecărui produs/serviciu), ceea ce produce rotunjiri diferite față de sursa reală.

## Ce face iConta.eu

La data acestui ghid, iConta.eu generează **D300** și **D394** din aceeași sursă de date — liniile facturilor introduse în aplicație — folosind exact aceeași formulă de deducere a cotei de TVA (din liniile facturii, cu fallback identic la deducerea inversă din total/TVA când lipsesc liniile) în ambele generatoare. Un test intern al aplicației verifică explicit paritatea între cele două declarații pe TVA per cotă, tocmai pentru a preveni situația în care o modificare într-un singur generator ar produce, fără să fie observată, doi totali diferiți raportați la ANAF pentru aceeași lună.

[iConta.eu](/)
