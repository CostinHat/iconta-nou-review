---
title: "Cum tratez comisionul unei platforme marketplace din UE?"
description: "Comisionul unei platforme marketplace stabilite în UE se declară diferit după cum firma ta e plătitoare sau neplătitoare de TVA — D300 la plătitor, D301 secțiunea 4.1 la neplătitor."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum tratez comisionul unei platforme marketplace din UE?

Comisionul reținut de o platformă de tip marketplace stabilită în Uniunea Europeană (de exemplu pentru intermedierea vânzărilor tale online) este un **serviciu primit de la un prestator UE**. Fiscal, locul unde se plătește TVA e România, indiferent unde e stabilită platforma.

## Temeiul legal

::: ghid-temei
„Locul de prestare a serviciilor către o persoană impozabilă (...) este locul unde respectiva persoană care primește serviciile își are stabilit sediul activității sale economice." — Codul fiscal, art. 278 alin. (2)

„Taxa este datorată de orice persoană impozabilă (...) care este beneficiar al serviciilor care au locul prestării în România conform art. 278 alin. (2) și care sunt furnizate de către o persoană impozabilă care nu este stabilită pe teritoriul României (...)" — Codul fiscal, art. 307 alin. (2)

Secțiunea 4.1 din formularul D301 (OPANAF 592/2016) privește „Achiziții de servicii intracomunitare, pentru care beneficiarul este obligat la plata TVA conform art. 307 alin. (2)", de la persoane impozabile care „nu sunt stabilite pe teritoriul României (...), dar care sunt stabilite în Comunitate" (OPANAF 592/2016, Anexa 2, instrucțiuni).
:::

Deoarece platforma e stabilită în UE, ești în cazul tipic de **taxare inversă**: tu, ca beneficiar din România, calculezi și declari TVA-ul, nu platforma. Ce declarație completezi depinde de statutul tău de TVA:

- **Plătitor de TVA (art. 316)** — comisionul intră în **decontul de TVA (D300)**, la rândul de colectat și cel de deductibil (taxare inversă), cu efect net zero. Nu se completează D301 pentru acest profil.
- **Neplătitor de TVA** — trebuie să te înregistrezi special conform **art. 317 Cod fiscal**, *înainte* de a primi serviciul, fără prag valoric. Comisionul se declară apoi prin **D301, Secțiunea 4.1 (tip 5)**, până la **25 a lunii următoare** celei în care ia naștere exigibilitatea.

Pentru un neplătitor înregistrat prin art. 317, operațiunea de tip 5 intră automat și în calculul secțiunii 4 (rollup obligatoriu 4.1 → 4, cerut de structura formularului) și, dacă declari și codul de TVA al furnizorului, apare automat și în **D390** (declarația recapitulativă), cu cod S — pentru că art. 325 Cod fiscal obligă la D390 orice persoană înregistrată conform art. 316 **sau** art. 317.

## Ce se greșește în practică

- Se completează D301 deși firma e deja plătitoare de TVA — cele două declarații (D300 la plătitor, D301 la neplătitor) sunt mutual exclusive pentru aceeași operațiune, nu se completează amândouă.
- Se amână înregistrarea specială art. 317 până la momentul declarării, deși trebuie făcută **înainte** de primirea primului serviciu de acest tip.
- Se depune D301 „pe zero" din prudență, deși legea spune explicit că decontul special se depune **numai** pentru perioadele în care ia naștere exigibilitatea taxei.
- Se ignoră legătura obligatorie cu D390 — un neplătitor înregistrat prin art. 317 cu operațiuni intracomunitare depune, de regulă, ambele declarații în aceeași lună, nu doar D301.

## Ce face iConta.eu

Dacă firma e **plătitoare de TVA**, comisionul se înregistrează cu taxare inversă în decontul de TVA (D300), la rândurile de colectat și deductibil, net zero.

Dacă firma **nu e plătitoare de TVA**, ecranul D301 permite introducerea operațiunii ca tip 5, cu câmpurile prevăzute de OPANAF 592/2016 (nr. document, dată, valută, valoare, curs, cotă, opțional țară/cod TVA furnizor). Aplicația **blochează explicit** introducerea unei operațiuni D301 dacă firma e deja plătitoare de TVA. Cota de TVA folosită la calcul e preluată automat, în funcție de perioadă (nu e fixă în cod). La generare, dacă completezi și codul de TVA al furnizorului, operațiunea apare automat și în D390, cu codul corect (S, pentru servicii de tip 5).

O limită de care trebuie să ții cont: generarea D301 este blocată dacă nu există nicio operațiune introdusă în luna respectivă — aplicația nu produce o declarație „pe zero". De asemenea, rectificarea unei D301 deja depuse nu este disponibilă din aplicație ca funcție dedicată — o eventuală corecție trebuie tratată separat de contabil.

[iConta.eu](/)
