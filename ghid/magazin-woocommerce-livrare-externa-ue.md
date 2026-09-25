---
title: "Poate un magazin WooCommerce cu livrare externă UE să folosească integrarea?"
description: "Integrarea WooCommerce importă orice comandă, indiferent de destinația livrării, dar nu aplică regimul special de TVA la vânzările la distanță intracomunitare — o limită de precizat înainte de a te baza pe ea pentru vânzări către alte state UE."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Poate un magazin WooCommerce cu livrare externă UE să folosească integrarea?

Tehnic, da — integrarea importă orice comandă WooCommerce cu statusul potrivit, indiferent de țara de livrare. Dar „poate folosi integrarea" și „integrarea aplică regimul de TVA corect pentru vânzări către alte state UE" sunt două întrebări diferite, iar răspunsul la a doua e mai nuanțat.

## Temeiul legal

::: ghid-temei
„(2) Prin excepție de la prevederile alin. (1) lit. a), locul livrării în cazul vânzărilor intracomunitare de bunuri la distanță este considerat a fi locul în care se află bunurile în momentul în care se încheie expedierea sau transportul bunurilor către client."
— Codul fiscal, art. 275 alin. (2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„(1) Prevederile art. 275 alin. (2) și art. 278 alin. (5) lit. h) nu se aplică dacă sunt îndeplinite cumulativ următoarele condiții: [...] c) valoarea totală, fără TVA, a operațiunilor prevăzute la lit. b) nu depășește, în anul calendaristic curent, 10.000 euro sau echivalentul acestei sume în moneda națională și nici nu a depășit această sumă în cursul anului calendaristic precedent."
— Codul fiscal, art. 278^1 alin. (1) lit. c) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„(2) Prezentul regim special poate fi utilizat de către orice persoană impozabilă care are sediul activității economice în România [...] Regimul special poate fi utilizat în următoarele cazuri: a) de către orice persoană impozabilă care efectuează vânzări intracomunitare de bunuri la distanță."
— Codul fiscal, art. 315 alin. (2) lit. a) — Regimul special pentru vânzările intracomunitare de bunuri la distanță (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Peste pragul de 10.000 euro cumulat (bunuri + servicii electronice către persoane neimpozabile din UE), TVA datorat pentru o vânzare cu livrare într-un alt stat membru nu mai e cel românesc, ci cel al statului de destinație — declarat fie direct în acel stat, fie printr-o singură declarație OSS depusă în România.

## Ce se greșește în practică

- Se presupune că, odată conectat magazinul WooCommerce, aplicația de contabilitate „știe" automat să aplice cota de TVA a țării către care se livrează o comandă.
- Se ignoră cumulul anual de 10.000 euro pe toate statele UE, tratând fiecare vânzare izolat.
- Se confundă „poate importa comanda" cu „tratează corect fiscal comanda" — importul tehnic reușit nu înseamnă că regimul de TVA aplicat e cel corect pentru o vânzare la distanță peste prag.

## Ce face iConta.eu

Da, un magazin WooCommerce cu livrare externă UE poate folosi integrarea — mecanismul de import citește comenzile cu status `completed`/`processing` din API-ul WooCommerce și le transformă în facturi emise, fără să verifice sau să condiționeze nimic de adresa de livrare a comenzii. Configurarea (URL + chei de acces) și sincronizarea (automată, zilnică, sau manuală, la cerere) funcționează identic indiferent de țara clientului.

Limita reală, de spus onest: cota de TVA aplicată pe fiecare linie de comandă **nu vine niciodată din WooCommerce** — prețul preluat e fără TVA, iar cota o stabilește separat iConta, din nomenclatorul de produse propriu sau prin potrivire automată, pe baza regulilor românești de TVA (art. 291 CF — 21%/11%). Aplicația nu are o ramură separată care să aplice cota țării de destinație pentru o vânzare la distanță intracomunitară peste pragul de 10.000 euro, și nu ține un cumul automat al acestui prag. Practic: dacă vinzi sub prag, TVA românesc aplicat de aplicație e corect; dacă depășești pragul de 10.000 euro cumulat pe UE, integrarea tot importă comenzile și emite facturile, dar cota corectă pentru statul de destinație (și eventuala înregistrare OSS) rămân în sarcina ta, verificate manual — aplicația nu semnalează singură depășirea pragului.

De reținut și o a doua limită, independentă de subiectul TVA: importul din WooCommerce trimite explicit fiecare factură cu marcajul „persoană fizică" (`tert_pf=True`, în cod), indiferent de conținutul comenzii — decizia e declarată direct în sursă: „o comandă din magazinul online vine de la o persoană fizică fără cod fiscal". Dacă adresa de facturare din WooCommerce conține numele unei firme (câmpul „company"), acel nume ajunge totuși pe factură ca nume de client, dar codul fiscal (CUI) nu se preia niciodată — câmpul rămâne gol la orice import. Practic, nu există azi un mecanism prin integrare de a factura o comandă WooCommerce către un client cu cod fiscal propriu; dacă WooCommerce ar începe să trimită și CUI, ar trebui adăugată explicit o excepție de la acest marcaj implicit.

[iConta.eu](/)
