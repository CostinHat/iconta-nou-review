---
title: "Când se recalculează CMP-ul?"
description: "Momentul exact în care se recalculează costul mediu ponderat al unui stoc, conform OMFP 1802/2014 și modului de calcul folosit efectiv de iConta.eu."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Când se recalculează CMP-ul?

Costul mediu ponderat (CMP) nu este o valoare fixă, stabilită o singură dată la începutul lunii — el se schimbă de fiecare dată când intră marfă sau materie primă nouă în gestiune, la un preț diferit de cel existent deja în stoc. Întrebarea „când anume" recalculează sistemul acest cost are un răspuns clar atât în lege, cât și în motorul de calcul folosit de aplicație.

## Temeiul legal

::: ghid-temei
„(2) Metoda «costului mediu ponderat» (CMP) presupune calcularea costului fiecărui element pe baza mediei ponderate a costurilor elementelor similare aflate în stoc la începutul perioadei și a costului elementelor similare produse sau cumpărate în timpul perioadei. Media poate fi calculată periodic sau după fiecare recepție. Perioada de calcul nu trebuie să depășească durata medie de stocare."
— OMFP 1802/2014, pct. 96 alin. (2) (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

- Legea nu impune un singur moment de recalcul: permite explicit **două** variante — recalcul **periodic** (de exemplu lunar) sau recalcul **după fiecare recepție** (adică după fiecare intrare de marfă).
- Singura condiție e ca perioada aleasă pentru recalcul să nu depășească „durata medie de stocare" — practic, nu poți amâna recalculul ani de zile dacă marfa se învârte rapid prin gestiune.
- Alegerea între cele două variante ține de politica contabilă a firmei, nu de o obligație unică impusă de OMFP 1802/2014.

## Ce se greșește în practică

- Se presupune că „legea" ar cere obligatoriu recalcul după fiecare intrare — de fapt, varianta periodică (lunară) e la fel de legală.
- Se amestecă cele două variante în aceeași evidență (uneori recalcul la fiecare intrare, alteori doar lunar), ceea ce face fișa de magazie neconsecventă și greu de verificat.
- Se confundă recalculul CMP cu recalculul prețului de vânzare — CMP e un cost intern de evidență a stocului, nu prețul afișat clientului.

## Ce face iConta.eu

Motorul de stocuri cantitativ-valorice al iConta.eu (`core/stocuri_cv.py`) implementează exclusiv varianta „**recalcul după fiecare intrare**": la fiecare mișcare de tip intrare, cantitatea și valoarea totală din stoc se actualizează, iar CMP-ul curent rezultă din împărțirea valorii totale la cantitatea totală (`cmp_curent = val / cant`). Acest calcul e verificat direct în testele unitare ale aplicației, inclusiv un test dedicat exact recalculării CMP-ului după o intrare intermediară (zece bucăți la preț de 10, ieșire de cinci, apoi cinci bucăți noi la preț de 16 → CMP nou de 13, calculat ca medie ponderată pe stocul rămas plus intrarea nouă).

Important de precizat: aceasta este **alegerea implementată de iConta**, una dintre cele două variante permise de lege — nu singura variantă permisă de OMFP 1802/2014. Aplicația nu oferă o opțiune de recalcul periodic (lunar) pentru gestiunea cantitativ-valorică; dacă firma dorește varianta lunară, trebuie să folosească alt tip de evidență, nu modulul de stocuri cantitativ-valorice la CMP.

[iConta.eu](/)
