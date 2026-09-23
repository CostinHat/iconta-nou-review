---
title: "Cum se calculează costul mărfii cumpărate din UE?"
description: Costul mărfii cumpărate din UE se calculează la fel ca la orice altă achiziție — preț plus transport direct atribuibil — dar taxarea TVA prin taxare inversă cere o atenție separată, distinctă de calculul costului.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se calculează costul mărfii cumpărate din UE?

Costul de achiziție al mărfii cumpărate dintr-un stat membru UE se calculează după aceeași regulă generică valabilă pentru orice achiziție de stocuri — legea nu distinge după originea furnizorului. Ce diferă e regimul de TVA, care cere atenție separată dacă marfa e capitalizată prin același ecran folosit pentru costul accesoriu.

## Temeiul legal

::: ghid-temei
OMFP 1802/2014, Secțiunea 1.2, pct. 6: „costul de achiziție al bunurilor cuprinde prețul de cumpărare, taxele de import și alte taxe [...] cheltuielile de transport, manipulare și alte cheltuieli care pot fi atribuibile direct achiziției bunurilor respective."
:::

Definiția costului de achiziție nu distinge între furnizor intern, furnizor din UE sau import extracomunitar — costul include prețul de cumpărare plus cheltuielile direct atribuibile (transport, manipulare). Pentru o achiziție intracomunitară de bunuri (AIC), nu există taxe vamale (marfa circulă liber în UE), dar TVA se tratează prin **taxare inversă**: cumpărătorul înregistrează simultan TVA colectată și deductibilă (4426 = 4427), fără ca furnizorul UE să factureze TVA românesc.

## Ce se greșește în practică

- Se folosește ecranul de capitalizare a transportului pe NIR (gândit generic, pentru orice origine a mărfii) pentru o achiziție intracomunitară, iar nota de TVA generată automat presupune un furnizor intern care a facturat TVA (4426 = 401) — greșit pentru o AIC de bunuri, unde furnizorul UE nu facturează TVA românesc, iar tratamentul corect e taxarea inversă (4426 = 4427).
- Se așteaptă o factură cu TVA UE pe ea, deși furnizorul din alt stat membru, corect înregistrat pentru operațiuni intracomunitare, facturează fără TVA.
- Se dublează TVA-ul: se înregistrează taxarea inversă separat, corect, pentru achiziția intracomunitară, și apoi se introduce din nou marfa cu TVA suplimentară în ecranul NIR pentru capitalizarea transportului.

## Ce face iConta.eu

Achiziția intracomunitară de bunuri se înregistrează prin ecranul dedicat, ca sumă globală pe factură, cu taxare inversă generată automat (4426 = 4427) — acest ecran nu are linii de articole și nu repartizează nimic pe produse. Dacă firma vrea, în plus, capitalizarea proporțională a transportului pe articolele din NIR, cei doi pași nu sunt integrați automat: contabilul introduce transportul ca accesoriu în ecranul NIR (cu marfa introdusă la cotă 0 sau fără TVA suplimentară, ca să nu se dubleze TVA-ul deja tratat prin taxare inversă), iar nota de TVA a taxării inverse rămâne cea generată separat, prin ecranul de achiziții intracomunitare.

[iConta.eu](/)
