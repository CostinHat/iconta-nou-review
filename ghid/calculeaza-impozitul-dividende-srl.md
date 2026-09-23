---
title: "Cum se calculează impozitul pe dividende pentru SRL"
description: "Formula de calcul a impozitului reținut la sursă pentru dividendele plătite de un SRL asociaților persoane fizice."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se calculează impozitul pe dividende pentru SRL

Pentru un SRL cu asociați persoane fizice, impozitul pe dividende se calculează prin aplicarea cotei în vigoare la data distribuirii, asupra sumei efectiv plătite asociatului.

## Temeiul legal

::: ghid-temei
"(7) Veniturile sub formă de dividende, inclusiv câștigul obținut ca urmare a deținerii de titluri de participare definite de legislația în materie la organisme de plasament colectiv, se impozitează cu o cotă de 16% din suma acestora, impozitul fiind final. Obligația calculării și reținerii impozitului pe veniturile sub formă de dividende revine persoanelor juridice, odată cu plata dividendelor/sumelor reprezentând câștigul obținut ca urmare a deținerii de titluri de participare de către acționari/asociați/investitori."
— Codul fiscal, art. 97 alin. (7) (`anaf_surse/cod_fiscal_227_2015_consolidat.txt:9470-9474`)
:::

Formula de bază este: **impozit = cotă × bază de impozitare**, unde baza este suma dividendului efectiv **plătit** asociatului (nu suma aprobată spre distribuire), iar cota este cea de la data la care dividendul a fost **distribuit** (nu la data plății). Dacă distribuirea și plata cad în perioade cu cote diferite, calculul se face pe tranșe, folosind cota corespunzătoare fiecărei distribuiri din care provine suma plătită.

## Ce se greșește în practică

Se aplică frecvent o singură cotă (cea din anul curent) la întreaga sumă plătită, chiar și atunci când plata provine dintr-un dividend distribuit într-un an cu altă cotă legală — ceea ce duce la impozit calculat greșit.

## Ce face iConta.eu

Motorul de calcul (`core/d205.py`) determină baza de impozitare din dividendul efectiv plătit al fiecărui asociat, citit din contul 457, iar cota este preluată din registrul central de cote, sensibil la perioadă. Pentru situațiile în care distribuirea și plata sunt în ani diferiți sau plata este eșalonată, algoritmul FIFO din `core/dividende_curs.py` calculează impozitul ponderat pe fiecare tranșă, cu cota de la data distribuirii corespunzătoare — verificat prin teste care confirmă atât cazul unei plăți integrale amânate într-un an cu altă cotă, cât și cazul unei plăți parțiale eșalonate.

[iConta.eu](/)
