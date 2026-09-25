---
title: "Factura în regim TVA la încasare în e-Factura"
description: "Ce trebuie să conțină, din punct de vedere legal, o factură electronică emisă de o firmă la TVA la încasare, dincolo de simpla ei transmitere."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Factura în regim TVA la încasare în e-Factura

O factură emisă de o firmă înscrisă la TVA la încasare nu are o structură XML diferită față de o factură obișnuită — standardul RO_CIUS nu prevede un tip de document separat pentru acest regim. Diferența stă exclusiv în conținut: legea impune o mențiune obligatorie pe factură, indiferent de canalul prin care e transmisă (hârtie, PDF sau XML electronic).

## Temeiul legal

::: ghid-temei
„Elementele facturii [...] p) în cazul în care exigibilitatea TVA intervine la data încasării contravalorii integrale sau parțiale a livrării de bunuri ori a prestării de servicii, mențiunea «TVA la încasare»."
— Codul fiscal, art. 319 alin. (20) lit. p) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Legea nu cere un tip de factură distinct (`InvoiceTypeCode` diferit în UBL) pentru TVA la încasare — cere doar prezența unei mențiuni text pe document, alături de celelalte elemente obligatorii de la art. 319 alin. (20) (denumirea părților, baza de impozitare, cota, suma taxei etc.).
- Mențiunea trebuie citită de destinatar ca un semnal: dacă el e plătitor de TVA, dreptul lui de deducere pentru factura respectivă e amânat până când plătește furnizorul (art. 297 alin. 2) — deci conținutul facturii are efect direct asupra contabilității cumpărătorului, nu doar a emitentului.
- Restul conținutului obligatoriu (cotă, bază, sumă TVA) se calculează la fel ca la orice altă factură — regimul de TVA la încasare schimbă *momentul* la care taxa devine exigibilă (art. 282 alin. 3), nu *modul* în care se calculează suma taxei pe factură.
- Cota aplicabilă urmează regula specială de la art. 291 alin. (5): cea de la data faptului generator, cu excepția facturii/avansului emis(e) înainte de livrare, caz în care se aplică cota de la acea dată.

## Ce se greșește în practică

- Se pune mențiunea "TVA la încasare" doar pe factura tipărită/PDF pentru client, considerând-o o formalitate vizuală, fără să se verifice dacă apare și în factura electronică propriu-zisă transmisă prin sistemul național.
- Se presupune că lipsa mențiunii pe o factură electronică poate fi "reparată" ulterior printr-o notificare separată către client — legea cere mențiunea pe factură, nu pe o comunicare adiacentă.
- Se aplică o cotă de TVA greșită pe factura de avans emisă înainte de livrare, ignorând regula specială de la art. 291 alin. (5), care diferă de regula generală de la alin. (4).
- Se confundă absența mențiunii cu absența dreptului legal la amânarea deducerii la cumpărător — regula de la art. 297 alin. (2) se aplică prin efectul legii, indiferent dacă factura poartă sau nu mențiunea corectă; lipsa ei creează doar risc de eroare pentru cumpărător, nu anulează regula.

## Ce face iConta.eu

iConta.eu calculează corect baza de impozitare, cota (inclusiv regula specială art. 291 alin. 5, implementată separat în `core/cota_tva_incasare.py`) și suma TVA pe fiecare linie de factură, indiferent de regimul TVA al firmei. Generatorul de facturi electronice (`core/efactura_send.py`, F126) construiește un XML UBL/CIUS-RO valid din aceste date.

Ce nu face, verificat direct în cod: generatorul XML-ului nu include nicăieri mențiunea text „TVA la încasare" cerută de art. 319 alin. (20) lit. p) — categoriile de TVA folosite în XML sunt doar standard ("S") și cotă zero ("Z"), fără vreo mențiune sau categorie distinctă pentru regimul de încasare. Conținutul facturii electronice, așa cum e generat azi de aplicație, e deci incomplet față de cerința legală de mai sus pentru o firmă la TVA la încasare — un gol pe care contabilul trebuie să-l suplinească manual, prin alt mijloc, până la o actualizare a generatorului.

[iConta.eu](/)
