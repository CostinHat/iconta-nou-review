---
title: "Ce fac la primirea deciziei de impunere după control"
description: "Termenele legale de plată și de contestare a unei decizii de impunere emise în urma unei inspecții fiscale, conform Codului de procedură fiscală."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce fac la primirea deciziei de impunere după control

O inspecție fiscală se încheie, de regulă, cu o decizie de impunere — actul prin care organul fiscal stabilește sumele suplimentare de plată. De la data comunicării acestei decizii curg două termene diferite, care nu trebuie confundate: termenul de plată și termenul de contestare.

## Temeiul legal

::: ghid-temei
„ART. 270 Termenul de depunere a contestației
(1) Contestația se depune în termen de 45 de zile de la data comunicării actului administrativ fiscal, sub sancțiunea decăderii.

ART. 156 Termenele de plată
(1) Pentru diferențele de obligații fiscale principale și pentru obligațiile fiscale accesorii, stabilite prin decizie potrivit legii, termenul de plată se stabilește în funcție de data comunicării deciziei, astfel:
a) dacă data comunicării este cuprinsă în intervalul 1 - 15 din lună, termenul de plată este până la data de 5 a lunii următoare, inclusiv;
b) dacă data comunicării este cuprinsă în intervalul 16 - 31 din lună, termenul de plată este până la data de 20 a lunii următoare, inclusiv."
— Legea 207/2015 (Codul de procedură fiscală), art. 270 alin. (1) și art. 156 alin. (1) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Din textul de mai sus rezultă două lucruri esențiale pentru contribuabilul care primește o decizie de impunere:

- **Termenul de plată** nu e fix la un număr de zile, ci depinde de jumătatea lunii în care a fost comunicată decizia: 1-15 → scadență pe 5 luna următoare; 16-31 → scadență pe 20 luna următoare.
- **Termenul de contestare este de 45 de zile** de la comunicare, sub sancțiunea decăderii — după acest termen, calea contestației administrative se pierde, indiferent cât de întemeiate ar fi obiecțiile.
- Cele două termene curg în paralel: depunerea unei contestații **nu suspendă automat** obligația de plată (suspendarea executării se solicită separat, potrivit art. 278 din același cod).
- Dacă actul nu conține toate elementele obligatorii prevăzute de lege (inclusiv mențiunea privind calea de atac), contestația poate fi depusă într-un termen extins, de 3 luni.

## Ce se greșește în practică

- Se așteaptă soluționarea contestației înainte de a plăti, presupunând (greșit) că depunerea ei oprește automat curgerea dobânzilor și penalităților.
- Se calculează termenul de plată ca „30 de zile de la comunicare" în loc de regula pe jumătăți de lună din art. 156 alin. (1).
- Se lasă contestația pe ultima sută de metri și se pierde termenul de 45 de zile din cauza unei erori de calendar (zile calendaristice, nu lucrătoare).

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu automatizează etapa de după finalizarea unui control fiscal**. Aplicația are un semafor de conformare fiscală (`core/control_fiscal_api.py`) care compară declarațiile datorate cu cele depuse și semnalează lipsurile, dar acesta funcționează *înainte* de un control, nu gestionează decizia de impunere, termenul de plată din art. 156 sau termenul de contestare din art. 270 — nu există în cod nicio funcție care să calculeze aceste termene sau să genereze o alertă la primirea unei decizii de impunere. Urmărirea acestor termene rămâne, pentru moment, responsabilitatea contabilului sau a angajatorului.

[iConta.eu](/)
