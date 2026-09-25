---
title: "Ce date preia automat iConta din comenzile WooCommerce?"
description: "Lista exactă a câmpurilor pe care iConta.eu le citește dintr-o comandă WooCommerce la transformarea ei în factură — și, la fel de important, ce nu preia niciodată."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce date preia automat iConta din comenzile WooCommerce?

Conectorul WooCommerce al iConta.eu nu importă „toată comanda" așa cum arată ea în magazin, ci un set precis de câmpuri, mapate direct pe structura unei facturi. E util să știi exact ce se preia automat și ce rămâne, totuși, decizia aplicației (nu a magazinului tău online).

## Temeiul legal

Ce anume citește un conector dintr-o comandă de magazin online este o decizie tehnică a aplicației, nu o obligație legală — nu există o normă care să impună ce câmpuri trebuie preluate automat dintr-o platformă e-commerce. Ce contează legal e rezultatul: factura emisă trebuie să conțină elementele obligatorii prevăzute de legea facturării și să aplice corect cota de TVA — de aceea iConta.eu nu preia orbește cota de TVA din magazin (vezi mai jos), ci o stabilește ea însăși, conform regulilor fiscale.

## Ce se greșește în practică

- Se confundă „prețul preluat din WooCommerce" cu „TVA-ul preluat din WooCommerce" — cele două nu sunt același lucru. iConta preia doar prețul unitar (calculat din valoarea totală a liniei împărțită la cantitate), niciodată cota de TVA.
- Se presupune că, dacă la datele de facturare din comandă (billing) e completat un nume de firmă, factura va fi emisă către acea firmă, cu CUI propriu — nu se întâmplă: orice comandă e tratată ca vânzare către persoană fizică.
- Se așteaptă ca numărul comenzii din WooCommerce să apară identic pe factură — de fapt el ajunge în câmpul intern de sursă externă, folosit pentru a evita importul dublu, nu neapărat afișat ca atare pe factură.

## Ce face iConta.eu

Din fiecare comandă cu statusul `completed` sau `processing`, iConta.eu citește: numărul comenzii (sau, dacă lipsește, id-ul intern), data, numele terțului — `billing.company` dacă e completat, altfel prenume + nume din billing, iar dacă nici acestea nu există, textul generic „client web" —, moneda, și liniile de produse: descriere, cantitate și preț unitar (calculat ca total împărțit la cantitate, rotunjit la 2 zecimale), exact așa cum vine calculat de WooCommerce. **Cota de TVA nu se preia niciodată din magazin** — pe fiecare linie e lăsată nedeterminată la import, iar iConta o stabilește separat, din nomenclatorul de produse sau prin recunoaștere automată, niciodată printr-o valoare implicită ghicită. Fiecare comandă e importată o singură dată: dacă a fost deja transformată în factură, o rulare ulterioară o sare automat.

[iConta.eu](/)
