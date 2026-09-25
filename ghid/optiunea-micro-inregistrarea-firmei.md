---
title: "Opțiunea pentru micro la înregistrarea firmei"
description: "Condițiile în care o firmă nou-înființată poate opta pentru impozitul pe veniturile microîntreprinderilor chiar din primul an fiscal, potrivit art. 48 din Codul fiscal."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Opțiunea pentru micro la înregistrarea firmei

Regula generală e că o firmă optează pentru regimul micro începând cu anul fiscal **următor** celui în care îndeplinește condițiile. O firmă nou-înființată are însă o excepție: poate opta pentru micro chiar din **primul ei an fiscal**, dacă îndeplinește la timp condițiile specifice de la art. 48.

## Temeiul legal

::: ghid-temei
„(3) O persoană juridică română care este nou-înființată poate opta să plătească impozit pe veniturile microîntreprinderilor începând cu primul an fiscal, dacă condițiile prevăzute la art. 47 alin. (1) lit. d) și h) sunt îndeplinite la data înregistrării în registrul comerțului, iar cea prevăzută la lit. g) în termen de 90 de zile inclusiv de la data înregistrării persoanei juridice respective. În cazul în care, în acest termen, nu se îndeplinește condiția de la art. 47 alin. (1) lit. g), microîntreprinderea datorează impozit pe profit începând cu trimestrul următor celui în care expiră perioada de 90 de zile."
— Legea 227/2015, art. 48 alin. (3) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce trebuie verificat, concret, la înregistrarea unei firme noi care vrea regim micro din primul an:

- **La data înregistrării în registrul comerțului** trebuie deja îndeplinite: condiția lit. d) (capitalul social deținut de persoane, altele decât statul și unitățile administrativ-teritoriale) și condiția lit. h) (asociați/acționari care nu dețin peste 25% din mai multe firme micro simultan, cu excepția singurei firme desemnate).
- **Condiția salariatului** (lit. g), cel puțin un salariat) are un termen separat, mai generos: **90 de zile** de la data înregistrării firmei, nu de la momentul opțiunii.
- Dacă în cele 90 de zile firma **nu** angajează salariatul necesar, ea datorează impozit pe profit — nu de la data înregistrării, ci de la **trimestrul următor** celui în care expiră cele 90 de zile.
- Opțiunea pentru micro din primul an fiscal e reală doar dacă toate cele trei condiții sunt îndeplinite la termenele lor specifice — nu e suficient să fie îndeplinite „până la 31 decembrie", ca la firmele deja existente.

## Ce se greșește în practică

- Se aplică regula generală (opțiunea valabilă doar din anul fiscal următor) și la o firmă nou-înființată, ignorând excepția specifică de la art. 48 alin. (3), care permite opțiunea încă din primul an.
- Se presupune că salariatul trebuie angajat imediat, la data înregistrării, în loc să se folosească fereastra de 90 de zile prevăzută explicit de lege pentru această condiție.
- Se ratează termenul de 90 de zile fără să se conștientizeze consecința: nu se pierde doar dreptul la micro pentru anul curent, ci firma datorează impozit pe profit din trimestrul următor expirării termenului, cu efect retroactiv asupra calculelor deja făcute pe regim micro.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu urmărește automat termenul de 90 de zile** de la înregistrarea unei firme noi pentru verificarea condiției salariatului, necesară păstrării opțiunii pentru micro din primul an fiscal — această verificare rămâne manuală, pe baza datei de înființare și a datei de angajare a primului salariat, introduse de contabil. Aplicația are evidența reală a salariaților firmei (`salariati_import_api.py`, cu funcția care determină dacă firma are cel puțin un salariat activ), dar nu leagă această evidență de termenul legal de 90 de zile din art. 48 alin. (3).

[iConta.eu](/)
