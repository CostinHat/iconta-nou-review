---
title: "Cum se ajustează TVA la mijloacele fixe cu durată sub 5 ani cumpărate înainte de 2016?"
description: "Pentru activele cu durată de utilizare sub 5 ani cumpărate până la 31.12.2015, TVA se ajustează proporțional cu valoarea rămasă neamortizată; activele complet amortizate nu se mai ajustează."
published: 2026-09-29
modified: 2026-09-29
poarta: v1
---

# Cum se ajustează TVA la mijloacele fixe cu durată sub 5 ani cumpărate înainte de 2016?

Nu se aplică regula cincimilor din art. 305, ci o regulă tranzitorie. TVA se ajustează proporțional cu valoarea rămasă neamortizată în momentul în care apare evenimentul care obligă la ajustare. Dacă activul este complet amortizat la acea dată, nu se mai ajustează nimic. În 2026 regula are aplicare practică redusă: un activ cu durată sub 5 ani, cumpărat cel târziu în 2015, este de regulă amortizat complet de mulți ani. Contează însă la verificarea ajustărilor din anii trecuți și la situații atipice.

## Temeiul legal

::: ghid-temei
„Prin excepție de la prevederile art. 305 alin. (5) , se ajustează taxa deductibilă proporțional cu valoarea rămasă neamortizată la momentul la care intervin evenimentele prevăzute la art. 305 alin. (4) pentru următoarele categorii de active corporale fixe care până la data de 31 decembrie 2015 nu erau considerate bunuri de capital"
— Codul fiscal (Legea 227/2015), art. 306 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

::: ghid-temei
„a) activele corporale fixe amortizabile a căror durată normală de utilizare stabilită pentru amortizarea fiscală este mai mică de 5 ani, care au fost achiziționate sau fabricate după data aderării până la data 31 decembrie 2015 inclusiv"
— HG 1/2016 (normele Codului fiscal), Titlul VII, pct. 80 alin. (1) (sursă: anaf_surse/hg_1_2016_norme_cod_fiscal.txt)

„(4) Ajustarea taxei în cazul activelor corporale fixe prevăzute la alin. (1) se efectuează proporțional cu valoarea rămasă neamortizată la momentul la care intervin evenimentele prevăzute la alin. (2) . Dacă activele sunt complet amortizate la momentul la care intervin evenimentele prevăzute la alin. (2) nu se mai fac ajustări de taxă."
— HG 1/2016, Titlul VII, pct. 80 alin. (4) (sursă: anaf_surse/hg_1_2016_norme_cod_fiscal.txt)
:::

Ce active intră:

- **Mijloace fixe amortizabile** cu durată normală de utilizare fiscală sub 5 ani, cumpărate sau fabricate după aderare și până la 31.12.2015 inclusiv.
- **Mijloace fixe în leasing** a căror limită minimă a duratei normale de utilizare e sub 5 ani, din aceeași perioadă. Aici valoarea neamortizată se calculează ca și cum bunul ar fi fost amortizat contabil pe durata minimă (pct. 80 alin. (5)).

Cum se ajustează:

- **Evenimentele** sunt cele de la art. 305 alin. (4): utilizare în alte scopuri decât activitatea economică sau pentru operațiuni fără drept de deducere, modificarea pro rata, încetarea existenței bunului etc.
- **Suma:** TVA dedusă × valoarea rămasă neamortizată / valoarea de intrare.
- **Cota:** cea în vigoare la data achiziției activului (pct. 80 alin. (6)), nu cota de azi.
- **La TVA la încasare:** se ajustează doar taxa plătită furnizorului (art. 306 alin. (2)).

::: ghid-exemplu
Exemplu istoric, pentru înțelegerea regulii: SC Exemplu SRL a cumpărat în decembrie 2014 un echipament de 10.000 lei. A dedus TVA de 2.400 lei, la cota de atunci. Durata de amortizare fiscală era de 4 ani (48 de luni), cu amortizare liniară din ianuarie 2015.

În iulie 2016 echipamentul trece la operațiuni scutite fără drept de deducere. Amortizate: 18 luni. Rămase: 30 de luni.

- Valoarea rămasă neamortizată: 10.000 × 30/48 = 6.250 lei.
- Ajustarea în favoarea statului: 2.400 × 6.250 / 10.000 = 1.500 lei, o singură dată.

Același eveniment apărut în 2019 sau mai târziu nu mai duce la nicio ajustare, pentru că echipamentul era complet amortizat.
:::

## Ce se greșește în practică

- Acestor active li se aplică cincimile din art. 305, deși regula lor specială e proporția valorii neamortizate.
- Ajustarea se calculează la cota actuală de TVA, nu la cea de la data achiziției.
- Se ajustează active complet amortizate, deși norma spune expres că nu se mai fac ajustări.
- Regula se aplică unor mijloace fixe cumpărate după 1 ianuarie 2016. Acelea sunt bunuri de capital după art. 305.

## Ce face iConta.eu

Registrul de mijloace fixe din iConta.eu arată, pentru fiecare activ, valoarea, amortizarea cumulată și valoarea rămasă. Mijloacele fixe preluate la migrare își continuă amortizarea de unde a rămas. Din acestea contabilul are baza de calcul a ajustării, dar aplicația nu calculează automat ajustarea TVA după art. 306. Suma rezultată se introduce manual pe rândurile de regularizare din decontul D300.

[iConta.eu](/)
