---
title: NIR pentru bunuri achiziționate de la furnizori din import
description: Achiziția de bunuri din import extracomunitar nu trece prin cronul RO e-Factura — se înregistrează direct din operațiunea „Import extracomunitar (DVI)”, indiferent dacă furnizorul are sau nu CUI.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# NIR pentru bunuri achiziționate de la furnizori din import

Dacă întrebarea pornește de la ideea că factura de la un furnizor din afara UE ar trebui să „apară” automat în aplicație, la fel ca o factură RO e-Factura primită prin SPV — răspunsul scurt e că nu, și motivul e structural, nu un bug.

## Temeiul legal

::: ghid-temei
„(1) Baza de impozitare pentru importul de bunuri este valoarea în vamă a bunurilor, stabilită conform legislației vamale în vigoare, la care se adaugă orice taxe, impozite, comisioane și alte taxe datorate în afara României, precum și cele datorate ca urmare a importului bunurilor în România, cu excepția taxei pe valoarea adăugată care urmează a fi percepută.
(2) Baza de impozitare cuprinde cheltuielile accesorii, precum comisioanele, cheltuieli de ambalare, transport și asigurare, care intervin până la primul loc de destinație a bunurilor în România, în măsura în care aceste cheltuieli nu au fost cuprinse în baza de impozitare stabilită conform alin. (1) [...]"

— Codul fiscal (Legea 227/2015 consolidat), art. 289 alin. (1)-(2)
:::

Achiziția de bunuri din import extracomunitar nu e o factură RO e-Factura: furnizorul e stabilit în afara UE, documentul relevant e declarația vamală de import (DVI), nu un XML transmis prin sistemul național. De aceea nu se așteaptă un „NIR” generat automat dintr-un flux de tip SPV.

## De ce nu vine din SPV / e-Factura

Sistemul RO e-Factura are ca element obligatoriu CIF-ul emitentului — în structura internă a facturilor primite prin SPV, câmpul furnizorului e definit ca obligatoriu completat. La un furnizor extracomunitar, acest CIF pur și simplu poate lipsi sau nu are formatul unui CUI românesc/UE — deci nu se poate reprezenta o achiziție de import prin același mecanism cu care intră facturile de la furnizorii cu CIF, care circulă prin RO e-Factura.

În plus, RO_CIUS (formatul facturii electronice din SPV) e un standard intern-românesc, aplicabil operațiunilor domestice — nu formatul în care circulă o achiziție extracomunitară. Din acest motiv, achiziția din import se introduce **direct de către contabil**, ca operațiune distinctă, nu ca rezultat al descărcării unei facturi din SPV.

Înregistrarea corectă a unei asemenea achiziții se face prin ecranul „Import extracomunitar (DVI)” (categoria Extern), unde se introduc valoarea în vamă, procentul taxei vamale, eventualele accize și cheltuieli accesorii, contul de destinație (de regulă 371) și cota de TVA aferentă operațiunii. Din aceste date rezultă automat taxa vamală, baza de TVA și nota contabilă corespunzătoare modului de plată a TVA (la vamă, prin certificat de amânare, sau — pentru neplătitori — ca și cost).

## Ce se greșește în practică

- Se așteaptă ca factura de import să apară singură în lista de „facturi primite prin SPV”, pentru că așa se întâmplă cu furnizorii interni — și se pierde timp căutând-o acolo.
- Se introduce prețul de pe factura externă a furnizorului ca bază de TVA, în loc de valoarea în vamă plus taxele și cheltuielile accesorii, care e baza legală reală.
- Se confundă declarația vamală de import (DVI) cu factura RO e-Factura — sunt documente și fluxuri diferite, care nu se substituie unul altuia.

## Ce face iConta.eu

Achiziția din import extracomunitar are un ecran dedicat, separat de mecanismul RO e-Factura: „Import extracomunitar (DVI)”. Nu există și nu a fost construită vreo legătură automată între acest ecran și cronul de descărcare a facturilor din SPV — cele două fluxuri sunt independente prin construcție, tocmai pentru că un furnizor extracomunitar fără CUI e imposibil de reprezentat corect în structura facturilor primite prin SPV. Rezultatul practic: contabilul introduce manual datele operațiunii, iar aplicația generează automat nota contabilă corectă, în funcție de statutul de plătitor de TVA și de existența certificatului de amânare.

[iConta.eu](/)
