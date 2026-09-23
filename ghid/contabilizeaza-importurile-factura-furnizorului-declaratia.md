---
title: "Cum se contabilizează importurile când factura furnizorului și declarația vamală au valori diferite?"
description: Baza de TVA la import se calculează exclusiv din valoarea stabilită în vamă (DVI), nu din valoarea facturii furnizorului — diferențele dintre cele două documente nu modifică baza de TVA.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se contabilizează importurile când factura furnizorului și declarația vamală au valori diferite?

Nu e o situație rară: valoarea de pe factura furnizorului extern și valoarea în vamă stabilită de autoritatea vamală (prin declarația vamală de import, DVI) pot diferi — din cauza cursului valutar folosit, a ajustărilor vamale sau a unor elemente incluse diferit în cele două documente. Pentru TVA, legea e clară asupra căreia dintre ele contează.

## Temeiul legal

::: ghid-temei
„(1) Baza de impozitare pentru importul de bunuri este valoarea în vamă a bunurilor, stabilită conform legislației vamale în vigoare, la care se adaugă orice taxe, impozite, comisioane și alte taxe datorate în afara României, precum și cele datorate ca urmare a importului bunurilor în România, cu excepția taxei pe valoarea adăugată care urmează a fi percepută.
(2) Baza de impozitare cuprinde cheltuielile accesorii, precum comisioanele, cheltuieli de ambalare, transport și asigurare, care intervin până la primul loc de destinație a bunurilor în România, în măsura în care aceste cheltuieli nu au fost cuprinse în baza de impozitare stabilită conform alin. (1) [...]"

— Codul fiscal (Legea 227/2015 consolidat), art. 289 alin. (1)-(2)
:::

Legea leagă explicit baza de impozitare de **valoarea în vamă**, stabilită conform legislației vamale — nu de valoarea înscrisă pe factura comercială a furnizorului. O diferență între cele două valori (de exemplu din cauza cursului de conversie folosit la vamă, diferit de cursul zilei facturii) nu se "corectează" în baza de TVA — se folosește valoarea oficială din DVI.

## Ce se greșește în practică

- Se calculează baza de TVA pornind de la valoarea facturii externe, convertită la cursul zilei facturii, ignorând valoarea stabilită efectiv în vamă.
- Se încearcă ajustarea ulterioară a bazei de TVA declarate, pe motiv că factura furnizorului arată altă sumă — legea cere valoarea vamală oficială, nu pe cea de pe factură.
- Se confundă diferența de valoare dintre factură și DVI cu o diferență de curs valutar propriu-zisă (relevantă pentru alte înregistrări contabile), deși pentru baza de TVA la import contează exclusiv valoarea vamală.

## Ce face iConta.eu

Câmpul „valoare vamală" de pe ecranul „Import extracomunitar (DVI)" se completează manual, independent de valoarea facturii furnizorului, pe baza declarației vamale de import. Motorul de calcul construiește baza de TVA exclusiv din acest câmp, la care adaugă taxa vamală (calculată ca procent din valoarea vamală), accizele și cheltuielile accesorii introduse — fără să facă referire la valoarea facturii externe. O eventuală diferență între factură și DVI rămâne o chestiune de evidență separată (de exemplu diferențe de curs valutar sau reconciliere cu furnizorul), care nu modifică baza de TVA calculată la import.

[iConta.eu](/)
