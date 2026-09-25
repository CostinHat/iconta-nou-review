---
title: "Cum trec de la normă de venit la sistem real în 2026?"
description: "Trecerea se face prin opțiune exprimată în Declarația unică, obligatorie pentru minimum 2 ani fiscali consecutivi, depusă până la termenul legal de depunere."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum trec de la normă de venit la sistem real în 2026?

Trecerea de la norma de venit la sistemul real nu e o simplă bifă administrativă — e o opțiune formală, cu efecte pe minimum doi ani fiscali, exercitată printr-un formular concret și un termen legal fix.

## Temeiul legal

::: ghid-temei
„Contribuabilii care obțin venituri din activități independente, impuși pe bază de norme de venit, au dreptul să opteze pentru determinarea venitului net în sistem real, potrivit art. 68."
— Codul fiscal (Legea 227/2015), art. 69^1 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„Opțiunea pentru determinarea venitului net anual în sistem real, inclusiv în cazul contribuabililor care încep activitatea în cursul anului fiscal, se exercită prin completarea Declarației unice privind impozitul pe venit și contribuțiile sociale datorate de persoanele fizice cu informații privind determinarea venitului net anual în sistem real și depunerea formularului la organul fiscal competent în termenul legal de depunere prevăzut la art. 122 alin. (3). În acest caz, perioada de 2 ani fiscali cuprinde anul fiscal de realizare a veniturilor pentru care se depune Declarația unică [...] prin care se exercită opțiunea și anul fiscal următor acestuia."
— Codul fiscal (Legea 227/2015), art. 69^1 alin. (3) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Pașii, așa cum rezultă din text:

- Opțiunea se exercită prin **completarea capitolului corespunzător sistemului real** din Declarația unică, nu printr-o cerere separată sau o notificare liberă.
- Formularul se depune la organul fiscal competent, **în termenul legal de depunere** al Declarației unice (art. 122 alin. (3) CF).
- Perioada obligatorie de 2 ani fiscali începe chiar cu anul pentru care se depune declarația prin care se exercită opțiunea, nu cu anul următor — deci un contribuabil care optează pentru 2026 rămâne la sistem real minimum până la finalul anului 2027.

## Ce se greșește în practică

- Se depune opțiunea în afara termenului legal de depunere a Declarației unice, ceea ce poate invalida trecerea pentru anul respectiv.
- Se presupune că opțiunea se poate retrage în același an dacă situația se dovedește dezavantajoasă — legea o face obligatorie pentru minimum 2 ani fiscali consecutivi.
- Se ignoră faptul că perioada de 2 ani include anul curent al opțiunii, nu doar anii următori, deci calculul corect al momentului la care se poate reveni la normă e adesea greșit.

## Ce face iConta.eu

iConta.eu **nu depune automat** opțiunea pentru sistem real și nu urmărește termenul legal de depunere a Declarației unice — aceste pași rămân sub controlul contabilului, care completează manual formularul oficial.

Modulul care generează Declarația unică (D212) în aplicație are secțiuni separate pentru cele două regimuri — capitolul de sistem real și capitolul de normă de venit — populate manual, cu datele deja calculate de contabil; aplicația **nu recalculează** cotele sau bazele de impozitare, doar emite structura XML pentru depunere.

[iConta.eu](/)
