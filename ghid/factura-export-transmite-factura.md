---
title: "Factura de export se transmite în e-Factura?"
description: "Obligația B2B de transmitere în RO e-Factura vizează doar tranzacțiile dintre persoane impozabile stabilite în România, ceea ce exclude, de regulă, facturile de export."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Factura de export se transmite în e-Factura?

„Export" e un cuvânt cu două înțelesuri complet diferite în contabilitate: pe de-o parte, operațiunea vamală de livrare a unor bunuri/servicii către un client din afara României (uneori scutită de TVA), pe de altă parte, simpla transmitere tehnică a unui fișier de date către alt program. Întrebarea de aici privește primul sens — facturile de export propriu-zise — și dacă acestea intră sub obligația de transmitere în sistemul național RO e-Factura.

## Temeiul legal

::: ghid-temei
„În relația comercială B2B, între persoane impozabile stabilite în România conform art. 266 alin. (2) din Legea nr. 227/2015, cu modificările și completările ulterioare, emitentul facturii electronice are obligația de transmitere a acesteia către destinatar utilizând sistemul național privind factura electronică RO e-Factura, cu respectarea prevederilor art. 4 alin. (1). Fac excepție facturile simplificate emise conform art. 319 alin. (12) din Legea nr. 227/2015, cu modificările și completările ulterioare."
— OUG 120/2021, art. 10 alin. (1) (text în forma actuală, modificat prin OUG 115/2023, art. LXV pct. 4) (sursă: anaf_surse/oug_115_2023_consolidat.txt)
:::

- Obligația de transmitere B2B în RO e-Factura se aplică strict între **două persoane impozabile stabilite în România** (conform art. 266 alin. (2) din Codul fiscal). Un client dintr-un stat terț (destinația tipică a unei operațiuni de export) nu e o persoană impozabilă stabilită în România, deci relația nu se încadrează în definiția B2B din lege.
- Legea confirmă explicit acest raționament și pe cale de excepție: prevederile tranzitorii din Legea nr. 296/2023, art. LIX alin. (4) lit. b), exceptau de la obligația de transmitere „livrările de bunuri/prestările de servicii efectuate către persoane impozabile care nu sunt stabilite și nici înregistrate în scopuri de TVA în România" — exact profilul unui client de export dintr-un stat non-UE.
- Practic, factura de export nu are, de regulă, un destinatar care să declanșeze obligația legală de transmitere în RO e-Factura. Ea rămâne, în schimb, supusă regulilor obișnuite de emitere și, dacă e cazul, de justificare a scutirii de TVA la export.

## Ce se greșește în practică

- Se confundă „export" (operațiune vamală, cu client din afara României) cu orice altă noțiune tehnică de „export" folosită informal pentru transferul de date între programe — cele două nu au nicio legătură juridică.
- Se presupune greșit că orice factură emisă de o firmă românească trebuie transmisă obligatoriu în RO e-Factura, indiferent cine e destinatarul.
- Se omite verificarea statutului real al clientului (stabilit/înregistrat TVA în România sau nu) înainte de a decide dacă se aplică obligația B2B.

## Ce face iConta.eu

Din acest dosar de cercetare este documentată și verificată în cod o singură funcționalitate apropiată ca terminologie — F171, exportul facturilor emise către programul de contabilitate SAGA, în format XML propriu al SAGA. Aceasta nu are nicio legătură cu transmiterea facturilor în sistemul RO e-Factura/SPV: e o punte tehnică opțională între iConta.eu și programul contabilului, fără temei legal propriu (nicio citare de act normativ în codul modulului). Aplicația are, conform dosarului, și un fișier separat pentru transmiterea facturilor către e-Factura (`core/efactura_send.py`), dar comportamentul lui concret — inclusiv modul în care tratează facturile de export — nu a fost verificat în acest dosar, așa că nu facem afirmații neconfirmate despre el aici.

[iConta.eu](/)
