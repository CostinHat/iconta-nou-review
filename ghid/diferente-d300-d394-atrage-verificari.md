---
title: "Ce diferențe între D300 și D394 pot atrage verificări ANAF?"
description: "Nu orice diferență între D300 și D394 e o eroare — dar câteva tipare concrete de discrepanță (livrări scutite omise, achiziții IC dublate) chiar merită verificate."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce diferențe între D300 și D394 pot atrage verificări ANAF?

D300 și D394 nu trebuie să fie identice — au sfere diferite prin definiție. Dar există câteva tipare concrete de diferență care nu sunt „normale", ci semne ale unei clasificări greșite, exact genul de discrepanță pe care o verificare încrucișată a ANAF le poate observa.

## Temeiul legal

::: ghid-temei
„Nu se înscriu achiziţiile intracomunitare de bunuri şi servicii pentru care există obligativitatea înscrierii în declaraţia 390."
— OPANAF 2194/2025 (care modifică Anexa 2 a OPANAF 3769/2015), aplicabil operațiunilor derulate de la 1.08.2025 (sursă: anaf_surse/opanaf_2194_2025_d394.txt)
:::

Din regula de excludere de mai sus, aplicată corect, rezultă exact ce nu ar trebui să difere „nejustificat" între cele două declarații:

- o operațiune națională taxabilă care apare cu TVA în D300, dar lipsește complet din D394, fără să fie o achiziție intracomunitară (excepția expresă) — e un semnal real de verificat, nu o diferență structurală normală;
- o **livrare scutită la cotă 0**, către un partener cu CUI românesc valid, care apare în D300 dar lipsește din D394 — livrările scutite se declară în D394 indiferent de tipul partenerului, deci o astfel de omisiune iese în evidență la o comparație rând cu rând;
- exporturile (livrări către parteneri din afara UE, cotă 0) trebuie să apară în ambele declarații — în D300 la rândul de operațiuni scutite cu drept de deducere, în D394 ca operațiune de tip L/LS — o discrepanță aici e la fel de vizibilă.

## Ce se greșește în practică

- Se raportează o livrare scutită cu cotă 0 către un partener din România doar în D300, presupunând că, fiind cotă zero, nu are ce să apară separat în D394 — regula corectă cere includerea ei, indiferent de partener.
- Se compară direct totalul de TVA colectat din D300 cu totalul din D394, fără să se scadă întâi achizițiile și livrările intracomunitare (care apar diferit sau deloc în cele două formulare).
- Se presupune că o eroare mică, la o singură factură, „se pierde" în totalul general — dar o verificare pe fiecare cotă de TVA, nu doar pe total, poate scoate în evidență exact acest tip de discrepanță punctuală.

## Ce face iConta.eu

Generatorul D394 conține o reparație aplicativă documentată exact pe acest tip de discrepanță: o livrare cu cotă 0 către un partener din România cu CUI valid era, la un moment dat, ignorată tacit din D394 — reparată printr-o regulă care o reclasifică automat drept livrare scutită (tip LS), pentru că regulile validatorului oficial cer explicit ca o cotă 0 să fie declarată drept LS, indiferent de tipul partenerului. Regresia e apărată printr-un test dedicat.

Dincolo de acest caz specific, verificarea generală rămâne cea descrisă și pentru relația D300–D394 pe ansamblu: a doua cale de calcul independentă din aplicație recalculează totalurile pe cotă direct din liniile brute ale facturilor și blochează generarea la orice divergență cu generatorul principal — dar nu acoperă operațiunile manuale (bonuri/borderouri) și nu prinde o eroare de intrare comună ambelor căi de calcul.

[iConta.eu](/)
