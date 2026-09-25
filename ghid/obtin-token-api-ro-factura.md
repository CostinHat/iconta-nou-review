---
title: "Cum obțin token pentru API RO e-Factura?"
description: "Cadrul legal al autorizării tehnice pentru accesul prin API la RO e-Factura și ce presupune, în practică, obținerea unui token de acces."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum obțin token pentru API RO e-Factura?

Accesul programatic la RO e-Factura nu se face cu o cheie API simplă, ca la multe servicii comerciale — se face prin autorizare OAuth2, pornind de la certificatul digital calificat al contribuabilului. Fără acest certificat, nu există token.

## Temeiul legal

::: ghid-temei
„(4) Procedura de utilizare şi funcţionare a sistemului naţional privind factura electronică RO e-Factura se aprobă prin ordin al ministrului finanţelor în termen de 15 zile de la data publicării prezentei ordonanţe de urgenţă în Monitorul Oficial al României, Partea I."
— OUG nr. 120/2021, art. 3 alin. (4) (sursă: anaf_surse/oug_120_2021.txt)
:::

Legea stabilește cadrul, dar lasă detaliile tehnice de autentificare — inclusiv mecanismul concret de emitere a token-urilor de acces — în seama unei proceduri aprobate prin ordin al ministrului finanțelor, actualizată periodic de ANAF pe măsură ce sistemul evoluează. Ce rezultă totuși clar din coroborarea cu art. 80 din Codul de procedură fiscală (identificarea electronică) este:

- Obținerea unui token de acces API pornește **obligatoriu** de la o autorizare făcută cu certificatul digital calificat al contribuabilului (persoană juridică sau PFA) — nu există o cale alternativă de autentificare pentru aceste categorii.
- Autorizarea inițială se face, tipic, printr-un flux de tip „consimțământ" în care contribuabilul, folosind certificatul, aprobă explicit accesul aplicației terțe la contul său SPV/e-Factura.
- Token-ul obținut are o durată de valabilitate limitată și trebuie reînnoit periodic — detaliile tehnice exacte (durate, limite de utilizare) sunt stabilite de ANAF prin proceduri tehnice, nu prin ordonanța de bază, și nu au fost identificate ca text de lege verbatim în sursele verificate pentru acest ghid.

## Ce se greșește în practică

- Se caută un „API key" static, ca la alte servicii web — RO e-Factura nu funcționează așa; accesul se bazează pe autorizare OAuth2 legată de identitatea fiscală a contribuabilului.
- Se presupune că un token obținut o singură dată rămâne valabil la nesfârșit — token-urile de acces au termene de expirare și trebuie reînnoite (refresh), proces care implică și el reguli tehnice specifice.
- Se încearcă autorizarea aplicației cu certificatul unei alte persoane decât titularul contului fiscal — autorizarea trebuie să vină de la reprezentantul legal sau împuternicitul cu drept de reprezentare pentru firma respectivă.

## Ce face iConta.eu

iConta.eu implementează fluxul de autorizare OAuth2 către ANAF în modulul `core/spv_conector.py`: contribuabilul autorizează, o singură dată, conectarea aplicației la contul său SPV, folosind certificatul digital calificat; iConta.eu primește și stochează criptat tokenul de acces, iar reînnoirea (refresh) se face automat, fără intervenție ulterioară din partea utilizatorului. Parametrii tehnici exacți (durate de expirare, limite de apeluri) sunt cei comunicați de ANAF prin documentația tehnică a sistemului, nu sunt stabiliți de iConta.eu, iar aplicația nu oferă un „token propriu" independent de autorizarea ANAF.

[iConta.eu](/)
