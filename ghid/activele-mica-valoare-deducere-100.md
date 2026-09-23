---
title: Activele de mică valoare - deducere 100% sau amortizare?
description: Ce se întâmplă fiscal cu un bun sub pragul mijlocului fix (5.000 lei din 2026) - deducere integrală la achiziție sau amortizare pe mai mulți ani - și cum decide iConta.eu între cele două fluxuri.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Activele de mică valoare - deducere 100% sau amortizare?

Un bun cu valoare mică (mobilier, un aparat electronic, o sculă) nu trebuie neapărat amortizat
ani de zile. Legea lasă contribuabilului o alegere pentru bunurile sub un anumit prag: cheltuială
integrală la achiziție, sau amortizare ca orice alt mijloc fix.

## Temeiul legal

::: ghid-temei
la data intrării în patrimoniul contribuabilului, are o valoare fiscală egală sau mai mare
decât suma de 5.000 lei; această limită se actualizată anual, în funcție de indicele de
inflație, prin hotărâre a Guvernului;

— Codul fiscal (Legea 227/2015), art.28 alin.(2) lit.b, forma consolidată la 25.02.2026 (modificată
prin OUG nr. 8/2026, publicată în M.Of. nr. 147/25.02.2026)
:::

::: ghid-temei
În cazul unei imobilizări corporale care la data intrării în patrimoniu are o valoare fiscală
mai mică decât limita stabilită prin hotărâre a Guvernului, contribuabilul poate recupera
aceste cheltuieli prin deduceri de amortizare, potrivit prevederilor prezentului articol.

— Codul fiscal (Legea 227/2015), art.28 alin.(21)
:::

Concret: un bun cu valoare **egală sau peste 5.000 lei** (pragul valabil de la 25.02.2026,
stabilit prin OUG 8/2026; anterior era 2.500 lei, conform HG 276/2013) intră **obligatoriu** ca
mijloc fix amortizabil, cu regimul de amortizare aplicabil categoriei lui.

Pentru un bun **sub acest prag**, legea dă contribuabilului o opțiune (alin.21): fie
înregistrarea integrală ca cheltuială deductibilă în luna achiziției (cel mai frecvent caz în
practică, pentru un obiect de inventar), fie tratarea lui ca mijloc fix și amortizarea pe
durata normală de utilizare — dacă firma preferă să eșaloneze cheltuiala.

## Ce se greșește în practică

- Se amortizează "din reflex" orice bun cumpărat, chiar dacă valoarea lui e sub prag și firma
  ar fi putut deduce integral cheltuiala imediat.
- Se deduce integral un bun care de fapt depășește pragul de 5.000 lei, tratându-l greșit ca
  obiect de inventar în loc de mijloc fix.
- Se ignoră faptul că pragul s-a schimbat pe parcursul anului 2026 (de la 2.500 la 5.000 lei,
  din 25.02.2026) și se aplică vechea limită unei achiziții făcute după această dată.

## Ce face iConta.eu

Pragul de încadrare ca mijloc fix nu e un literal fix în cod, ci se citește dintr-un registru
unic de cote (`plafon_mijloc_fix`), tocmai ca să nu apară divergențe când pragul se schimbă
legal — valorile din registru sunt 5.000 lei de la 25.02.2026 și 2.500 lei anterior.

Când înregistrați o achiziție ca **obiect de inventar** (`nota-obiect-inventar`, operație
achiziție), aplicația verifică automat pragul valabil la data achiziției și **refuză**
operațiunea dacă valoarea depășește pragul, cerând înregistrarea ca mijloc fix în locul
cheltuielii directe. Dacă alegeți în schimb să tratați un bun sub prag ca mijloc fix (opțiunea
din alin.21), acesta intră normal în registrul `Firma > Mijloace fixe`, cu amortizare calculată
pe metoda aleasă. Mijloacele fixe existente la 31.12.2025 cu valoare între 2.500 și 5.000 lei
nu se reclasifică retroactiv — se amortizează în continuare pe durata rămasă, conform regulii
tranzitorii din OUG 8/2026.

[iConta.eu](/)
