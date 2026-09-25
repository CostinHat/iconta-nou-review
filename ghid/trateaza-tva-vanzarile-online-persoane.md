---
title: "Cum se tratează TVA pentru vânzările online către persoane fizice din UE?"
description: "Pragul de 10.000 euro care decide dacă un magazin online aplică TVA românesc sau TVA din statul membru al cumpărătorului, pentru vânzările către persoane fizice din UE."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se tratează TVA pentru vânzările online către persoane fizice din UE?

Un magazin online românesc care vinde produse unor persoane fizice din alte state membre UE trebuie să decidă, pentru fiecare vânzare, dacă aplică TVA românesc sau TVA din statul membru al cumpărătorului. Răspunsul depinde de un singur criteriu cantitativ: volumul cumulat al acestor vânzări în anul curent și în anul precedent.

## Temeiul legal

::: ghid-temei
„Atunci când, în cursul unui an calendaristic, pragul prevăzut la alin. (1) lit. c) este depășit, prevederile art. 275 alin. (2) și art. 278 alin. (5) lit. h) se aplică de la momentul depășirii pragului."
— Legea 227/2015, art. 278^1 alin. (2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce trebuie urmărit efectiv:

- Pragul de la art. 278^1 alin. (1) lit. c) e de **10.000 euro** (46.337 lei, curs fixat) pe an calendaristic, cumulat pe toate vânzările la distanță de bunuri și serviciile electronice către persoane neimpozabile din alte state membre decât România.
- **Sub prag**: vânzarea se facturează cu TVA românesc, ca o vânzare internă obișnuită, indiferent de statul membru al cumpărătorului.
- **Peste prag**: de la momentul depășirii, locul livrării trece la statul membru al cumpărătorului (art. 275 alin. (2) pentru bunuri) — firma trebuie să aplice cota de TVA a statului respectiv, fie prin înregistrare directă acolo, fie prin regimul special OSS, care centralizează declararea pentru toate statele membre de consum printr-o singură declarație depusă în România.
- Firma poate opta pentru regula „locul cumpărătorului" încă de sub prag, dacă preferă (art. 278^1 alin. (3)) — opțiunea rămâne obligatorie minimum doi ani calendaristici.
- Verificarea pragului se face cu cursul de schimb publicat de Banca Centrală Europeană la data adoptării directivei relevante, valoarea fixă pentru România fiind 46.337 lei — nu cursul zilei fiecărei tranzacții.

## Ce se greșește în practică

- Se aplică TVA românesc pe toate vânzările către persoane fizice din UE, indiferent de volum, fără verificarea cumulativă a pragului de 10.000 euro pe an curent și precedent.
- Se calculează pragul separat pentru fiecare stat membru de destinație, în loc de cumulat pe toate statele membre (altele decât România) — pragul e unic, nu per țară.
- Se schimbă regimul de TVA (de la românesc la cel al cumpărătorului) doar pentru tranzacțiile viitoare din luna următoare depășirii, în loc de „de la momentul depășirii pragului", cum cere legea — inclusiv tranzacția care a cauzat depășirea poate necesita tratament diferit.

## Ce face iConta.eu

iConta.eu emite facturile cu cota de TVA introdusă de utilizator pentru fiecare vânzare, dar **nu calculează automat** volumul cumulat al vânzărilor B2C intracomunitare ale firmei față de pragul de 10.000 euro și nu schimbă singură regimul de TVA la depășire. Aplicația poate genera declarația specială D398 pentru regimul OSS, dar aceasta rămâne o declarație manuală — valorile pe fiecare stat membru de consum trebuie introduse de contabil, aplicația nu le derivă automat din facturile emise către persoane fizice din UE.

[iConta.eu](/)
