---
title: "Trebuie rectificată D205 dacă am corectat D100?"
description: "De ce D205 (declarația informativă privind impozitul reținut la sursă) și D100 se corectează pe căi separate, fără legătură automată între ele."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Trebuie rectificată D205 dacă am corectat D100?

D100 declară obligații de plată stabilite prin autoimpunere sau reținere la sursă (de exemplu impozitul pe dividende reținut la sursă), în timp ce D205 este o declarație **informativă**, care raportează anual, pe fiecare beneficiar de venit, sumele reținute. Corectarea uneia nu declanșează automat, din punct de vedere legal, corectarea celeilalte — dar legea le tratează diferit, iar diferența contează.

## Temeiul legal

::: ghid-temei
„(1) Declarația de impunere poate fi corectată de către contribuabil/plătitor, pe perioada termenului de prescripție a dreptului de a stabili creanțe fiscale. (2) Declarația informativă poate fi corectată de către contribuabil/plătitor indiferent de perioada la care se referă."
— Codul de procedură fiscală (Legea 207/2015), art. 105 alin. (1)-(2) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

- D100 e o „declarație de impunere" — corecția ei e supusă termenului de prescripție a dreptului organului fiscal de a stabili creanțe fiscale (regula generală: 5 ani).
- D205 e o „declarație informativă" — poate fi corectată **indiferent de perioada la care se referă**, fără plafonul de prescripție care limitează declarațiile de impunere.
- La nivelul formularului, corecția D205 se face explicit „în condițiile art. 105 și 170" din Codul de procedură fiscală, prin bifarea căsuței „Declarație rectificativă" pe același model de formular (OPANAF, instrucțiunile D205), iar rectificativa „se întocmește pe tipuri de venit și va cuprinde numai pozițiile corectate [...] sau pozițiile care, în mod eronat, nu au fost cuprinse în declarația inițială."

## Ce se greșește în practică

- Se presupune că, odată corectat D100, D205 trebuie automat rectificată în paralel — legea le tratează ca declarații distincte, cu regim de corecție diferit (impunere vs. informativă).
- Se retrimite integral D205 la o corecție, în loc să se cuprindă „numai pozițiile corectate" — regula explicită din instrucțiuni cere ca rectificativa să conțină doar diferențele, nu toate pozițiile declarate inițial.
- Se ignoră faptul că D205 poate fi corectată oricând, fără limita de prescripție — un contabil care descoperă o eroare veche pe D205 nu trebuie să se oprească la termenul de 5 ani valabil pentru D100.

## Ce face iConta.eu

D205 are, în iConta.eu, propriul marcaj de declarație rectificativă și se generează din surse de date proprii (reținerile efectiv înregistrate pe beneficiari, pe parcursul anului), independent de D710. Formularul 710 corectează exclusiv obligațiile declarate prin D100 pentru codurile 121 (impozit micro) și 103 (impozit pe profit) — nu D205, care nici măcar nu corespunde vreunuia dintre aceste două coduri de obligație. iConta.eu **nu are o funcție care leagă automat** o corecție D100 de o rectificare D205: dacă o eroare pe D100 afectează și datele raportate prin D205, verificarea și corecția D205 rămân un pas separat, decis de contabil, nu un flux declanșat automat din ecranul D710.

[iConta.eu](/)
