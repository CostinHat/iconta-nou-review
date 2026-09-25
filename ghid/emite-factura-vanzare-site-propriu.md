---
title: "Cum se emite factura pentru o vânzare pe un site propriu"
description: "Regulile de facturare pentru vânzările făcute printr-un magazin online propriu, inclusiv obligația de transmitere prin RO e-Factura pentru vânzările către persoane fizice, din 2025."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se emite factura pentru o vânzare pe un site propriu

O vânzare printr-un site propriu urmează regulile obișnuite de facturare din Codul fiscal, indiferent de canal. Diferența față de un magazin fizic ține de obligația RO e-Factura: din 1 ianuarie 2025, și vânzările către persoane fizice (relația B2C), nu doar cele către alte firme (B2B), intră sub obligația de transmitere a facturii prin sistemul național RO e-Factura — cu excepția bonurilor fiscale care îndeplinesc condițiile unei facturi simplificate.

## Temeiul legal

::: ghid-temei
„(2) Începând cu data de 1 ianuarie 2025, operatorii economici - persoane impozabile stabilite în România conform art. 266 alin. (2) din Legea nr. 227/2015, cu modificările și completările ulterioare, indiferent dacă sunt sau nu înregistrați în scopuri de TVA conform art. 316 din Legea nr. 227/2015, cu modificările și completările ulterioare, pentru livrările de bunuri și prestările de servicii care au locul livrării/prestării în România [...], efectuate în relația B2C, astfel cum este definită la art. 2 alin. (1) lit. n^1), au obligația să transmită facturile emise în sistemul național privind factura electronică RO e-Factura. Fac excepție bonurile fiscale emise în conformitate cu prevederile Ordonanței de urgență a Guvernului nr. 28/1999 [...], care îndeplinesc condițiile unei facturi simplificate [...].
(3) Livrările de bunuri/Prestările de servicii efectuate către o persoană fizică care nu se identifică în relația cu furnizorul/prestatorul prin niciun cod de identificare fiscală sau optează să se identifice prin codul numeric personal se consideră efectuate în relația B2C. Dacă beneficiarul, persoană fizică, nu se identifică prin niciun cod de identificare fiscală, facturile se emit utilizând un cod format din 13 cifre de zero în locul codului de identificare fiscală a beneficiarului."
— OUG 138/2024, care modifică art. 10^1 alin. (2) și (3) din OUG 120/2021 privind sistemul RO e-Factura (sursă: anaf_surse/oug_138_2024.txt)
:::

- Obligația de transmitere prin RO e-Factura pentru vânzările B2C se aplică operatorilor economici stabiliți în România, indiferent dacă sunt sau nu plătitori de TVA, pentru livrări/prestări cu locul în România.
- Vânzarea printr-un site propriu, către un client persoană fizică ce cumpără pentru consum propriu, e o operațiune B2C tipică — dacă persoana fizică nu comunică un cod de identificare fiscală, factura se emite cu un cod format din 13 cifre de zero în locul acestuia.
- Excepția principală: bonurile fiscale emise conform legii caselor de marcat, dacă îndeplinesc condițiile unei facturi simplificate, nu trebuie transmise separat prin RO e-Factura.
- Regulile generale de facturare (elemente obligatorii ale facturii, termene de emitere) rămân cele din Codul fiscal (art. 319); RO e-Factura e canalul obligatoriu de transmitere, nu o factură diferită de cea „clasică".
- Dacă site-ul propriu vinde și către alte firme (B2B), pentru acele tranzacții se aplică regimul B2B, în vigoare din 2024, cu propriile termene de transmitere (5 zile lucrătoare de la emitere).

## Ce se greșește în practică

- Se emite factura „clasică" pentru vânzarea online, fără să se transmită prin sistemul RO e-Factura, considerând greșit că obligația B2C nu vizează micile magazine online sau firmele neplătitoare de TVA — obligația se aplică indiferent de înregistrarea în scopuri de TVA.
- Se confundă vânzarea printr-un site propriu cu emiterea unui simplu bon fiscal, uitând că, dacă se emite factură (nu doar bon fiscal), aceasta intră sub obligația de transmitere RO e-Factura.
- Nu se completează corect codul de identificare al cumpărătorului persoană fizică atunci când acesta nu îl comunică — legea cere explicit codul de 13 zerouri în acest caz, nu lăsarea câmpului necompletat.
- Se presupune că regulile B2C se aplică și vânzărilor către alte firme făcute prin același site — cele două relații (B2B/B2C) au reglementări și termene distincte.

## Ce face iConta.eu

iConta.eu **are un modul general de facturare** (`facturi_api.py`), care calculează totalul și TVA din liniile facturii, și un modul de transmitere RO e-Factura (`efactura_send.py`), care generează XML-ul UBL 2.1/CIUS-RO și îl trimite către ANAF prin OAuth. În plus, pentru magazinele online construite pe WooCommerce, aplicația **are un conector dedicat** (`core/woocommerce.py`), care citește periodic comenzile din magazin prin API-ul WooCommerce și emite automat facturi corespunzătoare (idempotent, pe numărul comenzii, pentru a nu duplica o comandă deja preluată). Pentru un site propriu construit pe altă platformă decât WooCommerce, această preluare automată nu există, iar emiterea facturii se face, la fel ca pentru orice altă vânzare, prin introducerea manuală a datelor în ecranul de facturi al aplicației.

[iConta.eu](/)
