---
title: Cum corectez retroactiv regimul fiscal aplicat greșit?
description: Peste perioade fiscale deja închise, corectarea regimului fiscal cere un pas suplimentar — redeschiderea perioadei, schimbarea vectorului, apoi închiderea la loc.
published: 2026-09-25
modified: 2026-10-13
poarta: v1
---

# Cum corectez retroactiv regimul fiscal aplicat greșit?

Corectarea propriu-zisă a câmpului din Vector fiscal e simplă — problema apare când perioadele afectate au fost deja închise, pentru că aplicația refuză să rescrie trecutul fără un pas explicit de redeschidere.

## Temeiul legal

::: ghid-temei
„În sensul prezentului titlu, o microîntreprindere este o persoană juridică română care îndeplinește cumulativ următoarele condiții, la data de 31 decembrie a anului fiscal precedent:”
— Codul fiscal (Legea 227/2015), art. 47 alin. (1) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))

„Dacă în cursul unui an fiscal o microîntreprindere realizează venituri mai mari de 100.000 euro, aceasta datorează impozit pe profit începând cu trimestrul în care s-a depășit această limită.”
— Codul fiscal (Legea 227/2015), art. 52 alin. (1) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))
:::

Regimul fiscal corect ține de aceste două articole (condițiile de încadrare ca microîntreprindere și ieșirea din regim în cursul anului). Regula descrisă mai jos e însă o **regulă de produs a iConta**, nu o prevedere legală: aplicația nu permite modificarea vectorului fiscal peste o perioadă fiscală deja închisă, tocmai pentru că declarațiile aferente au fost deja depuse și o schimbare silențioasă ar rescrie trecutul fără urmă.

Dacă firma nu are nicio perioadă fiscală închisă în intervalul afectat, corecția e o simplă resalvare a câmpului „regimul fiscal (Date firmă)” (sau a oricărui alt atribut al vectorului), cu validare imediată.

Dacă însă există cel puțin o perioadă închisă (chiar dacă nu toate din interval), aplicația refuză direct salvarea, cu un mesaj explicit care indică prima lună blocată și motivul: câmpul decide ce se datorează, iar pentru lunile închise declarațiile s-au depus deja. Calea de corecție e în trei pași, toți consemnați: redeschide perioada afectată (din ecranul Perioade blocate, cu motiv obligatoriu), schimbă vectorul la valoarea corectă, apoi închide perioada la loc.

Această regulă se aplică indiferent de direcția corecției (micro→profit sau profit→micro) și indiferent de care dintre cele patru atribute ale vectorului (regim fiscal, plătitor TVA, periodicitate, operațiuni IC) trebuie schimbat.

## Ce se greșește în practică

- Se încearcă modificarea directă a vectorului fără să se verifice întâi dacă există perioade închise în interval — aplicația refuză operațiunea, dar contabilul poate interpreta greșit refuzul ca un bug, nu ca o protecție intenționată.
- Se redeschide perioada, se schimbă vectorul, dar se omite închiderea la loc — lăsând perioada vulnerabilă la alte modificări neintenționate.
- Se presupune că schimbarea vectorului în iConta corectează automat și declarațiile deja depuse la ANAF — vectorul e o evidență internă, corectarea declarațiilor (rectificative) se face separat, direct la ANAF.

## Ce face iConta.eu

Regula (cod intern R46, aplicația) interoghează direct tabelul de perioade blocate ale firmei; dacă găsește orice perioadă închisă, salvarea vectorului e refuzată cu mesajul care indică prima lună blocată. Validarea e strictă și pe alte fronturi: schimbarea regimului fiscal la o firmă în partidă simplă (PFA/II) e refuzată explicit (PFA nu are regim micro/profit), la fel ca o valoare de regim în afara „micro"/"profit" la partidă dublă.

[iConta.eu](/)
