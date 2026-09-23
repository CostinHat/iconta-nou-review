---
title: "Amortizarea la lichidarea firmei: ultimele înregistrări"
description: "Cum se descarcă amortizarea cumulată a unui mijloc fix vândut în procedura de lichidare."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Amortizarea la lichidarea firmei: ultimele înregistrări

Când un mijloc fix este vândut în timpul lichidării, amortizarea lui nu mai continuă lunar — ea se descarcă integral, odată cu ieșirea activului din patrimoniu.

## Temeiul legal

::: ghid-temei
Lichidatorii pot „să vândă, prin licitație publică, imobilele și orice avere mobiliară a societății" (Legea 31/1990, art. 255 alin. (1) lit. c)), operațiune posibilă pentru că „societatea își păstrează personalitatea juridică pentru operațiunile lichidării, până la terminarea acesteia" (Legea 31/1990, art. 233 alin. (4)).
:::

Monografia contabilă detaliată pentru operațiunile de lichidare este cuprinsă în anexele OMFP 897/2015, care nu au putut fi consultate direct pentru acest ghid — au fost publicate separat, în Monitorul Oficial. Ce se poate confirma sigur este mecanismul efectiv aplicat de motorul de calcul al iConta la vânzarea unui activ în lichidare, descris mai jos.

## Ce se greșește în practică

- Se lasă activul „la amortizare" în continuare după vânzare, în loc să se descarce integral amortizarea cumulată în aceeași notă cu vânzarea.
- Se înregistrează doar ieșirea valorii rămase, fără să se scoată și amortizarea cumulată din contul de imobilizare — rezultă solduri reziduale incorecte pe conturile de imobilizări și amortizare.

## Ce face iConta.eu

La operația „Vânzare activ la lichidare" din ecranul „Lichidare / radiere firmă", pe lângă prețul de vânzare și valoarea brută a activului, se introduce și amortizarea cumulată. Nota contabilă generată automat descarcă, într-o singură operațiune, atât valoarea rămasă a activului cât și amortizarea cumulată aferentă (cheltuială 6583 și amortizare 28xx, scoase din contul de imobilizare 21x), în paralel cu înregistrarea venitului din vânzare și a TVA colectate. Aceasta este, practic, ultima înregistrare de amortizare pentru activul respectiv — descărcarea integrală, nu o amortizare lunară suplimentară.

Notă: conținutul exact al monografiei contabile din Anexele OMFP 897/2015 nu a putut fi verificat direct din textul legii pentru acest ghid; cele de mai sus descriu ce calculează efectiv aplicația, nu un citat din anexă.

[iConta.eu](/)
