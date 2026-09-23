---
title: "De ce nu corespunde contul 281 cu registrul mijloacelor fixe?"
description: "Cea mai frecventă cauză: nota lunară de amortizare nu a fost generată pentru toate lunile, sau notele de casare/reevaluare stau ca ciorne nevalidate în Registrul jurnal."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# De ce nu corespunde contul 281 cu registrul mijloacelor fixe?

Un decalaj între soldul contabil al amortizării cumulate și ce arată registrul de mijloace fixe are, cel mai adesea, o explicație structurală, nu o eroare de calcul.

## Temeiul legal

::: ghid-temei
"La reevaluarea unei imobilizări corporale, amortizarea cumulată la data reevaluării este tratată în unul din următoarele moduri: [...] b) eliminată din valoarea contabilă brută a activului și valoarea netă, determinată în urma corectării cu ajustările de valoare, este recalculată la valoarea reevaluată a activului. Această metodă este folosită, deseori, pentru clădirile care sunt reevaluate la valoarea lor de piață." — OMFP 1802/2014, pct. 103 lit. b)
:::

Aplicația verifică explicit acest decalaj în contextul reevaluării: dacă soldul contabil real al contului de amortizare e mai mic decât ce calculează registrul, reevaluarea e refuzată, tocmai pentru că ar elimina o amortizare neînregistrată încă.

## Ce se greșește în practică

Se presupune că orice diferență între cont și registru e o eroare de calcul a motorului de amortizare, când de fapt cauza tipică e alta: fie nota lunară de amortizare nu a fost generată pentru toate lunile scurse, fie o notă de casare sau reevaluare stă încă drept **ciornă**, nevalidată în Registrul jurnal.

## Ce face iConta.eu

Nota lunară de amortizare trebuie generată explicit, lună de lună (o dată pe lună, aplicația refuză o regenerare pentru aceeași lună) — odată generată, ea e înregistrată direct cu status „validată", nu ca ciornă. Notele de casare și reevaluare, în schimb, sunt generate ca ciorne și nu ajung în soldul contabil real decât după validare separată din Registrul jurnal. În oricare din cele două situații, soldul contului de amortizare poate rămâne mai mic decât valoarea calculată de registru la aceeași dată — iar aplicația folosește exact acest control (soldul contabil vs. registrul) pentru a refuza o reevaluare care ar produce un cont de amortizare negativ silențios.

[iConta.eu](/)
