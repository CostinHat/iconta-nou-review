---
title: "Poate o firmă de închirieri imobiliare să fie microîntreprindere?"
description: "Verificarea condițiilor din Codul fiscal pentru ca o firmă cu activitate de închiriere de imobile să aplice impozitul pe veniturile microîntreprinderilor."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Poate o firmă de închirieri imobiliare să fie microîntreprindere?

Da. Activitatea de închiriere de imobile nu se numără printre activitățile excluse expres din sistemul de impunere pe veniturile microîntreprinderilor. O firmă cu acest obiect de activitate poate fi microîntreprindere dacă îndeplinește condițiile generale de la art. 47 alin. (1) din Codul fiscal, la fel ca orice altă persoană juridică română.

## Temeiul legal

::: ghid-temei
„(3) Nu intră sub incidența prezentului titlu următoarele persoane juridice române: [...]
f) persoana juridică română care desfășoară activități în domeniul bancar;
g) persoana juridică română care desfășoară activități în domeniul asigurărilor și reasigurărilor, al pieței de capital, precum și persoana juridică română care desfășoară activități de intermediere/distribuție în aceste domenii, cu excepția intermediarilor secundari de asigurări și/sau reasigurări [...] care au realizat venituri din activitatea de distribuție de asigurări/reasigurări în proporție de până la 15% inclusiv din veniturile totale;
h) persoana juridică română care desfășoară activități în domeniul jocurilor de noroc;
i) persoana juridică română care desfășoară activități de explorare, dezvoltare, exploatare a zăcămintelor de petrol și gaze naturale."
— Legea nr. 227/2015 (Codul fiscal), art. 47 alin. (3) lit. f)-i) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Lista de la art. 47 alin. (3) este exhaustivă și cuprinde doar patru domenii: bancar, asigurări/reasigurări/piață de capital, jocuri de noroc și explorare/exploatare petrol și gaze. Închirierea de imobile nu apare printre ele, deci o firmă din acest domeniu trebuie doar să verifice condițiile generale de la art. 47 alin. (1):

- venituri realizate care nu depășesc echivalentul a 100.000 euro (la 31 decembrie a anului precedent, cumulat, dacă e cazul, cu veniturile întreprinderilor legate);
- capitalul social deținut de alte persoane decât statul și unitățile administrativ-teritoriale;
- firma nu se află în dizolvare urmată de lichidare;
- are cel puțin un salariat (cu excepțiile de la art. 48 alin. (3));
- dacă are asociați care dețin peste 25% și la alte firme eligibile pentru micro, este singura desemnată să aplice regimul micro;
- a depus la termen situațiile financiare anuale, dacă avea această obligație.

## Ce se greșește în practică

- Se presupune, din analogie cu regimul PFA (unde veniturile din chirii sunt tratate distinct, ca venituri din cedarea folosinței bunurilor), că și la nivel de SRL activitatea de închiriere ar avea un tratament special la impozitul micro — nu este cazul; SRL-ul e tratat unitar, indiferent de obiectul de activitate, în afara celor patru excluderi de la art. 47 alin. (3).
- Se confundă lista de excluderi din sistemul micro cu lista veniturilor din chirii impozabile separat la persoane fizice (titlul IV) — sunt regimuri fiscale diferite, pentru contribuabili diferiți.
- Se ignoră condiția salariatului (art. 47 alin. (1) lit. g)), frecvent nerespectată la firmele mici de administrare a unui singur imobil închiriat, care nu au niciun angajat.

## Ce face iConta.eu

La data acestui ghid, iConta.eu nu are o funcționalitate care să verifice automat, în funcție de codul CAEN al firmei, dacă activitatea desfășurată se încadrează în excluderile de la art. 47 alin. (3). Aplicația permite setarea manuală a regimului fiscal al firmei (`regim_fiscal` = „micro" sau „profit", în `core/vector_fiscal_api.py`), pe baza căreia stabilește declarațiile datorate (D100 trimestrial pentru micro, D101 anual pentru profit, via `core/d100.py` și `core/d101.py`). Evaluarea eligibilității propriu-zise, inclusiv verificarea că activitatea de închiriere nu intră în vreo excludere, rămâne responsabilitatea contabilului.

[iConta.eu](/)
