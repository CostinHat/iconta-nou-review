---
title: "Cum completez D212 pentru PFA la normă de venit?"
description: "La normă de venit se declară norma anuală (eventual ajustată), nu venitul brut și cheltuielile — iar CAS și CASS se calculează pe norma respectivă, nu pe un venit net dedus din contabilitate."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum completez D212 pentru PFA la normă de venit?

Diferența față de sistemul real e structurală: la normă de venit nu se completează venit brut și cheltuieli deductibile, ci direct valoarea normei anuale stabilite de direcția regională a finanțelor publice, eventual ajustată cu coeficienții de corecție publicați pentru activitatea respectivă.

## Temeiul legal

::: ghid-temei
„Contribuabilii pot ajusta normele anuale de venit de la alin. (4) în declarația unică privind impozitul pe venit și contribuțiile sociale datorate de persoanele fizice. Ajustarea normelor anuale de venit se realizează de către contribuabil prin aplicarea coeficienților de corecție publicați de către Direcțiile generale regionale ale finanțelor publice, respectiv a municipiului București, asupra normelor anuale de venit."
— Codul fiscal (Legea 227/2015), art. 69 alin. (10) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„Contribuabilii care desfășoară activități pentru care venitul net se determină pe bază de norme de venit au obligația să completeze numai partea referitoare la venituri din Registrul de evidență fiscală și nu au obligații privind evidența contabilă."
— Codul fiscal, art. 69 alin. (8) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce rezultă practic pentru completarea D212 la capitolul de normă de venit:

- Norma de venit anuală e cea publicată pentru activitatea CAEN și locul de desfășurare, nu poate fi mai mică decât nivelul a 12 salarii minime brute pe țară (art. 69 alin. (3)).
- Dacă activitatea s-a desfășurat doar o parte din an, norma se reduce proporțional (art. 69 alin. (5) și art. 122 alin. (2)).
- CAS și CASS se calculează pe norma de venit (eventual ajustată), nu pe cheltuieli reale — pentru că nu există evidența cheltuielilor la normă (art. 69 alin. (8)).
- Nu se completează secțiunile de cheltuieli deductibile ale declarației, deoarece nu există obligație de evidență contabilă la normă de venit.

## Ce se greșește în practică

- Se completează câmpurile de venit brut/cheltuieli deductibile din capitolul de sistem real, în loc de câmpul dedicat normei de venit — cele două capitole nu sunt interschimbabile în structura declarației.
- Se declară norma nemodificată, deși activitatea nu s-a desfășurat un an calendaristic întreg — omiterea reducerii proporționale supraevaluează venitul impozabil.
- Se calculează CAS/CASS pe o bază estimată din venituri reale, în loc de norma de venit publicată — la normă de venit, baza de calcul e norma, nu încasările efective.

## Ce face iConta.eu

Generatorul D212 al iConta.eu (`core/d212.py`) emite capitolul dedicat normei de venit (`cap12`) cu câmpurile oficiale — `real_norma_venit`, `real_ajustare`, `real_venit_net_anual`, `real_impozit` — dar declarația e **manuală**: valoarea normei, ajustarea și rezultatul se introduc direct, nu se preiau din vreo evidență ținută în aplicație.

Registrul de evidență fiscală pentru persoane fizice din iConta.eu (`core/registru_evidenta_fiscala.py`, conform OMFP 3254/2017) susține corect regula specifică normei de venit: la `mod_venit_net = 3` (normă de venit), aplicația **refuză** înregistrarea dacă se introduce o valoare la cheltuieli deductibile, exact potrivit art. 1 alin. (2) din ordin. Calculul automat CAS/CASS din `core/rip_api.py` (`fisa_d212`) e construit însă pentru sistem real (venit brut minus cheltuieli din Registrul-jurnal de încasări și plăți) și nu acoperă norma de venit — pentru PFA la normă, CAS și CASS se calculează manual, pe norma declarată.

[iConta.eu](/)
