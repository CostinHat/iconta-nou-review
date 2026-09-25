---
title: "Ce se întâmplă dacă nu răspund la solicitarea ANAF?"
description: "Nefurnizarea la termen a informațiilor periodice cerute de organul fiscal e o contravenție de sine stătătoare, cu amendă separată de orice altă sancțiune fiscală."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce se întâmplă dacă nu răspund la solicitarea ANAF?

O solicitare de informații venită de la ANAF nu e o simplă formalitate de ignorat — legea tratează separat, ca faptă contravențională de sine stătătoare, situația în care contribuabilul nu furnizează la termen informațiile pe care organul fiscal le cere periodic.

## Temeiul legal

::: ghid-temei
„(1) Constituie contravenții următoarele fapte [...]: h) nefurnizarea la termen de către contribuabil/plătitor a informațiilor periodice solicitate de organul fiscal potrivit art. 59; [...]
(2) Contravențiile prevăzute la alin. (1) se sancționează astfel: [...] c) cu amendă de la 12.000 lei la 14.000 lei pentru persoanele juridice încadrate în categoria contribuabililor mijlocii și mari și cu amendă de la 2.000 lei la 3.500 lei, pentru celelalte persoane juridice, precum și pentru persoanele fizice, în cazul săvârșirii faptei prevăzute la alin. (1) lit. e) - h)."
— Legea 207/2015 (Codul de procedură fiscală), art. 336 alin. (1) lit. h) și alin. (2) lit. c) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Ce rezultă din text:

- **Obligația de bază e cea de la art. 59 alin. (1)**: contribuabilul/plătitorul e obligat să furnizeze **periodic** organului fiscal central informații referitoare la activitatea desfășurată — e vorba de informații cerute cu caracter de regularitate, nu de o singură solicitare punctuală, izolată.
- **Sancțiunea e separată de orice altă amendă fiscală** — nefurnizarea la termen a acestor informații e o contravenție distinctă (lit. h)), cu amenda ei proprie: 12.000-14.000 lei pentru contribuabilii mijlocii/mari, 2.000-3.500 lei pentru restul persoanelor juridice și pentru persoanele fizice.
- **„La termen" e elementul central al faptei** — nu neapărat refuzul total de a răspunde, ci depășirea termenului stabilit pentru transmiterea informațiilor cerute, indiferent dacă acestea sunt ulterior furnizate.
- **Natura informațiilor și periodicitatea se stabilesc prin ordin al președintelui ANAF** (art. 59 alin. (4)), deci obligația concretă de răspuns depinde de ce anume prevede ordinul aplicabil pentru tipul de declarație/informație vizată.

## Ce se greșește în practică

- Se tratează orice solicitare venită de la ANAF ca având aceeași bază legală și același regim sancționator, deși legea distinge tipuri diferite de obligații de informare (furnizarea periodică de la art. 59, prezentarea de înscrisuri de la art. 64, informațiile pentru stabilirea stării de fapt fiscale de la art. 58), fiecare cu propria contravenție și propriul cuantum de amendă.
- Se ignoră termenul comunicat de organul fiscal, presupunând că un răspuns „dat până la urmă" anulează contravenția — fapta constă exact în depășirea termenului, indiferent de furnizarea ulterioară a informațiilor.
- Se confundă nefurnizarea informațiilor periodice cu neplata unei obligații fiscale — sunt fapte complet diferite, cu regimuri de sancționare separate, care pot totuși coexista la aceeași firmă.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu are o funcționalitate care să urmărească solicitările de informații primite de la ANAF** sau termenele de răspuns la acestea, conform art. 59. Aplicația generează și urmărește termenele declarațiilor fiscale periodice standard (D100, D112, D300 etc., prin `core/control_fiscal_api.py`), dar o solicitare punctuală venită direct de la organul fiscal, în afara acestor declarații standard, nu e captată sau semnalată de aplicație. Urmărirea și respectarea termenului de răspuns rămân, la acest moment, în sarcina contribuabilului.

[iConta.eu](/)
