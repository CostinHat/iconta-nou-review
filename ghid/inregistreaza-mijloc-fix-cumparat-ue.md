---
title: "Cum se înregistrează un mijloc fix cumpărat din UE?"
description: "Un mijloc fix cumpărat de la un furnizor din UE, cu transport în România, e achiziție intracomunitară ca oricare alta — cu taxare inversă calculată automat —, dar contul contabil trebuie ales manual, cel de imobilizări, nu cel sugerat implicit pentru mărfuri."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se înregistrează un mijloc fix cumpărat din UE?

Faptul că bunul cumpărat e un mijloc fix, nu marfă de revânzare, nu schimbă regimul de TVA la achiziția intracomunitară — schimbă doar contul contabil în care intră.

## Temeiul legal

::: ghid-temei
„CF art. 268 alin. (1)-(3) lit. a) — Operațiuni impozabile; alin. (3) lit. a) — AIC de bunuri (altele decât mijloace de transport noi/accizabile) urmând unei LIC scutite.” — `cod_fiscal_227_2015_consolidat.txt` L16593-16626, dosarul F050.

„`achizitie_ic` (achiziție intracomunitară): câmpuri dată, valoare RON, cod TVA furnizor UE, nr. factură, furnizor, cont destinație (sugestie `371`), tip (bunuri/servicii), cotă TVA % (opțional, sugestie 21)...” — `static/js/ecrane/operatiuni_ecran.js`, dosarul F050.
:::

Ca la orice achiziție intracomunitară de bunuri: taxa se calculează prin taxare inversă (4426=4427), iar operațiunea intră în D390 la codul A. Diferența față de o achiziție de marfă e doar destinația contabilă — un mijloc fix nu intră în contul de mărfuri.

## Ce se greșește în practică

- Se lasă contul de destinație pe sugestia implicită a ecranului (`371`, mărfuri), gândită pentru bunuri de revânzare, fără să se schimbe manual la contul de imobilizări corespunzător.
- Se omite calculul taxării inverse pe motiv că „e o investiție, nu o marfă de vânzare” — regimul de TVA la AIC nu depinde de destinația bunului (marfă, imobilizare, consum propriu).
- Nu se verifică plafonul de 10.000 euro pentru achiziții intracomunitare de bunuri (art. 268 alin. (4) lit. b), cu detaliile de calcul la alin. (5)-(6)) — mijlocul fix intră în același cumul anual ca orice altă achiziție de bunuri, dacă firma e neplătitoare de TVA.

## Ce face iConta.eu

Ecranul de achiziție intracomunitară calculează automat taxarea inversă pe baza codului de TVA al furnizorului (prefixul e validat contra listei statelor membre, dar verificarea live în VIES nu e legată de acest ecran — e disponibilă la emiterea facturilor de vânzare, nu la înregistrarea celor primite). Contul de destinație are o sugestie implicită orientată spre mărfuri (`371`) — pentru un mijloc fix, contul corect de imobilizări se selectează manual, sistemul nu îl deduce automat din tipul bunului.

[iConta.eu](/)
