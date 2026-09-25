---
title: "Cum decid între lichidare și insolvență"
description: "Diferența legală dintre dizolvarea/lichidarea voluntară a unei firme și procedura de insolvență, cu temeiurile din Legea societăților și legea insolvenței."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum decid între lichidare și insolvență

Când o firmă își încetează activitatea, alegerea între lichidare voluntară și insolvență nu e o chestiune de preferință administrativă, ci una impusă de starea reală a patrimoniului firmei — legea le tratează ca două proceduri complet diferite, cu praguri și condiții distincte.

## Temeiul legal

::: ghid-temei
„Insolvența este acea stare a patrimoniului debitorului care se caracterizează prin insuficiența fondurilor bănești disponibile pentru plata datoriilor certe, lichide și exigibile și care se prezumă atunci când debitorul, după 60 de zile de la scadență, nu a plătit datoria sa față de creditor; prezumția este relativă."
— Legea nr. 85/2014, art. 5 pct. 29 (sursă: anaf_surse/legea_85_2014.html)
:::

Criteriul care separă cele două căi:

- **Lichidarea voluntară** (Legea nr. 31/1990, art. 227 și urm.) e opțiunea firmelor care își pot achita toate datoriile — dizolvarea se hotărăște de asociați, deschide procedura lichidării, iar societatea își păstrează personalitatea juridică doar pentru operațiunile lichidării, până la finalizarea ei (art. 233, sursă: anaf_surse/legea_31_1990_societatile.txt). E o procedură de închidere „pe curat", nu una declanșată de dificultăți financiare.
- **Insolvența** (Legea nr. 85/2014) e procedura la care firma **trebuie** să recurgă atunci când se află efectiv în starea descrisă mai sus: fonduri bănești insuficiente pentru datorii certe, lichide și exigibile, prezumate după 60 de zile de neplată de la scadență. Nu e o alegere „mai ușoară" decât lichidarea, ci o consecință a stării de fapt a patrimoniului.
- Diferența practică esențială: în lichidare, activele se valorifică și datoriile se sting **integral**, urmate de partajul eventualului surplus către asociați; în insolvență, dacă activele nu acoperă toate datoriile, procedura se poate transforma în **faliment**, cu satisfacerea creditorilor doar parțial, în ordinea de prioritate legală.
- O firmă aflată deja în insolvență/dizolvare are și un regim special de comunicare a actelor fiscale — acestea se transmit administratorului judiciar sau lichidatorului judiciar, nu direct firmei (Legea nr. 207/2015, art. 47 alin. (18), sursă: anaf_surse/legea_207_2015_consolidat.txt).

## Ce se greșește în practică

- Se începe procedura de lichidare voluntară pentru o firmă care, de fapt, nu-și poate acoperi toate datoriile din active — dacă în timpul lichidării se descoperă că activele nu ajung, procedura corectă e trecerea la insolvență, nu continuarea lichidării „pe datorie".
- Se confundă cele două proceduri ca fiind interschimbabile, alegând-o pe cea „mai simplă" administrativ, fără verificarea prealabilă a stării reale a patrimoniului (active vs. datorii certe, lichide, exigibile).
- Se ignoră prezumția de insolvență de la 60 de zile de neplată — chiar dacă firma consideră întârzierea „temporară", odată depășit acest termen, prezumția legală de insolvență operează, relativ, dar există.

## Ce face iConta.eu

La data acestui ghid, iConta.eu are un motor dedicat pentru monografia contabilă a **lichidării** voluntare (`core/lichidare.py`): valorificarea activelor, închiderea TVA și impozitelor curente, partajul către asociați, inclusiv impozitarea câștigului din lichidare. Procedura de **insolvență**, reglementată de Legea nr. 85/2014, nu are un modul dedicat în aplicație — ea se administrează, prin natura ei, prin administratorul judiciar/lichidatorul judiciar desemnat, în afara evidenței contabile curente din iConta.eu.

[iConta.eu](/)
