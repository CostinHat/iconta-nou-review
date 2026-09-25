---
title: "Cine amortizează amenajările făcute într-un spațiu închiriat?"
description: "Investițiile pe care le face chiriașul într-un spațiu luat cu chirie sunt mijloace fixe amortizabile distincte, iar amortizarea se face de chiriaș, nu de proprietar, potrivit Codului fiscal."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cine amortizează amenajările făcute într-un spațiu închiriat?

Când o firmă renovează sau amenajează un spațiu pe care îl are cu chirie, întrebarea „cine trece amenajarea la mijloace fixe și cine o amortizează" are un răspuns direct în Codul fiscal: investiția se amortizează de cel care a făcut-o, adică de chiriaș, chiar dacă bunul de bază (clădirea) rămâne în proprietatea locatorului.

## Temeiul legal

::: ghid-temei
„Sunt, de asemenea, considerate mijloace fixe amortizabile: a) investițiile efectuate la mijloacele fixe care fac obiectul unor contracte de închiriere, concesiune, locație de gestiune, asociere în participațiune și altele asemenea."
— Legea nr. 227/2015 (Codul fiscal), art. 28 alin. (3) lit. a) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Amenajarea sau investiția făcută de chiriaș într-un spațiu închiriat este **mijloc fix amortizabil de sine stătător**, separat de clădirea proprietarului.
- Amortizarea acestei investiții se înregistrează **la chiriaș** (cel care a suportat cheltuiala), nu la proprietarul imobilului — proprietarul nu a făcut investiția și nu are ce amortiza.
- Durata de amortizare se stabilește, în practică, în funcție de durata contractului de închiriere sau de durata normală de utilizare a categoriei de investiție, cea care se dovedește mai relevantă economic.
- Dacă la încetarea contractului investiția rămâne neamortizată integral și nu e recuperată de la proprietar, valoarea rămasă se tratează potrivit clauzelor contractuale (despăgubire, cesiune fără plată etc.), aspect care nu mai ține de regula de amortizare în sine.

## Ce se greșește în practică

- Se așteaptă ca proprietarul spațiului să înregistreze amenajarea făcută și plătită de chiriaș, pentru că el rămâne titularul clădirii — greșit, art. 28 alin. (3) lit. a) leagă amortizarea de cel care a suportat investiția.
- Amenajarea se trece direct pe cheltuieli, integral, în luna facturii, în loc să fie capitalizată ca mijloc fix și amortizată pe durata rămasă a contractului sau pe durata economică de utilizare.
- Se folosește aceeași durată normală de utilizare ca pentru clădire (de zeci de ani), deși investiția e legată de un contract de închiriere mult mai scurt.

## Ce face iConta.eu

La data acestui ghid, modulul de mijloace fixe din iConta.eu (`core/repo_mijloace_fixe.py`) permite înregistrarea oricărui mijloc fix cu cont de imobilizare, cont de amortizare, valoare și durată normală de funcționare, deci o amenajare la un spațiu închiriat poate fi introdusă ca mijloc fix distinct și amortizată normal, ca orice altă imobilizare. Aplicația nu are însă o categorie sau un flux dedicat special „investiție în activ închiriat" care să sugereze automat durata sau tratamentul — încadrarea corectă (mijloc fix separat, la chiriaș) rămâne o decizie a contabilului la introducerea datelor.

[iConta.eu](/)
