---
title: "Cum se înregistrează un mijloc fix importat din afara UE?"
description: Un mijloc fix cumpărat din afara UE se calculează fiscal la fel ca orice import — baza de TVA pornește de la valoarea în vamă, nu de la factura furnizorului —, doar contul de destinație diferă, de la marfă la imobilizare.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se înregistrează un mijloc fix importat din afara UE?

Regulile de TVA la import nu depind de natura bunului — marfă sau mijloc fix. Ce se schimbă la un mijloc fix este doar destinația contabilă a valorii de intrare (un cont de imobilizări, nu de stocuri), calculul TVA rămânând identic.

## Temeiul legal

::: ghid-temei
„(1) Baza de impozitare pentru importul de bunuri este valoarea în vamă a bunurilor, stabilită conform legislației vamale în vigoare, la care se adaugă orice taxe, impozite, comisioane și alte taxe datorate în afara României, precum și cele datorate ca urmare a importului bunurilor în România, cu excepția taxei pe valoarea adăugată care urmează a fi percepută.
(2) Baza de impozitare cuprinde cheltuielile accesorii, precum comisioanele, cheltuieli de ambalare, transport și asigurare, care intervin până la primul loc de destinație a bunurilor în România, în măsura în care aceste cheltuieli nu au fost cuprinse în baza de impozitare stabilită conform alin. (1) [...]"

— Codul fiscal (Legea 227/2015 consolidat), art. 289 alin. (1)-(2)
:::

Baza de TVA se calculează la fel indiferent de destinația bunului: valoare vamală + taxe vamale + accize (dacă e cazul) + cheltuieli accesorii până la primul loc de destinație din România. Peste această bază se aplică cota de TVA declarată pentru operațiune. Modul concret de tratare a TVA (plată la vamă cu deducere pe DVI, autolichidare prin certificat de amânare, sau cost nedeductibil pentru neplătitori) urmează aceleași reguli ca la orice alt import.

## Ce se greșește în practică

- Se calculează baza de TVA pornind de la valoarea facturii furnizorului extern, în loc de valoarea în vamă stabilită prin declarația vamală de import (DVI) — cele două pot diferi.
- Se folosește implicit un cont de stocuri/mărfuri pentru înregistrare, deși un mijloc fix intră pe un cont de imobilizări corespunzător.
- Se ignoră faptul că taxa vamală și cheltuielile accesorii (transport, asigurare) până la primul loc de destinație intră în baza de TVA — și, pentru neplătitorii de TVA, direct în costul de intrare al mijlocului fix.

## Ce face iConta.eu

Ecranul „Import extracomunitar (DVI)" (categoria Operațiuni speciale > Extern) e generic pentru orice tip de bun importat: nu există un ecran separat "import mijloc fix" — se folosește același motor de calcul. Câmpul de cont de destinație are o sugestie implicită (371, cont de mărfuri), dar contabilul poate alege orice alt cont, inclusiv un cont de imobilizări corespunzător tipului de mijloc fix. Restul mecanismului — calculul bazei de TVA din valoare vamală + taxe + accize + accesorii, modul de tratare a TVA în funcție de certificatul de amânare și statutul de plătitor, generarea notei contabile — rămâne identic celui aplicat oricărei alte operațiuni de import.

[iConta.eu](/)
