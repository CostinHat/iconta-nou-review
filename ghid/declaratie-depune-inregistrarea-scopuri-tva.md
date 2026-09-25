---
title: "Ce declarație se depune pentru înregistrarea în scopuri de TVA în 2026?"
description: "Declarația electronică unică de înregistrare fiscală (D700), care a înlocuit vechile formulare de înregistrare/mențiuni fiscale, și ce presupune ea pentru o firmă care se înregistrează în scopuri de TVA."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce declarație se depune pentru înregistrarea în scopuri de TVA în 2026?

Vechile formulare de înregistrare fiscală pe hârtie/PDF au fost înlocuite, pentru mediul electronic, de un singur formular unificat — declarația 700 (D700). Prin ea se solicită, printre altele, înregistrarea în scopuri de TVA (potrivit art. 316 sau art. 317 din Codul fiscal), dar și orice altă modificare a vectorului fiscal al firmei.

## Temeiul legal

::: ghid-temei
„(1) Persoana impozabilă care are sediul activității economice în România și realizează sau intenționează să realizeze o activitate economică ce implică operațiuni taxabile, scutite de taxa pe valoarea adăugată cu drept de deducere, cu locul în România, trebuie să solicite înregistrarea în scopuri de TVA la organul fiscal competent, după cum urmează: [...]"
— Legea 227/2015 (Codul fiscal), art. 316 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„(3) Organele fiscale competente vor înregistra în scopuri de TVA, conform prezentului articol, orice persoană care solicită înregistrarea, conform alin. (1)-(2^1)."
— Legea 227/2015 (Codul fiscal), art. 317 alin. (3) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

În 2026, procedural, situația e următoarea:

- formularele vechi — 010, 020, 070 — erau declarațiile clasice de înregistrare/mențiuni fiscale, depuse pe suport de hârtie sau ca document distinct; ele **nu mai au corespondent** ca validator XML separat, fiind înlocuite de declarația electronică unificată **D700** pentru mediul electronic;
- D700 e declarația prin care se solicită atât înregistrarea fiscală inițială, cât și orice mențiune ulterioară asupra vectorului fiscal — inclusiv opțiunea/obligația de înregistrare în scopuri de TVA conform art. 316 sau art. 317 din Codul fiscal — marcată prin bifele corespunzătoare fiecărei operațiuni (înregistrare, modificare, radiere) pe fiecare tip de obligație fiscală;
- structura D700 conține zeci de secțiuni și bife condiționate de operațiunea aleasă (Caen, Contabilitate, Domiciliu, Impozite, Sedii secundare etc.), definite prin ordinul ANAF care aprobă modelul și conținutul formularului.

## Ce se greșește în practică

- Se caută încă „formularul 020" sau „070" ca document separat de depus — acestea sunt formulare vechi, fără validator XML activ, înlocuite de D700 în mediul electronic.
- Se completează D700 fără să se bifeze corect operațiunea („înregistrare" vs. „modificare" vs. „radiere") pentru fiecare obligație de vector fiscal vizată — o bifă greșită poate produce înregistrarea/anularea unei alte obligații decât cea intenționată.
- Se depune cererea de înregistrare TVA fără actele justificative cerute de procedura ANAF (de exemplu, pentru evaluarea intenției și capacității de a desfășura operațiuni în sfera TVA, potrivit criteriilor de condiționare a înregistrării).

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu generează și nu depune declarația D700**. Verificarea la sursă arată că D700 e o declarație de tip „SmartPDF" — validatorul oficial ANAF (DUKIntegrator) nu o validează ca fișier XML de sine stătător, spre deosebire de alte declarații (D100, D112, D300 etc.), iar o mapare corectă operațiune→câmpuri ar necesita instrucțiunile oficiale de completare pe fiecare bifă, nu doar structura tehnică a formularului. Fără această validare la sursă, aplicația nu construiește și nu publică un XML negarantat, potrivit regulii proprii de lucru. Înregistrarea în scopuri de TVA rămâne, deocamdată, un demers depus direct de contribuabil sau de contabil prin mijloacele puse la dispoziție de ANAF.

[iConta.eu](/)
