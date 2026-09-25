---
title: "Pot emite factură în aceeași zi în care primesc CUI-ul firmei?"
description: "De ce firma poate emite facturi din prima zi de existență juridică, fără o perioadă de așteptare, chiar dacă nu e încă plătitoare de TVA."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Pot emite factură în aceeași zi în care primesc CUI-ul firmei?

Da. Din momentul înmatriculării în registrul comerțului, firma are personalitate juridică deplină și codul ei unic de înregistrare — nu există o perioadă de așteptare legală înainte de a putea emite prima factură.

## Temeiul legal

::: ghid-temei
„Societatea este persoană juridică de la data înmatriculării în registrul comerțului."
— Legea 31/1990 privind societățile, art. 41 alin. (1) (sursă: anaf_surse/legea_31_1990_societatile.txt)
:::

- Personalitatea juridică — și, odată cu ea, capacitatea de a încheia acte comerciale, inclusiv de a emite facturi — se dobândește chiar la data înmatriculării, nu la o dată ulterioară.
- Orice persoană sau entitate subiect al unui raport juridic fiscal primește un cod de identificare fiscală la înregistrare (art. 82 alin. (1) Cod de procedură fiscală) — CUI-ul e disponibil din acel moment, fără un termen suplimentar de „activare".
- Dacă firma nu e încă înregistrată în scopuri de TVA (art. 316 CF), facturile se emit **fără TVA**, ca operațiuni ale unei persoane neplătitoare — asta nu împiedică emiterea facturii, doar îi schimbă conținutul (fără linie de TVA colectată).
- Odată ce firma se înregistrează în scopuri de TVA, obligația de a menționa distinct cota și suma taxei colectate pe fiecare factură (art. 319 alin. (20) lit. j) CF) devine aplicabilă de la data înregistrării.

## Ce se greșește în practică

- Se amână emiterea primei facturi din prudență, crezând că e nevoie de o perioadă de „activare" a CUI-ului — legal, firma poate acționa comercial din ziua înmatriculării.
- Se presupune că lipsa înregistrării în scopuri de TVA împiedică emiterea facturii — o firmă neplătitoare de TVA poate factura normal, doar fără linie de TVA pe document.
- Se confundă obținerea CUI-ului (la înmatriculare) cu obținerea statutului de plătitor de TVA (proces separat, prin înregistrare conform art. 316 CF) — sunt momente diferite, iar factura se poate emite valabil chiar înainte de al doilea.

## Ce face iConta.eu

Validarea CUI la ANAF din iConta.eu interoghează serviciul oficial ANAF pentru un CUI dat și întoarce, printre altele, statutul de plătitor de TVA al firmei — funcția e folosită la verificarea partenerilor. Verificarea automată a codului de TVA în VIES nu are loc la emiterea oricărei facturi către un partener cu cod de prefix non-românesc: ea rulează doar în fluxul dedicat de „Vânzare intracomunitară" (`core/uc_tenants.py::vanzare_ic`), unde codul de TVA al clientului, tipul operațiunii (bunuri/servicii) și dovada transportului se introduc explicit, iar `core/intracomunitar.py::verifica_vies` interoghează serviciul oficial VIES înainte de a genera factura. Fluxul obișnuit de emitere a unei facturi (`core/facturi_api.py::emite_factura`) nu conține nicio verificare VIES. Emiterea propriu-zisă a facturii nu e condiționată în aplicație de vreo perioadă de așteptare de la înființarea firmei — odată introdusă firma și datele ei (inclusiv statutul de plătitor/neplătitor de TVA), iConta permite emiterea de facturi din prima zi, cu sau fără TVA, conform statutului fiscal real al firmei la acel moment.

[iConta.eu](/)
