---
title: Cum corectez amortizarea calculată greșit
description: O amortizare greșită vine aproape mereu din trei cauze — luna de start greșită, metoda nepermisă pentru categoria de cont sau coeficientul degresiv greșit — iar corecția înseamnă recalcularea de la data punerii în funcțiune, nu ajustarea cifrei curente.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum corectez amortizarea calculată greșit?

O amortizare greșită nu rămâne izolată într-o singură lună — se propagă în toate lunile următoare, pentru că fiecare calcul pornește de la soldul anterior. Găsirea cauzei exacte a greșelii contează mai mult decât corectarea cifrei curente: dacă premisa e greșită (luna de start, metoda, coeficientul), orice ajustare făcută doar pe luna curentă lasă eroarea să reapară.

## Temeiul legal

::: ghid-temei
**Art. 28 din Codul fiscal (Legea 227/2015)** stabilește mecanic modul de calcul, pe fiecare metodă:

**Alin. (6)** (liniară): *„amortizarea se stabilește prin aplicarea cotei de amortizare liniară la valoarea fiscală de la data intrării în patrimoniul contribuabilului a mijlocului fix amortizabil."*

**Alin. (7)** (degresivă): *„amortizarea se calculează prin multiplicarea cotelor de amortizare liniară cu unul dintre coeficienții următori: a) 1,5, dacă durata normală de utilizare a mijlocului fix amortizabil este între 2 și 5 ani; ... b) 2,0, dacă durata normală de utilizare a mijlocului fix amortizabil este între 6 și 10 ani; ... c) 2,5, dacă durata normală de utilizare a mijlocului fix amortizabil este mai mare de 10 ani."*

**Alin. (12) lit. a)** (momentul de start): *„Amortizarea fiscală se calculează după cum urmează: a) începând cu luna următoare celei în care mijlocul fix amortizabil se pune în funcțiune, prin aplicarea regimului de amortizare prevăzut la alin. (5);"*
:::

## Cele trei cauze cele mai frecvente

**1. Luna de start greșită.** Amortizarea începe cu luna **următoare** punerii în funcțiune (alin. 12 lit. a), nu cu luna în care a avut loc PIF-ul. Un activ pus în funcțiune pe 15 martie începe să se amortizeze din aprilie, integral — nu proporțional cu cele câteva zile rămase din martie și nu din martie însuși.

**2. Metoda nepermisă pentru categoria de cont.** Fiecare categorie de mijloc fix are metode permise diferite (alin. 5): construcțiile (cont 212) doar liniar; echipamentele tehnologice și computerele (cont 2131) — liniar, degresiv sau accelerat; orice alt mijloc fix (inclusiv mijloacele de transport) — doar liniar sau degresiv, fără accelerat. O amortizare accelerată aplicată unui mijloc fix din categoria „orice altul" e greșită de la premisă, nu doar de calcul.

**3. Coeficientul degresiv greșit.** Coeficientul (1,5 / 2,0 / 2,5) depinde de durata normală de utilizare a activului, nu se alege liber — vezi tabelul din alin. (7) de mai sus.

## Cum se corectează

Corecția reală înseamnă recalcularea amortizării **de la data punerii în funcțiune**, cu parametrii corecți (metodă, coeficient, lună de start), nu ajustarea cifrei din luna curentă pentru a „echilibra" un total aproximativ. Diferența dintre amortizarea corect calculată și ce a fost deja înregistrat se reglează prin cont 6811 (dacă a fost înregistrat prea puțin) sau printr-o notă de stornare (dacă a fost înregistrat în plus), astfel încât soldul contului 2813 la data corecției să reflecte amortizarea cumulată reală.

## Ce se greșește în practică

- **Se ajustează doar amortizarea lunii curente**, „ca să iasă bine soldul", fără să se recalculeze de la PIF cu parametrii corecți — asta lasă toate lunile anterioare cu cifra greșită în continuare.
- **Se schimbă metoda de amortizare la mijlocul duratei**, fără temei, doar pentru a „repara" o cifră care pare prea mare sau prea mică — metoda se alege la punerea în funcțiune și rămâne fixă pentru acel activ (schimbarea ei ulterioară nu e un mecanism de corecție de erori).
- **Se calculează manual amortizarea în paralel cu ce arată registrul**, pe o foaie de calcul separată — orice discrepanță între cele două nu semnalează automat unde a apărut greșeala reală, pentru că nu există o singură sursă de adevăr pentru calcul.

## Ce face iConta.eu

Amortizarea se calculează cu un singur motor de calcul, folosit deopotrivă de ecranul registrului de mijloace fixe și de generatorul declarației D406/SAF-T — nu există un calcul simplificat separat pentru unul dintre cele două. Motorul aplică automat metoda pe categoria de cont a activului și refuză o metodă nepermisă pentru acea categorie, iar amortizat/rămas se recalculează la orice dată direct din datele activului (data punerii în funcțiune, metoda, durata normală de utilizare) — corectarea acestor date în registru propagă automat recalcularea, în loc să lase o cifră veche blocată undeva.

[iConta.eu](/)
