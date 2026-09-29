---
title: "Reducere de preț acordată după schimbarea cotei de TVA: ce cotă și ce curs folosești la ajustare?"
description: "Cota, regimul și cursul operațiunii de bază care a generat reducerea; doar dacă operațiunea de bază nu se poate identifica se aplică cota și cursul de la data reducerii."
published: 2026-09-29
modified: 2026-09-29
poarta: v1
---

# Reducere de preț acordată după schimbarea cotei de TVA: ce cotă și ce curs folosești la ajustare?

La o reducere de preț acordată după livrare, ajustarea bazei de impozitare se face cu **cota de TVA, regimul de impozitare și cursul de schimb ale operațiunii de bază**, adică ale livrării inițiale. Cota în vigoare la data reducerii nu contează. O livrare facturată cu 19% înainte de 1 august 2025 se ajustează tot cu 19%, chiar dacă reducerea se acordă când cota standard este 21%.

Numai când operațiunea de bază nu poate fi identificată se aplică cota, regimul și cursul de la data la care intervine reducerea. De aceea, factura de reducere trebuie să trimită clar la factura sau facturile inițiale.

## Temeiul legal

::: ghid-temei
„În cazul evenimentelor menționate la art. 287 , taxa este exigibilă la data la care intervine oricare dintre evenimente, iar regimul de impozitare, cotele aplicabile și cursul de schimb valutar sunt aceleași ca și ale operațiunii de bază care a generat aceste evenimente."
— Codul fiscal (Legea 227/2015), art. 282 alin. (9) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„în cazul în care se acordă reduceri de preț după livrarea bunurilor sau prestarea serviciilor;"
— Codul fiscal (Legea 227/2015), art. 287 lit. c) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

::: ghid-temei
„(2) În aplicarea art. 282 alin. (9) din Codul fiscal, în cazul în care intervin evenimentele prevăzute la art. 287 din Codul fiscal, ulterior datei la care se modifică cota de TVA și/sau regimul de impozitare, pentru ajustarea bazei de impozitare sunt aplicabile cota și regimul de impozitare ale operațiunii de bază care a generat aceste evenimente. Pentru operațiunile a căror bază impozabilă este determinată în valută, cursul de schimb valutar utilizat pentru ajustarea bazei de impozitare este același ca al operațiunii de bază care a generat aceste evenimente, respectiv cursul de schimb valutar utilizat pentru determinarea bazei de impozitare a taxei pe valoarea adăugată pentru operațiunea de bază. Totuși, în cazul în care nu se poate determina operațiunea de bază care a generat aceste evenimente, se vor aplica cota de TVA și regimul de impozitare în vigoare la data la care a intervenit evenimentul și, corespunzător, și cursul de schimb valutar de la această dată, în cazul operațiunilor pentru care baza de impozitare este determinată în valută."
— Normele metodologice de aplicare a Codului fiscal (HG 1/2016), Titlul VII, pct. 25 alin. (2) (norme art. 282 alin. (9) CF) (sursă: anaf_surse/hg_1_2016_norme_cod_fiscal.txt)
:::

Ce înseamnă concret:

- **Exigibilitatea** ajustării este la data reducerii: reducerea se raportează în decontul perioadei în care e acordată.
- **Cota** este cea a livrării inițiale. Dacă reducerea privește facturi cu cote diferite, fiecare parte se ajustează cu cota proprie.
- **Cursul** este cel folosit la baza de impozitare a livrării inițiale în valută, nu cursul BNR din ziua reducerii.
- **Regimul** rămâne și el al operațiunii de bază. O livrare scutită sau cu taxare inversă se ajustează în același regim.
- **Excepția** se aplică doar când reducerea nu poate fi legată de nicio operațiune de bază identificabilă. Atunci se folosesc cota și cursul de la data acordării. Dacă reducerea poate fi repartizată pe facturile inițiale, se aplică regula generală.

::: ghid-exemplu
SC Exemplu SRL a facturat în iulie 2025 o livrare de 10.000 lei + TVA 19% (1.900 lei). În septembrie 2025, când cota standard este 21%, acordă clientului o reducere de 10% pentru aceeași livrare. Factura de reducere: bază −1.000 lei, TVA −1.000 × 19% = **−190 lei**, raportată în decontul lunii septembrie. Ajustarea cu 21% (−210 lei) ar fi greșită. Dacă livrarea fusese în euro, la curs 5,00 lei/euro, reducerea în euro se transformă tot la 5,00, nu la cursul din septembrie.
:::

## Ce se greșește în practică

- Se emite factura de reducere cu cota curentă (21%) pentru livrări facturate inițial cu 19%.
- În valută se folosește cursul BNR din data reducerii, iar ajustarea în lei nu mai corespunde livrării inițiale.
- Factura de reducere nu indică facturile de bază, deși reducerea putea fi atribuită unor livrări anume. Se pierde astfel dreptul de a aplica vechea cotă.
- Se raportează reducerea retroactiv, în decontul lunii livrării, în loc de perioada în care intervine.

## Ce face iConta.eu

În iConta.eu, stornarea unei facturi emise copiază cota de TVA de pe fiecare linie a facturii inițiale, cursul valutar al originalului și clasificarea ei. La stornare și la factura de reducere, aplicația verifică cota fiecărei linii față de cotele în vigoare la data operațiunii de bază, nu la data documentului de corecție (art. 282 alin. (9)), astfel încât un storno sau o reducere cu 19% pe o factură emisă înainte de 1 august 2025 este acceptat cu cota operațiunii de bază. Exigibilitatea rămâne la data documentului de corecție, iar în D300 ajustarea se raportează potrivit instrucțiunilor formularului. Verificarea cotei și a cursului rămâne a contabilului.

[iConta.eu](/)
