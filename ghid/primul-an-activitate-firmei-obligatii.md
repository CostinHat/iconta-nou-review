---
title: "Primul an de activitate al firmei: obligații pe lună"
description: "Ce trebuie să depună și să respecte, lună de lună, o firmă nou-înființată în primul an fiscal, de la înregistrarea contabilă până la declarațiile fiscale."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Primul an de activitate al firmei: obligații pe lună

Primul an de activitate al unei firme nu are un regim fiscal special declarat ca atare, dar concentrează mai multe termene care, pentru o firmă nouă, apar toate deodată: organizarea contabilității, opțiunea de impozitare, primele declarații fiscale și, dacă e cazul, înregistrarea în scopuri de TVA. Obligațiile diferă lună de lună, în funcție de regimul ales și de evenimentele care apar (angajare, prima factură, prima achiziție intracomunitară).

## Temeiul legal

::: ghid-temei
„Persoanele juridice române pot opta să aplice impozitul reglementat de prezentul titlu începând cu anul fiscal următor celui în care îndeplinesc condițiile de microîntreprindere prevăzute la art. 47 alin. (1). [...] Persoanele juridice române comunică organelor fiscale competente aplicarea sistemului de impunere pe veniturile microîntreprinderilor, până la data de 31 martie inclusiv a anului pentru care se plătește impozitul pe veniturile microîntreprinderilor."
— Legea 227/2015, art. 48 alin. (2) și art. 55 alin. (2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Reperele generale ale primului an, indiferent de regimul de impozitare:

- **La înființare** — organizarea contabilității (potrivit Legii 82/1991), deschiderea unui cont bancar, stabilirea vectorului fiscal la ANAF (impozit pe profit/microîntreprindere, TVA dacă e cazul, contribuții pentru salariați).
- **Din prima lună cu salariați** — înregistrarea contractului de muncă în REGES-ONLINE înainte de începerea activității salariatului și depunerea lunară a declarației unificate D112 (contribuții și impozit pe venituri din salarii).
- **Trimestrial** (pentru firmele nou-înființate, care aplică de regulă regimul microîntreprindere de la înființare) — declararea și plata impozitului pe veniturile microîntreprinderilor, cu declarația aferentă.
- **Dacă se depășesc plafoanele de la art. 47** (venituri peste 100.000 euro sau nu mai are salariat) — trecerea la impozit pe profit începe din trimestrul respectiv, cu obligații declarative diferite din acel moment.
- **Dacă se optează pentru TVA sau se depășește plafonul de scutire** — înregistrarea în scopuri de TVA și depunerea lunară/trimestrială a decontului de TVA (D300).

## Ce se greșește în practică

- Se presupune că firma nou-înființată nu are nicio obligație declarativă până la prima factură emisă, ignorând obligațiile care curg de la data înregistrării (de exemplu, declararea vectorului fiscal, chiar și „pe zero").
- Se confundă termenul de comunicare a opțiunii pentru microîntreprindere/profit (care, la firmele existente deja, e 31 martie) cu regula aplicabilă firmelor nou-înființate, care aplică de regulă regimul microîntreprindere încă din prima zi, fără să mai comunice o opțiune separată.
- Se angajează primul salariat fără să se verifice că înregistrarea în REGES-ONLINE trebuie făcută **cel târziu în ziua anterioară** începerii activității, nu ulterior.

## Ce face iConta.eu

iConta.eu ține evidența contabilă generală a firmei de la înființare, generează declarațiile fiscale (D100, D112, D300, D406 etc.) pe baza datelor introduse și semnalează, prin modulul de control fiscal (`core/control_fiscal_api.py`), obligațiile declarative datorate în funcție de vectorul fiscal configurat pentru firmă. La data acestui ghid, aplicația **nu are un „checklist" dedicat, pas cu pas, pentru primul an de activitate** — obligațiile lunii curente se văd în ecranul de control fiscal, dar planificarea integrată a primului an (de la înregistrare la primele declarații) rămâne un proces pe care contabilul îl gestionează folosind evidența contabilă generală oferită de aplicație.

[iConta.eu](/)
