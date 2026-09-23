---
title: Ce diferențe între e-Factura și D394 pot genera notificări
description: Diferențele dintre facturile transmise prin RO e-Factura și cele declarate în D394 se pot verifica manual, în ecranul de control fiscal - dar, astăzi, nu generează o notificare proactivă (clopoțel) separată.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Ce diferențe între e-Factura și D394 pot genera notificări?

Titlul întrebării presupune că astfel de diferențe „generează notificări" automate. Răspunsul corect e mai nuanțat: diferențele pot fi identificate — și chiar sunt, printr-o confruntare deja construită în aplicație —, dar afișarea lor astăzi e o constatare pe care contribuabilul trebuie să o verifice activ, nu o alertă trimisă proactiv.

## Ce fel de diferențe apar, de fapt

Confruntarea reală se face între facturile transmise prin sistemul RO e-Factura, care au primit recipisă de acceptare din partea ANAF, și facturile declarate efectiv în D394 (declarația informativă privind livrările/prestările și achizițiile efectuate pe teritoriul național). Diferențele tipice, verificate una câte una, sunt:

- o factură transmisă și acceptată prin RO e-Factura, dar care nu apare deloc în D394 depus pentru aceeași perioadă;
- o factură inclusă în D394, dar fără corespondent transmis (sau acceptat) prin RO e-Factura;
- sume diferite între cele două surse pentru aceeași factură (eroare de raportare pe una din cele două căi).

Orice astfel de diferență e un semnal relevant pentru un eventual control — ANAF face, de altfel, propriile confruntări automate între sursele de date disponibile, exact pe acest tip de neconcordanțe.

## Ce se greșește în practică

- Se presupune că o factură emisă corect prin RO e-Factura ajunge automat, fără verificare, și în D394 — cele două fluxuri sunt generate separat și pot diverge din motive administrative (interval diferit de raportare, eroare de includere).
- Se verifică D394 doar la depunere, o singură dată, fără o reconciliere ulterioară cu ce a fost efectiv acceptat prin RO e-Factura — recipisa de acceptare poate întârzia sau poate lipsi pentru facturi incluse deja în declarație.
- Se așteaptă o notificare automată pentru asemenea diferențe, în loc de o verificare activă, periodică, înainte de un control — la acest moment, o asemenea notificare nu există în aplicație.

## Ce face iConta.eu

Ecranul de control fiscal al firmei include o confruntare dedicată, orizontală, între facturile transmise prin RO e-Factura (cu recipisă acceptată de ANAF) și facturile incluse în D394 depus, cu stări vizuale (verde/roșu/gri) pentru fiecare potrivire sau neconcordanță găsită. Această verificare se calculează însă doar la deschiderea ecranului — e o constatare pe cerere (pull), nu o alertă trimisă automat (push): la acest moment, diferențele identificate aici nu sunt incluse în lista de notificări proactive afișate în clopoțelul aplicației, care acoperă alte zone de conformare (TVA, D112, D390, cota de TVA). Recomandarea practică, până la o eventuală extindere a listei de notificări proactive, e verificarea periodică a acestui ecran — nu doar înainte de o depunere, ci și după ea.

[iConta.eu](/)
