---
title: "Ce este controlul antifraudă și ce poate verifica?"
description: "Definiția legală a controlului antifraudă fiscală, competența Direcției generale antifraudă fiscală și diferența față de inspecția fiscală obișnuită."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce este controlul antifraudă și ce poate verifica?

Controlul antifraudă nu e o formă de inspecție fiscală clasică — e o procedură distinctă, cu reguli proprii, exercitată de o structură specializată a ANAF, fără obligația de înștiințare prealabilă a contribuabilului.

## Temeiul legal

::: ghid-temei
„(1) Controlul antifraudă se efectuează de către funcționarii publici din cadrul Direcției generale antifraudă fiscală pe întreg teritoriul țării, în baza analizei de risc. Aceștia sunt denumiți, în sensul prezentului capitol, organe de control antifraudă fiscală. (2) Controlul antifraudă are ca obiect prevenirea și combaterea fraudei și evaziunii fiscale. Organele de control antifraudă fiscală exercită activități de control operativ, fără informarea prealabilă a contribuabilului/plătitorului cu privire la efectuarea controlului."
— Legea 207/2015 (Codul de procedură fiscală), art. 136 alin. (1)-(2) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Câteva elemente esențiale pentru un contribuabil vizat:

- controlul îl efectuează exclusiv **Direcția generală antifraudă fiscală**, nu inspectorii fiscali „obișnuiți" — organul e distinct de cel care face inspecția fiscală clasică sau controlul inopinat (art. 134-135 din același cod);
- se declanșează, de regulă, **pe baza analizei de risc**, dar legea permite și controale fără analiză de risc prealabilă, în cazuri de urgență (constatarea, în exercitarea atribuțiilor, a unor încălcări care impun intervenție imediată) sau pentru acțiuni cu caracter specific de prevenire/combatere a fraudei (art. 136 alin. 3);
- controlul se face **fără înștiințare prealabilă**, spre deosebire de inspecția fiscală programată, care presupune aviz de inspecție comunicat din timp;
- contribuabilul **nu poate contesta procedura de selecție** folosită pentru declanșarea controlului (art. 136 alin. 4) — poate contesta însă constatările și actele emise în urma controlului, pe căile obișnuite.

## Ce se greșește în practică

- Se confundă controlul antifraudă cu inspecția fiscală și se așteaptă un aviz de inspecție trimis din timp — controlul antifraudă e, prin definiție, fără înștiințare prealabilă.
- Se contestă faptul că firma „a fost selectată fără motiv" — legea exclude explicit acest tip de obiecție; contestația trebuie să vizeze constatările concrete, nu criteriul de selecție.
- Se presupune că un control antifraudă exclude o inspecție fiscală ulterioară pe aceleași obligații — cele două proceduri sunt distincte și pot coexista, cu regulile lor proprii de coordonare.

## Ce face iConta.eu

iConta.eu nu are un modul dedicat controlului antifraudă sau inspecției fiscale ANAF — verificarea `core/control_fiscal_api.py` din aplicație este un „semafor de conformare fiscală" intern, care compară declarațiile datorate cu cele efectiv depuse de firmă, pentru a semnala lipsurile din propriile obligații declarative. Nu are nicio legătură cu analiza de risc a ANAF și nu poate anticipa sau simula un control antifraudă real.

[iConta.eu](/)
