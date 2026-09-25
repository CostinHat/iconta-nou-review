---
title: "Cum găsesc rapid o factură veche în arhiva e-Factura?"
description: "De ce căutarea rapidă a unei facturi vechi transmise prin SPV se face în evidența proprie a firmei, nu direct în arhiva ANAF, și ce oferă iConta.eu pentru asta."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum găsesc rapid o factură veche în arhiva e-Factura?

Toate facturile transmise sau primite prin sistemul RO e-Factura rămân disponibile în Spațiul Privat Virtual (SPV), dar portalul ANAF nu este gândit ca instrument de căutare rapidă pentru uz curent — interogarea facturilor prin API-ul RO e-Factura se face pe intervale de date și necesită autentificare cu certificat digital la fiecare căutare. De aceea, firmele care emit sau primesc volum mare de facturi țin propria evidență, sincronizată local, tocmai pentru a regăsi rapid o factură veche fără să interogheze de fiecare dată ANAF.

## Temeiul legal

::: ghid-temei
„(10) Prin excepție de la prevederile alin. (6) lit. a), persoana impozabilă este scutită de obligația emiterii facturii pentru următoarele operațiuni, cu excepția cazului în care beneficiarul solicită factura: a) livrările de bunuri prin magazinele de comerț cu amănuntul și prestările de servicii către populație, pentru care este obligatorie emiterea de bonuri fiscale [...], conform Ordonanței de urgență a Guvernului nr. 28/1999 privind obligația operatorilor economici de a utiliza aparate de marcat electronice fiscale, republicată, cu modificările și completările ulterioare."
— Legea nr. 227/2015 (Codul fiscal), art. 319 alin. (10) lit. a) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Citatul de mai sus nu privește direct arhivarea, ci delimitează ce operațiuni sunt obligate să emită factură (deci să existe în SPV) — este relevant pentru a înțelege de ce nu orice vânzare a firmei apare în arhiva e-Factura: vânzările către populație, documentate prin bonuri fiscale, rămân în afara sistemului RO e-Factura, cu excepția cazului în care clientul cere expres factură.

- Facturile **B2B** intră obligatoriu în sistemul RO e-Factura și rămân disponibile în arhiva SPV a firmei emitente și a celei destinatare.
- Vânzările **către populație**, documentate prin bon fiscal, nu generează automat o factură în arhiva e-Factura, decât dacă a fost solicitată expres de client.
- Regăsirea rapidă a unei facturi vechi ține, deci, de organizarea evidenței proprii a firmei (numerotare, arhivare locală, registre), nu doar de arhiva SPV, care nu conține absolut toate documentele de vânzare ale firmei.

## Ce se greșește în practică

- Se caută o factură veche direct pe portalul ANAF, de fiecare dată, deși interogarea SPV e gândită pentru descărcare pe interval de date, nu pentru căutare punctuală rapidă.
- Se presupune că orice vânzare a firmei, inclusiv cele către persoane fizice cu bon fiscal, se regăsește automat în arhiva e-Factura.
- Se renunță la o evidență proprie, locală, a facturilor, considerând arhiva ANAF suficientă — ceea ce face imposibilă o căutare rapidă după client, sumă sau produs, criterii pe care portalul ANAF nu le oferă nativ.

## Ce face iConta.eu

La data acestui ghid, iConta.eu importă și înregistrează local facturile primite și trimise prin RO e-Factura (`core/efactura_import.py`, `core/efactura_send.py`), iar funcția `lista_facturi` din `core/facturi_api.py` permite filtrarea facturilor proprii după an, lună și direcție (emise/primite), direct din evidența firmei, fără interogarea portalului ANAF de fiecare dată. Aplicația nu oferă însă un motor de căutare full-text peste conținutul facturilor (produse, descrieri) și nu înlocuiește arhiva oficială SPV ca sursă legală a documentului original.

[iConta.eu](/)
