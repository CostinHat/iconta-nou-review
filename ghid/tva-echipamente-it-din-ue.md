---
title: TVA la achiziția de echipamente IT din UE
description: Laptopurile, monitoarele sau serverele cumpărate de la un furnizor din alt stat membru UE sunt achiziție intracomunitară de bunuri (art. 268 alin. (3) lit. a) Cod fiscal), cu TVA autoimpusă prin 4426 = 4427, nu prin plată la furnizor.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se tratează TVA la cumpărarea de echipamente IT dintr-un alt stat membru UE?

Un laptop comandat de la un magazin online din Germania sau un lot de monitoare de la un distribuitor din Olanda ajung, fiscal, pe același traseu ca orice altă marfă cumpărată din UE: e o achiziție intracomunitară de bunuri, iar TVA nu vine pe factura furnizorului, ci se autoimpune la cumpărător. Greșeala frecventă e tratarea acestor achiziții ca „import fără TVA" sau, la polul opus, așteptarea unei facturi cu TVA românesc de la furnizorul extern, care nu va veni.

## Temeiul legal

::: ghid-temei
**Art. 268 alin. (3) lit. a) Cod fiscal** — echipamentele IT sunt bunuri, deci intră direct sub definiția AIC: *„Sunt, de asemenea, operațiuni impozabile și următoarele operațiuni efectuate cu plată, pentru care locul este considerat a fi în România, potrivit art. 276: a) o achiziție intracomunitară de bunuri, altele decât mijloace de transport noi sau produse accizabile, efectuată de o persoană impozabilă ce acționează ca atare sau de o persoană juridică neimpozabilă, care nu beneficiază de excepția prevăzută la alin. (4)..."*

**Art. 308 alin. (1) Cod fiscal** — obligația de plată trece la cumpărător: *„Persoana care efectuează o achiziție intracomunitară de bunuri care este taxabilă, conform prezentului titlu, este obligată la plata taxei."*

**Norme HG 1/2016, pct. 109 alin. (1)** — formula contabilă: *„Din punct de vedere contabil, beneficiarul înregistrează în cursul perioadei fiscale în care taxa este exigibilă suma taxei aferente în următoarea formulă contabilă: 4426 = 4427. Prevederile acestui alineat sunt valabile pentru orice alte situații în care se aplică taxarea inversă."*
:::

## Conturi și formulă

Recepția echipamentelor se înregistrează la valoarea din factura furnizorului UE (convertită în lei), fără TVA:

`303/214 = 401` — funcție de destinație: `303` (materiale de natura obiectelor de inventar) sau direct cheltuială, dacă valoarea nu justifică imobilizare; `214` dacă echipamentul se capitalizează ca mijloc fix (vezi și ghidul despre mijloace fixe din UE, pentru pragul de capitalizare).

TVA se autoimpune separat: `4426 = 4427`, cu `TVA = bază × cotă / 100`, rotunjit aritmetic la 2 zecimale.

Condiția ca operațiunea să fie tratată ca AIC e ca furnizorul să aibă un cod de TVA valabil dintr-un stat membru UE — nu contează dacă marfa vine dintr-un depozit local al unui retailer mare sau direct din țara de origine, ci unde e înregistrat furnizorul în scop de TVA.

## Un exemplu

::: ghid-exemplu
O firmă cumpără 10 laptopuri de la un furnizor din Olanda, factură totală **22.000 lei**, cotă TVA **21%**.

- **Recepție**: `303 = 401` cu **22.000 lei**
- **TVA autoimpusă**: `4426 = 4427` cu 22.000 × 21 / 100 = **4.620 lei**

Firma nu plătește TVA olandez și nu plătește TVA suplimentar furnizorului — cei 22.000 lei ajung integral la el. Cei 4.620 lei de TVA sunt simultan deductibili și colectați în decontul lunii.
:::

## Ce se greșește în practică

- **Se confundă cu importul.** Import înseamnă bunuri dintr-o țară din afara UE, cu TVA plătit sau garantat în vamă; achiziția dintr-un alt stat membru UE e AIC, cu taxare inversă, mecanism complet diferit.
- **Se așteaptă factură cu TVA românesc de la furnizorul extern.** Furnizorul facturează fără TVA pe baza codului tău de TVA valabil; taxa se calculează la tine.
- **Se ignoră TVA complet**, tratând achiziția ca „scutită", pentru că pe factură nu apare nicio sumă de TVA — de fapt taxa există, doar că se autoimpune, nu se plătește furnizorului.

## Ce face iConta.eu

Codul de TVA al furnizorului e analizat automat — prefixul de țară (cu mapare specială pentru Grecia, `GR → EL`) e verificat contra listei celor 27 de state membre UE plus `XI` (Irlanda de Nord); operațiunea e tratată ca intracomunitară doar dacă țara codului nu e România. TVA la taxare inversă se calculează cu `TVA = bază × cotă / 100`, rotunjit aritmetic la 2 zecimale, iar cota trebuie transmisă explicit — nu are valoare implicită înghețată în cod.

[iConta.eu](/)
