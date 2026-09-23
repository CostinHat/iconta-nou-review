---
title: "Amortizarea accelerată: condiții și cum se recunoaște"
description: "Cui i se permite amortizarea accelerată, regula de 50% în primul an și cum verifică iConta.eu dacă metoda e permisă pe categoria activului."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Amortizarea accelerată: condiții și cum se recunoaște

Amortizarea accelerată e una dintre cele patru metode fiscale de amortizare, dar nu poate fi aleasă pentru orice mijloc fix — legea o permite doar pentru anumite categorii de active.

## Temeiul legal

::: ghid-temei
"a) pentru primul an de utilizare, amortizarea nu poate depăși 50% din valoarea fiscală de la data intrării în patrimoniul contribuabilului a mijlocului fix; [...] b) pentru următorii ani de utilizare, amortizarea se calculează prin raportarea valorii rămase de amortizare a mijlocului fix la durata normală de utilizare rămasă a acestuia." — Codul fiscal, art. 28 alin. (8)
:::

Regimul pe categorie e stabilit de alin.(5) al aceluiași articol: construcțiile (cont 212) merg **doar** pe liniar; echipamentele tehnologice, mașinile, uneltele și instalațiile de lucru (cont 2131) pot alege liniar, degresiv **sau accelerat**; orice alt mijloc fix amortizabil (categoria generică, inclusiv animale și plantații) poate alege doar liniar sau degresiv, **fără** accelerat. Terenurile (cont 211) nu se amortizează deloc.

Practic: amortizarea accelerată e disponibilă real doar pentru mijloacele fixe încadrate contabil la cont 2131 — nu pentru clădiri, nu pentru terenuri și nu pentru categoria generică de active (mobilier, aparatură etc.).

## Ce se greșește în practică

Cea mai frecventă greșeală: se alege "accelerată" pentru un activ care nu se încadrează la echipamente tehnologice (de exemplu un mijloc fix trecut pe un cont generic sau pe categoria "orice alt mijloc fix"), fără să se verifice că legea nu permite metoda pentru acea categorie.

## Ce face iConta.eu

Motorul unic de amortizare din aplicație (folosit deopotrivă de registru, de nota lunară, de casare și de reevaluare) verifică la fiecare calcul dacă metoda aleasă e permisă pentru categoria activului, derivată din contul de imobilizare. Dacă metoda nu e permisă, aplicația **nu calculează tacit o cifră liniară** — rândul respectiv din registru arată o eroare explicită la coloanele amortizat/rămas, în locul unei valori fabricate.

[iConta.eu](/)
