---
title: "Am tratat greșit tichetele de masă"
description: Cea mai frecventă greșeală la tichetele de masă e calcularea impozitului de 10% pe valoarea nominală brută, în loc de baza rămasă după scăderea CASS — o diferență de formulă, nu de rotunjire, care umflă reținerea reală.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Am tratat greșit tichetele de masă

Cele mai frecvente erori la tichetele de masă nu țin de plafonul legal, ci de ordinea calculului fiscal și de zilele luate în calcul la numărul de tichete acordate. Ambele pot fi verificate și corectate pornind de la formula și regulile de mai jos.

## Temeiul legal

::: ghid-temei
Codul fiscal, art. 78 alin. (2) lit. a): „prin aplicarea cotei de 10% asupra bazei de calcul determinată ca diferență între venitul net din salarii calculat prin deducerea din venitul brut a contribuțiilor sociale obligatorii aferente unei luni, datorate potrivit legii ... și [deducerea personală, cotizația sindicală etc.]"
:::

Aplicată pe tichetele de masă, formula corectă e: CASS 10% pe valoarea nominală integrală, apoi **impozitul 10% pe baza rămasă după scăderea acestei CASS** — nu pe valoarea nominală brută. Pentru un tichet de 945 lei nominal (de exemplu 21 tichete × 45 lei, plafonul 2026):

```
nominal        = 945,00 lei
CASS (10%)     = 945,00 × 0,10 = 94,50 lei
baza impozit   = 945,00 − 94,50 = 850,50 lei   (NU 945,00)
impozit (10%)  = 850,50 × 0,10 = 85,05 lei     (NU 94,50)
reținere totală = 94,50 + 85,05 = 179,55 lei   (≈ 19,0%, NU 20%)
net efectiv     = 945,00 − 179,55 = 765,45 lei (NU 756 lei)
```

O a doua sursă frecventă de eroare ține de zilele care dau drept la tichet: acesta se acordă doar pentru zilele **efectiv lucrate** (HG 1045/2018, art. 10 alin. (1)) — concediul de odihnă, delegația/detașarea, absențele și învoirile nu dau drept la tichet, iar concediul medical se scade separat, din evidența de concedii medicale. Zilele de telemuncă, în schimb, **dau** drept la tichet de masă — nu există nicio excludere legală pentru ele, fiind zile efectiv lucrate.

## Ce se greșește în practică

- Se calculează impozitul de 10% pe valoarea nominală brută a tichetului, în loc de baza rămasă după scăderea CASS — eroarea umflă reținerea totală de la ≈19% la 20%.
- Se exclude, din greșeală, telemunca de la zilele care dau drept la tichet de masă — regula de excludere explicită din HG 1045/2018 vizează doar concediul de odihnă, delegația/detașarea, absențele și învoirea, nu telemunca.
- Se confundă regula de excludere a telemuncii din calculul indemnizației de hrană în bani (Codul fiscal, art. 76 alin. (4^1) lit. b) — aplicabilă doar celor fără tichete de masă) cu regula tichetelor de masă, unde telemunca nu e exclusă.

## Ce face iConta.eu

Motorul de salarizare (`core/salarizare.py`) aplică automat formula corectă — CASS 10% pe nominal, apoi impozit 10% pe baza rămasă după CASS — fără să lase loc calculului manual pe nominalul brut. Numărul de tichete se calculează din pontajul lunii, confirmat obligatoriu înainte de generarea D112 pe tichete de masă, scăzând explicit doar zilele de concediu de odihnă, delegație/detașare, absențe și învoire; telemunca nu apare în lista de excludere, deci generează tichet normal. Dacă o lună a fost deja procesată cu o formulă greșită (de exemplu preluată manual dintr-un exemplu numeric incorect), corectarea presupune refacerea calculului acelei luni în statul de plată, cu formula de mai sus — F133 nu oferă un instrument separat de „corectare retroactivă" dincolo de recalcularea lunii respective.

[iConta.eu](/)
