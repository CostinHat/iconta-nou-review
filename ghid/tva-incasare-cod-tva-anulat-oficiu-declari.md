---
title: "TVA la încasare și cod TVA anulat din oficiu: când declari în D311 încasările ulterioare?"
description: "Până pe 25 a lunii următoare celei în care încasezi, pentru fiecare lună cu încasări din facturi emise înainte de anulare. Se declară doar încasările făcute cât timp nu ai cod valabil."
published: 2026-10-02
modified: 2026-10-02
poarta: v1
---

# TVA la încasare și cod TVA anulat din oficiu: când declari în D311 încasările ulterioare?

Pentru o factură emisă cât timp aplicai TVA la încasare și încasată după ce ți s-a anulat din oficiu codul de TVA, taxa devine exigibilă la încasare. Ea se declară în D311 până pe 25 inclusiv a lunii următoare celei în care ai încasat. Dacă încasezi o factură în trei tranșe, în trei luni diferite, depui trei declarații D311, fiecare pentru luna încasării. Termenul nu se raportează la data anulării și nici la data facturii.

Mai contează un detaliu: D311 acoperă doar încasările făcute în perioada în care nu ai cod valabil de TVA. Odată reînregistrată firma, încasările de după reînregistrare nu mai intră în această rubrică a D311.

## Temeiul legal

::: ghid-temei
„b) taxa colectată care trebuie plătită pentru livrări de bunuri/prestări de servicii efectuate înainte de anularea înregistrării în scopuri de TVA a persoanelor impozabile care au aplicat sistemul TVA la încasare, dar a căror exigibilitate de taxă potrivit art. 282 alin. (3)-(8) intervine în perioada în care persoana impozabilă nu are un cod valabil de TVA."
— Codul fiscal (Legea 227/2015), art. 324 alin. (10) lit. b) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„până la 25 inclusiv a lunii următoare celei în care a intervenit exigibilitatea taxei pentru livrări de bunuri/prestări de servicii, efectuate înainte de anularea înregistrării în scopuri de TVA, potrivit prevederilor art. 316 alin. (11) lit. a)-e) , g) sau h) din Codul fiscal , în situația în care exigibilitatea taxei pentru aceste operațiuni intervine, potrivit sistemului TVA la încasare, în perioada în care persoanele impozabile nu au cod valabil de TVA;"
— OPANAF 188/2018, anexa nr. 2 (termene de depunere) (sursă: anaf_surse/ordin_188_2018.html)
:::

Cum se aplică pas cu pas:

1. **Identifici facturile vizate.** Sunt facturile emise înainte de anulare, în sistemul TVA la încasare, rămase neîncasate total sau parțial la data anulării. Practic, soldul TVA neexigibilă rămas pe fiecare factură.
2. **Urmărești lunile cu încasări.** Exigibilitatea intervine la încasarea integrală sau parțială. Fiecare lună cu încasări din aceste facturi este o perioadă de raportare separată.
3. **Calculezi taxa pe suma încasată.** TVA exigibilă este partea de taxă cuprinsă în suma încasată. La cota de 21%, aceasta este 21/121 din încasare.
4. **Completezi D311.** La secțiunea III bifezi anularea din oficiu (pct. 2.1). Taxa se trece la secțiunea IV, litera B: livrări efectuate înaintea anulării, cu exigibilitatea intervenită, potrivit sistemului TVA la încasare, în perioada fără cod valabil. Perioada de raportare este anul și luna în care a intervenit exigibilitatea.
5. **Depui și plătești până pe 25 a lunii următoare.** Termenul de 25 decembrie devine 21 decembrie, potrivit Codului de procedură fiscală (Legea 207/2015), art. 155 alin. (2).

Ce nu intră aici:

- **Încasările după reînregistrare.** Art. 324 alin. (10) lit. b) vizează exigibilitatea care intervine „în perioada în care persoana impozabilă nu are un cod valabil de TVA". O încasare făcută după reînregistrarea conform art. 316 alin. (12) nu mai îndeplinește această condiție. Tratamentul ei fiscal ulterior trebuie analizat separat.
- **Operațiunile făcute după anulare.** Livrările efectuate efectiv după anulare se declară tot în D311, dar la litera A a secțiunii IV, pe alte reguli de exigibilitate.

::: ghid-exemplu
SC Exemplu SRL aplica TVA la încasare. Pe 10 mai 2026 emite o factură de 12.100 lei: 10.000 lei bază plus 2.100 lei TVA la 21%. Codul de TVA îi este anulat din oficiu, cu efect din 1 iulie 2026. Clientul plătește în două tranșe:

- **14 august 2026: 6.050 lei.** TVA exigibilă: 6.050 × 21/121 = 1.050 lei. Se declară în D311 pentru august 2026, până pe 25 septembrie 2026.
- **3 noiembrie 2026: 6.050 lei.** TVA exigibilă: 1.050 lei. Se declară în D311 pentru noiembrie 2026. Termenul de 25 decembrie se mută pe 21 decembrie 2026.

Total declarat prin D311: 1.050 + 1.050 = 2.100 lei, adică exact TVA de pe factură.

Dacă firma ar fi fost reînregistrată în scopuri de TVA în octombrie 2026, încasarea din noiembrie ar fi căzut într-o perioadă cu cod valabil și nu ar mai fi intrat la litera B din D311.
:::

## Ce se greșește în practică

- Se depune o singură D311 la data anulării, pentru tot soldul TVA neexigibilă, deși exigibilitatea apare doar la încasare, lună de lună.
- TVA se calculează la 21% din suma încasată, nu ca parte cuprinsă în ea, adică 21/121.
- Se uită de termenul special de 21 decembrie pentru încasările din noiembrie.
- După reînregistrare, încasările continuă să fie declarate în D311 din inerție.

## Ce face iConta.eu

iConta.eu urmărește TVA la încasare pe fiecare factură: la fiecare încasare totală sau parțială trece proporțional taxa din 4428 în 4427. Soldul TVA neexigibilă pe facturile rămase deschise este vizibil în evidență. D311 se întocmește în aplicație pe un formular manual. Contabilul alege motivul anulării și introduce baza și TVA pe situația „livrări cu TVA la încasare exigibilă după anulare", iar aplicația calculează subtotalurile și generează XML-ul validat pe validatorul ANAF. Depunerea se face din SPV.

[iConta.eu](/)
