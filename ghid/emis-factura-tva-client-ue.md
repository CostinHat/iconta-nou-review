---
title: "Am emis factură cu TVA către un client din UE din greșeală"
description: "Condițiile scutirii de TVA pentru livrarea intracomunitară de bunuri și ce trebuie corectat pe factură atunci când TVA a fost aplicată greșit unui client din alt stat membru."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Am emis factură cu TVA către un client din UE din greșeală

Dacă ai emis o factură cu TVA românesc către un client stabilit în alt stat membru UE, deși operațiunea îndeplinea condițiile de scutire pentru livrare intracomunitară, factura trebuie corectată. Mai jos e condiția legală care declanșează scutirea și ce se greșește de obicei la verificarea ei.

## Temeiul legal

::: ghid-temei
„Sunt, de asemenea, scutite de taxă următoarele: a) livrările intracomunitare de bunuri către o persoană impozabilă sau către o persoană juridică neimpozabilă care acționează ca atare în alt stat membru decât cel în care începe expedierea sau transportul bunurilor, care îi comunică furnizorului un cod valabil de înregistrare în scopuri de TVA, atribuit de autoritățile fiscale din alt stat membru, cu excepția: 1. livrărilor intracomunitare efectuate de o întreprindere mică, altele decât livrările intracomunitare de mijloace de transport noi; [...] 2. livrărilor intracomunitare care au fost supuse regimului special pentru bunurile second-hand, opere de artă, obiecte de colecție și antichități, conform prevederilor art. 312 [...]"
— Legea 227/2015 (Codul fiscal), art. 294 alin. (2) lit. a) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Descompusă, condiția are trei elemente cumulative, toate trebuie verificate înainte de emitere:

- Cumpărătorul trebuie să fie **persoană impozabilă** (sau persoană juridică neimpozabilă care acționează ca atare) stabilită **în alt stat membru** decât cel din care pleacă marfa.
- Cumpărătorul trebuie să fi **comunicat furnizorului un cod valabil de TVA** atribuit de autoritățile fiscale din acel stat membru — practic, un cod verificabil în sistemul VIES la data operațiunii.
- Scutirea **nu** se aplică dacă furnizorul e o întreprindere mică (regimul special de scutire, altul decât pentru mijloace de transport noi) sau dacă bunurile intră sub regimul special second-hand/opere de artă (art. 312).

Când scutirea e aplicabilă, factura trebuie să conțină și mențiunea obligatorie de trimitere la scutire, cerută separat de Codul fiscal:

> „Factura cuprinde în mod obligatoriu următoarele informații: [...] l) în cazul în care este aplicabilă o scutire de taxă, trimiterea la dispozițiile aplicabile din prezentul titlu ori din Directiva 112 sau orice altă mențiune din care să rezulte că livrarea de bunuri ori prestarea de servicii face obiectul unei scutiri; [...]"
> — Codul fiscal, art. 319 alin. (20) lit. l) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

## Ce se greșește în practică

- Se presupune că orice client „din UE" beneficiază automat de scutire, fără să se verifice dacă are cod de TVA valid comunicat și activ la data livrării (nu la o dată ulterioară).
- Codul de TVA e verificat o singură dată, la începutul relației comerciale, și nu se mai reconfirmă pentru facturile ulterioare — codul poate fi între timp invalidat.
- Se aplică regula de la livrarea de bunuri (art. 294) și la prestări de servicii, deși servicii B2B intracomunitare au un regim de determinare a locului prestării diferit, care nu ține de acest articol.
- Se corectează factura greșită prin simpla emitere a uneia noi „cu suma fără TVA", fără storno pe factura inițială și fără mențiunea de scutire cerută de art. 319 alin. (20) lit. l).

## Ce face iConta.eu

`core/factura_pdf.py` (F045) este exclusiv un generator de PDF: randează datele deja calculate ale facturii (cotă TVA, sume, partener) exact cum sunt salvate în rândul din baza de date — aplicația **nu determină și nu verifică** regimul de TVA al operațiunii (dacă un client are cod valid VIES, dacă operațiunea e scutită etc.). Stabilirea corectă a regimului rămâne o decizie a contabilului, făcută înainte de emitere.

O precizare utilă pentru corectarea unei facturi de acest tip: chiar dacă reemiți factura cu regimul corect (scutire sau taxare inversă), generatorul de PDF **nu afișează mențiunea obligatorie** aferentă — nu citește deloc câmpul care marchează taxarea inversă, iar mențiunea de trimitere la scutire (lit. l) nu e randată automat pentru linii cu cotă 0%. Până la o eventuală reparație, mențiunea trebuie adăugată manual, de exemplu în câmpul de descriere a liniei, ca soluție de ocolire.

[iConta.eu](/)
