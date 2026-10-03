---
title: "Cum se calculează salariul unui angajat care pleacă în mijlocul lunii?"
description: "Principiul plății proporționale cu timpul efectiv lucrat, din Codul muncii, aplicat la calculul salariului pentru o lună incompletă."
published: 2026-09-24
modified: 2026-10-03
poarta: v1
---

# Cum se calculează salariul unui angajat care pleacă în mijlocul lunii?

Codul muncii nu are un articol care să dea explicit o formulă de calcul pentru „salariul unei luni incomplete la încetarea contractului" — principiul aplicat vine dintr-o regulă înrudită, cea a plății proporționale cu timpul efectiv lucrat, redirecționăm onest spre acest temei, cu mențiunea limitării.

## Temeiul legal

::: ghid-temei
„Salariatul încadrat cu contract de muncă cu timp parțial se bucura de drepturile salariaţilor cu norma întreaga, în condiţiile prevăzute de lege şi de contractele colective de muncă aplicabile. [...] Drepturile salariale se acordă proporţional cu timpul efectiv lucrat, raportat la drepturile stabilite pentru programul normal de lucru."
— Legea nr. 53/2003 (Codul muncii), art. 106 alin. (1)-(2) (sursă: anaf_surse/legea_53_2003_codul_muncii.txt)
:::

Principiul din acest articol — plata proporțională cu timpul efectiv lucrat, raportată la programul normal de lucru — e cel aplicat în practică și pentru un salariat cu normă întreagă care încetează contractul în cursul lunii: salariul lunii respective se calculează proporțional cu zilele/orele efectiv lucrate din programul normal al lunii, nu integral.

Limitarea onestă: articolul citat vizează explicit contractul cu timp parțial, nu situația unei norme întregi întrerupte la mijlocul lunii de o încetare a contractului. Nu am găsit, în sursele verificate, un articol din Codul muncii care să reglementeze explicit acest al doilea caz cu o formulă proprie — practica de calcul (salariul lunar împărțit la numărul de ore/zile lucrătoare din lună, înmulțit cu orele/zilele efectiv lucrate) se sprijină pe principiul general al proporționalității, nu pe un text dedicat exact acestei situații.

## Ce se greșește în practică

- Se plătește salariul integral pe luna în care contractul a încetat la mijloc, din comoditate de calcul — principiul proporționalității cu timpul efectiv lucrat se aplică oricând norma nu a fost completă, indiferent de motiv.
- Se calculează proporția după zile calendaristice, nu după zilele lucrătoare din programul normal al lunii — cele două dau rezultate diferite, iar art. 106 alin. (2) raportează la „programul normal de lucru", nu la calendar.
- Se presupune că formula de calcul e aceeași indiferent de tipul de spor sau indemnizație — unele componente ale salariului pot avea reguli proprii de proporționalizare, diferite de salariul de bază.

## Ce face iConta.eu

iConta.eu calculează automat brutul cuvenit pentru luna de încetare, ca și pentru luna de angajare: numără zilele lucrătoare din fereastra în care contractul e în vigoare (de la prima zi a lunii sau data angajării, până la data încetării — inclusiv — sau ultima zi a lunii) și împarte salariul lunii la toate zilele lucrătoare ale lunii (fără weekend și sărbători legale). Zilele de concediu fără plată sau de suspendare înregistrate pe salariat ies din calcul, iar la o schimbare de salariu în cursul lunii fiecare zi primește salariul ei. Același calcul se folosește în statul de plată și în D112. Absențele marcate doar în pontaj nu reduc automat salariul de bază — ele se înregistrează ca suspendare dacă trebuie să afecteze brutul.

[iConta.eu](/)
