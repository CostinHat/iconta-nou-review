---
title: "Cum tratez o factură de la Amazon UE în contabilitate?"
description: "Diferența dintre achiziția intracomunitară de bunuri și achiziția de servicii atunci când firma cumpără de la Amazon EU Sarl sau alt operator UE, cu regulile de TVA aplicabile."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum tratez o factură de la Amazon UE în contabilitate?

O factură emisă de Amazon (de regulă Amazon EU S.à r.l., cu sediul în Luxemburg, sau alt operator din alt stat membru) nu se tratează niciodată ca o factură internă. Regimul de TVA depinde de ce se cumpără — bunuri expediate dintr-un alt stat membru sau servicii (abonament, comisioane de vânzător, publicitate) — și de codul de TVA pe care firma l-a furnizat la achiziție.

## Temeiul legal

::: ghid-temei
„(1) Se consideră achiziție intracomunitară de bunuri obținerea dreptului de a dispune, ca și un proprietar, de bunuri mobile corporale expediate sau transportate la destinația indicată de cumpărător, de către furnizor, de către cumpărător sau de către altă persoană, în contul furnizorului sau al cumpărătorului, către un stat membru, altul decât cel de plecare a transportului sau de expediere a bunurilor."
— Legea nr. 227/2015 (Codul fiscal), art. 273 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Din citat rezultă mecanismul de bază:

- Dacă bunul e expediat dintr-un depozit Amazon aflat în alt stat membru (Germania, Polonia, Franța etc.) către România, iar firma cumpărătoare a comunicat vânzătorului codul său valabil de TVA din România, operațiunea este **achiziție intracomunitară de bunuri (AIC)** — se autofactureză, TVA se calculează prin taxare inversă (colectată și dedusă simultan) și se raportează atât în decontul de TVA, cât și în declarația recapitulativă D390.
- Dacă pe factură apare TVA local (de exemplu TVA din Luxemburg sau din țara de expediere), înseamnă că furnizorul nu a tratat operațiunea ca AIC — de regulă pentru că firma cumpărătoare nu era înregistrată în scopuri de TVA la data comenzii sau achiziția e sub pragul de la distanță. În acest caz TVA-ul străin nu e deductibil în România și, de regulă, nu poate fi recuperat decât printr-o cerere de rambursare TVA din alt stat membru.
- Dacă factura e pentru servicii (abonament Amazon, comision de marketplace, publicitate sponsorizată), se aplică regulile de la art. 278 privind locul prestării B2B — de regulă taxare inversă, cu autofactură, similar AIC-ului.

## Ce se greșește în practică

- Se înregistrează factura Amazon ca o cheltuială simplă, fără autofactură și fără raportare în D390, pentru că „e doar un abonament sau o comandă mică".
- Se deduce TVA-ul afișat pe factură ca și cum ar fi TVA românesc, deși e TVA străin, nedeductibil în decontul intern.
- Nu se verifică dacă vânzătorul care apare pe factură este Amazon EU S.à r.l. (Luxemburg) sau o altă entitate din grup — codul de TVA al furnizorului diferă și determină statul de origine al achiziției intracomunitare.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu are un conector dedicat pentru Amazon**. Aplicația oferă un modul general pentru achiziții intracomunitare (`core/intracomunitar.py`), cu funcții de validare VIES a codului de TVA al furnizorului și de calcul al taxării inverse (`tva_taxare_inversa`, `note_taxare_inversa`), pe care contabilul le poate folosi pentru a înregistra manual o factură Amazon ca AIC. Singurul conector automat de import comenzi din prezent este cel pentru WooCommerce (`core/woocommerce.py`), relevant pentru magazine online proprii, nu pentru achiziții de la Amazon. Introducerea și clasificarea corectă a facturii Amazon — AIC, achiziție de servicii sau achiziție cu TVA străin nedeductibil — rămân o decizie manuală a contabilului.

[iConta.eu](/)
