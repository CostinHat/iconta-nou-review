---
title: Calendar obligații la înființarea firmei 2026
description: Pașii, în ordine, ca o firmă nou-înființată în 2026 să apară corect pe calendarul de scadențe din iConta.eu — și ce rămâne, oricum, în afara aplicației.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Calendar obligații la înființarea firmei 2026

O firmă nou creată în iConta.eu nu are automat un calendar de scadențe — are nevoie, întâi, de vectorul fiscal completat. Fără el, ecranul „Termene" nu poate deriva nimic pentru firma respectivă.

## Temeiul legal

::: ghid-temei
„Tipurile de obligații fiscale pentru care, potrivit legii, contribuabilul/plătitorul are obligația declarării lor și care formează vectorul fiscal sunt stabilite prin ordin al președintelui A.N.A.F."
— Legea nr. 207/2015 (Codul de procedură fiscală), art. 91 alin. (4)
:::

Vectorul fiscal — ce declarații datorează firma — se stabilește la înregistrarea fiscală la ANAF, nu se deduce singur. În iConta.eu, la crearea unei firme noi, schema tehnică se creează, dar vectorul fiscal NU vine precompletat — trebuie introdus manual, din ecranul „Date firmă".

## Pașii, în ordine

1. **Înregistrarea la ANAF/ONRC** se face în afara iConta.eu — declarația de înregistrare fiscală (D700) și opțiunile de regim/TVA se depun direct la organul fiscal. Aplicația nu urmărește și nu generează acest pas.
2. **Completarea vectorului fiscal în iConta.eu**, din ecranul „Date firmă" (F100): regimul fiscal (micro sau profit), statutul de plătitor de TVA, tipul de decont (lunar/trimestrial, dacă e plătitor) și dacă are operațiuni intracomunitare. Fiecare din aceste patru câmpuri e obligatoriu — necompletat, nu ia o valoare implicită tăcută, ci intră explicit ca „necunoscut".
3. **Abia după completare**, ecranul „Termene" poate deriva declarațiile datorate. Până atunci, firma apare separat, sub „neevaluate", cu mesajul „Vector fiscal necompletat — nu pot evalua obligațiile firmei."
4. **Din luna angajării primului salariat**, D112 intră automat în calendar — nu trebuie activat manual, dar nici nu apare mai devreme.

## Ce apare, tipic, din primul trimestru

- **D100 trimestrial**, dacă firma e la regim micro — inclusiv „pe zero", fără venituri, pentru că formularul D100 nu are o variantă de scutire pentru trimestrul fără activitate.
- **SAF-T (D406)**, cu perioadă de grație la prima raportare (6 luni transmitere lunară / 3 luni transmitere trimestrială) — perioadă pe care calendarul NU o scade automat din termenul afișat.
- **D300/D394**, dacă firma e plătitoare de TVA, în ritmul deconturilor sale.
- **D101** abia anul viitor, pentru anul curent, dacă firma e la regim de profit — termen 25 iunie anul următor.

## Ce se greșește în practică

- Se așteaptă ca noua firmă să apară pe calendar imediat după creare, fără să se completeze mai întâi vectorul fiscal — apare, în schimb, pe lista de „neevaluate".
- Se confundă înregistrarea fiscală la ANAF cu ceva ce urmărește aplicația — iConta.eu nu depune și nu ține evidența declarației de înregistrare/mențiuni (D700 și predecesoarele ei, D010/D020/D070, sunt blocate tehnic în aplicație, fără validator XML disponibil).
- Se presupune că D112 trebuie „activat" — de fapt apare singur, din luna reală a angajării.

## Ce face iConta.eu

Odată completat vectorul fiscal, ecranul „Termene" derivă automat obligațiile viitoare (60 de zile) pentru firma nouă, cu aceeași logică folosită pentru orice altă firmă din portofoliu — nu există un tratament special pentru „firmă nouă" în motor, în afară de faptele reale (fără salariați încă, la prima raportare SAF-T etc.), care influențează firesc rezultatul.

Ce nu face: nu depune și nu urmărește declarația de înregistrare fiscală la ANAF/ONRC, și nu calculează perioada de grație SAF-T — ambele rămân în sarcina contabilului.

[iConta.eu](/)
