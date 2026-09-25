---
title: "Regularizarea facturilor vechi prin e-Factura"
description: "Cum se corectează prin sistemul RO e-Factura o factură emisă anterior, conform mecanismului de corectare prevăzut de Codul fiscal."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Regularizarea facturilor vechi prin e-Factura

Când o factură emisă anterior trebuie corectată — pentru că a fost greșită, sau pentru că baza de impozitare s-a modificat ulterior — corecția nu înseamnă „ștergerea" facturii vechi, ci emiterea unei noi facturi, structurate potrivit unei reguli precise din Codul fiscal. Dacă furnizorul e obligat să transmită facturi prin RO e-Factura, corecția urmează același drum ca orice altă factură emisă.

## Temeiul legal

::: ghid-temei
„(1) Corectarea informațiilor înscrise în facturi sau în alte documente care țin loc de factură se efectuează astfel: [...] b) în cazul în care factura a fost transmisă beneficiarului, fie se emite o nouă factură care trebuie să cuprindă, pe de o parte, informațiile din factura inițială, numărul și data facturii corectate, valorile cu semnul minus sau, după caz, o mențiune din care să rezulte că valorile respective sunt negative, iar, pe de altă parte, informațiile și valorile corecte, fie se emite o nouă factură conținând informațiile și valorile corecte și concomitent se emite o factură cu valorile cu semnul minus sau, după caz, cu o mențiune din care să rezulte că valorile respective sunt negative, în care se înscriu numărul și data facturii corectate."
— Codul fiscal (Legea 227/2015), art. 330 alin. (1) lit. b) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Regularizarea unei facturi deja transmise beneficiarului se face printr-una din cele două variante permise: fie o singură factură nouă care cuprinde atât stornarea (valorile vechi, cu semnul minus) cât și valorile corecte, fie două facturi separate — una cu valorile corecte, una de stornare a facturii inițiale (cu referire explicită la numărul și data acesteia).
- Orice factură de corecție trebuie să facă trimitere expresă la factura inițială corectată (numărul și data ei), astfel încât legătura dintre cele două documente să fie clară și verificabilă.
- Dacă factura inițială cade sub incidența obligației de transmitere prin RO e-Factura, și factura de corecție trebuie transmisă prin același sistem, cu respectarea termenului legal de 5 zile lucrătoare de la emitere — regularizarea unei facturi „vechi" nu scutește de această obligație curentă.

## Ce se greșește în practică

- Se corectează o factură veche doar în evidența contabilă internă, fără emiterea uneia dintre cele două variante de document prevăzute de art. 330 alin. (1) lit. b), ceea ce lasă beneficiarul fără un document opozabil pentru corecție.
- Se emite factura de corecție fără să se menționeze explicit numărul și data facturii inițiale corectate, ceea ce face imposibilă legarea celor două documente la o verificare ulterioară.
- Se uită transmiterea facturii de corecție prin RO e-Factura, atunci când furnizorul are obligația generală de raportare prin acest sistem — se presupune, greșit, că doar facturile „noi" trebuie transmise, nu și corecțiile celor vechi.

## Ce face iConta.eu

iConta.eu are integrare cu RO e-Factura pentru generarea și transmiterea facturilor emise (`efactura_send.py`), construită pe structura XML UBL 2.1 / CIUS-RO cerută de ANAF. La verificarea codului, aplicația are o funcție dedicată de stornare (`facturi_api.storneaza`, expusă prin ruta `/tenants/{tenant_id}/facturi/{factura_id}/storno`): pe baza unei facturi emise existente, generează automat o factură de stornare cu liniile copiate și cantitățile cu semn negativ, cu număr propriu din aceeași serie și cu referință explicită la factura originală (`storno_din_id`) — corespunde variantei de la art. 330 alin. (1) lit. b) în care se emite o factură separată cu valorile cu semnul minus. Factura de stornare astfel generată intră apoi în același flux de transmitere prin RO e-Factura ca orice altă factură emisă. Emiterea facturii ulterioare, cu valorile corecte, rămâne o operațiune separată a utilizatorului — aplicația nu leagă automat cele două documente într-un singur pas.

[iConta.eu](/)
