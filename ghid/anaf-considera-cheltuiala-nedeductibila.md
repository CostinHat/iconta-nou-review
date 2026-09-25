---
title: "Ce fac dacă ANAF consideră o cheltuială nedeductibilă?"
description: "Pașii legali după o decizie de impunere prin care ANAF respinge deductibilitatea unei cheltuieli: contestația administrativă, termene și organul competent."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce fac dacă ANAF consideră o cheltuială nedeductibilă?

Dacă, în urma unei inspecții fiscale, ANAF emite o decizie de impunere prin care recalifică o cheltuială drept nedeductibilă (și, implicit, majorează impozitul pe profit datorat), contribuabilul nu e obligat să accepte tacit concluzia. Legea îi dă dreptul la contestație administrativă — o cale de atac obligatorie înainte de a merge la instanță.

## Temeiul legal

::: ghid-temei
„(1) Împotriva titlului de creanță, precum și împotriva altor acte administrative fiscale se poate formula contestație potrivit prezentului titlu. Contestația este o cale administrativă de atac și nu înlătură dreptul la acțiune al celui care se consideră lezat în drepturile sale printr-un act administrativ fiscal. [...]
(3) Baza de impozitare și creanța fiscală stabilite prin decizie de impunere se contestă numai împreună."
— Legea 207/2015, art. 268 alin. (1), (3) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Pașii concreți, potrivit Codului de procedură fiscală:

- **Termenul de depunere**: 45 de zile de la data comunicării deciziei de impunere, sub sancțiunea decăderii (art. 270 alin. (1)) — termen strict, care nu se prelungește pentru simplul motiv că se pregătesc argumente suplimentare.
- **Forma contestației**: în scris, cu datele de identificare, obiectul contestației, motivele de fapt și de drept, dovezile pe care se întemeiază și semnătura contestatorului (art. 269 alin. (1)).
- **Unde se depune**: la organul fiscal emitent al actului atacat, care întocmește dosarul și îl înaintează, în cel mult 5 zile, organului de soluționare competent (art. 270 alin. (3)) — de regulă structura specializată de soluționare a contestațiilor din cadrul Ministerului Finanțelor (art. 272).
- **Contestația nu suspendă automat** obligația de plată a sumei stabilite prin decizie, decât dacă se solicită separat suspendarea executării, în condițiile legii contenciosului administrativ.
- Dacă respingerea contestației se menține, urmează calea instanței de contencios administrativ.

## Ce se greșește în practică

- Se depune contestația fără să se indice punctual sumele și măsurile contestate, individualizate pe categorii de creanțe fiscale — organul de soluționare poate cere, în 5 zile, precizarea sumei, iar lipsa răspunsului atrage considerarea contestat a întregului act.
- Se lasă termenul de 45 de zile să treacă, în așteptarea unor documente suplimentare sau a unei negocieri informale cu inspectorul — depășirea termenului atrage decăderea din dreptul de a mai contesta.
- Se contestă doar impozitul recalculat, fără a contesta și baza de impozitare din care rezultă — legea cere ca cele două să fie contestate împreună (art. 268 alin. (3)).

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu are un modul de gestionare a contestațiilor fiscale** — aplicația nu generează formularul de contestație, nu urmărește termenul de 45 de zile și nu ține un dosar al corespondenței cu structura de soluționare a contestațiilor. Modulul de control fiscal (`core/control_fiscal_api.py`) urmărește obligațiile declarative curente ale firmei, nu litigiile ulterioare unei inspecții. Redactarea și depunerea contestației, cu respectarea formei și termenului legal, rămân în sarcina contribuabilului sau a consultantului fiscal.

[iConta.eu](/)
