---
title: "Control ANAF pe e-Factura: ce verifică"
description: "Ce urmărește ANAF prin sistemul RO e-Factura și care este sancțiunea concretă pentru nerespectarea termenului de transmitere."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Control ANAF pe e-Factura: ce verifică

Sistemul RO e-Factura nu este doar un canal de transmitere a facturilor, ci și un instrument de control automatizat: fiecare factură transmisă este comparată, cronologic și valoric, cu termenul legal de emitere și cu termenul legal de transmitere în sistem. Depășirea termenului de transmitere este o contravenție de sine stătătoare, verificată direct din datele sistemului, fără să fie nevoie de o inspecție fiscală clasică la sediul firmei.

## Temeiul legal

::: ghid-temei
„Nerespectarea prevederilor alin. (6) pentru una sau mai multe facturi al căror termen-limită de transmitere în sistemul național privind factura electronică RO e-Factura intervine în cursul unei luni calendaristice constituie contravenție și se sancționează cu amendă de la 5.000 lei la 10.000 lei, pentru persoanele juridice încadrate în categoria contribuabililor mari, [...] cu amendă de la 2.500 lei la 5.000 lei, pentru persoanele juridice încadrate în categoria contribuabililor mijlocii, [...] și cu amendă de la 1.000 lei la 2.500 lei, pentru celelalte persoane juridice, precum și pentru persoanele fizice."
— Legea nr. 296/2023, art. LIX alin. (7) (sursă: anaf_surse/legea_296_2023_masuri_fiscal_bugetare_asigurarea_sustenabilitatii.txt)
:::

- Termenul de transmitere verificat de ANAF este de **5 zile lucrătoare de la data emiterii facturii**, dar nu mai târziu de 5 zile lucrătoare de la data-limită prevăzută pentru emiterea facturii conform Codului fiscal (art. LIX alin. (6) din aceeași lege).
- Amenda diferă în funcție de categoria contribuabilului (mare, mijlociu sau „celelalte persoane juridice și persoane fizice"), deci ANAF verifică inclusiv corecta încadrare a firmei în aceste categorii.
- Sancțiunea se aplică per lună calendaristică în care apare cel puțin o depășire de termen, nu per factură — dar practic sistemul semnalează fiecare factură cu termen depășit.
- Controlul automatizat pe e-Factura se corelează, din 2024, cu alte sisteme naționale de interes strategic (RO e-Transport, RO e-SAF-T, RO e-TVA), toate folosite de ANAF pentru a identifica neconcordanțe între ce se declară și ce circulă efectiv prin facturi.

## Ce se greșește în practică

- Se consideră că termenul de transmitere curge de la data facturării „reale" (de exemplu, data livrării), nu de la data-limită legală de emitere a facturii, care poate fi diferită.
- Se ignoră faptul că orice zi de întârziere peste termenul de 5 zile lucrătoare contează, chiar dacă factura a fost totuși transmisă până la finalul lunii.
- Se subestimează cumulul: mai multe facturi întârziate în aceeași lună generează o singură amendă „per lună", dar valoarea de plecare a acesteia poate escalada rapid dacă practica se repetă lună de lună.
- Se presupune greșit că neplata amenzii sau contestarea ei oprește obligația de transmitere corectă în continuare — obligația și sancțiunea sunt independente.

## Ce face iConta.eu

Din verificarea codului, iConta.eu are un modul complet de integrare cu RO e-Factura: generarea și validarea fișierului XML UBL (`efactura_send.py`), orchestrarea încărcării facturilor în sistemul ANAF (`efactura_trimitere.py`), iar urmărirea ulterioară a stării mesajului transmis (interogare `stareMesaj`) și descărcarea recipisei/confirmării se fac printr-un proces separat, rulat periodic (`spv_poll.py`), nu sincron la trimitere. Practic, aplicația vă ajută să respectați exact termenul de transmitere verificat de ANAF, semnalând facturile netrimise sau respinse. Aplicația nu execută însă un „control" propriu-zis în sensul de audit fiscal — rolul ei este să asigure transmiterea corectă și la timp, nu să simuleze verificarea pe care o face ANAF.

[iConta.eu](/)
