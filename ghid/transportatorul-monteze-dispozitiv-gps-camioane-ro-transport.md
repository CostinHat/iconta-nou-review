---
title: "Transportatorul trebuie să monteze dispozitiv GPS pe camioane pentru RO e-Transport?"
description: "Da: operatorul de transport rutier echipează vehiculele cu terminal de poziționare prin satelit, cu excepția celor care transmit deja poziția prin dispozitivele proprii."
published: 2026-09-29
modified: 2026-09-29
poarta: v1
---

# Transportatorul trebuie să monteze dispozitiv GPS pe camioane pentru RO e-Transport?

Da. Pentru transporturile monitorizate prin RO e-Transport, operatorul de transport rutier trebuie să asigure transmiterea poziției vehiculului pe tot traseul. În acest scop echipează camioanele cu un dispozitiv de poziționare și transmisie de date prin satelit. Obligația nu se aplică vehiculelor care transmit deja poziția prin dispozitivele lor proprii, de exemplu printr-un sistem telematic montat din fabrică.

Contează în practică pentru că obligația aparține transportatorului, nu firmei care a declarat transportul și a obținut codul UIT. Amenda se aplică transportatorului chiar dacă declarația din sistem este corectă.

## Temeiul legal

::: ghid-temei
„(1) Operatorul de transport rutier este obligat să asigure transferul datelor curente de poziționare a vehiculului de transport, care fac obiectul declarației, pe toată durata traseului de transport al bunurilor care fac obiectul monitorizării prin Sistemul RO e-Transport. (2) Operatorul de transport rutier este obligat să echipeze vehiculele de transport cu dispozitive de tip terminal de telecomunicații care utilizează tehnologii de poziționare și transmisie de date prin satelit [...] (3) Prevederile alin. (2) nu se aplică în cazul în care datele de poziționare ale vehiculului de transport sunt transferate de dispozitivele acestuia."
— OUG 41/2022, art. 8^2 alin. (1)-(3) (sursă: anaf_surse/oug_41_2022.txt)
„e) nerespectarea de către operatorul de transport a prevederilor art. 8^2 ."
— OUG 41/2022, art. 13^1 alin. (1) lit. e) (sursă: anaf_surse/oug_41_2022.txt)
„(3) Contravențiile prevăzute la alin. (1) lit. c) și e) se sancționează cu amendă de la 10.000 de lei la 50.000 de lei în cazul persoanelor fizice sau cu amendă de la 20.000 de lei la 100.000 de lei în cazul persoanelor juridice."
— OUG 41/2022, art. 13^1 alin. (3) (sursă: anaf_surse/oug_41_2022.txt)
:::

Concret:

- **Cine are obligația:** operatorul de transport rutier, adică firma care efectuează transportul. Obligația nu revine, ca atare, expeditorului sau beneficiarului care doar a declarat transportul. Dacă firma își transportă singură bunurile, verifică dacă se încadrează în definiția operatorului de transport rutier de la art. 2 pct. 3.
- **Pentru ce vehicule:** vehiculele cu care se transportă bunuri monitorizate prin sistem, adică bunuri cu risc fiscal ridicat pe teritoriul național și transporturi rutiere internaționale (art. 1 alin. (2)).
- **Ce dispozitiv:** un terminal care transmite poziția prin satelit, pe care rulează modulele informatice ale sistemului. Potrivit art. 7, Centrul Național pentru Informații Financiare pune aceste module la dispoziție gratuit.
- **Excepția:** dacă vehiculul transmite poziția prin dispozitivele proprii, nu mai este nevoie de un terminal separat. Obligația de la alin. (1) rămâne: datele de poziționare trebuie să ajungă în sistem pe toată durata traseului.
- **Obligația legată:** transportatorul pune la dispoziția șoferului codul UIT primit (art. 8^2 alin. (4)).

::: ghid-exemplu
SC Exemplu SRL are 4 camioane și transportă pentru clienți bunuri cu risc fiscal ridicat. Două camioane au sistem telematic propriu care transmite poziția în RO e-Transport. Celelalte două nu au. Firma echipează cu terminal doar cele două camioane fără sistem propriu. Dacă un camion fără dispozitiv pleacă în cursă cu un cod UIT, firma riscă o amendă între 20.000 și 100.000 de lei, pentru că este persoană juridică.
:::

## Ce se greșește în practică

- Se crede că declarația cu cod UIT, depusă de furnizor sau de beneficiar, acoperă și partea de poziționare. Transmiterea poziției este o obligație separată a transportatorului.
- Se montează un terminal și pe vehicule care transmit deja poziția prin sistemul propriu, deși excepția de la alin. (3) le acoperă.
- Transportatorul nu verifică dacă dispozitivul a transmis poziția pe tot traseul. Legea cere transfer pe toată durata transportului, nu doar echiparea vehiculului.
- Se confundă sancțiunea transportatorului (art. 8^2) cu cea a șoferului care nu pornește sau oprește dispozitivul la momentele prevăzute (art. 8^3).

## Ce face iConta.eu

iConta.eu generează XML-ul notificării RO e-Transport (UIT) pe structura oficială, cu datele de transport, inclusiv numărul vehiculului. Aplicația nu transmite date de poziționare și nu verifică dacă vehiculele sunt echipate. Echiparea și funcționarea dispozitivelor rămân în sarcina transportatorului.

[iConta.eu](/)
