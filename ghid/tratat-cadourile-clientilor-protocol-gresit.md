---
title: "Am tratat cadourile clienților ca protocol greșit"
description: "Limita de deducere fiscală pentru cheltuielile de protocol la impozitul pe profit, conform Codului fiscal."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Am tratat cadourile clienților ca protocol greșit

Cadourile oferite clienților — mese de afaceri, obiecte promoționale, atenții la evenimente — intră de regulă la cheltuieli de protocol. Dar deducerea lor la impozitul pe profit nu este integrală, ci plafonată.

## Temeiul legal

::: ghid-temei
„Următoarele cheltuieli au deductibilitate limitată: a) cheltuielile de protocol în limita unei cote de 2% aplicată asupra profitului contabil la care se adaugă cheltuielile cu impozitul pe profit și cheltuielile de protocol. În cadrul cheltuielilor de protocol se includ și cheltuielile înregistrate cu taxa pe valoarea adăugată colectată potrivit prevederilor titlului VII, pentru cadourile oferite de contribuabil, cu valoare mai mare de 100 lei;"
— Legea 227/2015 (Codul fiscal), art. 25 alin. (3) lit. a) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce înseamnă practic acest plafon de 2%:

- Cheltuielile de protocol sunt deductibile **doar în limita a 2%** aplicată asupra bazei de calcul stabilite de Codul fiscal — nu integral, așa cum sunt, de regulă, cheltuielile curente de exploatare.
- Baza de calcul a plafonului este **profitul contabil la care se adaugă cheltuielile cu impozitul pe profit și cheltuielile de protocol** — adică plafonul se determină pornind de la un rezultat „brut", nu de la profitul net înregistrat deja după scăderea acestor cheltuieli.
- În cheltuielile de protocol se include și **TVA colectată** aferentă acestora, potrivit acelorași prevederi.
- Partea care depășește plafonul de 2% este **cheltuială nedeductibilă** la calculul impozitului pe profit — nu se pierde ca sumă cheltuită, dar nu reduce baza impozabilă.

## Ce se greșește în practică

- Se deduce integral valoarea cadourilor oferite clienților, fără să se aplice plafonul de 2%, considerându-le cheltuieli curente de marketing sau reprezentare fără limită.
- Se calculează plafonul de 2% direct din profitul net contabil, în loc să se pornească de la baza corectă — profit contabil plus impozit pe profit plus cheltuieli de protocol.
- Se omite includerea TVA colectate aferente cheltuielilor de protocol în valoarea supusă plafonării.

## Ce face iConta.eu

Am verificat rapid în `core/` dacă există un modul dedicat calculului cheltuielilor de protocol la determinarea impozitului pe profit (D101) și **nu am găsit** o funcție care să aplice automat plafonul de 2% din art. 25 alin. (3) lit. a) din Codul fiscal. Clasificarea unei cheltuieli drept „protocol" și încadrarea ei în plafonul deductibil rămân, la acest moment, o verificare manuală a contabilului la închiderea perioadei fiscale.

[iConta.eu](/)
