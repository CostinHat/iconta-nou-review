---
title: "Poate un magazin online să fie microîntreprindere?"
description: "Condițiile din Codul fiscal pentru încadrarea la impozitul pe veniturile microîntreprinderilor și de ce comerțul online nu e exclus din start."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Poate un magazin online să fie microîntreprindere?

Da. Un magazin online (comerț electronic, indiferent dacă vinde produse proprii sau doar intermediază) nu face parte din categoriile de activități excluse explicit de la impozitul pe veniturile microîntreprinderilor. Ca orice altă firmă, trebuie doar să îndeplinească condițiile generale de la art. 47 din Codul fiscal — nu există niciun regim special sau o interdicție pentru comerțul desfășurat printr-un site propriu.

## Temeiul legal

::: ghid-temei
„(1) În sensul prezentului titlu, o microîntreprindere este o persoană juridică română care îndeplinește cumulativ următoarele condiții, la data de 31 decembrie a anului fiscal precedent: [...]
c) a realizat venituri care nu au depășit echivalentul în lei a 100.000 euro [...];
d) capitalul social al acesteia este deținut de persoane, altele decât statul și unitățile administrativ-teritoriale;
e) nu se află în dizolvare, urmată de lichidare, înregistrată în registrul comerțului sau la instanțele judecătorești, potrivit legii;
g) are cel puțin un salariat [...];
h) are asociați/acționari care dețin, în mod direct sau indirect, peste 25% din valoarea/numărul titlurilor de participare sau al drepturilor de vot și este singura persoană juridică stabilită de către asociați/acționari să aplice prevederile prezentului titlu;
i) a depus în termen situațiile financiare anuale, dacă are această obligație potrivit legii.
(3) Nu intră sub incidența prezentului titlu următoarele persoane juridice române: [...] persoana juridică română care desfășoară activități în domeniul bancar [...] în domeniul asigurărilor și reasigurărilor [...] în domeniul jocurilor de noroc [...] de explorare, dezvoltare, exploatare a zăcămintelor de petrol și gaze naturale."
— Codul fiscal (Legea 227/2015), art. 47 alin. (1) lit. c), d), e), g), h), i) și alin. (3) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Un magazin online e o persoană juridică română obișnuită (de regulă SRL); intră sub incidența Titlului III „Impozitul pe veniturile microîntreprinderilor" ca orice altă firmă, dacă îndeplinește condițiile de mai sus.
- Lista de excluderi de la alin. (3) e limitativă și vizează domenii specifice (bancar, asigurări/reasigurări, jocuri de noroc, petrol și gaze), nu comerțul cu amănuntul sau comerțul electronic.
- Condiția de venituri (100.000 euro, verificată la 31 decembrie a anului precedent) se aplică la fel indiferent de canalul de vânzare — magazin fizic, marketplace sau site propriu.
- Condiția salariatului (lit. g) și cea a asociaților cu peste 25% (lit. h) se verifică identic, indiferent de obiectul de activitate.

## Ce se greșește în practică

- Se presupune greșit că „activitate online" sau „comerț electronic" ar fi un cod CAEN exclus automat de la regimul micro — nu există o asemenea excludere în lege.
- Se confundă condițiile de eligibilitate pentru microîntreprindere (art. 47) cu alte praguri fiscale (de exemplu plafonul de TVA de la art. 310), care sunt reglementate separat și au alte limite.
- Se ignoră condiția de la lit. h) — dacă asociatul deține peste 25% și în alte firme eligibile pentru micro, trebuie desemnată o singură persoană juridică pentru aplicarea regimului, până la 31 martie anul următor.
- Se uită condiția salariatului: un magazin online la început de drum, fără niciun angajat, nu îndeplinește lit. g) și nu poate aplica regimul micro, indiferent cât de mic e cifra de afaceri.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu are un verificator automat de eligibilitate pentru regimul de microîntreprindere** (nu am găsit în cod niciun modul care să calculeze pragul de 100.000 euro sau să verifice condițiile de la art. 47). Regimul fiscal (`regim_fiscal`) se stabilește ca dată introdusă de utilizator în profilul firmei, nu se derivă automat din venituri sau din structura asociaților. Există în schimb un modul separat, `categorie_marime.py`, care încadrează firma în categoria de mărime (micro/mici/mijlocii-mari) pentru situațiile financiare anuale — dar acesta e un concept contabil distinct (OMFP 1802/2014), nu regimul fiscal al microîntreprinderilor, și nu trebuie confundat cu el.

[iConta.eu](/)
