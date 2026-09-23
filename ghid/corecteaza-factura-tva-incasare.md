---
title: "Cum se corectează o factură cu TVA la încasare"
description: "Ce verifică aplicația la introducerea unei operațiuni de TVA la încasare și cum se corectează erorile de cotă sau de dată."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se corectează o factură cu TVA la încasare

Când o operațiune de TVA la încasare e respinsă sau are cota greșită, cauza e aproape întotdeauna una din datele obligatorii cerute de art. 291 alin. (5) — data faptului generator, ramura aleasă și, după caz, data documentului.

## Temeiul legal

::: ghid-temei
Art. 291 alin. (5) Cod fiscal: „În cazul operațiunilor supuse sistemului TVA la încasare, cota aplicabilă este cea în vigoare la data la care intervine faptul generator, cu excepția situațiilor în care este emisă o factură sau este încasat un avans, înainte de data livrării/prestării, pentru care se aplică cota în vigoare la data la care a fost emisă factura ori la data la care a fost încasat avansul." (`cod_fiscal_227_2015_consolidat.txt`, liniile 18151-18159)
:::

Legea distinge două situații pentru cota aplicabilă: regula generală (cota de la faptul generator) și excepția (cota de la data facturii sau a avansului, dacă acestea au fost emise/încasate înainte de livrare). Aplicarea greșită a acestei distincții e cea mai frecventă sursă de eroare de cotă într-o operațiune de TVA la încasare.

## Ce se greșește în practică

Modulul care calculează cota (`core/cota_tva_incasare.py`) refuză explicit patru situații, fiecare cu cod de eroare distinct:

1. lipsă dată a faptului generator;
2. ramura art. 291 alin. (5) nealeasă (nu s-a precizat dacă se aplică regula generală sau excepția);
3. lipsă dată document (factură/avans) pe ramura de excepție;
4. dată document ulterioară datei livrării — contradicție logică cu ramura de excepție aleasă.

O „corecție" a facturii, în majoritatea cazurilor, înseamnă completarea sau rectificarea uneia dintre aceste patru date/alegeri.

## Ce face iConta.eu

Ecranul „TVA la încasare (art. 282)" (rută `nota-tva-incasare`, categorie „TVA regimuri speciale") cere explicit: data operațiunii, sensul (încasare/plată), suma încasată cu TVA, data faptului generator, ramura art. 291 alin. (5) și, condiționat, data facturii/avansului. Textul de ajutor din ecran citează direct legea: „Cota de TVA e cea în vigoare la data livrării, nu la data încasării (art. 291 alin. 5 Cod fiscal)."

Aplicația **nu deduce automat** care document a fost emis primul — este o decizie de produs asumată explicit, pentru că o deducere automată „ar produce o cifră validă și falsă". Contabilul trebuie să aleagă manual ramura corectă; dacă alegerea sau datele sunt incomplete ori contradictorii, aplicația respinge operațiunea în loc să calculeze o cotă potențial greșită.

[iConta.eu](/)
