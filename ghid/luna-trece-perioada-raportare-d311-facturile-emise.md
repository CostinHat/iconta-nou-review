---
title: "Ce lună se trece ca perioadă de raportare în D311 la facturile emise după reînregistrare?"
description: "Se trece anul și luna în care a intervenit exigibilitatea taxei care trebuia colectată în perioada fără cod de TVA, nu luna în care emiți factura după reînregistrare."
published: 2026-10-02
modified: 2026-10-02
poarta: v1
---

# Ce lună se trece ca perioadă de raportare în D311 la facturile emise după reînregistrare?

La facturile emise după reînregistrare pentru perioada în care codul de TVA a fost anulat, perioada de raportare din D311 este **luna în care a intervenit exigibilitatea taxei** care trebuia colectată atunci. Nu se trece luna emiterii facturii și nici luna reînregistrării.

Regula decide câte declarații depui și de la ce dată curg accesoriile. Dacă vânzările din perioada fără cod sunt împrăștiate pe mai multe luni, completezi câte un D311 pentru fiecare lună de exigibilitate, chiar dacă toate facturile se emit în aceeași zi.

## Temeiul legal

::: ghid-temei
„Perioada de raportare - se completează cu anul și luna în care a intervenit exigibilitatea taxei pe valoarea adăugată pentru livrările de bunuri/prestările de servicii și/sau achizițiile de bunuri și/sau servicii pentru care persoana impozabilă este obligată la plata taxei. În situațiile prevăzute la pct. 5^1 alin. (2) lit. c) și d) din titlul I al Normelor metodologice se completează cu anul și luna în care a intervenit exigibilitatea taxei pe care persoana impozabilă ar fi trebuit să o colecteze în perioada în care a avut codul de înregistrare în scopuri de TVA anulat."
— OPANAF nr. 188/2018, anexa nr. 2, „Perioada de raportare" (sursă: [OPANAF nr. 188/2018 pentru aprobarea formularului 311](https://legislatie.just.ro/Public/DetaliiDocument/197537))
:::

::: ghid-temei
„(1) Exigibilitatea taxei intervine la data la care are loc faptul generator. (2) Prin excepție de la prevederile alin. (1) , exigibilitatea taxei intervine: a) la data emiterii unei facturi, înainte de data la care intervine faptul generator; ... b) la data la care se încasează avansul, pentru plățile în avans efectuate înainte de data la care intervine faptul generator."
— Codul fiscal (Legea 227/2015), art. 282 alin. (1)-(2) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))
:::

Cum stabilești luna:

- **Regula generală:** exigibilitatea intervine la data faptului generator, adică la data livrării bunurilor sau a prestării serviciilor (art. 281 alin. (1) și art. 282 alin. (1) din Codul fiscal).
- **Factură emisă înainte de livrare:** dacă în perioada fără cod s-a emis o factură înainte de livrare, exigibilitatea intervine la data facturii (art. 282 alin. (2) lit. a)).
- **Avans:** dacă s-a încasat un avans înainte de livrare, exigibilitatea intervine la data încasării avansului (art. 282 alin. (2) lit. b)).
- **Situațiile vizate:** facturile de corecție emise după reînregistrare pentru operațiuni deja facturate (pct. 5^1 alin. (2) lit. c) din normele aprobate prin HG 1/2016) și facturile emise pentru prima dată, pentru operațiuni nefacturate (lit. d)).
- **O declarație pe perioadă:** formularul are o singură rubrică de perioadă (lună și an), iar la rectificare instrucțiunile cer câte o declarație rectificativă pentru fiecare perioadă de raportare.

Data emiterii facturii de după reînregistrare nu schimbă luna de exigibilitate. Factura din septembrie pentru o livrare din aprilie se raportează pe aprilie.

::: ghid-temei
„Persoana impozabilă datorează obligații fiscale accesorii conform art. 173 și 181 din Legea nr. 207/2015, cu modificările și completările ulterioare, de la data la care avea obligația să plătească TVA aferentă livrărilor de bunuri/prestărilor de servicii taxabile, efectuate în perioada în care a avut codul de înregistrare în scopuri de TVA anulat, și până la data plății taxei"
— HG 1/2016 (Normele metodologice ale Codului fiscal), titlul I, pct. 5^1 alin. (2) lit. d) (sursă: [HG nr. 1/2016 (Normele metodologice ale Codului fiscal)](https://legislatie.just.ro/Public/DetaliiDocument/174822))
:::

Luna de raportare corectă fixează și începutul calculului de accesorii, potrivit Codului de procedură fiscală (Legea 207/2015).

::: ghid-exemplu
SC Exemplu SRL a avut codul anulat din oficiu între 1 februarie și 31 iulie 2026. În septembrie 2026, după reînregistrare, emite trei documente:

- factură de corecție pentru o factură fără TVA emisă pe 12 martie 2026, livrarea fiind făcută tot pe 12 martie: perioada de raportare este **martie 2026**;
- factură pentru o prestare din 20 mai 2026, nefacturată: perioada de raportare este **mai 2026**;
- factură pentru o livrare din 3 iulie 2026, pentru care se încasase un avans de 5.000 lei pe 28 iunie 2026: pentru avans, perioada este **iunie 2026**; pentru diferență, **iulie 2026**.

Rezultă patru perioade de raportare, deci patru declarații D311, deși toate documentele s-au emis în septembrie.
:::

## Ce se greșește în practică

- Se trece în D311 luna emiterii facturii de după reînregistrare, adică septembrie în exemplul de mai sus.
- Toate operațiunile din perioada fără cod se cumulează într-o singură declarație.
- Avansurile încasate în perioada fără cod se ignoră și se raportează doar livrarea finală.
- Accesoriile se calculează de la data emiterii facturii, nu de la scadența taxei pentru luna de exigibilitate.

## Ce face iConta.eu

În iConta.eu, la D311 contabilul alege luna de raportare înainte de a completa formularul. D311 din aplicație acoperă însă doar situația de după anularea codului (secțiunea IV). Secțiunea V, folosită la facturile emise după reînregistrare, nu e încă disponibilă, așa că aceste declarații se întocmesc în afara aplicației. Stabilirea lunii de exigibilitate pentru fiecare operațiune și calculul accesoriilor rămân în sarcina contabilului.

[iConta.eu](/)
