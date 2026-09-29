---
title: "Transport mixt cu bunuri cu risc fiscal ridicat și alte bunuri: se declară toată marfa în RO e-Transport?"
description: "Da. Dacă într-o partidă de bunuri sunt și bunuri cu risc fiscal ridicat, și alte bunuri, utilizatorul declară în RO e-Transport datele pentru toate bunurile din partidă."
published: 2026-09-29
modified: 2026-09-29
poarta: v1
---

# Transport mixt cu bunuri cu risc fiscal ridicat și alte bunuri: se declară toată marfa în RO e-Transport?

Da. Când într-o partidă de bunuri se transportă atât bunuri cu risc fiscal ridicat, cât și bunuri care nu sunt pe lista de risc, declarația din RO e-Transport cuprinde toate bunurile din partidă, nu doar pe cele cu risc. Nu se „separă" declarația pe categorii.

Pentru cabinet, regula contează la clienții care livrează pe teritoriul național marfă amestecată: un distribuitor de materiale de construcții, un angro alimentar, un furnizor de echipamente cu accesorii. O declarație care cuprinde doar produsele cu risc lasă în afara sistemului restul încărcăturii și expune firma la amendă.

## Temeiul legal

::: ghid-temei
„(1) În cazul în care în cadrul unei partide de bunuri sunt transportate atât bunuri cu risc fiscal ridicat, cât și alte bunuri care nu fac parte din categoria celor cu risc fiscal ridicat stabilite în acest sens prin ordin al președintelui Agenției Naționale de Administrare Fiscală, utilizatorii prevăzuți la art. 8 alin. (1) au obligația să declare în Sistemul RO e-Transport datele aferente transporturilor pentru toate bunurile transportate în cadrul unei partide de bunuri."
— OUG 41/2022, art. 12 alin. (1) (sursă: anaf_surse/oug_41_2022.txt)

„(2) În cazul în care din documentele deținute de către utilizatorii prevăzuți la art. 8 alin. (1) lit. d) nu rezultă încadrarea bunurilor transportate în una dintre categoriile de bunuri prevăzute la alin. (1) , aceștia au obligația declarării în Sistemul RO e-Transport a datelor aferente transporturilor pentru toate bunurile transportate în cadrul unei partide de bunuri."
— OUG 41/2022, art. 12 alin. (2) (sursă: anaf_surse/oug_41_2022.txt)
:::

Cum se aplică:

- **Unitatea de raportare e partida de bunuri**: un ansamblu indivizibil de bunuri cu același loc de încărcare și de descărcare, un singur utilizator declarant și un singur destinatar final (art. 2 pct. 5). Dacă în aceeași partidă există și un singur produs cu risc, se declară toată partida.
- **Partide diferite în același camion**: dacă în vehicul sunt mai multe partide (alt destinatar, alt loc de descărcare), regula se aplică fiecărei partide separat.
- **Depozitarul** (la bunurile în tranzit): dacă din documente nu rezultă încadrarea bunurilor, declară toată partida (art. 12 alin. (2)).
- **La transporturile internaționale** întrebarea nu se pune, pentru că acestea se declară oricum, indiferent de marfă (art. 1 alin. (2), art. 8^1).

Nerespectarea art. 12 se sancționează cu amendă de la 10.000 la 50.000 lei pentru persoane fizice sau de la 20.000 la 100.000 lei pentru persoane juridice (art. 13^1 alin. (1) lit. c) și alin. (3)).

::: ghid-exemplu
SC Exemplu SRL livrează unui client din Cluj, cu un singur camion și o singură factură, 10 tone de produse de pe lista bunurilor cu risc fiscal ridicat și 2 tone de accesorii care nu sunt pe listă. E o singură partidă (același loc de încărcare, același loc de descărcare, un singur destinatar), deci declarația cuprinde ambele poziții, cu cantitățile, greutățile și valorile fiecăreia.
:::

## Ce se greșește în practică

- Se declară doar pozițiile cu risc fiscal ridicat din factură, iar restul mărfii circulă fără date în sistem.
- Se împarte artificial încărcătura în două facturi pentru același destinatar și loc, ca să se evite declararea; partida se judecă după încărcare, descărcare și destinatar, nu după numărul facturii.
- Se omit bunurile fără cod tarifar de risc la declararea de către depozitar, deși documentele nu clarifică încadrarea.

## Ce face iConta.eu

Cardul e-Transport din iConta.eu generează XML-ul notificării în structura oficială v2 cu o listă de bunuri transportate, fiecare cu cod tarifar, denumire, cantitate, unitate de măsură, greutăți și valoare, deci o partidă mixtă poate fi declarată integral în aceeași notificare. Încadrarea fiecărui bun ca fiind cu risc fiscal ridicat sau nu rămâne verificarea contabilului.

[iConta.eu](/)
