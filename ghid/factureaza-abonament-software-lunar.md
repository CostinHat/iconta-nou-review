---
title: "Cum se facturează un abonament software lunar?"
description: "Regula fiscală pentru facturarea prestărilor de servicii continue, precum abonamentele software, și cum automatizează iConta.eu emiterea lunară a facturii."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se facturează un abonament software lunar?

Un abonament software (SaaS, mentenanță, licență cu plată periodică) e, din punct de vedere fiscal, o prestare de servicii cu caracter continuu, nu o livrare unică. Legea tratează separat momentul la care se consideră „efectuată" o astfel de prestare, iar acest moment determină și ritmul la care trebuie emisă factura.

## Temeiul legal

::: ghid-temei
„În cazul livrărilor de bunuri și al prestărilor de servicii care se efectuează continuu, altele decât cele prevăzute la alin. (7), cum sunt livrările de gaze naturale, de apă, de energie electrică, serviciile de telefonie, de închiriere, de leasing, de consesionare, de arendare de bunuri, de acordare cu plată pentru o anumită perioadă a unor drepturi reale, precum dreptul de uzufruct și superficia, asupra unui bun imobil, și alte livrări/prestări asemenea, se consideră că livrarea de bunuri/prestarea de servicii este efectuată la fiecare dată prevăzută în contract pentru plata bunurilor livrate/serviciilor prestate sau, în lipsa unei astfel de prevederi contractuale, la data emiterii unei facturi, dar perioada de decontare nu poate depăși un an."
— Cod fiscal (Legea 227/2015), art. 281 alin. (8) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Un abonament software se încadrează la „alte livrări/prestări asemenea" cu caracter continuu — nu la excepția de la alin. (7), care vizează servicii cu decontare pe bază de situații de lucrări (construcții, consultanță etc.).
- Momentul la care prestația „se consideră efectuată" e fie data de plată prevăzută în contract (de exemplu, ziua din lună la care se facturează abonamentul), fie, dacă nu există o astfel de clauză, data emiterii facturii.
- Legea impune un singur plafon: perioada de decontare nu poate depăși un an. Facturarea lunară respectă acest plafon fără nicio problemă — practic e cadența cea mai comună pentru abonamente.

## Ce se greșește în practică

- Se emite factura „când se apucă cineva", nu la o dată consecventă — ceea ce face dificilă corelarea cu extrasul de cont și cu eventualele reclamații ale clientului privind perioada facturată.
- Se uită de o lună întreagă (concediu, aglomerație) și factura pentru acea perioadă nu mai iese deloc, deși prestarea a continuat.
- Se emite o singură factură cumulată pentru mai multe luni în urmă, deși contractul prevede plată lunară — ceea ce nu respectă data de plată stabilită contractual.

## Ce face iConta.eu

Ecranul **Facturi recurente** din iConta.eu automatizează exact acest caz: se creează un șablon (client, linii de facturare, sumă, zi de emitere din lună), iar un job (cron) rulează zilnic, la 07:00, și emite automat câte o factură pe lună pentru fiecare șablon activ, atâta timp cât ziua configurată a trecut și șablonul nu a mai emis deja în luna curentă. Dacă rularea zilnică lipsește exact în ziua configurată, factura tot iese la următoarea rulare din aceeași lună — nu se pierde nicio lună — dar cu data facturii egală cu ziua reală a emiterii, nu neapărat ziua din șablon. Un șablon existent nu poate fi editat (sumă, linii, zi) — poate fi doar activat/dezactivat sau șters și recreat.

[iConta.eu](/)
