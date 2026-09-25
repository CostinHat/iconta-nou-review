---
title: "e-Factura la o firmă în lichidare"
description: "Dacă obligația RO e-Factura se menține pentru o societate aflată în lichidare și cum funcționează trimiterea în iConta.eu în această perioadă."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# e-Factura la o firmă în lichidare

O firmă intrată în lichidare nu dispare din circuitul fiscal din prima zi — își păstrează personalitatea juridică exact pentru operațiunile lichidării, inclusiv vânzarea activelor rămase. Cât timp mai emite facturi, obligația de a le transmite prin RO e-Factura rămâne aceeași ca înainte de dizolvare.

## Temeiul legal

::: ghid-temei
„Societatea își păstrează personalitatea juridică pentru operațiunile lichidării, până la terminarea acesteia."
— Legea 31/1990 (a societăților), art. 233 alin. (4) (sursă: anaf_surse/legea_31_1990_societatile.txt)
:::

- Lichidatorii pot, în cursul lichidării, „să vândă, prin licitație publică, imobilele și orice avere mobiliară a societății" și „să lichideze și să încaseze creanțele societății" (Legea 31/1990, art. 255) — deci firma poate continua să emită facturi (de exemplu la vânzarea activelor) pe toată durata lichidării.
- Legea B2B a e-Facturii nu prevede nicio excepție pentru firmele în lichidare: „În relația comercială B2B, între persoane impozabile stabilite în România [...], emitentul facturii electronice **are obligația** de transmitere a acesteia către destinatar utilizând sistemul național privind factura electronică RO e-Factura" (art. 10 alin. 1 OUG 120/2021, forma modificată prin Legea 296/2023) — obligația e legată de calitatea de persoană impozabilă stabilită în România, pe care societatea o păstrează pe durata lichidării.
- Nerespectarea obligației de transmitere se sancționează la fel, indiferent de starea societății: amendă egală cu 15% din valoarea facturii pentru nerespectarea obligației de transmitere (Legea 296/2023, art. 13^2 alin. 2).
- Radierea efectivă din registrul comerțului, care pune capăt personalității juridice, are loc abia la finalul lichidării — până atunci, obligațiile fiscale curente, inclusiv cele de facturare electronică, continuă să se aplice.

## Ce se greșește în practică

- Se presupune că, odată deschisă lichidarea, obligațiile de facturare electronică încetează automat — de fapt ele durează cât societatea mai are personalitate juridică și mai efectuează operațiuni impozabile.
- Se emit facturi „pe hârtie" sau prin alte canale în perioada de lichidare, considerând regimul B2B suspendat, deși legea nu prevede nicio excepție pentru această situație.
- Se confundă raportarea contabilă specifică lichidării (situațiile financiare de lichidare, depuse la finalul procesului) cu obligațiile curente de facturare — sunt cerințe diferite, cu momente diferite.

## Ce face iConta.eu

iConta **nu are nicio ramură de cod separată pentru facturarea unei firme aflate în lichidare** — nici în generarea și trimiterea facturilor prin RO e-Factura, nici în ecranul de facturi. O firmă marcată în lichidare emite și transmite facturi exact prin același flux ca oricare altă firmă: generare XML UBL/CIUS-RO, validare la validatorul public ANAF, apoi trimitere prin butonul „Trimite în SPV", cu urmărirea recipisei prin cronul de poll la 30 de minute. Nu există niciun blocaj, avertisment sau comportament diferit legat de starea de lichidare a firmei.

Modulul de lichidare al aplicației (notele contabile pentru vânzarea activelor și partajul final către asociați) e complet separat de motorul e-Factura — cele două nu comunică între ele. Dacă un activ e vândut în cursul lichidării și factura respectivă trebuie transmisă prin RO e-Factura, contabilul trece prin ecranul obișnuit de facturi, la fel ca la orice altă vânzare a firmei.

[iConta.eu](/)
