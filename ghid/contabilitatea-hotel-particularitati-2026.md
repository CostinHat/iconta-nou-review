---
title: "Contabilitatea unui hotel: particularități 2026"
description: "Cota redusă de TVA aplicabilă serviciilor de cazare și restaurant într-un hotel, conform art. 291 din Codul fiscal, și cazul separat al băuturilor alcoolice."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Contabilitatea unui hotel: particularități 2026

Cea mai frecventă particularitate contabilă a unui hotel nu ține de complexitatea operațională, ci de faptul că sub același acoperiș coexistă mai multe cote de TVA — cazarea, masa și băutura se tratează diferit, iar greșeala de încadrare apare exact la granița dintre ele.

## Temeiul legal

::: ghid-temei
„(2) Cota redusă de 11% se aplică asupra bazei de impozitare pentru următoarele prestări de servicii și/sau livrări de bunuri: [...]
m) cazarea în cadrul sectorului hotelier sau al sectoarelor cu funcție similară, inclusiv închirierea terenurilor amenajate pentru camping;
n) serviciile de restaurant și de catering, cu excepția băuturilor alcoolice, precum și a băuturilor nealcoolice care se încadrează la codul NC 2202."
— Legea 227/2015 (Codul fiscal), art. 291 alin. (2) lit. m), n) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce rezultă concret pentru evidența unui hotel:

- **Cazarea propriu-zisă** — camera de hotel, pensiunea, locul de camping — intră la cota redusă de 11% (lit. m), indiferent dacă e vândută separat sau ca parte a unui pachet.
- **Serviciile de restaurant și catering** din hotel (micul dejun, room service, restaurantul propriu) beneficiază și ele de 11% (lit. n) — **cu excepția băuturilor alcoolice**, care rămân integral la cota standard de 21%, și a băuturilor nealcoolice de la codul NC 2202 (în principal apă minerală/băuturi carbogazoase), care rămân de asemenea la cota standard.
- **Un pachet „cazare + mic dejun"** trebuie analizat pentru a stabili dacă e o prestație unică (cazare, la 11%) sau prestații distincte facturate separat — dacă micul dejun include băutură alcoolică (de exemplu, un pahar de vin inclus), acea componentă trebuie separată la 21%.
- **Minibar-ul din cameră** conține tipic atât produse la cotă redusă (apă plată, sucuri care nu se încadrează la NC 2202), cât și produse la cotă standard (băuturi alcoolice, unele băuturi carbogazoase) — nu se poate aplica o cotă unică pentru tot conținutul minibarului.

## Ce se greșește în practică

- Se aplică 11% pentru toată nota de plată a restaurantului hotelului, inclusiv băuturile alcoolice servite — legea exclude explicit alcoolul din categoria redusă, indiferent că e servit în contextul unei mese.
- Se tratează un pachet „all inclusive" ca o singură prestație la 11%, fără separarea componentelor de băuturi alcoolice care rămân la 21% — structura pachetului trebuie analizată pe componente, nu tratată automat ca prestație unică.
- Se aplică cota redusă și pentru servicii conexe care nu sunt cazare sau restaurant (de exemplu, servicii spa, închiriere săli de conferință) — acestea nu se regăsesc în lista de la art. 291 alin. (2) și rămân la cota standard.

## Ce face iConta.eu

Modulul de cote TVA din iConta.eu (`core/cote_tva.py`) are categorii dedicate pentru „cazare" (cazare hotelieră sau în sectoare cu funcție similară, inclusiv loc de camping) și „restaurant_catering", ambele la cota redusă de 11%, cu o categorie separată pentru băuturile alcoolice — care rămân la cota standard chiar și în context de restaurant/catering, conform excepției explicite din lege. Contabilul rămâne responsabil să descompună corect un pachet mixt (cazare + masă + băutură) pe componentele lui, atunci când firma nu emite facturi separate pentru fiecare element.

[iConta.eu](/)
