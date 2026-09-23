---
title: Ce bilanț se depune la lichidarea unui SRL?
description: O societate în lichidare nu depune S1005/S1003 în regimul obișnuit al firmei în funcțiune — legea prevede un regim distinct, cu termene diferite, iar în iConta.eu acest regim nu are azi un formular dedicat generat automat.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce bilanț se depune la lichidarea unui SRL?

O societate aflată în lichidare nu mai urmează termenul „obișnuit" al bilanțului anual (31 mai, respectiv 30 aprilie). Legea contabilității îi rezervă un regim distinct, cu componente și termene proprii.

## Temeiul legal

::: ghid-temei
„Prevederile alin. (1) se aplică și în cazul fuziunii, divizării și transformării, precum și în situația lichidării [...], caz în care situațiile financiare au aceleași componente cu situațiile financiare anuale."
— Legea contabilității nr. 82/1991, republicată, art. 28 alin. (1^1)

„Pe perioada lichidării, persoanele juridice aflate în lichidare [...] depun, în termen de 90 de zile de la încheierea fiecărui an calendaristic, la ANAF o raportare contabilă anuală, al cărei conținut se stabilește prin ordin al ministrului finanțelor publice."
— Legea contabilității nr. 82/1991, republicată, art. 36 alin. (3)
:::

Din text rezultă două situații diferite, ambele distincte de S1005/S1003 „normal":

- **Situațiile financiare de lichidare** propriu-zise (întocmite în vederea fuziunii, divizării, transformării sau lichidării) au aceleași componente ca situațiile financiare anuale obișnuite (art. 28 alin. (1^1)) și se depun „în condițiile prevăzute de reglementările contabile emise în acest sens" (art. 36 alin. (4)) — adică OMFP 897/2015, norme metodologice privind fuziunea, divizarea, dizolvarea și lichidarea.
- **Raportarea contabilă anuală pe perioada lichidării** — cât timp societatea rămâne în lichidare, la finalul fiecărui an calendaristic, cu termen fix de **90 de zile** de la încheierea anului (art. 36 alin. (3)), diferit atât de termenul de 31 mai/30 aprilie al firmelor în funcțiune, cât și de excepția de 150/120 de zile aplicabilă doar exercițiilor financiare necalendaristice.

Conținutul tehnic exact al Anexei nr. 1 la OMFP 897/2015 (formatul propriu-zis al acestor situații/raportări) nu a putut fi confirmat integral în sursele verificate — textul ordinului indică explicit că anexa „se publică" separat, achiziționabilă de la Monitorul Oficial, și nu e inclusă în mirror-ul consultat.

## Ce se greșește în practică

- Se așteaptă depunerea unui S1005/S1003 „normal", cu termenul de 31 mai/30 aprilie, deși societatea e deja în lichidare — termenul corect pentru raportarea anuală pe perioada lichidării este de 90 de zile de la sfârșitul anului calendaristic (nu de la data intrării în lichidare).
- Se confundă raportarea contabilă anuală pe perioada lichidării cu situațiile financiare de lichidare întocmite o singură dată, la închiderea efectivă a societății.

## Ce face iConta.eu

Trebuie spus deschis: modulul de lichidare din iConta.eu (funcționalitatea F057, `core/lichidare.py`) generează notele contabile aferente operațiunilor de lichidare — vânzarea activelor rămase și partajul către asociați (inclusiv impozitul pe câștigul din lichidare, calculat în regim de dividend) — dar **nu generează niciun formular sau document de raportare de bilanț de lichidare**. Componentele obligatorii de mai sus (situații financiare de lichidare sau raportarea anuală de 90 de zile) nu au azi un corespondent funcțional dedicat în aplicație; ele rămân, la acest moment, de întocmit separat, pe baza temeiului legal descris mai sus.

[iConta.eu](/)
