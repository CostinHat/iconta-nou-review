---
title: "Ce venituri sunt neimpozabile la calculul impozitului pe profit?"
description: "Lista veniturilor pe care Codul fiscal le scoate din baza de calcul a impozitului pe profit, conform art. 23 din Legea 227/2015."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce venituri sunt neimpozabile la calculul impozitului pe profit?

Nu toate veniturile înregistrate contabil intră în baza de calcul a impozitului pe profit. Codul fiscal listează explicit, la art. 23, veniturile care se scad din rezultatul contabil pentru a ajunge la rezultatul fiscal — o listă închisă, nu un principiu general de interpretare.

## Temeiul legal

::: ghid-temei
„Articolul 23 Venituri neimpozabile
La calculul rezultatului fiscal, următoarele venituri sunt neimpozabile:
a) dividendele primite de la o persoană juridică română;
b) dividende primite de la o persoană juridică străină plătitoare de impozit pe profit sau a unui impozit similar impozitului pe profit, situată într-un stat terț, [...] dacă persoana juridică română care primește dividendele deține la persoana juridică străină [...] pe o perioadă neîntreruptă de un an, minimum 10% din capitalul social [...];
d) veniturile din anularea, recuperarea, inclusiv refacturarea cheltuielilor pentru care nu s-a acordat deducere, veniturile din reducerea sau anularea provizioanelor pentru care nu s-a acordat deducere, veniturile din restituirea ori anularea unor dobânzi și/sau penalități pentru care nu s-a acordat deducere [...];
i) veniturile din evaluarea/reevaluarea/vânzarea/cesionarea titlurilor de participare deținute la o persoană juridică română sau la o persoană juridică străină situată într-un stat cu care România are încheiată o convenție de evitare a dublei impuneri, dacă [...] contribuabilul deține pe o perioadă neîntreruptă de un an minimum 10% din capitalul social [...]"
— Legea 227/2015 (Codul fiscal), art. 23 lit. a), b), d), i) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Lista completă a art. 23 cuprinde 18 litere (a-s, litera q lipsind din numerotare). Cele mai întâlnite în practica firmelor mici și mijlocii sunt:

- **Dividendele primite de la o persoană juridică română** (lit. a) — nu se mai impozitează o dată încasate la firma-mamă, pentru că au fost deja impozitate la firma care le-a distribuit.
- **Veniturile din anularea provizioanelor/cheltuielilor nedeductibile** (lit. d) — dacă o cheltuială sau un provizion nu a fost dedus fiscal la constituire, anularea lui ulterioară nu poate fi impozabilă a doua oară — ar însemna dublă impunere pe aceeași sumă.
- **Veniturile din titluri de participare** deținute pe termen lung (peste 1 an, minimum 10% din capital), la lit. i) și j) — regim de participare, gândit să nu descurajeze structurile de grup.
- **Veniturile prevăzute expres ca neimpozabile în acorduri/memorandumuri aprobate prin acte normative** (lit. h) — o categorie reziduală, dar tot cu condiție: actul normativ trebuie să o declare explicit.

Important: lista e limitativă. Un venit care „pare" să nu ar trebui impozitat, dar nu se regăsește la niciuna dintre literele art. 23, rămâne impozabil.

## Ce se greșește în practică

- Se presupune că orice venit „fără flux de numerar" (reversare de provizion, anulare de datorie) e automat neimpozabil — de fapt depinde dacă suma corespunzătoare a fost dedusă fiscal la constituire (art. 23 lit. d) cere explicit „pentru care nu s-a acordat deducere").
- Se tratează dividendele primite de la o persoană juridică străină ca neimpozabile necondiționat, ignorând condiția de deținere de minimum 10% pe o perioadă neîntreruptă de un an (lit. b).
- Se confundă venitul neimpozabil (scăzut din baza de calcul a impozitului pe profit) cu venitul scutit de TVA sau cu venitul neimpozabil la impozitul pe venit al persoanelor fizice — sunt regimuri fiscale diferite, cu liste diferite.

## Ce face iConta.eu

Modulul de calcul al Declarației 101 din iConta.eu tratează distinct secțiunea „Venituri neimpozabile" (rândurile 17-21 din formular), separată de veniturile impozabile din rezultatul contabil — vezi `core/d101.py`. Contabilul introduce sumele pe categoriile relevante din contabilitate, iar aplicația le scade din baza de calcul conform structurii oficiale a formularului; verificarea încadrării unui venit concret la litera corespunzătoare din art. 23 (de exemplu, condiția de deținere de 10%/1 an pentru dividende) rămâne responsabilitatea profesională a contabilului, conform regulii de lucru a aplicației privind datele introduse de utilizator.

[iConta.eu](/)
