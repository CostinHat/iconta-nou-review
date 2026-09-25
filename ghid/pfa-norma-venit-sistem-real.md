---
title: "PFA la normă de venit sau sistem real în 2026: cum știu ce regim mi se aplică?"
description: "Regulile din Codul fiscal care decid dacă o PFA determină venitul net pe bază de normă de venit sau în sistem real, și situațiile în care sistemul real devine obligatoriu."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# PFA la normă de venit sau sistem real în 2026: cum știu ce regim mi se aplică?

Regula de bază: dacă activitatea PFA-ului este inclusă în nomenclatorul de activități pentru care se pot stabili norme anuale de venit, venitul net se determină, implicit, pe bază de normă de venit „de la locul desfășurării activității". Regimul se schimbă însă automat în sistem real în anumite situații, iar contribuabilul poate oricând opta voluntar pentru sistem real.

## Temeiul legal

::: ghid-temei
„(1) În cazul contribuabililor care realizează venituri din activități independente, altele decât venituri din profesii liberale definite la art. 67 alin. (2), venitul net anual se determină pe baza normelor de venit de la locul desfășurării activității.
[...]
(7) În cazul în care un contribuabil desfășoară o activitate inclusă în nomenclatorul prevăzut la alin. (2) și o altă activitate independentă, venitul net anual se determină în sistem real, pe baza datelor din contabilitate, potrivit prevederilor art. 68.
[...]
(9) Contribuabilii, pentru care venitul net se determină pe bază de norme de venit și care în anul fiscal anterior au înregistrat un venit brut anual mai mare decât echivalentul în lei al sumei de 25.000 euro, începând cu anul fiscal următor au obligația determinării venitului net anual în sistem real."
— Legea nr. 227/2015 (Codul fiscal), art. 69 alin. (1), (7), (9) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Regulile, în ordine practică de verificare:

1. **Regula implicită**: dacă activitatea PFA-ului (codul CAEN) se regăsește în nomenclatorul de activități pentru care se pot stabili norme de venit, venitul net anual = norma de venit stabilită de administrația fiscală județeană pentru locul desfășurării activității, ajustată eventual cu coeficienți de corecție (art. 69 alin. (10)).
2. **Trecere obligatorie la sistem real, în cursul aceluiași an**: dacă PFA-ul desfășoară, pe lângă activitatea de la normă, și o altă activitate independentă care nu se încadrează la normă, venitul net pentru **toate** activitățile independente se determină în sistem real (art. 69 alin. (7)).
3. **Trecere obligatorie la sistem real, din anul următor**: dacă venitul brut anual din anul precedent a depășit echivalentul a 25.000 euro, PFA-ul trece obligatoriu la sistem real din anul fiscal următor și trebuie să depună Declarația unică (art. 69 alin. (9)).
4. **Opțiune voluntară**: chiar dacă rămâne sub pragurile de mai sus, contribuabilul poate opta oricând pentru sistem real (art. 69^1), opțiune obligatorie pentru minimum 2 ani fiscali consecutivi.

## Ce se greșește în practică

- Se aplică norma de venit fără verificarea prealabilă a nomenclatorului de activități publicat de direcția generală regională a finanțelor publice — nu toate codurile CAEN de activități independente au normă de venit stabilită.
- Se ignoră pragul de 25.000 euro venit brut anual, care obligă trecerea la sistem real din anul următor, chiar dacă activitatea rămâne, în principiu, eligibilă pentru normă.
- Se calculează greșit norma de venit atunci când PFA-ul are și o a doua activitate independentă neinclusă în nomenclator — în acest caz toată activitatea (inclusiv cea „la normă") trece la sistem real, nu doar cea de-a doua.

## Ce face iConta.eu

La data acestui ghid, iConta.eu nu are o funcționalitate care să verifice automat, pe baza codului CAEN, dacă o activitate PFA se încadrează în nomenclatorul cu normă de venit sau să detecteze automat depășirea pragului de 25.000 euro pentru trecerea obligatorie la sistem real — aceste verificări rămân în sarcina contabilului. Pentru PFA-urile în sistem real (partidă simplă), aplicația oferă modulul de evidență a operațiunilor (`core/rip_api.py`), cu funcția `fisa_d212`, care calculează venitul brut, cheltuielile deductibile și baza CAS/CASS din operațiunile validate introduse de utilizator, pentru generarea Declarației unice (D212).

[iConta.eu](/)
