---
title: "TVA pentru produsele vândute prin marketplace"
description: "Regimul special de TVA aplicabil platformelor online care facilitează vânzarea de bunuri ale unor terți, potrivit Codului fiscal: când marketplace-ul devine el însuși furnizor din perspectiva TVA."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# TVA pentru produsele vândute prin marketplace

Când o firmă vinde propriile produse prin propriul magazin online, regulile de TVA sunt cele obișnuite. Situația se schimbă radical când vânzarea se face prin intermediul unei platforme (marketplace) care conectează vânzători terți cu clienți — legea tratează, în anumite condiții, platforma însăși ca fiind cea care livrează bunurile, din perspectiva TVA.

## Temeiul legal

::: ghid-temei
„În cazul în care o persoană impozabilă, prin utilizarea unei interfețe electronice cum ar fi o piață online, o platformă, un portal sau alte mijloace similare, facilitează vânzarea la distanță de bunuri importate din teritorii terțe sau țări terțe în loturi cu o valoare intrinsecă de maximum 150 euro, se consideră că această persoană impozabilă a primit și a livrat ea însăși bunurile respective. [...]
În cazul în care o persoană impozabilă, prin utilizarea unei interfețe electronice cum ar fi o piață online, o platformă, un portal sau alte mijloace similare, facilitează livrarea de bunuri în Uniunea Europeană de către o persoană impozabilă nestabilită în Uniunea Europeană către o persoană neimpozabilă, se consideră că persoana impozabilă care a facilitat livrarea a primit și a livrat ea însăși bunurile respective."
— Legea 227/2015, art. 270 alin. (15) și (16) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce rezultă, strict din text:

- Regula „e considerată furnizor" se aplică platformei (interfața electronică) în **două situații** clar delimitate: (1) facilitarea vânzării la distanță de bunuri importate din afara UE, în loturi de maximum 150 euro valoare intrinsecă; (2) facilitarea livrării de bunuri în UE de către un vânzător nestabilit în UE, către un client neimpozabil (persoană fizică, de regulă).
- În aceste cazuri, platforma „a primit și a livrat ea însăși bunurile" — juridic-fiscal, tranzacția se rupe în două livrări distincte, iar obligația de TVA aferentă vânzării către client trece la platformă, nu rămâne la vânzătorul terț.
- Platforma care facilitează astfel de vânzări are și obligația de a ține registre care să permită autorităților fiscale verificarea corectitudinii TVA-ului evidențiat.
- Situația unui vânzător stabilit în România care vinde prin propriul cont pe un marketplace, către clienți tot din România, nu se încadrează, potrivit textului citat, în niciuna dintre cele două ipoteze — acolo rămân aplicabile regulile obișnuite de TVA, iar textul nu confirmă un tratament special pentru acest caz.

## Ce se greșește în practică

- Se presupune că orice vânzare printr-un marketplace transferă automat obligația de TVA către platformă — regula se aplică strict celor două situații de mai sus (import sub 150 euro sau vânzător non-UE către persoană neimpozabilă din UE), nu oricărei tranzacții intermediate.
- Se ignoră obligația de a ține registre separate atunci când firma însăși operează o platformă care facilitează vânzări pentru vânzători terți — text aplicabil oricărei „persoane impozabile" care joacă rolul de interfață electronică.
- Se confundă vânzarea prin propriul magazin online (unde regulile obișnuite de TVA se aplică integral vânzătorului) cu vânzarea printr-un marketplace terț care intermediază pentru mai mulți vânzători — regimul special vizează exclusiv al doilea caz, și doar în condițiile descrise.

## Ce face iConta.eu

iConta.eu are un conector pentru importul comenzilor dintr-un magazin propriu WooCommerce (`core/woocommerce.py`), care transformă comenzile în facturi în aplicație. Acest conector vizează magazinul propriu al firmei, nu o platformă de tip marketplace care intermediază vânzări pentru mai mulți comercianți terți. La data acestui ghid, iConta.eu **nu implementează regimul special de TVA pentru interfețe electronice** de la art. 270 alin. (15)-(16) (recunoașterea platformei ca furnizor considerat) și art. 321^1 (ținerea registrelor speciale aferente) — pentru firmele care vând efectiv prin marketplace-uri terțe, încadrarea corectă a TVA-ului rămâne o analiză manuală.

[iConta.eu](/)
