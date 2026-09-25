---
title: "Cum îmi planific bugetul pentru înființare și primul an"
description: "De ce primul exercițiu financiar al unei firme noi începe chiar la data înființării, nu la 1 ianuarie, și ce înseamnă asta pentru bugetul primului an."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum îmi planific bugetul pentru înființare și primul an

Un antreprenor la prima firmă tinde să gândească bugetul pe an calendaristic — de la 1 ianuarie. Legal însă, exercițiul financiar al unei firme nou-înființate începe exact din ziua înmatriculării, oricare ar fi aceasta, iar acest detaliu schimbă felul în care se planifică primele luni de activitate.

## Temeiul legal

::: ghid-temei
„(8) Exercițiul financiar al unităților nou-înființate începe la data înființării, potrivit legii."
— Legea contabilității nr. 82/1991, art. 27 alin. (8) (sursă: anaf_surse/legea_82_1991_consolidat.txt)
:::

Ce înseamnă, practic, pentru bugetul primului an:

- Primul exercițiu financiar nu ține 12 luni calendaristice pline, ci **de la data înmatriculării până la 31 decembrie** al aceluiași an — un SRL înființat în octombrie are un prim exercițiu financiar de doar câteva luni, cu obligații de raportare proporționale, nu anuale complete.
- Bugetul trebuie să includă, din prima lună, costurile fixe legate de obligația de a organiza și conduce contabilitatea (art. 1 din aceeași lege), indiferent de nivelul veniturilor — nu există o „perioadă de grație" în care firma nu are obligații contabile.
- Alegerea între impozitul pe veniturile microîntreprinderii și impozitul pe profit, precum și decizia de înregistrare în scopuri de TVA (obligatorie sau opțională), trebuie luate cât mai devreme, pentru că determină ce declarații și ce termene se aplică din prima lună de activitate, nu abia din anul următor.
- Cheltuielile de capital (aport la capitalul social, achiziții de mijloace fixe, stoc inițial) și cheltuielile curente (chirie, servicii de contabilitate, salarii, dacă e cazul) trebuie estimate separat, pentru că primele influențează bilanțul, iar celelalte rezultatul fiscal al primului exercițiu, oricât de scurt ar fi acesta.

## Ce se greșește în practică

- Se bugetează primul an ca și cum ar începe de la 1 ianuarie, ignorând faptul că exercițiul financiar real începe la data înmatriculării.
- Se amână contractarea unui serviciu de contabilitate până la primele venituri, deși obligația de a organiza și conduce contabilitatea există din prima zi de existență legală a firmei, indiferent de cifra de afaceri.
- Nu se estimează separat costurile fixe recurente (contabilitate, taxe bancare, eventuale abonamente software) de investițiile inițiale, ceea ce duce la subestimarea bugetului lunar din primele luni.

## Ce face iConta.eu

La data acestui ghid, iConta.eu oferă evidența contabilă generală pentru firme nou-înființate — jurnal, balanță, registre contabile (`core/jurnal_api.py`, `core/bilant_api.py`) — și calculează obligațiile fiscale datorate de la data înregistrării firmei, prin modulul de control fiscal (`core/control_fiscal_api.py`). Aplicația nu oferă însă un instrument dedicat de planificare bugetară sau de estimare a costurilor de înființare și ale primului an — ea intervine din momentul în care firma există și încep să fie introduse operațiuni economice, nu în etapa de planificare prealabilă înființării.

[iConta.eu](/)
