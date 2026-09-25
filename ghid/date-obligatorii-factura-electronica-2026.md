---
title: "Date obligatorii pe factura electronică 2026"
description: "Lista informațiilor pe care factura trebuie să le cuprindă obligatoriu, conform Codului fiscal, valabilă și pentru facturile electronice RO e-Factura."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Date obligatorii pe factura electronică 2026

Fie că e emisă pe hârtie sau electronic prin RO e-Factura, o factură trebuie să cuprindă un set minim de informații stabilit direct în Codul fiscal — lipsa oricăreia dintre ele face factura incompletă din punct de vedere fiscal.

## Temeiul legal

::: ghid-temei
„Factura cuprinde în mod obligatoriu următoarele informații: a) numărul de ordine, în baza uneia sau a mai multor serii, care identifică factura în mod unic; [...] b) data emiterii facturii; [...] d) denumirea/numele, adresa și codul de înregistrare în scopuri de TVA sau, după caz, codul de identificare fiscală ale persoanei impozabile care a livrat bunurile sau a prestat serviciile; [...] f) denumirea/numele și adresa beneficiarului bunurilor sau serviciilor, precum și codul de înregistrare în scopuri de TVA sau codul de identificare fiscală al beneficiarului [...]; h) denumirea și cantitatea bunurilor livrate, denumirea serviciilor prestate [...]; i) baza de impozitare a bunurilor și serviciilor [...], pentru fiecare cotă, scutire sau operațiune netaxabilă, prețul unitar, exclusiv taxa, precum și rabaturile, remizele, risturnele și alte reduceri de preț [...]; j) indicarea cotei de taxă aplicate și a sumei taxei colectate, exprimate în lei [...]."
— Legea 227/2015 (Codul fiscal), art. 319 alin. (20) lit. a), b), d), f), h), i), j) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce trebuie reținut, dincolo de lista propriu-zisă:

- Lista completă de la art. 319 alin. (20) e mai lungă decât fragmentul de mai sus (include și mențiuni speciale pentru scutiri, taxare inversă, regim de marjă etc.) — elementele reproduse aici sunt cele care lipsesc cel mai frecvent din facturile completate manual.
- Codul de identificare fiscală al beneficiarului (lit. f) e obligatoriu doar „dacă acesta este o persoană impozabilă ori o persoană juridică neimpozabilă" — pentru o persoană fizică simplă, cumpărător final, această mențiune nu se aplică la fel.
- Pentru facturile emise în relația B2B între persoane impozabile stabilite în România, legea consideră factură validă doar documentul care respectă și condițiile OUG 120/2021 privind RO e-Factura, pe lângă conținutul minim de la art. 319.

## Ce se greșește în practică

- Se omite baza de impozitare separată pe fiecare cotă de TVA, când factura are linii cu cote diferite (de exemplu 21% și 11%), agregând totul într-o singură sumă.
- Se completează codul de identificare fiscală al beneficiarului chiar și pentru persoane fizice care nu au calitatea de persoană impozabilă, sau invers, se omite pentru beneficiari care sunt firme.
- Se emite o factură fără număr secvențial unic pe serie, dublând sau sărind numere, ceea ce ridică probleme la validarea în RO e-Factura.

## Ce face iConta.eu

Modulul de facturare al iConta.eu generează facturile cu câmpurile obligatorii prevăzute de art. 319 alin. (20) — numerotare secvențială pe serie, datele părților, baza de impozitare pe fiecare cotă de TVA, cota și suma taxei — și le transmite apoi în sistemul RO e-Factura. Verificarea faptului că fiecare mențiune specială (scutire, taxare inversă, regim de marjă) e completă și corectă pentru operațiunea respectivă rămâne, totuși, în sarcina contabilului.

[iConta.eu](/)
