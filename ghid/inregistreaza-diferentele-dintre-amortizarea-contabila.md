---
title: "Cum se înregistrează diferențele dintre amortizarea contabilă și cea fiscală?"
description: "Regula din Codul fiscal potrivit căreia amortizarea fiscală se determină independent de amortizarea contabilă, cu impact direct asupra calculului impozitului pe profit."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se înregistrează diferențele dintre amortizarea contabilă și cea fiscală?

Amortizarea contabilă (cea din bilanț, calculată după politica contabilă a firmei) și amortizarea fiscală (cea recunoscută la calculul impozitului pe profit) nu sunt același lucru — legea le separă explicit, nu doar ca practică, ci ca regulă de drept.

## Temeiul legal

::: ghid-temei
„(17) Pentru mijloacele fixe amortizabile, deducerile de amortizare se determină fără a lua în calcul amortizarea contabilă. Câștigurile sau pierderile rezultate din vânzarea ori din scoaterea din funcțiune a acestor mijloace fixe se calculează pe baza valorii fiscale a acestora, diminuată cu amortizarea fiscală, cu excepția celor prevăzute la alin. (14)."
— Legea 227/2015 (Codul fiscal), art. 28 alin. (17) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce rezultă de aici pentru evidența practică:

- **Amortizarea contabilă** urmează politica contabilă a firmei (metodă, durată de utilizare economică estimată), stabilită potrivit reglementărilor contabile aplicabile (OMFP 1802/2014, pentru firmele care le aplică).
- **Amortizarea fiscală** urmează exclusiv regulile art. 28 din Codul fiscal — metodă (liniară, degresivă sau accelerată, după caz), durată normală de funcționare din Catalogul aprobat prin HG (HG 2139/2004), fără legătură cu politica contabilă a firmei.
- Când cele două durate sau metode diferă, apare o **diferență temporară** între rezultatul contabil și rezultatul fiscal: în anii în care amortizarea fiscală e mai mare decât cea contabilă, profitul impozabil e mai mic decât profitul contabil (și invers, în anii următori, când amortizarea fiscală se epuizează mai devreme).
- La vânzarea sau scoaterea din funcțiune a mijlocului fix, câștigul/pierderea fiscală **nu se calculează pe baza valorii contabile rămase**, ci pe baza valorii fiscale rămase (cost de achiziție minus amortizarea fiscală cumulată) — o a doua sursă de diferență, în afara amortizării curente.
- Practic, diferența se „înregistrează" nu printr-o notă contabilă separată de amortizare, ci prin elementul similar veniturilor/cheltuielilor din calculul impozitului pe profit (rândurile de reconciliere fiscal-contabilă din Declarația 101), reflectând suma cu care rezultatul fiscal diferă de cel contabil în anul respectiv.

## Ce se greșește în practică

- Se folosește aceeași durată și metodă de amortizare atât pentru contabilitate, cât și pentru calculul fiscal, fără să se verifice dacă durata contabilă aleasă se încadrează în intervalul minim-maxim din Catalogul HG 2139/2004 — dacă nu se încadrează, amortizarea fiscală trebuie recalculată separat, chiar dacă în contabilitate a fost înregistrată altfel.
- La vânzarea unui mijloc fix, se calculează profitul/pierderea din vânzare pe baza valorii contabile nete, ignorând valoarea fiscală rămasă — care poate fi diferită dacă amortizările au avut ritmuri diferite.
- Se presupune că diferența dintre cele două amortizări „se anulează" automat la sfârșitul duratei de amortizare — corect doar dacă totalul amortizat pe fiecare traseu e identic (aceeași bază amortizabilă); dacă bazele diferă (de exemplu din cauza unei reevaluări contabile care nu se recunoaște fiscal), diferența rămâne definitivă, nu doar temporară.

## Ce face iConta.eu

Modulul de mijloace fixe din iConta.eu (`core/repo_mijloace_fixe.py`) ține o singură schemă de amortizare per mijloc fix (valoare, valoare reziduală, durată normală de funcționare în luni), folosită pentru amortizarea contabilă înregistrată în evidență. La data acestui ghid, aplicația **nu calculează și nu urmărește separat o amortizare fiscală distinctă** de cea contabilă și nu automatizează reconcilierea impozitului amânat rezultat din diferențele temporare — nu există, în cod, o funcție dedicată „amortizare_fiscala" sau tratamentul impozitului pe profit amânat. Contabilul rămâne responsabil să verifice, pentru fiecare mijloc fix, dacă durata și metoda contabilă coincid cu cele admise fiscal și, dacă nu, să calculeze manual diferența pentru declarația de impozit pe profit.

[iConta.eu](/)
