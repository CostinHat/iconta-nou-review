---
title: "Amortizarea activelor de mică valoare și valoare mică: plafon"
description: "Plafonul de 5.000 lei (majorat de la 2.500 lei prin OUG 8/2026) sub care un bun nu se amortizează ca mijloc fix, ci se trece integral pe cheltuieli ca obiect de inventar."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Amortizarea activelor de mică valoare și valoare mică: plafon

Plafonul sub care un bun nu mai e tratat ca mijloc fix amortizabil, ci ca obiect de inventar trecut integral pe cheltuieli, s-a schimbat în 2026: de la 2.500 lei la 5.000 lei, dar numai pentru bunurile intrate în patrimoniu după data modificării.

## Temeiul legal

::: ghid-temei
„Mijlocul fix amortizabil este orice imobilizare corporală care îndeplinește cumulativ următoarele condiții: [...] b) la data intrării în patrimoniul contribuabilului, are o valoare fiscală egală sau mai mare decât suma de 5.000 lei; această limită se actualizată anual, în funcție de indicele de inflație, prin hotărâre a Guvernului; [...] c) are o durată normală de utilizare mai mare de un an."
— Legea 227/2015, art. 28 alin. (2) lit. b)-c), astfel cum a fost modificată de OUG nr. 8/2026, art. 6 pct. 7, în vigoare de la 25.02.2026 (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Regula de încadrare: dacă valoarea de achiziție a bunului e sub pragul în vigoare la data intrării în patrimoniu, sau dacă durata normală de utilizare e sub un an, bunul nu se amortizează, ci se înregistrează ca obiect de inventar — cheltuiala se recunoaște integral la darea în folosință (contul 603), cu evidență extracontabilă separată (D8035) până la scoaterea din uz. Pragul e valabil doar pentru bunurile intrate în patrimoniu **de la data modificării**: bunurile intrate anterior, la vechiul plafon de 2.500 lei, rămân mijloace fixe amortizabile și continuă amortizarea pe durata rămasă — pragul nou nu le reclasifică retroactiv.

## Ce se greșește în practică

- Se aplică noul plafon de 5.000 lei retroactiv, la mijloace fixe intrate în patrimoniu înainte de 25.02.2026, reclasificându-le greșit ca obiecte de inventar — legea nu prevede o astfel de reclasificare.
- Se ignoră data exactă a intrării în patrimoniu (nu data facturii, nu data plății, ci data recepției/punerii în funcțiune, după caz) la stabilirea pragului aplicabil unui bun cumpărat chiar în perioada de tranziție.
- Se confundă plafonul de încadrare ca mijloc fix (art. 28) cu alte praguri fiscale din Codul fiscal (de exemplu plafonul de deductibilitate a amortizării pentru autoturisme, 1.500 lei/lună), care sunt reguli complet separate.

## Ce face iConta.eu

iConta.eu are un motor dedicat pentru obiecte de inventar (conform OMFP 1802/2014), cu funcția `prag_mf(la_data)`, care determină pragul de încadrare ca mijloc fix exact la data intrării bunului în patrimoniu — 2.500 lei pentru bunuri intrate până la 24.02.2026 inclusiv, 5.000 lei pentru cele intrate de la 25.02.2026, conform OUG 8/2026, art. 6 pct. 7. Aplicația are un test dedicat (gard de conformitate) care verifică explicit atât valoarea corectă a pragului la fiecare dată, cât și faptul că un bun de 3.000 lei e clasificat mijloc fix înainte de 25.02.2026 și obiect de inventar după — și că pragul e citit dintr-o singură sursă (registrul de cote al aplicației), nu duplicat în mai multe module.

[iConta.eu](/)
