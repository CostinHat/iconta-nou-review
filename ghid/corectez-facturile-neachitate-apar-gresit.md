---
title: "Cum corectez facturile neachitate care apar greșit ca stinse?"
description: "O factură marcată eronat ca încasată/plătită trebuie corectată la baza ei — documentul justificativ real, nu doar prin schimbarea unui status."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum corectez facturile neachitate care apar greșit ca stinse?

Se întâmplă frecvent, mai ales când reconcilierea cu extrasul bancar se face automat: o factură ajunge marcată drept „stinsă" (încasată sau plătită), deși în realitate suma respectivă vine de la alt partener sau acoperă o altă factură cu valoare identică. Corectarea nu înseamnă doar schimbarea unui status în ecran, ci refacerea legăturii dintre plata reală și factura corectă.

## Temeiul legal

::: ghid-temei
„(1) Orice operațiune economico-financiară efectuată se consemnează în momentul efectuării ei într-un document care stă la baza înregistrărilor în contabilitate, dobândind astfel calitatea de document justificativ. (2) Documentele justificative care stau la baza înregistrărilor în contabilitate angajează răspunderea persoanelor care le-au întocmit, vizat și aprobat, precum și a celor care le-au înregistrat în contabilitate, după caz."
— Legea contabilității nr. 82/1991, art. 6 (sursă: anaf_surse/legea_82_1991_consolidat.txt)
:::

Legea contabilității nu tratează explicit situația unei „stingeri" greșite generate de o reconciliere automată — dar principiul de mai sus e cel care se aplică direct: orice înregistrare, inclusiv marcarea unei facturi ca încasată, trebuie să corespundă unui document justificativ real. Dacă documentul (extrasul bancar) arată o altă realitate decât cea înregistrată, înregistrarea nu are acoperire legală și trebuie corectată.

- O factură devine „stinsă" corect doar când există un document real (extras bancar, chitanță, ordin de plată) care dovedește exact acea încasare/plată, nu doar o coincidență de sumă.
- Potrivirile automate pe sumă exactă pot greși atunci când doi parteneri au facturi de aceeași valoare sau când descrierea plății bancare nu conține CUI-ul plătitorului.
- Corectarea presupune anularea/reversarea înregistrării contabile generate din alocarea greșită și realocarea plății pe factura corectă — nu doar modificarea manuală a unui câmp de status.

## Ce se greșește în practică

- Se acceptă propunerea automată de reconciliere fără verificarea partenerului și a sumei rămase de încasat pe factura respectivă.
- Se modifică direct statusul facturii, fără să se corecteze și înregistrarea contabilă generată din alocare — rămân astfel două surse care nu se mai potrivesc.
- Nu se verifică dacă descrierea plății bancare conține datele de identificare ale plătitorului, deși potrivirea automată se bazează în primul rând pe acestea.

## Ce face iConta.eu

Verificarea codului sursă confirmă că iConta.eu are un motor de reconciliere bancară care încearcă, în ordine, potrivire exactă pe sumă, apoi combinații de facturi cu sumă egală și, în final, alocare FIFO pe facturile deschise ale partenerului identificat prin CUI. Documentele deja marcate „stinse" nu mai sunt căutate la o nouă potrivire — de aceea, dacă o factură a fost închisă greșit (de exemplu din cauza unei sume identice la alt partener sau a lipsei CUI-ului din descrierea plății), corectarea presupune reluarea alocării pentru linia din extras respectivă, cu selectarea manuală a facturii corecte, înainte de a contabiliza operațiunea.

[iConta.eu](/)
