---
title: "Cum se facturează un abonament software anual?"
description: "Ce spune legea despre perioada de decontare a prestărilor continue precum abonamentele anuale, și de ce facturarea anuală nu se face din modulul de facturi recurente al iConta.eu."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se facturează un abonament software anual?

Un abonament software plătit o dată pe an rămâne, fiscal, tot o prestare de servicii cu caracter continuu — doar că perioada de decontare aleasă e cea mai lungă permisă de lege. Momentul la care se consideră „efectuată" prestarea și limita legală a perioadei de facturare sunt reglementate explicit, indiferent de cadență.

## Temeiul legal

::: ghid-temei
„În cazul livrărilor de bunuri și al prestărilor de servicii care se efectuează continuu, altele decât cele prevăzute la alin. (7), cum sunt livrările de gaze naturale, de apă, de energie electrică, serviciile de telefonie, de închiriere, de leasing, de consesionare, de arendare de bunuri, de acordare cu plată pentru o anumită perioadă a unor drepturi reale, precum dreptul de uzufruct și superficia, asupra unui bun imobil, și alte livrări/prestări asemenea, se consideră că livrarea de bunuri/prestarea de servicii este efectuată la fiecare dată prevăzută în contract pentru plata bunurilor livrate/serviciilor prestate sau, în lipsa unei astfel de prevederi contractuale, la data emiterii unei facturi, dar perioada de decontare nu poate depăși un an."
— Cod fiscal (Legea 227/2015), art. 281 alin. (8) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Legea nu obligă la o cadență anume pentru facturarea unui abonament — obligă doar la un plafon: perioada de decontare nu poate depăși un an calendaristic.
- O facturare anuală e, deci, exact la limita superioară permisă de lege — perfect legală, atâta timp cât nu se depășește un an.
- Data la care prestația „se consideră efectuată" rămâne fie data de plată din contract, fie, în lipsa acesteia, data emiterii facturii — ambele valabile și pentru un ciclu anual.

## Ce se greșește în practică

- Se presupune că orice serviciu continuu trebuie neapărat facturat lunar — legea nu impune asta, doar plafonează perioada maximă la un an.
- Se emite o factură anuală, dar cu o perioadă de prestare care depășește de fapt un an (de exemplu, se reportează neintenționat facturarea și se acoperă 13-14 luni într-o singură factură) — ceea ce încalcă plafonul din art. 281 alin. (8).
- Se caută în aplicație un mecanism „automat" pentru facturarea anuală, presupunând (greșit) că orice modul de recurență acceptă orice cadență.

## Ce face iConta.eu

Aici trebuie spus clar: modulul **Facturi recurente** din iConta.eu **nu suportă facturarea anuală**. Mecanismul e ireductibil lunar — nu doar ca opțiune implicită, ci structural: tabela din baza de date pentru șabloane nu are nicio coloană de periodicitate, iar jobul zilnic de emitere verifică exclusiv dacă șablonul a mai emis o factură „în luna curentă"; după ce trece luna, șablonul redevine eligibil automat. Un abonament configurat aici ar primi, în realitate, câte o factură în fiecare lună, nu una pe an — exact opusul intenției. Pentru facturarea anuală a unui abonament software, factura se emite manual, o singură dată pe an, din ecranul obișnuit de facturare, nu din Facturi recurente.

[iConta.eu](/)
