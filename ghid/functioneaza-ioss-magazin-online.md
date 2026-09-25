---
title: "Cum funcționează IOSS pentru un magazin online"
description: "Regimul IOSS (Import One Stop Shop) pentru vânzarea la distanță de bunuri importate din afara UE, sub 150 euro pe colet — cum simplifică TVA la import și declarația D399."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum funcționează IOSS pentru un magazin online

IOSS (Import One Stop Shop) rezolvă o problemă specifică magazinelor online care vând clienților din UE bunuri aduse din afara Uniunii: fără IOSS, fiecare colet cu valoare mică ar genera formalități vamale separate și TVA la import perceput la graniță, adesea de curier, cu costuri suplimentare pentru client. Cu IOSS, TVA-ul se colectează o singură dată, la vânzare, iar coletul trece vamal fără taxă suplimentară de import.

## Temeiul legal

::: ghid-temei
„În sensul prezentului articol vânzarea la distanță de bunuri importate din teritorii terțe sau țări terțe acoperă numai bunurile, cu excepția produselor care fac obiectul accizelor, în loturi cu o valoare intrinsecă de maximum 150 euro."
— Legea 227/2015, art. 315^2 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Cum funcționează, pas cu pas:

- Regimul se aplică doar bunurilor, altele decât cele accizabile, în transporturi (colete) cu valoare intrinsecă de până la 150 euro — peste acest prag, se aplică regulile obișnuite de import cu TVA și taxe vamale la graniță.
- Vânzătorul (sau intermediarul desemnat, dacă vânzătorul nu e stabilit în UE) se înregistrează pentru IOSS într-un singur stat membru, care devine statul membru de identificare — pentru un magazin online românesc, de regulă România.
- La vânzare, magazinul colectează TVA-ul direct de la client, la cota aplicabilă în statul membru de destinație a coletului — deci prețul afișat clientului include deja TVA-ul corect, fără surprize la livrare.
- Lunar, magazinul depune o declarație specială de TVA (D399, în România) care raportează, pe fiecare stat membru de consum, baza și TVA-ul colectat — declarația se depune **în euro**, indiferent de moneda de facturare către client.
- Coletele vândute prin IOSS trec vama fără perceperea unei taxe de import suplimentare de către curier, pentru că TVA-ul a fost deja achitat prin declarația IOSS a vânzătorului.

## Ce se greșește în practică

- Se presupune că IOSS se aplică oricărui produs sub 150 euro, ignorând excepția explicită pentru produsele accizabile (de exemplu alcool, tutun), care rămân supuse regulilor obișnuite de import indiferent de valoare.
- Se calculează plafonul de 150 euro pe factura totală a comenzii, când de fapt se raportează la valoarea intrinsecă a fiecărui **colet/transport**, nu la valoarea cumulată a unei comenzi trimise în mai multe pachete.
- Se depune declarația D399 în lei sau în moneda de facturare a clientului, deși legea cere declararea **în euro**, indiferent de moneda tranzacției.

## Ce face iConta.eu

iConta.eu poate genera declarația D399 pentru regimul IOSS, cu structura de câmpuri cerută de validatorul oficial ANAF (perioadă trimestrială declarată, stat membru de consum, cotă, bază și TVA). Ca și la D398, această declarație e **manuală**: aplicația nu ține evidența automată a vânzărilor IOSS pe colet și stat de consum, deci toate valorile trebuie introduse de contabil pe baza evidențelor magazinului online — iConta.eu nu importă automat comenzile dintr-o platformă de e-commerce pentru a le clasifica după regimul IOSS.

[iConta.eu](/)
