---
title: "Ce normă de venit se aplică dacă PFA-ul are sediul într-un județ și lucrează în altul?"
description: "Norma de venit aplicabilă unei PFA se stabilește după locul desfășurării activității, nu după sediul declarat — ce spune Codul fiscal și ce înseamnă practic."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce normă de venit se aplică dacă PFA-ul are sediul într-un județ și lucrează în altul?

Codul fiscal leagă norma de venit de **locul desfășurării activității**, nu de sediul/domiciliul fiscal declarat al PFA-ului. Dacă o PFA are sediul înregistrat într-un județ, dar activitatea se desfășoară efectiv în alt județ, norma de venit aplicabilă este cea stabilită de direcția generală regională a finanțelor publice pentru locul unde activitatea se desfășoară efectiv.

## Temeiul legal

::: ghid-temei
„(1) În cazul contribuabililor care realizează venituri din activități independente, altele decât venituri din profesii liberale definite la art. 67 alin. (2), venitul net anual se determină pe baza normelor de venit de la locul desfășurării activității."
— Legea nr. 227/2015 (Codul fiscal), art. 69 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce rezultă din formularea legii:

- Criteriul legal este explicit „locul desfășurării activității", nu sediul social/profesional sau domiciliul fiscal al PFA-ului. Cele două pot să nu coincidă, iar legea nu lasă loc de opțiune: se aplică norma județului unde activitatea are loc.
- Direcțiile generale regionale ale finanțelor publice stabilesc și publică anual nivelul normelor de venit pe activități CAEN, la nivel de județ (art. 69 alin. (2)), inclusiv coeficienții de corecție care pot fi aplicați de contribuabil (art. 69 alin. (10)).
- Când o activitate se desfășoară efectiv în mai multe locații/județe, norma corectă rămâne cea a locului unde se realizează efectiv activitatea generatoare de venit — nu o medie sau norma sediului.

## Ce se greșește în practică

- Se aplică automat norma de venit publicată pentru județul de sediu/domiciliu fiscal al PFA-ului, fără a verifica dacă activitatea se desfășoară efectiv în alt județ, unde norma poate fi diferită (mai mare sau mai mică).
- Se presupune că norma de venit e unică la nivel național, deși ea diferă de la un județ la altul, în funcție de nivelul stabilit de fiecare direcție generală regională a finanțelor publice.
- Se omite documentarea locului real al desfășurării activității (contracte, facturi, puncte de lucru) în cazul unui control, când se poate cere justificarea normei aplicate.

## Ce face iConta.eu

La data acestui ghid, iConta.eu nu are un nomenclator încărcat cu normele de venit pe județe și activități CAEN și nu determină automat, în funcție de locul desfășurării activității, care normă se aplică unei PFA. Contribuabilul/contabilul trebuie să identifice manual norma de venit corectă (publicată de direcția generală regională a finanțelor publice competentă pentru locul activității) și să o introducă direct în declarație. Pentru PFA-urile în sistem real, aplicația oferă evidența operațiunilor prin `core/rip_api.py`, dar pentru cele la normă de venit nu există o funcționalitate specifică de localizare geografică a normei.

[iConta.eu](/)
