---
title: "Ce fac dacă am declarat operațiunea în luna greșită în D390?"
description: "Regula din Codul de procedură fiscală pentru corectarea declarațiilor informative, aplicată situației în care o operațiune intracomunitară a fost raportată în D390 pe altă lună decât cea corectă."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce fac dacă am declarat operațiunea în luna greșită în D390?

D390 este o declarație informativă, iar regimul de corectare al declarațiilor informative e mai permisiv decât cel al declarațiilor de impunere — fără restricția legată de rezerva verificării ulterioare sau de termenul de prescripție.

## Temeiul legal

::: ghid-temei
„(1) Declarația de impunere poate fi corectată de către contribuabil/plătitor, pe perioada termenului de prescripție a dreptului de a stabili creanțe fiscale.
(2) Declarația informativă poate fi corectată de către contribuabil/plătitor indiferent de perioada la care se referă.
(3) Declarațiile prevăzute la alin. (1) și (2) pot fi corectate prin depunerea unei declarații rectificative."
— Legea 207/2015 (Codul de procedură fiscală), art. 105 alin. (1)-(3) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

D390 (Declarația recapitulativă privind livrările/achizițiile/prestările intracomunitare) e o declarație informativă, nu o declarație de impunere — nu stabilește ea însăși o obligație de plată. Consecința practică a art. 105 alin. (2):

- Corecția se face prin **depunerea unei declarații rectificative** pentru luna greșită, în care operațiunea trecută eronat se elimină, și pentru luna corectă, în care operațiunea se adaugă.
- Spre deosebire de declarațiile de impunere (D300, D100 etc.), **nu există limitare la termenul de prescripție** — puteți corecta D390 „indiferent de perioada la care se referă", chiar dacă perioada respectivă ar fi, pentru alte tipuri de declarații, deja prescrisă.
- Corecția unei erori de lună afectează două declarații rectificative distincte: una pentru luna în care operațiunea a fost declarată greșit (se scoate) și una pentru luna corectă (se adaugă), nu o singură declarație „mutată".

## Ce se greșește în practică

- Se așteaptă un control ANAF pentru a semnala eroarea, deși art. 105 alin. (2) permite corectarea oricând, din inițiativa proprie, fără nicio restricție de termen.
- Se depune o singură declarație rectificativă, pe luna în care operațiunea ar fi trebuit raportată, fără să se corecteze și declarația lunii în care a fost raportată greșit — rezultatul e o operațiune dublată în evidența ANAF, nu una mutată.
- Se confundă regimul D390 cu cel al declarațiilor de impunere și se renunță la corectare din teama unei prescripții care, pentru declarațiile informative, nu se aplică.

## Ce face iConta.eu

La data acestui ghid, generatorul D390 al iConta.eu (`core/d390.py`) **emite doar declarații inițiale** — codul confirmă explicit că generatorul produce numai `d_rec="0"` (fără secțiunea de corecție), deci **nu generează automat declarații rectificative**. Contabilul trebuie să identifice manual cele două luni afectate (cea în care operațiunea a fost declarată greșit și cea corectă) și să depună rectificativele corespunzătoare prin canalul obișnuit de transmitere la ANAF.

[iConta.eu](/)
