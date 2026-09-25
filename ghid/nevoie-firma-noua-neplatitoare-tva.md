---
title: "Când are nevoie o firmă nouă neplătitoare de TVA de cod special de TVA?"
description: "Situațiile în care o firmă neplătitoare de TVA trebuie să solicite înregistrarea specială conform art. 317 din Codul fiscal, înainte de o achiziție sau un serviciu intracomunitar."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Când are nevoie o firmă nouă neplătitoare de TVA de cod special de TVA?

O firmă neplătitoare de TVA (de exemplu la regimul de scutire pentru întreprinderi mici) poate ajunge, chiar fără să devină plătitoare „normală", să aibă obligația de a solicita un cod special de TVA — dacă face achiziții intracomunitare peste un anumit plafon sau dacă primește ori prestează anumite servicii intracomunitare.

## Temeiul legal

::: ghid-temei
„Are obligația să solicite înregistrarea în scopuri de TVA, conform prezentului articol: a) persoana impozabilă care are sediul activității economice în România, [...] neînregistrate și care nu au obligația să se înregistreze conform art. 316 [...], care efectuează o achiziție intracomunitară taxabilă în România, înainte de efectuarea achiziției intracomunitare, dacă valoarea achiziției intracomunitare respective depășește plafonul pentru achiziții intracomunitare în anul calendaristic în care are loc achiziția intracomunitară; [...] b) persoana impozabilă care are sediul activității economice în România [...], dacă prestează servicii care au locul în alt stat membru, pentru care beneficiarul serviciului este persoana obligată la plata taxei conform echivalentului din legislația altui stat membru al art. 307 alin. (2), înainte de prestarea serviciului; [...] c) persoana impozabilă care își are stabilit sediul activității economice în România [...], dacă primesc de la un prestator, persoană impozabilă stabilită în alt stat membru, servicii pentru care sunt obligate la plata taxei în România conform art. 307 alin. (2), înaintea primirii serviciilor respective."
— Legea 227/2015 (Codul fiscal), art. 317 alin. (1) lit. a)-c) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Cele trei situații de bază pentru o firmă neplătitoare de TVA:

- **Achiziții intracomunitare de bunuri peste plafon** — înregistrarea se cere **înainte** de achiziția care depășește plafonul. Plafonul e de **10.000 euro** (echivalentul în lei), cumulat pe anul calendaristic curent sau precedent (CF art. 268 alin. (4)-(5)) — sub acest plafon, achiziția nu e operațiune impozabilă în România și nu declanșează obligația.
- **Prestarea de servicii cu locul în alt stat membru**, pentru care beneficiarul (din alt stat membru) e obligat la plata taxei — înregistrarea se cere **înainte** de prestarea serviciului.
- **Primirea de servicii de la un prestator din alt stat membru**, pentru care firma română e obligată la plata taxei prin taxare inversă — înregistrarea se cere **înainte** de primirea serviciului.

În toate cele trei cazuri, obligația de înregistrare precede operațiunea — nu se declară ulterior, „la regularizare".

## Ce se greșește în practică

- Se așteaptă depășirea plafonului de 10.000 euro pentru a solicita înregistrarea, deși pentru servicii intracomunitare (lit. b și c) nu există un asemenea plafon — obligația apare de la prima operațiune de acest tip.
- Se confundă plafonul de 10.000 euro pentru achiziții de bunuri cu alte plafoane din legislația TVA (de exemplu cel de scutire pentru întreprinderi mici) — sunt praguri independente.
- Se solicită înregistrarea după ce operațiunea a avut deja loc, deși legea cere înregistrarea **înainte** de achiziție/prestare/primire.

## Ce face iConta.eu

Aplicația păstrează în profilul firmei un marcaj explicit pentru înregistrarea specială conform art. 317 (`inreg_art317`), folosit apoi de motorul de operațiuni intracomunitare la calculul TVA pentru achiziții cu taxare inversă: dacă firma e neplătitoare de TVA și NU are acest marcaj, aplicația tratează TVA-ul aferent ca nedeductibil, inclus în costul achiziției (consecința firească a lipsei înregistrării art. 316/317, conform CF art. 297) — comportament distinct de cel al unei firme plătitoare, la care TVA-ul e simultan colectat și dedus. Aplicația nu calculează însă automat plafonul de 10.000 euro pentru achizițiile intracomunitare de bunuri și nu semnalează proactiv momentul în care firma ar trebui să solicite înregistrarea — verificarea depășirii plafonului rămâne o responsabilitate a contabilului.

[iConta.eu](/)
