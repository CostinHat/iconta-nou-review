---
title: "Avansurile încasate intră în plafonul de TVA?"
description: "Ce se cuprinde în cifra de afaceri relevantă pentru plafonul de scutire de TVA al întreprinderilor mici, conform Codului fiscal, și cum se tratează avansurile."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Avansurile încasate intră în plafonul de TVA?

Plafonul de scutire de TVA pentru întreprinderile mici (395.000 lei, din 2025) se calculează pe baza „cifrei de afaceri" definite explicit de Codul fiscal — iar avansul, ca simplă încasare anticipată, nu e prin el însuși o livrare sau o prestare.

## Temeiul legal

::: ghid-temei
„Cifra de afaceri care servește drept referință pentru aplicarea alin. (1) este constituită din valoarea totală, exclusiv taxa [...], a livrărilor de bunuri și a prestărilor de servicii efectuate de persoana impozabilă în cursul unui an calendaristic, taxabile sau, după caz, care ar fi taxabile dacă nu ar fi desfășurate de o mică întreprindere, a operațiunilor scutite cu drept de deducere și, dacă nu sunt accesorii activității principale, a operațiunilor scutite fără drept de deducere prevăzute la art. 292 alin. (2) lit. a), b), e) și f), cu locul în România."
— Legea 227/2015 (Codul fiscal), art. 310 alin. (2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Din formularea legii rezultă:

- plafonul se calculează pe baza **livrărilor de bunuri și prestărilor de servicii efectuate**, nu pe baza sumelor încasate — un avans, prin definiție, precede livrarea/prestarea efectivă, deci nu constituie el însuși o operațiune „efectuată" în sensul acestui text;
- avansul intră totuși în calculul cifrei de afaceri **atunci când, prin natura lui, coincide cu momentul livrării/prestării** — de exemplu, dacă bunul se livrează integral la momentul plății avansului sau dacă facturarea avansului se face concomitent cu executarea efectivă a serviciului; în restul cazurilor, suma relevantă e cea a livrării/prestării finale, facturate la finalizarea tranzacției;
- textul exclude explicit din calculul plafonului **livrările de active fixe corporale** și **cesiunea/transferul de active necorporale**, indiferent de valoarea lor — o distincție separată de tema avansurilor, dar utilă pentru firmele care vând mijloace fixe ocazional.

## Ce se greșește în practică

- Se adună la cifra de afaceri relevantă pentru plafon orice sumă încasată în cont, inclusiv avansuri care nu corespund încă unei livrări sau prestări efectuate — plafonul se raportează la operațiuni efectuate, nu la fluxul de casă.
- Se omite din calculul plafonului valoarea finală a unei livrări/prestări facturate, pe motiv că „avansul a fost deja luat în calcul" într-o lună anterioară — dacă avansul nu a corespuns unei livrări efective la momentul respectiv, valoarea relevantă rămâne cea a operațiunii finalizate.
- Se ignoră faptul că, odată depășit plafonul, înregistrarea în scopuri de TVA devine obligatorie de la data depășirii, indiferent dacă sumele care au dus la depășire au fost încasate ca avans sau ca plată integrală.

## Ce face iConta.eu

iConta.eu urmărește plafonul relevant pentru TVA la încasare (`core/tva_incasare.py`, funcția `plafon_la()`), care e un prag distinct de cel de înregistrare în scopuri de TVA analizat mai sus. Aplicația nu are, la data acestui ghid, o funcție separată care să calculeze automat cifra de afaceri relevantă pentru plafonul de scutire al întreprinderilor mici (art. 310) și să distingă în acest calcul avansurile de livrările/prestările efective — verificarea plafonului de înregistrare rămâne, pentru acest scenariu, responsabilitatea contabilului.

[iConta.eu](/)
