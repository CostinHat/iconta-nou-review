---
title: "TVA la încasare: care este data încasării la plata cu cec, bilet la ordin sau card bancar?"
description: "Pentru cec, cambie sau bilet la ordin: data din extrasul de cont dacă îl încasezi sau scontezi, data girului dacă îl girezi. La card: data din extrasul de cont."
published: 2026-09-29
modified: 2026-09-29
poarta: v1
---

# TVA la încasare: care este data încasării la plata cu cec, bilet la ordin sau card bancar?

Pentru firma care aplică sistemul TVA la încasare, data încasării stabilește luna în care TVA devine exigibilă. Normele fixează această dată pentru fiecare instrument de plată:

- **cec, cambie, bilet la ordin**: data din **extrasul de cont**, dacă furnizorul încasează sau scontează instrumentul; **data girului**, dacă furnizorul îl girează altei persoane;
- **card de debit sau de credit**: data din **extrasul de cont** (sau din documentul asimilat), nu data tranzacției la POS;
- **transfer bancar**: data din extrasul de cont.

Data la care primești biletul la ordin nu este data încasării. Dacă îl ții în portofoliu până la scadență, TVA devine exigibilă abia la încasarea prin bancă. Dacă îl girezi imediat unui furnizor, devine exigibilă la data girului.

## Temeiul legal

::: ghid-temei
„(10) În cazul încasărilor prin bancă de tipul transfer-credit, data încasării contravalorii totale/parțiale a livrării de bunuri/prestării de servicii de către persoana care aplică sistemul TVA la încasare este data înscrisă în extrasul de cont sau în alt document asimilat acestuia. (11) În cazul în care încasarea se efectuează prin instrumente de plată de tip transfer-debit, respectiv cec, cambie și bilet la ordin, data încasării contravalorii totale/parțiale a livrării de bunuri/prestării de servicii de către persoana care aplică sistemul TVA la încasare este: a) data înscrisă în extrasul de cont sau în alt document asimilat acestuia, în situația în care furnizorul/prestatorul care aplică sistemul TVA la încasare nu girează instrumentul de plată, ci îl încasează/scontează. În cazul scontării instrumentului de plată, se consideră că persoana respectivă a încasat contravaloarea integrală a instrumentului de plată; [...] b) data girului, în situația în care furnizorul/prestatorul care aplică sistemul TVA la încasare girează instrumentul de plată altei persoane. În acest scop se păstrează o copie de pe instrumentul de plată care a fost girat, în care se află mențiunea cu privire la persoana către care a fost girat instrumentul de plată. [...] (12) Data încasării în situația în care plata s-a efectuat prin carduri de debit sau de credit de către cumpărător este data înscrisă în extrasul de cont ori în alt document asimilat acestuia."
— Normele metodologice de aplicare a Codului fiscal (HG 1/2016), Titlul VII, pct. 26 alin. (10)-(12) (norme art. 282 CF) (sursă: [HG nr. 1/2016 (Normele metodologice ale Codului fiscal)](https://legislatie.just.ro/Public/DetaliiDocument/174822))
:::

::: ghid-temei
„exigibilitatea taxei intervine la data încasării contravalorii integrale sau parțiale a livrării de bunuri ori a prestării de servicii, în cazul persoanelor impozabile care optează în acest sens, denumite în continuare persoane care aplică sistemul TVA la încasare."
— Codul fiscal (Legea 227/2015), art. 282 alin. (3) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))
:::

Ce înseamnă concret:

- **Scontare**: la scontarea biletului la ordin la bancă, se consideră încasată **integral** contravaloarea instrumentului, chiar dacă banca reține un scont. TVA exigibilă se calculează pe valoarea integrală.
- **Gir**: data girului devine data încasării. Păstrează copia instrumentului girat, cu mențiunea persoanei către care a fost girat. Fără ea, data girului nu se poate dovedi.
- **Card**: plata cu cardul făcută de client pe 30 septembrie și decontată de bancă pe 2 octombrie are data încasării 2 octombrie, data din extras.

::: ghid-exemplu
SC Exemplu SRL, în sistemul TVA la încasare, emite pe 1 octombrie o factură de 12.100 lei (10.000 lei + TVA 2.100 lei), cu TVA înregistrată în 4428. Pe 5 octombrie primește de la client un bilet la ordin de 12.100 lei, scadent pe 5 decembrie.
- Dacă îl girează pe 12 octombrie unui furnizor: data încasării este **12 octombrie**, iar TVA de 2.100 lei trece din 4428 în 4427 în octombrie.
- Dacă îl păstrează și îl încasează la scadență, cu banii în cont pe 6 decembrie: TVA devine exigibilă în **decembrie**.
- Dacă îl scontează pe 20 octombrie și primește 11.900 lei: se consideră încasați integral 12.100 lei, iar TVA de 2.100 lei devine exigibilă în octombrie.
:::

## Ce se greșește în practică

- Data primirii biletului la ordin sau a cecului este tratată ca dată a încasării.
- La gir nu se păstrează copia instrumentului girat, deci lipsește dovada datei girului.
- La scontare, TVA exigibilă se calculează doar pe suma netă primită de la bancă, nu pe valoarea integrală.
- La card se folosește data bonului de la POS în locul datei din extrasul de cont.

## Ce face iConta.eu

iConta.eu are modulul TVA la încasare. Factura se emite cu TVA neexigibilă (4428), iar la fiecare încasare aloci suma pe factură și aplicația calculează TVA exigibilă prin suta mărită, cu transferul 4428 = 4427, verificând și plafonul de eligibilitate. Data încasării folosită este cea înregistrată de contabil. Alegerea ei (extras, gir sau scontare) după regulile de mai sus rămâne decizia contabilului.

[iConta.eu](/)
