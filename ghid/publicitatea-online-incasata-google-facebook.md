---
title: "Publicitatea online încasată de la Google/Facebook: TVA"
description: "Tratamentul TVA pentru serviciile de publicitate online cumpărate de la Google sau Meta: locul prestării, taxarea inversă și obligațiile declarative."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Publicitatea online încasată de la Google/Facebook: TVA

Când o firmă din România cumpără publicitate online de la Google (Google Ireland Limited) sau Meta (Facebook), operațiunea e o achiziție de servicii de la un prestator stabilit în alt stat membru sau într-un stat terț. Regula generală pentru serviciile B2B mută locul prestării la sediul beneficiarului, iar TVA-ul se datorează prin taxare inversă — nu se plătește TVA către Google sau Facebook, ci se autolichidează de firma din România.

## Temeiul legal

::: ghid-temei
„(2) Locul de prestare a serviciilor către o persoană impozabilă care acționează ca atare este locul unde respectiva persoană care primește serviciile își are stabilit sediul activității sale economice. [...]"
— Legea 227/2015, art. 278 alin. (2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„(2) Taxa este datorată de orice persoană impozabilă, inclusiv de către persoana juridică neimpozabilă înregistrată în scopuri de TVA conform art. 316 sau 317, care este beneficiar al serviciilor care au locul prestării în România conform art. 278 alin. (2) și care sunt furnizate de către o persoană impozabilă care nu este stabilită pe teritoriul României [...]"
— Legea 227/2015, art. 307 alin. (2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce rezultă practic pentru factura de la Google/Facebook:

- **Locul prestării e România** (locul unde e stabilit beneficiarul, firma românească), potrivit regulii generale B2B de la art. 278 alin. (2) — indiferent că Google Ireland sau Meta emit factura fără TVA.
- **TVA-ul se autolichidează prin taxare inversă**: firma din România înregistrează atât TVA colectată, cât și TVA deductibilă pentru aceeași sumă (operațiune neutră pentru firmele cu drept integral de deducere), potrivit art. 307 alin. (2).
- **Condiția de aplicare**: firma trebuie să fie înregistrată în scopuri de TVA (fie normal, conform art. 316, fie special pentru achiziții intracomunitare de servicii, conform art. 317) — fără cod valid de TVA, prestatorul extern ar trebui, teoretic, să factureze cu TVA-ul din statul lui, ceea ce Google/Meta evită tocmai verificând codul de TVA la înregistrarea contului publicitar.
- **Obligația declarativă**: operațiunea se raportează în decontul de TVA (D300), la rândurile de achiziții de servicii intracomunitare/taxare inversă, și, dacă firma nu e înregistrată normal în scopuri de TVA, prin declarația specială D301.

## Ce se greșește în practică

- Se așteaptă o factură cu TVA românesc de la Google/Facebook, deși aceștia facturează fără TVA tocmai pentru că regula B2B mută obligația de plată la beneficiar.
- Se înregistrează cheltuiala de publicitate fără taxare inversă, considerând-o o simplă achiziție externă fără TVA, ceea ce omite atât obligația de a colecta, cât și dreptul de a deduce TVA-ul aferent.
- Se ignoră faptul că, pentru firmele neînregistrate normal în scopuri de TVA (de exemplu microîntreprinderi sub plafon), achiziția de servicii de la un prestator extern declanșează totuși obligația de înregistrare specială și de aplicare a taxării inverse, potrivit art. 317.

## Ce face iConta.eu

iConta.eu gestionează operațiunile de taxare inversă și achizițiile intracomunitare de servicii prin modulul de TVA (`core/d301.py` — pentru persoanele neînregistrate normal în scopuri de TVA, care fac achiziții intracomunitare sau operațiuni cu taxare inversă) și prin cotele de TVA aplicate facturilor (`core/cote_tva.py`). La data acestui ghid, aplicația **nu are o regulă automată de recunoaștere a furnizorilor Google/Meta** pentru a aplica direct taxarea inversă la introducerea facturii — încadrarea corectă a achiziției de publicitate online ca operațiune cu taxare inversă se face manual, la introducerea documentului.

[iConta.eu](/)
