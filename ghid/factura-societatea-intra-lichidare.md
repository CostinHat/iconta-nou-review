---
title: "Ce fac cu e-Factura când societatea intră în lichidare?"
description: "De ce obligația de transmitere a facturilor prin RO e-Factura nu încetează la deschiderea lichidării, ci abia la radierea firmei, conform Codului fiscal."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce fac cu e-Factura când societatea intră în lichidare?

Deschiderea procedurii de lichidare nu scoate firma din sistemul RO e-Factura. Cât timp societatea există ca persoană juridică și emite facturi pentru operațiuni realizate în România, obligația de transmitere electronică rămâne neschimbată — inclusiv pentru facturile emise de lichidator în cursul lichidării.

## Temeiul legal

::: ghid-temei
„(1^1) Prin excepție de la prevederile alin. (1), pentru operațiunile realizate între persoane impozabile stabilite în România conform art. 266 alin. (2), sunt considerate facturi numai facturile care îndeplinesc condițiile prevăzute de Ordonanța de urgență a Guvernului nr. 120/2021 privind administrarea, funcționarea și implementarea sistemului național privind factura electronică RO e-Factura și factura electronică în România [...], cu modificările și completările ulterioare."
— Legea nr. 227/2015 (Codul fiscal), art. 319 alin. (1^1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce rezultă din text pentru o firmă în lichidare:

- Obligația de a transmite facturile prin RO e-Factura este legată de calitatea de **persoană impozabilă stabilită în România**, conform art. 266 alin. (2) — nu de faptul că firma funcționează „normal" sau se află în lichidare. Cât timp firma nu a fost radiată din registrul comerțului, ea rămâne persoană impozabilă stabilită și obligația subzistă.
- Legea nu prevede nicio excepție sau suspendare a obligației RO e-Factura pentru perioada de lichidare — nici pentru facturile emise către alți operatori economici (B2B), nici, dacă e cazul, pentru cele către instituții publice.
- În consecință, orice factură emisă în cursul lichidării — de exemplu pentru vânzarea de active ale societății — trebuie să îndeplinească aceleași condiții prevăzute de OUG 120/2021 ca orice factură emisă înainte de deschiderea procedurii.
- Obligația încetează doar odată cu radierea efectivă a societății, moment din care firma nu mai există ca persoană impozabilă și nu mai emite facturi.

## Ce se greșește în practică

- Se presupune că, odată deschisă lichidarea, facturarea „simplificată", fără RO e-Factura, devine acceptabilă, pentru că firma „oricum se închide".
- Se încetează transmiterea facturilor în sistem imediat ce apare mențiunea „societate în lichidare" în datele firmei, deși radierea nu a avut încă loc.
- Nu se verifică dacă lichidatorul numit are acces la contul SPV al firmei pentru a continua transmiterea facturilor pe durata lichidării.

## Ce face iConta.eu

La data acestui ghid, iConta.eu are module dedicate atât pentru transmiterea facturilor prin RO e-Factura (`core/efactura_send.py`, `core/efactura_trimitere.py`), cât și pentru tratamentul fiscal specific lichidării — de exemplu calculul cotei de impozit pe câștigul din lichidare la asociatul persoană fizică (`core/lichidare.py`, cota de 10% conform art. 97 alin. (5) din Codul fiscal). Aplicația **nu suspendă și nu oprește automat fluxul de e-Factura** atunci când o firmă e marcată ca aflându-se în lichidare — facturile continuă să fie generate și transmise prin același flux ca înainte, atâta vreme cât firma rămâne activă și înregistrată, iar utilizatorul are acces la conectorul SPV configurat.

[iConta.eu](/)
