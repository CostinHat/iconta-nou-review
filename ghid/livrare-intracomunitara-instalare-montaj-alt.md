---
title: "Livrare intracomunitară cu instalare sau montaj în alt stat"
description: "Bunurile livrate cu instalare sau montaj de către furnizor nu sunt livrare intracomunitară scutită — locul livrării e unde se face montajul, iar TVA se tratează după regulile acelui stat."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Livrare intracomunitară cu instalare sau montaj în alt stat

Regula de bază a livrării intracomunitare scutite (cod TVA valid + dovada transportului) nu se aplică bunurilor pe care furnizorul le instalează sau le montează în statul de destinație — pentru acestea, locul livrării nu mai e locul de plecare al transportului, ci locul montajului.

## Temeiul legal

::: ghid-temei
„Se consideră a fi locul livrării de bunuri: [...] b) locul unde se efectuează instalarea sau montajul, de către furnizor ori de către altă persoană în numele furnizorului, în cazul bunurilor care fac obiectul unei instalări sau unui montaj."
— Codul fiscal (Legea 227/2015), art. 275 alin. (1) lit. b) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„[...] o achiziție intracomunitară de bunuri [...] care urmează unei livrări intracomunitare efectuate în afara României de către o persoană impozabilă ce acționează ca atare și care nu este considerată întreprindere mică în statul membru în care are loc livrarea și căreia nu i se aplică prevederile art. 275 alin. (1) lit. b) cu privire la livrările de bunuri care fac obiectul unei instalări sau unui montaj sau ale art. 275 alin. (2) cu privire la vânzările la distanță."
— Codul fiscal, art. 268 alin. (3) lit. a) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce înseamnă practic pentru o firmă din România care livrează bunuri cu montaj în alt stat membru:

- Livrarea nu e o livrare intracomunitară scutită în sensul obișnuit — art. 275 exclude expres din acest regim bunurile livrate după asamblare sau instalare de către furnizor. Locul livrării e locul montajului, nu locul de plecare a bunurilor din România.
- Dacă montajul are loc într-un alt stat membru, furnizorul din România devine, de regulă, persoană obligată la plata TVA în acel stat (sau, în anumite condiții, se aplică mecanismul de taxare inversă, cu beneficiarul ca plătitor) — regulile concrete se stabilesc după legislația statului de montaj, nu doar după Codul fiscal românesc.
- Operațiunea nu se raportează ca livrare intracomunitară „L" în declarația recapitulativă (D390), pentru că nu se încadrează în scutirea de la art. 294 alin. (2) lit. a) — se tratează, de regulă, ca operațiune fără loc de impozitare în România.
- Distincția contează și pentru facturare: factura nu poartă mențiunea de scutire pentru livrare intracomunitară, ci trebuie să reflecte tratamentul TVA real al operațiunii cu montaj.

## Ce se greșește în practică

- Se facturează livrarea cu montaj ca livrare intracomunitară scutită obișnuită, cu mențiunea „scutit conform art. 294 alin. (2) lit. a)" — mențiunea nu e corectă, pentru că acest tip de bunuri e exclus explicit din regimul respectiv.
- Se verifică doar codul de TVA al clientului și dovada transportului (ca la o livrare intracomunitară normală), ignorând faptul că locul livrării s-a mutat în statul de montaj.
- Se presupune că regulile românești de TVA guvernează integral operațiunea, deși obligația de înregistrare sau de plată a taxei se stabilește, de regulă, după legislația statului unde are loc montajul.

## Ce face iConta.eu

`core/intracomunitar.py`, modulul de operațiuni intracomunitare al iConta.eu, implementează validarea livrării intracomunitare scutite standard (`valideaza_lic`) — cod TVA valid în VIES plus dovada transportului — potrivit art. 294 alin. (2) lit. a) din Codul fiscal. Modulul nu tratează explicit excepția bunurilor livrate cu instalare sau montaj (art. 275 alin. (1) lit. b)): dacă o astfel de operațiune ar fi introdusă prin funcția de validare a livrării intracomunitare obișnuite, aplicația nu semnalează că regimul de scutire nu se aplică bunurilor montate de furnizor.

Pentru livrări cu instalare sau montaj în alt stat membru, tratamentul TVA corect — inclusiv o eventuală obligație de înregistrare în statul de montaj — trebuie stabilit manual de contabil, pe baza legislației aplicabile în acel stat.

[iConta.eu](/)
