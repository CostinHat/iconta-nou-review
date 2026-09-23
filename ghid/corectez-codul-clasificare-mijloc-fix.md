---
title: Cum corectez codul de clasificare al unui mijloc fix?
description: Odată aleasă, durata normală de funcționare rămâne fixă până la recuperarea integrală a valorii sau scoaterea din funcțiune (HG 2139/2004). Corectarea unui cod greșit deja folosit e o corecție de eroare, nu o simplă editare de câmp.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum corectez codul de clasificare al unui mijloc fix?

Ca și la GH-02664, subiectul ține de registrul de mijloace fixe (amortizare, impozit pe profit), nu de TVA. Ce se schimbă aici e situația: nu mai cauți codul pentru prima dată, ci corectezi unul greșit introdus deja.

## Temeiul legal

::: ghid-temei
**HG nr. 2139/2004, Catalogul privind clasificarea și duratele normale de funcționare a mijloacelor fixe, cap. II pct. 4**: „pentru fiecare mijloc fix nou achiziționat se utilizează sistemul unor plaje de ani cuprinse între o valoare minimă și una maximă... Astfel stabilită, durata normală de funcționare a mijlocului fix rămâne neschimbată până la recuperarea integrală a valorii de intrare a acestuia sau scoaterea sa din funcțiune.”
:::

## De ce contează momentul corecției

Dacă descoperi eroarea **înainte** să fi rulat vreo amortizare pe activul respectiv, corectarea codului (și, implicit, a duratei alese din plaja aferentă) e o simplă îndreptare de date, fără consecințe fiscale.

Dacă activul e **deja în amortizare**, cu note de amortizare deja contabilizate pe baza duratei greșite, corectarea nu mai e o editare simplă — durata folosită până acum a fost, potrivit catalogului, „fixă" pentru acel activ. O schimbare retroactivă a codului (deci a plajei de ani) e practic o corectare a unei erori contabile, cu regulile aferente (OMFP nr. 1802/2014 — distincția eroare semnificativă/nesemnificativă, corectare pe rezultatul curent sau pe rezultatul reportat), nu doar rescrierea unui câmp.

## Ce se greșește în practică

Se schimbă codul „din mers", direct în evidență, fără să se documenteze corecția ca eroare contabilă și fără să se recalculeze amortizarea deja înregistrată pe durata greșită — situație care iese la iveală abia la un control sau la reconcilierea D406.

## Ce face iConta.eu

Aici e limita reală, de precizat cinstit: **nu există în aplicație o acțiune dedicată de editare a unui mijloc fix deja introdus.** Singurele operațiuni disponibile pe un mijloc fix existent sunt reevaluarea (`urca_valoarea`, pentru majorarea valorii) și scoaterea din evidență (casare/vânzare) — nu și modificarea codului sau a duratei normale de funcționare pe un rând existent. Singura cale de introducere a mijloacelor fixe e importul de fișier CSV/XLSX (`POST /tenants/{id}/mijloace-fixe-import`), iar acest import **înlocuiește întregul registru al firmei** (șterge tot și reinserează din fișier), nu actualizează un singur rând.

Practic, astăzi, corectarea codului unui singur mijloc fix înseamnă reîncărcarea întregului fișier de mijloace fixe, cu valoarea corectată pe rândul respectiv și toate celelalte active reintroduse identic — o operațiune „totul sau nimic", nu o editare punctuală. Recomandăm verificarea atentă a fișierului întreg înainte de reîncărcare și, pentru un activ deja intrat în amortizare, tratarea corecției conform regulilor de corectare a erorilor contabile, nu ca o simplă modificare de câmp.

[iConta.eu](/)
