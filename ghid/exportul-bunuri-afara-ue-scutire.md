---
title: "Exportul de bunuri în afara UE: scutire cu drept de deducere"
description: Livrarea de bunuri expediate în afara Uniunii Europene este scutită de TVA cu drept de deducere, dar scutirea se justifică doar cu dovada declarației vamale de export — nu se confundă cu validarea VIES de la livrările intracomunitare.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Exportul de bunuri în afara UE: scutire cu drept de deducere

Când bunurile părăsesc efectiv teritoriul Uniunii Europene, livrarea este scutită de TVA, dar cu **drept de deducere** — adică firma nu colectează TVA la vânzare, dar își păstrează integral dreptul de a deduce TVA aferentă achizițiilor legate de acele bunuri. Condiția de fond nu este cine e clientul, ci faptul că bunurile ies din UE și că acest lucru poate fi dovedit.

## Temeiul legal

::: ghid-temei
„Sunt scutite de taxă: a) livrările de bunuri expediate sau transportate în afara Uniunii Europene de către furnizor sau de altă persoană în contul său; ... b) livrările de bunuri expediate sau transportate în afara Uniunii Europene de către cumpărătorul care nu este stabilit în România sau de altă persoană în contul său [...]”

— Codul fiscal (Legea 227/2015 consolidat), art. 294 alin. (1) lit. a)-b)
:::

Spre deosebire de livrarea intracomunitară (LIC), unde scutirea depinde de un cod de TVA valid verificat în VIES, la exportul extracomunitar clientul poate fi orice persoană — inclusiv un consumator final, fără cod de TVA — pentru că regula nu ține de statutul fiscal al cumpărătorului, ci de traversarea efectivă a graniței UE și de dovada acesteia.

## Ce se greșește în practică

- Se caută, ca la o livrare intracomunitară, un cod de TVA valid al clientului verificat în VIES — la export extracomunitar acest lucru nu e relevant, condiția e dovada ieșirii bunurilor din UE.
- Se facturează cu TVA românesc "din prudență", deși scutirea se aplică de drept dacă bunurile ies din UE și există dovada corespunzătoare.
- Se emite factura de export fără să existe încă declarația vamală de export (DVE/EAD) care să justifice scutirea, riscând o reîncadrare ulterioară a operațiunii.

## Ce face iConta.eu

Ecranul „Export extracomunitar (DVE)" (categoria Operațiuni speciale > Extern) cere data, valoarea, țara clientului (obligatorie) și dovada exportului (DVE, câmp text) — nu cere și nu verifică un cod de TVA al clientului, pentru că nu e relevant la acest tip de operațiune. Fără dovada exportului, aplicația respinge operațiunea cu mesajul: „fara declaratia vamala de export (DVE) scutirea art. 294(1)a nu se justifica - factureaza cu TVA pana la obtinerea dovezii". Cu dovada introdusă, nota contabilă generată este simplă: contul de venit (implicit 707) = 4111 (client), doar cu valoarea bunurilor, fără nicio linie de TVA.

[iConta.eu](/)
