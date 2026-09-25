---
title: "Cum se facturează servicii IT către persoane fizice din UE?"
description: "Locul prestării serviciilor IT către persoane fizice din alte state membre UE, pragul de 10.000 euro pentru TVA local vs. TVA din statul clientului, și ce înseamnă asta pentru factură."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se facturează servicii IT către persoane fizice din UE?

Un dezvoltator sau o firmă românească de IT care vinde direct unor persoane fizice din alte state UE (nu unor firme) aplică regula de TVA pentru servicii B2C, nu regula B2B — iar dacă vânzările depășesc un anumit prag, TVA-ul nu se mai declară în România, ci în statul membru al clientului.

## Temeiul legal

::: ghid-temei
„Prevederile art. 275 alin. (2) si art. 278 alin. (5) lit. h) nu se aplică dacă sunt îndeplinite cumulativ următoarele condiții: a) furnizorul sau prestatorul este stabilit [...] într-un singur stat membru; b) sunt prestate servicii către persoane neimpozabile care sunt stabilite [...] în orice stat membru, altul decât statul membru prevăzut la lit. a) [...]; și c) valoarea totală, fără TVA, a operațiunilor prevăzute la lit. b) nu depășește, în anul calendaristic curent, 10.000 euro sau echivalentul acestei sume în moneda națională și nici nu a depășit această sumă în cursul anului calendaristic precedent."
— Legea 227/2015, art. 278^1 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce înseamnă în practică pentru servicii IT prestate electronic (ex. dezvoltare software la comandă, mentenanță, servicii furnizate pe cale electronică):

- Regula implicită pentru servicii furnizate pe cale electronică către persoane neimpozabile (persoane fizice) e că locul prestării e „unde beneficiarul este stabilit, își are domiciliul stabil sau reședința obișnuită" (art. 278 alin. (5) lit. h) pct. 3) — deci, teoretic, TVA din statul clientului, de la prima operațiune.
- Excepția de la art. 278^1 „împinge" locul prestării înapoi la statul prestatorului (România), atât timp cât valoarea cumulată a acestor vânzări B2C intracomunitare (nu doar servicii electronice, ci și vânzări la distanță de bunuri) rămâne sub 10.000 euro (46.337 lei) pe an calendaristic, curent și precedent.
- Sub prag: se facturează cu TVA românesc (19%, cota standard, dacă nu se aplică altă cotă specifică), ca pentru o vânzare internă.
- Peste prag: locul prestării trece automat la statul membru al fiecărui client, de la momentul depășirii — firma trebuie fie să se înregistreze în TVA în fiecare stat membru relevant, fie să aplice regimul special OSS (One Stop Shop) pentru a declara și plăti centralizat TVA-ul datorat altor state membre, fără înregistrare separată în fiecare.
- Firma poate opta pentru aplicarea directă a regulii „locul beneficiarului" chiar sub prag, caz în care opțiunea e obligatorie pentru cel puțin doi ani calendaristici (art. 278^1 alin. (3)).

## Ce se greșește în practică

- Se aplică automat TVA românesc pe toate vânzările către persoane fizice din UE, indiferent de volum, fără să se verifice dacă pragul de 10.000 euro a fost depășit în anul curent sau precedent.
- Se calculează pragul doar din serviciile electronice, ignorând obligația de cumulare cu eventualele vânzări la distanță de bunuri către persoane fizice din UE realizate de aceeași firmă.
- Se presupune că depășirea pragului obligă la înregistrare separată în fiecare stat membru al clienților — de regulă, regimul OSS permite declararea centralizată, fără înregistrări multiple, dacă firma optează pentru el.

## Ce face iConta.eu

iConta.eu emite facturi cu cota de TVA aleasă de utilizator pentru fiecare operațiune, dar **nu urmărește automat pragul cumulat de 10.000 euro** pe vânzările B2C intracomunitare ale firmei și nu calculează singură momentul în care locul prestării ar trebui să treacă la statul clientului. Aplicația poate genera declarația specială D398 (regimul OSS), dar aceasta e o **declarație manuală**: iConta.eu nu ține evidența operațiunilor OSS pe stat de consum și cotă străină, așa că toate valorile (baza impozabilă și TVA pe fiecare stat membru) trebuie introduse de contabil — aplicația nu le derivă din facturile emise.

[iConta.eu](/)
