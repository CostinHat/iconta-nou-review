---
title: "Cum influențează prețurile de transfer calculul impozitului pe profit"
description: "Ce prevede Codul fiscal despre ajustarea rezultatului fiscal atunci când tranzacțiile cu persoane afiliate nu respectă principiul valorii de piață."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum influențează prețurile de transfer calculul impozitului pe profit

Când o firmă vinde, cumpără sau împrumută bani de la o societate afiliată (același grup, aceiași asociați), prețul practicat contează fiscal — nu doar contabil. Dacă acel preț nu respectă valoarea de piață, organul fiscal are dreptul să recalculeze baza de impozitare.

## Temeiul legal

::: ghid-temei
„(4) Tranzacțiile între persoane afiliate se realizează conform principiului valorii de piață. În cadrul unei tranzacții, al unui grup de tranzacții între persoane afiliate, organele fiscale pot ajusta, în cazul în care principiul valorii de piață nu este respectat, sau pot estima, în cazul în care contribuabilul nu pune la dispoziția organului fiscal competent datele necesare pentru a stabili dacă prețurile de transfer practicate în situația analizată respectă principiul valorii de piață, suma venitului sau a cheltuielii aferente rezultatului fiscal oricăreia dintre părțile afiliate pe baza nivelului tendinței centrale a pieței."
— Legea nr. 227/2015 (Codul fiscal), art. 11 alin. (4) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Efectul direct asupra impozitului pe profit:

- Dacă prețul dintr-o tranzacție cu o persoană afiliată e sub sau peste valoarea de piață, organul fiscal poate **ajusta suma venitului sau a cheltuielii** recunoscute fiscal la oricare dintre firmele afiliate — ceea ce schimbă direct baza de calcul a impozitului pe profit.
- Dacă firma nu poate demonstra, cu documente, că prețurile respectă principiul valorii de piață, organul fiscal poate **estima** suma pe baza „nivelului tendinței centrale a pieței" — practic, fără să mai fie nevoie să dovedească exact cât ar fi trebuit să fie prețul corect.
- Legea listează metodele acceptate pentru stabilirea valorii de piață: comparării prețurilor, cost plus, prețului de revânzare, marjei nete, împărțirii profitului, sau orice altă metodă recunoscută în Liniile directoare OCDE privind prețurile de transfer.
- Ajustarea se face „în scopul stabilirii impozitelor directe" (art. 11 alin. (5)) — deci afectează în primul rând impozitul pe profit, nu TVA.

## Ce se greșește în practică

- Se stabilesc prețurile în tranzacțiile intragrup fără nicio documentație justificativă, considerându-se că, atâta timp cât ambele firme sunt din România și plătesc taxe, „nu contează" prețul practicat — legea nu face această excepție.
- Se ignoră obligația de a pune la dispoziția organului fiscal datele privind respectarea principiului valorii de piață — absența lor deschide calea estimării, nu prezumției de conformitate.
- Se confundă ajustarea prețurilor de transfer cu o simplă chestiune de evidență contabilă — de fapt schimbă direct baza de impozitare a profitului.

## Ce face iConta.eu

Verificat în cod: modulul `core/d394.py` gestionează declararea existenței operațiunilor cu persoane afiliate prin câmpul `prsAfiliat` din declarația D394, pe baza unui indicator setat în profilul firmei (`are_operatiuni_afiliate`). Aplicația **nu calculează și nu ajustează automat prețurile de transfer** — nu există în cod o funcționalitate care să aplice metodele de determinare a valorii de piață (comparării prețurilor, cost plus etc.) sau să recalculeze rezultatul fiscal în funcție de acestea. Declararea corectă a operațiunilor cu persoane afiliate și, dacă e cazul, întocmirea dosarului prețurilor de transfer rămân în sarcina contabilului.

[iConta.eu](/)
