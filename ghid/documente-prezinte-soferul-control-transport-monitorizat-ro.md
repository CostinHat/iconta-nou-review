---
title: "Ce documente trebuie să prezinte șoferul la un control pentru un transport monitorizat RO e-Transport?"
description: "Șoferul prezintă documentele care însoțesc transportul (factură, aviz, CMR etc.) împreună cu codul UIT primit de la transportator, în format fizic sau electronic."
published: 2026-09-29
modified: 2026-09-29
poarta: v1
---

# Ce documente trebuie să prezinte șoferul la un control pentru un transport monitorizat RO e-Transport?

La control, șoferul trebuie să prezinte două lucruri împreună: documentele care însoțesc transportul bunurilor și codul UIT al transportului. Codul UIT poate fi pe hârtie sau pe telefon, dar trebuie să fie la șofer; nu e suficient ca firma să îl fi obținut în sistem.

Pentru cabinet, partea practică e lanțul de transmitere: firma-client care declară obține codul UIT, îl dă transportatorului, iar transportatorul îl dă șoferului. Dacă lanțul se rupe, amenda o poate primi fiecare verigă.

## Temeiul legal

::: ghid-temei
„(1) Conducătorul vehiculului de transport este obligat să prezinte, la solicitarea organelor competente din cadrul Agenției Naționale de Administrare Fiscală ori din cadrul Autorității Vamale Române, respectiv la solicitarea ofițerilor și agenților de poliție din cadrul Poliției Române, documentele care însoțesc transportul de bunuri care fac obiectul monitorizării prin sistemul RO e-Transport împreună cu codul UIT pus la dispoziție conform prevederilor art. 8^2 alin. (4) ."
— OUG 41/2022, art. 10 alin. (1) (sursă: anaf_surse/oug_41_2022.txt)

„(4) Operatorul de transport rutier este obligat să pună la dispoziția conducătorului auto codul UIT primit conform prevederilor art. 8 alin. (2) ."
— OUG 41/2022, art. 8^2 alin. (4) (sursă: anaf_surse/oug_41_2022.txt)

„12. identificarea prin cod UIT - deținerea și prezentarea codului UIT pe timpul transportului de către operatorul de transport rutier sau operatorul economic care transportă cu vehicule care îi aparțin bunuri în nume propriu, în format fizic sau electronic, împreună cu documentul care însoțește transportul bunurilor."
— OUG 41/2022, art. 2 pct. 12 (sursă: anaf_surse/oug_41_2022.txt)
:::

Ce are șoferul la el:

- **Documentele de însoțire a mărfii** — factura, avizul de însoțire, CMR-ul sau documentul vamal, după tipul operațiunii. Ordonanța nu le enumeră; sunt documentele care însoțesc în mod obișnuit transportul respectiv.
- **Codul UIT**, în format fizic sau electronic.
- **Dispozitivul de poziționare pornit**, pentru că șoferul trebuie să îl pornească înainte de începerea transportului pe teritoriul național și să îl oprească doar după livrare sau după ieșirea din țară (art. 8^3).

Lanțul codului UIT:

1. Utilizatorul care declară (furnizorul, beneficiarul, importatorul etc.) pune codul UIT la dispoziția transportatorului, direct sau prin organizatorul transportului, cel târziu la intrarea în țară sau la punerea în mișcare a vehiculului (art. 8 alin. (2)).
2. Transportatorul îl dă șoferului (art. 8^2 alin. (4)).
3. Șoferul îl prezintă la control, împreună cu documentele (art. 10 alin. (1)).

Nerespectarea art. 10 alin. (1) sau a art. 8^3 de către șofer se sancționează cu amendă de la 5.000 lei la 10.000 lei (art. 13^1 alin. (1) lit. d) și alin. (4)).

## Ce se greșește în practică

- Codul UIT e obținut de firmă, dar rămâne în e-mailul contabilului și nu ajunge la șofer.
- Șoferul are codul UIT, dar nu are documentele de însoțire, sau invers; legea le cere împreună.
- Se trimite transportatorului un cod UIT al altui transport sau unul expirat.
- Se crede că la transportul cu vehicule proprii nu e nevoie de cod UIT la șofer; operatorul economic care transportă în nume propriu îl deține și îl prezintă la fel.

## Ce face iConta.eu

Cardul e-Transport din iConta.eu generează XML-ul notificării în structura oficială v2 și verifică fereastra de timp a codului UIT. Aplicația nu transmite codul UIT către transportator sau șofer; comunicarea lui pe lanțul transportului rămâne în sarcina firmei-client.

[iConta.eu](/)
