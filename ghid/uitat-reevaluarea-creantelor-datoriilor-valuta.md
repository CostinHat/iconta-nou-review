---
title: "Ce fac dacă am uitat reevaluarea creanțelor și datoriilor în valută la sfârșitul lunii?"
description: "Obligația reevaluării lunare a soldurilor valutare, ce riști dacă o omiți și cum recuperezi diferența în iConta.eu, în funcție de dacă luna e încă deschisă."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce fac dacă am uitat reevaluarea creanțelor și datoriilor în valută la sfârșitul lunii?

Reevaluarea lunară a soldurilor valutare nu e opțională — legea o cere explicit, la finalul fiecărei luni, pentru toate creanțele și datoriile în valută încă nedecontate. Dacă ai omis-o, răspunsul depinde de un singur lucru: dacă luna respectivă mai e deschisă în contabilitate sau ai închis-o deja.

## Temeiul legal

::: ghid-temei
„325. - (1) La finele fiecărei luni, creanțele și datoriile în valută se evaluează la cursul de schimb al pieței valutare, comunicat de Banca Națională a României din ultima zi bancară a lunii în cauză. Diferențele de curs înregistrate se recunosc în contabilitate la venituri sau cheltuieli din diferențe de curs valutar, după caz. (2) Pentru ultima zi a lunii se efectuează atât contabilizarea tranzacțiilor în valută, cât și evaluarea lunară la cursul Băncii Naționale a României [...]"
— OMFP 1802/2014, pct. 325 alin. (1) și (2) (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

- Obligația vizează **toate** soldurile monetare în valută încă deschise la finalul lunii: creanțe, datorii și disponibilități (conturi bancare, casierie în valută) — nu doar unele dintre ele.
- Cursul de referință e cel comunicat de BNR din **ultima zi bancară** a lunii, nu ultima zi calendaristică (dacă acestea diferă, ex. weekend sau sărbătoare legală).
- Reevaluarea și contabilizarea tranzacțiilor lunii se fac în aceeași zi — ultima zi a lunii — nu separat, la o dată ulterioară.
- Dacă ai omis reevaluarea, soldul din bilanț la finalul lunii rămâne exprimat la un curs vechi, ceea ce poate denatura atât rezultatul lunii, cât și eventualele raportări către bancă sau acționari bazate pe acele solduri.

## Ce se greșește în practică

- Se sare reevaluarea pentru soldurile mici, considerându-le nesemnificative — legea nu prevede un prag de minimis pentru pct. 325.
- Se face reevaluarea la o dată aleasă arbitrar în luna următoare, nu la cursul BNR din ultima zi bancară a lunii care se închide.
- Se reevaluează doar creanțele, uitând datoriile sau disponibilitățile în valută (conturi bancare, casierie).

## Ce face iConta.eu

Din ecranul **Operațiuni speciale → Reevaluare valuta**, introduci lista soldurilor (cont, valoare în valută, monedă, curs de evidență, tip), iar aplicația ia automat cursul BNR pentru fiecare monedă la data cerută și generează, prin `core/uc_tenants.py` (`reevaluare_valuta`), o singură notă contabilă cu toate diferențele calculate corect pe 665/765. Dacă ai uitat operațiunea și luna respectivă e **încă deschisă**, poți rula reevaluarea retroactiv, cu data de la finalul acelei luni — aplicația o acceptă. Dacă luna e deja **închisă**, ruta refuză nota nouă (constrângerea `_cere_luna_deschisa`) și returnează un mesaj de eroare clar, nu o eroare tehnică — în acest caz, corectarea se face pe altă cale contabilă (notă de corecție în luna curentă), decizie care rămâne a contabilului, nu automatizată de aplicație.

[iConta.eu](/)
