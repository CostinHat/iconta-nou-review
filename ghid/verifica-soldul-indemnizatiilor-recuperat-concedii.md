---
title: "Cum se verifică soldul indemnizațiilor de recuperat pentru concedii medicale?"
description: "Cum se recuperează de la Fondul național unic de asigurări sociale de sănătate sumele reprezentând indemnizații de concediu medical plătite salariaților, potrivit OUG 158/2005."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se verifică soldul indemnizațiilor de recuperat pentru concedii medicale?

O parte din indemnizația de concediu medical e suportată de angajator, o parte de Fondul național unic de asigurări sociale de sănătate (FNUASS) — iar partea din urmă nu se „vede" în cont automat, ci trebuie recuperată printr-un circuit distinct de raportare.

## Temeiul legal

::: ghid-temei
„(1) Sumele reprezentând indemnizații, care se plătesc asiguraților și care, potrivit prevederilor prezentei ordonanțe de urgență, se suportă din bugetul Fondului național unic de asigurări sociale de sănătate, se recuperează din bugetul Fondului național unic de asigurări sociale de sănătate din creditele bugetare prevăzute cu această destinație. Aceste sume nu pot fi recuperate din sumele constituite reprezentând contribuție de asigurări sociale de sănătate."
— OUG nr. 158/2005, art. 38 alin. (1) (sursă: anaf_surse/oug_158_2005_consolidat.txt)
:::

Din text rezultă circuitul corect de recuperare:

- Sumele suportate de FNUASS (partea din indemnizație aflată peste zilele plătite de angajator) **nu se scad direct din contribuția de asigurări sociale de sănătate datorată** — se recuperează separat, din creditele bugetare ale Fondului, printr-o cerere de restituire.
- Angajatorul trebuie să depună la casa de asigurări de sănătate din raza sediului social exemplarul 2 al certificatelor de concediu medical, atunci când solicită restituirea sumelor respective.
- Cererile de restituire pot fi respinse la plată de casa de asigurări; angajatorul are un termen limitat (de regulă 90 de zile de la comunicarea respingerii) pentru a remedia cauzele și a redepune cererea.

## Ce se greșește în practică

- Se presupune că suma de recuperat de la FNUASS se compensează automat cu obligațiile de contribuție de asigurări de sănătate ale firmei — legea interzice explicit această compensare directă.
- Se pierde termenul de remediere și redepunere a cererii de restituire, în urma unei respingeri la plată din partea casei de asigurări, iar sumele respective rămân definitiv nerecuperate.
- Se confundă suma totală a indemnizației (brută, plătită salariatului) cu suma efectiv de recuperat de la Fond, care corespunde doar zilelor și cotei suportate de FNUASS, nu de angajator.

## Ce face iConta.eu

La data acestui ghid, iConta.eu calculează, pentru fiecare certificat de concediu medical introdus, separarea sumei pe zile suportate de angajator și zile suportate de FNUASS, folosită apoi în declarația D112 (`core/d112.py`). Aplicația **nu urmărește** stadiul efectiv al cererilor de restituire depuse la casa de asigurări și nu ține un sold automat al sumelor recuperate față de cele declarate — compararea sumei calculate ca fiind de recuperat cu încasările reale de la Fond rămâne o reconciliere pe care contabilul o face manual, pe baza extrasului de cont.

[iConta.eu](/)
