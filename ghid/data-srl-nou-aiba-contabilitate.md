---
title: "De la ce dată trebuie un SRL nou să aibă contabilitate?"
description: "Momentul de la care ia naștere obligația legală de a organiza și conduce contabilitatea unei societăți comerciale nou-înființate, conform Legii contabilității."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# De la ce dată trebuie un SRL nou să aibă contabilitate?

„Nu am avut încă activitate, nu am nevoie de contabil" e o presupunere greșită frecventă la firmele nou-înființate. Obligația de a organiza și conduce contabilitatea nu depinde de existența unor operațiuni economice sau a unor venituri — ea ia naștere odată cu firma însăși.

## Temeiul legal

::: ghid-temei
„(1) Societățile comerciale, societățile/companiile naționale, regiile autonome, institutele naționale de cercetare-dezvoltare, societățile cooperatiste și celelalte persoane juridice au obligația să organizeze și să conducă contabilitatea financiară, potrivit prezentei legi."
— Legea contabilității nr. 82/1991, art. 1 alin. (1) (sursă: anaf_surse/legea_82_1991_consolidat.txt)
:::

Din text și din regulile corelate privind exercițiul financiar rezultă:

- Obligația de a organiza și conduce contabilitatea revine oricărei societăți comerciale **din chiar momentul dobândirii personalității juridice** (înmatricularea la registrul comerțului) — nu de la prima factură emisă, de la primul angajat sau de la depășirea unui prag de venituri.
- Exercițiul financiar al unei firme nou-înființate începe la data înființării, potrivit legii — deci și perioada pentru care trebuie ținută contabilitatea și întocmite situațiile financiare anuale pornește din aceeași zi, nu de la 1 ianuarie al anului respectiv.
- Chiar dacă firma nu are încă activitate economică (fără facturi emise, fără salariați), există totuși obligații contabile minime — de exemplu înregistrarea capitalului social vărsat, a cheltuielilor de constituire, a eventualelor conturi bancare deschise.
- Lipsa de activitate nu echivalează cu lipsa obligațiilor de raportare — chiar și o firmă „adormită" trebuie să depună situații financiare anuale (eventual în formă simplificată, pentru firme fără activitate), potrivit acelorași reguli.

## Ce se greșește în practică

- Se amână contractarea unui serviciu de contabilitate până la prima factură emisă sau primul salariat angajat, deși obligația legală există din ziua înmatriculării.
- Se consideră că o firmă fără activitate nu are nicio obligație de raportare, deși legea prevede depunerea situațiilor financiare anuale indiferent de nivelul activității.
- Se confundă data începerii activității economice efective (prima vânzare, primul contract) cu data de la care începe exercițiul financiar și obligația contabilă, care e data înmatriculării.

## Ce face iConta.eu

La data acestui ghid, iConta.eu permite crearea profilului unei firme noi și organizarea evidenței contabile din prima zi de existență legală a acesteia, cu module pentru jurnal contabil, balanță și situații financiare (`core/jurnal_api.py`, `core/bilant_api.py`). Aplicația nu decide însă și nu verifică automat data reală a înmatriculării comparativ cu data de la care se introduc primele înregistrări — corectitudinea perioadei acoperite de evidența contabilă, de la data efectivă a înființării, rămâne o verificare a contabilului la configurarea firmei în aplicație.

[iConta.eu](/)
