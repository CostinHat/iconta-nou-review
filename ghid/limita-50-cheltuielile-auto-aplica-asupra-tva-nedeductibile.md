---
title: "Limita de 50% la cheltuielile auto se aplică și asupra TVA nedeductibile?"
description: "Da: TVA nedeductibilă (50% din TVA la vehiculele folosite mixt) devine cheltuială, se adaugă la bază, iar limita de 50% la impozitul pe profit se aplică pe totalul astfel obținut."
published: 2026-09-29
modified: 2026-09-29
poarta: v1
---

# Limita de 50% la cheltuielile auto se aplică și asupra TVA nedeductibile?

Da. La un vehicul folosit și în scop personal, operezi în doi pași, în ordine. Întâi limitezi TVA: se deduce 50% din TVA, iar cealaltă jumătate devine cheltuială. Apoi, la impozitul pe profit, aplici limita de 50% pe **cheltuiala fără TVA plus TVA nedeductibilă**. Partea de TVA pe care nu ai putut-o deduce trece deci și ea prin limitarea de 50% la profit.

Contează pentru că mulți contabili aplică limita de profit doar pe valoarea fără TVA și trec TVA nedeductibilă integral pe cheltuieli deductibile. Normele spun explicit că ordinea e inversă: întâi limitarea la TVA, apoi limitarea la profit, pe o bază care include TVA nedeductibilă.

## Temeiul legal

::: ghid-temei
„50% din cheltuielile aferente vehiculelor rutiere motorizate care nu sunt utilizate exclusiv în scopul activității economice, cu o masă totală maximă autorizată care să nu depășească 3.500 kg și care să nu aibă mai mult de 9 scaune de pasageri, incluzând și scaunul șoferului, aflate în proprietatea sau în folosința contribuabilului."
— Codul fiscal (Legea 227/2015), art. 25 alin. (3) lit. l) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

::: ghid-temei
„În cadrul cheltuielilor aferente vehiculelor rutiere motorizate supuse limitării fiscale se cuprind cheltuielile direct atribuibile unui vehicul, cum sunt: impozitele locale, asigurarea obligatorie de răspundere civilă auto, inspecțiile tehnice periodice, rovinieta, chiriile, partea nedeductibilă din taxa pe valoarea adăugată, dobânzile, comisioanele"
— HG 1/2016, Normele metodologice, titlul II, pct. 16 alin. (3) (sursă: anaf_surse/hg_1_2016_norme_cod_fiscal.txt)

„Aplicarea limitei de 50% pentru stabilirea valorii nedeductibile la determinarea rezultatului fiscal se efectuează după aplicarea limitării aferente taxei pe valoarea adăugată, respectiv aceasta se aplică și asupra taxei pe valoarea adăugată pentru care nu s-a acordat drept de deducere din punctul de vedere al taxei pe valoarea adăugată."
— HG 1/2016, Normele metodologice, titlul II, pct. 16 alin. (3) (sursă: anaf_surse/hg_1_2016_norme_cod_fiscal.txt)
:::

Ordinea de calcul:

1. **TVA**: pentru vehiculele folosite mixt, deduci 50% din TVA (art. 298 CF). Cealaltă jumătate e TVA nedeductibilă și devine cheltuială.
2. **Baza pentru profit**: cheltuiala fără TVA + TVA nedeductibilă.
3. **Limitarea la profit**: 50% din această bază e nedeductibil la calculul rezultatului fiscal.

Ce intră în bază: întreținere și reparații, combustibil, impozite locale, RCA, ITP, rovinietă, chirii, dobânzi, comisioane, plus partea nedeductibilă din TVA. Ce nu intră: amortizarea, pe care Codul fiscal o scoate expres din lit. l).

Exemplele din norme folosesc cifre de TVA mai vechi. Mecanismul e cel de mai sus, iar cifrele le refaci cu cota de TVA în vigoare, 21% din 01.08.2025.

::: ghid-exemplu
SC Exemplu SRL, plătitoare de TVA, face o reparație la un autoturism folosit mixt: 2.000 lei + TVA 21% = 420 lei.

**TVA**: deductibilă 50% x 420 = 210 lei; nedeductibilă 210 lei, trecută pe cheltuieli.

**Baza pentru profit**: 2.000 + 210 = 2.210 lei.

**Nedeductibil la profit**: 2.210 x 50% = 1.105 lei. Deductibil: 1.105 lei.

Dacă s-ar fi aplicat limita doar pe 2.000 lei, nedeductibilul ar fi fost 1.000 lei, iar TVA nedeductibilă de 210 lei ar fi fost dedusă integral, cu 105 lei deduși în plus.
:::

## Ce se greșește în practică

- Limita de 50% la profit se aplică doar pe valoarea fără TVA, iar TVA nedeductibilă e tratată integral ca deductibilă.
- Ordinea se inversează: se limitează întâi la profit și apoi la TVA, iar baza iese greșit.
- Amortizarea autoturismului se include în limitare, deși codul o exclude.
- Se aplică limitele la vehiculele din categoriile exceptate (curierat, pază, agenți de vânzări, taxi, închiriere), unde cheltuielile sunt integral deductibile.

## Ce face iConta.eu

La facturile primite, iConta.eu contează TVA pe cote. Limitarea de 50% la TVA pentru vehicule și limitarea de 50% la impozitul pe profit nu sunt însă calculate automat pe tipul de vehicul. Contabilul stabilește partea nedeductibilă, o înregistrează în nota contabilă și o trece pe rândul de cheltuieli nedeductibile din D101, pe care aplicația o generează din balanță.

[iConta.eu](/)
