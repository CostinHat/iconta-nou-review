---
title: "Ce termene are un contribuabil mijlociu în 2026"
description: "Ce înseamnă încadrarea la categoria „contribuabil mijlociu" și de ce termenele ei de declarare nu sunt stabilite direct în Codul de procedură fiscală, ci prin ordin ANAF."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce termene are un contribuabil mijlociu în 2026

Categoria de „contribuabil mijlociu" nu schimbă, prin ea însăși, termenele generale de declarare (D100, D112, D300 etc.) — aceleași termene din Codul de procedură fiscală și Codul fiscal se aplică oricărei firme, indiferent de mărime. Ce diferă e organul fiscal competent să administreze firma și criteriile care o încadrează în această categorie, stabilite de ANAF.

## Temeiul legal

::: ghid-temei
„(3) În scopul administrării de către organul fiscal central a obligațiilor fiscale datorate de contribuabilii mari și mijlocii, inclusiv de sediile secundare ale acestora, prin ordin al președintelui A.N.A.F. se poate stabili competența de administrare în sarcina altor organe fiscale decât cele prevăzute la alin. (1), precum și criteriile de selecție și listele contribuabililor care dobândesc calitatea de contribuabil mare sau, după caz, contribuabil mijlociu. (4) Organul fiscal central competent notifică contribuabilul ori de câte ori intervin modificări cu privire la calitatea de contribuabil mare sau, după caz, contribuabil mijlociu."
— Legea 207/2015 (Codul de procedură fiscală), art. 30 alin. (3), (4) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Ce rezultă din text:

- Legea **nu stabilește ea însăși** criteriile de încadrare la „contribuabil mijlociu" — le deleagă unui ordin al președintelui ANAF, care publică periodic listele contribuabililor mari și mijlocii și criteriile de selecție (de regulă, cifră de afaceri, active, număr de angajați).
- Efectul principal al încadrării e **administrativ**: contribuabilul mijlociu e administrat de o structură fiscală dedicată (direcție/administrație pentru contribuabili mijlocii), diferită de organul fiscal teritorial obișnuit — nu neapărat termene de declarare diferite.
- Firma trebuie **notificată** de organul fiscal ori de câte ori intervine o modificare a calității ei (intrare sau ieșire din categoria contribuabililor mijlocii) — încadrarea nu e permanentă și poate fi revizuită.
- Termenele concrete de depunere a fiecărei declarații (D100, D112, D300, D101 etc.) rămân cele generale din Codul fiscal și Codul de procedură fiscală — un contribuabil mijlociu nu are, doar prin acest statut, un calendar declarativ diferit de al unei firme mici, cu excepția eventualelor obligații suplimentare de raportare stabilite explicit pentru categoriile mari (de exemplu SAF-T, care se extinde pe categorii, cu date de referință proprii).

## Ce se greșește în practică

- Se caută în Codul de procedură fiscală un „calendar special" pentru contribuabilii mijlocii — termenele generale de declarare rămân aceleași; diferă administrarea, nu scadențele declarațiilor uzuale.
- Se ignoră notificarea oficială a schimbării de statut (art. 30 alin. (4)), continuând să se raporteze la organul fiscal vechi după ce firma a fost transferată la administrarea contribuabililor mijlocii.
- Se confundă termenul de depunere D406/SAF-T (care depinde de categoria de contribuabil, cu date de referință publicate separat) cu termenele generale ale celorlalte declarații, care nu depind de categorie.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu are o funcționalitate dedicată** categorisirii firmei ca „mare", „mijlociu" sau „mic" contribuabil și nu calculează diferit termenele de declarare în funcție de această categorie — nu am găsit în cod un asemenea mecanism în `core/control_fiscal_api.py`, modulul care calculează obligațiile și termenele declarative generale. Aplicația generează termenele uzuale (D100, D112, D300 etc.) pe baza tipului de decont și a datelor firmei, indiferent de categoria ei de mărime; verificarea calendarului specific SAF-T, legat de categoria de contribuabil, rămâne responsabilitatea contabilului.

[iConta.eu](/)
