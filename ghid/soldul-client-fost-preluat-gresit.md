---
title: "Ce fac dacă soldul unui client a fost preluat greșit?"
description: "Cum se corectează în contabilitate o eroare privind soldul preluat al unui client, în funcție de semnificația și exercițiul financiar afectat."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce fac dacă soldul unui client a fost preluat greșit?

Un sold de client preluat greșit — fie la trecerea la un alt program de contabilitate, fie la o simplă introducere manuală — este o eroare contabilă în sensul legii, iar modul de corectare depinde de un singur criteriu: dacă eroarea privește exercițiul financiar curent sau unul deja închis, și dacă e semnificativă sau nu.

## Temeiul legal

::: ghid-temei
„66. [...] Erorile din perioadele anterioare sunt omisiuni și declarații eronate cuprinse în situațiile financiare anuale ale entității pentru una sau mai multe perioade anterioare rezultând din greșeala de a utiliza sau de a nu utiliza informații credibile care [...] a) erau disponibile la momentul la care situațiile financiare anuale pentru acele perioade au fost aprobate spre a fi emise; [...]
(2) Astfel de erori includ efectele greșelilor matematice, greșelilor de aplicare a politicilor contabile, ignorării sau interpretării greșite a evenimentelor și fraudelor.
67. - (1) Corectarea erorilor aferente exercițiului financiar curent se efectuează pe seama contului de profit și pierdere. (2) Corectarea erorilor semnificative aferente exercițiilor financiare precedente se efectuează pe seama rezultatului reportat (contul 1174 «Rezultatul reportat provenit din corectarea erorilor contabile»). (3) Erorile nesemnificative aferente exercițiilor financiare precedente se corectează, de asemenea, pe seama rezultatului reportat. Totuși, potrivit politicilor contabile aprobate, erorile nesemnificative pot fi corectate pe seama contului de profit și pierdere."
— OMFP nr. 1.802/2014, Reglementări contabile privind situațiile financiare anuale individuale, pct. 66-67 (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

- **Eroare descoperită în același exercițiu financiar** în care s-a produs: se corectează direct, pe seama conturilor de venituri/cheltuieli sau prin stornarea și reînregistrarea corectă a soldului, fără să afecteze rezultatul reportat.
- **Eroare descoperită după închiderea exercițiului** (situațiile financiare ale anului respectiv au fost deja depuse): corectarea trece prin contul 1174 „Rezultatul reportat provenit din corectarea erorilor contabile", nu prin contul de profit și pierdere al anului curent — soldul corect al clientului nu trebuie să "polueze" rezultatul anului în care a fost descoperită eroarea.
- Excepție: dacă eroarea e nesemnificativă (nu ar influența deciziile utilizatorilor situațiilor financiare), politica contabilă a firmei poate permite corectarea ei direct pe rezultatul curent, chiar dacă privește un exercițiu anterior.
- Independent de tratamentul contabil, orice corecție de sold de client trebuie susținută de un document (notă contabilă, extras din vechea evidență, confirmare de sold) care explică de ce soldul inițial era greșit — nu se modifică o cifră fără urmă justificativă.

## Ce se greșește în practică

- Se corectează soldul greșit direct în soldul inițial al anului curent, fără notă contabilă și fără să se stabilească dacă eroarea e semnificativă sau nu — ceea ce face imposibilă reconstituirea ulterioară a corecției.
- Se trece o eroare din exercițiul anterior direct pe cheltuieli/venituri curente (cont 6xx/7xx), deși pentru erorile semnificative din exerciții închise legea cere trecerea prin rezultatul reportat (1174).
- Se ignoră impactul fiscal: o corecție de sold de client care modifică o creanță poate afecta baza de calcul a impozitului pe profit sau TVA aferentă unei perioade anterioare, ceea ce poate necesita și o declarație rectificativă, nu doar o notă contabilă.
- Se preia soldul greșit "ca atare" la migrarea într-un program nou, fără o reconciliere prealabilă cu fișa de cont sau balanța de verificare din sistemul vechi.

## Ce face iConta.eu

iConta.eu are un modul de import al soldurilor inițiale (balanță de deschidere), care permite introducerea sau corectarea conturilor analitice de clienți (inclusiv 4111) direct dintr-un fișier de balanță. Acest lucru face posibilă re-importarea unui sold corect atunci când cel preluat inițial a fost greșit. La data acestui ghid, aplicația **nu are o funcție dedicată de „corectare a erorilor contabile"** care să genereze automat înregistrarea prin contul 1174 pentru erori semnificative din exerciții închise — distincția între eroare curentă și eroare din exercițiu anterior, precum și înregistrarea contabilă corespunzătoare, rămân în sarcina contabilului.

[iConta.eu](/)
