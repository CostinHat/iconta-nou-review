---
title: Cum corectez suma dividendelor în D205?
description: Suma vine automat din notele contabile validate pe contul 457 — corectarea reală se face acolo, nu pe declarație. Atenție și la cotele diferite pe ani: o sumă "ciudată" poate fi de fapt corect calculată cu cotă mixtă pe tranșe.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum corectez suma dividendelor în D205?

Suma din D205 nu se introduce direct pe declarație — vine automat din notele contabile validate pe contul 457. Dacă suma pare greșită, primul loc de verificat e nota contabilă, nu formularul.

## Temeiul legal

::: ghid-temei
**Legea 141/2025, art. VII alin. (2)**: „În cazul dividendelor distribuite în baza situațiilor financiare interimare întocmite în cursul anului 2025/anului fiscal modificat care începe în anul 2025, cota de impozit pe dividende este de 10%, fără recalcularea impozitului pe dividendele respective, după regularizarea acestora pe baza situațiilor financiare anuale [...]"
:::

## Unde se corectează, de fapt

Baza (suma distribuită/plătită) și impozitul se calculează automat din contul 457: creditul reprezintă dividendul **distribuit**, debitul reprezintă dividendul **plătit** — iar impozitul se calculează pe suma plătită, nu pe cea doar distribuită. Aplicația citește exclusiv notele contabile cu status „validată" — o notă greșită sau nevalidată e cauza cea mai probabilă a unei sume greșite în declarație.

Pentru un **beneficiar introdus manual** (nu preluat automat din 457), aplicația nu face reconcilierea completă față de contabilitate — verifică doar consistența internă (impozitul calculat = cota × bază), deci corectitudinea sumei introduse manual e responsabilitatea integrală a celui care o introduce.

## Atenție la cota pe tranșe, înainte de a presupune o eroare

Dacă un dividend a fost distribuit într-un an (cu o anumită cotă) și plătit eșalonat sau în anul următor (cu o cotă diferită), impozitul se calculează **ponderat**, pe fiecare tranșă de plată, cu cota de la data distribuirii, nu cu o cotă unică aplicată la sfârșitul anului. O sumă care pare „greșită" la prima vedere poate fi de fapt corect calculată cu cote mixte — verificați datele de distribuire și de plată înainte de a presupune o eroare de calcul.

## Ce se greșește în practică

Se corectează suma direct „vizual", pe fișierul generat, în loc de a corecta nota contabilă sursă — orice modificare directă pe declarație, fără corectarea contului 457, se pierde la următoarea regenerare și nu reflectă realitatea contabilă.

## Ce face iConta.eu

Suma se calculează automat din contul 457, cu impozitul ponderat corect pe tranșe atunci când cota s-a schimbat între anul distribuirii și anul plății. O reconciliere independentă recalculează separat baza și impozitul per beneficiar și blochează generarea la orice divergență față de contabilitate — dar doar pentru beneficiarii proveniți din 457; pentru cei introduși manual, verificarea se limitează la consistența internă a calculului.

[iConta.eu](/)
