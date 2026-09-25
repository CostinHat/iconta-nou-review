---
title: "Ce fac dacă sistemul RO e-Factura este indisponibil în ultima zi de transmitere?"
description: "Ce spune Codul de procedură fiscală despre cazurile de forță majoră sau caz fortuit care împiedică îndeplinirea la termen a unei obligații fiscale, aplicabil și indisponibilității sistemului RO e-Factura."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce fac dacă sistemul RO e-Factura este indisponibil în ultima zi de transmitere?

Termenul de 5 zile lucrătoare pentru transmiterea facturii în sistemul RO e-Factura este o obligație fiscală ca oricare alta, supusă regulii generale a Codului de procedură fiscală privind forța majoră și cazul fortuit: dacă îndeplinirea obligației a fost efectiv împiedicată de un eveniment de acest tip (inclusiv, în principiu, o indisponibilitate a sistemului imputabilă infrastructurii ANAF), termenul nu curge sau se suspendă, iar obligația rămâne îndeplinită în termen dacă se execută în cel mult 60 de zile de la încetarea evenimentului.

## Temeiul legal

::: ghid-temei
„(1) Termenele prevăzute de lege pentru îndeplinirea obligațiilor fiscale, după caz, nu încep să curgă sau se suspendă în situația în care îndeplinirea acestor obligații a fost împiedicată de ivirea unui caz de forță majoră sau a unui caz fortuit.
(2) Obligațiile fiscale se consideră a fi îndeplinite în termen, fără perceperea de dobânzi, penalități de întârziere sau majorări de întârziere, după caz, ori aplicarea de sancțiuni prevăzute de lege, dacă acestea se execută în termen de 60 de zile de la încetarea evenimentelor prevăzute la alin. (1)."
— Legea nr. 207/2015 (Codul de procedură fiscală), art. 78 alin. (1), (2) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Ce înseamnă practic, pentru transmiterea facturii în RO e-Factura:

- Termenul general de transmitere este de 5 zile lucrătoare de la data emiterii facturii, dar nu mai târziu de 5 zile lucrătoare de la data-limită prevăzută pentru emiterea facturii (Legea nr. 296/2023, care a modificat OUG 120/2021).
- Dacă transmiterea a fost efectiv împiedicată de o cauză de forță majoră sau un caz fortuit — categorie în care se poate încadra o indisponibilitate generalizată, nu una punctuală/individuală, a sistemului RO e-Factura — art. 78 din Codul de procedură fiscală permite considerarea obligației îndeplinite în termen, cu condiția executării ei în cel mult 60 de zile de la încetarea evenimentului.
- Aceasta este o regulă **generală**, aplicabilă tuturor obligațiilor fiscale, nu o dispoziție specifică RO e-Factura — corpusul de surse verificat pentru acest ghid nu conține o procedură dedicată, emisă de ANAF, pentru indisponibilitatea punctuală a sistemului RO e-Factura, motiv pentru care încadrarea unei anumite situații concrete în „caz fortuit" trebuie analizată de la caz la caz, ideal cu documentarea indisponibilității (anunț oficial ANAF, capturi de ecran cu eroarea, jurnal de încercări).

## Ce se greșește în practică

- Se presupune că orice eroare tehnică personală (conexiune proprie la internet, certificat expirat) echivalează cu un „caz fortuit" care suspendă termenul — art. 78 vizează evenimente care împiedică obiectiv îndeplinirea obligației, nu dificultăți particulare ale contribuabilului.
- Se renunță la transmiterea facturii după prima încercare eșuată, fără a documenta momentul și natura indisponibilității, ceea ce face ulterior dificilă invocarea art. 78 în fața organului fiscal.
- Se așteaptă mai mult de 60 de zile de la încetarea indisponibilității pentru a transmite factura, depășind termenul de grație prevăzut la art. 78 alin. (2), ceea ce anulează beneficiul termenului „îndeplinit la timp".

## Ce face iConta.eu

La data acestui ghid, iConta.eu transmite facturile către SPV/RO e-Factura prin modulele `core/efactura_trimitere.py` și `core/spv_conector.py`, care includ o logică de reîncercare automată pentru anumite erori tranzitorii — reautentificare la eroarea 401 și așteptare exponențială („backoff") la eroarea 429 (prea multe cereri). Aplicația nu are însă o procedură specifică de gestionare a unei indisponibilități complete a sistemului ANAF (de exemplu, erori 503 prelungite) și nu documentează automat, în scopuri de probă pentru art. 78 din Codul de procedură fiscală, momentul și durata unei astfel de indisponibilități — contabilul rămâne responsabil să păstreze dovezi ale încercărilor eșuate de transmitere.

[iConta.eu](/)
