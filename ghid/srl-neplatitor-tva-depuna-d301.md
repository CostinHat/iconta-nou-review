---
title: Un SRL neplătitor de TVA trebuie să depună D301?
description: Da, dacă are achiziții intracomunitare de bunuri sau servicii — dar numai pentru lunile în care apar astfel de operațiuni; obligația nu e legată de forma juridică, ci de statutul de TVA și de tipul de achiziție.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Un SRL neplătitor de TVA trebuie să depună D301?

Da, dacă SRL-ul face achiziții intracomunitare — de bunuri, de mijloace de transport noi, sau de servicii de la un prestator stabilit în UE. Faptul că firma nu e plătitoare de TVA „obișnuită" (neînregistrată conform art. 316) nu o scoate din sfera obligațiilor de TVA pentru acest tip de operațiuni; îi schimbă doar declarația prin care le raportează.

## Temeiul legal

::: ghid-temei
„numai de către persoanele înregistrate conform art. 317 (...) dar care nu sunt înregistrate și nu trebuie să se înregistreze conform art. 316" — OPANAF 592/2016, Anexa 2, Instrucțiuni (condiția de depunere a Secțiunii 1)
:::

Norma leagă explicit obligația de statutul de TVA al firmei: un neplătitor de TVA „obișnuit" (art. 316), dacă are achiziții intracomunitare, se înregistrează special prin art. 317 și depune D301 — nu deconturile obișnuite de TVA, pe care nu le are cum depune fără să fie plătitor.

### Când se depune și când nu

- **Se depune** pentru fiecare lună în care apare o achiziție intracomunitară de bunuri (secțiunea 1), de mijloace de transport noi (secțiunea 2), sau de servicii de la un prestator din UE (secțiunea 4.1).
- **Nu se depune** pentru o lună fără nicio astfel de operațiune: „Decontul special se depune numai pentru perioadele în care ia naștere exigibilitatea taxei" (OPANAF 592/2016).
- **Nu se completează** dacă firma devine plătitoare de TVA prin art. 316 — atunci achizițiile intracomunitare trec la taxare inversă în D300, nu în D301.

### Ce declarație suplimentară poate apărea

Dacă operațiunea e o achiziție de bunuri sau un serviciu intracomunitar (nu mijloc de transport nou și nu una din situațiile de la art. 307 alin. (3)/(5)/(6)), aceeași operațiune intră și în D390 (declarația recapitulativă), conform art. 325 din Codul fiscal — obligatorie pentru orice persoană înregistrată prin art. 316 **sau** art. 317.

## Ce se greșește în practică

- Se presupune că „SRL neplătitor de TVA" înseamnă „fără nicio obligație de TVA" — fals pentru achizițiile intracomunitare, unde obligația trece la beneficiar.
- Se depune D301 lunar, din prudență, chiar și pentru lunile fără operațiuni — norma interzice explicit depunerea pe zero.
- Se completează D301, dar se omite D390, deși operațiunea (bunuri sau servicii intracomunitare) o cere pe amândouă.

## Ce face iConta.eu

La introducerea unei operațiuni D301, aplicația verifică vectorul fiscal al firmei: dacă firma e înregistrată ca plătitoare de TVA, introducerea e refuzată, cu mesajul că achiziția aparține D300. Pentru o firmă neplătitoare, câmpurile de țară și cod TVA ale furnizorului, dacă sunt completate, populează automat operațiunea corespunzătoare și în D390. Declarația nu se generează pentru o lună fără operațiuni introduse.

[iConta.eu](/)
